# v0.1.1 — Core Dependencies Setup

<aside>

**Version:** v0.1.1

**Parent:** v0.1.0 — Environment & Tech Stack

**Status:** ⬜ Not Started

**Duration:** 45-60 minutes

**Deliverable:** Fully configured Python environment with all dependencies

</aside>

---

## Objective

Install and verify all required dependencies. This version is broken into **sub-versions** for granular tracking:

---

## Complete Dependency List

---

## Workflow: Dependency Installation

```
┌─────────────────────────────────────────────────────────────────┐
│                 DEPENDENCY INSTALLATION FLOW                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   v0.1.1a: PYTHON ENVIRONMENT                                   │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │ 1. Check Python version (≥3.10)                           │ │
│   │ 2. Create virtual environment                              │ │
│   │ 3. Activate environment                                    │ │
│   │ 4. Upgrade pip                                             │ │
│   └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│   v0.1.1b: LLM LIBRARIES                                        │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │ 1. pip install langchain langchain-openai                 │ │
│   │ 2. pip install tiktoken                                    │ │
│   │ 3. Verify: import langchain                                │ │
│   └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│   v0.1.1c: SUPPORTING LIBRARIES                                 │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │ 1. pip install streamlit python-dotenv                    │ │
│   │ 2. pip install llmlingua                                   │ │
│   │ 3. pip install pytest (optional)                           │ │
│   │ 4. Freeze requirements.txt                                 │ │
│   └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Sub-Pages

[v0.1.1a — Python Environment Setup](../../phase-1/v0.1.1/python_environment_setup.md)

[v0.1.1b — LangChain & LLM Libraries](../../phase-1/v0.1.1/langchain_and_llm_libraries.md)

[v0.1.1c — Supporting Libraries](../../phase-1/v0.1.1/supporting_libraries.md)

---

## Verification Script

Run this after completing all sub-versions:

```python
# verify_install.py - Verify all dependencies

def verify_dependencies():
    """Verify all required packages are installed."""
    
    required = {
        "langchain": "0.1.0",
        "langchain_openai": "0.0.5",
        "tiktoken": "0.5.0",
        "streamlit": "1.29.0",
        "dotenv": "1.0.0",
    }
    
    results = {}
    
    for package, min_version in required.items():
        try:
            module = __import__(package)
            version = getattr(module, "__version__", "unknown")
            results[package] = {"status": "✅", "version": version}
        except ImportError:
            results[package] = {"status": "❌", "version": "NOT FOUND"}
    
    return results

if __name__ == "__main__":
    results = verify_dependencies()
    for pkg, info in results.items():
        print(f"{info['status']} {pkg}: {info['version']}")
```

---

## Acceptance Criteria

- [ ]  Python 3.10+ installed and verified
- [ ]  Virtual environment created and activated
- [ ]  All required packages installed
- [ ]  `verify_[install.py](http://install.py)` shows all ✅
- [ ]  `requirements.txt` generated with pinned versions

---

## Troubleshooting Guide

---

## Logging

Log all installation commands and outputs:

```bash
# Create install log
pip install langchain 2>&1 | tee -a install.log
pip install tiktoken 2>&1 | tee -a install.log
# ... repeat for all packages
```