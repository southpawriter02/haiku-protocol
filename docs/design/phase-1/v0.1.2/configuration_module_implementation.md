# v0.1.2c — Configuration Module Implementation

<aside>

**Version:** 0.1.2c

**Parent:** v0.1.2 — API Configuration & Secrets

**Status:** ⬜ Not Started

**Duration:** 5–10 minutes

**Deliverable:** `src/config.py` module with Config class that loads and validates environment variables

</aside>

---

## Objective

Implement the `src/config.py` configuration module with a Config class that loads environment variables from `.env` file using python-dotenv, validates required keys (OPENAI_API_KEY), coerces data types (string→bool for DEBUG), and provides a validate() classmethod. The module centralizes all configuration access and ensures invalid configurations fail fast at import time.

---

## Configuration Module Architecture

### Design: Centralized Configuration

```
┌──────────────────────────────────────────────────────────┐
│           Configuration Module Architecture              │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  USER CODE (e.g., test_api.py)                           │
│       │                                                  │
│       ▼                                                  │
│  ┌──────────────────┐                                    │
│  │ from config      │                                    │
│  │ import Config    │                                    │
│  └────────┬─────────┘                                    │
│           │                                              │
│           ▼                                              │
│  ┌────────────────────────────────────────────────────┐  │
│  │ src/config.py (Configuration Module)               │  │
│  ├────────────────────────────────────────────────────┤  │
│  │                                                    │  │
│  │  1. load_dotenv(".env")  [from python-dotenv]    │  │
│  │     └─ Reads .env file, loads into os.environ    │  │
│  │                                                    │  │
│  │  2. class Config:                                 │  │
│  │     ├─ OPENAI_API_KEY = os.getenv(...)           │  │
│  │     ├─ OPENAI_MODEL = os.getenv(..., default)    │  │
│  │     ├─ DEBUG = boolean coercion logic             │  │
│  │     │                                              │  │
│  │     └─ @classmethod validate():                   │  │
│  │        ├─ Check required keys exist                │  │
│  │        ├─ Validate format (sk- prefix)            │  │
│  │        ├─ Type checking                            │  │
│  │        └─ Return True/False + error messages      │  │
│  │                                                    │  │
│  └────────────────────────────────────────────────────┘  │
│           │                                              │
│           ▼                                              │
│  ┌──────────────────────────────────────────────────┐   │
│  │ User Code accesses Config.OPENAI_API_KEY         │   │
│  │ Guaranteed to be valid (or error raised)        │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Benefits

- **Single Source of Truth**: All config in one place
- **Fail Fast**: Invalid config detected at import time, not runtime
- **Type Safety**: Configuration values coerced to correct types
- **Validation**: Required keys and format checked automatically
- **Testability**: Config can be mocked in tests
- **Documentation**: Config.validate() prints clear error messages

---

## Configuration Loading Flow

### Detailed Load & Validate Sequence

```
┌─────────────────────────────────────────────────────────────┐
│      Configuration Module Initialization Sequence           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: Import config.py                                  │
│  ├─ Python executes: from dotenv import load_dotenv      │
│  ├─ Python executes: load_dotenv()                        │
│  │  └─ Reads .env file (if exists)                        │
│  │  └─ Sets os.environ variables                          │
│  │                                                         │
│  ▼                                                         │
│  Step 2: Define Config class attributes                    │
│  ├─ OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")     │
│  │  └─ Gets value from os.environ (set by load_dotenv)  │
│  │  └─ Or empty string if not found                      │
│  │                                                         │
│  ├─ OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")    │
│  │  └─ Gets value or default: "gpt-4"                   │
│  │                                                         │
│  ├─ DEBUG = os.getenv("DEBUG", "false").lower() == "true"│
│  │  └─ String from os.environ → .lower() → == "true"    │
│  │  └─ Result: True or False                              │
│  │                                                         │
│  ▼                                                         │
│  Step 3: Optionally validate on import                     │
│  ├─ if __name__ == "__main__":                           │
│  │  └─ Config.validate()  (only when run directly)       │
│  │                                                         │
│  ├─ or call Config.validate() from user code             │
│  │  └─ Checks required fields                             │
│  │  └─ Validates format (sk- prefix)                      │
│  │  └─ Returns True/False                                 │
│  │                                                         │
│  ▼                                                         │
│  Step 4: User code runs (e.g., test_api.py)              │
│  └─ Uses Config.OPENAI_API_KEY, Config.OPENAI_MODEL, etc │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Source Code: src/config.py

```python
#!/usr/bin/env python3
"""
Configuration module for Haiku Protocol.

Loads environment variables from .env file and provides centralized
configuration access with validation.

Usage:
    from src.config import Config

    if not Config.validate():
        raise RuntimeError("Configuration validation failed")

    api_key = Config.OPENAI_API_KEY
    model = Config.OPENAI_MODEL
    debug_mode = Config.DEBUG
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional


# ============================================
# Load Environment Variables
# ============================================

def _load_env():
    """Load environment variables from .env file."""
    # Find project root (parent directory of src/)
    src_dir = Path(__file__).parent
    project_root = src_dir.parent

    env_file = project_root / ".env"

    if env_file.exists():
        load_dotenv(env_file)
    else:
        # Warn if .env doesn't exist (may be running in production)
        import sys
        print(
            f"⚠️  Warning: .env file not found at {env_file}",
            file=sys.stderr
        )


# Load .env at module import time
_load_env()


# ============================================
# Configuration Class
# ============================================

class Config:
    """
    Application configuration.

    Provides centralized access to all configuration settings,
    loaded from environment variables.

    Attributes:
        OPENAI_API_KEY (str): OpenAI API key (required)
        OPENAI_MODEL (str): Model name (default: gpt-4)
        DEBUG (bool): Debug mode enabled (default: False)
    """

    # ----------------------------------------
    # Required Configuration
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
    # Classmethods (for easier access)
    # ----------------------------------------

    # Note: @property requires instance access (config.OPENAI_API_KEY)
    # Use classmethods (Config.get_openai_api_key()) for class-level access

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
        """
        Validate configuration requirements.

        Checks:
        - OPENAI_API_KEY is present and non-empty
        - OPENAI_API_KEY has correct format (starts with 'sk-')
        - OPENAI_MODEL is non-empty
        - DEBUG is valid boolean

        Returns:
            bool: True if all validations pass, False otherwise

        Prints:
            Error messages to stdout for each validation failure
            Success message if all checks pass

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

        elif not isinstance(api_key, str):
            errors.append(f"OPENAI_API_KEY must be string, got {type(api_key)}")

        elif len(api_key) < 10:
            errors.append(f"OPENAI_API_KEY too short (got {len(api_key)} chars)")

        elif not api_key.startswith("sk-"):
            # Check if it looks like a placeholder
            if api_key in ("your-key-here", "sk-your-key"):
                warnings.append(
                    "OPENAI_API_KEY looks like placeholder (is this .env.example?)"
                )
            else:
                errors.append(
                    f"OPENAI_API_KEY format invalid (should start with 'sk-', got '{api_key[:10]}...')"
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
            errors.append("OPENAI_MODEL is empty (should be 'gpt-4' or similar)")

        elif not isinstance(model, str):
            errors.append(f"OPENAI_MODEL must be string, got {type(model)}")

        # Warn if model is unusual
        valid_models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o"]
        if model not in valid_models:
            warnings.append(
                f"OPENAI_MODEL '{model}' is unusual. Known models: {valid_models}"
            )

        # ---- Debug Configuration ----

        debug = cls.get_debug_mode()

        if not isinstance(debug, bool):
            errors.append(f"DEBUG must be boolean, got {type(debug)}")

        # ---- Print Results ----

        if errors or warnings:
            print("\n" + "=" * 60)
            print("⚠️  Configuration Validation Results")
            print("=" * 60)

        if errors:
            print("\n❌ ERRORS (Configuration Invalid):")
            for i, error in enumerate(errors, 1):
                print(f"   {i}. {error}")

        if warnings:
            print("\n⚠️  WARNINGS (Review Recommended):")
            for i, warning in enumerate(warnings, 1):
                print(f"   {i}. {warning}")

        if errors or warnings:
            print("=" * 60 + "\n")

        success = len(errors) == 0

        if success:
            print("✅ Configuration validated successfully")
            print(f"   API Model: {model}")
            print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
            print(f"   Debug Mode: {debug}\n")

        return success

    # ----------------------------------------
    # Pretty Printing
    # ----------------------------------------

    @classmethod
    def print_config(cls, mask_secrets: bool = True):
        """
        Print current configuration to stdout.

        Args:
            mask_secrets: If True, mask sensitive values like API keys

        Example:
            Config.print_config()
            # Output:
            # OPENAI_API_KEY: sk-proj-...def0
            # OPENAI_MODEL: gpt-4
            # DEBUG: False
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
# Instantiation (for compatibility)
# ============================================

# Create instance if needed (optional, classmethods above are preferred)
config = Config()


# ============================================
# Script Execution (self-test)
# ============================================

if __name__ == "__main__":
    """
    Run configuration validation when module is executed directly.

    Usage:
        python src/config.py

    Output:
        Prints configuration validation results
    """
    print("Haiku Protocol - Configuration Module (v0.1.2c)")
    print("=" * 60)

    # Validate configuration
    valid = Config.validate()

    # Print current settings (with secrets masked)
    Config.print_config(mask_secrets=True)

    # Exit with appropriate code
    exit(0 if valid else 1)
```

---

## Alternative Implementation: Using Class Attributes (Simpler)

```python
# Simpler approach: use class attributes directly
# (Don't need @property or @classmethod)

from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    """Simpler configuration using direct class attributes."""

    # Required
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Optional with defaults
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        errors = []

        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")
        elif not cls.OPENAI_API_KEY.startswith("sk-"):
            errors.append("OPENAI_API_KEY format invalid")

        if errors:
            for error in errors:
                print(f"❌ {error}")
            return False

        print("✅ Configuration validated")
        return True

# Usage:
# from config import Config
# api_key = Config.OPENAI_API_KEY
```

---

## Configuration Load Decision Tree

### When to Call Config.validate()

```
┌─────────────────────────────────────────────────┐
│  Should I call Config.validate()?               │
├─────────────────────────────────────────────────┤
│                                                 │
│    Running in production environment?           │
│              │                                   │
│    ┌─────────┴────────┐                         │
│    ▼ YES              ▼ NO                      │
│  [SKIP]          ┌──────────────────────┐      │
│  (env vars       │ Is config critical   │      │
│   already set)   │ to app startup?      │      │
│                  └──────────┬───────────┘      │
│                             │                   │
│                  ┌──────────┴──────────┐       │
│                  ▼ YES                 ▼ NO    │
│             [CALL]              [OPTIONAL]     │
│          validate()            validate()      │
│         (abort if fails)      (warn only)     │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Integration with Other Modules

### Pattern: Import and Use Config

```python
# In any module that needs configuration:

from src.config import Config

def connect_to_api():
    """Example function using Config."""

    # Option 1: Classmethod access (works on class directly)
    api_key = Config.get_openai_api_key()
    model = Config.get_openai_model()

    # Option 2: Use Config.validate() before risky operations
    if not Config.validate():
        raise RuntimeError("Invalid configuration")

    # Now safe to use config values
    return ChatOpenAI(
        api_key=api_key,
        model=model,
        temperature=0
    )
```

---

## Testing Configuration

```python
# test_config.py - Unit tests for Config module

import os
import pytest
from src.config import Config


class TestConfig:
    """Test configuration loading and validation."""

    def test_openai_api_key_loaded(self):
        """Test that OPENAI_API_KEY is loaded from environment."""
        # Mock: os.environ has been set by load_dotenv()
        api_key = Config.get_openai_api_key()
        assert isinstance(api_key, str)
        # In real env: should start with 'sk-'

    def test_openai_model_defaults(self):
        """Test that OPENAI_MODEL has correct default."""
        model = Config.get_openai_model()
        assert model == "gpt-4"

    def test_debug_coercion(self):
        """Test that DEBUG is correctly coerced to boolean."""
        # Temporarily set DEBUG to various values
        original = os.getenv("DEBUG")

        try:
            # Test "true" → True
            os.environ["DEBUG"] = "true"
            assert Config.get_debug_mode() is True

            # Test "false" → False
            os.environ["DEBUG"] = "false"
            assert Config.get_debug_mode() is False

            # Test empty → False
            os.environ["DEBUG"] = ""
            assert Config.get_debug_mode() is False

        finally:
            # Restore original
            if original is None:
                os.environ.pop("DEBUG", None)
            else:
                os.environ["DEBUG"] = original

    def test_validate_missing_api_key(self, capsys):
        """Test validation fails when API key is missing."""
        original = os.getenv("OPENAI_API_KEY")

        try:
            os.environ["OPENAI_API_KEY"] = ""
            valid = Config.validate()
            assert valid is False

            captured = capsys.readouterr()
            assert "OPENAI_API_KEY" in captured.out

        finally:
            if original:
                os.environ["OPENAI_API_KEY"] = original

    def test_validate_invalid_api_key_format(self):
        """Test validation fails for invalid API key format."""
        original = os.getenv("OPENAI_API_KEY")

        try:
            os.environ["OPENAI_API_KEY"] = "invalid-key"
            valid = Config.validate()
            assert valid is False

        finally:
            if original:
                os.environ["OPENAI_API_KEY"] = original

    def test_validate_valid_api_key(self):
        """Test validation passes with valid API key."""
        original = os.getenv("OPENAI_API_KEY")

        try:
            os.environ["OPENAI_API_KEY"] = "sk-proj-validkeytesting"
            valid = Config.validate()
            assert valid is True

        finally:
            if original:
                os.environ["OPENAI_API_KEY"] = original
```

---

## Acceptance Criteria

- [ ] `src/config.py` file created in project
- [ ] `Config` class defined with OPENAI_API_KEY, OPENAI_MODEL, DEBUG attributes
- [ ] `load_dotenv()` called at module load time to read .env file
- [ ] `Config.validate()` classmethod implemented
- [ ] `validate()` checks for required OPENAI_API_KEY
- [ ] `validate()` checks API key format (starts with 'sk-')
- [ ] `validate()` returns True if all checks pass, False otherwise
- [ ] `validate()` prints clear error messages for failures
- [ ] DEBUG value correctly coerced from string to boolean
- [ ] OPENAI_MODEL defaults to "gpt-4" if not set
- [ ] Module runs without import errors when .env exists
- [ ] `python src/config.py` prints validation results
- [ ] Config can be imported and used by other modules

---

## Limitations & Constraints

- Configuration is loaded at module import time (can't be changed dynamically without reloading module)
- Type coercion is limited to basic types (str, bool); complex structures require manual parsing
- No built-in support for nested config (use separate classes for sub-configs)
- Environment variable names are case-sensitive (OPENAI_API_KEY != openai_api_key)
- Validation is optional (validate() must be called; not automatic)
- .env file format is strict (no complex syntax, multiline values need escaping)
- No encryption for config values at rest (secrets stored plaintext in .env)
- Hard-coded defaults (gpt-4) may need updates as OpenAI releases new models

---

## Dependencies

**Must exist before this sub-part runs:**
- `.env` file created with actual API key (v0.1.2a)
- `.env.example` created as template (v0.1.2a)
- `.gitignore` configured to exclude .env (v0.1.2b)
- python-dotenv package installed (v0.1.1c)
- Python 3.10+ (v0.1.1a)
- `src/` directory exists (v0.1.3 or earlier)

**Python imports used:**
- `os` (standard library)
- `pathlib.Path` (standard library)
- `dotenv.load_dotenv` (installed in v0.1.1c)

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'dotenv'"

**Solution:** Install python-dotenv package (should be done in v0.1.1c):

```bash
pip install python-dotenv==1.0.0

# Verify installation
python -c "from dotenv import load_dotenv; print('✅ dotenv installed')"
```

---

### Issue: "OPENAI_API_KEY validation fails even though .env has the key"

**Solution:** Verify .env file format and key content:

```bash
# Check .env file exists in project root
ls -la .env

# Check file contains the key
grep OPENAI_API_KEY .env

# Expected output:
# OPENAI_API_KEY=sk-proj-...

# If key is there, check for formatting issues:
# - No quotes around value
# - No spaces around =
# - Key starts with OPENAI_API_KEY (exact spelling)

# Test Config module directly
python -c "from src.config import Config; print(Config.get_openai_api_key())"
```

---

### Issue: "load_dotenv() not finding .env file"

**Solution:** Check file path and current working directory:

```bash
# Verify .env exists in project root
pwd  # Show current directory
ls -la .env

# If config.py can't find it, check paths:
# src/config.py expects: project_root/.env
# If src/ is in a different location, adjust path:

# In config.py, change:
# env_file = project_root / ".env"
# To:
# env_file = Path(__file__).parent.parent / ".env"
```

---

### Issue: "DEBUG always evaluates to False even when set to 'true'"

**Solution:** Check string comparison in coercion logic:

```python
# The coercion logic is:
debug_str = os.getenv("DEBUG", "false").lower().strip()
return debug_str in ("true", "1", "yes", "on")

# Make sure DEBUG in .env is one of:
# DEBUG=true    ✅
# DEBUG=1       ✅
# DEBUG=yes     ✅
# DEBUG=on      ✅
# DEBUG=True    ✅ (gets lowercased)

# NOT these:
# DEBUG=True    ❌ (will match after .lower())
# DEBUG=TRUE    ❌ (will match after .lower())

# Test manually:
python -c "import os; os.environ['DEBUG']='true'; print(os.getenv('DEBUG', 'false').lower().strip() in ('true', '1', 'yes', 'on'))"
# Should print: True
```

---

## User Story

> As a **developer working on Haiku Protocol**, I want to **centralize configuration access through a Config class** so that **I can easily load API keys from .env, validate them, and use them throughout the application without repeating environment variable access code**.

---

## Inputs from Previous Sub-Parts

This sub-part receives inputs from v0.1.2a and v0.1.2b:

**From v0.1.2a (Environment File Creation & Structure):**
- **`.env` file** with OPENAI_API_KEY, OPENAI_MODEL, DEBUG keys
- **Expected format**: UPPER_SNAKE_CASE, one per line, no quotes around values
- **Validation**: File permissions 0o600, actual secrets present

**From v0.1.2b (Git Security & Secret Protection):**
- **`.gitignore` confirmation**: .env is excluded from git
- **Security guarantee**: .env will never be accidentally committed
- **Assurance**: Safe to implement code that reads from .env

This sub-part uses these files to:
1. Load .env file into Python's os.environ using load_dotenv()
2. Create Config class that reads values from os.environ
3. Validate that required keys (OPENAI_API_KEY) have correct format
4. Provide centralized API for other modules to access configuration

---

## Outputs to Next Sub-Part

This sub-part produces:

**File 1: `src/config.py` module**
```python
from src.config import Config

# Access via classmethods (preferred):
api_key = Config.get_openai_api_key()
model = Config.get_openai_model()
debug = Config.get_debug_mode()

# Or via instance properties:
config = Config()
api_key = config.OPENAI_API_KEY
model = config.OPENAI_MODEL
debug = config.DEBUG

# Validate before use:
if Config.validate():
    # Safe to proceed
    pass
```

**Key exports:**
- `Config` class (main interface)
- `Config.get_openai_api_key()` (classmethod) or `config.OPENAI_API_KEY` (instance property)
- `Config.get_openai_model()` (classmethod) or `config.OPENAI_MODEL` (instance property)
- `Config.get_debug_mode()` (classmethod) or `config.DEBUG` (instance property)
- `Config.validate()` (classmethod)
- `Config.print_config()` (classmethod)

**How v0.1.2d uses this output:**

v0.1.2d (API Connection Testing & Validation) receives:
- **Config class** that can be imported and used to load OPENAI_API_KEY
- **validate() method** to ensure configuration is valid before attempting API call
- **Model and other settings** from Config attributes to create ChatOpenAI instance
- **Guarantee**: Configuration is validated before API test runs

v0.1.2d will import Config and use it to:
1. Get OPENAI_API_KEY for ChatOpenAI initialization
2. Call Config.validate() to ensure key is valid format
3. Use Config.OPENAI_MODEL to specify which model to test
4. Report clear error messages if configuration is invalid

---

## Decision Log

(Placeholder: Record decisions made during implementation)
- Decision on Config class design: **Using classmethods** for testability and clarity
- Decision on load_dotenv timing: **At module import time** to fail fast
- Decision on validation: **Optional (Config.validate() called by user)** rather than automatic
- Decision on defaults: **gpt-4 for model, false for debug** (most common use case)
- Decision on type coercion: **Only for DEBUG** (string→bool), other values remain strings
- Decision on error handling: **Print messages, return bool** rather than raising exceptions (allows graceful fallback)

