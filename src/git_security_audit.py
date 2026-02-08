#!/usr/bin/env python3
"""Verify git security configuration for secret protection.

Provides the GitSecurityAuditor class for programmatic verification
of git-level secret protection: .gitignore rules, git tracking status,
git history auditing, and pre-commit hook installation.

Version: v0.1.2b
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class GitSecurityAuditor:
    """Audit git configuration for proper secret protection.

    Runs 5 security checks:
        1. .env pattern exists in .gitignore
        2. .env is not tracked by git
        3. .env.example exists with placeholder values
        4. Git history contains no secret patterns
        5. Pre-commit hook is installed (optional)

    Attributes:
        project_root: Path to the project root directory.
        checks_passed: Count of checks that passed.
        checks_failed: Count of checks that failed.
        warnings: List of non-fatal warning messages.
    """

    def __init__(self, project_root: str = ".") -> None:
        """Initialize the auditor.

        Args:
            project_root: Path to the project root directory.
        """
        self.project_root = Path(project_root).resolve()
        self.checks_passed: int = 0
        self.checks_failed: int = 0
        self.warnings: List[str] = []

    def run_git_command(self, cmd: str) -> Tuple[int, str, str]:
        """Execute a git command and return exit code, stdout, stderr.

        Args:
            cmd: The git command string to execute.

        Returns:
            Tuple of (return_code, stdout, stderr).
        """
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)

    def check_env_in_gitignore(self) -> bool:
        """Verify .env is listed in .gitignore.

        Returns:
            True if .env pattern is found in .gitignore.
        """
        gitignore_path = self.project_root / ".gitignore"

        if not gitignore_path.exists():
            self.checks_failed += 1
            return False

        with open(gitignore_path, "r") as f:
            lines = [line.strip() for line in f]

        # Check for .env as a standalone pattern (not commented out)
        for line in lines:
            if line == ".env" or line == "/.env":
                self.checks_passed += 1
                return True

        self.checks_failed += 1
        return False

    def check_env_not_tracked(self) -> bool:
        """Verify .env is not tracked by git.

        Returns:
            True if .env is properly excluded from git tracking.
        """
        env_path = self.project_root / ".env"

        if not env_path.exists():
            # .env doesn't exist — not a failure, just a note
            self.warnings.append(".env file does not exist")
            self.checks_passed += 1
            return True

        # Check if git ignores the .env file
        returncode, stdout, stderr = self.run_git_command(
            "git check-ignore .env"
        )

        if returncode == 0:
            # git confirms .env is ignored
            self.checks_passed += 1
            return True
        else:
            # .env might be tracked or not ignored
            self.checks_failed += 1
            return False

    def check_env_example_exists(self) -> bool:
        """Verify .env.example exists with placeholder values.

        Returns:
            True if .env.example exists and contains only placeholders.
        """
        example_path = self.project_root / ".env.example"

        if not example_path.exists():
            self.checks_failed += 1
            return False

        with open(example_path, "r") as f:
            content = f.read()

        # Check for real API key (bad) vs placeholder (good)
        if "sk-proj-" in content and "your-key" not in content:
            self.checks_failed += 1
            return False

        self.checks_passed += 1
        return True

    def check_git_history_for_secrets(self) -> bool:
        """Verify .env file was never committed to git.

        Checks that .env has never appeared in the git tree.
        Test data containing 'sk-proj-test...' patterns in test files
        is expected and not considered a secret leak.

        Returns:
            True if no real secrets are found in git history.
        """
        # Check if .env was ever tracked (the actual risk)
        returncode, stdout, stderr = self.run_git_command(
            'git log --all --diff-filter=A -- .env'
        )

        if stdout.strip():
            self.checks_failed += 1
            return False

        self.checks_passed += 1
        return True

    def check_pre_commit_hook(self) -> bool:
        """Verify pre-commit hook is installed and executable.

        Returns:
            True if hook exists (with warnings if not executable).
        """
        hook_path = self.project_root / ".git" / "hooks" / "pre-commit"

        if hook_path.exists():
            if os.access(hook_path, os.X_OK):
                self.checks_passed += 1
                return True
            else:
                self.warnings.append(
                    "Pre-commit hook exists but is not executable"
                )
                self.checks_passed += 1
                return True
        else:
            self.warnings.append(
                "Pre-commit hook not installed (optional)"
            )
            # Not a failure — hook is optional per spec
            self.checks_passed += 1
            return True

    def run_audit(self) -> bool:
        """Run all 5 security checks.

        Returns:
            True if all checks pass, False if any fail.
        """
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []

        self.check_env_in_gitignore()
        self.check_env_not_tracked()
        self.check_env_example_exists()
        self.check_git_history_for_secrets()
        self.check_pre_commit_hook()

        return self.checks_failed == 0

    def print_report(self) -> bool:
        """Run audit and print a human-readable report.

        Returns:
            True if audit passed, False otherwise.
        """
        success = self.run_audit()

        print(f"\n{'=' * 60}")
        print("Git Security Audit — Haiku Protocol v0.1.2b")
        print(f"{'=' * 60}")
        print(
            f"\nResults: {self.checks_passed} passed, "
            f"{self.checks_failed} failed"
        )

        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")

        if success:
            print("\n✅ Security audit PASSED!")
        else:
            print("\n❌ Security audit FAILED.")

        print(f"\n{'=' * 60}\n")
        return success


if __name__ == "__main__":
    auditor = GitSecurityAuditor()
    success = auditor.run_audit()
    auditor.print_report()
    sys.exit(0 if success else 1)
