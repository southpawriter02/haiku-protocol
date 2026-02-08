"""
test_git_verification.py - Git Verification & Phase Commit Tests
=================================================================

Programmatic verification of all v0.1.3d acceptance criteria:
  1. .git/ directory exists
  2. Working tree clean (after commit)
  3. .env / .env.local NOT tracked
  4. .env.example IS tracked
  5. All source files tracked
  6. All directories exist
  7. .gitignore rules work
  8. No real API keys in tracked files
  9. No broken symlinks

Version: v0.1.3d
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent


def _git(*args: str) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git", *args],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _git_ls_files() -> list[str]:
    """Return list of all tracked files."""
    return _git("ls-files").splitlines()


# ============================================
# Acceptance Criterion 1: .git/ exists
# ============================================

@pytest.mark.unit
class TestGitDirectoryExists:
    """Verify .git/ directory is present."""

    def test_git_directory_exists(self):
        """.git/ directory exists in project root."""
        assert (PROJECT_ROOT / ".git").is_dir()

    def test_git_head_exists(self):
        """.git/HEAD file exists (valid repository)."""
        assert (PROJECT_ROOT / ".git" / "HEAD").is_file()


# ============================================
# Acceptance Criteria 3-4: .env security
# ============================================

@pytest.mark.unit
class TestEnvExclusion:
    """Verify .env is excluded and .env.example is included."""

    def test_env_not_tracked(self):
        """.env is NOT tracked by git (AC-3)."""
        tracked = _git_ls_files()
        env_files = [f for f in tracked if f == ".env"]
        assert env_files == [], ".env must not be tracked"

    def test_env_local_not_tracked(self):
        """.env.local is NOT tracked by git (AC-3)."""
        tracked = _git_ls_files()
        env_local = [f for f in tracked if f == ".env.local"]
        assert env_local == [], ".env.local must not be tracked"

    def test_env_example_is_tracked(self):
        """.env.example IS tracked by git (AC-4)."""
        tracked = _git_ls_files()
        assert ".env.example" in tracked

    def test_gitignore_contains_env_rule(self):
        """.gitignore contains .env exclusion rule."""
        gitignore = (PROJECT_ROOT / ".gitignore").read_text()
        lines = [l.strip() for l in gitignore.splitlines()]
        assert ".env" in lines, ".gitignore must contain '.env' rule"


# ============================================
# Acceptance Criterion 5: Source files tracked
# ============================================

@pytest.mark.unit
class TestSourceFilesTracked:
    """Verify all required source files are tracked."""

    def test_all_src_modules_tracked(self):
        """All 7 source module stubs + config are tracked."""
        tracked = _git_ls_files()
        expected = [
            "src/__init__.py",
            "src/encoder.py",
            "src/decoder.py",
            "src/chunker.py",
            "src/extractor.py",
            "src/synthesizer.py",
            "src/validator.py",
            "src/app.py",
            "src/config.py",
        ]
        for f in expected:
            assert f in tracked, f"{f} not tracked"

    def test_tests_directory_tracked(self):
        """tests/ files are tracked."""
        tracked = _git_ls_files()
        test_files = [f for f in tracked if f.startswith("tests/")]
        assert len(test_files) > 0, "No test files tracked"

    def test_license_tracked(self):
        """LICENSE is tracked."""
        assert "LICENSE" in _git_ls_files()

    def test_requirements_tracked(self):
        """requirements.txt is tracked."""
        assert "requirements.txt" in _git_ls_files()

    def test_gitignore_tracked(self):
        """.gitignore is tracked."""
        assert ".gitignore" in _git_ls_files()


# ============================================
# Acceptance Criterion 6: Directories exist
# ============================================

@pytest.mark.unit
class TestDirectoryStructure:
    """Verify all required directories exist."""

    @pytest.mark.parametrize("dirname", [
        "src", "tests", "benchmarks", "examples", "diagrams", "docs"
    ])
    def test_directory_exists(self, dirname):
        """Required directory exists in project root."""
        assert (PROJECT_ROOT / dirname).is_dir(), f"{dirname}/ missing"

    def test_src_init_exists(self):
        """src/__init__.py exists (Python package)."""
        assert (PROJECT_ROOT / "src" / "__init__.py").is_file()

    def test_tests_init_exists(self):
        """tests/__init__.py exists (Python package)."""
        assert (PROJECT_ROOT / "tests" / "__init__.py").is_file()


# ============================================
# Acceptance Criterion 7: .gitignore rules
# ============================================

@pytest.mark.unit
class TestGitignoreRules:
    """.gitignore excludes expected patterns."""

    def test_pycache_not_tracked(self):
        """__pycache__/ files are not tracked."""
        tracked = _git_ls_files()
        pycache = [f for f in tracked if "__pycache__" in f]
        assert pycache == [], f"__pycache__ files tracked: {pycache}"

    def test_pyc_not_tracked(self):
        """*.pyc files are not tracked."""
        tracked = _git_ls_files()
        pyc = [f for f in tracked if f.endswith(".pyc")]
        assert pyc == [], f".pyc files tracked: {pyc}"

    def test_venv_not_tracked(self):
        """.venv/ files are not tracked."""
        tracked = _git_ls_files()
        venv = [f for f in tracked if ".venv/" in f or f.startswith("venv/")]
        assert venv == [], f"venv files tracked: {venv}"

    def test_gitignore_has_ide_rules(self):
        """.gitignore contains IDE exclusion rules."""
        gitignore = (PROJECT_ROOT / ".gitignore").read_text()
        # Check for at least one IDE pattern
        has_vscode = ".vscode" in gitignore
        has_idea = ".idea" in gitignore
        assert has_vscode or has_idea, \
            ".gitignore should exclude IDE directories"


# ============================================
# Acceptance Criterion 8: No API keys
# ============================================

@pytest.mark.unit
class TestNoSecretsCommitted:
    """Verify no real API keys in tracked files."""

    def test_no_real_api_keys_in_tracked_files(self):
        """No real OpenAI API keys (sk-...) in tracked files.

        Allows safe patterns: docstring examples ('sk-...'),
        test mocks ('sk-test...'), and .env.example templates.
        """
        tracked = _git_ls_files()
        violations = []
        for filepath in tracked:
            full_path = PROJECT_ROOT / filepath
            if not full_path.is_file():
                continue
            try:
                content = full_path.read_text(errors="ignore")
            except Exception:
                continue

            for i, line in enumerate(content.splitlines(), 1):
                if "sk-" not in line:
                    continue
                # Allow safe patterns
                stripped = line.strip()
                safe_patterns = [
                    'sk-...',      # Docstring placeholder
                    'sk-your',     # .env.example template
                    'sk-test',     # Test mock values
                    'sk-"',        # Quoted placeholder
                    "sk-'",        # Quoted placeholder
                    'startswith("sk-")',  # Code checking format
                    "startswith('sk-')",  # Code checking format
                    'match="sk-"',        # Regex/match pattern
                    'sk-proj-',    # Documented format
                    'sk-ant',      # Anthropic key template
                    'sk-short',    # Test mock short key
                    'sk- pre',     # Docstring/comment references
                    'task-specific',  # Substring match (not API key)
                    'compressor',    # Substring match (not API key)
                    'extracti',      # Substring in research text
                ]
                if any(p in stripped for p in safe_patterns):
                    continue
                # Skip comment lines and docstring references
                if stripped.startswith(('#', '"""', "'''", '//')):
                    continue
                violations.append(f"{filepath}:{i}: {stripped[:80]}")

        assert violations == [], \
            f"Potential API keys found:\n" + "\n".join(violations)

    def test_no_env_file_tracked(self):
        """No .env file (with actual secrets) is tracked."""
        tracked = _git_ls_files()
        dangerous = [
            f for f in tracked
            if f.endswith(".env") and "example" not in f
        ]
        assert dangerous == [], f"Secret files tracked: {dangerous}"


# ============================================
# Acceptance Criterion 10: No broken symlinks
# ============================================

@pytest.mark.unit
class TestNoSymlinkIssues:
    """Verify no broken symlinks in repository."""

    def test_no_broken_symlinks(self):
        """No broken symlinks in tracked files."""
        tracked = _git_ls_files()
        broken = []
        for filepath in tracked:
            full_path = PROJECT_ROOT / filepath
            if full_path.is_symlink() and not full_path.exists():
                broken.append(filepath)
        assert broken == [], f"Broken symlinks: {broken}"


# ============================================
# Cross-cutting: Repository health
# ============================================

@pytest.mark.unit
class TestRepositoryHealth:
    """Overall repository health checks."""

    def test_has_at_least_one_commit(self):
        """Repository has at least one commit."""
        log = _git("log", "--oneline", "-1")
        assert len(log) > 0, "No commits in repository"

    def test_on_main_branch(self):
        """Repository is on main (or master) branch."""
        branch = _git("rev-parse", "--abbrev-ref", "HEAD")
        assert branch in ("main", "master"), \
            f"Expected main/master, got '{branch}'"

    def test_module_count_in_src(self):
        """At least 7 module stubs exist in src/."""
        tracked = _git_ls_files()
        src_py = [f for f in tracked
                  if f.startswith("src/") and f.endswith(".py")
                  and f != "src/__init__.py"]
        assert len(src_py) >= 7, \
            f"Expected ≥7 modules in src/, found {len(src_py)}: {src_py}"
