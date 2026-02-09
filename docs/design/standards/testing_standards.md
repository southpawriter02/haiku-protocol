# Testing Standards — Haiku Protocol

<aside>

**Scope:** All phases (v0.1.x through v0.4.x)

**Status:** Active

**Applies To:** All Python source in `src/`, `tests/`, and integration scripts

**Deliverable:** Enforceable testing conventions, pytest configuration, coverage targets, fixture patterns, and CI/CD integration requirements

</aside>

---

## Purpose

This document establishes the testing standards for the Haiku Protocol project. Every module, class, and public function must be tested. These standards ensure code correctness, prevent regressions, and provide confidence during refactoring and feature development.

---

## Testing Philosophy

### Core Principles

1. **Tests are not optional.** Every pull request that touches `src/` must include or update corresponding tests.
2. **Tests are documentation.** A test should demonstrate how a function is used and what it guarantees.
3. **Tests must be deterministic.** No test should depend on network state, time of day, or random values without explicit seeding.
4. **Tests must be independent.** Each test must pass in isolation and in any execution order.
5. **Tests must be fast.** Unit tests should complete in under 1 second each. Tests requiring external APIs are integration tests and must be marked accordingly.

### Test Pyramid

```
         ┌───────────┐
         │  E2E /    │  ← Few: Full Streamlit UI workflows
         │  System   │     (v0.3.x)
         ├───────────┤
         │Integration│  ← Some: API calls, multi-module flows
         │  Tests    │     (v0.2.x+)
         ├───────────┤
         │           │
         │   Unit    │  ← Many: Individual functions, classes
         │   Tests   │     (every phase)
         │           │
         └───────────┘
```

**Target distribution:** 70% unit, 20% integration, 10% E2E.

---

## Framework and Tooling

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| pytest | 7.4.3+ | Test runner and framework |
| pytest-cov | 4.1.0+ | Coverage measurement and reporting |
| pytest-asyncio | 0.23.1+ | Async test support (for async LLM calls) |

### Optional Tools

| Tool | Version | Purpose |
|------|---------|---------|
| pytest-mock | 3.12.0+ | Simplified mocking via `mocker` fixture |
| pytest-xdist | 3.5.0+ | Parallel test execution |
| pytest-timeout | 2.2.0+ | Per-test timeout enforcement |

---

## Directory Structure

```
tests/
├── __init__.py                    # Required: makes tests a package
├── conftest.py                    # Shared fixtures, configuration
├── test_encoder.py                # Unit tests for src/encoder.py
├── test_decoder.py                # Unit tests for src/decoder.py
├── test_chunker.py                # Unit tests for src/chunker.py
├── test_extractor.py              # Unit tests for src/extractor.py
├── test_synthesizer.py            # Unit tests for src/synthesizer.py
├── test_validator.py              # Unit tests for src/validator.py
├── test_config.py                 # Unit tests for src/config.py
├── test_api.py                    # API connection validation (v0.1.2d)
├── integration/                   # Integration tests (v0.2.x+)
│   ├── __init__.py
│   ├── test_pipeline.py           # End-to-end compression pipeline
│   └── test_api_integration.py    # Live API call tests
└── fixtures/                      # Test data and sample documents
    ├── sample_short.txt           # < 100 tokens
    ├── sample_medium.txt          # 100–500 tokens
    └── sample_long.txt            # 500+ tokens
```

---

## Naming Conventions

### Files

| Pattern | Example | Usage |
|---------|---------|-------|
| `test_{module}.py` | `test_encoder.py` | Unit tests mirroring `src/{module}.py` |
| `test_{feature}.py` | `test_pipeline.py` | Integration tests for cross-module features |
| `conftest.py` | `conftest.py` | Shared fixtures (one per directory level) |

### Functions

```python
# Pattern: test_{method_or_behavior}_{scenario}_{expected_result}

# Good examples:
def test_encode_short_document_returns_cnl():
def test_encode_empty_document_raises_value_error():
def test_validate_missing_api_key_returns_false():
def test_chunk_semantic_strategy_respects_sentence_boundaries():

# Bad examples:
def test_1():                    # No description
def test_encode():               # Too vague
def test_it_works():             # Not specific
def testEncode():                # Wrong naming style
```

### Classes (for grouped tests)

```python
# Pattern: Test{ClassName}

class TestHaikuEncoder:
    """Tests for HaikuEncoder class."""

    def test_encode_returns_string(self):
        ...

    def test_encode_empty_input_raises(self):
        ...

class TestHaikuEncoderBatch:
    """Tests for HaikuEncoder batch operations."""

    def test_encode_batch_multiple_documents(self):
        ...
```

---

## Test Structure — The AAA Pattern

Every test must follow the **Arrange–Act–Assert** pattern:

```python
def test_chunk_fixed_size_creates_correct_count():
    """Fixed-size chunking produces expected number of chunks."""
    # Arrange — set up inputs and expected state
    chunker = DocumentChunker(chunk_size=100, strategy="fixed_size")
    document = "a" * 350  # 350 characters

    # Act — execute the behavior under test
    chunks = chunker.chunk(document)

    # Assert — verify the outcome
    assert len(chunks) == 4  # 100 + 100 + 100 + 50
    assert all(isinstance(c, Chunk) for c in chunks)
    assert chunks[-1].token_count <= 100
```

### Rules

- **One behavior per test.** If a test has multiple unrelated assertions, split it.
- **No logic in tests.** No `if`, `for`, or `try/except` in test bodies (except `pytest.raises`).
- **Descriptive assertion messages** for non-obvious checks:

```python
# Good — message explains the business rule
assert metrics.compression_ratio > 0.3, (
    f"Compression ratio {metrics.compression_ratio} below minimum 30% threshold"
)

# Acceptable — assertion is self-evident
assert result.is_valid is True
```

---

## Fixtures

### Project-Level Fixtures (tests/conftest.py)

```python
"""Shared test fixtures for Haiku Protocol test suite."""

import os
import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory path."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def sample_short_text():
    """Short sample document (< 100 tokens) for fast unit tests."""
    return (
        "The algorithm processes input data using a neural network. "
        "It produces compressed output in CNL format."
    )


@pytest.fixture(scope="session")
def sample_medium_text():
    """Medium sample document (100–500 tokens) for standard tests."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    return (fixtures_dir / "sample_medium.txt").read_text()


@pytest.fixture
def mock_config(monkeypatch):
    """Mock configuration with test values (no real API key needed)."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-for-unit-testing")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


@pytest.fixture
def encoder(mock_config):
    """HaikuEncoder instance with mocked configuration."""
    from src.encoder import HaikuEncoder
    return HaikuEncoder()


@pytest.fixture
def chunker():
    """DocumentChunker instance with default settings."""
    from src.chunker import DocumentChunker
    return DocumentChunker(chunk_size=512, strategy="semantic")
```

### Fixture Best Practices

| Do | Don't |
|----|-------|
| Use `scope="session"` for expensive, immutable fixtures (file reads, model loads) | Use `scope="session"` for mutable state |
| Use `monkeypatch` for environment variable overrides | Directly modify `os.environ` without cleanup |
| Keep fixtures small and focused | Create "god fixtures" that set up everything |
| Name fixtures after what they provide (`sample_short_text`) | Name fixtures after the test (`setup_for_test_1`) |
| Put shared fixtures in `conftest.py` | Duplicate fixture code across test files |

---

## Mocking Standards

### When to Mock

| Scenario | Mock? | Rationale |
|----------|-------|-----------|
| OpenAI API calls | Yes | Cost, speed, determinism |
| File system reads (test data) | No | Use actual fixture files |
| Config loading from `.env` | Yes | Use `monkeypatch.setenv()` |
| LLM model initialization | Yes | Expensive, requires downloads |
| Pure Python functions | No | Test the real thing |
| Time-dependent logic | Yes | Use `freezegun` or manual injection |

### Mocking Patterns

```python
# Pattern 1: monkeypatch for environment variables
def test_config_loads_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-1234567890")
    from src.config import Config
    assert Config.get_openai_api_key() == "sk-test-1234567890"


# Pattern 2: unittest.mock for class methods
from unittest.mock import patch, MagicMock

def test_encoder_calls_chunker():
    with patch("src.encoder.DocumentChunker") as MockChunker:
        mock_instance = MockChunker.return_value
        mock_instance.chunk.return_value = [Chunk(text="test", chunk_id=0, ...)]

        encoder = HaikuEncoder()
        encoder.encode("test document")

        mock_instance.chunk.assert_called_once()


# Pattern 3: Mock LLM responses
def test_synthesizer_generates_cnl():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content="[CNL: test output]")

    synthesizer = CNLSynthesizer(llm=mock_llm)
    result = synthesizer.synthesize(entities=[...], relations={...})

    assert "[CNL:" in result
```

---

## Markers and Categories

### Required Markers

```python
# In conftest.py or pytest.ini, register custom markers:

# pytest.ini
[pytest]
markers =
    unit: Unit tests (no external dependencies)
    integration: Integration tests (may require API keys or network)
    slow: Tests that take > 5 seconds
    api: Tests that make real API calls (cost money)
```

### Applying Markers

```python
import pytest

@pytest.mark.unit
def test_chunk_returns_list():
    """Pure unit test — no external dependencies."""
    ...

@pytest.mark.integration
@pytest.mark.api
def test_api_connection_live():
    """Integration test — requires valid API key and network."""
    ...

@pytest.mark.slow
def test_encode_large_document():
    """Performance test — processes 10,000+ token document."""
    ...
```

### Running by Marker

```bash
# Run only unit tests (fast, no API needed)
pytest -m unit

# Run everything except API tests
pytest -m "not api"

# Run integration tests only
pytest -m integration
```

---

## Coverage Requirements

### Targets

| Phase | Minimum Coverage | Target Coverage | Scope |
|-------|-----------------|-----------------|-------|
| v0.1.x | N/A (stubs only) | N/A | Config and API validation only |
| v0.2.x | 70% | 85% | All `src/` modules |
| v0.3.x | 80% | 90% | `src/` + Streamlit helpers |
| v0.4.x (release) | 85% | 95% | Full project |

### Running Coverage

```bash
# Basic coverage report
pytest --cov=src --cov-report=term-missing

# HTML report (open htmlcov/index.html)
pytest --cov=src --cov-report=html

# Fail if coverage drops below threshold
pytest --cov=src --cov-fail-under=80
```

### Coverage Configuration (pyproject.toml or .coveragerc)

```ini
[tool:pytest]
addopts = --cov=src --cov-report=term-missing --tb=short -q

[coverage:run]
source = src
omit =
    src/app.py          # Streamlit UI — tested separately
    src/__init__.py     # Package metadata only

[coverage:report]
fail_under = 80
show_missing = true
exclude_lines =
    pragma: no cover
    raise NotImplementedError
    if __name__ == "__main__"
    if TYPE_CHECKING
```

### What to Exclude from Coverage

- `NotImplementedError` stubs (v0.1.3c placeholders)
- `if __name__ == "__main__"` blocks
- Type-checking-only imports (`if TYPE_CHECKING`)
- Streamlit UI code (tested via integration/E2E, not unit)

---

## Parametrized Testing

Use `@pytest.mark.parametrize` for testing the same logic with multiple inputs:

```python
import pytest

@pytest.mark.parametrize("strategy,expected_type", [
    ("fixed_size", list),
    ("semantic", list),
    ("sliding_window", list),
])
def test_chunk_strategies_return_list(strategy, expected_type):
    """All chunking strategies return a list of Chunks."""
    chunker = DocumentChunker(strategy=strategy)
    result = chunker.chunk("Sample document text for testing.")
    assert isinstance(result, expected_type)


@pytest.mark.parametrize("input_text,expected_error", [
    ("", ValueError),
    (None, TypeError),
    (123, TypeError),
])
def test_encode_invalid_input_raises(input_text, expected_error):
    """Invalid inputs raise appropriate exceptions."""
    encoder = HaikuEncoder()
    with pytest.raises(expected_error):
        encoder.encode(input_text)


@pytest.mark.parametrize("debug_value,expected", [
    ("true", True),
    ("True", True),
    ("TRUE", True),
    ("1", True),
    ("yes", True),
    ("false", False),
    ("0", False),
    ("no", False),
    ("", False),
])
def test_debug_coercion(monkeypatch, debug_value, expected):
    """DEBUG environment variable correctly coerced to boolean."""
    monkeypatch.setenv("DEBUG", debug_value)
    assert Config.get_debug_mode() is expected
```

---

## Testing Async Code

For modules that use async LLM calls (v0.2.x+):

```python
import pytest

@pytest.mark.asyncio
async def test_async_encode():
    """Async encoding completes and returns CNL string."""
    encoder = HaikuEncoder()
    result = await encoder.encode_async("Test document")
    assert isinstance(result, str)
    assert len(result) > 0
```

---

## Error and Edge Case Testing

### Required Edge Cases per Module

Every module test file must cover:

1. **Empty input** — empty string, empty list, None
2. **Boundary values** — single character, single token, maximum size
3. **Invalid types** — wrong argument types
4. **Invalid format** — malformed input data
5. **Error propagation** — exceptions from dependencies are handled

```python
class TestHaikuEncoderEdgeCases:
    """Edge case tests for HaikuEncoder."""

    def test_encode_empty_string_raises(self, encoder):
        with pytest.raises(ValueError, match="empty"):
            encoder.encode("")

    def test_encode_none_raises(self, encoder):
        with pytest.raises(TypeError):
            encoder.encode(None)

    def test_encode_single_word_returns_cnl(self, encoder):
        result = encoder.encode("Hello")
        assert isinstance(result, str)

    def test_encode_very_long_document(self, encoder, sample_long_text):
        """Encoder handles documents exceeding chunk size."""
        result = encoder.encode(sample_long_text)
        assert len(result) < len(sample_long_text)
```

---

## Test Data Management

### Fixture Files

Store reusable test data in `tests/fixtures/`:

```
tests/fixtures/
├── sample_short.txt               # "The algorithm processes input data..."
├── sample_medium.txt              # 200-word technical document
├── sample_long.txt                # 1000+ word document
├── expected_cnl_short.txt         # Expected CNL output for sample_short
├── invalid_cnl.txt                # Intentionally malformed CNL
└── edge_cases/
    ├── unicode_heavy.txt          # Non-ASCII characters
    ├── empty.txt                  # Zero-byte file
    └── single_line.txt            # No paragraph breaks
```

### Rules for Test Data

| Do | Don't |
|----|-------|
| Use small, focused fixture files | Use real user data or production content |
| Version-control all fixture files | Generate fixture data at test time (unless random) |
| Document what each fixture tests | Create fixtures without clear purpose |
| Keep fixtures under 10 KB each | Use large files for unit tests (save for integration) |

---

## Integration Test Standards

Integration tests live in `tests/integration/` and have additional rules:

```python
"""
Integration tests for the full compression pipeline.

These tests may:
- Make real API calls (marked with @pytest.mark.api)
- Take longer than 5 seconds (marked with @pytest.mark.slow)
- Require valid .env configuration

Run with: pytest tests/integration/ -m integration
"""

import pytest

@pytest.mark.integration
@pytest.mark.api
def test_full_compression_pipeline():
    """Test encoder → chunker → extractor → synthesizer → validator flow."""
    from src.encoder import HaikuEncoder
    from src.validator import HaikuValidator

    encoder = HaikuEncoder()
    validator = HaikuValidator()

    original = "The Haiku Protocol compresses documents using CNL."
    compressed = encoder.encode(original)
    result = validator.validate(original, compressed)

    assert result.is_valid
    assert result.confidence > 0.7
```

---

## Workflow: Writing Tests

### Step-by-Step Process

```
1. Identify the function or class to test
       │
       ▼
2. Create or open tests/test_{module}.py
       │
       ▼
3. Write the test function name (descriptive)
       │
       ▼
4. Write the Arrange section (setup)
       │
       ▼
5. Write the Act section (call the function)
       │
       ▼
6. Write the Assert section (verify)
       │
       ▼
7. Run the test: pytest tests/test_{module}.py -v
       │
       ▼
8. Verify coverage: pytest --cov=src/{module}
       │
       ▼
9. Add edge cases and error scenarios
       │
       ▼
10. Run full suite: pytest --cov=src --cov-fail-under=80
```

### Pre-Commit Checklist

Before committing code changes:

- [ ] All existing tests pass: `pytest`
- [ ] New tests written for new/changed code
- [ ] Coverage has not decreased: `pytest --cov=src`
- [ ] No tests depend on network (unless marked `@pytest.mark.api`)
- [ ] No tests modify global state without cleanup
- [ ] Test names are descriptive and follow naming convention

---

## Dos and Don'ts

### Do

- Write tests before or alongside implementation (test-informed development)
- Use fixtures for shared setup
- Use parametrize for repetitive test patterns
- Test both happy path and error paths
- Use `pytest.raises` for expected exceptions
- Keep unit tests under 1 second each
- Mock external dependencies (APIs, file I/O to external systems)
- Run the full test suite before pushing

### Don't

- Write tests that depend on execution order
- Use `time.sleep()` in tests (use mocks instead)
- Test private methods directly (test through public interface)
- Hardcode file paths (use `tmp_path` fixture or `project_root`)
- Leave debugging `print()` statements in tests
- Skip writing tests because "it's just a small change"
- Mock the thing you're testing (mock its *dependencies*)
- Write tests that pass when the code is broken (tautological tests)

---

## Acceptance Criteria (for this document)

- [ ] pytest is the sole test framework (no unittest-style `self.assert*`)
- [ ] All test files follow `test_{module}.py` naming
- [ ] All test functions follow `test_{method}_{scenario}_{result}` naming
- [ ] `conftest.py` exists with shared fixtures
- [ ] Coverage target of 80%+ is configured and enforced
- [ ] Custom markers (`unit`, `integration`, `api`, `slow`) are registered
- [ ] Parametrized tests are used where 3+ inputs test the same logic
- [ ] Mocking patterns documented for API calls and configuration
- [ ] Integration tests are separated into `tests/integration/`
- [ ] Test fixture files are stored in `tests/fixtures/`
- [ ] Edge case requirements are defined for every module

---

## Related Documents

- [v0.1.2d — API Connection Testing & Validation](../phase-1/v0.1.2/api_connection_testing_and_validation.md) — First test module created
- [v0.1.2c — Configuration Module Implementation](../phase-1/v0.1.2/configuration_module_implementation.md) — Test examples for Config class
- [v0.1.3c — Source Module Stubs](../phase-1/v0.1.3/source_module_stubs.md) — Module interfaces to be tested
- [v0.3.2 — Test Suite Implementation](../phase-3/v0.3.2/README.md) — Phase where comprehensive tests are written
- [Logging Standards](logging_standards.md) — Logging configuration for test output
