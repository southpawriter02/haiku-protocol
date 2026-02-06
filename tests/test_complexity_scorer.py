"""Tests for benchmarks/complexity_scorer.py."""

import json
import logging
from pathlib import Path

import pytest

# Import from benchmarks package
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "benchmarks"))
from complexity_scorer import (
    classify_by_score,
    estimate_tokens,
    score_all_samples,
    score_document_complexity,
)


# ── Happy Path Tests ──


class TestScoreDocumentComplexity:
    """Tests for score_document_complexity function."""

    @pytest.mark.unit
    def test_score_simple_document_returns_low_score(self):
        """Simple procedural text scores below 0.35 threshold.

        # Acceptance Criterion: "Each document verified as procedural"
        """
        # Arrange
        text = "Install the package:\n\n```bash\npip install requests\n```"

        # Act
        score, indicators = score_document_complexity(text)

        # Assert
        assert score < 0.35, (
            "Simple document scored %.2f, expected below 0.35" % score
        )
        assert isinstance(indicators, dict)

    @pytest.mark.unit
    def test_score_medium_document_returns_mid_score(self):
        """Medium procedural text scores between 0.35 and 0.70.

        # Acceptance Criterion: "Each document verified as procedural"
        """
        # Arrange — enough procedural markers to score 0.35-0.70
        text = (
            "# Configure Git\n\n"
            "## Prerequisites\n\n"
            "Before starting, first install Git. Require admin access.\n\n"
            "## Steps\n\n"
            "Step 1: Initialize repository\n\n"
            "```bash\ngit init\n```\n\n"
            "Step 2: Configure user\n\n"
            "```bash\ngit config user.name 'Dev'\n```\n\n"
            "Step 3: If you need SSH, first generate a key\n\n"
            "```bash\nssh-keygen -t ed25519\n```\n\n"
            "Warning: Keep your private key secure.\n\n"
            "Note: Read the SSH documentation for details.\n\n"
            "Step 4: When remote is needed, unless already set, add origin\n\n"
            "```bash\ngit remote add origin url\n```\n\n"
            "Step 5: If errors occur, refer to troubleshooting.\n\n"
            "```bash\ngit config --list\n```\n\n"
            "Important: Verify your email before pushing.\n\n"
            "Step 6: Verify configuration\n\n"
            "```bash\ngit log --oneline\n```\n"
        )

        # Act
        score, indicators = score_document_complexity(text)

        # Assert
        assert 0.35 <= score < 0.70, (
            "Medium document scored %.2f, expected 0.35-0.70" % score
        )

    @pytest.mark.unit
    def test_score_complex_document_returns_high_score(self):
        """Complex procedural text scores 0.70 or above.

        # Acceptance Criterion: "Each document verified as procedural"
        """
        # Arrange — build a rich procedural document with many markers
        text = (
            "# Full Deployment Guide\n\n"
            "## Prerequisites\n\n"
            "Before you begin, first install required tools. "
            "Require admin access and a valid license.\n\n"
            "## Steps\n\n"
        )
        # Add many steps with conditionals, commands, and cross-refs
        for i in range(1, 12):
            text += "Step %d: Configure stage %d\n\n" % (i, i)
            text += "```bash\nkubectl apply -f stage%d.yaml\n```\n\n" % i
            text += "```bash\nkubectl get pods\n```\n\n"
            if i % 2 == 0:
                text += "Warning: Check status before continuing.\n\n"
                text += "Important: Verify resources are available.\n\n"
            if i % 3 == 0:
                text += "If errors occur, refer to troubleshooting.\n\n"
                text += "Note: See also the reference documentation.\n\n"
                text += "When the pod is ready, unless failing, continue.\n\n"

        text += "## Troubleshooting\n\n"
        text += "If deployment fails, refer to the troubleshooting guide.\n"
        text += "When errors occur, unless handled, read the docs.\n"
        text += "Depending on the cluster, see also the admin guide.\n"
        text += "If timeout, first check the network before retrying.\n"

        # Act
        score, indicators = score_document_complexity(text)

        # Assert
        assert score >= 0.70, (
            "Complex document scored %.2f, expected >= 0.70" % score
        )

    @pytest.mark.unit
    def test_score_returns_tuple_of_float_and_dict(self):
        """Return type is Tuple[float, Dict[str, int]].

        # Acceptance Criterion: "Automated complexity scorer run"
        """
        # Arrange
        text = "Step 1: Run the command\n\n```bash\nls\n```\n"

        # Act
        result = score_document_complexity(text)

        # Assert
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], float)
        assert isinstance(result[1], dict)

    @pytest.mark.unit
    def test_score_indicators_have_expected_keys(self):
        """Indicators dict contains all 6 expected keys.

        # Acceptance Criterion: "Automated complexity scorer run"
        """
        # Arrange
        text = "A simple document with some text."

        # Act
        _, indicators = score_document_complexity(text)

        # Assert
        expected_keys = {
            "step_markers",
            "command_blocks",
            "warnings",
            "conditionals",
            "prerequisites",
            "cross_references",
        }
        assert set(indicators.keys()) == expected_keys

    @pytest.mark.unit
    def test_score_is_normalized_between_zero_and_one(self):
        """Score is always between 0.0 and 1.0 inclusive.

        # Acceptance Criterion: "Automated complexity scorer run"
        """
        # Arrange — document with many indicators to push score high
        text = (
            "Step 1 Step 2 Step 3 Step 4 Step 5 Step 6 Step 7 Step 8\n"
            "Warning Warning Warning Warning Warning\n"
            "If else when unless depending\n"
            "prerequisite require before first\n"
            "see also refer link to read\n"
            "```code```\n" * 10
        )

        # Act
        score, _ = score_document_complexity(text)

        # Assert
        assert 0.0 <= score <= 1.0, (
            "Score %.4f is outside [0.0, 1.0] range" % score
        )


# ── Edge Case Tests ──


class TestScoreDocumentComplexityEdgeCases:
    """Edge case tests for score_document_complexity."""

    @pytest.mark.unit
    def test_score_empty_string_raises_value_error(self):
        """Empty string raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            score_document_complexity("")

    @pytest.mark.unit
    def test_score_whitespace_only_raises_value_error(self):
        """Whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            score_document_complexity("   \n\t  ")

    @pytest.mark.unit
    def test_score_none_raises_type_or_value_error(self):
        """None input raises ValueError."""
        with pytest.raises((TypeError, ValueError)):
            score_document_complexity(None)

    @pytest.mark.unit
    def test_score_single_word_returns_zero(self):
        """Single word with no procedural markers scores near zero."""
        score, indicators = score_document_complexity("Hello")
        assert score == 0.0
        assert all(v == 0 for v in indicators.values())

    @pytest.mark.unit
    def test_score_no_procedural_markers_returns_zero(self):
        """Text with no procedural markers scores exactly 0.0."""
        text = "The weather is nice today. I like coffee."
        score, _ = score_document_complexity(text)
        assert score == 0.0


# ── Classification Tests ──


class TestClassifyByScore:
    """Tests for classify_by_score function."""

    @pytest.mark.unit
    @pytest.mark.parametrize("score,expected_tier", [
        (0.0, "SIMPLE"),
        (0.10, "SIMPLE"),
        (0.34, "SIMPLE"),
        (0.35, "MEDIUM"),
        (0.50, "MEDIUM"),
        (0.69, "MEDIUM"),
        (0.70, "COMPLEX"),
        (0.85, "COMPLEX"),
        (1.0, "COMPLEX"),
    ])
    def test_classify_score_to_tier(self, score, expected_tier):
        """Score boundaries map correctly to tier labels."""
        assert classify_by_score(score) == expected_tier


# ── Token Estimation Tests ──


class TestEstimateTokens:
    """Tests for estimate_tokens function."""

    @pytest.mark.unit
    def test_estimate_four_chars_equals_one_token(self):
        """4-character string estimates to 1 token."""
        assert estimate_tokens("abcd") == 1

    @pytest.mark.unit
    def test_estimate_empty_string_returns_zero(self):
        """Empty string estimates to 0 tokens."""
        assert estimate_tokens("") == 0

    @pytest.mark.unit
    def test_estimate_400_chars_returns_100_tokens(self):
        """400 characters estimates to 100 tokens."""
        assert estimate_tokens("a" * 400) == 100


# ── Integration: Score All Samples ──


class TestScoreAllSamples:
    """Tests for score_all_samples function."""

    @pytest.mark.unit
    def test_score_all_samples_returns_list(self, tmp_path):
        """Returns a list of result dictionaries.

        # Use Case: "Benchmarking engineer curates documents and runs scorer"
        """
        # Arrange
        samples_dir = tmp_path / "samples"
        samples_dir.mkdir()
        (samples_dir / "test.md").write_text("Step 1: Do something\n")

        # Act
        results = score_all_samples(samples_dir)

        # Assert
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]["document"] == "test"

    @pytest.mark.unit
    def test_score_all_samples_result_has_required_keys(self, tmp_path):
        """Each result dict contains all required fields.

        # Acceptance Criterion: "Automated complexity scorer run and results logged"
        """
        # Arrange
        samples_dir = tmp_path / "samples"
        samples_dir.mkdir()
        (samples_dir / "doc.md").write_text("Step 1: Install\n```bash\npip install\n```\n")

        # Act
        results = score_all_samples(samples_dir)

        # Assert
        required_keys = {
            "document", "file", "character_count", "word_count",
            "token_estimate", "complexity_score", "tier_classification",
            "indicators", "scored_at",
        }
        assert required_keys.issubset(set(results[0].keys()))

    @pytest.mark.unit
    def test_score_all_samples_nonexistent_dir_raises(self, tmp_path):
        """Non-existent directory raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            score_all_samples(tmp_path / "does_not_exist")

    @pytest.mark.unit
    def test_score_all_samples_empty_dir_returns_empty_list(self, tmp_path):
        """Empty directory returns empty results list."""
        samples_dir = tmp_path / "empty"
        samples_dir.mkdir()
        results = score_all_samples(samples_dir)
        assert results == []


# ── Log Output Tests ──


class TestComplexityScorerLogging:
    """Tests verifying log output from complexity scorer."""

    @pytest.mark.unit
    def test_score_document_logs_info_message(self, caplog):
        """Scoring logs INFO message with character count.

        # Acceptance Criterion: "Automated complexity scorer run and results logged"
        """
        with caplog.at_level(logging.INFO):
            score_document_complexity("Step 1: Test document text")

        assert "Scoring document complexity" in caplog.text
        assert "Complexity score" in caplog.text

    @pytest.mark.unit
    def test_score_all_samples_logs_completion(self, caplog, tmp_path):
        """score_all_samples logs scoring completion message."""
        samples_dir = tmp_path / "samples"
        samples_dir.mkdir()
        (samples_dir / "test.md").write_text("Step 1: Example\n")

        with caplog.at_level(logging.INFO):
            score_all_samples(samples_dir)

        assert "Scoring complete" in caplog.text


# ── Use Case Test ──


class TestFullCurationWorkflow:
    """End-to-end test simulating the v0.0.3a curation use case."""

    @pytest.mark.unit
    def test_curate_and_score_three_documents(self, tmp_path):
        """Simulate full curation workflow: create, score, classify 3 docs.

        # Use Case: "Benchmarking engineer curates a diverse set of
        #   procedural documents with known complexity levels to
        #   establish a fair baseline for compression testing."
        """
        # Arrange — create 3 documents at different complexity tiers
        samples_dir = tmp_path / "samples"
        samples_dir.mkdir()

        simple_text = (
            "# Install pip\n\n"
            "Run:\n\n```bash\npython -m ensurepip\n```\n"
        )
        medium_text = (
            "# Setup Git\n\n"
            "## Prerequisites\n\n"
            "Before starting, first install Git. Require admin access.\n\n"
            "Step 1: Install\n\n"
            "```bash\napt install git\n```\n\n"
            "Step 2: Configure\n\n"
            "```bash\ngit config user.name 'Dev'\n```\n\n"
            "Step 3: If remote, first set origin\n\n"
            "```bash\ngit remote add origin url\n```\n\n"
            "Warning: Verify credentials before pushing.\n\n"
            "Step 4: When done, unless errors, read the log.\n\n"
            "```bash\ngit log\n```\n\n"
            "Important: Check email settings.\n\n"
            "Step 5: Verify\n\n"
            "```bash\ngit status\n```\n"
        )
        complex_text = (
            "# Deploy Application\n\n"
            "## Prerequisites\n\n"
            "Before starting, first install tools. Require cluster access.\n\n"
        )
        for i in range(1, 12):
            complex_text += "Step %d: Configure stage %d\n\n" % (i, i)
            complex_text += "```bash\nkubectl apply -f stage%d.yaml\n```\n\n" % i
            complex_text += "```bash\nkubectl get pods\n```\n\n"
            if i % 2 == 0:
                complex_text += "Warning: Check status before continuing.\n\n"
                complex_text += "Important: Verify resources.\n\n"
            if i % 3 == 0:
                complex_text += "If errors occur, refer to troubleshooting.\n\n"
                complex_text += "Note: See also the deployment reference.\n\n"
                complex_text += "When ready, unless failing, continue.\n\n"
        complex_text += "Depending on config, see also the admin docs.\n"
        complex_text += "If timeout, first check network before retrying.\n"

        (samples_dir / "simple.md").write_text(simple_text)
        (samples_dir / "medium.md").write_text(medium_text)
        (samples_dir / "complex.md").write_text(complex_text)

        # Act
        results = score_all_samples(samples_dir)

        # Assert — each document classified to its expected tier
        tier_map = {r["document"]: r["tier_classification"] for r in results}
        assert tier_map["simple"] == "SIMPLE"
        assert tier_map["medium"] == "MEDIUM"
        assert tier_map["complex"] == "COMPLEX"
        assert len(results) == 3
