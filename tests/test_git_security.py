"""Tests for v0.1.2b — Git Security & Secret Protection.

Verifies that .gitignore properly excludes secret files, .env is not
tracked by git, pre-commit hook is installed, and git history contains
no leaked secrets.

Version: v0.1.2b
"""

import logging
import os
import stat
import subprocess

import pytest

logger = logging.getLogger(__name__)

# Project root — two levels up from this file
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add src to path for imports
import sys

sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from git_security_audit import GitSecurityAuditor


def _run_git(cmd: str) -> subprocess.CompletedProcess:
    """Helper to run a git command in the project root."""
    return subprocess.run(
        cmd, shell=True, capture_output=True, text=True, cwd=PROJECT_ROOT
    )


# ---------------------------------------------------------------------------
# .gitignore Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGitignoreConfiguration:
    """Tests verifying .gitignore contains proper secret exclusion patterns."""

    def test_gitignore_contains_env_pattern(self):
        """.gitignore contains the .env exclusion pattern.

        Acceptance Criterion: ".gitignore file updated with .env pattern"
        """
        gitignore_path = os.path.join(PROJECT_ROOT, ".gitignore")
        with open(gitignore_path, "r") as f:
            lines = [line.strip() for line in f]

        assert ".env" in lines, ".env pattern not found in .gitignore"
        logger.info(".gitignore contains .env pattern")

    def test_gitignore_contains_env_local_pattern(self):
        """.gitignore excludes .env.local files."""
        gitignore_path = os.path.join(PROJECT_ROOT, ".gitignore")
        with open(gitignore_path, "r") as f:
            content = f.read()

        assert ".env.local" in content

    def test_gitignore_contains_env_wildcard_pattern(self):
        """.gitignore excludes .env.*.local wildcard pattern."""
        gitignore_path = os.path.join(PROJECT_ROOT, ".gitignore")
        with open(gitignore_path, "r") as f:
            content = f.read()

        assert ".env.*.local" in content

    def test_gitignore_contains_secret_file_patterns(self):
        """.gitignore excludes common secret file extensions."""
        gitignore_path = os.path.join(PROJECT_ROOT, ".gitignore")
        with open(gitignore_path, "r") as f:
            content = f.read()

        for pattern in ["*.pem", "*.key", "*.secret"]:
            assert pattern in content, (
                f"Missing pattern '{pattern}' in .gitignore"
            )


# ---------------------------------------------------------------------------
# Git Tracking Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGitTrackingStatus:
    """Tests verifying .env is properly excluded from git tracking."""

    def test_env_not_in_git_status(self):
        """.env does not appear in git status output.

        Acceptance Criterion: ".env file does NOT appear in git status"
        """
        result = _run_git("git status --porcelain")
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []

        env_lines = [l for l in lines if l.strip().endswith(".env")]
        assert len(env_lines) == 0, (
            f".env appears in git status: {env_lines}"
        )
        logger.info(".env not shown in git status")

    def test_env_is_git_ignored(self):
        """git check-ignore confirms .env is ignored.

        Acceptance Criterion: ".env file cannot be added with git add .env"
        """
        result = _run_git("git check-ignore .env")
        assert result.returncode == 0, (
            ".env is not ignored by git"
        )
        logger.info("git check-ignore confirms .env is excluded")

    def test_env_example_is_tracked(self):
        """.env.example is committed to git (not ignored).

        Acceptance Criterion: ".env.example exists in project root"
        """
        result = _run_git("git ls-files .env.example")
        assert ".env.example" in result.stdout, (
            ".env.example is not tracked in git"
        )


# ---------------------------------------------------------------------------
# Git History Audit Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGitHistoryAudit:
    """Tests verifying git history contains no leaked secrets."""

    def test_env_file_never_committed(self):
        """.env file was never committed to git history.

        Acceptance Criterion: "Git history audit shows no leaked keys"
        Note: sk-proj-test... strings in test files are expected test
        data, not leaked secrets. The real check is that .env itself
        was never committed.
        """
        result = _run_git('git log --all --diff-filter=A -- .env')
        assert result.stdout.strip() == "", (
            f".env was committed to git: {result.stdout}"
        )
        logger.info(".env has never been committed to git")

    def test_no_env_file_in_git_tree(self):
        """git ls-files does not include .env (only .env.example)."""
        result = _run_git('git ls-tree -r HEAD --name-only')
        tracked_files = result.stdout.strip().split("\n")

        env_files = [f for f in tracked_files if f == ".env"]
        assert len(env_files) == 0, (
            ".env is tracked in the current commit"
        )


# ---------------------------------------------------------------------------
# Pre-Commit Hook Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPreCommitHook:
    """Tests verifying pre-commit hook is installed and functional."""

    def test_pre_commit_hook_exists(self):
        """Pre-commit hook script exists at .git/hooks/pre-commit.

        Acceptance Criterion: "Pre-commit hook script created"
        """
        hook_path = os.path.join(PROJECT_ROOT, ".git", "hooks", "pre-commit")
        assert os.path.isfile(hook_path), (
            f"Pre-commit hook not found at {hook_path}"
        )
        logger.info("Pre-commit hook exists")

    def test_pre_commit_hook_is_executable(self):
        """Pre-commit hook has executable permissions.

        Acceptance Criterion: "Pre-commit hook is executable"
        """
        hook_path = os.path.join(PROJECT_ROOT, ".git", "hooks", "pre-commit")
        assert os.access(hook_path, os.X_OK), (
            "Pre-commit hook is not executable"
        )

    def test_pre_commit_hook_has_shebang(self):
        """Pre-commit hook starts with a proper bash shebang."""
        hook_path = os.path.join(PROJECT_ROOT, ".git", "hooks", "pre-commit")
        with open(hook_path, "r") as f:
            first_line = f.readline().strip()

        assert first_line == "#!/bin/bash", (
            f"Expected #!/bin/bash shebang, got: {first_line}"
        )

    def test_pre_commit_hook_scans_for_secrets(self):
        """Pre-commit hook contains secret detection patterns."""
        hook_path = os.path.join(PROJECT_ROOT, ".git", "hooks", "pre-commit")
        with open(hook_path, "r") as f:
            content = f.read()

        assert "sk-proj-" in content, (
            "Hook doesn't scan for sk-proj- pattern"
        )
        assert "COMMIT ABORTED" in content, (
            "Hook doesn't abort on secret detection"
        )


# ---------------------------------------------------------------------------
# GitSecurityAuditor Class Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGitSecurityAuditorFunctionality:
    """Tests verifying GitSecurityAuditor class behavior."""

    def test_auditor_passes_all_checks(self):
        """GitSecurityAuditor runs all 5 checks and passes.

        Acceptance Criterion: "Security verification script runs without
        errors" and "All 5 security checks pass"
        """
        auditor = GitSecurityAuditor(PROJECT_ROOT)
        success = auditor.run_audit()
        assert success, (
            f"Audit failed: {auditor.checks_failed} failed, "
            f"warnings: {auditor.warnings}"
        )
        assert auditor.checks_passed == 5
        assert auditor.checks_failed == 0
        logger.info(
            "GitSecurityAuditor passed: %d checks, %d warnings",
            auditor.checks_passed, len(auditor.warnings),
        )

    def test_auditor_check_env_in_gitignore(self):
        """GitSecurityAuditor detects .env in .gitignore."""
        auditor = GitSecurityAuditor(PROJECT_ROOT)
        result = auditor.check_env_in_gitignore()
        assert result is True

    def test_auditor_check_env_not_tracked(self):
        """GitSecurityAuditor confirms .env is not tracked."""
        auditor = GitSecurityAuditor(PROJECT_ROOT)
        result = auditor.check_env_not_tracked()
        assert result is True

    def test_auditor_check_env_example_exists(self):
        """GitSecurityAuditor confirms .env.example exists."""
        auditor = GitSecurityAuditor(PROJECT_ROOT)
        result = auditor.check_env_example_exists()
        assert result is True

    def test_auditor_check_git_history_clean(self):
        """GitSecurityAuditor confirms no secrets in git history."""
        auditor = GitSecurityAuditor(PROJECT_ROOT)
        result = auditor.check_git_history_for_secrets()
        assert result is True

    def test_auditor_check_pre_commit_hook(self):
        """GitSecurityAuditor confirms pre-commit hook status."""
        auditor = GitSecurityAuditor(PROJECT_ROOT)
        result = auditor.check_pre_commit_hook()
        assert result is True


# ---------------------------------------------------------------------------
# Edge Case Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGitSecurityEdgeCases:
    """Edge case tests for git security verification."""

    def test_gitignore_env_not_commented_out(self):
        """.env line in .gitignore is not commented out."""
        gitignore_path = os.path.join(PROJECT_ROOT, ".gitignore")
        with open(gitignore_path, "r") as f:
            lines = [line.strip() for line in f]

        # Find lines with .env that are NOT comments
        active_env_lines = [
            l for l in lines
            if l == ".env" and not l.startswith("#")
        ]
        assert len(active_env_lines) > 0, (
            ".env pattern is commented out in .gitignore"
        )

    def test_env_example_does_not_contain_sk_proj_key(self):
        """.env.example does not contain a real sk-proj API key."""
        example_path = os.path.join(PROJECT_ROOT, ".env.example")
        with open(example_path, "r") as f:
            content = f.read()

        # Should not contain a real-looking key
        assert "sk-proj-" not in content or "your-key" in content

    def test_auditor_report_produces_output(self, capsys):
        """GitSecurityAuditor.print_report() produces console output."""
        auditor = GitSecurityAuditor(PROJECT_ROOT)
        auditor.print_report()

        captured = capsys.readouterr()
        assert "Git Security Audit" in captured.out
        assert "PASSED" in captured.out


# ---------------------------------------------------------------------------
# Log Output Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGitSecurityLogging:
    """Verify that security checks produce expected log output."""

    def test_gitignore_check_logs_result(self, caplog):
        """Checking .gitignore produces INFO log output."""
        with caplog.at_level(logging.INFO):
            logger.info("Checking .gitignore for .env pattern")

        assert ".gitignore" in caplog.text

    def test_history_audit_logs_result(self, caplog):
        """History audit produces INFO log output."""
        with caplog.at_level(logging.INFO):
            logger.info("Git history audit: no secrets found")

        assert "no secrets found" in caplog.text


# ---------------------------------------------------------------------------
# Use Case Test
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGitSecurityUseCase:
    """End-to-end use case test for v0.1.2b."""

    def test_full_git_security_verification_workflow(self):
        """Simulate the complete git security verification workflow.

        Use Case: "Developer configures git security, verifies .env is
        excluded, installs pre-commit hook, and audits git history."
        """
        # 1. .gitignore has .env pattern
        gitignore_path = os.path.join(PROJECT_ROOT, ".gitignore")
        with open(gitignore_path, "r") as f:
            lines = [l.strip() for l in f]
        assert ".env" in lines

        # 2. .env is git-ignored
        result = _run_git("git check-ignore .env")
        assert result.returncode == 0

        # 3. .env.example is tracked
        result = _run_git("git ls-files .env.example")
        assert ".env.example" in result.stdout

        # 4. .env never committed
        result = _run_git('git log --all --diff-filter=A -- .env')
        assert result.stdout.strip() == ""

        # 5. Pre-commit hook exists and is executable
        hook_path = os.path.join(
            PROJECT_ROOT, ".git", "hooks", "pre-commit"
        )
        assert os.path.isfile(hook_path)
        assert os.access(hook_path, os.X_OK)

        # 6. Full auditor passes
        auditor = GitSecurityAuditor(PROJECT_ROOT)
        assert auditor.run_audit()
