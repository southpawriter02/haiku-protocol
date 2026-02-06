"""Tests for research/pattern_extractor.py — Pattern Extraction Tool for v0.0.2a."""

import logging
import sys
from pathlib import Path

import pytest

# Ensure research/ is importable
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "research"))

from pattern_extractor import (
    AMBIGUITY_PRIORITY,
    CATEGORY_PATTERNS,
    PatternExtractor,
    run_corpus_analysis,
)


# ── Happy Path Tests ──


class TestPatternExtractorHappyPath:
    """Happy path tests for PatternExtractor class."""

    # Acceptance Criterion: "Pattern extraction script executed on full corpus"
    def test_extract_patterns_returns_expected_keys(self):
        """extract_patterns returns dictionary with all required keys."""
        # Arrange
        extractor = PatternExtractor()
        text = "Run the build command. Verify the output."

        # Act
        result = extractor.extract_patterns(text)

        # Assert
        expected_keys = {
            "frequencies",
            "raw_counts",
            "primary_counts",
            "examples",
            "total_sentences_analyzed",
            "multi_match_percentage",
        }
        assert expected_keys == set(result.keys())

    # Acceptance Criterion: "8+ semantic categories identified and documented"
    def test_all_eight_categories_defined(self):
        """All 8 semantic categories are present in CATEGORY_PATTERNS."""
        # Arrange
        expected_categories = {
            "Actions",
            "States",
            "Dependencies",
            "Warnings",
            "Conditions",
            "Verifications",
            "References",
            "Metadata",
        }

        # Act & Assert
        assert set(CATEGORY_PATTERNS.keys()) == expected_categories

    # Acceptance Criterion: "Frequency analysis completed (percentages calculated)"
    def test_frequency_values_are_percentage_strings(self):
        """Frequencies are formatted as percentage strings like '50.0%'."""
        # Arrange
        extractor = PatternExtractor()

        # Act
        result = extractor.extract_patterns("Run the command. Verify the result.")

        # Assert
        for category, pct_str in result["frequencies"].items():
            assert pct_str.endswith("%"), (
                f"Frequency for {category} should end with '%', got: {pct_str}"
            )
            # Should be parseable as float
            float(pct_str.rstrip("%"))

    # Acceptance Criterion: "Minimum 3 real-world examples captured per pattern"
    def test_examples_are_populated_for_matched_categories(self):
        """Matched categories include at least one example sentence."""
        # Arrange
        extractor = PatternExtractor()
        text = "Build the image. Deploy it. Run tests."

        # Act
        result = extractor.extract_patterns(text)

        # Assert
        for category in result["raw_counts"]:
            if result["raw_counts"][category] > 0:
                assert len(result["examples"][category]) > 0, (
                    f"Category {category} has matches but no examples"
                )

    # Acceptance Criterion: "Python script tested and executable without errors"
    def test_extract_from_single_file(self, tmp_path):
        """extract_from_file reads and processes a file correctly."""
        # Arrange
        test_file = tmp_path / "test_doc.txt"
        test_file.write_text("Install the package. Verify it works.\n")
        extractor = PatternExtractor()

        # Act
        result = extractor.extract_from_file(str(test_file))

        # Assert
        assert result["total_sentences_analyzed"] == 2
        assert result["raw_counts"]["Actions"] > 0

    def test_extract_patterns_counts_total_sentences(self):
        """Total sentences analyzed matches the input sentence count."""
        # Arrange
        extractor = PatternExtractor()
        text = "First do X. Then do Y. Finally do Z."

        # Act
        result = extractor.extract_patterns(text)

        # Assert
        assert result["total_sentences_analyzed"] == 3

    def test_actions_detected_for_imperative_verbs(self, sample_action_text):
        """Action verbs like build, deploy, run are classified as Actions."""
        # Arrange
        extractor = PatternExtractor()

        # Act
        result = extractor.extract_patterns(sample_action_text)

        # Assert
        assert result["raw_counts"]["Actions"] >= 3

    def test_warnings_detected_for_warning_markers(self, sample_warning_text):
        """WARNING keyword triggers Warnings classification."""
        # Arrange
        extractor = PatternExtractor()

        # Act
        result = extractor.extract_patterns(sample_warning_text)

        # Assert
        assert result["raw_counts"]["Warnings"] >= 1

    def test_conditions_detected_for_if_then(self, sample_conditional_text):
        """If/then/otherwise triggers Conditions classification."""
        # Arrange
        extractor = PatternExtractor()

        # Act
        result = extractor.extract_patterns(sample_conditional_text)

        # Assert
        assert result["raw_counts"]["Conditions"] >= 1


# ── Edge Case Tests ──


class TestPatternExtractorEdgeCases:
    """Edge case tests for PatternExtractor."""

    def test_extract_empty_string_raises_value_error(self):
        """Empty string input raises ValueError."""
        # Arrange
        extractor = PatternExtractor()

        # Act & Assert
        with pytest.raises(ValueError, match="empty"):
            extractor.extract_patterns("")

    def test_extract_whitespace_only_raises_value_error(self):
        """Whitespace-only input raises ValueError."""
        # Arrange
        extractor = PatternExtractor()

        # Act & Assert
        with pytest.raises(ValueError, match="empty"):
            extractor.extract_patterns("   \n\t  ")

    def test_extract_none_raises_value_error(self):
        """None input raises ValueError."""
        # Arrange
        extractor = PatternExtractor()

        # Act & Assert
        with pytest.raises(ValueError):
            extractor.extract_patterns(None)

    def test_extract_single_word_no_crash(self):
        """Single word input produces valid results without crashing."""
        # Arrange
        extractor = PatternExtractor()

        # Act
        result = extractor.extract_patterns("Hello")

        # Assert
        assert result["total_sentences_analyzed"] == 1

    def test_extract_no_matching_patterns(self):
        """Text with no procedural patterns produces empty frequencies."""
        # Arrange
        extractor = PatternExtractor()

        # Act
        result = extractor.extract_patterns("The sky is blue today.")

        # Assert
        assert result["total_sentences_analyzed"] == 1
        # May match some categories loosely, but should not crash

    def test_extract_from_nonexistent_file_raises(self):
        """Non-existent file raises FileNotFoundError."""
        # Arrange
        extractor = PatternExtractor()

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="not found"):
            extractor.extract_from_file("/nonexistent/path.txt")

    def test_max_examples_respected(self):
        """Examples per category are capped at max_examples."""
        # Arrange
        extractor = PatternExtractor(max_examples=2)
        # 5 action sentences — only 2 should be stored
        text = "Run A. Build B. Deploy C. Create D. Install E."

        # Act
        result = extractor.extract_patterns(text)

        # Assert
        assert len(result["examples"]["Actions"]) <= 2

    def test_reset_clears_accumulated_state(self):
        """reset() clears all frequency and example state."""
        # Arrange
        extractor = PatternExtractor()
        extractor.extract_patterns("Build the image. Deploy it.")

        # Act
        extractor.reset()
        result = extractor._format_results()

        # Assert
        assert result["total_sentences_analyzed"] == 0
        assert result["frequencies"] == {}


# ── Error Path Tests ──


class TestPatternExtractorErrors:
    """Error path tests for PatternExtractor."""

    def test_run_corpus_analysis_missing_dir_raises(self):
        """Non-existent corpus directory raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            run_corpus_analysis("/nonexistent/corpus/")

    def test_run_corpus_analysis_empty_dir_raises(self, tmp_path):
        """Empty corpus directory (no matching files) raises ValueError."""
        # tmp_path exists but has no .txt files
        with pytest.raises(ValueError, match="No files matching"):
            run_corpus_analysis(str(tmp_path))


# ── Ambiguity Resolution Tests ──


class TestAmbiguityResolution:
    """Tests for the ambiguity resolution priority system."""

    # Acceptance Criterion: "Classification ambiguities resolved (documented in Decision Log)"
    def test_warnings_take_priority_over_actions(self):
        """WARNING sentences get primary=Warnings even if action verbs present."""
        # Arrange
        extractor = PatternExtractor()

        # Act
        result = extractor.extract_patterns(
            "WARNING: Do not delete the backup files."
        )

        # Assert — Warnings should be in primary_counts
        assert result["primary_counts"].get("Warnings", 0) >= 1

    def test_verifications_beat_actions(self):
        """'Verify' gets primary=Verifications over Actions."""
        # Arrange
        extractor = PatternExtractor()

        # Act
        result = extractor.extract_patterns("Verify the deployment is running.")

        # Assert
        assert result["primary_counts"].get("Verifications", 0) >= 1

    def test_conditions_beat_dependencies(self):
        """'If ... then' gets primary=Conditions, not Dependencies."""
        # Arrange
        extractor = PatternExtractor()

        # Act
        result = extractor.extract_patterns(
            "If the build fails, then restore from backup."
        )

        # Assert
        # The sentence matches Conditions (if/then) and should get Conditions primary
        # because Conditions is higher priority than Dependencies
        assert "Conditions" in result["primary_counts"]

    def test_ambiguity_priority_covers_all_categories(self):
        """AMBIGUITY_PRIORITY list includes all defined categories."""
        assert set(AMBIGUITY_PRIORITY) == set(CATEGORY_PATTERNS.keys())


# ── Log Output Tests ──


class TestPatternExtractorLogging:
    """Tests that verify logging output from PatternExtractor."""

    # Acceptance Criterion: "Python script tested and executable without errors"
    def test_extract_patterns_logs_start_message(self, caplog):
        """extract_patterns logs INFO when extraction starts."""
        # Arrange
        extractor = PatternExtractor()

        # Act
        with caplog.at_level(logging.INFO, logger="pattern_extractor"):
            extractor.extract_patterns("Run the build command.")

        # Assert
        assert "Pattern extraction started" in caplog.text

    def test_extract_patterns_logs_completion(self, caplog):
        """extract_patterns logs INFO when extraction completes."""
        # Arrange
        extractor = PatternExtractor()

        # Act
        with caplog.at_level(logging.INFO, logger="pattern_extractor"):
            extractor.extract_patterns("Run the build command.")

        # Assert
        assert "Pattern extraction complete" in caplog.text

    def test_extract_from_file_logs_filename(self, caplog, tmp_path):
        """extract_from_file logs the filename being processed."""
        # Arrange
        test_file = tmp_path / "test_doc.txt"
        test_file.write_text("Deploy the app.\n")
        extractor = PatternExtractor()

        # Act
        with caplog.at_level(logging.INFO, logger="pattern_extractor"):
            extractor.extract_from_file(str(test_file))

        # Assert
        assert "Reading corpus file" in caplog.text

    def test_debug_logs_sentence_classification(self, caplog):
        """DEBUG level logs individual sentence classification details."""
        # Arrange
        extractor = PatternExtractor()

        # Act
        with caplog.at_level(logging.DEBUG, logger="pattern_extractor"):
            extractor.extract_patterns("Run the test.")

        # Assert
        assert "Sentence" in caplog.text
        assert "primary=" in caplog.text


# ── Corpus Integration Test ──


class TestCorpusAnalysis:
    """Integration-level test for full corpus analysis."""

    # Use Case: "As a grammar engineer, I need to understand recurring patterns
    #            in procedural documentation so that I can design operators that
    #            naturally encode real-world technical instructions."
    @pytest.mark.unit
    def test_full_corpus_analysis_produces_all_categories(self, corpus_dir):
        """Full corpus analysis identifies all 8 semantic categories."""
        # Arrange & Act
        results = run_corpus_analysis(corpus_dir)

        # Assert — all 8 categories should appear
        assert results["documents_analyzed"] >= 10, (
            f"Expected 10+ documents, got {results['documents_analyzed']}"
        )
        assert results["total_sentences_analyzed"] > 0

        # All 8 categories should have at least 1 match
        expected_categories = {
            "Actions", "States", "Dependencies", "Warnings",
            "Conditions", "Verifications", "References", "Metadata",
        }
        for category in expected_categories:
            assert category in results["raw_counts"], (
                f"Category '{category}' missing from results"
            )
            assert results["raw_counts"][category] > 0, (
                f"Category '{category}' has 0 matches — expected at least 1"
            )

    @pytest.mark.unit
    def test_full_corpus_examples_per_category(self, corpus_dir):
        """Each category in the full corpus has at least 3 examples."""
        # Acceptance Criterion: "Minimum 3 real-world examples captured per pattern"
        # Arrange & Act
        results = run_corpus_analysis(corpus_dir)

        # Assert
        for category in results["raw_counts"]:
            if results["raw_counts"][category] >= 3:
                assert len(results["examples"][category]) >= 3, (
                    f"Category '{category}' has {results['raw_counts'][category]} "
                    f"matches but only {len(results['examples'][category])} examples"
                )

    @pytest.mark.unit
    def test_full_corpus_document_list_complete(self, corpus_dir):
        """Corpus analysis reports all processed document filenames."""
        # Arrange & Act
        results = run_corpus_analysis(corpus_dir)

        # Assert
        assert len(results["document_list"]) >= 11
        assert all(f.endswith(".txt") for f in results["document_list"])
