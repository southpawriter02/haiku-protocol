#!/usr/bin/env python3
"""Validate environment file structure and format.

Provides the EnvValidator class for programmatic validation of .env
and .env.example files. Checks naming conventions, required variables,
API key format, and file permissions.

Version: v0.1.2a
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class EnvValidator:
    """Validates .env and .env.example files for proper format.

    Attributes:
        env_file: Path to the environment file to validate.
        variables: Parsed environment variables from the file.
        errors: List of validation errors found.
        warnings: List of validation warnings found.
    """

    # Regex for valid environment variable format: KEY=value
    ENV_VAR_PATTERN = re.compile(r"^([A-Z_][A-Z0-9_]*)=(.*)$")

    # Required variables that must be present
    # (OPENAI_API_KEY becomes optional for local providers)
    REQUIRED_VARS = {"OPENAI_API_KEY"}

    # Optional variables with default values
    OPTIONAL_VARS = {
        "OPENAI_MODEL": "gpt-4",
        "DEBUG": "false",
        "LLM_PROVIDER": "openai",
        "LLM_BASE_URL": "",
        "LLM_API_KEY": "",
    }

    def __init__(self, env_file: str = ".env") -> None:
        """Initialize the validator.

        Args:
            env_file: Path to the environment file to validate.
        """
        self.env_file = Path(env_file)
        self.variables: Dict[str, str] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def load_env_file(self) -> bool:
        """Load and parse environment file.

        Returns:
            True if the file was loaded successfully, False otherwise.
        """
        if not self.env_file.exists():
            self.errors.append(f"File not found: {self.env_file}")
            return False

        try:
            with open(self.env_file, "r") as f:
                for line_num, line in enumerate(f, 1):
                    # Skip empty lines and comments
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    # Parse KEY=value format
                    match = self.ENV_VAR_PATTERN.match(line)
                    if match:
                        key, value = match.groups()
                        self.variables[key] = value
                    else:
                        self.errors.append(
                            f"Line {line_num}: Invalid format "
                            f"(expected KEY=value): {line}"
                        )
            return True

        except IOError as e:
            self.errors.append(f"Failed to read {self.env_file}: {e}")
            return False

    def validate_naming_conventions(self) -> bool:
        """Ensure all keys use UPPER_SNAKE_CASE.

        Returns:
            True if all keys follow the naming convention.
        """
        all_valid = True
        for key in self.variables.keys():
            if not re.match(r"^[A-Z][A-Z0-9_]*$", key):
                self.errors.append(
                    f"Invalid variable name '{key}' "
                    f"(must be UPPER_SNAKE_CASE)"
                )
                all_valid = False
        return all_valid

    def validate_required_vars(self) -> bool:
        """Check that all required variables are present.

        Returns:
            True if all required variables are found.
        """
        provider = self.variables.get("LLM_PROVIDER", "openai").lower()
        required = set(self.REQUIRED_VARS)

        # OPENAI_API_KEY is not required for local providers
        if provider in ("ollama", "lmstudio"):
            required.discard("OPENAI_API_KEY")

        missing = required - set(self.variables.keys())
        if missing:
            for var in missing:
                self.errors.append(f"Missing required variable: {var}")
            return False
        return True

    def validate_api_key_format(self) -> bool:
        """Validate API key has correct format (starts with 'sk-').

        Skips validation for local providers (Ollama, LM Studio)
        since they don't require API keys.

        Returns:
            True if the API key format is valid or a known placeholder.
        """
        provider = self.variables.get("LLM_PROVIDER", "openai").lower()

        # Local providers don't need a real API key
        if provider in ("ollama", "lmstudio"):
            return True

        api_key = self.variables.get("OPENAI_API_KEY", "")

        if not api_key:
            self.errors.append("OPENAI_API_KEY is empty")
            return False

        if api_key.startswith("sk-your-key") or api_key == "sk-proj-xxxxxxx":
            self.warnings.append(
                "OPENAI_API_KEY looks like placeholder value "
                "(is this .env.example?)"
            )
            return True  # Not an error for .env.example

        if not api_key.startswith("sk-"):
            self.errors.append(
                f"OPENAI_API_KEY appears invalid "
                f"(should start with 'sk-'), got: {api_key[:5]}..."
            )
            return False

        if len(api_key) < 20:
            self.warnings.append(
                f"OPENAI_API_KEY seems too short "
                f"(expected ~48 chars, got {len(api_key)})"
            )

        return True

    def validate_optional_vars(self) -> bool:
        """Validate optional variables if present.

        Returns:
            True if all optional variables have valid values.
        """
        # DEBUG should be true or false
        if "DEBUG" in self.variables:
            debug_val = self.variables["DEBUG"].lower()
            if debug_val not in ("true", "false"):
                self.errors.append(
                    f"DEBUG must be 'true' or 'false', got '{debug_val}'"
                )
                return False

        return True

    def validate_file_permissions(self) -> bool:
        """Check that .env file has restrictive permissions (600).

        Returns:
            True always (warnings only, not errors).
        """
        # Only check if not .env.example
        if self.env_file.name == ".env.example":
            return True

        stat_info = self.env_file.stat()
        mode = stat_info.st_mode & 0o777

        if mode != 0o600:
            self.warnings.append(
                f"File permissions are {oct(mode)} "
                f"(should be 0o600 for security)"
            )

        return True

    def run_all_checks(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validation checks.

        Returns:
            Tuple of (success, errors, warnings).
        """
        self.load_env_file()

        if self.errors:  # Stop if file can't be read
            return False, self.errors, self.warnings

        self.validate_naming_conventions()
        self.validate_required_vars()
        self.validate_api_key_format()
        self.validate_optional_vars()
        self.validate_file_permissions()

        success = len(self.errors) == 0
        return success, self.errors, self.warnings

    def print_report(self) -> bool:
        """Print validation report to console.

        Returns:
            True if validation passed, False otherwise.
        """
        success, errors, warnings = self.run_all_checks()

        print(f"\n{'=' * 60}")
        print(f"Environment File Validation: {self.env_file}")
        print(f"{'=' * 60}")

        if errors:
            print("\n❌ ERRORS:")
            for error in errors:
                print(f"   • {error}")

        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"   • {warning}")

        if not errors:
            print("\n✅ All validation checks passed!")
            print(f"\nLoaded {len(self.variables)} environment variables:")
            for key, value in sorted(self.variables.items()):
                # Mask sensitive values
                if "KEY" in key or "SECRET" in key or "PASSWORD" in key:
                    display_value = (
                        value[:5] + "..." if len(value) > 5 else "***"
                    )
                else:
                    display_value = value
                print(f"   {key} = {display_value}")

        print(f"\n{'=' * 60}\n")
        return not bool(errors)


# Command-line usage
if __name__ == "__main__":
    # Validate .env file
    validator = EnvValidator(".env")
    success = validator.print_report()

    # Also validate .env.example for reference
    if Path(".env.example").exists():
        print("\nAlso checking .env.example...")
        example_validator = EnvValidator(".env.example")
        example_validator.print_report()

    sys.exit(0 if success else 1)
