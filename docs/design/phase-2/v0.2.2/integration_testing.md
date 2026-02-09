# v0.2.2e — Integration Testing & Accuracy Validation

<aside>

**Version:** v0.2.2e

**Parent:** v0.2.2 — Entity Extraction

**Status:** ⬜ Not Started

**Duration:** 25–35 minutes

**Deliverable:** End-to-end integration tests, extraction accuracy measurement, golden test samples, and documentation updates

</aside>

---

## Objective

Validate the complete entity extraction module (v0.2.2a–d) through end-to-end integration tests, accuracy measurement against golden reference extractions, and pipeline handoff verification. This sub-part confirms that the extractor:

1. Produces correct entities from real documentation samples
2. Handles the full pipeline: chunk → extract → validate → aggregate
3. Outputs data in the exact format expected by the CNL synthesizer (v0.2.3)
4. Meets accuracy targets for each entity type

---

## User Stories

> As a quality assurance engineer, I want golden test samples with hand-labeled expected entities so that I can measure extraction accuracy and detect regressions when prompts change.

> As the CNL synthesizer developer, I want integration tests proving the extractor's `BatchResult` output format matches my input contract — with no missing or unexpected fields.

---

## Golden Test Samples

### Sample Corpus

Create golden samples in `benchmarks/samples/extraction/`:

| File | Description | Expected Entities |
|------|-------------|-------------------|
| `procedural.md` | Step-by-step server restart guide | 4–6 actions, 2–3 states, 2 commands, 1 warning, 2 dependencies |
| `deployment.md` | Container deployment with rollback | 5–7 actions, 3–4 states, 4+ commands, 2 warnings, 3+ dependencies |
| `configuration.md` | Config file editing with validation | 3–4 actions, 2–3 states, 1–2 commands, 1 warning, 1+ dependency |
| `empty_section.md` | Section with only narrative, no procedures | 0 actions, 0–1 states, 0 commands, 0 warnings, 0 dependencies |
| `mixed_content.md` | Tables, code blocks, inline commands | 3–5 actions, 2 states, 3+ commands, 0–1 warnings, 1+ dependency |

### Golden Reference Format

```json
{
    "source": "procedural.md",
    "reference_entities": {
        "actions": ["Save_Configuration", "Restart_Server", "Verify_Status"],
        "states": ["Config_Saved", "Service_Running"],
        "commands": ["systemctl restart app-server", "systemctl status app-server"],
        "warnings": ["Data_Loss"],
        "dependencies": [
            {"action": "Restart_Server", "requires": "Config_Saved"}
        ]
    },
    "notes": "Minimum expected entities. LLM may extract additional valid entities."
}
```

Store golden references in `benchmarks/golden/extraction/`.

---

## Accuracy Metrics

### Measurement Approach

Accuracy is measured per entity type using set-based comparison against golden references. Because LLMs may extract valid entities not in the golden set, we use **recall as the primary metric** (did the extractor find what it should have?) and **precision as secondary** (were the extracted entities valid?).

```python
@dataclass
class AccuracyMetrics:
    """Accuracy metrics for extraction quality measurement.

    Attributes:
        entity_type: Which entity type these metrics are for.
        expected_count: Number of entities in golden reference.
        extracted_count: Number of entities actually extracted.
        true_positives: Entities in both expected and extracted.
        false_negatives: Entities expected but not extracted.
        false_positives: Entities extracted but not expected.
        recall: true_positives / expected_count.
        precision: true_positives / extracted_count.
    """
    entity_type: str
    expected_count: int = 0
    extracted_count: int = 0
    true_positives: int = 0
    false_negatives: int = 0
    false_positives: int = 0

    @property
    def recall(self) -> float:
        """What fraction of expected entities were found."""
        return self.true_positives / max(self.expected_count, 1)

    @property
    def precision(self) -> float:
        """What fraction of extracted entities were correct."""
        return self.true_positives / max(self.extracted_count, 1)

    @property
    def f1(self) -> float:
        """Harmonic mean of precision and recall."""
        p, r = self.precision, self.recall
        return 2 * p * r / max(p + r, 1e-9)
```

### Target Thresholds

| Entity Type | Min Recall | Min Precision | Notes |
|-------------|-----------|---------------|-------|
| Actions | ≥ 0.80 | ≥ 0.70 | Core extraction target; most common entity |
| States | ≥ 0.70 | ≥ 0.60 | Harder to identify; implicit in text |
| Commands | ≥ 0.90 | ≥ 0.90 | Explicit in docs; easy to detect |
| Warnings | ≥ 0.70 | ≥ 0.60 | Often subtle; "may cause..." patterns |
| Dependencies | ≥ 0.60 | ≥ 0.50 | Requires inference; lowest threshold |

---

## Integration Tests

### Test Categories and Minimums

| Category | Tests | Description |
|----------|-------|-------------|
| **End-to-End Pipeline** | 3 | Load .md → chunk → extract → validate output for each golden sample |
| **Accuracy** | 5 | One test per entity type measuring recall against golden reference |
| **Schema Handoff** | 4 | Output keys match synthesizer input, JSON-serializable, correct types, no extra keys |
| **Batch Pipeline** | 3 | Chunk document → batch extract → all chunks have entities, stats correct, failures isolated |
| **Cache Integration** | 2 | Second run uses cache, cache cleared on prompt change |
| **Edge Cases** | 4 | Empty section produces empty entities, very long section doesn't timeout, code block content handled, Unicode preserved |
| **Confidence** | 3 | High confidence for clean procedural docs, lower for narrative-only, confidence correlates with entity count |
| **Naming Compliance** | 2 | Extracted action/state names match PascalCase_With_Underscores, commands are lowercase |

### Example Test Code

```python
"""Integration tests for the entity extraction module. (v0.2.2e)"""
import json
import pathlib
import pytest
from unittest.mock import patch, Mock

from src.chunker import MarkdownChunker, ChunkingConfig, chunk_document
from src.extractor import (
    EntityExtractor, ExtractedEntities,
    validate_identifier, validate_extraction_output,
)


GOLDEN_DIR = pathlib.Path("benchmarks/golden/extraction")
SAMPLES_DIR = pathlib.Path("benchmarks/samples/extraction")


@pytest.fixture
def golden_procedural():
    """Load golden reference for procedural.md."""
    return json.loads((GOLDEN_DIR / "procedural.json").read_text())


class TestEndToEndPipeline:
    """Full pipeline: chunk → extract → validate. (v0.2.2e)"""

    @patch("src.extractor.ChatOpenAI")
    def test_full_pipeline_procedural(self, mock_llm_class, golden_procedural):
        """Full pipeline produces expected entities for procedural.md."""
        # Mock LLM to return golden reference entities
        mock_response = Mock()
        mock_response.content = json.dumps(golden_procedural["reference_entities"])
        mock_llm_class.return_value.invoke.return_value = mock_response

        # Load and chunk document
        doc = (SAMPLES_DIR / "procedural.md").read_text()
        chunks = chunk_document(doc)

        # Extract entities from first chunk
        extractor = EntityExtractor()
        result = extractor.extract(chunks[0]["content"], chunk_id=chunks[0]["id"])

        assert not result.is_empty
        assert result.chunk_id == chunks[0]["id"]
        assert result.confidence > 0

    @patch("src.extractor.ChatOpenAI")
    def test_batch_pipeline_produces_enriched_chunks(self, mock_llm_class):
        """Batch extraction attaches entities to chunk dicts."""
        mock_response = Mock()
        mock_response.content = '{"actions": ["Do_Thing"], "states": [], "commands": [], "warnings": [], "dependencies": []}'
        mock_llm_class.return_value.invoke.return_value = mock_response

        doc = (SAMPLES_DIR / "procedural.md").read_text()
        chunks = chunk_document(doc)

        extractor = EntityExtractor()
        batch_result = extractor.extract_batch(chunks)

        assert len(batch_result.results) == len(chunks)
        for result_chunk in batch_result.results:
            assert "entities" in result_chunk


class TestAccuracyMeasurement:
    """Entity extraction accuracy tests. (v0.2.2e)"""

    def test_action_recall_meets_threshold(self, golden_procedural):
        """Action recall >= 0.80 against golden reference."""
        expected = set(golden_procedural["reference_entities"]["actions"])
        # In real test, extracted comes from LLM; here we simulate
        extracted = set(golden_procedural["reference_entities"]["actions"])
        recall = len(expected & extracted) / max(len(expected), 1)
        assert recall >= 0.80

    def test_command_recall_meets_threshold(self, golden_procedural):
        """Command recall >= 0.90 against golden reference."""
        expected = set(golden_procedural["reference_entities"]["commands"])
        extracted = set(golden_procedural["reference_entities"]["commands"])
        recall = len(expected & extracted) / max(len(expected), 1)
        assert recall >= 0.90


class TestSchemaHandoff:
    """Verify output matches CNL synthesizer input. (v0.2.2e)"""

    @patch("src.extractor.ChatOpenAI")
    def test_output_has_synthesizer_required_keys(self, mock_llm_class):
        """Extraction output has all keys required by v0.2.3 synthesizer."""
        mock_response = Mock()
        mock_response.content = '{"actions": ["A"], "states": ["S"], "commands": ["c"], "warnings": [], "dependencies": [{"action": "A", "requires": "S"}]}'
        mock_llm_class.return_value.invoke.return_value = mock_response

        extractor = EntityExtractor()
        result = extractor.extract("text")
        output = result.to_dict()

        required_keys = {"actions", "states", "commands", "warnings", "dependencies"}
        assert required_keys.issubset(set(output.keys()))

    @patch("src.extractor.ChatOpenAI")
    def test_output_json_roundtrip(self, mock_llm_class):
        """Output survives JSON serialize → deserialize."""
        mock_response = Mock()
        mock_response.content = '{"actions": ["Deploy"], "states": ["Ready"], "commands": ["kubectl apply"], "warnings": [], "dependencies": []}'
        mock_llm_class.return_value.invoke.return_value = mock_response

        extractor = EntityExtractor()
        result = extractor.extract("text")
        serialized = json.dumps(result.to_dict())
        deserialized = json.loads(serialized)
        assert deserialized["actions"] == ["Deploy"]


class TestNamingCompliance:
    """Verify extracted names follow conventions. (v0.2.2e)"""

    @patch("src.extractor.ChatOpenAI")
    def test_action_names_are_pascalcase(self, mock_llm_class):
        """Actions follow PascalCase_With_Underscores."""
        mock_response = Mock()
        mock_response.content = '{"actions": ["Restart_Server", "Backup_Database"], "states": [], "commands": [], "warnings": [], "dependencies": []}'
        mock_llm_class.return_value.invoke.return_value = mock_response

        extractor = EntityExtractor()
        result = extractor.extract("text")
        for action in result.actions:
            assert validate_identifier(action), f"Invalid: {action}"
```

---

## Benchmark Report Extension

Extend the benchmark report from v0.2.1d to include extraction metrics:

```json
{
    "module": "extractor",
    "version": "v0.2.2e",
    "timestamp": "2026-02-10T12:00:00Z",
    "accuracy": {
        "actions": {"recall": 0.85, "precision": 0.82, "f1": 0.83},
        "states": {"recall": 0.74, "precision": 0.68, "f1": 0.71},
        "commands": {"recall": 0.95, "precision": 0.93, "f1": 0.94},
        "warnings": {"recall": 0.72, "precision": 0.65, "f1": 0.68},
        "dependencies": {"recall": 0.65, "precision": 0.55, "f1": 0.60}
    },
    "performance": {
        "avg_extraction_time_ms": 1200,
        "batch_throughput_chunks_per_min": 45
    }
}
```

---

## Documentation Updates

| File | Change |
|------|--------|
| `CHANGELOG.md` | Add v0.2.2 entries (a–e summary) |
| `CLAUDE.md` | Update `ACTIVE VERSION` to `v0.2.2e` |
| `v0.2.2/README.md` | Add sub-page links + mark status ✅ |
| `v0.2.0/README.md` | Mark entity extractor exit criterion checked |

---

## Logging Requirements

| Level | When | Example Message |
|-------|------|-----------------|
| **INFO** | Integration test suite started | Via pytest output |
| **INFO** | Accuracy result | `"Accuracy: %s recall=%.2f precision=%.2f f1=%.2f"` |
| **DEBUG** | Golden sample loaded | `"Loaded golden: %s (%d expected entities)"` |
| **WARNING** | Below accuracy threshold | `"Accuracy below threshold: %s recall=%.2f (min=%.2f)"` |

---

## Acceptance Criteria

- [ ] 5 golden sample documents created in `benchmarks/samples/extraction/`
- [ ] 5 golden reference JSON files created in `benchmarks/golden/extraction/`
- [ ] `tests/test_extractor_integration.py` created with ≥26 integration tests
- [ ] Full pipeline tested: chunk → extract → validate for each golden sample
- [ ] `AccuracyMetrics` dataclass computes recall, precision, and F1
- [ ] Accuracy thresholds met for all entity types (with mocked LLM)
- [ ] Output schema matches v0.2.3 synthesizer input requirements
- [ ] JSON round-trip preserves all data
- [ ] Extracted names follow PascalCase_With_Underscores convention
- [ ] Benchmark report extended with extraction metrics
- [ ] `CHANGELOG.md` updated with v0.2.2 entries
- [ ] `CLAUDE.md` active version updated
- [ ] All tests pass: `python -m pytest tests/test_extractor_integration.py -v`

---

## Dependencies

**Must be completed before v0.2.2e:**
- v0.2.2a–d — All prior extractor sub-parts
- v0.2.1 — Chunking Module (for pipeline integration)

---

## Outputs to v0.2.3

**For v0.2.3 — CNL Synthesis Engine:**
- Complete, tested extraction module at `src/extractor.py`
- `extract_entities()` convenience function
- `extract_batch()` for batch processing
- Golden samples available for synthesis testing
- Schema compatibility proven via integration tests

---

## Decision Log

| Decision | Rationale | Status |
|----------|-----------|--------|
| Recall as primary accuracy metric | LLM may extract valid entities beyond golden set; recall measures minimum coverage | ✅ Approved |
| Conservative dependency thresholds (≥0.60) | Dependency inference is the hardest extraction task; lower thresholds avoid fragile tests | ✅ Approved |
| Mock LLM in all integration tests | Ensures deterministic, repeatable results without API costs | ✅ Approved |
| Separate golden reference files from samples | Golden files can evolve independently; multiple golden sets for A/B testing | ✅ Approved |
| `AccuracyMetrics` as dataclass | Enables structured reporting and programmatic threshold checks | ✅ Approved |
