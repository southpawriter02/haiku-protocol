# v0.1.1a — Python Environment Setup

<aside>

**Version:** v0.1.1a

**Parent:** v0.1.1 — Core Dependencies Setup

**Status:** ⬜ Not Started

**Duration:** 10-15 minutes

**Deliverable:** Python 3.10+ with virtual environment

</aside>

---

## Objective

Establish a clean, isolated Python environment for the project.

---

## Prerequisites Check

```bash
# Check current Python version
python --version
# OR
python3 --version

# Expected output: Python 3.10.x or higher
```

---

## Decision Tree: Python Installation

```
┌─────────────────────────────────────────┐
│  python --version returns 3.10+?        │
└─────────────────────────────────────────┘
          │                    │
         YES                   NO
          │                    │
          ▼                    ▼
┌─────────────────┐   ┌─────────────────────────┐
│ Skip to venv    │   │ Which OS are you on?    │
│ creation        │   └─────────────────────────┘
└─────────────────┘        │         │        │
                        macOS    Windows    Linux
                           │         │        │
                           ▼         ▼        ▼
              ┌────────────┐ ┌────────┐ ┌────────────┐
              │ brew       │ │ python │ │ apt/yum    │
              │ install    │ │ .org   │ │ install    │
              │ python@3.11│ │ download│ │ python3.11│
              └────────────┘ └────────┘ └────────────┘
```

---

## Installation by OS

### macOS

```bash
# Option 1: Homebrew (recommended)
brew install python@3.11

# Option 2: pyenv (for multiple versions)
brew install pyenv
pyenv install 3.11.6
pyenv global 3.11.6

# Verify
python3 --version
```

### Windows

```powershell
# Option 1: Download from python.org
# 1. Go to https://www.python.org/downloads/
# 2. Download Python 3.11.x
# 3. Run installer
# 4. ✅ Check "Add Python to PATH"

# Option 2: Windows Store
# Search "Python 3.11" in Microsoft Store

# Verify
python --version
```

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# Verify
python3.11 --version
```

---

## Virtual Environment Setup

```bash
# Navigate to project directory
cd ~/projects/haiku-protocol

# Create virtual environment
python -m venv haiku-env
# OR
python3 -m venv haiku-env

# Activate (macOS/Linux)
source haiku-env/bin/activate

# Activate (Windows PowerShell)
.\haiku-env\Scripts\Activate.ps1

# Activate (Windows CMD)
haiku-env\Scripts\activate.bat

# Verify activation (should show haiku-env prefix)
which python  # macOS/Linux
where python  # Windows
```

---

## Upgrade pip

```bash
# Always upgrade pip in a new venv
pip install --upgrade pip

# Verify
pip --version
# Expected: pip 23.x.x or higher
```

---

## Acceptance Criteria

- [ ]  `python --version` returns 3.10 or higher
- [ ]  Virtual environment `haiku-env` created
- [ ]  Virtual environment activated (prompt shows `(haiku-env)`)
- [ ]  `pip --version` shows latest version
- [ ]  `which python` points to `haiku-env/bin/python`

---

## Verification Commands

```bash
# All-in-one verification
echo "=== Python Environment Verification ==="
echo "Python: $(python --version)"
echo "Pip: $(pip --version)"
echo "Location: $(which python)"
echo "Venv Active: $VIRTUAL_ENV"
```

---

## Logging

```bash
# Log environment setup
echo "$(date): Python environment setup" >> setup.log
python --version >> setup.log
pip --version >> setup.log
echo "Venv: $VIRTUAL_ENV" >> setup.log
```

---

## Inputs from Previous Sub-Parts

This sub-part is the **first step in v0.1.1 — Core Dependencies Setup**. It does not receive inputs from prior v0.1.1 sub-parts because none exist yet. However, it depends on:

- **v0.1.0 — Phase 1 Environment & Tech Stack**: Decision to use Python 3.10+ and virtual environments
- **v0.0.1a — Academic Research Survey**: Research phase established Python as the primary language for LLM orchestration

---

## Outputs to Next Sub-Part

This sub-part produces:

- **Python 3.10+ verified and accessible** via `python` or `python3` command
- **Virtual environment `haiku-env`** created and activated
- **pip upgraded** to latest version within the virtual environment

**How v0.1.1b uses these outputs:**

v0.1.1b (LangChain & LLM Libraries) requires:
- An activated virtual environment to install packages into
- pip upgraded to handle dependency resolution
- Python 3.10+ for compatibility with langchain and tiktoken

---

## Troubleshooting