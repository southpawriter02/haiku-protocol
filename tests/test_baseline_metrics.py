"""Tests for benchmarks/baseline_metrics.py.

Unit test suite covering token counting, content analysis, primary metrics,
document analysis, and the full analysis pipeline for v0.0.3b — Token
Counting & Raw Metrics Collection.
"""

import json
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Import from benchmarks package
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "benchmarks"))
from baseline_metrics import (
    count_conditions,
    count_commands,
    count_cross_references,
    count_prerequisites,
    count_procedures,
    count_sentences,
    count_tokens,
    count_warnings,
    compute_content_analysis,
    compute_primary_metrics,
    analyze_document,
    analyze_all_samples,
    get_tokenizer,
    get_unique_token_count,
)


# ── Fixtures ──


@pytest.fixture(autouse=True)
def reset_tokenizer_state():
    """Reset module-level tokenizer state between tests.

    The baseline_metrics module caches its tokenizer on first access.
    This fixture ensures each test starts with a clean state.
    """
    import baseline_metrics

    baseline_metrics.TOKENIZER_MODE = "uninitialized"
    baseline_metrics._tiktoken_encoder = None
    baseline_metrics._regex_pattern = None
    yield


@pytest.fixture
def simple_text():
    """Minimal procedural text for testing."""
    return "Step 1: Run the command\n\n```bash\npip install requests\n```\n"


@pytest.fixture
def medium_text():
    """Medium-complexity procedural text with multiple markers."""
    return (
        "# Setup Git\n\n"
        "## Prerequisites\n\n"
        "Before starting, first install Git. Require admin access.\n\n"
        "Step 1: Install Git\n\n"
        "```bash\napt install git\n```\n\n"
        "Step 2: Configure user\n\n"
        "```bash\ngit config user.name 'Dev'\n```\n\n"
        "Warning: Verify credentials before pushing.\n\n"
        "Note: See also the SSH documentation.\n\n"
        "Step 3: If remote is needed, first add origin\n\n"
        "```bash\ngit remote add origin url\n```\n\n"
    )


@pytest.fixture
def samples_dir_with_docs(tmp_path):
    """Create a temporary samples directory with 3 test documents."""
    samples = tmp_path / "samples"
    samples.mkdir()

    (samples / "simple.md").write_text(
        "# Install pip\n\nRun:\n\n```bash\npython -m ensurepip\n```\n"
    )
    (samples / "medium.md").write_text(
        "# Setup\n\n## Prerequisites\n\n"
        "Before starting, first install tools.\n\n"
        "Step 1: Install\n\n```bash\napt install git\n```\n\n"
        "Step 2: Configure\n\n```bash\ngit config user.name\n```\n\n"
        "Warning: Check settings.\n\n"
        "If errors occur, refer to troubleshooting.\n\n"
    )
    (samples / "complex.md").write_text(
        "# Deploy\n\n## Prerequisites\n\n"
        "Before starting, first install tools. Require cluster access.\n\n"
        + "".join(
            "Step %d: Stage %d\n\n```bash\nkubectl apply -f s%d.yaml\n```\n\n"
            "```bash\nkubectl get pods\n```\n\n"
            % (i, i, i)
            for i in range(1, 6)
        )
        + "Warning: Check status. Important: Verify.\n\n"
        "If errors, refer to docs. See also admin guide.\n"
        "When ready, unless failing, continue.\n"
    )

    return samples


# ── Token Counting Tests ──


class TestCountTokens:
    """Tests for count_tokens function."""

    @pytest.mark.unit
    def test_count_tokens_returns_positive_int_for_text(self):
        """Token count for non-empty text is a positive integer.

        # Acceptance Criterion: "Character, word, token, and sentence counts
        #   for all documents verified and recorded"
        """
        # Arrange
        text = "Hello world"

        # Act
        result = count_tokens(text)

        # Assert
        assert isinstance(result, int)
        assert result > 0

    @pytest.mark.unit
    def test_count_tokens_empty_string_returns_zero(self):
        """Empty string produces zero tokens."""
        # Arrange / Act
        result = count_tokens("")

        # Assert
        assert result == 0

    @pytest.mark.unit
    def test_count_tokens_none_raises_value_error(self):
        """None input raises ValueError."""
        with pytest.raises(ValueError, match="None"):
            count_tokens(None)

    @pytest.mark.unit
    def test_count_tokens_longer_text_has_more_tokens(self):
        """Longer text produces more tokens than shorter text."""
        # Arrange
        short = "Hello"
        long_text = "Hello world, this is a much longer piece of text"

        # Act
        short_count = count_tokens(short)
        long_count = count_tokens(long_text)

        # Assert
        assert long_count > short_count

    @pytest.mark.unit
    def test_count_tokens_code_block_tokenized(self):
        """Code blocks are tokenized (not skipped)."""
        # Arrange
        text = "```bash\nkubectl apply -f deployment.yaml\n```"

        # Act
        result = count_tokens(text)

        # Assert
        assert result > 0, "Code blocks should produce tokens"


class TestGetUniqueTokenCount:
    """Tests for get_unique_token_count function."""

    @pytest.mark.unit
    def test_unique_tokens_less_than_or_equal_total(self):
        """Unique token count is always <= total token count.

        # Acceptance Criterion: "Unique token counts calculated and included"
        """
        # Arrange
        text = "the the the dog dog cat"

        # Act
        total = count_tokens(text)
        unique = get_unique_token_count(text)

        # Assert
        assert unique <= total

    @pytest.mark.unit
    def test_unique_tokens_positive_for_text(self):
        """Non-empty text has at least one unique token."""
        # Act
        result = get_unique_token_count("Hello world")

        # Assert
        assert result > 0

    @pytest.mark.unit
    def test_unique_tokens_none_raises_value_error(self):
        """None input raises ValueError."""
        with pytest.raises(ValueError, match="None"):
            get_unique_token_count(None)

    @pytest.mark.unit
    def test_unique_tokens_repeated_text_fewer_unique(self):
        """Highly repetitive text has fewer unique tokens than diverse text."""
        # Arrange
        repetitive = "dog dog dog dog dog dog dog dog"
        diverse = "cat bird fish dog snake horse frog bee"

        # Act
        rep_unique = get_unique_token_count(repetitive)
        div_unique = get_unique_token_count(diverse)

        # Assert
        assert rep_unique < div_unique


# ── Sentence Counting Tests ──


class TestCountSentences:
    """Tests for count_sentences function."""

    @pytest.mark.unit
    def test_count_sentences_single_sentence(self):
        """Single sentence ending with period counts as 1."""
        assert count_sentences("Hello world.") == 1

    @pytest.mark.unit
    def test_count_sentences_multiple_sentences(self):
        """Multiple sentences are counted correctly."""
        text = "First sentence. Second sentence. Third one!"
        assert count_sentences(text) == 3

    @pytest.mark.unit
    def test_count_sentences_question_mark(self):
        """Question marks are recognized as sentence terminators."""
        text = "Is this working? Yes it is."
        assert count_sentences(text) == 2

    @pytest.mark.unit
    def test_count_sentences_empty_raises_value_error(self):
        """Empty text raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            count_sentences("")

    @pytest.mark.unit
    def test_count_sentences_whitespace_raises_value_error(self):
        """Whitespace-only text raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            count_sentences("   \n\t  ")


# ── Content Analysis Tests: Procedures ──


class TestCountProcedures:
    """Tests for count_procedures function."""

    @pytest.mark.unit
    def test_count_procedures_with_steps(self):
        """'Step N' markers are counted correctly.

        # Acceptance Criterion: "Content analysis metrics computed"
        """
        text = "Step 1: Do this\nStep 2: Do that\nStep 3: Finish"
        assert count_procedures(text) == 3

    @pytest.mark.unit
    def test_count_procedures_case_insensitive(self):
        """Procedure markers are case-insensitive."""
        text = "STEP 1: start\nstep 2: continue\nSection 3: end"
        assert count_procedures(text) == 3

    @pytest.mark.unit
    def test_count_procedures_no_markers_returns_zero(self):
        """Text without procedure markers returns 0."""
        assert count_procedures("Just some plain text here.") == 0


# ── Content Analysis Tests: Prerequisites ──


class TestCountPrerequisites:
    """Tests for count_prerequisites function."""

    @pytest.mark.unit
    def test_count_prerequisites_multiple_keywords(self):
        """Multiple prerequisite keywords are counted."""
        text = "Before starting, first ensure you require admin access."
        # "Before", "first", "ensure", "require" = 4
        assert count_prerequisites(text) == 4

    @pytest.mark.unit
    def test_count_prerequisites_no_markers_returns_zero(self):
        """Text without prerequisite markers returns 0."""
        assert count_prerequisites("Just run the command.") == 0


# ── Content Analysis Tests: Commands ──


class TestCountCommands:
    """Tests for count_commands function."""

    @pytest.mark.unit
    def test_count_commands_fenced_blocks(self):
        """Fenced code blocks (```) are counted."""
        text = "Run:\n\n```bash\npip install\n```\n\nThen:\n\n```bash\npytest\n```"
        result = count_commands(text)
        # 2 fenced blocks + inline backticks inside them
        assert result >= 2

    @pytest.mark.unit
    def test_count_commands_inline_code(self):
        """Inline `code` is counted."""
        text = "Use `pip install` and `pytest` commands."
        result = count_commands(text)
        assert result >= 2

    @pytest.mark.unit
    def test_count_commands_no_code_returns_zero(self):
        """Text without code blocks returns 0."""
        assert count_commands("No code here at all.") == 0


# ── Content Analysis Tests: Warnings ──


class TestCountWarnings:
    """Tests for count_warnings function."""

    @pytest.mark.unit
    def test_count_warnings_multiple_types(self):
        """Different warning keywords are all counted."""
        text = "Warning: be careful. Note: important detail. Caution: danger."
        result = count_warnings(text)
        # "Warning", "Note", "important", "Caution" = 4
        assert result == 4

    @pytest.mark.unit
    def test_count_warnings_no_markers_returns_zero(self):
        """Text without warning markers returns 0."""
        assert count_warnings("Everything is fine.") == 0


# ── Content Analysis Tests: Conditions ──


class TestCountConditions:
    """Tests for count_conditions function."""

    @pytest.mark.unit
    def test_count_conditions_multiple_keywords(self):
        """Multiple conditional keywords are counted."""
        text = "If errors occur, when ready, unless failing, otherwise retry."
        result = count_conditions(text)
        # "If", "when", "unless", "otherwise" = 4
        assert result == 4

    @pytest.mark.unit
    def test_count_conditions_no_markers_returns_zero(self):
        """Text without conditional keywords returns 0."""
        assert count_conditions("Run the command now.") == 0


# ── Content Analysis Tests: Cross-References ──


class TestCountCrossReferences:
    """Tests for count_cross_references function."""

    @pytest.mark.unit
    def test_count_cross_references_multiple_markers(self):
        """Cross-reference markers are counted."""
        text = "See also the docs. Refer to the guide. Consult the manual."
        result = count_cross_references(text)
        # "See also", "Refer", "Consult" = 3
        assert result == 3

    @pytest.mark.unit
    def test_count_cross_references_no_markers_returns_zero(self):
        """Text without cross-reference markers returns 0."""
        assert count_cross_references("Just plain text.") == 0


# ── Composite Metrics Tests ──


class TestComputePrimaryMetrics:
    """Tests for compute_primary_metrics function."""

    @pytest.mark.unit
    def test_primary_metrics_returns_all_keys(self, simple_text):
        """Primary metrics dict contains all 8 expected keys.

        # Acceptance Criterion: "Character, word, token, and sentence counts
        #   for all documents verified and recorded"
        """
        # Act
        metrics = compute_primary_metrics(simple_text)

        # Assert
        expected_keys = {
            "character_count",
            "word_count",
            "sentence_count",
            "token_count",
            "unique_token_count",
            "avg_tokens_per_sentence",
            "avg_tokens_per_word",
            "content_density_score",
        }
        assert set(metrics.keys()) == expected_keys

    @pytest.mark.unit
    def test_primary_metrics_floats_have_two_decimals(self, simple_text):
        """Floating-point metrics are rounded to 2 decimal places.

        # Acceptance Criterion: "Output JSON uses consistent 2-decimal
        #   rounding for floats"
        """
        # Act
        metrics = compute_primary_metrics(simple_text)

        # Assert
        for key in ["avg_tokens_per_sentence", "avg_tokens_per_word",
                     "content_density_score"]:
            value = metrics[key]
            # Verify rounding: multiply by 100 and check it's an integer
            assert round(value, 2) == value, (
                "Metric '%s' not rounded to 2 decimals: %s" % (key, value)
            )

    @pytest.mark.unit
    def test_primary_metrics_empty_raises_value_error(self):
        """Empty text raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            compute_primary_metrics("")

    @pytest.mark.unit
    def test_primary_metrics_character_count_matches_len(self, simple_text):
        """Character count matches len() of the input text."""
        metrics = compute_primary_metrics(simple_text)
        assert metrics["character_count"] == len(simple_text)

    @pytest.mark.unit
    def test_primary_metrics_word_count_matches_split(self, simple_text):
        """Word count matches whitespace split count."""
        metrics = compute_primary_metrics(simple_text)
        assert metrics["word_count"] == len(simple_text.split())


class TestComputeContentAnalysis:
    """Tests for compute_content_analysis function."""

    @pytest.mark.unit
    def test_content_analysis_returns_all_keys(self, medium_text):
        """Content analysis dict contains all 6 expected keys.

        # Acceptance Criterion: "Content analysis metrics computed"
        """
        # Act
        analysis = compute_content_analysis(medium_text)

        # Assert
        expected_keys = {
            "number_of_procedures",
            "number_of_prerequisites",
            "number_of_commands",
            "number_of_warnings",
            "number_of_conditions",
            "number_of_cross_references",
        }
        assert set(analysis.keys()) == expected_keys

    @pytest.mark.unit
    def test_content_analysis_all_values_are_ints(self, medium_text):
        """All content analysis values are integers."""
        analysis = compute_content_analysis(medium_text)
        for key, value in analysis.items():
            assert isinstance(value, int), (
                "Key '%s' has non-int value: %s (%s)" % (key, value, type(value))
            )

    @pytest.mark.unit
    def test_content_analysis_detects_procedures_in_medium(self, medium_text):
        """Medium-complexity text has multiple procedure markers."""
        analysis = compute_content_analysis(medium_text)
        assert analysis["number_of_procedures"] >= 3


# ── Document Analysis Tests ──


class TestAnalyzeDocument:
    """Tests for analyze_document function."""

    @pytest.mark.unit
    def test_analyze_document_returns_tier_and_metrics(self, tmp_path):
        """Result contains tier, file_path, metrics, content_analysis.

        # Acceptance Criterion: "All three sample documents successfully
        #   read and analyzed"
        """
        # Arrange
        doc = tmp_path / "test.md"
        doc.write_text("Step 1: Test\n\n```bash\necho hello\n```\n")

        # Act
        result = analyze_document(doc, "Simple")

        # Assert
        assert result["tier"] == "Simple"
        assert "metrics" in result
        assert "content_analysis" in result
        assert "error" not in result

    @pytest.mark.unit
    def test_analyze_document_missing_file_returns_error(self, tmp_path):
        """Non-existent file returns dict with error key."""
        # Arrange
        missing = tmp_path / "missing.md"

        # Act
        result = analyze_document(missing, "Simple")

        # Assert
        assert "error" in result

    @pytest.mark.unit
    def test_analyze_document_file_path_in_result(self, tmp_path):
        """Result includes the file path as a string."""
        doc = tmp_path / "doc.md"
        doc.write_text("Some text here.\n")
        result = analyze_document(doc, "Medium")
        assert result["file_path"] == str(doc)


# ── Full Pipeline Tests ──


class TestAnalyzeAllSamples:
    """Tests for analyze_all_samples function."""

    @pytest.mark.unit
    def test_analyze_all_returns_three_documents(self, samples_dir_with_docs):
        """All 3 sample documents are analyzed successfully.

        # Acceptance Criterion: "All three sample documents successfully
        #   read and analyzed"
        """
        # Act
        results = analyze_all_samples(samples_dir_with_docs)

        # Assert
        assert len(results["documents"]) == 3

    @pytest.mark.unit
    def test_analyze_all_has_version_metadata(self, samples_dir_with_docs):
        """Results include version and encoding metadata.

        # Acceptance Criterion: "raw_metrics.json file created with valid,
        #   parseable JSON structure"
        """
        # Act
        results = analyze_all_samples(samples_dir_with_docs)

        # Assert
        assert results["version"] == "0.0.3b"
        assert results["encoding"] == "cl100k_base"
        assert "tokenizer" in results
        assert "tokenizer_mode" in results
        assert "collected_at" in results

    @pytest.mark.unit
    def test_analyze_all_nonexistent_dir_raises(self, tmp_path):
        """Non-existent directory raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            analyze_all_samples(tmp_path / "does_not_exist")

    @pytest.mark.unit
    def test_analyze_all_empty_dir_returns_empty_docs(self, tmp_path):
        """Empty directory returns results with empty documents list."""
        empty = tmp_path / "empty"
        empty.mkdir()
        results = analyze_all_samples(empty)
        assert results["documents"] == []

    @pytest.mark.unit
    def test_analyze_all_result_is_json_serializable(self, samples_dir_with_docs):
        """Full results can be serialized to valid JSON.

        # Acceptance Criterion: "raw_metrics.json file created with valid,
        #   parseable JSON structure"
        """
        # Act
        results = analyze_all_samples(samples_dir_with_docs)

        # Assert
        json_str = json.dumps(results, indent=2)
        parsed = json.loads(json_str)
        assert parsed["version"] == "0.0.3b"
        assert len(parsed["documents"]) == 3

    @pytest.mark.unit
    def test_analyze_all_tiers_are_correct(self, samples_dir_with_docs):
        """Documents are assigned the correct tier labels."""
        results = analyze_all_samples(samples_dir_with_docs)
        tier_map = {d["tier"]: d for d in results["documents"]}
        assert "Simple" in tier_map
        assert "Medium" in tier_map
        assert "Complex" in tier_map


# ── Tokenizer Initialization Tests ──


class TestGetTokenizer:
    """Tests for get_tokenizer function."""

    @pytest.mark.unit
    def test_get_tokenizer_returns_tuple(self):
        """Returns a tuple of (mode_string, tokenizer_object)."""
        mode, tokenizer = get_tokenizer()
        assert mode in ("tiktoken", "regex_fallback")
        assert tokenizer is not None

    @pytest.mark.unit
    def test_get_tokenizer_caches_result(self):
        """Second call returns the same cached result."""
        mode1, tok1 = get_tokenizer()
        mode2, tok2 = get_tokenizer()
        assert mode1 == mode2
        assert tok1 is tok2

    @pytest.mark.unit
    def test_get_tokenizer_fallback_when_tiktoken_unavailable(self):
        """Falls back to regex when tiktoken import fails."""
        with patch.dict("sys.modules", {"tiktoken": None}):
            import baseline_metrics
            baseline_metrics.TOKENIZER_MODE = "uninitialized"
            baseline_metrics._tiktoken_encoder = None
            baseline_metrics._regex_pattern = None

            mode, _ = baseline_metrics.get_tokenizer()
            assert mode == "regex_fallback"


# ── Log Output Tests ──


class TestBaselineMetricsLogging:
    """Tests verifying log output from baseline_metrics module."""

    @pytest.mark.unit
    def test_compute_primary_metrics_logs_info(self, caplog, simple_text):
        """Primary metrics computation logs INFO message.

        # Acceptance Criterion: "Script execution completes without errors"
        """
        with caplog.at_level(logging.INFO):
            compute_primary_metrics(simple_text)

        assert "Primary metrics computed" in caplog.text

    @pytest.mark.unit
    def test_analyze_document_logs_start_and_complete(self, caplog, tmp_path):
        """Document analysis logs start and completion messages."""
        doc = tmp_path / "test.md"
        doc.write_text("Step 1: Example text.\n")

        with caplog.at_level(logging.INFO):
            analyze_document(doc, "Simple")

        assert "Analyzing document" in caplog.text
        assert "analysis complete" in caplog.text.lower()

    @pytest.mark.unit
    def test_analyze_all_logs_completion_count(
        self, caplog, samples_dir_with_docs
    ):
        """analyze_all_samples logs how many documents were processed."""
        with caplog.at_level(logging.INFO):
            analyze_all_samples(samples_dir_with_docs)

        assert "Analysis complete" in caplog.text
        assert "3 documents" in caplog.text


# ── End-to-End Use Case Test ──


class TestFullMetricsWorkflow:
    """End-to-end test simulating the v0.0.3b metrics collection use case."""

    @pytest.mark.unit
    def test_full_workflow_analyze_three_documents(self, samples_dir_with_docs):
        """Simulate full workflow: analyze 3 docs, verify JSON structure.

        # Use Case: "As a metrics engineer, I need programmatic token and
        #   content analysis for the baseline samples so that I can establish
        #   objective, reproducible measurements before compression testing."
        """
        # Act — analyze all samples
        results = analyze_all_samples(samples_dir_with_docs)

        # Assert — structure matches spec
        assert results["version"] == "0.0.3b"
        assert results["encoding"] == "cl100k_base"
        assert len(results["documents"]) == 3

        # Assert — each document has all required fields
        for doc in results["documents"]:
            assert "tier" in doc
            assert "file_path" in doc
            assert "metrics" in doc
            assert "content_analysis" in doc

            m = doc["metrics"]
            assert m["character_count"] > 0
            assert m["word_count"] > 0
            assert m["token_count"] > 0
            assert m["sentence_count"] > 0
            assert m["unique_token_count"] > 0
            assert m["unique_token_count"] <= m["token_count"]

            ca = doc["content_analysis"]
            for key in [
                "number_of_procedures",
                "number_of_prerequisites",
                "number_of_commands",
                "number_of_warnings",
                "number_of_conditions",
                "number_of_cross_references",
            ]:
                assert key in ca
                assert isinstance(ca[key], int)

        # Assert — JSON serializable
        json_str = json.dumps(results, indent=2)
        assert json.loads(json_str) == results
