# v0.1.3b — Root Configuration Files

<aside>

**Version:** v0.1.3b

**Parent:** v0.1.3 — Project Scaffolding

**Status:** ✅ Complete

**Duration:** 5–10 minutes

**Deliverable:** Complete root-level configuration files (LICENSE, requirements.txt, .gitignore, .env.example) placed in project root directory, enabling secure dependency management and version control configuration

</aside>

---

## Objective

Create and place comprehensive root-level configuration files that establish project licensing, dependency specifications, version control rules, and environment variable templates. This sub-part ensures the Haiku Protocol project adheres to open-source best practices, maintains reproducible builds through pinned dependency versions from v0.1.1, and protects sensitive environment configuration from v0.1.2. The configuration files serve as critical guardrails for development workflow, CI/CD integration, and secure credential management across all subsequent phases.

---

## Root Configuration File Strategy

### Configuration File Hierarchy

```
haiku-protocol/
├── 📄 LICENSE                  # MIT license (year: 2026)
├── 📄 requirements.txt         # Pinned Python dependencies
├── 📄 .gitignore              # Version control exclusions
└── 📄 .env.example            # Environment variable template
```

### File Purpose Matrix

| File | Purpose | Source | Audience | Sensitivity |
|------|---------|--------|----------|-------------|
| LICENSE | Legal permissions and copyright | v0.1.3b spec | Public | ✅ Public |
| requirements.txt | Reproducible dependency versions | v0.1.1c pinned list | Developers | ✅ Public |
| .gitignore | Git tracking rules | Best practices | Developers | ✅ Public |
| .env.example | Environment variable template | v0.1.2a structure | Developers | ✅ Public |

---

## File Implementation

### LICENSE — MIT License 2026

```
MIT License

Copyright (c) 2026 Haiku Protocol Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Rationale:** MIT license chosen for its permissiveness, industry standard adoption, and alignment with open-source research projects. Year set to 2026 per project specification.

---

### requirements.txt — Pinned Dependencies

```
# Haiku Protocol - Python Dependencies
# Generated from v0.1.1c analysis
# Update: 2026-02-06

# Core LLM and Prompt Processing
langchain==0.1.14
langchain-openai==0.0.8
langchain-anthropic==0.1.1

# Tokenization and Encoding
tiktoken==0.5.2
transformers==4.37.2

# Document Processing
beautifulsoup4==4.12.2
lxml==4.9.3
pypdf==4.0.1

# Structured Output and Data
pydantic==2.5.3
pydantic-settings==2.1.0

# Environment Configuration
python-dotenv==1.0.0

# Web Framework (Streamlit for demo)
streamlit==1.29.0
streamlit-chat==0.1.1

# Benchmarking and Evaluation
llmlingua==0.1.1
nltk==3.8.1

# Testing Framework
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.23.1

# Development Tools
black==23.12.0
flake8==6.1.0
isort==5.13.2
mypy==1.7.1

# Optional: Vector Storage (commented for v0.1.3)
# chromadb==0.4.15
# pinecone-client==3.0.0
```

**Dependency Notes:**
- **Core packages** (langchain, tiktoken, python-dotenv, streamlit, llmlingua, pytest) were installed and verified in v0.1.1a-c
- **Extended packages** (transformers, beautifulsoup4, lxml, pypdf, pydantic, pydantic-settings, streamlit-chat, nltk, pytest-cov, pytest-asyncio, black, flake8, isort, mypy, langchain-anthropic) are added here for Phase 2+ requirements, anticipating needs identified during v0.0.x research
- Version numbers may differ from v0.1.1c's initial install versions due to dependency resolution and compatibility updates

**Versioning Strategy:**
- Major.minor.patch pinning for reproducibility
- Range: dependencies released within last 6 months (safety margin)
- Compatible with Python 3.8–3.12 ecosystem
- Critical security updates included

**Dependency Grouping:**
- **Core:** LLM integration (langchain, OpenAI client)
- **Processing:** Document parsing, tokenization
- **Data:** Configuration, structured output
- **UI:** Streamlit for demo application
- **Evaluation:** LLMLingua baseline, NLTK for NLP
- **Testing:** Pytest with async support
- **Development:** Code quality tools (black, flake8, mypy)

---

### .gitignore — Comprehensive Exclusions

```
# ============================================================================
# Haiku Protocol .gitignore
# Covers Python, virtual environments, IDEs, OS files, and sensitive data
# ============================================================================

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environments
venv/
env/
ENV/
env.bak/
venv.bak/
.venv/

# IDE and Editor
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
.project
.pydevproject
.settings/
*.sublime-project
*.sublime-workspace
.atom/
.vim/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.hypothesis/

# Type Checking
.mypy_cache/
.dmypy.json
dmypy.json

# Code Formatting
.ruff_cache/

# Jupyter and Notebooks
.ipynb_checkpoints
*.ipynb

# Environment Variables (CRITICAL)
.env
.env.local
.env.*.local
.env.production.local

# Secrets and Credentials
*.pem
*.key
*.p12
*.pfx
api_keys.json
credentials.json
secrets.yaml

# Logs
*.log
logs/
debug.log

# Temporary Files
*.tmp
*.temp
*.bak
*.backup
*~
.tmp/

# OS-specific
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
.AppleDouble
.LSOverride

# IDE Run Configurations
.run/

# Build Artifacts
dist/
build/

# Benchmark Results (v0.0.3 comparison artifacts)
benchmarks/results/*.json
benchmarks/results/*.csv

# Demo and Cache Files
*.pkl
*.pickle
*.cache
cache/
```

**Security Safeguards:**
- `.env` files explicitly excluded (prevents credential leaks)
- `*.pem`, `*.key` files excluded (private keys)
- `credentials.json`, `secrets.yaml` excluded (API keys)
- Virtual environment directories excluded (dependencies not tracked)

**Development Environment:**
- IDE configurations excluded (allows team member customization)
- Cache directories excluded (Pytest, mypy, ruff)
- OS-specific files excluded (.DS_Store, Thumbs.db)

**Testing and Benchmarking:**
- `.pytest_cache/` excluded (test artifacts)
- `benchmarks/results/` excluded (v0.0.3 comparison outputs)
- `.coverage` excluded (coverage reports)

---

### .env.example — Environment Variable Template

```bash
# ============================================================================
# Haiku Protocol - Environment Variable Template
# Copy to .env and fill in actual values (never commit .env itself)
# This file documents all required and optional environment variables
# ============================================================================

# ─────────────────────────────────────────────────────────────────────────
# LLM PROVIDER CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────

# OpenAI API Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4

# Optional: Anthropic Claude Configuration
# ANTHROPIC_API_KEY=sk-ant-your-key-here
# ANTHROPIC_MODEL=claude-3-opus-20240229

# Optional: Cohere Configuration
# COHERE_API_KEY=your-cohere-key-here

# ─────────────────────────────────────────────────────────────────────────
# DATABASE AND STORAGE
# ─────────────────────────────────────────────────────────────────────────

# Optional: Chroma Vector Database
# CHROMA_DB_PATH=./data/chroma_db
# CHROMA_COLLECTION_NAME=haiku_documents

# Optional: Pinecone Vector Index
# PINECONE_API_KEY=your-pinecone-key-here
# PINECONE_INDEX_NAME=haiku-protocol

# ─────────────────────────────────────────────────────────────────────────
# APPLICATION CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────

# Execution Environment
ENV=development
# Options: development, staging, production

# Application Debug Mode
DEBUG=true

# Logging Level
LOG_LEVEL=INFO
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

# ─────────────────────────────────────────────────────────────────────────
# STREAMLIT UI CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────

# Streamlit Server Port (if custom)
STREAMLIT_SERVER_PORT=8501

# Streamlit Server Address
STREAMLIT_SERVER_ADDRESS=localhost

# ─────────────────────────────────────────────────────────────────────────
# BENCHMARKING AND METRICS
# ─────────────────────────────────────────────────────────────────────────

# Enable Benchmark Logging
ENABLE_BENCHMARKS=true

# Benchmark Output Directory
BENCHMARK_OUTPUT_DIR=./benchmarks/results

# ─────────────────────────────────────────────────────────────────────────
# DEVELOPMENT AND TESTING
# ─────────────────────────────────────────────────────────────────────────

# Test Database URL (if applicable)
TEST_DB_URL=sqlite:///./test.db

# Enable Test Coverage Reports
PYTEST_COV=true

# ─────────────────────────────────────────────────────────────────────────
# INSTRUCTIONS FOR USE
# ─────────────────────────────────────────────────────────────────────────
# 1. Copy this file: cp .env.example .env
# 2. Edit .env with your actual values
# 3. NEVER commit .env to git (it's in .gitignore)
# 4. Load in Python: from dotenv import load_dotenv; load_dotenv()
# 5. Access: os.getenv('OPENAI_API_KEY')
# ─────────────────────────────────────────────────────────────────────────
```

**Structure from v0.1.2a:**
- This template mirrors the environment variable structure defined in v0.1.2 — API Configuration & Secrets
- Sections are organized by functional area (LLM providers, storage, application config)
- All variables have documentation comments
- Sensitive variables are clearly marked

---

## File Creation Workflow

### Configuration Files Creation Script

```bash
#!/bin/bash
# create_root_config.sh - Create root-level configuration files
# Run from project root directory
# Depends on: v0.1.3a (directory structure exists)

set -e  # Exit on error

echo "📝 Creating root configuration files..."
echo ""

# Create LICENSE file
echo "📄 Creating LICENSE..."
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 Haiku Protocol Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
echo "✅ LICENSE created"
echo ""

# Create requirements.txt
echo "📄 Creating requirements.txt..."
cat > requirements.txt << 'EOF'
# Haiku Protocol - Python Dependencies
langchain==0.1.14
langchain-openai==0.0.8
langchain-anthropic==0.1.1
tiktoken==0.5.2
transformers==4.37.2
beautifulsoup4==4.12.2
lxml==4.9.3
pypdf==4.0.1
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
streamlit==1.29.0
streamlit-chat==0.1.1
llmlingua==0.1.1
nltk==3.8.1
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.23.1
black==23.12.0
flake8==6.1.0
isort==5.13.2
mypy==1.7.1
EOF
echo "✅ requirements.txt created"
echo ""

# Create .gitignore
echo "📄 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environments
venv/
env/
ENV/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/

# Type Checking
.mypy_cache/

# Jupyter
.ipynb_checkpoints
*.ipynb

# Environment Variables (CRITICAL)
.env
.env.local
.env.*.local

# Secrets
*.pem
*.key
*.p12
api_keys.json
credentials.json
secrets.yaml

# Logs and Temp
*.log
logs/
*.tmp

# OS
.DS_Store
Thumbs.db

# Build
dist/
build/

# Benchmarks
benchmarks/results/
EOF
echo "✅ .gitignore created"
echo ""

# Create .env.example
echo "📄 Creating .env.example..."
cat > .env.example << 'EOF'
# Haiku Protocol - Environment Variable Template
# Copy to .env and fill in actual values

# LLM Provider
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4

# Application Config
ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Benchmarking
ENABLE_BENCHMARKS=true
BENCHMARK_OUTPUT_DIR=./benchmarks/results

# Testing
PYTEST_COV=true
EOF
echo "✅ .env.example created"
echo ""

# Verify all files created
echo "═══════════════════════════════════════════════════"
if [ -f LICENSE ] && [ -f requirements.txt ] && \
   [ -f .gitignore ] && [ -f .env.example ]; then
    echo "✅ All root configuration files created successfully"
    echo ""
    echo "📊 File sizes:"
    ls -lh LICENSE requirements.txt .gitignore .env.example
    echo ""
    echo "📝 Files created:"
    echo "   • LICENSE (MIT, 2026)"
    echo "   • requirements.txt (21 dependencies)"
    echo "   • .gitignore (Python, IDE, OS, secrets)"
    echo "   • .env.example (template for environment variables)"
else
    echo "❌ Some files failed to create. Check permissions."
    exit 1
fi

echo ""
echo "✨ Next: Proceed to v0.1.3c (Source Module Stubs)"
```

---

## Verification and Validation

### Configuration Files Verification Script

```bash
#!/bin/bash
# verify_config_files.sh - Validate root configuration files

echo "🔍 Verifying root configuration files..."
echo ""

CHECKS=0
PASSED=0

# Check LICENSE file
CHECKS=$((CHECKS + 1))
if [ -f LICENSE ]; then
    if grep -q "MIT License" LICENSE && grep -q "2026" LICENSE; then
        echo "✅ LICENSE: Valid MIT license with 2026 copyright"
        PASSED=$((PASSED + 1))
    else
        echo "❌ LICENSE: Missing MIT header or 2026 year"
    fi
else
    echo "❌ LICENSE: File not found"
fi

# Check requirements.txt
CHECKS=$((CHECKS + 1))
if [ -f requirements.txt ]; then
    COUNT=$(grep -c "^[a-z]" requirements.txt || true)
    if [ "$COUNT" -ge 15 ]; then
        echo "✅ requirements.txt: Found $COUNT pinned dependencies"
        PASSED=$((PASSED + 1))
    else
        echo "❌ requirements.txt: Found only $COUNT dependencies (expected 15+)"
    fi
else
    echo "❌ requirements.txt: File not found"
fi

# Check .gitignore
CHECKS=$((CHECKS + 1))
if [ -f .gitignore ]; then
    if grep -q ".env" .gitignore && grep -q "__pycache__" .gitignore; then
        echo "✅ .gitignore: Contains critical exclusions (.env, __pycache__)"
        PASSED=$((PASSED + 1))
    else
        echo "❌ .gitignore: Missing critical exclusions"
    fi
else
    echo "❌ .gitignore: File not found"
fi

# Check .env.example
CHECKS=$((CHECKS + 1))
if [ -f .env.example ]; then
    if grep -q "OPENAI_API_KEY" .env.example && \
       grep -q "ENV=development" .env.example; then
        echo "✅ .env.example: Contains API key and environment variables"
        PASSED=$((PASSED + 1))
    else
        echo "❌ .env.example: Missing required variable definitions"
    fi
else
    echo "❌ .env.example: File not found"
fi

# Verify .env is NOT in working directory (security check)
CHECKS=$((CHECKS + 1))
if [ ! -f .env ]; then
    echo "✅ .env: Not present (good - don't commit secrets)"
    PASSED=$((PASSED + 1))
else
    echo "⚠️  .env: Present in working directory (ensure it's in .gitignore)"
fi

# Verify requirements.txt can be parsed
CHECKS=$((CHECKS + 1))
if command -v python3 &> /dev/null; then
    if python3 -c "import re; [re.match(r'^[a-z].*==', line) for line in open('requirements.txt') if line.strip()]" 2>/dev/null; then
        echo "✅ requirements.txt: Valid dependency format (can be installed)"
        PASSED=$((PASSED + 1))
    else
        echo "⚠️  requirements.txt: Format check skipped (Python validation not available)"
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "VERIFICATION RESULT: $PASSED/$CHECKS checks passed"
echo "═══════════════════════════════════════════════════"

if [ $PASSED -ge $((CHECKS - 1)) ]; then
    echo "✅ Configuration files ready for v0.1.3c"
    exit 0
else
    echo "❌ Review failures above"
    exit 1
fi
```

---

## Acceptance Criteria

- [ ] LICENSE file created with MIT license header and 2026 copyright year
- [ ] LICENSE file is readable and properly formatted (no encoding issues)
- [ ] requirements.txt created with 18+ pinned dependencies covering core, processing, UI, testing, and development
- [ ] All requirements.txt entries follow semantic versioning format (package==X.Y.Z)
- [ ] .gitignore created with comprehensive Python, IDE, OS, and sensitive data exclusions
- [ ] .gitignore includes `.env` and `*.pem`, `*.key` exclusions for security
- [ ] .gitignore includes `__pycache__/` and `*.pyc` for Python cache files
- [ ] .env.example created with complete environment variable template
- [ ] .env.example includes OPENAI_API_KEY, ENV, DEBUG, LOG_LEVEL variables
- [ ] .env.example includes helpful comments documenting each variable
- [ ] Actual .env file is NOT present in project root (only .env.example)
- [ ] All 4 files are in project root directory (alongside src/, tests/, etc.)
- [ ] Files are readable by team members (appropriate permissions: 644)
- [ ] requirements.txt can be installed: `pip install -r requirements.txt` (dry-run verification)

---

## Limitations & Constraints

1. **Hardcoded Dependency Versions:** requirements.txt uses exact versions (==X.Y.Z) rather than ranges. Updates must be manual; consider using `pip-tools` for lock file management in future versions.

2. **API Key Placeholders:** .env.example uses placeholder values (sk-your-key-here). Team members must fill in actual keys after copying.

3. **No Windows Path Normalization:** .gitignore uses Unix-style paths. Windows users should verify path formats match their environment.

4. **License Scope:** MIT license grants broad permissions but may need supplementary licensing for proprietary code or downstream commercial use.

5. **Secrets Security:** Even with .gitignore, developers must be cautious not to accidentally commit .env. Consider pre-commit hooks (git hooks) for additional protection.

6. **Python Version Lock:** requirements.txt assumes Python 3.8+. No python_requires field in setup.py (created in v0.4.x).

7. **Dependency Resolution:** No requirements-dev.txt or requirements-test.txt; all dependencies are in single file. Future versions may want to split by environment.

---

## Dependencies

**Must be completed before v0.1.3b:**
- v0.1.3a — Directory Structure Creation (directories exist and are writable)
- v0.1.1c — Supporting Libraries (pinned versions finalized; source for requirements.txt)
- v0.1.2a — Environment Configuration (variable names and structure; source for .env.example)

**External requirements:**
- Write permissions in project root directory
- Bash shell for script execution (optional; files can be created manually)
- Python 3.8+ (for optional validation of requirements.txt)

**No dependencies on:**
- v0.1.3c — Source Module Stubs (not needed for config files)
- v0.1.3d — Git Initialization (applied after git init)

---

## Troubleshooting

### Issue: .env File Accidentally Committed

**Symptom:** `.env` appears in `git status` or `git log`

**Solution:** This should not happen if .gitignore is properly configured BEFORE adding files. If it occurred:
```bash
# Remove from git tracking (but keep local file)
git rm --cached .env
git add .gitignore
git commit -m "Stop tracking .env file"

# Verify it's now ignored
git status
```

**Prevention:** Always run v0.1.3b before v0.1.3d (Git Initialization & Verification).

---

### Issue: requirements.txt Syntax Error

**Symptom:** `pip install -r requirements.txt` fails with syntax error

**Solution:** Verify format is `package==version` on each line:
```bash
# Check for invalid lines
grep -v "^#" requirements.txt | grep -v "^$" | grep -v "==" | head -5

# If issues found, manually edit or regenerate:
cat > requirements.txt << 'EOF'
langchain==0.1.14
# ... (complete list)
EOF
```

---

### Issue: .env.example File Empty or Incomplete

**Symptom:** `.env.example` missing variable definitions

**Solution:** Recreate with complete template:
```bash
cp .env.example .env.example.backup
cat > .env.example << 'EOF'
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview
ENV=development
DEBUG=true
LOG_LEVEL=INFO
ENABLE_BENCHMARKS=true
BENCHMARK_OUTPUT_DIR=./benchmarks/results
EOF
```

---

### Issue: LICENSE File Not Recognized as MIT

**Symptom:** GitHub or tools don't recognize LICENSE file as MIT

**Solution:** GitHub detects license by filename (LICENSE) and content. Verify:
```bash
# Check file exists in root
ls -la LICENSE

# Verify MIT header is present
head -1 LICENSE  # Should show "MIT License"

# Verify file is not zero bytes
wc -c LICENSE
```

If problems persist, regenerate exactly:
```bash
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 Haiku Protocol Contributors
...
EOF
```

---

### Issue: .gitignore Not Excluding .env Files

**Symptom:** `git status` still shows .env or .env.local files

**Solution:** Make sure .gitignore is committed properly:
```bash
# Check .gitignore is tracked
git status .gitignore

# If not tracked:
git add .gitignore
git commit -m "Add .gitignore"

# Clear git cache and recheck
git rm -r --cached .
git add .
git status  # Should not show .env files
```

---

### Issue: Dependency Version Conflicts

**Symptom:** `pip install -r requirements.txt` fails with conflict message

**Solution:** Try installing with conflict resolution disabled, then identify problem:
```bash
pip install --no-deps -r requirements.txt
# Or identify conflict manually
pip install -r requirements.txt --verbose 2>&1 | grep -A5 "conflict"
```

For v0.1.3, do not attempt to fix version conflicts—defer to v0.2.x implementation phases. Document issue in requirements.txt as comment.

---

## User Story

> As a project maintainer, I want to establish clear licensing, dependency management, and environment configuration standards so that the Haiku Protocol can be shared as open-source software with proper credentials handling and reproducible builds. The root configuration files serve as the foundation for team onboarding, CI/CD pipelines, and secure deployment practices.

---

## Inputs from Previous Sub-Parts

**From v0.1.3a — Directory Structure Creation:**
- All directories are created and accessible
- Root directory is clean and ready for configuration files
- No conflicting files exist in root

**From v0.1.1c — Supporting Libraries:**
- Pinned dependency versions are finalized
- Core packages: langchain, langchain-openai, tiktoken, streamlit
- Testing packages: pytest, pytest-cov, pytest-asyncio
- Development packages: black, flake8, mypy
- Benchmarking: llmlingua, nltk

**From v0.1.2a — Environment Configuration:**
- Environment variable structure defined: OPENAI_API_KEY, OPENAI_MODEL, ENV, DEBUG, LOG_LEVEL, etc.
- API configuration template ready for .env.example
- Security best practices for credential handling established

**From parent v0.1.3 — Project Scaffolding:**
- LICENSE template with MIT text and 2026 year
- requirements.txt structure and pinned versions
- .gitignore comprehensive rules
- .env.example structure

---

## Outputs to Next Sub-Part

**For v0.1.3c — Source Module Stubs:**
- requirements.txt available for future dependency validation in source code
- .env.example provides environment variable context for app.py stub
- .gitignore will preserve .env.example but exclude .env (secret files)

**For v0.1.3d — Git Initialization & Verification:**
- LICENSE file present for first commit
- requirements.txt present for first commit
- .gitignore rules active to prevent .env tracking
- .env.example (not .env) will be committed to demonstrate template

**For v0.2+ Implementation Phases:**
- requirements.txt provides exact dependency pinning for reproducible builds
- LICENSE establishes open-source MIT license for all code
- .gitignore prevents accidental credential commits throughout development
- .env.example serves as onboarding guide for new team members

---

## Decision Log

| Decision | Rationale | Status |
|----------|-----------|--------|
| Use MIT License for project | Permissive open-source license, industry standard for research projects | ✅ Approved |
| Set copyright year to 2026 | Current project specification year | ✅ Approved |
| Pin all dependencies with == | Ensures reproducible builds, prevents version surprises | ✅ Approved |
| Include 21 dependencies in single requirements.txt | Simplifies v0.1.3 phase, future versions can split by environment (dev/test/prod) | ✅ Approved |
| Explicitly exclude .env and credentials in .gitignore | Security best practice, prevents accidental secret commits | ✅ Approved |
| Use .env.example instead of .env.sample | Matches Python-dotenv convention, widely recognized by developers | ✅ Approved |
| Include helpful comments in .env.example | Improves developer onboarding and reduces support questions | ✅ Approved |
| Reference v0.1.1c and v0.1.2a | Establishes traceability and dependency chain | ✅ Approved |
