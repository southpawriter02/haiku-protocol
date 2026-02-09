# v0.2.2 — Entity Extraction

<aside>

**Version:** v0.2.2

**Parent:** v0.2.0 — Encoder Development

**Status:** ⬜ Not Started

**Duration:** 125–180 minutes (across 5 sub-parts)

**Deliverable:** `extractor.py` — LLM-powered entity extraction module

</aside>

---

## Objective

Build a module that uses an LLM (GPT-4 via LangChain) to extract structured semantic entities from document chunks. This is the second stage of the encoder pipeline, consuming `Chunk` objects from v0.2.1 and producing `ExtractedEntities` containers for the CNL synthesizer (v0.2.3).

---

## Sub-Parts

| Version | Name | Duration | Deliverable |
|---------|------|----------|-------------|
| [v0.2.2a](entity_data_model.md) | Entity Data Model & Interfaces | 20–30 min | `ExtractedEntities`, `Dependency`, `EntityType` enum, validators, 31+ tests |
| [v0.2.2b](extraction_prompt_engineering.md) | Extraction Prompt Engineering | 25–35 min | Versioned prompts, few-shot examples, schema validation, 26+ tests |
| [v0.2.2c](extractor_core.md) | EntityExtractor Core Implementation | 30–45 min | LLM integration, JSON parsing fallbacks, retry logic, confidence scoring, 27+ tests |
| [v0.2.2d](batch_extraction.md) | Batch Extraction & Error Resilience | 25–35 min | Batch processing, per-chunk error isolation, caching, progress callbacks, 26+ tests |
| [v0.2.2e](integration_testing.md) | Integration Testing & Accuracy Validation | 25–35 min | Golden test samples, accuracy metrics (recall/precision/F1), pipeline handoff, 26+ tests |

**Total: 136+ tests across all sub-parts**

---

## Entity Types

The extractor identifies five semantic entity types from the Haiku Protocol grammar:

| Entity Type | Operator | Format | Example |
|-------------|----------|--------|---------|
| **Action** | OP-001 `Action:` | PascalCase_With_Underscores | `Restart_Server` |
| **State** | OP-002 `State:` | PascalCase_With_Underscores | `Config_Saved` |
| **Command** | OP-004 `EXEC:` | Lowercase shell syntax | `systemctl restart app` |
| **Warning** | OP-006 `WARN:` | PascalCase_With_Underscores | `Data_Loss` |
| **Dependency** | OP-003 `REQUIRES` | action → state relationship | `Restart REQUIRES Config_Saved` |

---

## Pipeline Position

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENCODER PIPELINE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   v0.2.1 Chunker         v0.2.2 Extractor      v0.2.3 Synth    │
│   ┌─────────────┐        ┌──────────────┐      ┌───────────┐   │
│   │ Raw Markdown │──────▶│ Chunk + LLM  │────▶│ Entities  │   │
│   │ → Chunks     │        │ → Entities   │      │ → CNL     │   │
│   └─────────────┘        └──────────────┘      └───────────┘   │
│                                                                 │
│   Input: str              Input: Chunk.content   Input: Entities│
│   Output: List[Chunk]     Output: Entities       Output: CNL str│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation: `extractor.py`

See individual sub-part specs for detailed code:
- [v0.2.2a — Data Model](entity_data_model.md) — `ExtractedEntities`, `Dependency`, `EntityType`, validators
- [v0.2.2b — Prompt Engineering](extraction_prompt_engineering.md) — `PromptVersion`, `PromptRegistry`, `EXTRACTION_PROMPT_V1`
- [v0.2.2c — Core Extractor](extractor_core.md) — `EntityExtractor`, LLM integration, JSON parsing, confidence
- [v0.2.2d — Batch Processing](batch_extraction.md) — `extract_batch()`, `ExtractionCache`, `BatchResult`
- [v0.2.2e — Integration Tests](integration_testing.md) — Golden samples, accuracy metrics, pipeline handoff

---

## Acceptance Criteria

- [ ] `extractor.py` created in `src/` directory
- [ ] `ExtractedEntities` dataclass with 8 fields and serialization (v0.2.2a)
- [ ] `EntityType` enum with 5 grammar-linked values (v0.2.2a)
- [ ] Versioned prompt templates with few-shot examples (v0.2.2b)
- [ ] `EntityExtractor` class with LLM integration and retry logic (v0.2.2c)
- [ ] JSON parsing fallback chain: direct → regex → code block → empty (v0.2.2c)
- [ ] Confidence scoring based on 4 quality factors (v0.2.2c)
- [ ] `extract_batch()` processes multiple chunks with error isolation (v0.2.2d)
- [ ] `ExtractionCache` avoids re-extracting unchanged content (v0.2.2d)
- [ ] All unit tests pass (v0.2.2a–d: 110+ tests)
- [ ] Integration tests against golden samples (v0.2.2e: 26+ tests)
- [ ] Accuracy thresholds met for all entity types (v0.2.2e)
- [ ] Output schema compatible with v0.2.3 synthesizer input

---

## Decision Log

| Decision | Rationale | Status |
|----------|-----------|--------|
| GPT-4 as default model | Best extraction quality; configurable for cost optimization | ✅ Approved |
| Temperature = 0 | Deterministic extraction for reproducible results | ✅ Approved |
| Prompt versioning | Enables A/B testing and regression tracking | ✅ Approved |
| Graceful degradation (empty entities on failure) | Pipeline continues; caller filters by confidence | ✅ Approved |
| In-memory cache only | Simple; disk persistence deferred to future version | ✅ Approved |
| Mock all LLM calls in tests | Deterministic, cost-free, CI-compatible testing | ✅ Approved |