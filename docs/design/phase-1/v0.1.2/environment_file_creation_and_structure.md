# v0.1.2a — Environment File Creation & Structure

<aside>

**Version:** 0.1.2a

**Parent:** v0.1.2 — API Configuration & Secrets

**Status:** ⬜ Not Started

**Duration:** 5–10 minutes

**Deliverable:** `.env` and `.env.example` files created and properly formatted in project root

</aside>

---

## Objective

Create properly formatted environment variable files (`.env` and `.env.example`) following security best practices. The `.env` file will contain actual API keys and must never be committed to git, while `.env.example` serves as a template for developers and will be committed. Establish naming conventions (UPPER_SNAKE_CASE) and support multi-environment scenarios (.env.local, .env.development, .env.production).

---

## Environment File Architecture

### File Hierarchy & Purpose

```
┌─────────────────────────────────────────────────────────────────┐
│                 Environment File Strategy                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ .env (LOCAL - NOT IN GIT)                                  │ │
│  │ └─ Contains actual secrets: OPENAI_API_KEY=sk-proj-xxxx   │ │
│  │ └─ Used at runtime in development                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                          │                                       │
│                          ▼                                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ .env.example (TRACKED IN GIT)                              │ │
│  │ └─ Placeholder values only: OPENAI_API_KEY=sk-your-key    │ │
│  │ └─ Developers copy to .env and fill with real keys        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ .env.local (OPTIONAL - NOT IN GIT)                         │ │
│  │ └─ Overrides .env for local machine-specific settings     │ │
│  │ └─ Pattern: loads after .env, if exists                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ .env.development, .env.production (OPTIONAL)               │ │
│  │ └─ Environment-specific config (if using NODE_ENV)        │ │
│  │ └─ Set via deployment automation                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Environment Variable Naming Conventions

### Upper Snake Case Standard

```python
# ✅ CORRECT: All uppercase, words separated by underscores
OPENAI_API_KEY=sk-proj-xxxxxx
OPENAI_MODEL=gpt-4
DEBUG=true
MAX_RETRIES=3
CACHE_TTL_SECONDS=3600

# ❌ INCORRECT: Mixed case, dots, hyphens
openai_api_key=sk-proj-xxxxxx  # Too loose
OpenAI_API_Key=sk-proj-xxxxxx  # Mixed case
openai.api.key=sk-proj-xxxxxx  # Dots instead of underscores
OPENAI-API-KEY=sk-proj-xxxxxx  # Hyphens instead of underscores
```

### Semantic Grouping

```bash
# API Keys (external services)
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=pk-ant-...

# Model Configuration
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2048

# Application Behavior
DEBUG=false
LOG_LEVEL=INFO
CACHE_ENABLED=true

# Infrastructure
DATABASE_URL=postgresql://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379
```

---

## .env File Creation Workflow

### Step 1: Initialize .env File

```bash
# Command to create .env in project root
# (Run from project root directory)
touch .env

# Or with initial content:
cat > .env << 'EOF'
# OpenAI API Configuration
# Get key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Model selection (defaults to gpt-4 if not set)
OPENAI_MODEL=gpt-4

# Debug logging (true/false)
DEBUG=false
EOF
```

### Step 2: Create .env.example (Template for Git)

```bash
# Create template file with placeholder values
cat > .env.example << 'EOF'
# Haiku Protocol Environment Configuration
# Copy this file to .env and fill in actual values
# DO NOT commit .env to version control

# ============================================
# OpenAI API Configuration (Required)
# ============================================
# Obtain API key from: https://platform.openai.com/api-keys
# Key format: Must start with 'sk-'
OPENAI_API_KEY=sk-your-key-here

# ============================================
# Model Configuration (Optional)
# ============================================
# Specify which OpenAI model to use
# Defaults to: gpt-4
OPENAI_MODEL=gpt-4

# ============================================
# Debug & Logging (Optional)
# ============================================
# Enable verbose logging for troubleshooting
# Values: true or false
# Defaults to: false
DEBUG=false
EOF
```

### Step 3: Verify File Permissions

```bash
# Ensure .env file has restrictive permissions
# (Owner read/write only, no group/world access)
chmod 600 .env

# Verify:
ls -la .env
# Expected output: -rw------- 1 user user ...

# .env.example can be readable by all (it's safe)
chmod 644 .env.example
```

---

## Python Script: Environment File Validator

```python
#!/usr/bin/env python3
"""Validate environment file structure and format."""

import os
import re
from pathlib import Path
from typing import Dict, Tuple, List

class EnvValidator:
    """Validates .env and .env.example files for proper format."""

    # Regex for valid environment variable format: KEY=value
    ENV_VAR_PATTERN = re.compile(r'^([A-Z_][A-Z0-9_]*)=(.*)$')

    # Required variables that must be present
    REQUIRED_VARS = {"OPENAI_API_KEY"}

    # Optional variables with default values
    OPTIONAL_VARS = {
        "OPENAI_MODEL": "gpt-4",
        "DEBUG": "false"
    }

    def __init__(self, env_file: str = ".env"):
        self.env_file = Path(env_file)
        self.variables: Dict[str, str] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def load_env_file(self) -> bool:
        """Load and parse environment file."""
        if not self.env_file.exists():
            self.errors.append(f"File not found: {self.env_file}")
            return False

        try:
            with open(self.env_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    # Skip empty lines and comments
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    # Parse KEY=value format
                    match = self.ENV_VAR_PATTERN.match(line)
                    if match:
                        key, value = match.groups()
                        self.variables[key] = value
                    else:
                        self.errors.append(
                            f"Line {line_num}: Invalid format (expected KEY=value): {line}"
                        )
            return True

        except IOError as e:
            self.errors.append(f"Failed to read {self.env_file}: {e}")
            return False

    def validate_naming_conventions(self) -> bool:
        """Ensure all keys use UPPER_SNAKE_CASE."""
        for key in self.variables.keys():
            if not re.match(r'^[A-Z][A-Z0-9_]*$', key):
                self.errors.append(
                    f"Invalid variable name '{key}' (must be UPPER_SNAKE_CASE)"
                )
                return False
        return True

    def validate_required_vars(self) -> bool:
        """Check that all required variables are present."""
        missing = self.REQUIRED_VARS - set(self.variables.keys())
        if missing:
            for var in missing:
                self.errors.append(f"Missing required variable: {var}")
            return False
        return True

    def validate_api_key_format(self) -> bool:
        """Validate API key has correct format (starts with 'sk-')."""
        api_key = self.variables.get("OPENAI_API_KEY", "")

        if not api_key:
            self.errors.append("OPENAI_API_KEY is empty")
            return False

        if api_key.startswith("sk-your-key") or api_key == "sk-proj-xxxxxxx":
            self.warnings.append(
                "OPENAI_API_KEY looks like placeholder value (is this .env.example?)"
            )
            return True  # Not an error for .env.example

        if not api_key.startswith("sk-"):
            self.errors.append(
                f"OPENAI_API_KEY appears invalid (should start with 'sk-'), got: {api_key[:5]}..."
            )
            return False

        if len(api_key) < 20:
            self.warnings.append(
                f"OPENAI_API_KEY seems too short (expected ~48 chars, got {len(api_key)})"
            )

        return True

    def validate_optional_vars(self) -> bool:
        """Validate optional variables if present."""
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
        """Check that .env file has restrictive permissions (600)."""
        # Only check if not .env.example
        if self.env_file.name == ".env.example":
            return True

        stat_info = self.env_file.stat()
        mode = stat_info.st_mode & 0o777

        if mode != 0o600:
            self.warnings.append(
                f"File permissions are {oct(mode)} (should be 0o600 for security)"
            )

        return True

    def run_all_checks(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validation checks."""
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

    def print_report(self):
        """Print validation report to console."""
        success, errors, warnings = self.run_all_checks()

        print(f"\n{'='*60}")
        print(f"Environment File Validation: {self.env_file}")
        print(f"{'='*60}")

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
                    display_value = value[:5] + "..." if len(value) > 5 else "***"
                else:
                    display_value = value
                print(f"   {key} = {display_value}")

        print(f"\n{'='*60}\n")
        return not bool(errors)


# Command-line usage
if __name__ == "__main__":
    import sys

    # Validate .env file
    validator = EnvValidator(".env")
    success = validator.print_report()

    # Also validate .env.example for reference
    if Path(".env.example").exists():
        print("\nAlso checking .env.example...")
        example_validator = EnvValidator(".env.example")
        example_validator.print_report()

    sys.exit(0 if success else 1)
```

---

## Multi-Environment Support

### Strategy for Different Environments

```bash
# Development machine: uses .env (local secrets)
# Loaded by: python-dotenv's load_dotenv()

# Optional override for one machine:
# Create .env.local (same format as .env)
# .env.local overrides .env if present
# Also add to .gitignore

# Production deployment:
# Set environment variables via deployment tool
# (GitHub Secrets, Docker environment, CI/CD vars, etc.)
# No .env file needed in production
```

### Python Support for Cascading Loading

```python
# Specification pseudocode: shows desired behavior
# (actual implementation in v0.1.2c config.py)

from pathlib import Path
from dotenv import load_dotenv

def load_env_cascade():
    """Load environment variables with cascade: .env → .env.local → OS env."""

    # Load base .env file
    load_dotenv(".env")

    # Load .env.local if it exists (machine-specific overrides)
    if Path(".env.local").exists():
        load_dotenv(".env.local", override=True)

    # OS environment variables take highest priority
    # (already set in load_dotenv by default with override=False)
```

---

## Creation Checklist & Verification

### Manual Creation Steps

```bash
# 1. Create .env in project root
touch .env
chmod 600 .env

# 2. Add required variables
cat >> .env << 'EOF'
OPENAI_API_KEY=sk-proj-your-actual-key-here
OPENAI_MODEL=gpt-4
DEBUG=false
EOF

# 3. Create .env.example
cat > .env.example << 'EOF'
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
DEBUG=false
EOF

# 4. Verify files exist and permissions are correct
ls -la .env .env.example
# Expected: .env with -rw------- (600)
#           .env.example with -rw-r--r-- (644)

# 5. Verify .env is not tracked by git (yet, done in v0.1.2b)
git status

# 6. Run validator script
python3 validate_env.py
```

---

## Acceptance Criteria

- [ ] `.env` file exists in project root
- [ ] `.env` file contains OPENAI_API_KEY with valid sk-proj-... key
- [ ] `.env` file contains OPENAI_MODEL (defaults to gpt-4)
- [ ] `.env` file contains DEBUG setting (defaults to false)
- [ ] `.env` file permissions are 0o600 (owner read/write only)
- [ ] `.env.example` exists in project root
- [ ] `.env.example` contains same keys as `.env` with placeholder values
- [ ] `.env.example` has only placeholder values (no real secrets)
- [ ] `.env.example` is committed to git (verified in next sub-part)
- [ ] All variable names use UPPER_SNAKE_CASE convention
- [ ] Python validator script runs without errors on both files
- [ ] Validator confirms all required variables are present

---

## Limitations & Constraints

- Environment files are text-based and support simple KEY=value format only
- Complex data structures (JSON, arrays, nested objects) must be serialized as strings and parsed in code
- Variable values cannot contain newlines (single-line values only)
- Leading/trailing spaces around keys or values may cause parsing issues (should be trimmed)
- API key exposure risk if .env is accidentally committed (mitigated in v0.1.2b via .gitignore)
- No built-in encryption for environment file contents at rest
- Loading order matters: .env.local overrides .env; OS environment variables override both
- Comments in .env file (starting with #) must be on their own line

---

## Dependencies

**Must exist before this sub-part runs:**
- Project root directory created (v0.1.0)
- Git repository initialized (v0.1.0)
- Python 3.10+ installed (v0.1.1a)
- python-dotenv package installed (v0.1.1c)

**Prerequisite files:**
- (none - this is the first file creation step in v0.1.2)

---

## Troubleshooting

### Issue: "No such file or directory" when creating .env

**Solution:** Ensure you are in the project root directory. Run `pwd` to verify, then `ls` to see the project files. Create .env in this directory.

```bash
cd /path/to/haiku-protocol  # Navigate to project root
touch .env                   # Create file
```

---

### Issue: "OPENAI_API_KEY appears invalid (should start with 'sk-')"

**Solution:** The API key must start with 'sk-' (OpenAI's format). Verify you copied the entire key from platform.openai.com/api-keys. Keys typically look like: `sk-proj-abcdef123456...` (48+ characters).

```bash
# Check current key
cat .env | grep OPENAI_API_KEY

# Should output something like:
# OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx...

# If wrong, update it:
nano .env  # or your editor
```

---

### Issue: "File permissions are 0o644 (should be 0o600 for security)"

**Solution:** Restrict file permissions so only the owner can read/write. This prevents other users on the system from seeing your API key.

```bash
chmod 600 .env
ls -la .env  # Verify it shows: -rw------- 1 user user ...
```

---

### Issue: python-dotenv not installed (import error)

**Solution:** Install python-dotenv from v0.1.1c. If already completed, verify installation:

```bash
pip show python-dotenv
# Should show version 1.0.0 or later

# If not installed:
pip install python-dotenv==1.0.0
```

---

### Issue: "OPENAI_API_KEY is empty" but I know I filled it in

**Solution:** Check for common formatting issues:

```bash
# Don't use quotes around the value (they become part of the value):
OPENAI_API_KEY="sk-proj-xxx"  # ❌ Includes the quotes
OPENAI_API_KEY=sk-proj-xxx    # ✅ Correct

# Check file was saved:
cat .env

# Ensure no accidental spaces:
# Don't use: OPENAI_API_KEY = sk-...  (spaces around =)
# Use: OPENAI_API_KEY=sk-...  (no spaces)
```

---

## User Story

> As a **developer setting up Haiku Protocol locally**, I want to **create environment files that securely store my API keys** so that **I can run the application without hardcoding secrets and protect my keys from accidental git commits**.

---

## Inputs from Previous Sub-Parts

This sub-part is the **first file creation step in v0.1.2**. It does not receive explicit file inputs from prior v0.1.2 sub-parts because none exist yet. However, it depends on:

- **v0.1.0 — Phase 1 Environment & Tech Stack**: Project root directory and git repository initialized
- **v0.1.1 — Core Dependencies Setup**: Python 3.10+ and python-dotenv package installed
- **Parent v0.1.2 — API Configuration & Secrets**: Security requirements and format templates defined

The parent document (v0.1.2) defines the expected structure and content of these files.

---

## Outputs to Next Sub-Part

This sub-part produces two files:

**File 1: `.env` (not committed)**
```
OPENAI_API_KEY=sk-proj-[actual-key-here]
OPENAI_MODEL=gpt-4
DEBUG=false
```

**File 2: `.env.example` (committed to git)**
```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
DEBUG=false
```

**How v0.1.2b uses these outputs:**

v0.1.2b (Git Security & Secret Protection) receives:
- The **`.env` file path** to verify it's correctly excluded from git via .gitignore
- The **`.env.example` file** to confirm it contains no real secrets (safe to commit)
- **Validation that both files exist and are properly formatted** (confirms v0.1.2a completed successfully)

v0.1.2b will use these files to create .gitignore rules and pre-commit hooks that prevent accidental secret exposure.

---

## Decision Log

(Placeholder: Record decisions made during environment file creation)
- Decision on UPPER_SNAKE_CASE naming convention: **Adopted** to follow Python environment variable standard (PEP 441)
- Decision on file permissions (0o600): **Adopted** for security (owner read/write only)
- Decision on .env.example in git: **Yes** - serves as documentation and setup guide for new developers

