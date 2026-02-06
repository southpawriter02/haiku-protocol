"""Shared test fixtures for Haiku Protocol test suite."""

import sys
from pathlib import Path

import pytest

# Ensure the project root is importable
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def corpus_dir():
    """Path to the corpus directory with procedural document samples."""
    return str(project_root / "research" / "corpus")


@pytest.fixture(scope="session")
def sample_action_text():
    """Text containing clear Action pattern markers."""
    return "Build the Docker image. Deploy to production. Run the tests."


@pytest.fixture(scope="session")
def sample_warning_text():
    """Text containing clear Warning pattern markers."""
    return "WARNING: This will delete all data. Do not proceed without backup."


@pytest.fixture(scope="session")
def sample_conditional_text():
    """Text containing clear Condition pattern markers."""
    return "If the build fails, check the logs. Otherwise, deploy to staging."


@pytest.fixture(scope="session")
def sample_mixed_text():
    """Text containing multiple overlapping pattern markers."""
    return (
        "WARNING: This procedure requires maintenance window.\n"
        "First back up the database. Then stop application processes.\n"
        "Run migration script version 2.1.0.\n"
        "If migration fails, restore from backup.\n"
        "Verify schema integrity using validation script.\n"
        "See Rollback Procedure for error recovery.\n"
        "Prerequisites: Python 3.9 and backup completed."
    )
