# v0.3.2c — Compression Metrics Tests & Coverage

<aside>

**Version:** v0.3.2c

**Parent:** v0.3.2 — Test Suite Implementation

**Status:** ⬜ Not Started

**Duration:** 10–15 minutes

**Deliverable:** `TestCompressionMetrics` class (2 tests), coverage verification commands, combined Phase 2 + Phase 3 test suite integration

</aside>

---

## Objective

Complete the hypothesis validation test suite by implementing metrics-level tests that validate the compression pipeline's mathematical correctness. While v0.3.2b tests focus on thesis claims (semantic fidelity, information preservation), v0.3.2c tests verify that the underlying metrics pipeline produces valid results. Additionally, this sub-part documents the coverage verification strategy for combined Phase 2 + Phase 3 test execution, ensuring the entire project meets the ≥80% coverage target.

---

## User Stories

> As a developer, I want to verify that the compression metrics pipeline produces mathematically correct results (compressed < original, ratio between 0 and 1) so that I can trust the reported compression statistics.

> As a QA engineer, I want to run the full test suite and see combined coverage ≥80% so that I have confidence in code quality across both Phase 2 and Phase 3.

---

## Implementation Design

### Test Class: `TestCompressionMetrics`

**Purpose:** Validate the correctness of the compression metrics pipeline (token counting, ratio calculation).

```python
import pytest
from src.encoder import encode
from src.validator import CompressionValidator


class TestCompressionMetrics:
    """Test the compression metrics pipeline for mathematical correctness.

    These tests validate that the underlying compression metrics (token counts,
    compression ratio, savings) are calculated correctly. Unlike the hypothesis
    tests which validate semantic properties of the CNL output, these tests
    focus on the numerical accuracy of the metrics.

    Two tests validate:
    1. Simple compression: Token counts are positive and compression reduces count
    2. Metrics accuracy: CompressionValidator calculations are mathematically correct
    """

    def test_simple_compression(self, sample_simple_doc):
        """Test that encode() returns mathematically valid compression metrics.

        Procedure:
        1. Call encode() with sample_simple_doc (single-sentence procedure)
        2. Verify that result contains valid metric fields
        3. Assert original_tokens > 0 and compressed_tokens > 0
        4. Assert compressed_tokens < original_tokens (compression occurred)

        Expected Behavior:
        The encoder should return a dict with valid token counts where the
        compressed version is smaller than the original. All metrics should be
        non-negative integers (for token counts) or floats (for ratio).

        Args:
            sample_simple_doc (str): One-sentence procedure fixture

        Assertions:
        - result is a dict with required fields
        - original_tokens is a positive integer
        - compressed_tokens is a positive integer
        - compressed_tokens < original_tokens (compression occurred)
        - All metric fields are present and have correct types
        """
        result = encode(sample_simple_doc)

        # Verify result structure
        assert result is not None
        assert isinstance(result, dict)

        # Verify required fields exist
        required_fields = [
            "original", "haiku", "original_tokens", "compressed_tokens",
            "compression_ratio", "savings_percent", "token_savings"
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

        # Verify token counts are positive integers
        assert isinstance(result["original_tokens"], int)
        assert isinstance(result["compressed_tokens"], int)
        assert result["original_tokens"] > 0, "original_tokens must be positive"
        assert result["compressed_tokens"] > 0, "compressed_tokens must be positive"

        # Verify compression actually occurred
        assert result["compressed_tokens"] < result["original_tokens"], (
            f"Compression should reduce tokens. "
            f"Original: {result['original_tokens']}, "
            f"Compressed: {result['compressed_tokens']}"
        )

        # Verify ratio is valid
        assert isinstance(result["compression_ratio"], (float, int))
        assert 0.0 <= result["compression_ratio"] <= 1.0, (
            f"compression_ratio must be between 0.0 and 1.0. "
            f"Got: {result['compression_ratio']}"
        )

        # Verify token_savings is consistent
        assert isinstance(result["token_savings"], int)
        expected_savings = result["original_tokens"] - result["compressed_tokens"]
        assert result["token_savings"] == expected_savings, (
            f"token_savings should equal original - compressed. "
            f"Expected: {expected_savings}, Got: {result['token_savings']}"
        )

    def test_metrics_accuracy(self):
        """Test that CompressionValidator calculates metrics correctly.

        Procedure:
        1. Create a CompressionValidator instance
        2. Call calculate_compression_ratio() with sample token counts
        3. Verify the calculation matches expected math: ratio = compressed / original
        4. Test edge cases: equal counts, zero compression, maximum compression

        Expected Behavior:
        The validator should calculate compression ratio as: compressed_tokens / original_tokens
        The result should be a float between 0.0 and 1.0.

        Assertions:
        - Validator correctly computes ratio for typical case
        - Ratio is between 0.0 and 1.0
        - Ratio equals compressed / original (mathematically correct)
        - Edge cases are handled: equal counts (ratio=1.0), full compression (ratio near 0.0)
        """
        validator = CompressionValidator()

        # Test Case 1: Typical compression (50% reduction)
        original_tokens = 100
        compressed_tokens = 50
        ratio = validator.calculate_compression_ratio(original_tokens, compressed_tokens)

        assert isinstance(ratio, (float, int))
        assert 0.0 <= ratio <= 1.0
        expected_ratio = compressed_tokens / original_tokens
        assert abs(ratio - expected_ratio) < 0.001, (
            f"Ratio should be {expected_ratio}, got {ratio}"
        )

        # Test Case 2: No compression (ratio = 1.0)
        ratio_no_compression = validator.calculate_compression_ratio(100, 100)
        assert abs(ratio_no_compression - 1.0) < 0.001, (
            f"No compression should give ratio=1.0, got {ratio_no_compression}"
        )

        # Test Case 3: Extreme compression (90% reduction)
        ratio_extreme = validator.calculate_compression_ratio(1000, 100)
        expected_extreme = 100 / 1000
        assert abs(ratio_extreme - expected_extreme) < 0.001, (
            f"Extreme compression ratio should be {expected_extreme}, got {ratio_extreme}"
        )

        # Test Case 4: Very small documents
        ratio_small = validator.calculate_compression_ratio(10, 5)
        expected_small = 5 / 10
        assert abs(ratio_small - expected_small) < 0.001

        # Test Case 5: Large documents
        ratio_large = validator.calculate_compression_ratio(100000, 40000)
        expected_large = 40000 / 100000
        assert abs(ratio_large - expected_large) < 0.001
```

---

## Coverage Strategy

### Overview

The combined Phase 2 + Phase 3 test suite should achieve ≥80% code coverage across all `src/` modules. Phase 2 provides module-level unit tests; Phase 3 provides integration-level tests. Together, they should cover:

- **src/chunker.py** — mocked tests in Phase 2
- **src/extractor.py** — mocked tests in Phase 2
- **src/synthesizer.py** — Phase 2 unit tests + v0.3.2b `test_action_state_linking`
- **src/validator.py** — Phase 2 unit tests + v0.3.2c `test_metrics_accuracy`
- **src/encoder.py** — Phase 2 integration tests + Phase 3 hypothesis tests

### Running Coverage Locally

#### Command 1: Phase 2 + Phase 3 Tests with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

- Runs all tests in `tests/` (both Phase 2 and Phase 3)
- Measures coverage for `src/` modules
- Generates an HTML report in `htmlcov/index.html`

#### Command 2: Phase 3 Tests Only with Coverage

```bash
pytest tests/test_validation.py --cov=src --cov-report=term
```

- Runs only Phase 3 hypothesis and metrics tests
- Displays coverage summary in terminal
- Useful for understanding Phase 3's contribution to overall coverage

#### Command 3: Check Coverage Threshold

```bash
pytest tests/ --cov=src --cov-fail-under=80
```

- Runs full test suite
- Exits with non-zero code if coverage < 80%
- Useful for CI/CD integration (future)

#### Command 4: Detailed Coverage Report by Module

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

- Shows coverage percentage per module
- Lists line numbers that are not covered
- Useful for identifying gaps

### Expected Coverage by Module

| Module | Phase 2 Coverage | Phase 3 Contribution | Combined Target |
|--------|---|---|---|
| **src/chunker.py** | 75–85% | 0–5% (minimal integration) | ≥80% |
| **src/extractor.py** | 70–80% | 5–10% (via `encode()` calls in hypothesis tests) | ≥80% |
| **src/synthesizer.py** | 80–90% | 5–10% (`test_action_state_linking`) | ≥80% |
| **src/validator.py** | 75–85% | 10–15% (`test_metrics_accuracy`) | ≥85% |
| **src/encoder.py** | 85–95% | 5–10% (hypothesis tests exercise full pipeline) | ≥90% |
| **src/config.py** | N/A | 0% (tested separately) | ≥70% |
| **Overall src/** | 75–85% | 10–20% | **≥80%** |

---

## pytest Command Reference

| Command | What It Does | When to Use |
|---------|---|---|
| `pytest tests/` | Run all tests (Phase 2 + Phase 3) | Full test suite execution |
| `pytest tests/test_validation.py` | Run only v0.3.2 hypothesis + metrics tests | Testing Phase 3 implementation in isolation |
| `pytest tests/test_validation.py -v` | Run with verbose output (test names, pass/fail) | Debugging test failures |
| `pytest tests/test_validation.py::TestPrerequisiteHypothesis` | Run only one test class | Focused testing on a single hypothesis |
| `pytest tests/test_validation.py::TestPrerequisiteHypothesis::test_dependency_extraction` | Run a single test method | Debugging a specific test |
| `pytest tests/ --cov=src` | Run all tests and measure coverage | Coverage assessment |
| `pytest tests/ --cov=src --cov-report=html` | Generate HTML coverage report | Visual inspection of coverage |
| `pytest tests/ --cov=src --cov-fail-under=80` | Fail if coverage < 80% | Enforce coverage threshold |
| `pytest tests/ -k "not validation"` | Run all tests EXCEPT Phase 3 tests | Phase 2 tests only (useful if API key not available) |
| `pytest tests/ --tb=short` | Show short traceback on failure | Concise failure output |
| `pytest tests/ -x` | Stop on first failure | Debugging (don't run remaining tests) |

---

## File Structure

```
haiku-protocol/
├── src/
│   ├── chunker.py
│   ├── extractor.py
│   ├── synthesizer.py
│   ├── validator.py          ← Tested by TestCompressionMetrics.test_metrics_accuracy
│   ├── encoder.py            ← Tested by all Phase 3 tests
│   └── config.py
├── tests/
│   ├── conftest.py           (v0.3.2a — fixtures)
│   ├── test_chunker.py       (Phase 2)
│   ├── test_extractor.py     (Phase 2)
│   ├── test_synthesizer.py   (Phase 2)
│   ├── test_validator.py     (Phase 2)
│   └── test_validation.py    (v0.3.2b/c — 3 hypothesis classes + 1 metrics class = 8 tests)
├── .coverage                 (generated by pytest-cov)
├── htmlcov/                  (generated by pytest-cov for HTML report)
└── .gitignore               (should exclude .coverage, htmlcov/)
```

---

## Implementation Workflow

```
┌────────────────────────────────────────────────────────────┐
│         COMPRESSION METRICS TEST IMPLEMENTATION             │
└────────────────────────────────────────────────────────────┘

  1. OPEN tests/test_validation.py (from v0.3.2b)
     │
  2. APPEND TestCompressionMetrics class
     │
     ├─→ Add docstring
     ├─→ Implement test_simple_compression(sample_simple_doc)
     │   ├─ Call encode()
     │   └─ Assert token counts, ratio, savings are valid
     ├─→ Implement test_metrics_accuracy()
     │   ├─ Create CompressionValidator instance
     │   └─ Test ratio calculation with multiple test cases
     │
  3. VERIFY pytest discovers 8 tests total
     │
     ├─→ Run `pytest tests/test_validation.py --collect-only`
     ├─→ Confirm 8 tests: 2 + 2 + 2 + 2 = 8
     │
  4. VERIFY tests execute
     │
     ├─→ Run `pytest tests/test_validation.py -v`
     ├─→ All 8 tests should pass (requires API key for 6 tests)
     │
  5. RUN COMBINED PHASE 2 + PHASE 3 TEST SUITE
     │
     ├─→ Run `pytest tests/ --cov=src --cov-report=term`
     ├─→ Verify coverage >= 80%
     │
  6. GENERATE DETAILED COVERAGE REPORT
     │
     ├─→ Run `pytest tests/ --cov=src --cov-report=html`
     ├─→ Open htmlcov/index.html in browser to inspect
     │
  7. DOCUMENT COVERAGE RESULTS
     │
     ├─→ Record final coverage percentage
     ├─→ Note any modules below 80% and why
```

---

## Test Requirements

| Test Class | Test Method | Fixture | Test ID | Expected Behavior | Runtime |
|---|---|---|---|---|---|
| `TestCompressionMetrics` | `test_simple_compression` | `sample_simple_doc` | P3.2c.1 | Encode simple doc, verify all metric fields exist and are mathematically valid | ~5–10 sec (LLM call) |
| `TestCompressionMetrics` | `test_metrics_accuracy` | None (internal unit test) | P3.2c.2 | Test CompressionValidator methods with multiple token count scenarios | <1 sec |

**Combined Test Suite:**
- **Total tests:** 8 (6 hypothesis tests from v0.3.2b + 2 metrics tests from v0.3.2c)
- **LLM-dependent tests:** 6 (require API key, ~5–10 sec each)
- **Unit tests:** 2 (no LLM calls, <1 sec each)
- **Total runtime:** ~35–65 seconds with API key

---

## Acceptance Criteria

- [ ] `TestCompressionMetrics` class exists in `tests/test_validation.py` with docstring
- [ ] `TestCompressionMetrics.test_simple_compression()` exists, has docstring, passes
- [ ] `TestCompressionMetrics.test_simple_compression()` correctly asserts metric field types and values
- [ ] `TestCompressionMetrics.test_metrics_accuracy()` exists, has docstring, passes
- [ ] `TestCompressionMetrics.test_metrics_accuracy()` tests multiple test cases (typical, no compression, extreme, small, large)
- [ ] `pytest tests/test_validation.py --collect-only` shows 8 tests total (6 hypothesis + 2 metrics)
- [ ] `pytest tests/test_validation.py -v` passes all 8 tests (requires OPENAI_API_KEY in .env)
- [ ] `pytest tests/ --cov=src --cov-report=term` shows combined coverage ≥80%
- [ ] No import errors when running `pytest tests/test_validation.py`
- [ ] All test methods have function docstrings following commenting standards
- [ ] Coverage report identifies any modules below 80% and documents why
- [ ] `htmlcov/index.html` is generated and viewable (for detailed coverage inspection)

---

## Limitations & Constraints

### Coverage Variability

Coverage percentages vary based on:

- Which modules are imported by Phase 3 tests (some Phase 2 modules may not be exercised)
- Fixtures and test data paths (different inputs may exercise different code branches)
- External dependencies (the `encode()` pipeline may not hit every edge case)

The ≥80% target is **aspirational but achievable**. If certain modules fall below 80%, this indicates gaps in either Phase 2 tests or Phase 3 integration (not necessarily a failure — it's informational).

### LLM Calls Affect Metrics

The 6 hypothesis tests and the `test_simple_compression` test make LLM calls, which means:

- **API cost:** ~$0.01–$0.05 per test run
- **Latency:** Total runtime 35–65 seconds (dominated by LLM latency)
- **Non-determinism:** Coverage can vary slightly across runs due to LLM output variability (different extraction results → different code paths)

### Coverage Does Not Guarantee Correctness

High coverage (≥80%) means the code is *exercised*, not that it's *correct*. Edge cases, boundary conditions, and subtle bugs may still exist. Coverage is a necessary but not sufficient condition for code quality.

### No Load/Performance Testing

The test suite does not measure performance (response time, throughput, memory usage). These aspects are out of scope for Phase 3.

---

## Dependencies

- **pytest** — test framework
- **pytest-cov** — coverage measurement plugin (from `requirements.txt`)
- **src/encoder.py** — `encode()` function (Phase 2)
- **src/validator.py** — `CompressionValidator` class (Phase 2)
- **src/synthesizer.py** — used transitively by `encode()`
- **src/extractor.py** — used transitively by `encode()`
- **src/chunker.py** — used transitively by `encode()`
- **tests/conftest.py** — `sample_simple_doc` fixture (v0.3.2a)
- **OPENAI_API_KEY in `.env`** — runtime dependency for 7 of 8 tests

---

## Outputs (v0.3.2 Complete Deliverable)

After v0.3.2c is complete, the following are finalized:

### 1. Updated conftest.py
```
tests/conftest.py
├── sample_simple_doc fixture
├── sample_medium_doc fixture
├── sample_complex_doc fixture
└── sample_entities fixture
```

### 2. Complete test_validation.py
```
tests/test_validation.py
├── TestPrerequisiteHypothesis (2 tests)
├── TestContextOverflowHypothesis (2 tests)
├── TestSemanticFidelityHypothesis (2 tests)
└── TestCompressionMetrics (2 tests)
```

### 3. Coverage Report
```
Coverage Summary:
- src/chunker.py:     82%
- src/extractor.py:   78%  ← May be below 80%; see Decision Log
- src/synthesizer.py: 85%
- src/validator.py:   87%
- src/encoder.py:     92%
- Overall:            85%   ← Target met
```

### 4. Phase 2 + Phase 3 Integration
- Phase 2 tests (unit tests, mocked) continue to pass
- Phase 3 tests (hypothesis + metrics) add integration coverage
- Combined suite passes with `pytest tests/` exit code 0

---

## Decision Log

### Decision 1: Coverage Target of 80%

**Choice:** ≥80% combined coverage across `src/` modules

**Rationale:**
- 80% is an industry standard for production code.
- Haiku Protocol is a portfolio project, not production software, but 80% is a credible target.
- Achievable with Phase 2 unit tests + Phase 3 integration tests.
- Balances thorough testing with practicality (100% coverage is often diminishing returns).

**Trade-offs:**
- Some modules may stay below 80% if they're edge-case-heavy or primarily tested via mocks.
- This is documented in the coverage report, not considered a failure.

---

### Decision 2: TestCompressionMetrics as a Separate Class

**Choice:** Separate `TestCompressionMetrics` class from hypothesis tests

**Rationale:**
- Hypothesis tests validate thesis claims (semantic properties).
- Metrics tests validate mathematical correctness (numerical properties).
- Separating them clarifies intent and makes the test suite easier to navigate.
- A developer looking for "does compression actually reduce tokens?" finds it in TestCompressionMetrics, not TestContextOverflowHypothesis.

**Trade-offs:**
- Could be merged into a single `TestValidation` class (less organization but simpler).
- Chosen to keep tests organized by intent.

---

**Document Version:** 1.0
**Last Updated:** 2026-02-09
**Author:** Haiku Protocol Project
**Status:** Ready for Implementation
