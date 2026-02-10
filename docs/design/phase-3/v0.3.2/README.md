# v0.3.2 — Test Suite Implementation

<aside>

**Version:** v0.3.2

**Parent:** v0.3.0 — Demo & Visualization

**Status:** ⬜ Not Started

**Duration:** 45–60 minutes (across 3 sub-parts)

**Deliverable:** Complete pytest test suite (`conftest.py` update + `test_validation.py`)

</aside>

---

## Objective

Build a comprehensive test suite that proves the Haiku Protocol works as claimed. Implements the three hypothesis-validation tests from the original Technical Design Document (Prerequisite, Context Overflow, Semantic Fidelity) plus compression metrics tests.

---

## Sub-Parts

| Version | Name | Duration | Deliverable |
|---------|------|----------|-------------|
| [v0.3.2a](shared_fixtures.md) | Shared Test Fixtures (conftest.py) | 10–15 min | 4 shared fixtures: simple/medium/complex docs + sample entities |
| [v0.3.2b](hypothesis_validation_tests.md) | Hypothesis Validation Tests | 25–35 min | 3 test classes (6 tests): Prerequisite, Context Overflow, Semantic Fidelity |
| [v0.3.2c](compression_metrics_tests.md) | Compression Metrics Tests & Coverage | 10–15 min | TestCompressionMetrics (2 tests), coverage verification, pytest commands |

**Total: 8 tests in test_validation.py | Coverage target: ≥80% across src/**

---

## Test Categories

---

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_chunker.py          # Chunking module tests
├── test_extractor.py        # Entity extraction tests
├── test_synthesizer.py      # CNL synthesis tests
├── test_validator.py        # Metrics tests
├── test_encoder.py          # Full encoder tests
└── test_validation.py       # Hypothesis validation tests
```

---

## Implementation: [`conftest.py`](http://conftest.py)

```python
# tests/conftest.py - Shared test fixtures

import pytest

@pytest.fixture
def sample_simple_doc():
    """Simple single-procedure document."""
    return "To restart the server, save the config and run the restart command."

@pytest.fixture
def sample_medium_doc():
    """Medium complexity document."""
    return """
    Before deploying the application, ensure all tests pass.
    Run the build script to compile the assets.
    If the build succeeds, execute the deployment command.
    Verify that the service is running after deployment.
    Warning: Skipping tests may cause production issues.
    """

@pytest.fixture
def sample_complex_doc():
    """Complex multi-step document."""
    return """
    # Database Migration Guide
    
    ## Prerequisites
    Before starting the migration, ensure you have:
    - Admin access to the database
    - A recent backup (less than 24 hours old)
    - At least 50GB of free disk space
    
    ## Step 1: Create Backup
    Run the following command to create a backup:
```

pg_dump -U admin production_db > backup.sql

```

## Step 2: Run Migration
Execute the migration script:
```

python [manage.py](http://manage.py) migrate --database=production

```

## Step 3: Verify
Check that all tables are present:
```

psql -U admin -c "\dt"

```
    
    Warning: Do not proceed without a backup. Data loss is permanent.
    """

@pytest.fixture
def sample_entities():
    """Sample extracted entities."""
    return {
        "actions": ["Restart_Server"],
        "states": ["Config_Saved"],
        "commands": ["systemctl restart"],
        "warnings": ["Skip save causes data loss"],
        "dependencies": [
            {"action": "Restart", "requires": "Config_Saved"}
        ]
    }
```

---

## Implementation: `test_[validation.py](http://validation.py)`

```python
# tests/test_validation.py - Hypothesis Validation Tests

import pytest
from src.encoder import encode
from src.validator import CompressionValidator

class TestPrerequisiteHypothesis:
    """
    Test 1: The Prerequisite Test
    
    Hypothesis: Baseline AI loses track of dependencies in verbose text.
                Haiku preserves them through REQUIRES syntax.
    """
    
    def test_dependency_extraction(self, sample_medium_doc):
        """Test that dependencies are extracted and preserved."""
        result = encode(sample_medium_doc)
        
        # The REQUIRES keyword should appear in compressed output
        assert "REQUIRES" in result["haiku"] or "State:" in result["haiku"]
    
    def test_action_state_linking(self, sample_entities):
        """Test that actions are linked to required states."""
        from src.synthesizer import synthesize_cnl
        
        cnl = synthesize_cnl(sample_entities)
        
        # Should contain dependency relationship
        assert "REQUIRES" in cnl

class TestContextOverflowHypothesis:
    """
    Test 2: The Context Overflow Test
    
    Hypothesis: When context is saturated, Haiku retains more 
                actionable information than verbose text.
    """
    
    def test_compression_ratio(self, sample_complex_doc):
        """Test that compression achieves target ratio."""
        result = encode(sample_complex_doc)
        
        # Should achieve at least 40% compression
        assert result["compression_ratio"] >= 0.4
    
    def test_information_density(self, sample_complex_doc):
        """Test that compressed output is information-dense."""
        result = encode(sample_complex_doc)
        
        # Compressed output should still contain key information
        haiku = result["haiku"].lower()
        
        # Should preserve key concepts
        assert any(word in haiku for word in ["action", "exec", "state", "backup", "migrate"])

class TestSemanticFidelityHypothesis:
    """
    Test 3: The Semantic Fidelity Test
    
    Hypothesis: Compression is lossless—the meaning is fully recoverable.
    """
    
    def test_command_preservation(self, sample_medium_doc):
        """Test that literal commands are preserved."""
        result = encode(sample_medium_doc)
        
        # EXEC commands should preserve the command text
        if "EXEC:" in result["haiku"]:
            # Command should be recognizable
            assert any(c in result["haiku"].lower() for c in ["deploy", "build", "test", "run"])
    
    def test_warning_preservation(self, sample_medium_doc):
        """Test that warnings are preserved."""
        result = encode(sample_medium_doc)
        
        # Warnings should be captured
        haiku = result["haiku"]
        assert "WARN:" in haiku or "warning" in sample_medium_doc.lower()

class TestCompressionMetrics:
    """Test compression metrics calculation."""
    
    def test_simple_compression(self, sample_simple_doc):
        """Test compression of simple document."""
        result = encode(sample_simple_doc)
        
        assert result["original_tokens"] > 0
        assert result["compressed_tokens"] > 0
        assert result["compressed_tokens"] < result["original_tokens"]
    
    def test_metrics_accuracy(self):
        """Test that metrics are calculated correctly."""
        validator = CompressionValidator()
        
        original = "This is a test sentence with multiple tokens."
        compressed = "Test:Sentence"
        
        metrics = validator.calculate_metrics(original, compressed)
        
        assert metrics.original_tokens > metrics.compressed_tokens
        assert 0 <= metrics.compression_ratio <= 1
```

---

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_validation.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run only validation tests
pytest -k "Hypothesis"
```

---

## Acceptance Criteria

- [ ]  [`conftest.py`](http://conftest.py) with shared fixtures
- [ ]  Unit tests for each module
- [ ]  3 hypothesis validation tests
- [ ]  All tests pass (`pytest` returns 0)
- [ ]  Test coverage ≥80%