# v0.1.0 — Phase 1: Environment & Tech Stack

<aside>

**Phase:** 1 — Environment & Tech Stack

**Version:** v0.1.0

**Status:** Development

**Duration:** 1.5-2 hours

**Objective:** Configure development environment and install all dependencies

</aside>

---

## Phase Overview

This phase transforms your machine into a working development environment. By the end, you will have:

1. A **clean Python virtual environment**
2. All **dependencies installed and verified**
3. **API keys configured** securely
4. A **project scaffold** ready for code

---

## Version Roadmap

The three sub-versions (v0.1.1, v0.1.2, v0.1.3) are **not strictly sequential**. Some
sub-parts have cross-version dependencies — notably, `src/config.py` (v0.1.2c) requires
the `src/` directory created in v0.1.3a. The execution order below respects these
dependencies.

### Dependency-Ordered Execution Sequence

| Step | Sub-Part | Title | Depends On |
|------|----------|-------|------------|
| 1 | v0.1.1a | Python Environment Verification | — |
| 2 | v0.1.1b | LangChain & LLM Libraries | Step 1 |
| 3 | v0.1.1c | Supporting Libraries + `requirements.txt` | Step 2 |
| 4 | v0.1.2a | Environment File Creation (`.env`, `.env.example`) | — |
| 5 | v0.1.2b | Git Security & Secret Protection | Step 4 |
| 6 | v0.1.3a | Directory Structure Creation (`src/`, etc.) | — |
| 7 | v0.1.3b | Root Configuration Files (`LICENSE`, verify others) | Steps 3, 4, 5 |
| 8 | v0.1.2c | Configuration Module (`src/config.py`) | Steps 4, 6 |
| 9 | v0.1.2d | API Connection Testing (`tests/test_api.py`) | Step 8 |
| 10 | v0.1.3c | Source Module Stubs (7 modules in `src/`) | Steps 6, 8 |
| 11 | v0.1.3d | Git Verification & Phase Commit | All above |

### Dependency Graph

```
v0.1.1a ─→ v0.1.1b ─→ v0.1.1c ─────────────────────┐
                                                      ▼
v0.1.2a ─→ v0.1.2b ──────────────────────────→ v0.1.3b
   │                                              │
   └──────────────┐                                │
                  ▼                                ▼
v0.1.3a ──→ v0.1.2c ─→ v0.1.2d             (verify all)
               │                                   │
               └──────→ v0.1.3c ──────────→ v0.1.3d
```

### Commit Checkpoints

1. After Step 3 (v0.1.1c): `feat(v0.1.1): install dependencies and create requirements.txt`
2. After Step 5 (v0.1.2b): `feat(v0.1.2b): add environment config and git security`
3. After Step 7 (v0.1.3b): `feat(v0.1.3b): create directory structure and root config files`
4. After Step 9 (v0.1.2d): `feat(v0.1.2d): implement Config class and API connection test`
5. After Step 11 (v0.1.3d): `feat(v0.1.3d): add source module stubs and finalize Phase 1 scaffold`

---

## Phase Exit Criteria

- [ ]  `python --version` returns 3.10+
- [ ]  `pip list` shows all required packages
- [ ]  `.env` file exists with `OPENAI_API_KEY`
- [ ]  Project directory matches spec structure
- [ ]  `python -c "import langchain; print('OK')"` succeeds

---

## Phase 0 Carryover

Phase 0 already established several artifacts that overlap with Phase 1 deliverables.
Steps marked as "verification" confirm these meet the spec rather than recreating them:

- **Python 3.14 + `.venv/`** — Already active (Step 1 verifies)
- **Git repository** — Initialized on `main` with clean history
- **`pytest.ini`** — Marker registration in place
- **`tests/`** — 11 test files + `conftest.py` from Phase 0
- **`benchmarks/samples/`** — 3 curated procedural documents

---

## Decision Tree: Environment Setup

```
┌─────────────────────────────────────────┐
│  Do you have Python 3.10+ installed?    │
└─────────────────────────────────────────┘
          │                    │
         YES                   NO
          │                    │
          ▼                    ▼
┌─────────────────┐   ┌─────────────────────┐
│ Create venv     │   │ Install via pyenv   │
│ python -m venv  │   │ or python.org       │
└─────────────────┘   └─────────────────────┘
          │                    │
          └────────┬───────────┘
                   ▼
┌─────────────────────────────────────────┐
│  Do you have an OpenAI API key?         │
└─────────────────────────────────────────┘
          │                    │
         YES                   NO
          │                    │
          ▼                    ▼
┌─────────────────┐   ┌─────────────────────┐
│ Add to .env     │   │ Create at           │
│ file            │   │ platform.openai.com │
└─────────────────┘   └─────────────────────┘
```

---

## User Stories

---

## Workflow: Quick Start

```bash
# 1. Create and activate virtual environment
python -m venv haiku-env
source haiku-env/bin/activate  # macOS/Linux
# haiku-env\Scripts\activate   # Windows

# 2. Install dependencies
pip install langchain langchain-openai tiktoken llmlingua chromadb streamlit python-dotenv

# 3. Create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 4. Verify installation
python -c "import langchain; import tiktoken; print('Environment OK')"
```

---

## Sub-Pages

[v0.1.1 — Core Dependencies Setup](../../phase-1/v0.1.1/README.md)

[v0.1.2 — API Configuration & Secrets](../../phase-1/v0.1.2/README.md)

[v0.1.3 — Project Scaffolding](../../phase-1/v0.1.3/README.md)