# v0.1.2 — API Configuration & Secrets

<aside>

**Version:** v0.1.2

**Parent:** v0.1.0 — Environment & Tech Stack

**Status:** ⬜ Not Started

**Duration:** 15-20 minutes

**Deliverable:** Secure API configuration with .env file

</aside>

---

## Objective

Configure API keys securely using environment variables. **Never commit secrets to git.**

---

## Security Requirements

- Never commit `.env` files to version control
- Use `.env.example` with placeholder values for documentation
- Validate API key format before use (must start with `sk-`)
- Pre-commit hooks to catch accidentally staged secrets

---

## Workflow: API Configuration Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                API CONFIGURATION PIPELINE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   v0.1.2a: ENVIRONMENT FILE CREATION (5–10 min)                 │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │ 1. Create .env with OPENAI_API_KEY                        │ │
│   │ 2. Create .env.example with placeholder values            │ │
│   │ 3. Multi-environment support (.env.local, .env.production)│ │
│   │ 4. Validate .env structure                                │ │
│   └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│   v0.1.2b: GIT SECURITY & SECRET PROTECTION (5–10 min)         │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │ 1. Configure .gitignore for .env exclusion                │ │
│   │ 2. Optional: Install pre-commit hook for secret detection │ │
│   │ 3. Audit git history for accidentally committed secrets   │ │
│   │ 4. Run security checklist verification                    │ │
│   └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│   v0.1.2c: CONFIGURATION MODULE (5–10 min)                      │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │ 1. Create src/config.py with Config class                 │ │
│   │ 2. Load from .env via python-dotenv                       │ │
│   │ 3. Validate required vs optional keys                     │ │
│   │ 4. Type coercion (string→bool for DEBUG)                  │ │
│   └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│   v0.1.2d: API CONNECTION TESTING (5–10 min)                    │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │ 1. Create tests/test_api.py                               │ │
│   │ 2. Test API connectivity via ChatOpenAI                   │ │
│   │ 3. Handle errors (401, 429, timeout)                      │ │
│   │ 4. Verify: ✅ API Response received                        │ │
│   └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Templates

### .env (DO NOT COMMIT)

```bash
# OpenAI API Key - Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Specify model (defaults to gpt-4)
OPENAI_MODEL=gpt-4

# Optional: Enable debug logging
DEBUG=false
```

### .env.example (COMMIT THIS)

```bash
# Copy this file to .env and fill in your values
# DO NOT commit .env to version control

# Required: OpenAI API Key
OPENAI_API_KEY=sk-your-key-here

# Optional: Model selection
OPENAI_MODEL=gpt-4

# Optional: Debug mode
DEBUG=false
```

### .gitignore

```
# Environment variables
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*.so
.Python
venv/
haiku-env/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

---

## Configuration Module

Create `src/[config.py](http://config.py)`:

```python
# src/config.py - Configuration management

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # Required
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Optional with defaults
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")
        
        if not cls.OPENAI_API_KEY.startswith("sk-"):
            errors.append("OPENAI_API_KEY appears invalid (should start with 'sk-')")
        
        if errors:
            for error in errors:
                print(f"❌ Config Error: {error}")
            return False
        
        print("✅ Configuration validated successfully")
        return True

# Validate on import
if __name__ == "__main__":
    Config.validate()
```

---

## Decision Tree: API Key Setup

```
┌─────────────────────────────────────────┐
│  Do you have an OpenAI account?         │
└─────────────────────────────────────────┘
          │                    │
         YES                   NO
          │                    │
          ▼                    ▼
┌─────────────────┐   ┌─────────────────────────┐
│ Go to platform  │   │ Create account at       │
│ .openai.com     │   │ platform.openai.com     │
│ /api-keys       │   │ Add payment method      │
└─────────────────┘   └─────────────────────────┘
          │                    │
          └────────┬───────────┘
                   ▼
┌─────────────────────────────────────────┐
│  Create new API key                     │
│  Copy key (only shown once!)            │
└─────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  Paste into .env file                   │
│  Run: python src/config.py              │
│  Verify: ✅ Configuration validated      │
└─────────────────────────────────────────┘
```

---

## Testing API Connection

```python
# test_api.py - Verify API connection

from langchain_openai import ChatOpenAI
from config import Config

def test_api_connection():
    """Test that API key works."""
    
    if not Config.validate():
        return False
    
    try:
        llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=0,
            max_tokens=10
        )
        
        response = llm.invoke("Say 'API OK'")
        print(f"✅ API Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

if __name__ == "__main__":
    test_api_connection()
```

---

## Acceptance Criteria

- [ ]  `.env` file created with valid API key
- [ ]  `.env.example` created and committed
- [ ]  `.gitignore` includes `.env`
- [ ]  `src/[config.py](http://config.py)` validates configuration
- [ ]  `test_[api.py](http://api.py)` returns ✅
- [ ]  No secrets visible in git history

---

## Sub-Pages

[v0.1.2a — Environment File Creation & Structure](v0%201%202a%20%E2%80%94%20Environment%20File%20Creation%20&%20Structure%20a1234567890abcdef1234567890abcd01.md)

[v0.1.2b — Git Security & Secret Protection](../../phase-1/v0.1.2/git_security_and_secret_protection.md)

[v0.1.2c — Configuration Module Implementation](v0%201%202c%20%E2%80%94%20Configuration%20Module%20Implementation%20c3456789012cdef3456789012cdef03.md)

[v0.1.2d — API Connection Testing & Validation](v0%201%202d%20%E2%80%94%20API%20Connection%20Testing%20&%20Validation%20d4567890123def4567890123def0104.md)

---

## Security Checklist

- [ ]  API key starts with `sk-`
- [ ]  `.env` is in `.gitignore`
- [ ]  `.env` is NOT tracked by git (`git status` shows untracked)
- [ ]  `.env.example` has placeholder values only
- [ ]  No hardcoded keys in any Python files