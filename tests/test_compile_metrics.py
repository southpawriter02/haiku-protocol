"""Tests for benchmarks/compile_metrics.py.

Unit test suite covering JSON loading, metrics merging, markdown report
generation, and the full compilation pipeline for v0.0.3d — Metrics
Documentation & Reporting.
"""

import json
import logging
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# ── Ensure benchmarks/ is importable ──
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "benchmarks"))

from compile_metrics import (
    HAIKU_TARGETS,
    generate_markdown_report,
    load_json_file,
    merge_metrics,
    main,
)


# ── Fixtures ──


@pytest.fixture
def raw_metrics_data():
    """Minimal raw_metrics.json structure for testing."""
    return {
        "version": "0.0.3b",
        "tokenizer": "tiktoken",
        "documents": [
            {
                "tier": "Simple",
                "file_path": "benchmarks/samples/simple.md",
                "metrics": {
                    "character_count": 500,
                    "word_count": 80,
                    "token_count": 101,
                    "sentence_count": 5,
                    "content_density_score": 0.20,
                },
                "content_analysis": {
                    "number_of_procedures": 1,
                    "number_of_prerequisites": 0,
                    "number_of_commands": 2,
                    "number_of_warnings": 0,
                    "number_of_conditions": 0,
                },
            },
            {
                "tier": "Medium",
                "file_path": "benchmarks/samples/medium.md",
                "metrics": {
                    "character_count": 2500,
                    "word_count": 400,
                    "token_count": 443,
                    "sentence_count": 20,
                    "content_density_score": 0.30,
                },
                "content_analysis": {
                    "number_of_procedures": 3,
                    "number_of_prerequisites": 2,
                    "number_of_commands": 5,
                    "number_of_warnings": 1,
                    "number_of_conditions": 2,
                },
            },
            {
                "tier": "Complex",
                "file_path": "benchmarks/samples/complex.md",
                "metrics": {
                    "character_count": 10000,
                    "word_count": 1500,
                    "token_count": 1589,
                    "sentence_count": 70,
                    "content_density_score": 0.45,
                },
                "content_analysis": {
                    "number_of_procedures": 8,
                    "number_of_prerequisites": 5,
                    "number_of_commands": 15,
                    "number_of_warnings": 3,
                    "number_of_conditions": 7,
                },
            },
        ],
    }


@pytest.fixture
def llmlingua_data():
    """Minimal llmlingua_baseline.json structure for testing."""
    return {
        "version": "0.0.3c",
        "configuration": {
            "algorithm": "llmlingua",
            "target_ratio": 0.5,
        },
        "documents": [
            {
                "tier": "Simple",
                "metrics": {
                    "compression_ratio": 0.52,
                    "original_tokens": 101,
                    "compressed_tokens": 53,
                    "execution_time_seconds": 0.3,
                },
            },
            {
                "tier": "Medium",
                "metrics": {
                    "compression_ratio": 0.48,
                    "original_tokens": 443,
                    "compressed_tokens": 213,
                    "execution_time_seconds": 1.2,
                },
            },
            {
                "tier": "Complex",
                "metrics": {
                    "compression_ratio": 0.46,
                    "original_tokens": 1589,
                    "compressed_tokens": 731,
                    "execution_time_seconds": 5.5,
                },
            },
        ],
    }


@pytest.fixture
def merged_baseline(raw_metrics_data, llmlingua_data):
    """Pre-merged baseline_metrics for report tests."""
    return merge_metrics(raw_metrics_data, llmlingua_data)


@pytest.fixture
def json_file(tmp_path):
    """Helper to write a JSON file in tmp_path and return its path."""
    def _write(filename, data):
        path = tmp_path / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return path
    return _write


# ── HAIKU_TARGETS Tests ──


class TestHaikuTargets:
    """Tests for HAIKU_TARGETS constants."""

    @pytest.mark.unit
    def test_haiku_targets_has_three_tiers(self):
        """All three expected tiers are defined."""
        assert "Simple" in HAIKU_TARGETS
        assert "Medium" in HAIKU_TARGETS
        assert "Complex" in HAIKU_TARGETS

    @pytest.mark.unit
    def test_haiku_targets_min_less_than_max(self):
        """For each tier, min is strictly less than max."""
        for tier, targets in HAIKU_TARGETS.items():
            assert targets["min"] < targets["max"], (
                "%s: min (%.2f) not < max (%.2f)"
                % (tier, targets["min"], targets["max"])
            )

    @pytest.mark.unit
    def test_haiku_targets_have_description(self):
        """Each tier has a non-empty description."""
        for tier, targets in HAIKU_TARGETS.items():
            assert targets["description"], "%s has no description" % tier


# ── load_json_file Tests ──


class TestLoadJsonFile:
    """Tests for load_json_file function."""

    @pytest.mark.unit
    def test_load_valid_json(self, json_file):
        """Valid JSON file is loaded and parsed correctly."""
        # Arrange
        data = {"key": "value", "nested": {"a": 1}}
        path = json_file("valid.json", data)

        # Act
        result = load_json_file(path)

        # Assert
        assert result == data

    @pytest.mark.unit
    def test_load_missing_file_returns_none(self, tmp_path):
        """Missing file returns None."""
        # Arrange
        path = tmp_path / "nonexistent.json"

        # Act
        result = load_json_file(path)

        # Assert
        assert result is None

    @pytest.mark.unit
    def test_load_invalid_json_returns_none(self, tmp_path):
        """Invalid JSON content returns None."""
        # Arrange
        path = tmp_path / "invalid.json"
        path.write_text("not { valid json }", encoding="utf-8")

        # Act
        result = load_json_file(path)

        # Assert
        assert result is None

    @pytest.mark.unit
    def test_load_empty_file_returns_none(self, tmp_path):
        """Empty file returns None (invalid JSON)."""
        # Arrange
        path = tmp_path / "empty.json"
        path.write_text("", encoding="utf-8")

        # Act
        result = load_json_file(path)

        # Assert
        assert result is None

    @pytest.mark.unit
    def test_load_logs_info_on_success(self, json_file, caplog):
        """Successful load emits INFO log messages."""
        # Arrange
        path = json_file("test.json", {"x": 1})

        # Act
        with caplog.at_level(logging.INFO):
            load_json_file(path)

        # Assert
        assert "Loading JSON file" in caplog.text
        assert "Successfully loaded" in caplog.text

    @pytest.mark.unit
    def test_load_logs_error_on_missing_file(self, tmp_path, caplog):
        """Missing file emits ERROR log."""
        # Arrange
        path = tmp_path / "missing.json"

        # Act
        with caplog.at_level(logging.ERROR):
            load_json_file(path)

        # Assert
        assert "File not found" in caplog.text


# ── merge_metrics Tests ──


class TestMergeMetrics:
    """Tests for merge_metrics function."""

    @pytest.mark.unit
    def test_merge_returns_all_three_documents(
        self, raw_metrics_data, llmlingua_data
    ):
        """Merge produces exactly 3 merged documents."""
        # Act
        result = merge_metrics(raw_metrics_data, llmlingua_data)

        # Assert
        assert result is not None
        assert len(result["documents"]) == 3

    @pytest.mark.unit
    def test_merge_version_is_0_0_3d(
        self, raw_metrics_data, llmlingua_data
    ):
        """Merged result has version 0.0.3d."""
        # Act
        result = merge_metrics(raw_metrics_data, llmlingua_data)

        # Assert
        assert result["version"] == "0.0.3d"

    @pytest.mark.unit
    def test_merge_has_timestamp(self, raw_metrics_data, llmlingua_data):
        """Merged result includes a timestamp."""
        # Act
        result = merge_metrics(raw_metrics_data, llmlingua_data)

        # Assert
        assert "timestamp" in result
        assert len(result["timestamp"]) > 0

    @pytest.mark.unit
    def test_merge_document_has_required_keys(
        self, raw_metrics_data, llmlingua_data
    ):
        """Each merged document contains the required keys."""
        # Arrange
        required_keys = {
            "tier",
            "source_file",
            "raw_metrics",
            "content_analysis",
            "llmlingua_baseline",
            "haiku_protocol_targets",
            "analysis_notes",
        }

        # Act
        result = merge_metrics(raw_metrics_data, llmlingua_data)

        # Assert
        for doc in result["documents"]:
            assert required_keys.issubset(doc.keys()), (
                "Missing keys in %s tier: %s"
                % (doc.get("tier"), required_keys - doc.keys())
            )

    @pytest.mark.unit
    def test_merge_improvement_calculation_simple(
        self, raw_metrics_data, llmlingua_data
    ):
        """Simple tier improvement = (llmlingua_ratio - haiku_min) * 100.

        # Acceptance Criterion: "improvement_vs_llmlingua percentage
        #   computed correctly"
        """
        # Arrange
        # Simple: llmlingua = 0.52, haiku min = 0.30
        expected = round((0.52 - 0.30) * 100, 1)  # 22.0

        # Act
        result = merge_metrics(raw_metrics_data, llmlingua_data)

        # Assert
        simple_doc = result["documents"][0]
        actual = simple_doc["haiku_protocol_targets"][
            "improvement_vs_llmlingua_percent"
        ]
        assert actual == expected

    @pytest.mark.unit
    def test_merge_improvement_calculation_complex(
        self, raw_metrics_data, llmlingua_data
    ):
        """Complex tier improvement = (0.46 - 0.45) * 100 = 1.0."""
        # Act
        result = merge_metrics(raw_metrics_data, llmlingua_data)

        # Assert
        complex_doc = result["documents"][2]
        actual = complex_doc["haiku_protocol_targets"][
            "improvement_vs_llmlingua_percent"
        ]
        assert actual == 1.0

    @pytest.mark.unit
    def test_merge_llmlingua_baseline_keys(
        self, raw_metrics_data, llmlingua_data
    ):
        """Each merged doc's llmlingua_baseline has required keys."""
        # Arrange
        required = {
            "compression_ratio",
            "original_tokens",
            "compressed_tokens",
            "execution_time_seconds",
        }

        # Act
        result = merge_metrics(raw_metrics_data, llmlingua_data)

        # Assert
        for doc in result["documents"]:
            assert required.issubset(doc["llmlingua_baseline"].keys())

    @pytest.mark.unit
    def test_merge_haiku_targets_keys(
        self, raw_metrics_data, llmlingua_data
    ):
        """Each merged doc's haiku_protocol_targets has required keys."""
        # Arrange
        required = {
            "target_compression_ratio_min",
            "target_compression_ratio_max",
            "target_description",
            "improvement_vs_llmlingua_percent",
        }

        # Act
        result = merge_metrics(raw_metrics_data, llmlingua_data)

        # Assert
        for doc in result["documents"]:
            assert required.issubset(
                doc["haiku_protocol_targets"].keys()
            )

    @pytest.mark.unit
    def test_merge_missing_raw_documents_returns_none(
        self, llmlingua_data
    ):
        """Missing documents key in raw_metrics returns None."""
        # Arrange
        raw = {"version": "0.0.3b"}

        # Act
        result = merge_metrics(raw, llmlingua_data)

        # Assert
        assert result is None

    @pytest.mark.unit
    def test_merge_missing_llmlingua_documents_returns_none(
        self, raw_metrics_data
    ):
        """Missing documents key in llmlingua returns None."""
        # Arrange
        llmlingua = {"version": "0.0.3c"}

        # Act
        result = merge_metrics(raw_metrics_data, llmlingua)

        # Assert
        assert result is None

    @pytest.mark.unit
    def test_merge_tier_mismatch_skips_document(self, raw_metrics_data):
        """Document with no matching LLMLingua tier is skipped."""
        # Arrange
        llmlingua = {
            "version": "0.0.3c",
            "configuration": {},
            "documents": [
                {
                    "tier": "Simple",
                    "metrics": {
                        "compression_ratio": 0.52,
                        "original_tokens": 101,
                        "compressed_tokens": 53,
                        "execution_time_seconds": 0.3,
                    },
                },
                # Missing Medium and Complex
            ],
        }

        # Act
        result = merge_metrics(raw_metrics_data, llmlingua)

        # Assert
        assert result is not None
        assert len(result["documents"]) == 1
        assert result["documents"][0]["tier"] == "Simple"

    @pytest.mark.unit
    def test_merge_tier_mismatch_logs_warning(
        self, raw_metrics_data, caplog
    ):
        """Missing tier in LLMLingua results emits warning."""
        # Arrange
        llmlingua = {
            "version": "0.0.3c",
            "configuration": {},
            "documents": [
                {
                    "tier": "Simple",
                    "metrics": {
                        "compression_ratio": 0.52,
                        "original_tokens": 101,
                        "compressed_tokens": 53,
                        "execution_time_seconds": 0.3,
                    },
                },
            ],
        }

        # Act
        with caplog.at_level(logging.WARNING):
            merge_metrics(raw_metrics_data, llmlingua)

        # Assert
        assert "No LLMLingua results found for Medium tier" in caplog.text

    @pytest.mark.unit
    def test_merge_includes_metadata_fields(
        self, raw_metrics_data, llmlingua_data
    ):
        """Merged result includes encoding, tokenizer, and source refs."""
        # Act
        result = merge_metrics(raw_metrics_data, llmlingua_data)

        # Assert
        assert result["encoding"] == "cl100k_base"
        assert result["tokenizer"] == "tiktoken"
        assert result["raw_metrics_source"] == "v0.0.3b"
        assert result["llmlingua_metrics_source"] == "v0.0.3c"

    @pytest.mark.unit
    def test_merge_includes_llmlingua_configuration(
        self, raw_metrics_data, llmlingua_data
    ):
        """LLMLingua configuration is carried through to baseline."""
        # Act
        result = merge_metrics(raw_metrics_data, llmlingua_data)

        # Assert
        assert result["llmlingua_configuration"] == {
            "algorithm": "llmlingua",
            "target_ratio": 0.5,
        }

    @pytest.mark.unit
    def test_merge_analysis_notes_contains_numbers(
        self, raw_metrics_data, llmlingua_data
    ):
        """Analysis notes contain actual numbers, not placeholders."""
        # Act
        result = merge_metrics(raw_metrics_data, llmlingua_data)

        # Assert
        for doc in result["documents"]:
            notes = doc["analysis_notes"]
            assert "N/A" not in notes or "target" not in notes.lower()
            assert "LLMLingua achieves" in notes
            assert "Haiku Protocol should target" in notes

    @pytest.mark.unit
    def test_merge_logs_completion_count(
        self, raw_metrics_data, llmlingua_data, caplog
    ):
        """Successful merge logs the count of consolidated documents."""
        # Act
        with caplog.at_level(logging.INFO):
            merge_metrics(raw_metrics_data, llmlingua_data)

        # Assert
        assert "3 documents consolidated" in caplog.text


# ── generate_markdown_report Tests ──


class TestGenerateMarkdownReport:
    """Tests for generate_markdown_report function."""

    @pytest.mark.unit
    def test_report_contains_summary_table(self, merged_baseline):
        """Report includes a markdown summary table."""
        # Act
        report = generate_markdown_report(merged_baseline)

        # Assert
        assert "| Document" in report
        assert "|-------" in report

    @pytest.mark.unit
    def test_report_contains_all_tier_headings(self, merged_baseline):
        """Report has a heading for each tier."""
        # Act
        report = generate_markdown_report(merged_baseline)

        # Assert
        assert "### Simple Tier" in report
        assert "### Medium Tier" in report
        assert "### Complex Tier" in report

    @pytest.mark.unit
    def test_report_contains_raw_metrics_section(self, merged_baseline):
        """Report has 'Raw Metrics' for each document."""
        # Act
        report = generate_markdown_report(merged_baseline)

        # Assert
        assert "**Raw Metrics:**" in report
        assert "Character Count:" in report
        assert "Token Count:" in report

    @pytest.mark.unit
    def test_report_contains_llmlingua_section(self, merged_baseline):
        """Report has 'LLMLingua Compression' for each document."""
        # Act
        report = generate_markdown_report(merged_baseline)

        # Assert
        assert "**LLMLingua Compression:**" in report
        assert "Compression Ratio:" in report

    @pytest.mark.unit
    def test_report_contains_haiku_target_section(self, merged_baseline):
        """Report has 'Haiku Protocol Target' for each document."""
        # Act
        report = generate_markdown_report(merged_baseline)

        # Assert
        assert "**Haiku Protocol Target:**" in report
        assert "Target Compression:" in report
        assert "Improvement vs. LLMLingua:" in report

    @pytest.mark.unit
    def test_report_contains_actual_numbers(self, merged_baseline):
        """Report uses actual numbers, not placeholders.

        # Acceptance Criterion: "README section template or
        #   BASELINE_METRICS_REPORT.md includes actual numbers
        #   (not placeholders)"
        """
        # Act
        report = generate_markdown_report(merged_baseline)

        # Assert
        assert "101" in report  # Simple token count
        assert "443" in report  # Medium token count
        assert "1589" in report  # Complex token count

    @pytest.mark.unit
    def test_report_contains_interpretation_section(self, merged_baseline):
        """Report has 'Interpretation & Next Steps' section."""
        # Act
        report = generate_markdown_report(merged_baseline)

        # Assert
        assert "## Interpretation & Next Steps" in report
        assert "Baseline Performance" in report

    @pytest.mark.unit
    def test_report_empty_input_returns_stub(self):
        """Empty or missing documents produces stub report."""
        # Arrange
        empty = {"documents": []}

        # Act
        report = generate_markdown_report(empty)

        # Assert
        assert "No baseline metrics available" in report

    @pytest.mark.unit
    def test_report_none_input_returns_stub(self):
        """None input produces stub report."""
        # Act
        report = generate_markdown_report(None)

        # Assert
        assert "No baseline metrics available" in report

    @pytest.mark.unit
    def test_report_is_valid_markdown(self, merged_baseline):
        """Report starts with a heading and has non-trivial length."""
        # Act
        report = generate_markdown_report(merged_baseline)

        # Assert
        assert report.startswith("#")
        assert len(report) > 1000


# ── Pipeline / main Tests ──


class TestPipeline:
    """Tests for end-to-end main() pipeline."""

    @pytest.mark.unit
    def test_main_creates_baseline_json(
        self, tmp_path, raw_metrics_data, llmlingua_data
    ):
        """main() creates baseline_metrics.json in the benchmarks dir."""
        # Arrange
        benchmarks_dir = tmp_path / "benchmarks"
        benchmarks_dir.mkdir()

        with open(benchmarks_dir / "raw_metrics.json", "w") as f:
            json.dump(raw_metrics_data, f)
        with open(benchmarks_dir / "llmlingua_baseline.json", "w") as f:
            json.dump(llmlingua_data, f)

        # Use direct function calls (not main()) to test the pipeline
        # against tmp_path, avoiding filesystem coupling.
        raw = load_json_file(benchmarks_dir / "raw_metrics.json")
        llmlingua = load_json_file(
            benchmarks_dir / "llmlingua_baseline.json"
        )
        baseline = merge_metrics(raw, llmlingua)

        output_path = benchmarks_dir / "baseline_metrics.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2)

        # Assert
        assert output_path.exists()
        loaded = json.loads(output_path.read_text())
        assert loaded["version"] == "0.0.3d"
        assert len(loaded["documents"]) == 3

    @pytest.mark.unit
    def test_pipeline_json_is_valid(
        self, tmp_path, raw_metrics_data, llmlingua_data
    ):
        """Generated baseline_metrics.json is valid, parseable JSON.

        # Acceptance Criterion: "JSON file is valid, parseable,
        #   and pretty-printed with indent=2"
        """
        # Arrange
        benchmarks_dir = tmp_path / "benchmarks"
        benchmarks_dir.mkdir()

        with open(benchmarks_dir / "raw_metrics.json", "w") as f:
            json.dump(raw_metrics_data, f)
        with open(benchmarks_dir / "llmlingua_baseline.json", "w") as f:
            json.dump(llmlingua_data, f)

        # Act
        raw = load_json_file(benchmarks_dir / "raw_metrics.json")
        llmlingua = load_json_file(
            benchmarks_dir / "llmlingua_baseline.json"
        )
        baseline = merge_metrics(raw, llmlingua)

        output_path = benchmarks_dir / "baseline_metrics.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2)

        # Assert — re-parse from disk
        with open(output_path, "r") as f:
            reparsed = json.load(f)
        assert reparsed["version"] == "0.0.3d"

    @pytest.mark.unit
    def test_pipeline_all_tiers_present(
        self, raw_metrics_data, llmlingua_data
    ):
        """Pipeline produces all three tiers in output.

        # Acceptance Criterion: "All three documents (Simple, Medium,
        #   Complex) present in merged output with complete metrics"
        """
        # Act
        result = merge_metrics(raw_metrics_data, llmlingua_data)

        # Assert
        tiers = [doc["tier"] for doc in result["documents"]]
        assert "Simple" in tiers
        assert "Medium" in tiers
        assert "Complex" in tiers

    @pytest.mark.unit
    def test_pipeline_report_generation(
        self, raw_metrics_data, llmlingua_data, tmp_path
    ):
        """Pipeline generates markdown report file on disk."""
        # Arrange
        baseline = merge_metrics(raw_metrics_data, llmlingua_data)
        report = generate_markdown_report(baseline)
        report_path = tmp_path / "BASELINE_METRICS_REPORT.md"

        # Act
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        # Assert
        assert report_path.exists()
        content = report_path.read_text()
        assert "Baseline" in content
        assert "Simple" in content


# ── Edge Cases ──


class TestEdgeCases:
    """Edge case tests for robustness."""

    @pytest.mark.unit
    def test_merge_empty_documents_lists_returns_none(self):
        """Empty documents lists in both inputs returns None."""
        # Arrange
        raw = {"version": "0.0.3b", "documents": []}
        llmlingua = {"version": "0.0.3c", "documents": []}

        # Act
        result = merge_metrics(raw, llmlingua)

        # Assert
        assert result is None

    @pytest.mark.unit
    def test_merge_partial_raw_metrics(self, llmlingua_data):
        """Document with missing metrics keys still merges with defaults."""
        # Arrange
        raw = {
            "version": "0.0.3b",
            "tokenizer": "tiktoken",
            "documents": [
                {
                    "tier": "Simple",
                    "metrics": {},
                    "content_analysis": {},
                },
            ],
        }

        # Act
        result = merge_metrics(raw, llmlingua_data)

        # Assert
        assert result is not None
        assert len(result["documents"]) == 1

    @pytest.mark.unit
    def test_merge_unknown_tier_skipped(self, llmlingua_data):
        """Tier not in HAIKU_TARGETS falls back gracefully."""
        # Arrange
        raw = {
            "version": "0.0.3b",
            "tokenizer": "tiktoken",
            "documents": [
                {
                    "tier": "Unknown",
                    "metrics": {"token_count": 50},
                    "content_analysis": {},
                },
            ],
        }

        # Act
        result = merge_metrics(raw, llmlingua_data)

        # Assert — Unknown tier has no LLMLingua match, so skipped
        assert result is not None
        assert len(result["documents"]) == 0

    @pytest.mark.unit
    def test_float_rounding_precision(
        self, raw_metrics_data, llmlingua_data
    ):
        """Improvement percentages are rounded to 1 decimal."""
        # Act
        result = merge_metrics(raw_metrics_data, llmlingua_data)

        # Assert
        for doc in result["documents"]:
            improvement = doc["haiku_protocol_targets"][
                "improvement_vs_llmlingua_percent"
            ]
            # Ensure it's a float rounded to 1 decimal
            assert improvement == round(improvement, 1)

    @pytest.mark.unit
    def test_source_file_relative_paths(
        self, raw_metrics_data, llmlingua_data
    ):
        """Source file uses relative paths.

        # Acceptance Criterion: "All file paths in JSON use relative paths"
        """
        # Act
        result = merge_metrics(raw_metrics_data, llmlingua_data)

        # Assert
        for doc in result["documents"]:
            source = doc["source_file"]
            assert not source.startswith("/"), (
                "Absolute path detected: %s" % source
            )
