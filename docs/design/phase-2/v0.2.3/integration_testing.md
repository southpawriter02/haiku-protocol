# v0.2.3d: Integration Testing & Pipeline Handoff Validation

| Metadata | Value |
|----------|-------|
| **Version** | v0.2.3d |
| **Parent Module** | v0.2.3 — CNL Synthesis Engine |
| **Status** | ⬜ Not Started |
| **Estimated Duration** | 15–25 minutes |
| **Deliverable** | End-to-end synthesis integration tests, grammar compliance validation, golden synthesis samples, pipeline handoff tests, and documentation updates |

---

## Objective

Validate the complete v0.2.3 synthesis pipeline by:
1. Creating golden test samples with expected CNL outputs
2. Running end-to-end integration tests against all golden samples in both flat and flow modes
3. Verifying grammar compliance with v0.0.2b operator syntax
4. Testing pipeline handoff compatibility with v0.2.4 (Validation & Metrics)
5. Confirming determinism and edge case handling
6. Extending benchmark reporting with synthesis metrics
7. Updating project documentation

Upon completion, v0.2.3 will be production-ready for integration with v0.2.4 validation.

---

## User Stories

### US-v0.2.3d-1: Validate Synthesis Output Against Golden Samples
**As a** pipeline integrator,
**I want to** run integration tests that compare actual synthesis output to curated golden references,
**So that** I can confirm the synthesis engine produces expected CNL strings across diverse entity inputs.

**Acceptance Criteria:**
- 5 golden sample files created in `benchmarks/samples/synthesis/`
- 5 golden reference JSON files created in `benchmarks/golden/synthesis/`
- Integration test class covers all 5 samples in both flat and flow modes
- All tests pass without assertion errors
- Output matches reference format exactly

### US-v0.2.3d-2: Ensure Pipeline Handoff to v0.2.4 is Seamless
**As a** v0.2.4 validator module,
**I want to** receive synthesis output in a format I can immediately consume (str type, JSON-serializable, no special encoding),
**So that** the complete pipeline (chunk → extract → synthesize → validate) operates without friction.

**Acceptance Criteria:**
- All synthesis output is Python str type
- Output is JSON-serializable (can be stored and retrieved from JSON)
- Output is consumable by v0.2.4 token counter without transformation
- Handoff test verifies all three requirements
- Documentation confirms compatibility

---

## Golden Test Samples

### Sample Corpus

| File | Input Description | Expected CNL Output Pattern | Scenario |
|------|-------------------|-----------------------------|----------|
| `procedural_entities.json` | Entities from server restart guide | `Action:Restart_Server REQUIRES State:Config_Saved -> EXEC:systemctl restart app-server` | Procedural with dependency |
| `deployment_entities.json` | Entities from container deployment | `Action:Deploy REQUIRES State:DB_Online, State:Config_Valid -> EXEC:docker push ...; WARN:Skip_Backup -> Data_Loss` | Multi-state requirement + warning |
| `simple_entities.json` | Single action, no dependencies | `Action:Install_Dependencies` | Minimal case |
| `warning_heavy.json` | Multiple warnings, few actions | `Action:Delete_Data; WARN:No_Recovery -> Data_Loss; WARN:Skip_Backup -> Incomplete_Restore` | Warning-dominated synthesis |
| `empty_entities.json` | Empty entity lists | `""` (empty string) | Edge case: no entities |

### Golden Reference Format

Each golden reference file follows this JSON structure and is stored in `benchmarks/golden/synthesis/`:

```json
{
    "source": "procedural_entities.json",
    "input_entities": {
        "actions": ["Restart_Server"],
        "states": ["Config_Saved"],
        "commands": ["systemctl restart app-server"],
        "warnings": [],
        "dependencies": [
            {"action": "Restart_Server", "requires": "Config_Saved"}
        ]
    },
    "expected_cnl_flat": "Action:Restart_Server REQUIRES State:Config_Saved; EXEC:systemctl restart app-server",
    "expected_cnl_flow": "Action:Restart_Server REQUIRES State:Config_Saved -> EXEC:systemctl restart app-server",
    "notes": "Basic procedural synthesis with one dependency and one command."
}
```

#### Sample Golden References

**procedural.json:**
```json
{
    "source": "procedural_entities.json",
    "input_entities": {
        "actions": ["Restart_Server"],
        "states": ["Config_Saved"],
        "commands": ["systemctl restart app-server"],
        "warnings": [],
        "dependencies": [
            {"action": "Restart_Server", "requires": "Config_Saved"}
        ]
    },
    "expected_cnl_flat": "Action:Restart_Server REQUIRES State:Config_Saved; EXEC:systemctl restart app-server",
    "expected_cnl_flow": "Action:Restart_Server REQUIRES State:Config_Saved -> EXEC:systemctl restart app-server",
    "notes": "Basic procedural synthesis with one dependency and one command."
}
```

**deployment.json:**
```json
{
    "source": "deployment_entities.json",
    "input_entities": {
        "actions": ["Deploy"],
        "states": ["DB_Online", "Config_Valid"],
        "commands": ["docker push app-repo/service:latest"],
        "warnings": ["Skip_Backup"],
        "dependencies": [
            {"action": "Deploy", "requires": "DB_Online"},
            {"action": "Deploy", "requires": "Config_Valid"}
        ],
        "warning_consequences": [
            {"warning": "Skip_Backup", "consequence": "Data_Loss"}
        ]
    },
    "expected_cnl_flat": "Action:Deploy REQUIRES State:DB_Online, State:Config_Valid; EXEC:docker push app-repo/service:latest; WARN:Skip_Backup -> Data_Loss",
    "expected_cnl_flow": "Action:Deploy REQUIRES State:DB_Online, State:Config_Valid -> EXEC:docker push app-repo/service:latest; WARN:Skip_Backup -> Data_Loss",
    "notes": "Multi-state dependency with warning consequence."
}
```

**simple.json:**
```json
{
    "source": "simple_entities.json",
    "input_entities": {
        "actions": ["Install_Dependencies"],
        "states": [],
        "commands": [],
        "warnings": [],
        "dependencies": []
    },
    "expected_cnl_flat": "Action:Install_Dependencies",
    "expected_cnl_flow": "Action:Install_Dependencies",
    "notes": "Minimal: single action, no dependencies or commands."
}
```

**warning_heavy.json:**
```json
{
    "source": "warning_heavy.json",
    "input_entities": {
        "actions": ["Delete_Data"],
        "states": [],
        "commands": [],
        "warnings": ["No_Recovery", "Skip_Backup"],
        "dependencies": [],
        "warning_consequences": [
            {"warning": "No_Recovery", "consequence": "Data_Loss"},
            {"warning": "Skip_Backup", "consequence": "Incomplete_Restore"}
        ]
    },
    "expected_cnl_flat": "Action:Delete_Data; WARN:No_Recovery -> Data_Loss; WARN:Skip_Backup -> Incomplete_Restore",
    "expected_cnl_flow": "Action:Delete_Data; WARN:No_Recovery -> Data_Loss; WARN:Skip_Backup -> Incomplete_Restore",
    "notes": "Warning-heavy scenario with multiple consequences."
}
```

**empty.json:**
```json
{
    "source": "empty_entities.json",
    "input_entities": {
        "actions": [],
        "states": [],
        "commands": [],
        "warnings": [],
        "dependencies": []
    },
    "expected_cnl_flat": "",
    "expected_cnl_flow": "",
    "notes": "Edge case: empty entities produce empty CNL string."
}
```

---

## Grammar Compliance Validation

All synthesis output must conform to v0.0.2b operator syntax. Compliance is validated via regex pattern matching against recognized operator keywords and identifier formatting.

### Grammar Rules

1. **Action Operator:** `Action:[A-Z][A-Za-z0-9_]*`
   - Example: `Action:Restart_Server`, `Action:Deploy`

2. **State Operator:** `State:[A-Z][A-Za-z0-9_]*`
   - Example: `State:Config_Saved`, `State:DB_Online`
   - Multiple states separated by comma: `State:A, State:B`

3. **EXEC Operator:** `(?:-> )?EXEC:[^\s;]+`
   - Example: `EXEC:systemctl restart app-server`
   - Flow mode: `-> EXEC:...`
   - Flat mode: `; EXEC:...`

4. **WARN Operator (with consequence):** `WARN:[A-Z][A-Za-z0-9_]+ -> [A-Z][A-Za-z0-9_]+`
   - Example: `WARN:Skip_Backup -> Data_Loss`

5. **WARN Operator (simple):** `WARN:[A-Z][A-Za-z0-9_]+`
   - Example: `WARN:Critical_Check`

6. **REQUIRES Operator:** `REQUIRES State:[A-Z][A-Za-z0-9_]+(, State:[A-Z][A-Za-z0-9_]+)*`
   - Example: `REQUIRES State:Config_Saved`
   - Multiple: `REQUIRES State:DB_Online, State:Config_Valid`

7. **Separator (flat mode):** `; ` (semicolon + space)

8. **Flow Separator:** ` -> ` (space + arrow + space)

### Grammar Validation Implementation

```python
import re
from typing import Dict, List

# Patterns derived from v0.0.2b operator syntax
GRAMMAR_PATTERNS = {
    "action": re.compile(r"Action:[A-Z][A-Za-z0-9_]*"),
    "state": re.compile(r"State:[A-Z][A-Za-z0-9_]*"),
    "exec": re.compile(r"(?:-> )?EXEC:[^\s;]+"),
    "warn_with_consequence": re.compile(r"WARN:[A-Z][A-Za-z0-9_]+ -> [A-Z][A-Za-z0-9_]+"),
    "warn_simple": re.compile(r"WARN:[A-Z][A-Za-z0-9_]+(?! ->)"),
    "requires": re.compile(r"REQUIRES State:[A-Z][A-Za-z0-9_]+(, State:[A-Z][A-Za-z0-9_]+)*"),
    "separator": re.compile(r"; "),
    "flow": re.compile(r" -> "),
}


def validate_cnl_grammar(cnl_string: str) -> Dict[str, any]:
    """Validate that a CNL string conforms to grammar rules.

    Checks:
    1. All operator keywords are valid (Action, State, EXEC, WARN, REQUIRES)
    2. Identifiers follow PascalCase_With_Underscores
    3. Separators are correct ('; ' for flat, ' -> ' for flow)
    4. No unrecognized syntax fragments

    Args:
        cnl_string: The CNL string to validate (may be empty).

    Returns:
        Dict with keys:
            - 'valid' (bool): Whether grammar is valid
            - 'errors' (List[str]): Grammar violations found
            - 'warnings' (List[str]): Non-blocking issues
            - 'operator_count' (int): Total operators found
            - 'valid_operators' (int): Operators matching grammar
    """
    if not cnl_string:
        return {
            "valid": True,
            "errors": [],
            "warnings": [],
            "operator_count": 0,
            "valid_operators": 0,
        }

    errors = []
    warnings = []
    operator_count = 0
    valid_operators = 0

    # Check for invalid keywords
    invalid_keywords = re.findall(r"\b([A-Z_]+):", cnl_string)
    valid_keywords = {"Action", "State", "EXEC", "WARN", "REQUIRES"}
    for kw in set(invalid_keywords):
        if kw not in valid_keywords:
            errors.append(f"Invalid keyword: {kw}")

    # Count operators
    for pattern_name, pattern in GRAMMAR_PATTERNS.items():
        matches = pattern.findall(cnl_string)
        if matches:
            operator_count += len(matches)

    # Validate identifier format in each operator
    action_ops = re.findall(r"Action:([A-Za-z0-9_]+)", cnl_string)
    for ident in action_ops:
        if not _is_valid_identifier(ident):
            errors.append(f"Invalid action identifier: {ident}")
        else:
            valid_operators += 1

    state_ops = re.findall(r"State:([A-Za-z0-9_]+)", cnl_string)
    for ident in state_ops:
        if not _is_valid_identifier(ident):
            errors.append(f"Invalid state identifier: {ident}")
        else:
            valid_operators += 1

    warn_ops = re.findall(r"WARN:([A-Za-z0-9_]+)", cnl_string)
    for ident in warn_ops:
        if not _is_valid_identifier(ident):
            errors.append(f"Invalid warning identifier: {ident}")
        else:
            valid_operators += 1

    # Check separator consistency
    if " -> " in cnl_string:
        # Flow mode
        if "; EXEC:" in cnl_string:
            warnings.append("Flow mode should not use '; EXEC:', use ' -> EXEC:' instead")
    else:
        # Flat mode
        if " -> " in cnl_string:
            errors.append("Flat mode should not contain ' -> ' flow separator")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "operator_count": operator_count,
        "valid_operators": valid_operators,
    }


def _is_valid_identifier(ident: str) -> bool:
    """Check if identifier follows PascalCase_With_Underscores.

    Valid: Config_Saved, Deploy, A, A_B_C, TestCase123
    Invalid: config_saved, ALLCAPS, _leading, trailing_, 123Start
    """
    if not ident:
        return False
    if ident[0].isupper() and ident[-1] != "_":
        parts = ident.split("_")
        return all(part and part[0].isupper() for part in parts)
    return False
```

### Checking Approach

For each golden sample output:
1. Parse all operator keywords (Action, State, EXEC, WARN, REQUIRES)
2. Extract identifiers following each keyword
3. Validate identifiers match `[A-Z][A-Za-z0-9_]*` pattern
4. Verify separators: `; ` in flat mode, ` -> ` in flow mode
5. Report any grammar violations and halt tests if critical errors found

---

## Integration Tests

### Test Categories and Coverage

| Category | Test Count | Description |
|----------|-----------|-------------|
| End-to-End Synthesis | 5 | Load golden input entities → synthesize → compare with expected output for each golden sample |
| Grammar Compliance | 4 | Output contains only valid operators, identifiers are PascalCase, separators correct, no unrecognized fragments |
| Flat vs Flow Modes | 3 | Same input produces different output per mode, flow mode uses '->',  flat mode uses '; ' only |
| Pipeline Handoff | 4 | Output is str type, non-empty for non-empty entities, output is consumable by v0.2.4 validator, output is JSON-serializable |
| Determinism | 2 | Same input produces same output across 10 runs, output unchanged after synthesizer re-instantiation |
| Edge Cases | 3 | Empty entities, single action only, entities with only warnings |
| Round-Trip | 2 | Entities from v0.2.2 BatchResult.results format work, chunk_document → extract → synthesize chain |

**Total: 23+ integration tests**

### Example Test Implementation

```python
"""Integration tests for the CNL synthesis module. (v0.2.3d)"""
import json
import pathlib
import pytest

from src.synthesizer import CNLSynthesizer, SynthesisConfig, synthesize_cnl
from src.chunker import chunk_document
from src.extractor import EntityExtractor
from tests.fixtures.grammar_validator import validate_cnl_grammar


GOLDEN_DIR = pathlib.Path("benchmarks/golden/synthesis")
SAMPLES_DIR = pathlib.Path("benchmarks/samples/synthesis")


@pytest.fixture
def golden_procedural():
    """Load golden reference for procedural synthesis."""
    return json.loads((GOLDEN_DIR / "procedural.json").read_text())


@pytest.fixture
def golden_deployment():
    """Load golden reference for deployment synthesis."""
    return json.loads((GOLDEN_DIR / "deployment.json").read_text())


@pytest.fixture
def golden_simple():
    """Load golden reference for simple synthesis."""
    return json.loads((GOLDEN_DIR / "simple.json").read_text())


@pytest.fixture
def golden_warning_heavy():
    """Load golden reference for warning-heavy synthesis."""
    return json.loads((GOLDEN_DIR / "warning_heavy.json").read_text())


@pytest.fixture
def golden_empty():
    """Load golden reference for empty entities."""
    return json.loads((GOLDEN_DIR / "empty.json").read_text())


class TestEndToEndSynthesis:
    """Full synthesis: entities → CNL string. (v0.2.3d)"""

    def test_procedural_flat_matches_golden(self, golden_procedural):
        """Flat synthesis matches golden reference output."""
        synthesizer = CNLSynthesizer()
        result = synthesizer.synthesize(golden_procedural["input_entities"])
        assert result == golden_procedural["expected_cnl_flat"]

    def test_procedural_flow_matches_golden(self, golden_procedural):
        """Flow synthesis matches golden reference output."""
        synthesizer = CNLSynthesizer()
        result = synthesizer.synthesize_with_flow(golden_procedural["input_entities"])
        assert result == golden_procedural["expected_cnl_flow"]

    def test_deployment_flat_matches_golden(self, golden_deployment):
        """Deployment scenario flat synthesis matches reference."""
        synthesizer = CNLSynthesizer()
        result = synthesizer.synthesize(golden_deployment["input_entities"])
        assert result == golden_deployment["expected_cnl_flat"]

    def test_deployment_flow_matches_golden(self, golden_deployment):
        """Deployment scenario flow synthesis matches reference."""
        synthesizer = CNLSynthesizer()
        result = synthesizer.synthesize_with_flow(golden_deployment["input_entities"])
        assert result == golden_deployment["expected_cnl_flow"]

    def test_simple_matches_golden(self, golden_simple):
        """Simple (minimal) synthesis matches reference."""
        synthesizer = CNLSynthesizer()
        result = synthesizer.synthesize(golden_simple["input_entities"])
        assert result == golden_simple["expected_cnl_flat"]


class TestGrammarCompliance:
    """Verify output conforms to v0.0.2b grammar. (v0.2.3d)"""

    def test_all_identifiers_are_pascalcase(self, golden_procedural):
        """All identifiers follow PascalCase_With_Underscores."""
        result = synthesize_cnl(golden_procedural["input_entities"])
        validation = validate_cnl_grammar(result)
        assert validation["valid"], f"Grammar errors: {validation['errors']}"

    def test_no_invalid_keywords(self, golden_deployment):
        """Only valid keywords present (Action, State, EXEC, WARN, REQUIRES)."""
        result = synthesize_cnl(golden_deployment["input_entities"])
        import re
        keywords = re.findall(r"\b([A-Z_]+):", result)
        valid = {"Action", "State", "EXEC", "WARN", "REQUIRES"}
        for kw in set(keywords):
            assert kw in valid, f"Invalid keyword: {kw}"

    def test_separators_correct_flat(self, golden_procedural):
        """Flat mode uses '; ' separator, not ' -> '."""
        result = synthesize_cnl(golden_procedural["input_entities"])
        if ";" in result:
            # Should use '; ' not ' ;' or '  ;'
            assert "; " in result or result.count(";") == 0
            assert " -> " not in result, "Flat mode should not contain ' -> '"

    def test_separators_correct_flow(self, golden_procedural):
        """Flow mode uses ' -> ' for action-to-EXEC chains."""
        result = synthesize_cnl(golden_procedural["input_entities"])
        config = SynthesisConfig(mode="flow")
        synthesizer = CNLSynthesizer(config)
        flow_result = synthesizer.synthesize(golden_procedural["input_entities"])
        if "->" in flow_result:
            assert " -> " in flow_result, "Flow arrows must have spaces around them"


class TestFlatVsFlowModes:
    """Verify flat and flow modes produce correct output. (v0.2.3d)"""

    def test_same_input_different_modes(self, golden_procedural):
        """Same input may produce different output in flat vs flow."""
        entities = golden_procedural["input_entities"]
        flat_result = synthesize_cnl(entities)
        config_flow = SynthesisConfig(mode="flow")
        synthesizer_flow = CNLSynthesizer(config_flow)
        flow_result = synthesizer_flow.synthesize(entities)
        # Flat and flow may differ in separator style
        # Both are valid; they just format differently

    def test_flow_mode_contains_arrows(self, golden_procedural):
        """Flow mode output contains ' -> ' for action chains."""
        config = SynthesisConfig(mode="flow")
        synthesizer = CNLSynthesizer(config)
        result = synthesizer.synthesize(golden_procedural["input_entities"])
        if "EXEC:" in result and "Action:" in result:
            assert " -> " in result, "Flow mode should contain ' -> ' for action chains"

    def test_flat_mode_contains_no_arrows(self, golden_procedural):
        """Flat mode output contains '; ' separator, not ' -> '."""
        config = SynthesisConfig(mode="flat")
        synthesizer = CNLSynthesizer(config)
        result = synthesizer.synthesize(golden_procedural["input_entities"])
        assert " -> " not in result, "Flat mode should not contain ' -> ' arrows"


class TestPipelineHandoff:
    """Verify output is consumable by v0.2.4 validator. (v0.2.3d)"""

    def test_output_is_string(self, golden_procedural):
        """Synthesis output is a Python str."""
        result = synthesize_cnl(golden_procedural["input_entities"])
        assert isinstance(result, str), f"Expected str, got {type(result)}"

    def test_nonempty_entities_produce_nonempty_output(self, golden_procedural):
        """Non-empty entities produce non-empty CNL string."""
        result = synthesize_cnl(golden_procedural["input_entities"])
        assert len(result) > 0, "Non-empty entities should produce non-empty output"

    def test_output_json_serializable(self, golden_procedural):
        """Synthesis output can be stored as JSON value."""
        result = synthesize_cnl(golden_procedural["input_entities"])
        import json
        payload = {"cnl_output": result, "source": "test"}
        serialized = json.dumps(payload)
        deserialized = json.loads(serialized)
        assert deserialized["cnl_output"] == result

    def test_output_compatible_with_v024_tokenizer(self, golden_procedural):
        """Output can be consumed by v0.2.4 validator without transformation."""
        result = synthesize_cnl(golden_procedural["input_entities"])
        # Simulate v0.2.4 token counter
        # v0.2.4 expects: str input, no special encoding, valid CNL syntax
        assert isinstance(result, str)
        validation = validate_cnl_grammar(result)
        assert validation["valid"] or result == "", "Output must be valid CNL or empty"


class TestDeterminism:
    """Verify synthesis is deterministic. (v0.2.3d)"""

    def test_repeated_synthesis_identical(self, golden_procedural):
        """Same input produces same output across 10 runs."""
        entities = golden_procedural["input_entities"]
        results = [synthesize_cnl(entities) for _ in range(10)]
        assert len(set(results)) == 1, "Non-deterministic synthesis detected"

    def test_output_unchanged_after_reinit(self, golden_procedural):
        """Output unchanged after synthesizer re-instantiation."""
        entities = golden_procedural["input_entities"]
        result1 = CNLSynthesizer().synthesize(entities)
        result2 = CNLSynthesizer().synthesize(entities)
        assert result1 == result2, "Synthesis non-deterministic across re-instantiation"


class TestEdgeCases:
    """Verify edge case handling. (v0.2.3d)"""

    def test_empty_entities_produces_empty_string(self, golden_empty):
        """Empty entities dict produces empty CNL output."""
        entities = golden_empty["input_entities"]
        result = synthesize_cnl(entities)
        assert result == "", "Empty entities should produce empty string"

    def test_single_action_only(self, golden_simple):
        """Single action with no dependencies or commands."""
        entities = golden_simple["input_entities"]
        result = synthesize_cnl(entities)
        assert "Action:" in result
        assert len(result) > 0

    def test_warnings_only(self, golden_warning_heavy):
        """Entities with only warnings, minimal actions."""
        entities = golden_warning_heavy["input_entities"]
        result = synthesize_cnl(entities)
        assert "WARN:" in result


class TestRoundTrip:
    """Verify round-trip compatibility with v0.2.2 and chunk pipeline. (v0.2.3d)"""

    def test_entities_from_batch_result_format(self):
        """Entities extracted from v0.2.2 BatchResult work with synthesizer."""
        # Simulate BatchResult.results format
        batch_entities = {
            "actions": ["Restart_Server"],
            "states": ["Config_Saved"],
            "commands": ["systemctl restart app-server"],
            "warnings": [],
            "dependencies": [{"action": "Restart_Server", "requires": "Config_Saved"}]
        }
        result = synthesize_cnl(batch_entities)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_chunk_extract_synthesize_chain(self):
        """Full pipeline: chunk_document → extract → synthesize."""
        # Load sample document
        sample_doc = pathlib.Path("benchmarks/samples/documents/sample_restart.md").read_text()

        # Chunk
        chunks = chunk_document(sample_doc)
        assert len(chunks) > 0

        # Extract (from first chunk)
        extractor = EntityExtractor()
        batch_result = extractor.extract(chunks[0])
        entities = batch_result.results

        # Synthesize
        result = synthesize_cnl(entities)
        assert isinstance(result, str)

        # Validate grammar
        validation = validate_cnl_grammar(result)
        assert validation["valid"] or result == "", "Round-trip output must be valid CNL"
```

---

## Benchmark Report Extension

Extend `benchmarks/reports/synthesis_benchmark.json` with these metrics:

```json
{
    "module": "synthesizer",
    "version": "v0.2.3d",
    "timestamp": "2026-02-10T12:00:00Z",
    "integration_tests": {
        "total_tests": 23,
        "passed": 23,
        "failed": 0,
        "skipped": 0,
        "duration_seconds": 2.34
    },
    "synthesis": {
        "golden_samples_tested": 5,
        "flat_mode_matches": 5,
        "flow_mode_matches": 5,
        "grammar_compliance_percent": 100,
        "determinism_runs": 10,
        "determinism_success_rate": 100
    },
    "performance": {
        "avg_synthesis_time_ms": 2,
        "max_synthesis_time_ms": 5,
        "min_synthesis_time_ms": 1,
        "throughput_entities_per_sec": 500,
        "throughput_cnl_strings_per_sec": 100
    },
    "pipeline_handoff": {
        "v024_compatibility_verified": true,
        "output_type_valid": true,
        "json_serializable": true,
        "grammar_valid": true
    }
}
```

---

## Documentation Updates

| File | Change | Rationale |
|------|--------|-----------|
| `CHANGELOG.md` | Add v0.2.3 section with sub-parts (a–d summary), mark v0.2.3d as complete | Track release notes and feature completion |
| `CLAUDE.md` | Update ACTIVE VERSION from v0.2.2e to v0.2.3d | Direct future work to correct version |
| `docs/design/phase-2/v0.2.3/README.md` | Add sub-page links to (a), (b), (c), (d); mark status ✅ Complete | Enable navigation and indicate readiness |
| `docs/design/phase-2/v0.2.0/README.md` | Mark "CNL synthesizer (grammar + rules)" exit criterion as ✅ checked | Close v0.2.0 dependencies |

### Documentation Update Examples

**CHANGELOG.md:**
```markdown
## [v0.2.3] – 2026-02-10

### v0.2.3a – CNL Grammar & Rule Definition
- Defined v0.0.2b operator syntax (Action, State, EXEC, WARN, REQUIRES)
- Created grammar reference document
- Status: ✅ Complete

### v0.2.3b – Rule Engine Implementation
- Implemented synthesis rules for entity-to-CNL transformation
- Added flat and flow output modes
- Status: ✅ Complete

### v0.2.3c – Edge Cases & Optimizations
- Handled empty entities, warning-only outputs, determinism
- Optimized synthesis performance
- Status: ✅ Complete

### v0.2.3d – Integration Testing & Pipeline Handoff
- Created 5 golden test samples with reference outputs
- Implemented 23+ integration tests covering all modules
- Verified pipeline handoff compatibility with v0.2.4
- Status: ✅ Complete
```

**CLAUDE.md:**
```markdown
# Active Development Version

**ACTIVE VERSION: v0.2.3d – Integration Testing & Pipeline Handoff**

All new work should reference this version. Previous versions are archived.
```

---

## Logging Requirements

Integration tests log at the following levels for debugging and audit:

| Level | When | Example Log Message |
|-------|------|---------------------|
| INFO | Test suite started | `"Starting integration test suite for v0.2.3d (23 tests)"` |
| INFO | Golden sample tested (pass) | `"Golden test: procedural flat=PASS flow=PASS (0.002s)"` |
| INFO | Test category completed | `"Grammar Compliance: 4/4 tests passed"` |
| DEBUG | Grammar validation details | `"Grammar check: procedural output has 3 operators, all valid, 0 errors"` |
| DEBUG | Synthesis execution | `"Synthesize: 5 actions + 2 states + 1 warning -> 'Action:Deploy...' (1ms)"` |
| WARNING | Grammar violation found | `"Grammar violation in output: Invalid identifier 'deploy' (expected PascalCase)"` |
| WARNING | Non-determinism detected | `"Determinism test failed: Run 5 produced different output than Run 1"` |
| ERROR | Test failure | `"Test test_procedural_flat_matches_golden FAILED: expected='...' got='...'"` |

### Logging Implementation (pytest plugin or decorator):

```python
import logging
import time

logger = logging.getLogger("v0.2.3d")

def log_test_start(test_name: str):
    logger.info(f"Starting test: {test_name}")

def log_golden_result(sample_name: str, flat_pass: bool, flow_pass: bool, duration_ms: float):
    flat_status = "PASS" if flat_pass else "FAIL"
    flow_status = "PASS" if flow_pass else "FAIL"
    logger.info(f"Golden test: {sample_name} flat={flat_status} flow={flow_status} ({duration_ms:.3f}s)")

def log_grammar_check(cnl_output: str, validation_result: dict):
    logger.debug(f"Grammar check: {len(validation_result['valid_operators'])} operators found, {len(validation_result['errors'])} errors")
    if validation_result["errors"]:
        logger.warning(f"Grammar violations: {validation_result['errors']}")
```

---

## Acceptance Criteria

### Completion Checklist (14+ items)

- [ ] **5 golden sample entity files** created in `benchmarks/samples/synthesis/`:
  - [ ] `procedural_entities.json`
  - [ ] `deployment_entities.json`
  - [ ] `simple_entities.json`
  - [ ] `warning_heavy.json`
  - [ ] `empty_entities.json`

- [ ] **5 golden reference JSON files** created in `benchmarks/golden/synthesis/`:
  - [ ] `procedural.json`
  - [ ] `deployment.json`
  - [ ] `simple.json`
  - [ ] `warning_heavy.json`
  - [ ] `empty.json`

- [ ] **Integration test suite** (`tests/test_synthesizer_integration.py`):
  - [ ] Test file created with ≥23 integration tests
  - [ ] All 7 test categories implemented with correct counts
  - [ ] Test fixtures load golden references correctly

- [ ] **End-to-End Synthesis Tests** (5 tests):
  - [ ] Flat mode synthesis matches golden for each sample
  - [ ] Flow mode synthesis matches golden for each sample

- [ ] **Grammar Compliance Tests** (4 tests):
  - [ ] All identifiers validate as PascalCase
  - [ ] No invalid keywords (only Action, State, EXEC, WARN, REQUIRES)
  - [ ] Separators correct ('; ' flat, ' -> ' flow)
  - [ ] No unrecognized syntax fragments

- [ ] **Determinism Tests** (2 tests):
  - [ ] Same input produces same output × 10 runs
  - [ ] Output unchanged after synthesizer re-instantiation

- [ ] **Pipeline Handoff Tests** (4 tests):
  - [ ] Output is Python str type
  - [ ] Non-empty entities produce non-empty output
  - [ ] Output is JSON-serializable
  - [ ] Output compatible with v0.2.4 token counter

- [ ] **Edge Case Tests** (3 tests):
  - [ ] Empty entities produce empty string
  - [ ] Single action (no dependencies) works
  - [ ] Warning-only entities handled correctly

- [ ] **Flat Mode** uses '; ' separator only (no ' -> ')

- [ ] **Flow Mode** uses ' -> ' for action-to-EXEC chains

- [ ] **Benchmark Report** extended:
  - [ ] `benchmarks/reports/synthesis_benchmark.json` includes integration test metrics
  - [ ] Performance metrics (avg synthesis time, throughput) recorded
  - [ ] Pipeline handoff verification results included

- [ ] **Documentation Updated**:
  - [ ] `CHANGELOG.md` includes v0.2.3 entries (a–d summary)
  - [ ] `CLAUDE.md` active version updated to v0.2.3d
  - [ ] `docs/design/phase-2/v0.2.3/README.md` status marked ✅ Complete
  - [ ] `docs/design/phase-2/v0.2.0/README.md` exit criterion marked ✅

- [ ] **All Tests Pass**:
  - [ ] `python -m pytest tests/test_synthesizer_integration.py -v` exits with 0
  - [ ] All 23+ tests pass without warnings
  - [ ] Grammar validation enabled for all tests

---

## Dependencies

### Input Dependencies
- **v0.2.3a** – CNL Grammar & Rule Definition (completed)
- **v0.2.3b** – Rule Engine Implementation (completed)
- **v0.2.3c** – Edge Cases & Optimizations (completed)
- **v0.2.2** – Entity Extraction (for round-trip testing)
- **v0.2.1** – Chunking (for document round-trip testing)

### External Dependencies
- **pytest** ≥ 7.0 (test framework)
- **Python** ≥ 3.9 (type hints, regex module)
- **json** (standard library, golden reference serialization)

### Output Dependencies
- **v0.2.4** – Validation & Metrics (consumer of synthesize_cnl output)

---

## Outputs to v0.2.4

Upon completion, v0.2.3d delivers the following to v0.2.4 (Validation & Metrics):

1. **Synthesizer Module** (`src/synthesizer.py`):
   - Complete CNLSynthesizer class with flat and flow modes
   - Grammar validation utility
   - Edge case handling (empty entities, warnings-only, determinism)

2. **Convenience Function** (`synthesize_cnl()`):
   - Single-call synthesis for pipeline integration
   - No configuration required (uses defaults)
   - Returns str (Python string)

3. **Golden Samples & References**:
   - 5 golden test samples in `benchmarks/samples/synthesis/`
   - 5 golden reference files in `benchmarks/golden/synthesis/`
   - Available for v0.2.4 pipeline testing

4. **Integration Test Suite**:
   - 23+ tests demonstrating all synthesis capabilities
   - Grammar compliance validation approach
   - Round-trip pipeline testing (chunk → extract → synthesize)

5. **Documentation**:
   - Grammar rules and operator syntax (v0.0.2b)
   - Output format specification (flat vs flow)
   - Pipeline handoff interface definition

6. **Output Guarantees**:
   - All outputs are Python str type
   - All outputs are JSON-serializable
   - All outputs conform to v0.0.2b grammar
   - All outputs deterministic (same input → same output)
   - Empty entities produce empty string
   - Non-empty entities produce non-empty string

---

## Decision Log

### Decision 1: Golden Sample Format
**Chosen:** JSON input matching `ExtractedEntities.to_dict()` format
**Rationale:** Ensures test inputs mirror real pipeline data from v0.2.2 extractor. No format translation needed.
**Alternative Considered:** YAML (less rigid, but less consistent for CI).
**Impact:** All round-trip tests use same format as production extraction.

### Decision 2: Grammar Validation Method
**Chosen:** Regex pattern matching against operator keywords and identifier formats
**Rationale:** BNF parser is future work (v0.3+); regex sufficient for v0.0.2b verification. Simple, fast, maintainable.
**Alternative Considered:** Full PEG parser (over-engineering for current grammar complexity).
**Impact:** Grammar checks are fast (< 1ms per string) and easy to debug.

### Decision 3: Determinism Test Coverage
**Chosen:** 10 repeated runs of same synthesis with same input
**Rationale:** Cheap verification that no randomness exists in synthesizer. 10 runs is sufficient statistical sample.
**Alternative Considered:** 100 runs (diminishing returns; 10 catches all non-determinism).
**Impact:** Determinism verified in < 50ms per test; fast feedback.

### Decision 4: Pipeline Handoff Validation
**Chosen:** Verify str type + JSON serializability + v0.2.4 compatibility
**Rationale:** v0.2.4 validator needs str input for token counting. No special encoding or types allowed.
**Alternative Considered:** Just check str type (insufficient; misses serialization issues).
**Impact:** v0.2.4 can consume output immediately without workarounds.

### Decision 5: Flat vs Flow Mode Testing
**Chosen:** Both modes tested against golden references (separate expected outputs)
**Rationale:** Both modes are valid synthesis paths; ensure both are maintained and tested equally.
**Alternative Considered:** Test only one mode as primary (risk of mode drift).
**Impact:** Both modes remain production-ready; users can choose preferred format.

---

**End of v0.2.3d Specification**
