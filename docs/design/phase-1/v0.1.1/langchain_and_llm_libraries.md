# v0.1.1b — LangChain & LLM Libraries

<aside>

**Version:** v0.1.1b

**Parent:** v0.1.1 — Core Dependencies Setup

**Status:** ⬜ Not Started

**Duration:** 15-20 minutes

**Deliverable:** LangChain and LLM libraries installed

</aside>

---

## Objective

Install the core LLM orchestration libraries that power the encoder pipeline.

---

## Dependencies

---

## Installation Workflow

```bash
# Ensure venv is activated
source haiku-env/bin/activate  # or Windows equivalent

# Install LangChain core
pip install langchain

# Install OpenAI integration
pip install langchain-openai

# Install tokenizer
pip install tiktoken

# Verify installations
python -c "import langchain; print(f'langchain: {langchain.__version__}')"
python -c "import langchain_openai; print('langchain_openai: OK')"
python -c "import tiktoken; print('tiktoken: OK')"
```

---

## Alternative: Single Command

```bash
pip install langchain langchain-openai tiktoken
```

---

## Verification Script

```python
# verify_llm_libs.py

def verify_llm_libraries():
    """Verify LLM libraries are installed."""
    
    libraries = [
        ("langchain", "langchain"),
        ("langchain_openai", "langchain-openai"),
        ("tiktoken", "tiktoken"),
    ]
    
    all_ok = True
    
    for module_name, display_name in libraries:
        try:
            module = __import__(module_name)
            version = getattr(module, "__version__", "installed")
            print(f"✅ {display_name}: {version}")
        except ImportError as e:
            print(f"❌ {display_name}: NOT FOUND ({e})")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    success = verify_llm_libraries()
    exit(0 if success else 1)
```

---

## Quick Test: LangChain

```python
# test_langchain.py

from langchain_core.prompts import PromptTemplate

# Test PromptTemplate (no API required)
template = PromptTemplate(
    input_variables=["topic"],
    template="Tell me about {topic}"
)

result = template.format(topic="AI compression")
print(f"✅ PromptTemplate works: {result[:50]}...")

# Note: LLMChain is deprecated as of langchain 0.1.17+.
# Use LCEL (LangChain Expression Language) chains instead.
# Example: chain = prompt | llm | output_parser
```

---

## Quick Test: tiktoken

```python
# test_tiktoken.py

import tiktoken

# Load GPT-4 tokenizer
enc = tiktoken.encoding_for_model("gpt-4")

# Test tokenization
text = "To restart the server, you must first ensure that the configuration file is saved."
tokens = enc.encode(text)

print(f"✅ tiktoken works")
print(f"   Text: '{text[:40]}...'")
print(f"   Tokens: {len(tokens)}")
print(f"   Token IDs: {tokens[:10]}...")
```

---

## Acceptance Criteria

- [ ]  `pip show langchain` returns version ≥0.1.0
- [ ]  `pip show langchain-openai` returns version ≥0.0.5
- [ ]  `pip show tiktoken` returns version ≥0.5.0
- [ ]  `verify_llm_[libs.py](http://libs.py)` shows all ✅
- [ ]  `test_[tiktoken.py](http://tiktoken.py)` counts tokens correctly

---

## Dependency Notes

### LangChain Architecture

```
langchain (core)
├── langchain-core       # Base abstractions
├── langchain-community  # Third-party integrations
└── langchain-openai     # OpenAI-specific (we use this)
```

### tiktoken Models

---

## Inputs from Previous Sub-Parts

**From v0.1.1a (Python Environment Setup):**
- Python 3.10+ installed and verified
- Virtual environment `haiku-env` created and activated
- pip upgraded to latest version

---

## Outputs to Next Sub-Part

This sub-part produces:

- **langchain** package installed (core LLM orchestration)
- **langchain-openai** package installed (OpenAI integration)
- **tiktoken** package installed (cl100k_base tokenizer for GPT-4)
- Verification script `verify_llm_libs.py` confirms all packages available

**How v0.1.1c uses these outputs:**

v0.1.1c (Supporting Libraries) requires:
- langchain core installed (some supporting libraries depend on it)
- Virtual environment active (to install additional packages)
- All core LLM libraries verified before adding supporting tools

---

## Troubleshooting