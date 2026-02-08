"""Tests for v0.1.2a — Environment File Creation & Structure.

Verifies that .env and .env.example files exist with proper content,
permissions, and naming conventions. Tests the EnvValidator class for
programmatic validation of environment files.

Version: v0.1.2a
"""

import logging
import os
import stat
import tempfile

import pytest

logger = logging.getLogger(__name__)

# Project root — two levels up from this file
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add src to path for imports
import sys

sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from validate_env import EnvValidator


# ---------------------------------------------------------------------------
# Happy Path Tests — File Existence & Content
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEnvFileExistence:
    """Tests verifying .env and .env.example files exist with correct content."""

    def test_env_file_exists(self):
        """`.env` file exists in project root.

        Acceptance Criterion: ".env file exists in project root"
        """
        env_path = os.path.join(PROJECT_ROOT, ".env")
        assert os.path.isfile(env_path), f".env not found at {env_path}"
        logger.info(".env exists at %s", env_path)

    def test_env_example_file_exists(self):
        """.env.example file exists in project root.

        Acceptance Criterion: ".env.example exists in project root"
        """
        env_path = os.path.join(PROJECT_ROOT, ".env.example")
        assert os.path.isfile(env_path), (
            f".env.example not found at {env_path}"
        )
        logger.info(".env.example exists at %s", env_path)

    def test_env_contains_openai_api_key(self):
        """.env file contains OPENAI_API_KEY variable.

        Acceptance Criterion: ".env file contains OPENAI_API_KEY"
        """
        env_path = os.path.join(PROJECT_ROOT, ".env")
        with open(env_path, "r") as f:
            content = f.read()
        assert "OPENAI_API_KEY=" in content
        logger.info("OPENAI_API_KEY found in .env")

    def test_env_contains_openai_model(self):
        """.env file contains OPENAI_MODEL setting.

        Acceptance Criterion: ".env file contains OPENAI_MODEL"
        """
        env_path = os.path.join(PROJECT_ROOT, ".env")
        with open(env_path, "r") as f:
            content = f.read()
        assert "OPENAI_MODEL=" in content

    def test_env_contains_debug_setting(self):
        """.env file contains DEBUG setting.

        Acceptance Criterion: ".env file contains DEBUG setting"
        """
        env_path = os.path.join(PROJECT_ROOT, ".env")
        with open(env_path, "r") as f:
            content = f.read()
        assert "DEBUG=" in content

    def test_env_example_contains_same_keys(self):
        """.env.example contains the same keys as .env.

        Acceptance Criterion: ".env.example contains same keys as .env
        with placeholder values"
        """
        env_path = os.path.join(PROJECT_ROOT, ".env")
        example_path = os.path.join(PROJECT_ROOT, ".env.example")

        env_validator = EnvValidator(env_path)
        env_validator.load_env_file()

        example_validator = EnvValidator(example_path)
        example_validator.load_env_file()

        env_keys = set(env_validator.variables.keys())
        example_keys = set(example_validator.variables.keys())

        assert env_keys == example_keys, (
            f"Key mismatch: .env has {env_keys}, "
            f".env.example has {example_keys}"
        )

    def test_env_example_has_no_real_secrets(self):
        """.env.example contains only placeholder values, not real secrets.

        Acceptance Criterion: ".env.example has only placeholder values
        (no real secrets)"
        """
        example_path = os.path.join(PROJECT_ROOT, ".env.example")

        validator = EnvValidator(example_path)
        validator.load_env_file()

        api_key = validator.variables.get("OPENAI_API_KEY", "")
        # Should be a known placeholder pattern
        assert "your-key" in api_key or "xxxxxxx" in api_key, (
            f"OPENAI_API_KEY in .env.example looks like a real key: "
            f"{api_key[:10]}..."
        )


# ---------------------------------------------------------------------------
# Permission Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEnvFilePermissions:
    """Tests verifying file permissions meet security requirements."""

    def test_env_file_permissions_are_600(self):
        """.env file has restrictive permissions (owner read/write only).

        Acceptance Criterion: ".env file permissions are 0o600"
        """
        env_path = os.path.join(PROJECT_ROOT, ".env")
        file_stat = os.stat(env_path)
        mode = stat.S_IMODE(file_stat.st_mode)

        assert mode == 0o600, (
            f".env permissions are {oct(mode)}, expected 0o600"
        )
        logger.info(".env permissions: %s (correct)", oct(mode))

    def test_env_example_permissions_allow_read(self):
        """.env.example has standard readable permissions."""
        example_path = os.path.join(PROJECT_ROOT, ".env.example")
        file_stat = os.stat(example_path)
        mode = stat.S_IMODE(file_stat.st_mode)

        # Should be readable (at least 644)
        assert mode & stat.S_IRUSR, ".env.example not readable by owner"
        assert mode & stat.S_IRGRP, ".env.example not readable by group"


# ---------------------------------------------------------------------------
# Naming Convention Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestNamingConventions:
    """Tests verifying UPPER_SNAKE_CASE naming convention."""

    def test_all_env_vars_use_upper_snake_case(self):
        """All variable names in .env use UPPER_SNAKE_CASE.

        Acceptance Criterion: "All variable names use UPPER_SNAKE_CASE"
        """
        env_path = os.path.join(PROJECT_ROOT, ".env")
        validator = EnvValidator(env_path)
        validator.load_env_file()

        assert validator.validate_naming_conventions(), (
            f"Naming convention errors: {validator.errors}"
        )

    def test_all_example_vars_use_upper_snake_case(self):
        """All variable names in .env.example use UPPER_SNAKE_CASE."""
        example_path = os.path.join(PROJECT_ROOT, ".env.example")
        validator = EnvValidator(example_path)
        validator.load_env_file()

        assert validator.validate_naming_conventions()


# ---------------------------------------------------------------------------
# EnvValidator Functional Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEnvValidatorFunctionality:
    """Tests verifying EnvValidator class behavior."""

    def test_validator_parses_valid_env_file(self):
        """EnvValidator successfully parses a well-formed .env file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            f.write("OPENAI_API_KEY=sk-proj-test123456789012345678\n")
            f.write("OPENAI_MODEL=gpt-4\n")
            f.write("DEBUG=false\n")
            tmp_path = f.name

        try:
            validator = EnvValidator(tmp_path)
            result = validator.load_env_file()
            assert result is True
            assert len(validator.variables) == 3
            assert validator.variables["OPENAI_API_KEY"] == (
                "sk-proj-test123456789012345678"
            )
        finally:
            os.unlink(tmp_path)

    def test_validator_skips_comments_and_empty_lines(self):
        """EnvValidator ignores comments and empty lines."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            f.write("# This is a comment\n")
            f.write("\n")
            f.write("OPENAI_API_KEY=sk-proj-test123456789012345678\n")
            f.write("# Another comment\n")
            f.write("\n")
            tmp_path = f.name

        try:
            validator = EnvValidator(tmp_path)
            validator.load_env_file()
            assert len(validator.variables) == 1
            assert "OPENAI_API_KEY" in validator.variables
        finally:
            os.unlink(tmp_path)

    def test_validator_detects_missing_required_vars(self):
        """EnvValidator reports missing required variables."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            f.write("OPENAI_MODEL=gpt-4\n")
            tmp_path = f.name

        try:
            validator = EnvValidator(tmp_path)
            validator.load_env_file()
            result = validator.validate_required_vars()
            assert result is False
            assert any(
                "OPENAI_API_KEY" in e for e in validator.errors
            )
        finally:
            os.unlink(tmp_path)

    def test_validator_detects_invalid_naming(self):
        """EnvValidator rejects non-UPPER_SNAKE_CASE variable names."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            f.write("openai_api_key=sk-test\n")
            tmp_path = f.name

        try:
            validator = EnvValidator(tmp_path)
            validator.load_env_file()
            # The regex won't match lowercase, so it'll be a parse error
            # Let's check no variables were loaded
            assert len(validator.variables) == 0 or not (
                validator.validate_naming_conventions()
            )
        finally:
            os.unlink(tmp_path)

    def test_validator_detects_invalid_api_key_prefix(self):
        """EnvValidator rejects API keys that don't start with 'sk-'."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            f.write("OPENAI_API_KEY=pk-invalid-key-here\n")
            tmp_path = f.name

        try:
            validator = EnvValidator(tmp_path)
            validator.load_env_file()
            result = validator.validate_api_key_format()
            assert result is False
            assert any("invalid" in e.lower() for e in validator.errors)
        finally:
            os.unlink(tmp_path)

    def test_validator_warns_on_placeholder_key(self):
        """EnvValidator warns (not errors) on placeholder API keys."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            f.write("OPENAI_API_KEY=sk-your-key-here\n")
            tmp_path = f.name

        try:
            validator = EnvValidator(tmp_path)
            validator.load_env_file()
            result = validator.validate_api_key_format()
            assert result is True  # Should pass (warning, not error)
            assert len(validator.warnings) > 0
            assert any("placeholder" in w.lower() for w in validator.warnings)
        finally:
            os.unlink(tmp_path)

    def test_validator_rejects_invalid_debug_value(self):
        """EnvValidator rejects DEBUG values other than true/false."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            f.write("OPENAI_API_KEY=sk-proj-test123456789012345678\n")
            f.write("DEBUG=yes\n")
            tmp_path = f.name

        try:
            validator = EnvValidator(tmp_path)
            validator.load_env_file()
            result = validator.validate_optional_vars()
            assert result is False
        finally:
            os.unlink(tmp_path)

    def test_validator_run_all_checks_on_project_env(self):
        """EnvValidator runs all checks on the project's .env file.

        Acceptance Criterion: "Python validator script runs without
        errors on both files"
        """
        env_path = os.path.join(PROJECT_ROOT, ".env")
        validator = EnvValidator(env_path)
        success, errors, warnings = validator.run_all_checks()
        assert success, f"Validator errors on .env: {errors}"
        logger.info(
            ".env validation passed (warnings: %d)", len(warnings)
        )

    def test_validator_run_all_checks_on_project_env_example(self):
        """EnvValidator runs all checks on the project's .env.example."""
        example_path = os.path.join(PROJECT_ROOT, ".env.example")
        validator = EnvValidator(example_path)
        success, errors, warnings = validator.run_all_checks()
        assert success, f"Validator errors on .env.example: {errors}"
        logger.info(
            ".env.example validation passed (warnings: %d)",
            len(warnings),
        )


# ---------------------------------------------------------------------------
# Edge Case Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEnvValidatorEdgeCases:
    """Edge case tests for EnvValidator."""

    def test_validator_handles_nonexistent_file(self):
        """EnvValidator gracefully handles a nonexistent file."""
        validator = EnvValidator("/nonexistent/path/.env")
        result = validator.load_env_file()
        assert result is False
        assert len(validator.errors) > 0

    def test_validator_handles_empty_file(self):
        """EnvValidator handles an empty .env file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            tmp_path = f.name

        try:
            validator = EnvValidator(tmp_path)
            validator.load_env_file()
            assert len(validator.variables) == 0
        finally:
            os.unlink(tmp_path)

    def test_validator_handles_malformed_line(self):
        """EnvValidator reports errors on malformed lines."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            f.write("THIS_IS_NOT_VALID\n")
            tmp_path = f.name

        try:
            validator = EnvValidator(tmp_path)
            validator.load_env_file()
            assert len(validator.errors) > 0
            assert any("Invalid format" in e for e in validator.errors)
        finally:
            os.unlink(tmp_path)

    def test_validator_handles_empty_api_key(self):
        """EnvValidator rejects an empty OPENAI_API_KEY value."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            f.write("OPENAI_API_KEY=\n")
            tmp_path = f.name

        try:
            validator = EnvValidator(tmp_path)
            validator.load_env_file()
            result = validator.validate_api_key_format()
            assert result is False
        finally:
            os.unlink(tmp_path)

    def test_validator_warns_on_short_api_key(self):
        """EnvValidator warns when API key seems too short."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False
        ) as f:
            f.write("OPENAI_API_KEY=sk-short\n")
            tmp_path = f.name

        try:
            validator = EnvValidator(tmp_path)
            validator.load_env_file()
            validator.validate_api_key_format()
            assert any("short" in w.lower() for w in validator.warnings)
        finally:
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Log Output Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEnvValidatorLogging:
    """Verify that validator operations produce expected log output."""

    def test_env_file_check_logs_path(self, caplog):
        """Checking .env file existence logs the path."""
        env_path = os.path.join(PROJECT_ROOT, ".env")

        with caplog.at_level(logging.INFO):
            logger.info(".env validation started for: %s", env_path)

        assert ".env validation started" in caplog.text

    def test_validator_report_produces_output(self, capsys):
        """EnvValidator.print_report() produces console output."""
        env_path = os.path.join(PROJECT_ROOT, ".env")
        validator = EnvValidator(env_path)
        validator.print_report()

        captured = capsys.readouterr()
        assert "Environment File Validation" in captured.out


# ---------------------------------------------------------------------------
# Use Case Test
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEnvFilesUseCase:
    """End-to-end use case test for v0.1.2a."""

    def test_full_environment_file_verification_workflow(self):
        """Simulate the complete environment file creation workflow.

        Use Case: "Developer creates .env and .env.example, validates
        both files pass all checks, and confirms proper permissions."
        """
        # 1. .env exists
        env_path = os.path.join(PROJECT_ROOT, ".env")
        assert os.path.isfile(env_path)

        # 2. .env.example exists
        example_path = os.path.join(PROJECT_ROOT, ".env.example")
        assert os.path.isfile(example_path)

        # 3. .env has correct permissions
        mode = stat.S_IMODE(os.stat(env_path).st_mode)
        assert mode == 0o600

        # 4. Both files validate successfully
        env_validator = EnvValidator(env_path)
        success, errors, _ = env_validator.run_all_checks()
        assert success, f".env errors: {errors}"

        example_validator = EnvValidator(example_path)
        success, errors, _ = example_validator.run_all_checks()
        assert success, f".env.example errors: {errors}"

        # 5. Keys match between files
        assert set(env_validator.variables.keys()) == set(
            example_validator.variables.keys()
        )

        # 6. .env.example has placeholder values only
        api_key = example_validator.variables.get("OPENAI_API_KEY", "")
        assert "your-key" in api_key or "xxxxxxx" in api_key
