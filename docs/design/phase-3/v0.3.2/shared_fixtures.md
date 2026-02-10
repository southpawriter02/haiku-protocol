# v0.3.2a — Shared Test Fixtures (conftest.py)

<aside>

**Version:** v0.3.2a

**Parent:** v0.3.2 — Test Suite Implementation

**Status:** ⬜ Not Started

**Duration:** 10–15 minutes

**Deliverable:** Updated `tests/conftest.py` with 4 shared fixtures for hypothesis validation tests

</aside>

---

## Objective

Update the project's shared test fixtures in `tests/conftest.py` to provide standardized test data for all hypothesis validation tests. Instead of embedding sample documents in individual test methods, fixtures consolidate test data into reusable, maintainable definitions. This sub-part defines four fixtures: three document samples (simple, medium, complex) of increasing complexity, and a pre-built entity dictionary matching the project's canonical "restart server" example.

---

## User Stories

> As a test author writing hypothesis validation tests, I want shared fixtures so that I can use the same sample data across multiple test classes without duplicating test data in each test method.

> As a test suite maintainer, I want all fixture data defined in one place (conftest.py) so that I can update shared test data in a single location instead of searching through multiple test files.

---

## Implementation Design

### Fixture Overview

Four fixtures will be added to `tests/conftest.py`. These are **shared** fixtures, meaning they are available globally to all test files in the `tests/` directory and will not override or replace Phase 2 module-specific fixtures.

### Fixture 1: `sample_simple_doc`

**Type:** `pytest.fixture()`
**Returns:** `str` (Markdown text)
**Purpose:** A one-sentence procedure for testing basic compression and token counting

```python
@pytest.fixture
def sample_simple_doc():
    """A simple one-sentence procedure for basic compression testing.

    This fixture provides a minimal valid input to the encoder—a single,
    complete procedure statement. Used by TestCompressionMetrics and as a
    fallback for any test needing trivial input.

    Returns:
        str: One-sentence procedure.
    """
    return "To restart the server, save the config and run the restart command."
```

**Expected Usage:**
- `TestCompressionMetrics.test_simple_compression()` — verifies that encoding produces valid output and that compression_ratio exists
- Token count: ~16 original tokens (GPT-4 encoding), expected compression to ~8–10 tokens

---

### Fixture 2: `sample_medium_doc`

**Type:** `pytest.fixture()`
**Returns:** `str` (Markdown text)
**Purpose:** A multi-step procedure with warnings for testing prerequisite and context preservation

```python
@pytest.fixture
def sample_medium_doc():
    """A multi-step deployment procedure with warnings.

    This fixture contains a structured procedure with multiple steps, explicit
    prerequisites, and a safety warning. Used by TestPrerequisiteHypothesis
    and TestContextOverflowHypothesis to validate that dependency information
    and warnings survive compression.

    Returns:
        str: Multi-step procedure with warnings.
    """
    return """# Deploy Application

## Prerequisites

- Build system must be installed
- Tests must pass before deployment
- Database must be backed up

## Procedure

1. **Build:** Run `npm run build` to compile the application.
2. **Deploy:** Execute `npm run deploy` to push the build to production.
3. **Verify:** Run `npm run test:prod` to confirm the deployment succeeded.

## Warnings

- **Warning:** Skipping tests may cause production outages. Always run the full test suite before deployment.
- **Note:** This procedure requires administrative access to the deployment system."""
```

**Expected Usage:**
- `TestPrerequisiteHypothesis.test_dependency_extraction()` — verifies REQUIRES or State: operator presence
- `TestPrerequisiteHypothesis.test_action_state_linking()` — uses `sample_entities` to validate REQUIRES syntax
- `TestContextOverflowHypothesis.test_compression_ratio()` — expects ~40% compression ratio
- `TestSemanticFidelityHypothesis.test_warning_preservation()` — verifies WARN: operator presence
- Token count: ~120 original tokens, expected compression to ~50–70 tokens

---

### Fixture 3: `sample_complex_doc`

**Type:** `pytest.fixture()`
**Returns:** `str` (Markdown text)
**Purpose:** A full database migration guide with headers, code blocks, prerequisites, and warnings for testing comprehensive document compression

```python
@pytest.fixture
def sample_complex_doc():
    """A comprehensive database migration guide with code blocks.

    This fixture is a realistic, full-length technical document with multiple
    sections, code blocks, prerequisites, and warnings. Used by
    TestContextOverflowHypothesis and TestSemanticFidelityHypothesis to
    validate that complex information is meaningfully compressed while
    preserving critical details.

    Returns:
        str: Full-length database migration guide.
    """
    return """# PostgreSQL Database Migration Guide

## Overview

This guide walks you through migrating data from a legacy MySQL database to PostgreSQL. The process involves backing up the existing database, preparing the new PostgreSQL instance, and verifying data integrity after migration.

## Prerequisites

- PostgreSQL 13 or later installed and running
- MySQL database credentials and access
- Minimum 2x disk space of the current database size
- Network connectivity between MySQL and PostgreSQL servers
- Administrative access on both database systems

## Step 1: Backup the Current Database

Before any migration, back up your existing MySQL database using `mysqldump`:

```bash
mysqldump -u root -p legacy_db > legacy_db_backup.sql
```

This creates a complete snapshot of the database schema and data.

**Prerequisites:** MySQL client tools must be installed. The backup will take time proportional to database size.

## Step 2: Prepare PostgreSQL

Create the target database and user in PostgreSQL:

```bash
psql -U postgres -c "CREATE DATABASE legacy_db;"
psql -U postgres -c "CREATE USER legacy_user WITH PASSWORD 'secure_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE legacy_db TO legacy_user;"
```

This configures PostgreSQL to receive the migrated data.

## Step 3: Migrate Schema and Data

Use a migration tool like `pgloader` to automatically convert MySQL schema to PostgreSQL:

```bash
pgloader mysql://root:password@localhost/legacy_db postgresql://legacy_user:password@localhost/legacy_db
```

The tool handles schema conversion, data type mapping, and constraint translation.

**Prerequisites:** pgloader must be installed. Network connectivity from your machine to both databases is required.

## Step 4: Verify Data Integrity

Execute validation queries to confirm data was migrated correctly:

```bash
psql -U legacy_user legacy_db -c "SELECT COUNT(*) FROM users;"
psql -U legacy_user legacy_db -c "SELECT COUNT(*) FROM orders;"
```

Compare these counts against the original MySQL database.

## Warnings and Caveats

- **Warning:** Do not delete the original MySQL database until you have verified the PostgreSQL migration is complete and correct. Backup deletion is irreversible.
- **Important:** The migration process may take hours for large databases. Plan downtime accordingly.
- **Caution:** Data type conversions (MySQL DATETIME to PostgreSQL TIMESTAMP) may cause subtle timezone-related bugs. Thoroughly test application behavior after migration.

## Rollback Plan

If migration fails, restore from the backup:

```bash
mysql -u root -p legacy_db < legacy_db_backup.sql
```

This reverts to the pre-migration state.

## Next Steps

After successful migration:
1. Update application connection strings to point to PostgreSQL
2. Run application test suite against the new database
3. Monitor production for 48 hours before decommissioning the MySQL instance
4. Archive the backup file for long-term retention"""
```

**Expected Usage:**
- `TestContextOverflowHypothesis.test_compression_ratio()` — expects ≥40% compression ratio on realistic document
- `TestContextOverflowHypothesis.test_information_density()` — verifies action/state/exec keywords survive compression
- `TestSemanticFidelityHypothesis.test_command_preservation()` — verifies shell commands (pg_dump, psql, pgloader) are preserved as EXEC: operators
- `TestSemanticFidelityHypothesis.test_warning_preservation()` — verifies multiple WARN: operators are preserved
- Token count: ~900 original tokens, expected compression to ~350–450 tokens

---

### Fixture 4: `sample_entities`

**Type:** `pytest.fixture()`
**Returns:** `dict` (entity dictionary)
**Purpose:** A pre-built entity dictionary matching the canonical "restart server" example, used to test CNL synthesis without requiring live extraction

```python
@pytest.fixture
def sample_entities():
    """A pre-built entity dictionary representing a server restart procedure.

    This fixture contains a fully-formed entity dictionary with Actions,
    States, Commands, Warnings, and Dependencies. It matches the project's
    canonical "restart server" example and is used by tests that validate
    CNL synthesis directly without requiring live LLM extraction.

    This fixture data should match the shape and content of what EntityExtractor
    would produce from the sample_simple_doc.

    Returns:
        dict: Entity dictionary with keys: actions, states, commands, warnings, dependencies.
    """
    return {
        "actions": {
            "Save_Config": "Save the application configuration file to persistent storage",
            "Run_Restart": "Execute the restart command to reboot the server"
        },
        "states": {
            "Config_Saved": "Configuration file has been written and persisted",
            "Server_Running": "Server process is active and responding to requests",
            "Server_Stopped": "Server process is terminated"
        },
        "commands": {
            "save_config": "save the config",
            "restart_command": "run the restart command"
        },
        "warnings": {
            "Unsaved_Changes": "Unsaved changes will be lost if the config is not saved before restart"
        },
        "dependencies": [
            {
                "action": "Run_Restart",
                "requires": "Config_Saved",
                "reason": "Server must have persisted configuration before restart"
            }
        ]
    }
```

**Expected Usage:**
- `TestPrerequisiteHypothesis.test_action_state_linking()` — passes to `synthesize_cnl(sample_entities)` to validate REQUIRES operator generation
- This fixture allows testing CNL synthesis without live API calls (suitable for both Phase 2 and Phase 3 test suites)

---

## Fixture Coverage Matrix

| Fixture | `TestPrerequisiteHypothesis` | `TestContextOverflowHypothesis` | `TestSemanticFidelityHypothesis` | `TestCompressionMetrics` |
|---------|-----|-----|-----|-----|
| `sample_simple_doc` | ✗ | ✗ | ✗ | ✓ (test_simple_compression) |
| `sample_medium_doc` | ✓ (both tests) | ✓ (both tests) | ✓ (both tests) | ✗ |
| `sample_complex_doc` | ✗ | ✓ (both tests) | ✓ (both tests) | ✗ |
| `sample_entities` | ✓ (test_action_state_linking) | ✗ | ✗ | ✗ |

---

## File Structure

```
haiku-protocol/
├── tests/
│   ├── conftest.py                    ← UPDATED: Add 4 fixtures
│   ├── test_chunker.py                (Phase 2 — unchanged)
│   ├── test_extractor.py              (Phase 2 — unchanged)
│   ├── test_synthesizer.py            (Phase 2 — unchanged)
│   ├── test_validator.py              (Phase 2 — unchanged)
│   └── test_validation.py             (Phase 3 — NEW, uses these fixtures)
```

---

## Implementation Workflow

```
┌────────────────────────────────────────────────────────────┐
│                   FIXTURE IMPLEMENTATION                    │
└────────────────────────────────────────────────────────────┘

  1. OPEN tests/conftest.py
     │
     ├─→ Check for existing Phase 2 fixtures
     │   (pytest should already have fixture definitions)
     │
  2. ADD sample_simple_doc FIXTURE
     │
     ├─→ Define with @pytest.fixture decorator
     ├─→ Return one-sentence string
     ├─→ Add docstring
     │
  3. ADD sample_medium_doc FIXTURE
     │
     ├─→ Define with @pytest.fixture decorator
     ├─→ Return multi-step procedure Markdown
     ├─→ Include warnings, prerequisites, multiple steps
     ├─→ Add docstring
     │
  4. ADD sample_complex_doc FIXTURE
     │
     ├─→ Define with @pytest.fixture decorator
     ├─→ Return full-length technical document (Markdown)
     ├─→ Include headers, code blocks, warnings, prerequisites
     ├─→ Add docstring
     │
  5. ADD sample_entities FIXTURE
     │
     ├─→ Define with @pytest.fixture decorator
     ├─→ Return dict with actions, states, commands, warnings, dependencies
     ├─→ Add docstring
     │
  6. VERIFY imports are present (pytest)
     │
  7. RUN `pytest tests/conftest.py --collect-only` to confirm fixtures are discoverable
     │
  8. DOCUMENT fixture signatures in this file (DONE)
```

---

## Acceptance Criteria

- [ ] `sample_simple_doc` fixture exists in `tests/conftest.py` and returns a string
- [ ] `sample_medium_doc` fixture exists and returns a multi-step Markdown document string
- [ ] `sample_complex_doc` fixture exists and returns a full-length technical document string
- [ ] `sample_entities` fixture exists and returns a dict with keys: actions, states, commands, warnings, dependencies
- [ ] All four fixtures are decorated with `@pytest.fixture`
- [ ] All four fixtures have docstrings following the project's commenting standards
- [ ] `pytest tests/conftest.py --collect-only` lists all four fixtures as discoverable
- [ ] Fixtures are accessible from `tests/test_validation.py` (imports via pytest automatic discovery)
- [ ] Fixtures do NOT override or break any existing Phase 2 fixtures (if Phase 2 already has `sample_simple_doc`, coordinate naming to avoid collision)
- [ ] Each fixture is imported or injected correctly by Phase 3 test methods (verified during v0.3.2b/c implementation)

---

## Limitations & Constraints

### Static Content
- Fixtures return hardcoded strings and dictionaries. They do not generate random data, use factories, or parametrize content.
- If test data needs to change, the fixtures themselves must be manually edited. This is acceptable because fixtures represent "golden" canonical examples.

### No Replacement of Phase 2 Fixtures
- If `tests/conftest.py` already contains fixtures with the same names (e.g., a `sample_simple_doc` from Phase 2), this sub-part documents how to handle the collision:
  - **Option A (Recommended):** Verify that the existing fixture matches the specification in this document. If so, use the existing fixture without re-definition.
  - **Option B:** Rename the Phase 3 fixture to avoid collision (e.g., `sample_simple_doc_v3`, then update references in v0.3.2b/c tests).
  - **Option C:** Merge the fixtures if Phase 2 and Phase 3 definitions are compatible.

### No File-Based Fixtures
- All test data is embedded as Python string literals and dictionaries within fixture functions. Test data is NOT loaded from external files (e.g., `benchmarks/samples/`).
- This avoids file I/O complexity and keeps the test suite self-contained.

### Fixture Scope
- All four fixtures use the default scope: `scope="function"`. Each test method receives a fresh copy of the fixture data.
- Fixtures are not module-scoped, session-scoped, or class-scoped.

---

## Dependencies

- **pytest** (from `requirements.txt`) — provides the `@pytest.fixture` decorator
- **No external dependencies** — fixtures use only Python built-ins (str, dict)

---

## Outputs to Next Sub-Part

After v0.3.2a is complete:

1. **Fixture availability:** The four fixtures are available via pytest's automatic discovery mechanism.
2. **Next step (v0.3.2b):** The hypothesis validation test classes in `test_validation.py` import and use these fixtures as test method parameters.
3. **Next step (v0.3.2c):** The compression metrics tests also reference `sample_simple_doc` and `sample_complex_doc`.

---

## Decision Log

### Decision 1: Inline Strings vs. File-Loaded Fixtures

**Choice:** Inline strings (embedded in fixture definitions)

**Rationale:**
- Keeps the test suite self-contained. No external file dependencies.
- Fixtures are the single source of truth for test data.
- Simpler to debug — data is visible in the code without opening additional files.
- File loading adds I/O complexity and path management issues.

**Trade-offs:**
- Long test documents make `conftest.py` larger (~400 lines).
- Changes to test data require editing Python code, not just text files.

---

### Decision 2: Additive vs. Replacement Fixtures

**Choice:** Additive (new fixtures added to existing `conftest.py` without replacing Phase 2 fixtures)

**Rationale:**
- Phase 2 may already have fixtures with similar names (e.g., module-specific fixtures for chunker, extractor, synthesizer tests).
- Adding Phase 3 fixtures globally allows Phase 3 tests to use them without forcing Phase 2 tests to migrate.
- Phase 2 tests continue to work unchanged.
- When Phase 2 and Phase 3 need the same data (e.g., both use a "simple_doc"), they can share the Phase 3.2a fixtures.

**Trade-offs:**
- If naming collisions occur, fixtures must be disambiguated (rename or merge).
- Requires coordination between Phase 2 and Phase 3 specifications.

---

**Document Version:** 1.0
**Last Updated:** 2026-02-09
**Author:** Haiku Protocol Project
**Status:** Ready for Implementation
