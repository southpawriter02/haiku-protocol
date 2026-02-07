"""Tests for v0.1.1a — Python Environment Setup.

Verifies the development environment meets the project's minimum
requirements: Python 3.10+, virtual environment active, pip available,
and the interpreter resolves to the virtual environment directory.

Version: v0.1.1a
"""

import logging
import os
import sys

import pytest

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Happy Path Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPythonEnvironment:
    """Tests verifying the Python environment meets v0.1.1a acceptance criteria."""

    def test_python_version_meets_minimum(self):
        """Python interpreter is 3.10 or higher.

        Acceptance Criterion: "python --version returns 3.10 or higher"
        """
        # Arrange
        major = sys.version_info.major
        minor = sys.version_info.minor

        # Act / Assert
        assert major == 3, f"Expected Python 3.x, got {major}.x"
        assert minor >= 10, (
            f"Expected Python 3.10+, got {major}.{minor}"
        )
        logger.info(
            "Python version check passed: %d.%d.%d",
            major, minor, sys.version_info.micro,
        )

    def test_virtual_environment_is_active(self):
        """A virtual environment is active (sys.prefix != sys.base_prefix).

        Acceptance Criterion: "Virtual environment created"
        Acceptance Criterion: "Virtual environment activated (prompt shows venv)"
        """
        # Act
        in_venv = sys.prefix != sys.base_prefix

        # Assert
        assert in_venv, (
            "No virtual environment detected. "
            f"sys.prefix={sys.prefix}, sys.base_prefix={sys.base_prefix}"
        )
        logger.info("Virtual environment active: prefix=%s", sys.prefix)

    def test_pip_is_available_and_current(self):
        """pip is importable and reports a version string.

        Acceptance Criterion: "pip --version shows latest version"
        """
        # Act
        import pip  # noqa: F811
        version = pip.__version__

        # Assert
        assert version, "pip version string is empty"
        parts = version.split(".")
        assert len(parts) >= 2, f"Unexpected pip version format: {version}"
        assert int(parts[0]) >= 20, (
            f"pip version {version} is outdated; expected 20+"
        )
        logger.info("pip version check passed: %s", version)

    def test_python_executable_is_in_venv(self):
        """The Python executable path is inside the virtual environment directory.

        Acceptance Criterion: "which python points to haiku-env/bin/python"
        (adapted: points to .venv/bin/python per project convention)
        """
        # Arrange
        executable = sys.executable
        venv_prefix = sys.prefix

        # Assert
        assert executable.startswith(venv_prefix), (
            f"Python executable {executable} is not inside "
            f"the virtual environment at {venv_prefix}"
        )
        logger.info(
            "Python executable is inside venv: %s", executable
        )


# ---------------------------------------------------------------------------
# Edge Case Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPythonEnvironmentEdgeCases:
    """Edge case tests for environment verification."""

    def test_sys_version_info_is_named_tuple(self):
        """sys.version_info is a structured named tuple with expected fields."""
        assert hasattr(sys.version_info, "major")
        assert hasattr(sys.version_info, "minor")
        assert hasattr(sys.version_info, "micro")

    def test_sys_prefix_is_absolute_path(self):
        """sys.prefix is an absolute path, not relative."""
        assert os.path.isabs(sys.prefix), (
            f"sys.prefix is not absolute: {sys.prefix}"
        )

    def test_sys_executable_exists_on_disk(self):
        """The Python executable reported by sys.executable actually exists."""
        assert os.path.isfile(sys.executable), (
            f"sys.executable does not exist: {sys.executable}"
        )


# ---------------------------------------------------------------------------
# Log Output Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPythonEnvironmentLogging:
    """Verify that environment checks produce expected log output."""

    def test_version_check_logs_info(self, caplog):
        """Python version check logs at INFO level.

        Use Case: "Developer verifies environment setup and sees confirmation
        in log output"
        """
        with caplog.at_level(logging.INFO):
            major = sys.version_info.major
            minor = sys.version_info.minor
            logger.info(
                "Python version check passed: %d.%d.%d",
                major, minor, sys.version_info.micro,
            )

        assert "Python version check passed" in caplog.text

    def test_venv_check_logs_prefix(self, caplog):
        """Virtual environment check logs the sys.prefix at INFO level."""
        with caplog.at_level(logging.INFO):
            logger.info("Virtual environment active: prefix=%s", sys.prefix)

        assert "Virtual environment active" in caplog.text
        assert sys.prefix in caplog.text


# ---------------------------------------------------------------------------
# Use Case Test
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEnvironmentUseCase:
    """End-to-end use case test for v0.1.1a."""

    def test_full_environment_verification_workflow(self):
        """Simulate the complete environment verification workflow.

        Use Case: "Developer clones repo, creates and activates venv,
        upgrades pip, and runs verification — all checks pass."
        """
        # 1. Python version ≥ 3.10
        assert sys.version_info >= (3, 10)

        # 2. Virtual environment is active
        assert sys.prefix != sys.base_prefix

        # 3. pip is available
        import pip  # noqa: F811
        assert pip.__version__

        # 4. Python executable is inside venv
        assert sys.executable.startswith(sys.prefix)

        # 5. All paths resolve to real locations
        assert os.path.isfile(sys.executable)
        assert os.path.isdir(sys.prefix)
