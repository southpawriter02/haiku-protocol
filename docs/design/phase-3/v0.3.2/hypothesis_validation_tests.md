# v0.3.2b — Hypothesis Validation Tests

<aside>

**Version:** v0.3.2b

**Parent:** v0.3.2 — Test Suite Implementation

**Status:** ⬜ Not Started

**Duration:** 25–35 minutes

**Deliverable:** `tests/test_validation.py` with 3 hypothesis test classes (6 tests total) validating Prerequisite, Context Overflow, and Semantic Fidelity theses

</aside>

---

## Objective

Implement three test classes that directly validate the Haiku Protocol's core thesis claims from the original Technical Design Document (Section 4: "The Semantic Zip Protocol"). These tests are **integration-level and live** — they call the full `encode()` pipeline with real documents and make assertions about the presence and structure of CNL operators in the output. Unlike Phase 2's module-level unit tests (which mock individual functions), v0.3.2b tests prove that the entire encoder pipeline delivers on its stated hypothesis.

---

## User Stories

> As a portfolio reviewer, I want to see concrete test results proving the Haiku Protocol's thesis claims so that I can understand what the encoder actually achieves beyond "it compresses things."

> As a developer, I want to run `pytest tests/test_validation.py` and see all hypothesis tests pass so that I have confidence the encoder meets its design objectives.

---

## Thesis Mapping

This table links each thesis claim from the Technical Design Document to the test that validates it:

| Thesis Name | Test Class | Test Methods | What It Proves | How It Tests |
|---|---|---|---|---|
| **Prerequisite Hypothesis** | `TestPrerequisiteHypothesis` | `test_dependency_extraction`, `test_action_state_linking` | The encoder preserves dependency relationships (State and Action links) from verbose documentation | 1. `test_dependency_extraction`: encodes realistic procedure, asserts `REQUIRES` or `State:` operator presence in haiku output. 2. `test_action_state_linking`: synthesizes CNL from pre-built entities, asserts `REQUIRES` operator correctly links actions to states. |
| **Context Overflow Hypothesis** | `TestContextOverflowHypothesis` | `test_compression_ratio`, `test_information_density` | The encoder achieves meaningful compression (≥40%) while retaining domain-specific information density | 1. `test_compression_ratio`: encodes complex document, asserts `compression_ratio >= 0.4`. 2. `test_information_density`: encodes same document, asserts domain keywords (action, exec, state, backup, migrate) are preserved. |
| **Semantic Fidelity Hypothesis** | `TestSemanticFidelityHypothesis` | `test_command_preservation`, `test_warning_preservation` | The encoder preserves safety-critical and literal information (commands, warnings) that verbose text makes easy to overlook | 1. `test_command_preservation`: encodes procedure with shell commands, asserts `EXEC:` operators contain recognizable command keywords. 2. `test_warning_preservation`: encodes procedure with warnings, asserts `WARN:` operators are present in output. |

---

## Implementation Design

### Test Class 1: `TestPrerequisiteHypothesis`

**Purpose:** Validate that the encoder preserves dependency information (REQUIRES, State operators) that verbose text makes difficult for LLMs to track.

```python
import pytest
from src.encoder import encode
from src.synthesizer import synthesize_cnl


class TestPrerequisiteHypothesis:
    """Test the Prerequisite Hypothesis: encoder preserves dependency relationships.

    The Prerequisite Hypothesis claims that compressed CNL preserves the explicit
    dependency relationships (action REQUIRES state) that are often implicit or
    scattered across verbose documentation.

    Two tests validate this:
    1. Dependency extraction: Real document compression preserves REQUIRES operators
    2. Action-state linking: CNL synthesis correctly generates REQUIRES operators
    """

    def test_dependency_extraction(self, sample_medium_doc):
        """Test that encode() output contains dependency operators (REQUIRES or State:).

        Procedure:
        1. Call encode() with sample_medium_doc (multi-step procedure with prerequisites)
        2. Check that the haiku output contains either "REQUIRES" or "State:" operator

        Expected Behavior:
        The compressed CNL should explicitly link actions to prerequisite states,
        making dependencies visible rather than buried in prose.

        Args:
            sample_medium_doc (str): Multi-step deployment procedure fixture

        Assertions:
        - haiku output is non-empty string
        - haiku contains "REQUIRES" OR haiku contains "State:" (at least one operator)
        """
        result = encode(sample_medium_doc)

        # Verify encode() returned valid output structure
        assert result is not None
        assert "haiku" in result
        assert isinstance(result["haiku"], str)
        assert len(result["haiku"]) > 0

        haiku = result["haiku"].upper()

        # Assert that at least one dependency operator appears
        assert "REQUIRES" in haiku or "STATE:" in haiku, (
            f"Expected REQUIRES or State: operator in compressed output. "
            f"Got: {result['haiku'][:200]}"
        )

    def test_action_state_linking(self, sample_entities):
        """Test that synthesize_cnl() generates REQUIRES operators correctly.

        Procedure:
        1. Call synthesize_cnl() with sample_entities (pre-built entity dict)
        2. Check that the CNL output contains "REQUIRES" operator

        Expected Behavior:
        The CNL synthesis should explicitly include REQUIRES operators that link
        actions to their prerequisite states.

        Args:
            sample_entities (dict): Pre-built entity dictionary with actions, states, dependencies

        Assertions:
        - cnl output is non-empty string
        - cnl contains "REQUIRES" operator (linking action to state)
        """
        cnl = synthesize_cnl(sample_entities)

        # Verify synthesize_cnl() returned valid output
        assert cnl is not None
        assert isinstance(cnl, str)
        assert len(cnl) > 0

        # Assert that REQUIRES operator is present, proving state-action linking
        assert "REQUIRES" in cnl.upper(), (
            f"Expected REQUIRES operator in synthesized CNL. "
            f"Got: {cnl[:200]}"
        )
```

---

### Test Class 2: `TestContextOverflowHypothesis`

**Purpose:** Validate that the encoder achieves significant compression (≥40% token reduction) while preserving domain-specific information.

```python
class TestContextOverflowHypothesis:
    """Test the Context Overflow Hypothesis: encoder achieves high compression with information retention.

    The Context Overflow Hypothesis claims that compressed CNL achieves meaningful
    token reduction (≥40%) while preserving domain-specific concepts that are
    critical for task execution (actions, states, commands, backups, migrations, etc.).

    Two tests validate this:
    1. Compression ratio: Actual compression ratio meets ≥0.4 threshold
    2. Information density: Key domain concepts survive compression
    """

    def test_compression_ratio(self, sample_complex_doc):
        """Test that compression_ratio >= 0.4 on realistic document.

        Procedure:
        1. Call encode() with sample_complex_doc (full database migration guide)
        2. Check that result["compression_ratio"] >= 0.4

        Expected Behavior:
        A realistic, multi-section technical document should compress to at most
        40% of its original token count, demonstrating meaningful compression.

        Args:
            sample_complex_doc (str): Full-length database migration guide fixture

        Assertions:
        - compression_ratio field exists in encode() result
        - compression_ratio is a float between 0.0 and 1.0
        - compression_ratio >= 0.4
        """
        result = encode(sample_complex_doc)

        # Verify result structure
        assert result is not None
        assert "compression_ratio" in result
        assert isinstance(result["compression_ratio"], (float, int))

        ratio = float(result["compression_ratio"])

        # Assert meaningful compression (≥40% reduction = ≤40% of original)
        assert 0.0 <= ratio <= 1.0, (
            f"compression_ratio must be between 0.0 and 1.0. Got: {ratio}"
        )
        assert ratio >= 0.4, (
            f"Expected compression_ratio >= 0.4, got {ratio}. "
            f"Original tokens: {result.get('original_tokens')}, "
            f"Compressed tokens: {result.get('compressed_tokens')}"
        )

    def test_information_density(self, sample_complex_doc):
        """Test that domain-specific keywords survive compression.

        Procedure:
        1. Call encode() with sample_complex_doc
        2. Check that haiku output contains at least one of the key domain concepts:
           "action", "exec", "state", "backup", "migrate"

        Expected Behavior:
        Even at high compression ratios, critical domain vocabulary should survive
        because CNL explicitly names actions, commands, and states.

        Args:
            sample_complex_doc (str): Full-length database migration guide fixture

        Assertions:
        - haiku output is non-empty
        - At least one domain keyword appears in haiku (case-insensitive)
        """
        result = encode(sample_complex_doc)

        # Verify output structure
        assert result is not None
        assert "haiku" in result
        assert isinstance(result["haiku"], str)
        assert len(result["haiku"]) > 0

        haiku_lower = result["haiku"].lower()

        # Define domain-critical keywords from sample_complex_doc
        domain_keywords = ["action", "exec", "state", "backup", "migrate"]

        # Assert that at least one domain keyword appears
        keyword_matches = [kw for kw in domain_keywords if kw in haiku_lower]
        assert len(keyword_matches) > 0, (
            f"Expected at least one domain keyword ({domain_keywords}) in haiku. "
            f"Got: {result['haiku'][:300]}"
        )
```

---

### Test Class 3: `TestSemanticFidelityHypothesis`

**Purpose:** Validate that compression is lossless for safety-critical information — commands and warnings survive encoding.

```python
class TestSemanticFidelityHypothesis:
    """Test the Semantic Fidelity Hypothesis: encoder preserves safety-critical information.

    The Semantic Fidelity Hypothesis claims that compression is lossless for critical
    content: literal commands (shell syntax) and warnings are preserved in the
    compressed output, making them recoverable without consulting the original.

    Two tests validate this:
    1. Command preservation: Shell commands are retained via EXEC: operators
    2. Warning preservation: Safety warnings are retained via WARN: operators
    """

    def test_command_preservation(self, sample_medium_doc):
        """Test that shell commands are preserved as EXEC: operators.

        Procedure:
        1. Call encode() with sample_medium_doc (procedure with shell commands)
        2. If EXEC: appears in haiku, assert it contains recognizable command keywords

        Expected Behavior:
        Literal commands (npm, postgres, etc.) should survive compression as
        EXEC: operators. The keywords "npm", "run", "build", "deploy", or "test"
        should be recognizable in the output.

        Args:
            sample_medium_doc (str): Multi-step procedure with npm commands fixture

        Assertions:
        - haiku is non-empty
        - If EXEC: operator is present, verify command keywords survive
        """
        result = encode(sample_medium_doc)

        # Verify output structure
        assert result is not None
        assert "haiku" in result
        haiku = result["haiku"]
        assert isinstance(haiku, str)
        assert len(haiku) > 0

        # Define command keywords from sample_medium_doc
        command_keywords = ["npm", "build", "deploy", "test", "run"]

        # Check for EXEC operator or recognizable command syntax
        haiku_upper = haiku.upper()

        # If EXEC: operator is present, verify keywords appear
        if "EXEC:" in haiku_upper:
            # Find keywords in the haiku (case-insensitive)
            haiku_lower = haiku.lower()
            keyword_matches = [kw for kw in command_keywords if kw in haiku_lower]

            assert len(keyword_matches) > 0, (
                f"EXEC: operator found but no command keywords ({command_keywords}) detected. "
                f"EXEC content may have been corrupted. Got: {haiku}"
            )
        # If EXEC: is not present, at least some command keyword should appear
        else:
            haiku_lower = haiku.lower()
            keyword_matches = [kw for kw in command_keywords if kw in haiku_lower]
            assert len(keyword_matches) > 0, (
                f"Expected either EXEC: operator or command keywords in haiku. "
                f"Got: {haiku}"
            )

    def test_warning_preservation(self, sample_medium_doc):
        """Test that warnings are preserved as WARN: operators.

        Procedure:
        1. Call encode() with sample_medium_doc (procedure with warnings)
        2. Check that haiku output contains WARN: operator

        Expected Behavior:
        Safety warnings from the original document should be explicitly preserved
        as WARN: operators in the compressed output, ensuring they are not lost
        during compression.

        Args:
            sample_medium_doc (str): Multi-step procedure with warning fixture

        Assertions:
        - haiku is non-empty
        - haiku contains WARN: operator (case-insensitive check)
        """
        result = encode(sample_medium_doc)

        # Verify output structure
        assert result is not None
        assert "haiku" in result
        haiku = result["haiku"]
        assert isinstance(haiku, str)
        assert len(haiku) > 0

        # Assert that WARN: operator is present
        haiku_upper = haiku.upper()
        assert "WARN:" in haiku_upper, (
            f"Expected WARN: operator in compressed output. "
            f"Warnings may have been dropped during compression. "
            f"Got: {haiku}"
        )
```

---

## Assertion Strategy

### Why Assertions Are Conservative (Not Exact Output Matching)

The hypothesis test assertions intentionally avoid exact output matching. Instead, they validate **structural properties** of the CNL output. This design choice reflects the reality of LLM-powered systems:

#### Problem: LLM Non-Determinism

The `encode()` pipeline relies on GPT-4 for entity extraction. Even with `temperature=0`, GPT-4's output is **nearly deterministic but not perfectly deterministic** across multiple identical invocations. This means:

- The exact text of extracted actions may vary ("Save_Config" vs. "Save_Configuration")
- The specific wording in CNL operators may differ ("REQUIRES" vs. "NEEDS")
- Token counts may vary slightly due to tokenizer sensitivity

If tests asserted exact outputs, they would be **flaky** — failing randomly on legitimate, semantically equivalent results.

#### Solution: Structural Assertions

Instead, tests verify that **CNL operators and domain concepts are present**, not that exact strings match. Examples:

- ✗ **Bad:** `assert result["haiku"] == "ACTION: Save_Config REQUIRES Config_Saved STATE"`
- ✓ **Good:** `assert "REQUIRES" in result["haiku"]`

- ✗ **Bad:** `assert result["compression_ratio"] == 0.42`
- ✓ **Good:** `assert result["compression_ratio"] >= 0.4`

#### Rationale

1. **Reflects real-world usage:** A developer using the encoder cares that dependencies are captured, not the exact wording.
2. **Accommodates LLM variability:** `temperature=0` provides consistency, not perfection. Structural checks are robust to minor variations.
3. **Tests the thesis, not the implementation:** The hypothesis test proves the encoder *achieves its claim* (dependencies are preserved), not that it *produces a specific string*.

---

## File Structure

```
haiku-protocol/
├── src/
│   ├── encoder.py          (Phase 2 — provides encode() function)
│   ├── synthesizer.py      (Phase 2 — provides synthesize_cnl() function)
│   └── validator.py        (Phase 2 — provides token counting, compression metrics)
├── tests/
│   ├── conftest.py         (v0.3.2a — fixtures)
│   ├── test_chunker.py     (Phase 2)
│   ├── test_extractor.py   (Phase 2)
│   ├── test_synthesizer.py (Phase 2)
│   ├── test_validator.py   (Phase 2)
│   └── test_validation.py  (v0.3.2b — NEW, 3 hypothesis test classes)
```

---

## Implementation Workflow

```
┌────────────────────────────────────────────────────────────┐
│              HYPOTHESIS TEST IMPLEMENTATION                 │
└────────────────────────────────────────────────────────────┘

  1. CREATE tests/test_validation.py (if not exists)
     │
  2. IMPORT required modules
     │
     ├─→ import pytest
     ├─→ from src.encoder import encode
     ├─→ from src.synthesizer import synthesize_cnl
     │
  3. DEFINE TestPrerequisiteHypothesis class
     │
     ├─→ Add docstring referencing thesis definition
     ├─→ Implement test_dependency_extraction(sample_medium_doc)
     │   ├─ Call encode()
     │   └─ Assert "REQUIRES" or "State:" in haiku
     ├─→ Implement test_action_state_linking(sample_entities)
     │   ├─ Call synthesize_cnl()
     │   └─ Assert "REQUIRES" in cnl
     │
  4. DEFINE TestContextOverflowHypothesis class
     │
     ├─→ Add docstring
     ├─→ Implement test_compression_ratio(sample_complex_doc)
     │   ├─ Call encode()
     │   └─ Assert compression_ratio >= 0.4
     ├─→ Implement test_information_density(sample_complex_doc)
     │   ├─ Call encode()
     │   └─ Assert domain keywords present
     │
  5. DEFINE TestSemanticFidelityHypothesis class
     │
     ├─→ Add docstring
     ├─→ Implement test_command_preservation(sample_medium_doc)
     │   ├─ Call encode()
     │   └─ Assert EXEC: or command keywords present
     ├─→ Implement test_warning_preservation(sample_medium_doc)
     │   ├─ Call encode()
     │   └─ Assert WARN: in haiku
     │
  6. VERIFY test discovery
     │
     ├─→ Run `pytest tests/test_validation.py --collect-only`
     ├─→ Confirm 6 tests are discovered
     │
  7. VERIFY tests execute (REQUIRES VALID OPENAI_API_KEY IN .env)
     │
     ├─→ Run `pytest tests/test_validation.py -v`
     ├─→ Confirm all 6 tests pass
     │
  8. CHECK assertions are conservative (no exact output matching)
```

---

## Test Requirements

| Test Class | Test Method | Fixture | Test ID | Expected Behavior | Runtime |
|---|---|---|---|---|---|
| `TestPrerequisiteHypothesis` | `test_dependency_extraction` | `sample_medium_doc` | P3.2b.1 | Encode procedure, assert "REQUIRES" or "State:" in output | ~5–10 sec (LLM call) |
| `TestPrerequisiteHypothesis` | `test_action_state_linking` | `sample_entities` | P3.2b.2 | Synthesize CNL, assert "REQUIRES" in output | <1 sec (no LLM call) |
| `TestContextOverflowHypothesis` | `test_compression_ratio` | `sample_complex_doc` | P3.2b.3 | Encode complex doc, assert compression_ratio >= 0.4 | ~5–10 sec |
| `TestContextOverflowHypothesis` | `test_information_density` | `sample_complex_doc` | P3.2b.4 | Encode complex doc, assert domain keywords present | ~5–10 sec |
| `TestSemanticFidelityHypothesis` | `test_command_preservation` | `sample_medium_doc` | P3.2b.5 | Encode procedure, assert commands preserved | ~5–10 sec |
| `TestSemanticFidelityHypothesis` | `test_warning_preservation` | `sample_medium_doc` | P3.2b.6 | Encode procedure, assert WARN: in output | ~5–10 sec |

**Total Test Suite Runtime:** ~30–60 seconds (5 tests with LLM calls, 1 test without)

---

## Logging Requirements

**No custom logging is implemented for v0.3.2b.** Test output is handled by pytest.

### pytest Output

All test results are reported via pytest's standard output:

```
tests/test_validation.py::TestPrerequisiteHypothesis::test_dependency_extraction PASSED
tests/test_validation.py::TestPrerequisiteHypothesis::test_action_state_linking PASSED
tests/test_validation.py::TestContextOverflowHypothesis::test_compression_ratio PASSED
tests/test_validation.py::TestContextOverflowHypothesis::test_information_density PASSED
tests/test_validation.py::TestSemanticFidelityHypothesis::test_command_preservation PASSED
tests/test_validation.py::TestSemanticFidelityHypothesis::test_warning_preservation PASSED

======================== 6 passed in 45.32s ========================
```

### Assertion Failure Output

If an assertion fails, pytest displays:

```
AssertionError: Expected REQUIRES or State: operator in compressed output.
Got: [first 200 chars of haiku output]
```

The assertion error message includes:
- What was expected
- What was received (truncated for readability)
- The fixture that was used

No additional logging framework (Python `logging` module, structured JSON logs, etc.) is required.

---

## Acceptance Criteria

- [ ] `tests/test_validation.py` file exists
- [ ] `TestPrerequisiteHypothesis` class exists with docstring
- [ ] `TestPrerequisiteHypothesis.test_dependency_extraction()` exists and runs (fixtures inject `sample_medium_doc`)
- [ ] `TestPrerequisiteHypothesis.test_action_state_linking()` exists and runs (fixtures inject `sample_entities`)
- [ ] `TestContextOverflowHypothesis` class exists with docstring
- [ ] `TestContextOverflowHypothesis.test_compression_ratio()` exists and runs (fixtures inject `sample_complex_doc`)
- [ ] `TestContextOverflowHypothesis.test_information_density()` exists and runs (fixtures inject `sample_complex_doc`)
- [ ] `TestSemanticFidelityHypothesis` class exists with docstring
- [ ] `TestSemanticFidelityHypothesis.test_command_preservation()` exists and runs (fixtures inject `sample_medium_doc`)
- [ ] `TestSemanticFidelityHypothesis.test_warning_preservation()` exists and runs (fixtures inject `sample_medium_doc`)
- [ ] All 6 test methods have docstrings following the project's commenting standards
- [ ] All test methods pass when run with `pytest tests/test_validation.py` (requires valid OPENAI_API_KEY)
- [ ] Assertions are conservative/structural (no exact output matching)
- [ ] No hardcoded test data in test methods (all data comes from conftest.py fixtures)
- [ ] Tests are discoverable by `pytest tests/test_validation.py --collect-only` (shows 6 tests)

---

## Limitations & Constraints

### Live LLM Calls

The hypothesis tests call `encode()`, which invokes GPT-4 for entity extraction. This means:

- **API credential required:** A valid `OPENAI_API_KEY` must be in `.env`.
- **Runtime cost:** Each test with an LLM call costs tokens ($0.01–$0.05 per call).
- **Not CI-safe:** These tests cannot run in a CI environment without hardcoding API credentials (security risk). They are designed for **local execution and portfolio demonstration**.
- **Latency:** 5–10 seconds per test (network roundtrip to OpenAI API).
- **Non-determinism:** Output varies slightly across runs even with `temperature=0`. Assertions account for this.

### LLM Non-Determinism

GPT-4 with `temperature=0` is *nearly* deterministic but not perfectly deterministic. This is why assertions are conservative (e.g., `>= 0.4` not `== 0.42`).

### No Embedding-Based Semantics

The tests do NOT use embedding-based semantic similarity (e.g., cosine similarity between sentence embeddings) to validate fidelity. Instead, they use structural validation (operator presence, keyword presence). This avoids dependency on external embedding infrastructure.

### No Exact Output Matching

Tests never assert `result["haiku"] == "expected string"`. This would fail due to LLM non-determinism and is not meaningful for validating the thesis.

### No Test Data Files

All test data is embedded in fixtures (conftest.py). Test data is not loaded from external Markdown files, JSON, or CSV.

---

## Dependencies

- **pytest** — test framework (from `requirements.txt`)
- **src/encoder.py** — `encode()` function (Phase 2)
- **src/synthesizer.py** — `synthesize_cnl()` function (Phase 2)
- **src/validator.py** — token counting infrastructure (Phase 2, optional for this sub-part)
- **tests/conftest.py** — shared fixtures: `sample_medium_doc`, `sample_complex_doc`, `sample_entities` (v0.3.2a)
- **OPENAI_API_KEY in `.env`** — runtime dependency (required for `test_dependency_extraction`, `test_compression_ratio`, `test_information_density`, `test_command_preservation`, `test_warning_preservation`)

---

## Outputs to Next Sub-Part

After v0.3.2b is complete:

1. **Test classes implemented:** `TestPrerequisiteHypothesis`, `TestContextOverflowHypothesis`, `TestSemanticFidelityHypothesis` are in `tests/test_validation.py`.
2. **6 tests passing:** All hypothesis validation tests pass with a live API key.
3. **Next step (v0.3.2c):** Add `TestCompressionMetrics` class with 2 additional tests to the same file.
4. **Next step (v0.3.2c):** Run combined test suite and verify ≥80% code coverage.

---

## Decision Log

### Decision 1: Live Tests vs. Mocked Tests

**Choice:** Live tests (real LLM calls, not mocked)

**Rationale:**
- The hypothesis tests validate **real-world behavior**, not implementation details.
- Mocking the encoder would test the mock, not the system.
- The thesis claims ("the encoder preserves dependencies") are only meaningful when validated against real LLM output.
- Phase 2's mocked unit tests handle CI-safe deterministic testing. Phase 3 is about proving real capability.

**Trade-offs:**
- Tests require API credentials and cannot run in CI without security concerns.
- Tests are slower (5–10 seconds each due to LLM latency).
- Tests cost money (OpenAI API usage).
- Non-deterministic output requires conservative assertions.

---

### Decision 2: Structural vs. Exact Assertions

**Choice:** Structural assertions (operator presence, keyword presence, ratio thresholds)

**Rationale:**
- LLM output is not deterministic; exact string matching would cause flaky tests.
- Testing the thesis is about validating claims, not exact wording.
- Structural tests are more robust to prompt refinements and model variations.
- A developer using the encoder cares that dependencies are captured, not exact syntax.

**Trade-offs:**
- Assertions are loose and could theoretically pass with inadequate output.
- But this is acceptable because the assertions validate the core thesis claim (dependencies are present), which is the actual requirement.

---

### Decision 3: 0.4 Compression Ratio Threshold Rationale

**Choice:** `compression_ratio >= 0.4` (meaning ≤40% of original token count, i.e., ≥60% compression)

**Rationale:**
- The Haiku Protocol targets "significant compression for limited token budgets."
- A ≥60% reduction is meaningful and demonstrates the thesis claim.
- 0.4 is conservative (doesn't require >90% compression, which could be noisy).
- Based on Phase 2 pilot testing, complex technical documents typically achieve 50–70% compression.

**Trade-offs:**
- Could be tighter (e.g., 0.3 for even better compression) or looser (e.g., 0.5 for stricter validation).
- The 0.4 threshold balances demonstrating meaningful compression with allowing some variance.

---

**Document Version:** 1.0
**Last Updated:** 2026-02-09
**Author:** Haiku Protocol Project
**Status:** Ready for Implementation
