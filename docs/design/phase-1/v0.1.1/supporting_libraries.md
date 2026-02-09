# v0.1.1c — Supporting Libraries

<aside>

**Version:** v0.1.1c

**Parent:** v0.1.1 — Core Dependencies Setup

**Status:** ⬜ Not Started

**Duration:** 15-20 minutes

**Deliverable:** Supporting libraries installed and requirements.txt frozen

</aside>

---

## Objective

Install remaining dependencies for UI, benchmarking, and testing. Freeze all versions.

---

## Dependencies

---

## Installation Workflow

```bash
# Ensure venv is activated
source haiku-env/bin/activate

# Install Streamlit (demo UI)
pip install streamlit

# Install dotenv (environment variables)
pip install python-dotenv

# Install LLMLingua (benchmarking)
pip install llmlingua

# Optional: Testing
pip install pytest

# Optional: Vector storage (for future RAG features)
# pip install chromadb
```

---

## Alternative: Single Command

```bash
pip install streamlit python-dotenv llmlingua pytest
```

---

## Freeze Requirements

```bash
# Generate requirements.txt with exact versions
pip freeze > requirements.txt

# View the file
cat requirements.txt
```

---

## Curated requirements.txt

For reproducibility, use pinned versions. Note: These are initial installation versions. The authoritative pinned versions for the project are in v0.1.3b's requirements.txt, which may specify updated versions after dependency resolution:

```
# requirements.txt - Haiku Protocol Dependencies
# Generated: 2026-02-05

# Core LLM Libraries
langchain==0.1.0
langchain-openai==0.0.5
langchain-core==0.1.10
tiktoken==0.5.2

# UI
streamlit==1.29.0

# Configuration
python-dotenv==1.0.0

# Benchmarking
llmlingua==0.1.3

# Testing
pytest==7.4.3

# Transitive dependencies (auto-installed)
# openai, pydantic, etc.
```

---

## Verification Script

```python
# verify_all_deps.py

def verify_all_dependencies():
    """Verify all project dependencies."""
    
    packages = {
        "langchain": "Core LLM framework",
        "langchain_openai": "OpenAI integration",
        "tiktoken": "Tokenizer",
        "streamlit": "Demo UI",
        "dotenv": "Environment variables",
        "llmlingua": "Benchmarking",
        "pytest": "Testing (optional)",
    }
    
    results = {"pass": [], "fail": []}
    
    for pkg, purpose in packages.items():
        try:
            __import__(pkg)
            results["pass"].append(pkg)
            print(f"✅ {pkg}: {purpose}")
        except ImportError:
            results["fail"].append(pkg)
            print(f"❌ {pkg}: {purpose} - NOT FOUND")
    
    print(f"\n{'='*40}")
    print(f"Passed: {len(results['pass'])}/{len(packages)}")
    
    return len(results["fail"]) == 0

if __name__ == "__main__":
    verify_all_dependencies()
```

---

## Quick Test: Streamlit

```bash
# Create a minimal test app
cat > test_streamlit.py << 'EOF'
import streamlit as st
st.title("✅ Streamlit Works!")
st.write("If you see this, installation was successful.")
EOF

# Run it (opens browser)
streamlit run test_streamlit.py

# Press Ctrl+C to stop
```

---

## Quick Test: LLMLingua

```python
# test_llmlingua.py

from llmlingua import PromptCompressor

# Initialize compressor
compressor = PromptCompressor()

# Test compression
text = "This is a test sentence to verify that LLMLingua is working correctly."

try:
    result = compressor.compress_prompt(text)
    print(f"✅ LLMLingua works")
    print(f"   Original: {text[:40]}...")
    print(f"   Compressed: {result['compressed_prompt'][:40]}...")
except Exception as e:
    print(f"⚠️ LLMLingua warning: {e}")
    print("   (May require GPU for full functionality)")
```

---

## Acceptance Criteria

- [ ]  `streamlit --version` returns version info
- [ ]  `pip show python-dotenv` shows installed
- [ ]  `pip show llmlingua` shows installed
- [ ]  `pip show pytest` shows installed (optional)
- [ ]  `requirements.txt` exists with pinned versions
- [ ]  `verify_all_[deps.py](http://deps.py)` shows all ✅

---

## Final Installation Verification

```bash
# All-in-one check
echo "=== Final Dependency Check ==="
pip list | grep -E "langchain|tiktoken|streamlit|dotenv|llmlingua|pytest"
```

Expected output:

```
langchain                0.1.0
langchain-openai         0.0.5
llmlingua                0.1.3
python-dotenv            1.0.0
pytest                   7.4.3
streamlit                1.29.0
tiktoken                 0.5.2
```

---

## Logging

```bash
# Log all installations
echo "=== Installation Log ===" >> install.log
echo "Date: $(date)" >> install.log
pip list >> install.log
echo "" >> install.log
```

---

## Inputs from Previous Sub-Parts

**From v0.1.1a (Python Environment Setup):**
- Python 3.10+ installed and verified
- Virtual environment `haiku-env` created and activated

**From v0.1.1b (LangChain & LLM Libraries):**
- langchain, langchain-openai, and tiktoken installed
- Core LLM libraries verified

---

## Outputs to Next Sub-Part

This sub-part produces:

- **streamlit** package installed (demo UI framework)
- **python-dotenv** package installed (environment variable loading)
- **llmlingua** package installed (benchmarking baseline)
- **pytest** package installed (testing framework)
- **requirements.txt** generated with `pip freeze` (initial version pinning)

**How v0.1.2 uses these outputs:**

v0.1.2 (API Configuration & Secrets) requires:
- python-dotenv installed (for `load_dotenv()` in config module)
- All packages installed and frozen in requirements.txt

**How v0.1.3b uses these outputs:**

v0.1.3b (Root Configuration Files) uses:
- The dependency list from this sub-part as the basis for the project's authoritative requirements.txt
- v0.1.3b may update version numbers after resolving transitive dependencies

---

## Troubleshooting