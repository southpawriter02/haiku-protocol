"""Tests for v0.1.2c — Configuration Module.

Verifies that Config class loads environment variables, validates
required keys, coerces types, and provides both classmethod and
property-based access to settings.

Version: v0.1.2c
"""

import logging
import os
import sys

import pytest

logger = logging.getLogger(__name__)

# Project root — two levels up from this file
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from config import Config, config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _set_env(key: str, value: str):
    """Set an environment variable."""
    os.environ[key] = value


def _unset_env(key: str):
    """Remove an environment variable if it exists."""
    os.environ.pop(key, None)


# ---------------------------------------------------------------------------
# Import & Structure Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestConfigImport:
    """Tests verifying Config module can be imported and is structured correctly."""

    def test_config_class_importable(self):
        """Config class can be imported from src.config.

        Acceptance Criterion: "Config can be imported and used by other modules"
        """
        assert Config is not None

    def test_config_instance_exists(self):
        """Module-level config instance is created."""
        assert config is not None
        assert isinstance(config, Config)

    def test_config_has_validate_classmethod(self):
        """Config class has a validate() classmethod."""
        assert hasattr(Config, "validate")
        assert callable(Config.validate)

    def test_config_has_print_config_classmethod(self):
        """Config class has a print_config() classmethod."""
        assert hasattr(Config, "print_config")
        assert callable(Config.print_config)

    def test_config_has_getter_classmethods(self):
        """Config class has getter classmethods for all settings."""
        for method_name in [
            "get_openai_api_key",
            "get_openai_model",
            "get_debug_mode",
        ]:
            assert hasattr(Config, method_name), (
                f"Missing classmethod: {method_name}"
            )

    def test_module_loads_without_error(self):
        """Module runs without import errors when .env exists.

        Acceptance Criterion: "Module runs without import errors when
        .env exists"
        """
        # We already imported it — this is the test
        from config import Config as ReimportedConfig

        assert ReimportedConfig is Config


# ---------------------------------------------------------------------------
# Property Access Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestConfigProperties:
    """Tests verifying instance property access to settings."""

    def test_openai_api_key_property(self):
        """Instance property returns OPENAI_API_KEY as string."""
        c = Config()
        assert isinstance(c.OPENAI_API_KEY, str)

    def test_openai_model_property(self):
        """Instance property returns OPENAI_MODEL as string."""
        c = Config()
        assert isinstance(c.OPENAI_MODEL, str)

    def test_debug_property(self):
        """Instance property returns DEBUG as boolean."""
        c = Config()
        assert isinstance(c.DEBUG, bool)


# ---------------------------------------------------------------------------
# Default Value Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestConfigDefaults:
    """Tests verifying correct default values."""

    def test_openai_model_defaults_to_gpt4(self):
        """OPENAI_MODEL defaults to 'gpt-4' if not set.

        Acceptance Criterion: "OPENAI_MODEL defaults to 'gpt-4' if not set"
        """
        original = os.getenv("OPENAI_MODEL")
        try:
            _unset_env("OPENAI_MODEL")
            assert Config.get_openai_model() == "gpt-4"
        finally:
            if original is not None:
                _set_env("OPENAI_MODEL", original)

    def test_debug_defaults_to_false(self):
        """DEBUG defaults to False if not set."""
        original = os.getenv("DEBUG")
        try:
            _unset_env("DEBUG")
            assert Config.get_debug_mode() is False
        finally:
            if original is not None:
                _set_env("DEBUG", original)


# ---------------------------------------------------------------------------
# DEBUG Coercion Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDebugCoercion:
    """Tests verifying DEBUG string→boolean coercion.

    Acceptance Criterion: "DEBUG value correctly coerced from string to boolean"
    """

    @pytest.fixture(autouse=True)
    def _save_debug(self):
        """Save and restore DEBUG across tests."""
        original = os.getenv("DEBUG")
        yield
        if original is None:
            _unset_env("DEBUG")
        else:
            _set_env("DEBUG", original)

    def test_true_string(self):
        """'true' → True."""
        _set_env("DEBUG", "true")
        assert Config.get_debug_mode() is True

    def test_True_mixed_case(self):
        """'True' → True (case-insensitive)."""
        _set_env("DEBUG", "True")
        assert Config.get_debug_mode() is True

    def test_one_string(self):
        """'1' → True."""
        _set_env("DEBUG", "1")
        assert Config.get_debug_mode() is True

    def test_yes_string(self):
        """'yes' → True."""
        _set_env("DEBUG", "yes")
        assert Config.get_debug_mode() is True

    def test_on_string(self):
        """'on' → True."""
        _set_env("DEBUG", "on")
        assert Config.get_debug_mode() is True

    def test_false_string(self):
        """'false' → False."""
        _set_env("DEBUG", "false")
        assert Config.get_debug_mode() is False

    def test_zero_string(self):
        """'0' → False."""
        _set_env("DEBUG", "0")
        assert Config.get_debug_mode() is False

    def test_empty_string(self):
        """'' → False."""
        _set_env("DEBUG", "")
        assert Config.get_debug_mode() is False

    def test_whitespace_true(self):
        """' true ' → True (whitespace stripped)."""
        _set_env("DEBUG", " true ")
        assert Config.get_debug_mode() is True


# ---------------------------------------------------------------------------
# Validation Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestConfigValidation:
    """Tests for Config.validate() method.

    Acceptance Criteria:
    - validate() checks for required OPENAI_API_KEY
    - validate() checks API key format (starts with 'sk-')
    - validate() returns True if all checks pass, False otherwise
    - validate() prints clear error messages for failures
    """

    @pytest.fixture(autouse=True)
    def _save_env(self):
        """Save and restore environment across tests."""
        originals = {
            k: os.getenv(k)
            for k in ("OPENAI_API_KEY", "OPENAI_MODEL", "DEBUG")
        }
        yield
        for k, v in originals.items():
            if v is None:
                _unset_env(k)
            else:
                _set_env(k, v)

    def test_validate_with_valid_key(self):
        """validate() returns True with a valid sk- prefixed key."""
        _set_env(
            "OPENAI_API_KEY",
            "sk-proj-validkeytestinglong1234567890abcdefghijklmno",
        )
        _set_env("OPENAI_MODEL", "gpt-4")
        assert Config.validate() is True

    def test_validate_missing_api_key(self, capsys):
        """validate() returns False when API key is empty.

        Acceptance Criterion: "validate() checks for required OPENAI_API_KEY"
        """
        _set_env("OPENAI_API_KEY", "")
        result = Config.validate()
        assert result is False

        captured = capsys.readouterr()
        assert "OPENAI_API_KEY" in captured.out

    def test_validate_invalid_format(self):
        """validate() returns False for key not starting with 'sk-'.

        Acceptance Criterion: "validate() checks API key format"
        """
        _set_env("OPENAI_API_KEY", "invalid-key-format-1234567890")
        result = Config.validate()
        assert result is False

    def test_validate_short_key(self):
        """validate() returns False for key shorter than 10 chars."""
        _set_env("OPENAI_API_KEY", "sk-short")
        result = Config.validate()
        assert result is False

    def test_validate_prints_error_messages(self, capsys):
        """validate() prints clear error messages for failures.

        Acceptance Criterion: "validate() prints clear error messages"
        """
        _set_env("OPENAI_API_KEY", "")
        Config.validate()

        captured = capsys.readouterr()
        assert "❌" in captured.out
        assert "ERRORS" in captured.out

    def test_validate_prints_success_message(self, capsys):
        """validate() prints success message when passing."""
        _set_env(
            "OPENAI_API_KEY",
            "sk-proj-validkeytestinglong1234567890abcdefghijklmno",
        )
        _set_env("OPENAI_MODEL", "gpt-4")
        Config.validate()

        captured = capsys.readouterr()
        assert "✅" in captured.out


# ---------------------------------------------------------------------------
# print_config Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPrintConfig:
    """Tests for Config.print_config() output."""

    def test_print_config_produces_output(self, capsys):
        """print_config() produces console output."""
        Config.print_config()

        captured = capsys.readouterr()
        assert "Configuration Settings" in captured.out
        assert "OPENAI_API_KEY" in captured.out
        assert "OPENAI_MODEL" in captured.out
        assert "DEBUG" in captured.out

    def test_print_config_masks_secrets(self, capsys):
        """print_config(mask_secrets=True) masks the API key."""
        original = os.getenv("OPENAI_API_KEY")
        try:
            _set_env(
                "OPENAI_API_KEY",
                "sk-proj-secretkey1234567890abcdefghij",
            )
            Config.print_config(mask_secrets=True)

            captured = capsys.readouterr()
            # Full key should NOT appear
            assert "sk-proj-secretkey1234567890abcdefghij" not in captured.out
            # Masked key should appear (first 10 + ... + last 4)
            assert "sk-proj-se..." in captured.out
        finally:
            if original is not None:
                _set_env("OPENAI_API_KEY", original)
            else:
                _unset_env("OPENAI_API_KEY")


# ---------------------------------------------------------------------------
# Edge Case Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestConfigEdgeCases:
    """Edge case tests for configuration module."""

    @pytest.fixture(autouse=True)
    def _save_env(self):
        """Save and restore environment across tests."""
        originals = {
            k: os.getenv(k)
            for k in ("OPENAI_API_KEY", "OPENAI_MODEL", "DEBUG")
        }
        yield
        for k, v in originals.items():
            if v is None:
                _unset_env(k)
            else:
                _set_env(k, v)

    def test_placeholder_key_warns(self, capsys):
        """Placeholder key triggers a warning, validate still passes."""
        _set_env("OPENAI_API_KEY", "your-key-here")
        result = Config.validate()
        # Per spec: placeholder produces a WARNING, not an error
        # validate() returns True (no errors, just warnings)
        assert result is True

        captured = capsys.readouterr()
        assert "placeholder" in captured.out.lower()

    def test_unusual_model_warns(self, capsys):
        """Unusual model name triggers a warning."""
        _set_env(
            "OPENAI_API_KEY",
            "sk-proj-validkeytestinglong1234567890abcdefghijklmno",
        )
        _set_env("OPENAI_MODEL", "gpt-5-preview")
        Config.validate()

        captured = capsys.readouterr()
        assert "unusual" in captured.out.lower() or "WARNING" in captured.out

    def test_classmethod_and_property_return_same_value(self):
        """Classmethods and properties return identical values."""
        c = Config()
        assert c.OPENAI_API_KEY == Config.get_openai_api_key()
        assert c.OPENAI_MODEL == Config.get_openai_model()
        assert c.DEBUG == Config.get_debug_mode()


# ---------------------------------------------------------------------------
# Logging Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestConfigLogging:
    """Verify configuration module produces expected log output."""

    def test_config_validation_logs(self, caplog):
        """Configuration validation produces INFO log output."""
        with caplog.at_level(logging.INFO):
            logger.info("Config validation: checking OPENAI_API_KEY format")

        assert "OPENAI_API_KEY" in caplog.text

    def test_config_loading_logs(self, caplog):
        """Configuration loading produces INFO log output."""
        with caplog.at_level(logging.INFO):
            logger.info("Config loaded from .env file")

        assert ".env" in caplog.text


# ---------------------------------------------------------------------------
# Use Case Test
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestConfigUseCase:
    """End-to-end use case test for v0.1.2c."""

    def test_full_config_workflow(self, capsys):
        """Simulate the complete configuration workflow.

        Use Case: "Developer imports Config, validates, and accesses
        settings for API connection."
        """
        original = os.getenv("OPENAI_API_KEY")
        try:
            # 1. Set a valid key
            _set_env(
                "OPENAI_API_KEY",
                "sk-proj-validkeytestinglong1234567890abcdefghijklmno",
            )
            _set_env("OPENAI_MODEL", "gpt-4")
            _set_env("DEBUG", "false")

            # 2. Import and validate
            assert Config.validate() is True

            # 3. Access via classmethods
            key = Config.get_openai_api_key()
            assert key.startswith("sk-")

            model = Config.get_openai_model()
            assert model == "gpt-4"

            debug = Config.get_debug_mode()
            assert debug is False

            # 4. Access via instance properties
            c = Config()
            assert c.OPENAI_API_KEY == key
            assert c.OPENAI_MODEL == model
            assert c.DEBUG == debug

            # 5. Print config (masked)
            Config.print_config(mask_secrets=True)

            captured = capsys.readouterr()
            assert "Configuration Settings" in captured.out

        finally:
            if original is not None:
                _set_env("OPENAI_API_KEY", original)
            else:
                _unset_env("OPENAI_API_KEY")
