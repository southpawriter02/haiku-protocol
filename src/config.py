#!/usr/bin/env python3
"""Configuration module for Haiku Protocol.

Loads environment variables from .env file and provides centralized
configuration access with validation.

Usage:
    from src.config import Config

    if not Config.validate():
        raise RuntimeError("Configuration validation failed")

    api_key = Config.OPENAI_API_KEY
    model = Config.OPENAI_MODEL
    debug_mode = Config.DEBUG

Version: v0.1.2c
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


# ============================================
# Load Environment Variables
# ============================================


def _load_env():
    """Load environment variables from .env file.

    Searches for .env in the project root (parent of src/).
    Prints a warning to stderr if the file is not found.
    """
    src_dir = Path(__file__).parent
    project_root = src_dir.parent

    env_file = project_root / ".env"

    if env_file.exists():
        load_dotenv(env_file)
    else:
        print(
            f"⚠️  Warning: .env file not found at {env_file}",
            file=sys.stderr,
        )


# Load .env at module import time
_load_env()


# ============================================
# Configuration Class
# ============================================


class Config:
    """Application configuration.

    Provides centralized access to all configuration settings,
    loaded from environment variables.

    Attributes:
        OPENAI_API_KEY (str): OpenAI API key (required).
        OPENAI_MODEL (str): Model name (default: gpt-4).
        DEBUG (bool): Debug mode enabled (default: False).
    """

    # ----------------------------------------
    # Required Configuration (properties)
    # ----------------------------------------

    @property
    def OPENAI_API_KEY(self) -> str:
        """Get OpenAI API key from environment."""
        return os.getenv("OPENAI_API_KEY", "")

    # ----------------------------------------
    # Optional Configuration with Defaults
    # ----------------------------------------

    @property
    def OPENAI_MODEL(self) -> str:
        """Get OpenAI model name (defaults to gpt-4)."""
        return os.getenv("OPENAI_MODEL", "gpt-4")

    @property
    def DEBUG(self) -> bool:
        """Get debug flag (defaults to False)."""
        debug_str = os.getenv("DEBUG", "false").lower().strip()
        return debug_str in ("true", "1", "yes", "on")

    # ----------------------------------------
    # Classmethods (for class-level access)
    # ----------------------------------------

    @classmethod
    def get_openai_api_key(cls) -> str:
        """Get OpenAI API key with validation."""
        return os.getenv("OPENAI_API_KEY", "")

    @classmethod
    def get_openai_model(cls) -> str:
        """Get OpenAI model name."""
        return os.getenv("OPENAI_MODEL", "gpt-4")

    @classmethod
    def get_debug_mode(cls) -> bool:
        """Get debug flag."""
        debug_str = os.getenv("DEBUG", "false").lower().strip()
        return debug_str in ("true", "1", "yes", "on")

    # ----------------------------------------
    # Validation
    # ----------------------------------------

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration requirements.

        Checks:
            - OPENAI_API_KEY is present and non-empty
            - OPENAI_API_KEY has correct format (starts with 'sk-')
            - OPENAI_MODEL is non-empty
            - DEBUG is valid boolean

        Returns:
            True if all validations pass, False otherwise.

        Example:
            if not Config.validate():
                raise RuntimeError("Configuration validation failed")
        """
        errors = []
        warnings = []

        # ---- Required Configuration ----

        api_key = cls.get_openai_api_key()

        if not api_key:
            errors.append("OPENAI_API_KEY is required but empty")

        elif len(api_key) < 10:
            errors.append(
                f"OPENAI_API_KEY too short (got {len(api_key)} chars)"
            )

        elif not api_key.startswith("sk-"):
            if api_key in ("your-key-here", "sk-your-key"):
                warnings.append(
                    "OPENAI_API_KEY looks like placeholder "
                    "(is this .env.example?)"
                )
            else:
                errors.append(
                    f"OPENAI_API_KEY format invalid "
                    f"(should start with 'sk-', "
                    f"got '{api_key[:10]}...')"
                )

        # Warn if key length is unusual
        if api_key.startswith("sk-") and len(api_key) < 30:
            warnings.append(
                f"OPENAI_API_KEY seems short ({len(api_key)} chars, "
                "expected 48+). Is it truncated?"
            )

        # ---- Optional Configuration with Defaults ----

        model = cls.get_openai_model()

        if not model:
            errors.append(
                "OPENAI_MODEL is empty (should be 'gpt-4' or similar)"
            )

        valid_models = [
            "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o",
        ]
        if model and model not in valid_models:
            warnings.append(
                f"OPENAI_MODEL '{model}' is unusual. "
                f"Known models: {valid_models}"
            )

        # ---- Debug Configuration ----

        debug = cls.get_debug_mode()

        if not isinstance(debug, bool):
            errors.append(f"DEBUG must be boolean, got {type(debug)}")

        # ---- Print Results ----

        if errors or warnings:
            print(f"\n{'=' * 60}")
            print("⚠️  Configuration Validation Results")
            print(f"{'=' * 60}")

        if errors:
            print("\n❌ ERRORS (Configuration Invalid):")
            for i, error in enumerate(errors, 1):
                print(f"   {i}. {error}")

        if warnings:
            print("\n⚠️  WARNINGS (Review Recommended):")
            for i, warning in enumerate(warnings, 1):
                print(f"   {i}. {warning}")

        if errors or warnings:
            print(f"{'=' * 60}\n")

        success = len(errors) == 0

        if success:
            print("✅ Configuration validated successfully")
            if api_key:
                print(f"   API Model: {model}")
                print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
                print(f"   Debug Mode: {debug}\n")

        return success

    # ----------------------------------------
    # Pretty Printing
    # ----------------------------------------

    @classmethod
    def print_config(cls, mask_secrets: bool = True):
        """Print current configuration to stdout.

        Args:
            mask_secrets: If True, mask sensitive values like API keys.
        """
        print("\nConfiguration Settings:")
        print("-" * 40)

        api_key = cls.get_openai_api_key()
        if mask_secrets and api_key:
            masked_key = api_key[:10] + "..." + api_key[-4:]
        else:
            masked_key = api_key or "(empty)"

        print(f"OPENAI_API_KEY: {masked_key}")
        print(f"OPENAI_MODEL: {cls.get_openai_model()}")
        print(f"DEBUG: {cls.get_debug_mode()}")
        print("-" * 40 + "\n")


# ============================================
# Module-level instance
# ============================================

config = Config()


# ============================================
# Script Execution (self-test)
# ============================================

if __name__ == "__main__":
    print("Haiku Protocol - Configuration Module (v0.1.2c)")
    print("=" * 60)

    valid = Config.validate()
    Config.print_config(mask_secrets=True)

    exit(0 if valid else 1)
