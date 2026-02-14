#!/usr/bin/env python3
"""Configuration module for Haiku Protocol.

Loads environment variables from .env file and provides centralized
configuration access with validation.  Supports multiple LLM providers
including OpenAI, Ollama, and LM Studio.

Usage:
    from src.config import Config

    if not Config.validate():
        raise RuntimeError("Configuration validation failed")

    provider = Config.get_llm_provider()   # "openai", "ollama", "lmstudio"
    api_key  = Config.get_llm_api_key()    # falls back to OPENAI_API_KEY
    model    = Config.get_llm_model()       # falls back to OPENAI_MODEL
    base_url = Config.get_llm_base_url()   # auto-set per provider

Version: v0.1.3
"""

import os
import sys
from pathlib import Path
try:
    from dotenv import load_dotenv
    _HAS_DOTENV = True
except ImportError:
    _HAS_DOTENV = False


# ============================================
# Load Environment Variables
# ============================================


def _load_env():
    """Load environment variables from .env file.

    Searches for .env in the project root (parent of src/).
    Prints a warning to stderr if the file is not found.
    Falls back to raw os.getenv if python-dotenv is not installed.
    """
    if not _HAS_DOTENV:
        return

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


# ============================================
# Provider Constants
# ============================================

VALID_PROVIDERS = ("openai", "ollama", "lmstudio")

_PROVIDER_DEFAULTS = {
    "openai": {
        "base_url": None,           # LangChain default
        "model": "gpt-4",
        "api_key_required": True,
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "model": "llama3.2",
        "api_key_required": False,
    },
    "lmstudio": {
        "base_url": "http://localhost:1234/v1",
        "model": "default",
        "api_key_required": False,
    },
}


class Config:
    """Application configuration.

    Provides centralized access to all configuration settings,
    loaded from environment variables.  Supports multiple LLM
    providers via ``LLM_PROVIDER``.

    Attributes:
        OPENAI_API_KEY (str): OpenAI API key (backward compat).
        OPENAI_MODEL (str): Model name (backward compat, default: gpt-4).
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
    # LLM Provider Classmethods
    # ----------------------------------------

    @classmethod
    def get_llm_provider(cls) -> str:
        """Get configured LLM provider.

        Returns:
            One of ``"openai"``, ``"ollama"``, or ``"lmstudio"``.
            Defaults to ``"openai"`` for backward compatibility.
        """
        return os.getenv("LLM_PROVIDER", "openai").lower().strip()

    @classmethod
    def get_llm_base_url(cls) -> str | None:
        """Get the LLM API base URL.

        If ``LLM_BASE_URL`` is set, it takes precedence. Otherwise the
        default for the current provider is used (``None`` for OpenAI,
        ``http://localhost:11434/v1`` for Ollama,
        ``http://localhost:1234/v1`` for LM Studio).
        """
        explicit = os.getenv("LLM_BASE_URL", "").strip()
        if explicit:
            return explicit
        provider = cls.get_llm_provider()
        return _PROVIDER_DEFAULTS.get(provider, {}).get("base_url")

    @classmethod
    def get_llm_api_key(cls) -> str:
        """Get API key for the active provider.

        For OpenAI, returns ``OPENAI_API_KEY``.  For local providers
        (Ollama / LM Studio) returns ``"not-needed"`` unless the user
        explicitly sets ``LLM_API_KEY`` or ``OPENAI_API_KEY``.
        """
        # Explicit LLM_API_KEY always wins
        explicit = os.getenv("LLM_API_KEY", "").strip()
        if explicit:
            return explicit
        # Fall back to OPENAI_API_KEY
        openai_key = cls.get_openai_api_key()
        if openai_key:
            return openai_key
        # Local providers don't need a key
        provider = cls.get_llm_provider()
        if provider in ("ollama", "lmstudio"):
            return "not-needed"
        return ""

    @classmethod
    def get_llm_model(cls) -> str:
        """Get model name for the active provider.

        Falls back to ``OPENAI_MODEL`` for backward compatibility,
        then to a sensible per-provider default.
        """
        # OPENAI_MODEL env var (backward compat)
        openai_model = os.getenv("OPENAI_MODEL", "")
        if openai_model:
            return openai_model
        provider = cls.get_llm_provider()
        return _PROVIDER_DEFAULTS.get(provider, {}).get("model", "gpt-4")

    @classmethod
    def is_local_provider(cls) -> bool:
        """Return True if the active provider is a local LLM server."""
        return cls.get_llm_provider() in ("ollama", "lmstudio")

    # ----------------------------------------
    # Validation
    # ----------------------------------------

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration requirements.

        Checks:
            - LLM_PROVIDER is a recognized value
            - API key is present for OpenAI (optional for local providers)
            - API key format for OpenAI (starts with 'sk-')
            - Model name is non-empty
            - DEBUG is valid boolean

        Returns:
            True if all validations pass, False otherwise.

        Example:
            if not Config.validate():
                raise RuntimeError("Configuration validation failed")
        """
        errors = []
        warnings = []

        # ---- Provider ----

        provider = cls.get_llm_provider()
        if provider not in VALID_PROVIDERS:
            errors.append(
                f"LLM_PROVIDER '{provider}' is not recognized. "
                f"Valid providers: {', '.join(VALID_PROVIDERS)}"
            )

        local = cls.is_local_provider()

        # ---- API Key ----

        api_key = cls.get_llm_api_key()

        if not local:
            # OpenAI requires a real key
            if not api_key:
                errors.append("OPENAI_API_KEY is required but empty")

            elif len(api_key) < 10:
                errors.append(
                    f"OPENAI_API_KEY too short (got {len(api_key)} chars)"
                )

            elif not api_key.startswith("sk-"):
                if api_key in ("your-key-here", "sk-your-key", "not-needed"):
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

        # ---- Model ----

        model = cls.get_llm_model()

        if not model:
            errors.append(
                "Model name is empty (set OPENAI_MODEL or check "
                "LLM_PROVIDER defaults)"
            )

        if not local:
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
            print(f"   Provider: {provider}")
            print(f"   API Model: {model}")
            base_url = cls.get_llm_base_url()
            if base_url:
                print(f"   Base URL: {base_url}")
            if api_key and api_key != "not-needed":
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
        provider = cls.get_llm_provider()
        api_key = cls.get_llm_api_key()
        base_url = cls.get_llm_base_url()

        if mask_secrets and api_key and api_key != "not-needed":
            masked_key = api_key[:10] + "..." + api_key[-4:]
        elif api_key:
            masked_key = api_key
        else:
            masked_key = "(empty)"

        print("\nConfiguration Settings:")
        print("-" * 40)
        print(f"LLM_PROVIDER: {provider}")
        if base_url:
            print(f"LLM_BASE_URL: {base_url}")
        print(f"API_KEY: {masked_key}")
        print(f"MODEL: {cls.get_llm_model()}")
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
    print("Haiku Protocol - Configuration Module (v0.1.3)")
    print("=" * 60)

    valid = Config.validate()
    Config.print_config(mask_secrets=True)

    exit(0 if valid else 1)
