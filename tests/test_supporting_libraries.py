"""Tests for v0.1.1c — Supporting Libraries.

Verifies that the supporting libraries (streamlit, python-dotenv,
llmlingua, pytest) are installed and that requirements.txt has been
frozen with pinned versions.

Version: v0.1.1c
"""

import logging
import os

import pytest

logger = logging.getLogger(__name__)

# Project root — two levels up from this file
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------
# Happy Path Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSupportingLibraryVersions:
    """Tests verifying supporting libraries meet v0.1.1c acceptance criteria."""

    def test_streamlit_is_importable(self):
        """streamlit is installed and reports a version.

        Acceptance Criterion: "streamlit --version returns version info"
        """
        # Act
        import streamlit

        version = streamlit.__version__

        # Assert
        assert version, "streamlit version string is empty"
        logger.info("streamlit version check passed: %s", version)

    def test_python_dotenv_is_importable(self):
        """python-dotenv is installed and importable.

        Acceptance Criterion: "pip show python-dotenv shows installed"
        """
        # Act
        import dotenv

        # Assert
        assert dotenv, "dotenv module is not importable"
        version = getattr(dotenv, "__version__", None)
        logger.info(
            "python-dotenv check passed: %s",
            version or "installed",
        )

    def test_llmlingua_is_importable(self):
        """llmlingua is installed and importable.

        Acceptance Criterion: "pip show llmlingua shows installed"
        """
        # Act
        import llmlingua

        # Assert
        assert llmlingua, "llmlingua module is not importable"
        logger.info("llmlingua check passed")

    def test_pytest_is_importable(self):
        """pytest is installed and reports a version.

        Acceptance Criterion: "pip show pytest shows installed (optional)"
        """
        # Act — pytest is already imported at module level, but verify version
        version = pytest.__version__

        # Assert
        assert version, "pytest version string is empty"
        logger.info("pytest version check passed: %s", version)


# ---------------------------------------------------------------------------
# Requirements File Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRequirementsFile:
    """Tests verifying requirements.txt exists and is well-formed."""

    def test_requirements_txt_exists(self):
        """requirements.txt exists at the project root.

        Acceptance Criterion: "requirements.txt exists with pinned versions"
        """
        # Arrange
        req_path = os.path.join(PROJECT_ROOT, "requirements.txt")

        # Assert
        assert os.path.isfile(req_path), (
            f"requirements.txt not found at {req_path}"
        )
        logger.info("requirements.txt exists at %s", req_path)

    def test_requirements_txt_has_pinned_versions(self):
        """requirements.txt contains entries with == pinning."""
        # Arrange
        req_path = os.path.join(PROJECT_ROOT, "requirements.txt")

        with open(req_path, "r") as f:
            lines = [
                line.strip() for line in f
                if line.strip() and not line.startswith("#")
            ]

        # Assert
        assert len(lines) > 0, "requirements.txt is empty"
        pinned = [line for line in lines if "==" in line]
        assert len(pinned) > 0, (
            "No pinned versions (==) found in requirements.txt"
        )
        logger.info(
            "requirements.txt has %d pinned entries out of %d total",
            len(pinned), len(lines),
        )

    def test_requirements_txt_contains_core_packages(self):
        """requirements.txt includes all core project dependencies."""
        # Arrange
        req_path = os.path.join(PROJECT_ROOT, "requirements.txt")

        with open(req_path, "r") as f:
            content = f.read().lower()

        # Assert — check for key packages
        expected = ["langchain", "tiktoken", "streamlit", "python-dotenv"]
        for pkg in expected:
            assert pkg in content, (
                f"Expected package '{pkg}' not found in requirements.txt"
            )


# ---------------------------------------------------------------------------
# Functional Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSupportingLibraryFunctionality:
    """Tests verifying core functionality of supporting libraries."""

    def test_dotenv_can_find_dotenv_file(self):
        """python-dotenv's find_dotenv function is callable."""
        from dotenv import find_dotenv

        # Act — should not raise, returns empty string if no .env found
        result = find_dotenv(usecwd=True)

        # Assert — function works (may or may not find a file)
        assert isinstance(result, str)
        logger.info("dotenv find_dotenv returned: %s", result or "(empty)")

    def test_llmlingua_prompt_compressor_class_exists(self):
        """LLMLingua's PromptCompressor class is importable."""
        from llmlingua import PromptCompressor

        assert PromptCompressor is not None
        logger.info("PromptCompressor class is importable")


# ---------------------------------------------------------------------------
# Edge Case Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSupportingLibraryEdgeCases:
    """Edge case tests for supporting library verification."""

    def test_requirements_txt_no_duplicate_packages(self):
        """requirements.txt has no duplicate package entries."""
        req_path = os.path.join(PROJECT_ROOT, "requirements.txt")

        with open(req_path, "r") as f:
            lines = [
                line.strip().split("==")[0].lower()
                for line in f
                if line.strip() and not line.startswith("#")
            ]

        duplicates = [pkg for pkg in lines if lines.count(pkg) > 1]
        assert len(duplicates) == 0, (
            f"Duplicate packages in requirements.txt: {set(duplicates)}"
        )

    def test_requirements_txt_is_not_empty_file(self):
        """requirements.txt has meaningful content (not just whitespace)."""
        req_path = os.path.join(PROJECT_ROOT, "requirements.txt")

        size = os.path.getsize(req_path)
        assert size > 100, (
            f"requirements.txt is suspiciously small: {size} bytes"
        )

    def test_streamlit_version_is_string(self):
        """streamlit.__version__ is a proper version string."""
        import streamlit

        version = streamlit.__version__
        parts = version.split(".")
        assert len(parts) >= 2, (
            f"Unexpected streamlit version format: {version}"
        )


# ---------------------------------------------------------------------------
# Log Output Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSupportingLibraryLogging:
    """Verify that library checks produce expected log output."""

    def test_streamlit_import_logs_version(self, caplog):
        """Importing streamlit and logging its version produces INFO output."""
        import streamlit

        with caplog.at_level(logging.INFO):
            logger.info("streamlit version: %s", streamlit.__version__)

        assert "streamlit version" in caplog.text

    def test_requirements_check_logs_count(self, caplog):
        """Requirements file check logs the entry count."""
        req_path = os.path.join(PROJECT_ROOT, "requirements.txt")

        with open(req_path, "r") as f:
            count = sum(
                1 for line in f
                if line.strip() and not line.startswith("#")
            )

        with caplog.at_level(logging.INFO):
            logger.info("requirements.txt contains %d entries", count)

        assert "requirements.txt contains" in caplog.text


# ---------------------------------------------------------------------------
# Use Case Test
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSupportingLibrariesUseCase:
    """End-to-end use case test for v0.1.1c."""

    def test_full_supporting_library_verification_workflow(self):
        """Simulate the complete supporting library verification workflow.

        Use Case: "Developer installs supporting libraries, verifies all
        are importable, and confirms requirements.txt is frozen."
        """
        # 1. streamlit importable
        import streamlit
        assert streamlit.__version__

        # 2. python-dotenv importable
        import dotenv
        assert dotenv

        # 3. llmlingua importable
        import llmlingua
        assert llmlingua

        # 4. pytest importable (already running in it)
        assert pytest.__version__

        # 5. requirements.txt exists and has content
        req_path = os.path.join(PROJECT_ROOT, "requirements.txt")
        assert os.path.isfile(req_path)
        with open(req_path, "r") as f:
            content = f.read()
        assert "==" in content, "No pinned versions in requirements.txt"
        assert len(content) > 100, "requirements.txt is too small"
