"""
Unit tests for benchmarks/llmlingua_baseline.py (v0.0.3c)

Tests the LLMLingua baseline execution pipeline including GPU detection,
compressor initialization, document compression, token counting, fallback
estimation, result assembly, comparison table generation, and end-to-end
pipeline orchestration.

All tests use mocks for LLMLingua and PyTorch dependencies to ensure
they run in any environment without requiring GPU hardware or the
llmlingua package to be installed.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

# llmlingua_baseline requires either tiktoken or regex for token counting
_has_tokenizer = False
try:
    import tiktoken
    _has_tokenizer = True
except ImportError:
    try:
        import regex
        _has_tokenizer = True
    except ImportError:
        pass

if not _has_tokenizer:
    pytest.skip(
        "Neither tiktoken nor regex installed — skipping llmlingua baseline tests",
        allow_module_level=True,
    )

# Ensure project root is importable
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

benchmarks_dir = project_root / "benchmarks"
if str(benchmarks_dir) not in sys.path:
    sys.path.insert(0, str(benchmarks_dir))

from benchmarks.llmlingua_baseline import (
    COMPRESSION_CONFIG,
    ESTIMATED_COMPRESSION_RATIOS,
    HAIKU_TARGET_RATIOS,
    SAMPLE_FILES,
    analyze_llmlingua_results,
    build_comparison_table,
    build_document_result,
    compress_document,
    count_compressed_tokens,
    detect_gpu_availability,
    estimate_compression_result,
    initialize_compressor,
    run_baseline,
)


# ── Fixtures ──


@pytest.fixture
def sample_text():
    """A representative procedural text for compression tests."""
    return (
        "Step 1: Install Docker on your system.\n"
        "Step 2: Configure the environment variables.\n"
        "Step 3: Run the application container.\n"
        "Note: Ensure port 8080 is available.\n"
    )


@pytest.fixture
def mock_compressor():
    """A mock PromptCompressor that returns predictable results."""
    compressor = MagicMock()
    compressor.compress_prompt.return_value = {
        "compressed_prompt": "Install Docker. Configure env. Run container.",
        "ratio": 0.4823,
        "compression_ratio": 0.4823,
    }
    return compressor


@pytest.fixture
def failing_compressor():
    """A mock PromptCompressor that raises an exception."""
    compressor = MagicMock()
    compressor.compress_prompt.side_effect = RuntimeError("OOM: out of memory")
    return compressor


@pytest.fixture
def sample_document_result():
    """A complete document result dict for testing build functions."""
    return {
        "tier": "Simple",
        "file_path": "benchmarks/samples/simple.md",
        "device_used": "mps",
        "gpu_available": True,
        "gpu_name": "Apple Metal Performance Shaders",
        "metrics": {
            "original_tokens": 101,
            "compressed_tokens": 49,
            "compression_ratio": 0.4853,
            "execution_time_seconds": 2.14,
        },
        "compressed_text_preview": "Install Docker. Configure env. Run container.",
        "semantic_preservation_notes": "Default LLMLingua v1 with 50% compression rate",
    }


@pytest.fixture
def three_document_results():
    """Three document results for comparison table tests."""
    return [
        {
            "tier": "Simple",
            "metrics": {
                "original_tokens": 101,
                "compressed_tokens": 52,
                "compression_ratio": 0.5149,
                "execution_time_seconds": 2.0,
            },
        },
        {
            "tier": "Medium",
            "metrics": {
                "original_tokens": 443,
                "compressed_tokens": 213,
                "compression_ratio": 0.4808,
                "execution_time_seconds": 3.5,
            },
        },
        {
            "tier": "Complex",
            "metrics": {
                "original_tokens": 1589,
                "compressed_tokens": 731,
                "compression_ratio": 0.4601,
                "execution_time_seconds": 7.2,
            },
        },
    ]


@pytest.fixture
def samples_dir(tmp_path):
    """Temporary samples directory with 3 markdown files."""
    samples = tmp_path / "samples"
    samples.mkdir()
    (samples / "simple.md").write_text(
        "Step 1: Install Docker.\nStep 2: Configure env.\n"
    )
    (samples / "medium.md").write_text(
        "Step 1: Install kubectl.\nStep 2: Configure kubeconfig.\n"
        "Step 3: Apply manifests.\nWarning: Check RBAC permissions.\n"
        "If cluster unreachable, verify VPN connection.\n"
    )
    (samples / "complex.md").write_text(
        "Step 1: Create Kubernetes manifest.\n"
        "Step 2: Apply with kubectl apply -f deploy.yaml.\n"
        "Step 3: Verify rollout status.\n"
        "Step 4: Expose service via LoadBalancer.\n"
        "Step 5: Update container image.\n"
        "Step 6: Scale deployment replicas.\n"
        "Step 7: Clean up old resources.\n"
        "Warning: Resource limits required.\n"
        "Note: Health probes recommended.\n"
        "If pods crash, check resource requests.\n"
    )
    return samples


@pytest.fixture
def raw_metrics_file(tmp_path):
    """Temporary raw_metrics.json with valid structure."""
    metrics = {
        "version": "0.0.3b",
        "encoding": "cl100k_base",
        "documents": [
            {"tier": "Simple", "metrics": {"token_count": 101}},
            {"tier": "Medium", "metrics": {"token_count": 443}},
            {"tier": "Complex", "metrics": {"token_count": 1589}},
        ],
    }
    path = tmp_path / "raw_metrics.json"
    path.write_text(json.dumps(metrics, indent=2))
    return path


@pytest.fixture
def mock_compressor_init():
    """Mock initialize_compressor to return None (estimation fallback).

    Prevents run_baseline() from downloading a real ~1GB model from
    HuggingFace during unit tests. All documents will use the estimation
    fallback path instead.
    """
    with patch(
        "benchmarks.llmlingua_baseline.initialize_compressor",
        return_value=None,
    ):
        yield


# ═══════════════════════════════════════════════════════════════════
# 5.1 — HAPPY PATH TESTS
# ═══════════════════════════════════════════════════════════════════


class TestDetectGpuAvailability:
    """Tests for detect_gpu_availability()."""

    # Acceptance Criterion: "GPU availability detected and reported in output JSON"

    @pytest.mark.unit
    def test_detect_gpu_returns_tuple(self):
        """detect_gpu_availability returns a 2-tuple."""
        # Acceptance Criterion: "GPU availability detected and reported in output JSON"
        result = detect_gpu_availability()
        assert isinstance(result, tuple)
        assert len(result) == 2

    @pytest.mark.unit
    def test_detect_gpu_first_element_is_bool(self):
        """First element is always a boolean."""
        # Acceptance Criterion: "GPU availability detected and reported in output JSON"
        has_gpu, _ = detect_gpu_availability()
        assert isinstance(has_gpu, bool)

    @pytest.mark.unit
    def test_detect_gpu_second_element_is_str_or_none(self):
        """Second element is either a string or None."""
        # Acceptance Criterion: "GPU availability detected and reported in output JSON"
        _, gpu_name = detect_gpu_availability()
        assert gpu_name is None or isinstance(gpu_name, str)

    @pytest.mark.unit
    @patch.dict(sys.modules, {"torch": None})
    def test_detect_gpu_no_torch_returns_false(self):
        """Returns (False, None) when PyTorch is not installed."""
        # Acceptance Criterion: "GPU availability detected and reported in output JSON"
        # Re-import to pick up the patched module state
        import importlib
        import benchmarks.llmlingua_baseline as mod
        importlib.reload(mod)
        has_gpu, gpu_name = mod.detect_gpu_availability()
        assert has_gpu is False
        assert gpu_name is None

    @pytest.mark.unit
    def test_detect_gpu_cuda_available(self):
        """Returns (True, device_name) when CUDA is available."""
        # Acceptance Criterion: "GPU availability detected and reported in output JSON"
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.get_device_name.return_value = "NVIDIA RTX 3080"
        mock_torch.backends.mps.is_available.return_value = False

        with patch.dict(sys.modules, {"torch": mock_torch}):
            import importlib
            import benchmarks.llmlingua_baseline as mod
            importlib.reload(mod)
            has_gpu, name = mod.detect_gpu_availability()
            assert has_gpu is True
            assert name == "NVIDIA RTX 3080"

    @pytest.mark.unit
    def test_detect_gpu_mps_available(self):
        """Returns (True, 'Apple Metal...') when MPS is available."""
        # Acceptance Criterion: "GPU availability detected and reported in output JSON"
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = True

        with patch.dict(sys.modules, {"torch": mock_torch}):
            import importlib
            import benchmarks.llmlingua_baseline as mod
            importlib.reload(mod)
            has_gpu, name = mod.detect_gpu_availability()
            assert has_gpu is True
            assert "Metal" in name


class TestInitializeCompressor:
    """Tests for initialize_compressor()."""

    # Acceptance Criterion: "LLMLingua successfully initialized and configured"

    @pytest.mark.unit
    def test_initialize_returns_compressor_on_success(self):
        """Returns a compressor object when initialization succeeds."""
        # Acceptance Criterion: "LLMLingua successfully initialized and configured"
        mock_compressor = MagicMock()
        mock_llmlingua = MagicMock()
        mock_llmlingua.PromptCompressor.return_value = mock_compressor

        with patch.dict(sys.modules, {"llmlingua": mock_llmlingua}):
            result = initialize_compressor("cpu")
            assert result is not None

    @pytest.mark.unit
    def test_initialize_returns_none_when_not_installed(self):
        """Returns None when llmlingua is not installed."""
        # Acceptance Criterion: "LLMLingua successfully initialized and configured"
        with patch.dict(sys.modules, {"llmlingua": None}):
            import importlib
            import benchmarks.llmlingua_baseline as mod
            importlib.reload(mod)
            result = mod.initialize_compressor("cpu")
            assert result is None

    @pytest.mark.unit
    def test_initialize_falls_back_to_cpu(self):
        """Falls back to CPU when primary device fails."""
        # Acceptance Criterion: "LLMLingua successfully initialized and configured"
        mock_compressor = MagicMock()
        devices_tried = []

        def side_effect(**kwargs):
            device = kwargs.get("device_map", "unknown")
            devices_tried.append(device)
            if device == "cuda":
                raise RuntimeError("CUDA not available")
            return mock_compressor

        mock_llmlingua = MagicMock()
        mock_llmlingua.PromptCompressor.side_effect = side_effect

        with patch.dict(sys.modules, {"llmlingua": mock_llmlingua}):
            result = initialize_compressor("cuda")
            assert result is mock_compressor
            # Should try both models on cuda (both fail), then first
            # model on cpu (succeeds). Verify CPU was eventually tried.
            assert "cpu" in devices_tried
            assert "cuda" in devices_tried


class TestCompressDocument:
    """Tests for compress_document()."""

    # Acceptance Criterion: "Compression metrics recorded: original_tokens,
    # compressed_tokens, compression_ratio, execution_time_seconds"

    @pytest.mark.unit
    def test_compress_success_returns_expected_keys(self, mock_compressor, sample_text):
        """Successful compression returns all expected keys."""
        # Acceptance Criterion: "Compression metrics recorded"
        result = compress_document(mock_compressor, sample_text, COMPRESSION_CONFIG)
        assert result["success"] is True
        assert "full_compressed_text" in result
        assert "compressed_text_preview" in result
        assert "compressed_text_length" in result
        assert "compression_ratio" in result
        assert "execution_time_seconds" in result
        assert "semantic_preservation_notes" in result

    @pytest.mark.unit
    def test_compress_ratio_is_float(self, mock_compressor, sample_text):
        """Compression ratio is a float."""
        # Acceptance Criterion: "Compression metrics recorded"
        result = compress_document(mock_compressor, sample_text, COMPRESSION_CONFIG)
        assert isinstance(result["compression_ratio"], float)

    @pytest.mark.unit
    def test_compress_preview_max_200_chars(self, mock_compressor, sample_text):
        """Compressed text preview is at most 200 characters."""
        # Acceptance Criterion: "Compressed text preview (first 200 chars) captured"
        result = compress_document(mock_compressor, sample_text, COMPRESSION_CONFIG)
        assert len(result["compressed_text_preview"]) <= 200

    @pytest.mark.unit
    def test_compress_time_is_nonnegative(self, mock_compressor, sample_text):
        """Execution time is a non-negative number."""
        # Acceptance Criterion: "Compression metrics recorded"
        result = compress_document(mock_compressor, sample_text, COMPRESSION_CONFIG)
        assert result["execution_time_seconds"] >= 0

    @pytest.mark.unit
    def test_compress_failure_returns_error(self, failing_compressor, sample_text):
        """Failed compression returns success=False with error message."""
        # Acceptance Criterion: "Compression metrics recorded"
        result = compress_document(
            failing_compressor, sample_text, COMPRESSION_CONFIG
        )
        assert result["success"] is False
        assert "error" in result
        assert "OOM" in result["error"]

    @pytest.mark.unit
    def test_compress_failure_includes_time(self, failing_compressor, sample_text):
        """Failed compression still records execution time."""
        # Acceptance Criterion: "Compression metrics recorded"
        result = compress_document(
            failing_compressor, sample_text, COMPRESSION_CONFIG
        )
        assert "execution_time_seconds" in result
        assert result["execution_time_seconds"] >= 0

    @pytest.mark.unit
    def test_compress_notes_mention_config(self, mock_compressor, sample_text):
        """Semantic notes reference the compression configuration."""
        # Acceptance Criterion: "Semantic preservation notes documented"
        result = compress_document(mock_compressor, sample_text, COMPRESSION_CONFIG)
        assert "50%" in result["semantic_preservation_notes"]
        assert "v1" in result["semantic_preservation_notes"]


# ═══════════════════════════════════════════════════════════════════
# 5.2 — EDGE CASE TESTS
# ═══════════════════════════════════════════════════════════════════


class TestCompressDocumentEdgeCases:
    """Edge case tests for compress_document()."""

    @pytest.mark.unit
    def test_compress_none_compressor_raises_value_error(self, sample_text):
        """Raises ValueError when compressor is None."""
        with pytest.raises(ValueError, match="Compressor must not be None"):
            compress_document(None, sample_text, COMPRESSION_CONFIG)

    @pytest.mark.unit
    def test_compress_none_text_raises_value_error(self, mock_compressor):
        """Raises ValueError when text is None."""
        with pytest.raises(ValueError, match="Text must not be None or empty"):
            compress_document(mock_compressor, None, COMPRESSION_CONFIG)

    @pytest.mark.unit
    def test_compress_empty_text_raises_value_error(self, mock_compressor):
        """Raises ValueError when text is empty."""
        with pytest.raises(ValueError, match="Text must not be None or empty"):
            compress_document(mock_compressor, "", COMPRESSION_CONFIG)

    @pytest.mark.unit
    def test_compress_whitespace_only_raises_value_error(self, mock_compressor):
        """Raises ValueError when text is only whitespace."""
        with pytest.raises(ValueError, match="Text must not be None or empty"):
            compress_document(mock_compressor, "   \n\t  ", COMPRESSION_CONFIG)


class TestCountCompressedTokens:
    """Tests for count_compressed_tokens()."""

    # Acceptance Criterion: "Compression metrics recorded: compressed_tokens"

    @pytest.mark.unit
    def test_count_returns_positive_int(self):
        """Token count is a positive integer for non-empty text."""
        # Acceptance Criterion: "Compression metrics recorded"
        count = count_compressed_tokens("Hello world, this is a test.")
        assert isinstance(count, int)
        assert count > 0

    @pytest.mark.unit
    def test_count_empty_string_returns_zero(self):
        """Token count for empty string is zero."""
        count = count_compressed_tokens("")
        assert count == 0

    @pytest.mark.unit
    def test_count_none_raises_value_error(self):
        """Raises ValueError for None input."""
        with pytest.raises(ValueError, match="Cannot tokenize None"):
            count_compressed_tokens(None)

    @pytest.mark.unit
    def test_count_longer_text_returns_more_tokens(self):
        """Longer text produces more tokens than shorter text."""
        short = count_compressed_tokens("hello")
        long = count_compressed_tokens("hello world this is a longer sentence")
        assert long > short

    @pytest.mark.unit
    def test_count_code_block_counts_tokens(self):
        """Code blocks are tokenized correctly."""
        code = "`kubectl apply -f deployment.yaml`"
        count = count_compressed_tokens(code)
        assert count > 0


class TestEstimateCompressionResult:
    """Tests for estimate_compression_result()."""

    # Acceptance Criterion: "If any document used fallback/estimation,
    # clearly flagged in JSON (cpu_only_estimated: true)"

    @pytest.mark.unit
    def test_estimate_simple_returns_expected_ratio(self):
        """Simple tier estimation uses 0.52 ratio."""
        # Acceptance Criterion: "Fallback clearly flagged"
        result = estimate_compression_result("Simple", 100)
        assert result["compression_ratio"] == 0.52
        assert result["compressed_tokens"] == 52

    @pytest.mark.unit
    def test_estimate_medium_returns_expected_ratio(self):
        """Medium tier estimation uses 0.48 ratio."""
        result = estimate_compression_result("Medium", 500)
        assert result["compression_ratio"] == 0.48
        assert result["compressed_tokens"] == 240

    @pytest.mark.unit
    def test_estimate_complex_returns_expected_ratio(self):
        """Complex tier estimation uses 0.46 ratio."""
        result = estimate_compression_result("Complex", 1000)
        assert result["compression_ratio"] == 0.46
        assert result["compressed_tokens"] == 460

    @pytest.mark.unit
    def test_estimate_flags_cpu_only(self):
        """Estimated results are flagged with cpu_only_estimated."""
        # Acceptance Criterion: "Fallback clearly flagged"
        result = estimate_compression_result("Simple", 100)
        assert result["cpu_only_estimated"] is True

    @pytest.mark.unit
    def test_estimate_zero_execution_time(self):
        """Estimated results have zero execution time."""
        result = estimate_compression_result("Simple", 100)
        assert result["execution_time_seconds"] == 0

    @pytest.mark.unit
    def test_estimate_notes_mention_unavailable(self):
        """Semantic notes explain LLMLingua was not executed."""
        result = estimate_compression_result("Medium", 200)
        assert "not executed" in result["semantic_preservation_notes"].lower()

    @pytest.mark.unit
    def test_estimate_invalid_tier_raises_value_error(self):
        """Raises ValueError for unknown tier."""
        with pytest.raises(ValueError, match="Unknown tier"):
            estimate_compression_result("Ultra", 500)


# ═══════════════════════════════════════════════════════════════════
# 5.3 — ERROR PATH TESTS
# ═══════════════════════════════════════════════════════════════════


class TestAnalyzeLlmlinguaResults:
    """Tests for analyze_llmlingua_results()."""

    @pytest.mark.unit
    def test_analyze_missing_file_returns_error(self, tmp_path):
        """Returns error dict when file doesn't exist."""
        missing = tmp_path / "nonexistent.md"
        result = analyze_llmlingua_results(
            missing, "Simple", None, "cpu", False, None
        )
        assert "error" in result
        assert "Failed to read" in result["error"]

    @pytest.mark.unit
    def test_analyze_with_none_compressor_uses_estimation(self, samples_dir):
        """Uses estimation fallback when compressor is None."""
        # Acceptance Criterion: "Fallback clearly flagged"
        file_path = samples_dir / "simple.md"
        result = analyze_llmlingua_results(
            file_path, "Simple", None, "cpu", False, None
        )
        assert result.get("cpu_only_estimated") is True
        assert "metrics" in result

    @pytest.mark.unit
    def test_analyze_with_failing_compressor_falls_back(
        self, samples_dir, failing_compressor
    ):
        """Falls back to estimation when compression fails."""
        file_path = samples_dir / "simple.md"
        result = analyze_llmlingua_results(
            file_path, "Simple", failing_compressor, "cpu", False, None
        )
        assert result.get("cpu_only_estimated") is True

    @pytest.mark.unit
    def test_analyze_successful_compression(self, samples_dir, mock_compressor):
        """Returns full metrics on successful compression."""
        # Acceptance Criterion: "Compression metrics recorded"
        file_path = samples_dir / "simple.md"
        result = analyze_llmlingua_results(
            file_path, "Simple", mock_compressor, "mps", True,
            "Apple Metal Performance Shaders"
        )
        assert "metrics" in result
        assert "error" not in result
        assert result.get("cpu_only_estimated") is not True
        assert result["metrics"]["compression_ratio"] == 0.4823

    @pytest.mark.unit
    def test_analyze_records_device_info(self, samples_dir, mock_compressor):
        """Result includes device and GPU information."""
        # Acceptance Criterion: "GPU availability detected and reported"
        file_path = samples_dir / "simple.md"
        result = analyze_llmlingua_results(
            file_path, "Simple", mock_compressor, "mps", True,
            "Apple Metal Performance Shaders"
        )
        assert result["device_used"] == "mps"
        assert result["gpu_available"] is True
        assert "Metal" in result["gpu_name"]


# ═══════════════════════════════════════════════════════════════════
# BUILD & COMPARISON TESTS
# ═══════════════════════════════════════════════════════════════════


class TestBuildDocumentResult:
    """Tests for build_document_result()."""

    @pytest.mark.unit
    def test_build_includes_all_required_keys(self):
        """Result dict contains all required schema keys."""
        # Acceptance Criterion: "Results saved with valid JSON structure"
        metrics = {
            "original_tokens": 100,
            "compressed_tokens": 50,
            "compression_ratio": 0.50,
            "execution_time_seconds": 1.5,
        }
        result = build_document_result(
            "Simple", Path("test.md"), "mps", True,
            "Apple MPS", metrics, "preview text", "notes"
        )
        assert result["tier"] == "Simple"
        assert result["device_used"] == "mps"
        assert result["gpu_available"] is True
        assert "metrics" in result
        assert result["compressed_text_preview"] == "preview text"

    @pytest.mark.unit
    def test_build_propagates_estimated_flag(self):
        """Propagates cpu_only_estimated flag from metrics."""
        # Acceptance Criterion: "Fallback clearly flagged"
        metrics = {
            "original_tokens": 100,
            "compressed_tokens": 52,
            "compression_ratio": 0.52,
            "execution_time_seconds": 0,
            "cpu_only_estimated": True,
        }
        result = build_document_result(
            "Simple", Path("test.md"), "cpu", False,
            None, metrics, "preview", "estimated notes"
        )
        assert result.get("cpu_only_estimated") is True

    @pytest.mark.unit
    def test_build_no_estimated_flag_when_real(self):
        """Does not include cpu_only_estimated when not estimated."""
        metrics = {
            "original_tokens": 100,
            "compressed_tokens": 48,
            "compression_ratio": 0.48,
            "execution_time_seconds": 2.1,
        }
        result = build_document_result(
            "Simple", Path("test.md"), "mps", True,
            "Apple MPS", metrics, "preview", "notes"
        )
        assert "cpu_only_estimated" not in result


class TestBuildComparisonTable:
    """Tests for build_comparison_table()."""

    # Acceptance Criterion: "Comparison table populated with actual
    # compression ratios from results"

    @pytest.mark.unit
    def test_comparison_table_has_correct_row_count(self, three_document_results):
        """Comparison table has one row per document."""
        # Acceptance Criterion: "Comparison table populated"
        table = build_comparison_table(three_document_results)
        assert len(table) == 3

    @pytest.mark.unit
    def test_comparison_table_row_keys(self, three_document_results):
        """Each row contains required keys."""
        table = build_comparison_table(three_document_results)
        for row in table:
            assert "tier" in row
            assert "original_tokens" in row
            assert "compressed_tokens" in row
            assert "llmlingua_ratio" in row
            assert "target_haiku_ratio" in row

    @pytest.mark.unit
    def test_comparison_table_haiku_targets_correct(self, three_document_results):
        """Haiku target ratios match HAIKU_TARGET_RATIOS constant."""
        table = build_comparison_table(three_document_results)
        for row in table:
            expected = HAIKU_TARGET_RATIOS.get(row["tier"])
            assert row["target_haiku_ratio"] == expected

    @pytest.mark.unit
    def test_comparison_table_skips_errored_documents(self):
        """Errored documents are excluded from comparison table."""
        docs = [
            {"tier": "Simple", "error": "file not found"},
            {
                "tier": "Medium",
                "metrics": {
                    "original_tokens": 400,
                    "compressed_tokens": 200,
                    "compression_ratio": 0.50,
                    "execution_time_seconds": 3.0,
                },
            },
        ]
        table = build_comparison_table(docs)
        assert len(table) == 1
        assert table[0]["tier"] == "Medium"

    @pytest.mark.unit
    def test_comparison_table_empty_input(self):
        """Empty documents list produces empty table."""
        table = build_comparison_table([])
        assert table == []


# ═══════════════════════════════════════════════════════════════════
# 5.4 — LOG OUTPUT TESTS
# ═══════════════════════════════════════════════════════════════════


class TestLoggingOutput:
    """Tests verifying log messages are emitted correctly."""

    @pytest.mark.unit
    def test_detect_gpu_logs_detection_started(self, caplog):
        """detect_gpu_availability logs 'GPU detection started'."""
        with caplog.at_level(logging.INFO):
            detect_gpu_availability()
        assert "GPU detection started" in caplog.text

    @pytest.mark.unit
    def test_compress_document_logs_started(self, caplog, mock_compressor, sample_text):
        """compress_document logs 'compression started'."""
        with caplog.at_level(logging.INFO):
            compress_document(mock_compressor, sample_text, COMPRESSION_CONFIG)
        assert "compression started" in caplog.text.lower()

    @pytest.mark.unit
    def test_compress_document_logs_complete(self, caplog, mock_compressor, sample_text):
        """compress_document logs 'compression complete'."""
        with caplog.at_level(logging.INFO):
            compress_document(mock_compressor, sample_text, COMPRESSION_CONFIG)
        assert "compression complete" in caplog.text.lower()

    @pytest.mark.unit
    def test_estimate_logs_info(self, caplog):
        """estimate_compression_result logs estimation details."""
        with caplog.at_level(logging.INFO):
            estimate_compression_result("Simple", 100)
        assert "estimated compression" in caplog.text.lower()

    @pytest.mark.unit
    def test_comparison_table_logs_row_count(self, caplog, three_document_results):
        """build_comparison_table logs the number of rows built."""
        with caplog.at_level(logging.INFO):
            build_comparison_table(three_document_results)
        assert "3 rows" in caplog.text

    @pytest.mark.unit
    def test_analyze_logs_analysis_started(self, caplog, samples_dir):
        """analyze_llmlingua_results logs 'Analysis started'."""
        with caplog.at_level(logging.INFO):
            analyze_llmlingua_results(
                samples_dir / "simple.md", "Simple", None, "cpu", False, None
            )
        assert "Analysis started" in caplog.text


# ═══════════════════════════════════════════════════════════════════
# 5.5 — PIPELINE & USE CASE TESTS
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.usefixtures("mock_compressor_init")
class TestRunBaseline:
    """Tests for run_baseline() orchestration function."""

    @pytest.mark.unit
    def test_run_baseline_missing_raw_metrics_raises(self, samples_dir, tmp_path):
        """Raises FileNotFoundError when raw_metrics.json is missing."""
        missing = tmp_path / "nonexistent_metrics.json"
        with pytest.raises(FileNotFoundError, match="raw_metrics.json"):
            run_baseline(samples_dir, missing, tmp_path / "out.json")

    @pytest.mark.unit
    def test_run_baseline_missing_samples_raises(self, raw_metrics_file, tmp_path):
        """Raises FileNotFoundError when samples directory is missing."""
        missing = tmp_path / "no_such_dir"
        with pytest.raises(FileNotFoundError, match="samples"):
            run_baseline(missing, raw_metrics_file, tmp_path / "out.json")

    @pytest.mark.unit
    def test_run_baseline_produces_json_output(
        self, samples_dir, raw_metrics_file, tmp_path
    ):
        """run_baseline writes valid JSON to the output path."""
        # Acceptance Criterion: "Results saved to benchmarks/llmlingua_baseline.json
        # with valid JSON structure"
        output = tmp_path / "llmlingua_baseline.json"
        results = run_baseline(samples_dir, raw_metrics_file, output)

        assert output.exists()
        loaded = json.loads(output.read_text())
        assert loaded["version"] == "0.0.3c"

    @pytest.mark.unit
    def test_run_baseline_has_required_top_level_keys(
        self, samples_dir, raw_metrics_file, tmp_path
    ):
        """Output contains all required top-level keys."""
        # Acceptance Criterion: "Configuration parameters exactly recorded"
        output = tmp_path / "output.json"
        results = run_baseline(samples_dir, raw_metrics_file, output)

        assert "version" in results
        assert "llmlingua_version" in results
        assert "configuration" in results
        assert "hardware" in results
        assert "documents" in results
        assert "comparison_table" in results

    @pytest.mark.unit
    def test_run_baseline_configuration_matches_spec(
        self, samples_dir, raw_metrics_file, tmp_path
    ):
        """Recorded configuration matches COMPRESSION_CONFIG."""
        # Acceptance Criterion: "Configuration parameters exactly recorded"
        output = tmp_path / "output.json"
        results = run_baseline(samples_dir, raw_metrics_file, output)

        assert results["configuration"] == COMPRESSION_CONFIG

    @pytest.mark.unit
    def test_run_baseline_processes_all_three_documents(
        self, samples_dir, raw_metrics_file, tmp_path
    ):
        """All three sample documents are processed."""
        # Acceptance Criterion: "All three sample documents processed"
        output = tmp_path / "output.json"
        results = run_baseline(samples_dir, raw_metrics_file, output)

        assert len(results["documents"]) == 3
        tiers = {doc["tier"] for doc in results["documents"]}
        assert tiers == {"Simple", "Medium", "Complex"}

    @pytest.mark.unit
    def test_run_baseline_includes_hardware_info(
        self, samples_dir, raw_metrics_file, tmp_path
    ):
        """Hardware section includes device and GPU fields."""
        # Acceptance Criterion: "GPU availability detected and reported"
        output = tmp_path / "output.json"
        results = run_baseline(samples_dir, raw_metrics_file, output)

        hw = results["hardware"]
        assert "device_used" in hw
        assert "gpu_available" in hw
        assert "gpu_name" in hw

    @pytest.mark.unit
    def test_run_baseline_comparison_table_populated(
        self, samples_dir, raw_metrics_file, tmp_path
    ):
        """Comparison table is populated with entries."""
        # Acceptance Criterion: "Comparison table populated"
        output = tmp_path / "output.json"
        results = run_baseline(samples_dir, raw_metrics_file, output)

        assert len(results["comparison_table"]) == 3


@pytest.mark.usefixtures("mock_compressor_init")
class TestEndToEndUseCase:
    """End-to-end use case test simulating the full workflow."""

    @pytest.mark.unit
    def test_full_baseline_workflow_with_estimation(
        self, samples_dir, raw_metrics_file, tmp_path
    ):
        """
        Full use case: run the baseline pipeline end-to-end.

        Use Case: "Developer runs the llmlingua_baseline.py script, which
        verifies raw_metrics.json exists, detects GPU/CPU, initializes
        LLMLingua with default configuration (50% compression rate, v1
        algorithm), compresses all 3 sample documents, records metrics
        (original tokens, compressed tokens, ratio, time), and saves
        results to benchmarks/llmlingua_baseline.json."

        In this test environment, LLMLingua is not installed, so the
        fallback estimation path is exercised for all documents.
        """
        output = tmp_path / "llmlingua_baseline.json"

        # Run the full pipeline
        results = run_baseline(samples_dir, raw_metrics_file, output)

        # Verify output file exists and is valid JSON
        assert output.exists()
        loaded = json.loads(output.read_text())

        # Verify version and config
        assert loaded["version"] == "0.0.3c"
        assert loaded["configuration"]["compression_rate"] == 0.5
        assert loaded["configuration"]["use_llmlingua2"] is False

        # Verify all 3 documents processed
        assert len(loaded["documents"]) == 3
        for doc in loaded["documents"]:
            assert "tier" in doc
            assert "metrics" in doc
            m = doc["metrics"]
            assert "original_tokens" in m
            assert "compressed_tokens" in m
            assert "compression_ratio" in m
            assert "execution_time_seconds" in m
            # In test env without LLMLingua, all should be estimated
            assert doc.get("cpu_only_estimated") is True

        # Verify comparison table
        assert len(loaded["comparison_table"]) == 3
        for row in loaded["comparison_table"]:
            assert row["estimated"] is True
            assert row["target_haiku_ratio"] in [
                "35-40%", "40-50%", "45-55%"
            ]

        # Verify hardware info
        assert "hardware" in loaded
        assert isinstance(loaded["hardware"]["gpu_available"], bool)


# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION CONSTANT TESTS
# ═══════════════════════════════════════════════════════════════════


class TestConfigurationConstants:
    """Tests verifying configuration constants match the spec."""

    @pytest.mark.unit
    def test_compression_config_rate(self):
        """Compression rate is 0.5 per spec."""
        # Acceptance Criterion: "Configuration parameters exactly recorded"
        assert COMPRESSION_CONFIG["compression_rate"] == 0.5

    @pytest.mark.unit
    def test_compression_config_uses_v1(self):
        """use_llmlingua2 is False per spec (v1 algorithm)."""
        assert COMPRESSION_CONFIG["use_llmlingua2"] is False

    @pytest.mark.unit
    def test_compression_config_full_context(self):
        """context_budget is -1 per spec (full context)."""
        assert COMPRESSION_CONFIG["context_budget"] == -1

    @pytest.mark.unit
    def test_estimated_ratios_all_tiers(self):
        """Estimated ratios exist for all three tiers."""
        assert "Simple" in ESTIMATED_COMPRESSION_RATIOS
        assert "Medium" in ESTIMATED_COMPRESSION_RATIOS
        assert "Complex" in ESTIMATED_COMPRESSION_RATIOS

    @pytest.mark.unit
    def test_haiku_targets_all_tiers(self):
        """Haiku target ratios exist for all three tiers."""
        assert "Simple" in HAIKU_TARGET_RATIOS
        assert "Medium" in HAIKU_TARGET_RATIOS
        assert "Complex" in HAIKU_TARGET_RATIOS

    @pytest.mark.unit
    def test_sample_files_three_entries(self):
        """SAMPLE_FILES has exactly 3 entries."""
        assert len(SAMPLE_FILES) == 3

    @pytest.mark.unit
    def test_sample_files_tiers(self):
        """SAMPLE_FILES covers Simple, Medium, Complex."""
        tiers = {tier for _, tier in SAMPLE_FILES}
        assert tiers == {"Simple", "Medium", "Complex"}


# ═══════════════════════════════════════════════════════════════════
# RAW METRICS TOKEN COUNT CONSISTENCY TESTS
# ═══════════════════════════════════════════════════════════════════


class TestRawMetricsTokenConsistency:
    """Tests verifying raw_metrics.json token counts flow correctly."""

    # Acceptance Criterion: "Compression metrics recorded: original_tokens"
    # This ensures original_tokens from v0.0.3b are used consistently.

    @pytest.mark.unit
    def test_analyze_uses_raw_metrics_count_when_provided(self, samples_dir):
        """analyze_llmlingua_results uses raw_metrics token count over local count."""
        # Acceptance Criterion: "Compression metrics recorded: original_tokens"
        file_path = samples_dir / "simple.md"
        # Pass a known count that differs from what local counting would produce
        result = analyze_llmlingua_results(
            file_path, "Simple", None, "cpu", False, None,
            raw_metrics_token_count=101,
        )
        assert result["metrics"]["original_tokens"] == 101

    @pytest.mark.unit
    def test_analyze_falls_back_to_local_when_none(self, samples_dir):
        """Falls back to local counting when raw_metrics count is None."""
        # Acceptance Criterion: "Compression metrics recorded: original_tokens"
        file_path = samples_dir / "simple.md"
        result = analyze_llmlingua_results(
            file_path, "Simple", None, "cpu", False, None,
            raw_metrics_token_count=None,
        )
        # Should still have a positive token count from local counting
        assert result["metrics"]["original_tokens"] > 0

    @pytest.mark.unit
    def test_run_baseline_passes_raw_metrics_tokens(
        self, samples_dir, raw_metrics_file, tmp_path, mock_compressor_init
    ):
        """run_baseline reads token counts from raw_metrics.json and passes them."""
        # Acceptance Criterion: "Compression metrics recorded: original_tokens"
        output = tmp_path / "output.json"
        results = run_baseline(samples_dir, raw_metrics_file, output)

        # Verify token counts match what's in raw_metrics_file
        for doc in results["documents"]:
            tier = doc["tier"]
            if tier == "Simple":
                assert doc["metrics"]["original_tokens"] == 101
            elif tier == "Medium":
                assert doc["metrics"]["original_tokens"] == 443
            elif tier == "Complex":
                assert doc["metrics"]["original_tokens"] == 1589

    @pytest.mark.unit
    def test_run_baseline_handles_malformed_raw_metrics(
        self, samples_dir, tmp_path, mock_compressor_init
    ):
        """run_baseline handles malformed raw_metrics gracefully."""
        # Write malformed JSON that's valid JSON but missing expected structure
        raw_path = tmp_path / "raw_metrics.json"
        raw_path.write_text('{"version": "0.0.3b"}')
        output = tmp_path / "output.json"

        # Should not raise; falls back to local counting
        results = run_baseline(samples_dir, raw_path, output)
        assert len(results["documents"]) == 3
        # Token counts should still be positive (from local counting)
        for doc in results["documents"]:
            assert doc["metrics"]["original_tokens"] > 0

    @pytest.mark.unit
    def test_analyze_logs_raw_metrics_source(self, caplog, samples_dir):
        """Logs indicate token count source as raw_metrics.json when provided."""
        file_path = samples_dir / "simple.md"
        with caplog.at_level(logging.INFO):
            analyze_llmlingua_results(
                file_path, "Simple", None, "cpu", False, None,
                raw_metrics_token_count=101,
            )
        assert "from raw_metrics.json" in caplog.text

    @pytest.mark.unit
    def test_analyze_logs_local_count_source(self, caplog, samples_dir):
        """Logs indicate token count source as local when no raw_metrics provided."""
        file_path = samples_dir / "simple.md"
        with caplog.at_level(logging.INFO):
            analyze_llmlingua_results(
                file_path, "Simple", None, "cpu", False, None,
                raw_metrics_token_count=None,
            )
        assert "locally counted" in caplog.text

    @pytest.mark.unit
    def test_compressed_tokens_still_locally_counted(
        self, samples_dir, mock_compressor
    ):
        """Compressed tokens are always locally counted (not from raw_metrics)."""
        # Acceptance Criterion: "Compression metrics recorded: compressed_tokens"
        file_path = samples_dir / "simple.md"
        result = analyze_llmlingua_results(
            file_path, "Simple", mock_compressor, "cpu", False, None,
            raw_metrics_token_count=101,
        )
        # original should be from raw_metrics, compressed from local count
        assert result["metrics"]["original_tokens"] == 101
        assert result["metrics"]["compressed_tokens"] > 0
        # compressed_tokens should differ from original (it's the mock output)
        assert result["metrics"]["compressed_tokens"] != 101
