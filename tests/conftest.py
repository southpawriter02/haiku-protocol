"""Shared test fixtures for Haiku Protocol test suite."""

import sys
from pathlib import Path

import pytest

# Ensure the project root is importable
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Also ensure research/ is directly importable (for parser, extractor, etc.)
research_dir = project_root / "research"
if str(research_dir) not in sys.path:
    sys.path.insert(0, str(research_dir))


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


# ── v0.0.2c: HaikuParser Fixtures ──


@pytest.fixture
def parser():
    """Fresh HaikuParser instance for each test."""
    from haiku_parser import HaikuParser
    return HaikuParser()


@pytest.fixture(scope="session")
def valid_haiku_cases():
    """10 valid haiku strings from the v0.0.2c specification.

    Each tuple is (description, haiku_string, expected_min_statements).
    """
    return [
        ("Simple action",
         "Action:Restart_Service", 1),
        ("Action with REQUIRES",
         "Action:Deploy REQUIRES State:Config_Valid", 1),
        ("Action with EXEC",
         "Action:Backup -> EXEC:backup.sh", 1),
        ("Sequential actions",
         "Action:Prepare; Action:Deploy; Action:Verify", 3),
        ("Conditional branching",
         "IF:Success THEN:Action:Continue ELSE:Action:Rollback", 3),
        ("Verification",
         "Action:Deploy -> EXEC:deploy.sh; VERIFY:Service_Running", 2),
        ("Warning",
         "Action:Delete WARN:No_Recovery -> Data_Loss", 1),
        ("Metadata + action",
         "META:version=1.0; Action:Execute -> EXEC:script.sh", 1),
        ("Loop with action",
         "LOOP:3:Action:Retry -> EXEC:attempt.sh", 2),
        ("Complex composition",
         "META:author=DevOps; Action:Backup REQUIRES State:Online -> EXEC:backup.sh; "
         "IF:Success THEN:Action:Verify ELSE:Action:Alert; VERIFY:Backup_Exists", 5),
    ]


@pytest.fixture(scope="session")
def invalid_haiku_cases():
    """5 invalid haiku strings from the v0.0.2c specification.

    Each tuple is (description, haiku_string, expected_error_substring).
    """
    return [
        ("Missing identifier",
         "Action:", "Unexpected"),
        ("REQUIRES without Action",
         "REQUIRES State:Online", "REQUIRES without preceding Action"),
        ("THEN without IF",
         "Action:Deploy THEN Action:Verify", "Unexpected"),
        ("WARN without Action context",
         "WARN:Unknown_Identifier -> Consequence", "No valid statements"),
        ("Unbalanced brackets",
         "Action:Deploy [broken_bracket", "Unexpected"),
    ]


# ── v0.0.2d: HaikuValidator Fixtures ──


@pytest.fixture
def validator():
    """Fresh HaikuValidator instance for a simple valid haiku."""
    from haiku_validator import HaikuValidator
    return HaikuValidator("Action:Deploy REQUIRES State:Online")


@pytest.fixture(scope="session")
def valid_validation_cases():
    """Haiku strings that should pass full validation (v0.0.2d).

    Each tuple is (description, haiku_string).
    """
    return [
        ("Simple action", "Action:Deploy"),
        ("Action with REQUIRES", "Action:Deploy REQUIRES State:Online"),
        ("Sequential actions", "Action:Prepare; Action:Deploy; Action:Verify"),
        ("Conditional", "IF:Success THEN:Action:Continue ELSE:Action:Rollback"),
        ("Loop", "LOOP:3:Action:Retry -> EXEC:attempt.sh"),
        ("Metadata + action", "META:version=1.0; Action:Execute -> EXEC:script.sh"),
        ("Action with VERIFY", "Action:Deploy; VERIFY:Service_Running"),
        ("REF statement", "Action:Deploy; REF:Runbook_Deploy:Recovery"),
    ]


@pytest.fixture(scope="session")
def invalid_validation_cases():
    """Haiku strings that should fail validation (v0.0.2d).

    Each tuple is (description, haiku_string, expected_error_code).
    """
    return [
        ("Syntax error", "Action:Deploy [broken", "VAL-001"),
        ("Self-referential", "Action:Deploy REQUIRES State:Deploy", "VAL-004"),
        ("Empty input", "", "VAL-001"),
    ]
