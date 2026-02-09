# v0.1.3a — Directory Structure Creation

<aside>

**Version:** v0.1.3a

**Parent:** v0.1.3 — Project Scaffolding

**Status:** ✅ Complete

**Duration:** 5–10 minutes

**Deliverable:** Complete directory tree with all required subdirectories, including `benchmarks/samples/` for v0.0.3 compatibility, and execution of `tree -L 2` for verification

</aside>

---

## Objective

Create the foundational directory structure for the Haiku Protocol project, establishing all required subdirectories (`src/`, `tests/`, `benchmarks/`, `benchmarks/samples/`, `examples/`, `diagrams/`, `docs/`) and initializing Python package markers (`__init__.py` files). This sub-part ensures the project has a professional, organized layout that supports modular development, testing, benchmarking, and documentation across all subsequent phases. The directory structure must match the parent v0.1.3 specification and enable seamless integration with v0.1.3b (configuration files) and v0.1.3c (source module stubs).

---

## Directory Structure Design

### Complete Project Layout

```
haiku-protocol/
│
├── 📁 src/                         # Source code packages
│   └── 📄 __init__.py              # Python package marker
│
├── 📁 tests/                       # Test suite and fixtures
│   └── 📄 __init__.py              # Python package marker
│
├── 📁 benchmarks/                  # Benchmark data and scripts
│   ├── 📄 __init__.py              # (optional) Python package marker
│   └── 📁 samples/                 # v0.0.3 baseline samples
│
├── 📁 examples/                    # Sample documents and outputs
│
├── 📁 diagrams/                    # Architecture diagrams and visuals
│
├── 📁 docs/                        # Project documentation
│
└── 📄 (placeholder files for next sub-parts)
```

### Directory Purpose Reference

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `src/` | Python source code packages | Encoder, decoder, chunker, extractor, synthesizer, validator, app |
| `tests/` | Unit and integration tests | Test modules for each src/ component |
| `benchmarks/` | Benchmark data and metrics | Baseline metrics, comparison scripts, results |
| `benchmarks/samples/` | v0.0.3 compatible sample data | Reference documents for consistent benchmarking |
| `examples/` | Usage examples and sample docs | Example input/output files for documentation |
| `diagrams/` | Architecture and flow diagrams | Mermaid source, PNG renders, demo GIFs |
| `docs/` | Additional project documentation | Literature reviews, decision logs, API docs |

---

## Scaffold Script Implementation

### scaffold.sh — Complete Directory Creator

```bash
#!/bin/bash
# scaffold.sh - Project Structure Initialization
# Creates complete directory hierarchy for Haiku Protocol v0.1.3
# Usage: chmod +x scaffold.sh && ./scaffold.sh

set -e  # Exit on any error

echo "🏗️  Starting Haiku Protocol Project Scaffold..."
echo ""

# Step 1: Create main project directory structure
echo "📁 Creating directory structure..."

mkdir -p src
mkdir -p tests
mkdir -p benchmarks/samples
mkdir -p examples
mkdir -p diagrams
mkdir -p docs

echo "✅ Directories created"
echo ""

# Step 2: Initialize Python packages with __init__.py files
echo "📄 Creating Python package markers..."

cat > src/__init__.py << 'EOF'
"""
The Haiku Protocol
==================

Lossless semantic compression for AI context windows.

This package will contain the compression and decompression pipeline.
"""

__version__ = "0.1.0"
__author__ = "Haiku Protocol Team"
EOF

cat > tests/__init__.py << 'EOF'
"""
Test Suite for Haiku Protocol

Unit and integration tests for compression/decompression pipeline.
"""
EOF

echo "✅ Package markers created"
echo ""

# Step 3: Create empty marker files for configuration
echo "📄 Creating placeholder root files..."

touch benchmarks/samples/.gitkeep
touch examples/.gitkeep
touch diagrams/.gitkeep
touch docs/.gitkeep

echo "✅ Root files created"
echo ""

# Step 4: Display final structure
echo "✨ Scaffold complete!"
echo ""
echo "📊 Project structure:"
echo ""

if command -v tree &> /dev/null; then
    tree -L 2 -a
else
    echo "Note: 'tree' command not available. Using 'find' instead:"
    find . -maxdepth 2 -not -path '*/\.*' | sort
fi

echo ""
echo "✅ Next steps:"
echo "   1. Review structure with: tree -L 2"
echo "   2. Add configuration files (v0.1.3b)"
echo "   3. Add source module stubs (v0.1.3c)"
echo "   4. Initialize git repository (v0.1.3d)"
```

---

## Execution Workflow

### Step-by-Step Directory Creation

```
┌──────────────────────────────────────────────────────────────┐
│              DIRECTORY STRUCTURE CREATION FLOW               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  STEP 1: PREPARE SCRIPT                                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ $ chmod +x scaffold.sh                                 │ │
│  │ → Makes script executable                              │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                   │
│                          ▼                                   │
│  STEP 2: EXECUTE SCAFFOLD                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ $ ./scaffold.sh                                        │ │
│  │ → Creates src/, tests/, benchmarks/samples/, etc.     │ │
│  │ → Creates __init__.py files                           │ │
│  │ → Creates .gitkeep marker files                       │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                   │
│                          ▼                                   │
│  STEP 3: VERIFY STRUCTURE                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ $ tree -L 2                                            │ │
│  │ ✅ All directories present                             │ │
│  │ ✅ Python packages initialized                         │ │
│  │ ✅ Ready for next sub-part                             │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Decision Tree: Directory Verification

```
┌──────────────────────────────────────────────────┐
│  Verify Directory Structure                      │
├──────────────────────────────────────────────────┤
│                                                  │
│   Does src/ exist and is it writable?            │
│              │                                   │
│   ┌──────────┴──────────┐                       │
│   ▼ YES                 ▼ NO                     │
│                      [STOP - Create manually]    │
│                                                  │
│   Do all 6 directories exist?                    │
│   (tests, benchmarks, examples, diagrams, docs) │
│              │                                   │
│   ┌──────────┴──────────┐                       │
│   ▼ YES                 ▼ NO                     │
│                      [Re-run scaffold.sh]        │
│                                                  │
│   Are __init__.py files in src/ and tests/?     │
│              │                                   │
│   ┌──────────┴──────────┐                       │
│   ▼ YES                 ▼ NO                     │
│                      [Re-run scaffold.sh]        │
│                                                  │
│   ✅ STRUCTURE VERIFIED                          │
│   → Proceed to v0.1.3b                          │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## Verification Commands

### Manual Structure Verification Script

```bash
#!/bin/bash
# verify_structure.sh - Validate directory creation

echo "🔍 Verifying Haiku Protocol directory structure..."
echo ""

CHECKS=0
PASSED=0

# Check each required directory
for dir in src tests benchmarks examples diagrams docs; do
    CHECKS=$((CHECKS + 1))
    if [ -d "$dir" ]; then
        echo "✅ Directory: $dir/"
        PASSED=$((PASSED + 1))
    else
        echo "❌ Directory: $dir/ (MISSING)"
    fi
done

echo ""

# Check Python package markers
for init_file in src/__init__.py tests/__init__.py; do
    CHECKS=$((CHECKS + 1))
    if [ -f "$init_file" ]; then
        echo "✅ File: $init_file"
        PASSED=$((PASSED + 1))
    else
        echo "❌ File: $init_file (MISSING)"
    fi
done

echo ""

# Check benchmarks/samples subdirectory
CHECKS=$((CHECKS + 1))
if [ -d "benchmarks/samples" ]; then
    echo "✅ Subdirectory: benchmarks/samples/"
    PASSED=$((PASSED + 1))
else
    echo "❌ Subdirectory: benchmarks/samples/ (MISSING)"
fi

echo ""

# Check git not yet initialized (v0.1.3d concern)
CHECKS=$((CHECKS + 1))
if [ ! -d ".git" ]; then
    echo "✅ Git not yet initialized (expected at v0.1.3d)"
    PASSED=$((PASSED + 1))
else
    echo "⚠️  Git already initialized (expected at v0.1.3d)"
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "VERIFICATION RESULT: $PASSED/$CHECKS checks passed"
echo "═══════════════════════════════════════════════════"

if [ $PASSED -eq $CHECKS ]; then
    echo "✅ ALL CHECKS PASSED - Ready for v0.1.3b"
    exit 0
else
    echo "❌ SOME CHECKS FAILED - Review above and re-run scaffold.sh"
    exit 1
fi
```

### Expected tree -L 2 Output

```
haiku-protocol/
├── benchmarks
│   └── samples
├── diagrams
├── docs
├── examples
├── src
│   └── __init__.py
└── tests
    └── __init__.py

7 directories, 2 files
```

---

## Acceptance Criteria

- [ ] All 6 primary directories created: `src/`, `tests/`, `benchmarks/`, `examples/`, `diagrams/`, `docs/`
- [ ] Subdirectory `benchmarks/samples/` created for v0.0.3 baseline compatibility
- [ ] `src/__init__.py` file created with package docstring and metadata
- [ ] `tests/__init__.py` file created with package docstring
- [ ] `.gitkeep` files placed in empty directories to preserve git tracking
- [ ] `tree -L 2` command output matches expected structure (7 directories, 2 files minimum)
- [ ] Script executes without errors (`echo $?` returns 0)
- [ ] Structure is ready for v0.1.3b (no git initialization yet)

---

## Limitations & Constraints

1. **Platform Compatibility:** Script uses `mkdir -p` which is POSIX-compliant. Windows users should use WSL2 or manually create directories.

2. **Tree Command Dependency:** The `tree` command may not be installed on all systems. Script includes fallback using `find` command.

3. **No Nested Configuration:** Root-level configuration files (LICENSE, requirements.txt, .gitignore, .env.example) are NOT created in this sub-part; those are v0.1.3b responsibility.

4. **Placeholder Files Only:** This sub-part creates directory structure only. No source code stubs (encoder.py, decoder.py, etc.) are created here; those come in v0.1.3c.

5. **Git Not Initialized:** Repository initialization is deferred to v0.1.3d for clarity of separation of concerns.

6. **Python Version:** Script assumes Python 3.8+ for compatibility with async features in later phases. No version check included in this sub-part.

---

## Dependencies

**Must be completed before v0.1.3a:**
- v0.1.0 — Phase 1 Environment & Tech Stack (dev environment set up)

**External requirements:**
- Bash shell interpreter (version 4.0+)
- POSIX-compatible `mkdir`, `touch`, `chmod` commands
- Optional: `tree` command for pretty-printing (or `find` fallback)
- Write permissions in target directory
- Unix-like filesystem (Linux, macOS, WSL2 on Windows)

**No dependencies on:**
- v0.1.1 — Core Dependencies (yet; used in v0.1.3b)
- v0.1.2 — API Configuration (yet; used in v0.1.3b)
- Git (yet; used in v0.1.3d)

---

## Troubleshooting

### Issue: Permission Denied on scaffold.sh

**Symptom:** `./scaffold.sh: Permission denied`

**Solution:**
```bash
chmod +x scaffold.sh
./scaffold.sh
```

Alternatively, run with `bash`:
```bash
bash scaffold.sh
```

---

### Issue: Directory Already Exists

**Symptom:** `mkdir: cannot create directory 'src': File exists`

**Solution:** The `mkdir -p` flag is idempotent and won't fail if directories exist. If you see this error, check if something unexpected is in that location:
```bash
ls -la src/
# If contents are safe, continue
# If not, move or rename the conflicting directory
mv src src.backup
./scaffold.sh
```

---

### Issue: tree Command Not Found

**Symptom:** `tree: command not found` (but script shows fallback)

**Solution:** Install tree on your system:
- **macOS:** `brew install tree`
- **Ubuntu/Debian:** `sudo apt-get install tree`
- **Fedora/RHEL:** `sudo dnf install tree`
- **Alpine:** `apk add tree`

Or use the built-in fallback:
```bash
find . -maxdepth 2 -not -path '*/\.*' | sort
```

---

### Issue: __init__.py Files Not Created

**Symptom:** `src/__init__.py` not found after running scaffold.sh

**Solution:** Verify script has correct permissions and ran successfully:
```bash
bash scaffold.sh 2>&1 | tee scaffold.log
grep -E "✅|❌" scaffold.log
```

If __init__.py still missing, create manually:
```bash
touch src/__init__.py tests/__init__.py
cat > src/__init__.py << 'EOF'
"""The Haiku Protocol - Lossless semantic compression for AI context windows."""
__version__ = "0.1.0"
__author__ = "Haiku Protocol Team"
EOF
```

---

### Issue: benchmarks/samples Directory Not Created

**Symptom:** `benchmarks/samples/` doesn't exist after running scaffold.sh

**Solution:** This directory is critical for v0.0.3 compatibility. Create manually:
```bash
mkdir -p benchmarks/samples
touch benchmarks/samples/.gitkeep
```

---

## User Story

> As a project developer, I want to establish a clean, professional directory structure for the Haiku Protocol that follows Python package conventions, so that I can organize code, tests, benchmarks, and documentation in a way that enables smooth collaboration and deployment. The structure should reflect best practices from established Python projects and clearly separate concerns (source code, testing, documentation, benchmarking).

---

## Inputs from Previous Sub-Parts

**From v0.1.0 — Phase 1 Environment & Tech Stack:**
- Development environment is configured and ready
- Python 3.8+ is installed and accessible
- Bash shell is available
- Target project directory location is determined

**From parent v0.1.3 — Project Scaffolding:**
- Parent page defines the complete directory structure specification
- Parent page provides the scaffold.sh script (with minor enhancements in this sub-part)
- Parent page specifies all required directories: src/, tests/, benchmarks/, examples/, diagrams/, docs/
- Parent page mentions benchmarks/ subdirectories but doesn't specify benchmarks/samples/ detail

**New detail in v0.1.3a:**
- Explicit creation of `benchmarks/samples/` subdirectory for v0.0.3 baseline compatibility
- .gitkeep files for git tracking of empty directories

---

## Outputs to Next Sub-Part

**For v0.1.3b — Root Configuration Files:**
- All 7 directories are now present and writable
- `src/` directory exists with `__init__.py` (can be updated with metadata in v0.1.3b context)
- `tests/` directory exists with `__init__.py`
- File system is clean and organized, ready for LICENSE, requirements.txt, .gitignore, .env.example files
- Directory structure matches parent v0.1.3 specification exactly

**For v0.1.3c — Source Module Stubs:**
- `src/` directory is ready for Python module files (encoder.py, decoder.py, etc.)
- `src/__init__.py` exists and can be updated with version and author metadata
- Directory structure supports proper Python package imports

**For v0.1.3d — Git Initialization & Verification:**
- Complete directory structure is in place before git initialization
- All directories and placeholder files exist for first commit
- `.gitkeep` files ensure empty directories are preserved in git

---

## Decision Log

| Decision | Rationale | Status |
|----------|-----------|--------|
| Use `mkdir -p` for idempotent directory creation | Allows script to be run multiple times safely without error | ✅ Approved |
| Create `benchmarks/samples/` as subdirectory | v0.0.3 baseline metrics need consistent location separate from v0.1.x benchmarks | ✅ Approved |
| Use `.gitkeep` instead of `.gitignore` in empty dirs | `.gitkeep` preserves empty directory structure in git without hiding files | ✅ Approved |
| Initialize `src/__init__.py` with docstring | Establishes package identity early; can be enhanced in v0.1.3b | ✅ Approved |
| Defer git initialization to v0.1.3d | Clear separation of concerns: structure first, git second | ✅ Approved |
| Include fallback for `tree` command | Ensures cross-platform compatibility if tree not installed | ✅ Approved |
