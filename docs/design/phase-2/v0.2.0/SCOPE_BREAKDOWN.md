# v0.2.0 — Scope Breakdown: Encoder Development

<aside>

**Phase:** 2 — Encoder Development

**Version:** v0.2.0

**Status:** Scope Definition

**Parent:** [v0.0.0 — Project Overview](../../phase-0/v0.0.0-OVERVIEW.md)

**Depends On:** Phase 1 (v0.1.0) — Environment & Tech Stack fully complete

**Purpose:** Define the boundaries, limitations, and high-level feature inventory for every sub-part in v0.2.0, preventing scope creep and undocumented feature invention

</aside>

---

## 1. Document Purpose

This scope breakdown serves as the **authoritative boundary contract** for Phase 2 of the Haiku Protocol project. Every feature described here traces directly to an existing design decision, grammar specification, or architecture diagram from Phase 0 or Phase 1. If a capability is not listed in this document, it is explicitly out of scope for v0.2.0.

This document does **not** contain implementation-level detail. Each sub-part listed below will receive its own dedicated design specification and implementation specification after scope approval. Think of this as the "what and why" — those specs will be the "how."

---

## 2. Phase 2 Mission Statement

> Build a four-stage encoder pipeline that accepts raw Markdown documentation as input and produces compressed CNL (Controlled Natural Language) strings as output, along with quantitative metrics measuring compression quality.

The encoder is the **core value proposition** of the Haiku Protocol. It is the component that demonstrates the thesis: a Technical Writer can design a structured compression grammar that outperforms generic compression algorithms because compression is about restructuring meaning, not just removing syntax.

---

## 3. What Phase 2 IS

Phase 2 builds the **encoder half** of the Haiku Protocol's encode/decode architecture. Specifically, it produces:

- A **document chunker** that segments Markdown by semantic boundaries (headers).
- An **entity extractor** that uses an LLM to identify structured semantic entities from each chunk.
- A **CNL synthesizer** that applies the grammar rules defined in Phase 0 (v0.0.2b/c) to generate Haiku strings.
- A **validator** that calculates token-level compression metrics and checks quality thresholds.
- An **end-to-end pipeline** that chains all four stages together: Markdown in, JSON + metrics out.

---

## 4. What Phase 2 IS NOT

The following capabilities are **explicitly out of scope** for v0.2.0. Each exclusion references the phase where it belongs.

| Excluded Capability | Reason | Deferred To |
|---|---|---|
| **Decoder / Expansion** | The decoder that expands CNL back to human-readable text is a separate pipeline direction. | Phase 3 or later |
| **Web UI / Streamlit Demo** | The interactive demo is a separate deliverable. | v0.3.0 (Phase 3) |
| **RAG Integration / ChromaDB Storage** | Embedding and retrieval of compressed CNL is a downstream use case. | v0.3.0 (Phase 3) |
| **LLMLingua Head-to-Head Benchmark** | Running the actual benchmark comparison requires the encoder to be complete first; the benchmark infrastructure is a Phase 3 deliverable. | v0.3.0 (Phase 3) |
| **Multi-format Input (DOCX, PDF, HTML)** | v0.2.0 accepts Markdown only. Other input formats require preprocessing not covered here. | Future / Out of scope |
| **Disk-based Caching / Persistence** | Extraction caching is in-memory only (per ADR in v0.2.2). Persistent caching is a performance optimization deferred. | Future |
| **Multi-model Support / Model Switching** | The extractor defaults to GPT-4 via LangChain. Support for Anthropic, local models, etc., is not in scope. | Future |
| **CLI Tool / Entry Point Script** | No user-facing CLI is built in Phase 2. Pipeline execution is via Python imports and test harnesses only. | v0.3.0 (Phase 3) |
| **Production Error Recovery / Monitoring** | Error handling is functional (retry, graceful degradation) but not production-grade (no alerting, circuit breakers, or dead-letter queues). | Future |
| **Documentation Finalization** | README.md, ARCHITECTURE.md, and CHANGELOG.md are updated incrementally but not finalized until Phase 4 (v0.4.x). | v0.4.0 (Phase 4) |

---

## 5. Phase 2 Input Assumptions

Phase 2 assumes the following artifacts exist and are functional from earlier phases:

| Artifact | Source Phase | What It Provides |
|---|---|---|
| Python 3.10+ virtual environment | v0.1.1a | Runtime environment with all dependencies installed |
| `requirements.txt` with LangChain, tiktoken, etc. | v0.1.1c | All libraries needed for LLM integration and token counting |
| `.env` with `OPENAI_API_KEY` | v0.1.2a | API credentials for GPT-4 calls in the extractor |
| `src/config.py` | v0.1.2c | Configuration class that loads environment variables |
| `src/` directory with module stubs | v0.1.3c | Placeholder files for `chunker.py`, `extractor.py`, `synthesizer.py`, `validator.py`, `encoder.py` |
| CNL Grammar Specification (12 operators) | v0.0.2b | Operator definitions, syntax rules, naming conventions, and composition rules |
| BNF Formalization | v0.0.2c | Formal grammar productions for parsing/validation |
| Validation Rules | v0.0.2d | Error taxonomy and validation constraints |
| Benchmark Samples (3 documents) | v0.0.3a | `simple.md`, `medium.md`, `complex.md` for testing the pipeline |
| `tests/` directory with `conftest.py` | v0.1.3a | Test infrastructure and shared fixtures |

If any of these artifacts are missing or broken, that is a **Phase 1 deficiency** to be resolved before Phase 2 implementation begins.

---

## 6. Phase 2 Output Deliverables

When Phase 2 is complete, the following artifacts will exist:

| Deliverable | Location | Description |
|---|---|---|
| `src/chunker.py` | Source | Document chunking module with `Chunk` dataclass, `MarkdownChunker`, hierarchy, and merging |
| `src/extractor.py` | Source | LLM-powered entity extraction with `ExtractedEntities`, prompts, retry logic, batch processing |
| `src/synthesizer.py` | Source | CNL string generation with `CNLSynthesizer`, grammar rule application, flow operators |
| `src/validator.py` | Source | Compression metrics with `CompressionValidator`, token counting, threshold checks |
| `src/encoder.py` | Source | End-to-end pipeline orchestrator that chains chunker → extractor → synthesizer → validator |
| `tests/test_chunker.py` | Tests | 100+ unit and integration tests for chunking |
| `tests/test_extractor.py` | Tests | 136+ unit and integration tests for extraction |
| `tests/test_synthesizer.py` | Tests | Unit tests for CNL synthesis |
| `tests/test_validator.py` | Tests | Unit tests for metrics and validation |
| `tests/test_encoder.py` | Tests | End-to-end pipeline integration tests |
| Updated `CHANGELOG.md` | Root | Entries documenting all v0.2.x additions |

---

## 7. Sub-Part Scope Summaries

### 7.1 — v0.2.1: Chunking Module

**Deliverable:** `src/chunker.py`
**Duration:** 105–160 minutes (4 sub-parts)
**Test Count:** 100+ tests

#### What It Does

The chunking module is the **first stage** of the encoder pipeline. It takes a raw Markdown string as input and segments it into a list of `Chunk` objects, where each chunk represents a semantically bounded section of the document.

The primary chunking strategy is **header-based splitting**: the module scans for Markdown headers (`#`, `##`, `###`, etc.) and uses them as natural division points. This respects the author's original semantic structure rather than imposing arbitrary token-count boundaries.

#### Features In Scope

- **Chunk Data Model (v0.2.1a):** A `Chunk` dataclass with 8 fields (`id`, `title`, `level`, `content`, `parent_id`, `children_ids`, `metadata`, `token_count`). Includes serialization to/from dictionary and JSON. A `ChunkingConfig` dataclass for controlling behavior (minimum header level, maximum header level, minimum chunk size for merging). Full type hints and validation.

- **Header-Based Splitting (v0.2.1b):** The core `MarkdownChunker` class that splits documents at header boundaries. Configurable header level range (e.g., split only at `##` and `###`, ignore `#` and `####`+). Code block awareness — headers inside fenced code blocks (`` ``` ``) are not treated as split points. Preamble handling — content before the first header becomes a "preamble" chunk with level 0. A `chunk_document()` convenience function for one-call usage.

- **Hierarchy and Merging (v0.2.1c):** A `resolve_hierarchy()` function that populates `parent_id` and `children_ids` based on header levels, establishing a tree structure. A `merge_small_chunks()` function that combines undersized chunks (below a configurable token threshold) with their nearest sibling to avoid fragments too small for meaningful extraction. A `chunk_with_hierarchy()` function that combines splitting, hierarchy resolution, and metadata enrichment in one call. Metadata enrichment adds word count, character count, and header path (e.g., "Main Title > Section 1 > Subsection 1.1").

- **Integration Testing (v0.2.1d):** End-to-end tests against the three benchmark sample documents from Phase 0 (`simple.md`, `medium.md`, `complex.md`). A chunking performance benchmark report (chunk count, average chunk size, distribution statistics). Validation that no content is lost — concatenating all chunk contents reproduces the original document (minus headers used as split points).

#### Features NOT In Scope

- **Semantic chunking** (splitting by topic similarity rather than headers) — deferred; header-based is sufficient for PoC.
- **Sliding window chunking** (overlapping fixed-size windows) — deferred; not needed for header-structured Markdown.
- **Token-based splitting** (splitting at exact token counts) — deferred; antithetical to semantic boundaries.
- **Non-Markdown input** (HTML, DOCX, plain text) — v0.2.0 is Markdown-only.
- **Recursive sub-chunking** (splitting chunks that are still too large after header-based splitting) — deferred to a future enhancement.

#### Key Design Constraints

1. Chunks are **immutable** once created. No mutation after construction.
2. Chunk IDs follow the format `chunk-NNN` with zero-padded sequential numbering.
3. The chunker is **stateless** — each call to `chunk_document()` is independent.
4. Token counting uses `tiktoken` with the `gpt-4` encoding by default (consistent with v0.2.4's validator).
5. All content is preserved. The chunker does not summarize, compress, or alter text in any way.

---

### 7.2 — v0.2.2: Entity Extraction

**Deliverable:** `src/extractor.py`
**Duration:** 125–180 minutes (5 sub-parts)
**Test Count:** 136+ tests

#### What It Does

The entity extraction module is the **second stage** of the encoder pipeline. It consumes `Chunk` objects from v0.2.1 and uses an LLM (GPT-4 via LangChain) to identify structured semantic entities within each chunk's content. These entities are the "nouns, verbs, and relationships" that carry actual meaning — the raw material the synthesizer (v0.2.3) needs to produce CNL strings.

The extractor maps directly to the five core entity types defined in the Haiku Protocol grammar (v0.0.2b): Actions, States, Commands, Warnings, and Dependencies.

#### Features In Scope

- **Entity Data Model (v0.2.2a):** An `ExtractedEntities` dataclass that holds lists of actions, states, commands, warnings, and dependencies extracted from a single chunk. A `Dependency` dataclass that represents an action-to-state requirement relationship. An `EntityType` enum with 5 values mapped to the grammar's operator IDs (OP-001 through OP-006). Validators that enforce naming conventions from v0.0.2b (PascalCase_With_Underscores for identifiers, lowercase for commands). Serialization to/from dictionary and JSON.

- **Extraction Prompt Engineering (v0.2.2b):** A `PromptVersion` dataclass and `PromptRegistry` for managing versioned extraction prompts. The initial `EXTRACTION_PROMPT_V1` with few-shot examples demonstrating each entity type. The prompt injects the CNL grammar rules from v0.0.2b as context so the LLM understands the target format. Schema validation ensuring the LLM's JSON response matches the expected `ExtractedEntities` structure. Prompt versioning allows future A/B testing without modifying the core extractor code.

- **Extractor Core (v0.2.2c):** The `EntityExtractor` class that wraps LangChain's `ChatOpenAI` integration. JSON parsing with a fallback chain: (1) direct JSON parse, (2) regex extraction from markdown code blocks, (3) code block detection, (4) graceful return of empty entities. Retry logic with configurable attempts (default: 3) for transient API failures. Confidence scoring based on 4 quality factors: entity count, naming convention compliance, dependency consistency, and extraction completeness. Temperature is fixed at 0 for deterministic, reproducible extraction.

- **Batch Processing (v0.2.2d):** An `extract_batch()` function that processes a list of chunks, isolating failures per-chunk so one bad extraction doesn't abort the entire document. An `ExtractionCache` (in-memory only — per ADR) that avoids re-extracting identical content. A `BatchResult` container with per-chunk results, aggregate statistics, and a list of failed chunk IDs. Progress callback support for tracking extraction progress on large documents.

- **Integration Testing (v0.2.2e):** Golden test samples — hand-annotated chunks with expected entity extractions for comparison. Accuracy metrics calculated per entity type: recall, precision, and F1 score. A target accuracy threshold of ≥90% on the golden test set. Pipeline handoff verification: the output of `extract_batch()` is directly consumable by v0.2.3's `CNLSynthesizer`. All LLM calls are mocked in unit tests for determinism, cost control, and CI compatibility.

#### Features NOT In Scope

- **Non-LLM extraction** (regex-based, rule-based, or NER-based extraction) — the extractor uses LLM-only. Rule-based approaches were evaluated in Phase 0 and determined insufficient for the semantic complexity of procedural documentation.
- **Multi-model support** (Anthropic Claude, local LLMs, etc.) — GPT-4 via OpenAI is the only supported model in v0.2.0. The architecture uses LangChain's abstraction layer, making future model additions straightforward, but that work is deferred.
- **Disk-based caching** — extraction results are cached in memory only. Persistent caching (Redis, SQLite, filesystem) is a future optimization.
- **Streaming extraction** — chunks are processed in batch, not streamed. Real-time extraction is a Phase 3 demo concern.
- **Extraction of VERIFY, REF, META, LOOP, NOTE, or SEQ operators** — the v0.2.2 extractor focuses on the **5 core entity types** (Action, State, Command, Warning, Dependency). The remaining 7 operators from v0.0.2b are either compositional (SEQ, LOOP, IF/THEN/ELSE) or metadata-level (META, REF, NOTE) and are handled by the synthesizer's grammar rules rather than extracted as raw entities. This is a deliberate design decision, not an omission.

#### Key Design Constraints

1. **All LLM calls are mocked in tests.** No test may make a real API call. This ensures tests are deterministic, free, and CI-safe.
2. **Graceful degradation.** If the LLM returns garbage, the extractor returns an empty `ExtractedEntities` object with confidence 0.0 rather than raising an exception. The pipeline continues; downstream consumers filter by confidence.
3. **No prompt chaining.** Each chunk is extracted in a single LLM call. Multi-turn extraction or chain-of-thought prompting is deferred.
4. **Prompt is injected, not hardcoded.** The prompt template is loaded from the `PromptRegistry`, making it swappable without code changes.
5. **Entity naming conventions are validated, not enforced.** The extractor checks whether the LLM's output follows PascalCase_With_Underscores naming but does not silently fix violations — it reports them via the confidence score.

---

### 7.3 — v0.2.3: CNL Synthesis Engine

**Deliverable:** `src/synthesizer.py`
**Duration:** 60–90 minutes
**Test Count:** To be determined in design spec

#### What It Does

The CNL synthesis engine is the **third stage** of the encoder pipeline and the place where the Haiku Protocol's core value materializes. It takes the `ExtractedEntities` from v0.2.2 and transforms them into compressed CNL strings by applying the grammar rules formalized in Phase 0 (v0.0.2b operator catalog, v0.0.2c BNF grammar, v0.0.2d validation rules).

This is a **rule-based** transformation, not an LLM call. The synthesizer applies deterministic grammar rules to produce predictable, parseable output.

#### Features In Scope

- **CNLStatement Data Model:** A `CNLStatement` dataclass representing a single CNL statement with an operator, value, optional modifier (e.g., `REQUIRES`), and optional target. Supports serialization.

- **Identifier Formatting:** Functions to convert extracted entity names into CNL-compliant identifiers. Actions and States use `PascalCase_With_Underscores`. Commands use `lowercase_with_hyphens` or literal shell syntax. Formatting rules are derived directly from v0.0.2b's Naming Conventions section.

- **Dependency Graph Construction:** From the list of extracted dependencies, build an ordering that places prerequisite states before the actions that require them. Actions with `REQUIRES` clauses are synthesized as `Action:X REQUIRES State:Y, State:Z`.

- **Statement Assembly:** Combine entities into composite CNL strings using the grammar's composition rules. Sequential statements joined with `;` (SEQ operator, OP-008). Causal/sequential flow indicated with `->` (EXEC operator, OP-004). Warnings appended with cause-consequence format: `WARN:Cause -> Consequence`.

- **Flow-Aware Synthesis:** A `synthesize_with_flow()` method that produces CNL strings with explicit `->` flow operators for procedural sequences (e.g., `Action:X REQUIRES State:Y -> EXEC:cmd`), as opposed to the flat `;`-separated mode.

- **Convenience Function:** A top-level `synthesize_cnl()` function that instantiates the synthesizer and runs synthesis in a single call, with a flag to toggle between flat and flow modes.

#### Features NOT In Scope

- **LLM-assisted synthesis** — the synthesizer is purely rule-based. It does not call the LLM. This is intentional: the grammar rules are deterministic and formalized, so LLM involvement would add cost and non-determinism without benefit.
- **Full operator coverage** — the synthesizer in v0.2.0 handles the 5 core operators that the extractor produces (Action, State, EXEC, WARN, REQUIRES) plus the compositional operators (SEQ via `;`, flow via `->`). It does **not** synthesize IF/THEN/ELSE, LOOP, VERIFY, REF, META, or NOTE operators. These require either more sophisticated extraction (deferred) or document-level context the current chunk-based pipeline doesn't provide.
- **CNL parsing / round-trip validation** — the synthesizer produces CNL strings but does not parse them back. A CNL parser that validates syntactic correctness against the BNF grammar is a valuable future addition but out of scope for v0.2.0.
- **Multi-chunk synthesis** — each chunk's entities are synthesized independently. Cross-chunk synthesis (e.g., recognizing that a state defined in Chunk 1 is required by an action in Chunk 3) is deferred.
- **Output formatting options** — the synthesizer produces a single string format. Alternative output formats (JSON-structured CNL, tree-structured CNL, etc.) are not in scope.

#### Key Design Constraints

1. **Deterministic output.** Given identical input entities, the synthesizer always produces identical CNL strings. No randomness, no LLM calls, no external dependencies.
2. **Grammar compliance.** All output must conform to the operator syntax defined in v0.0.2b. If the synthesizer cannot represent an entity within the grammar, it omits it (with a logged warning) rather than inventing syntax.
3. **Operator precedence.** The synthesizer respects the operator precedence table from v0.0.2b (EXEC at 4, Action/VERIFY/WARN at 5, State at 6, REQUIRES at 7, etc.) when constructing composite statements.
4. **No content invention.** The synthesizer uses only the entities provided by the extractor. It does not infer, interpolate, or fabricate entities. If the extractor missed something, the synthesizer's output will be incomplete — and that is correct behavior. The gap is surfaced in metrics, not hidden by synthesis guesswork.

---

### 7.4 — v0.2.4: Validation & Metrics

**Deliverable:** `src/validator.py`
**Duration:** 30–45 minutes
**Test Count:** To be determined in design spec

#### What It Does

The validation module is the **fourth and final stage** of the encoder pipeline. It takes the original document text and the synthesized CNL output, measures compression quality through token counting, and validates that the compression meets configurable quality thresholds.

This module provides the **quantitative evidence** for the project's thesis: that the Haiku Protocol achieves meaningful compression ratios on procedural documentation.

#### Features In Scope

- **CompressionMetrics Data Model:** A `CompressionMetrics` dataclass containing: `original_text`, `compressed_text`, `original_tokens`, `compressed_tokens`, `compression_ratio` (float between 0 and 1), `token_savings` (integer count), and `savings_percent` (human-readable string like `"56%"`). Supports `to_dict()` serialization and a human-readable `__repr__`.

- **Token Counting:** Uses `tiktoken` with the `gpt-4` encoding (model `cl100k_base`) for accurate, model-specific token counts. Exposed as a standalone `count_tokens()` convenience function for use outside the pipeline.

- **Compression Ratio Calculation:** Calculated as `1 - (compressed_tokens / original_tokens)`. Handles edge cases: zero-length input returns ratio 0.0 (not a division-by-zero error). Returns both the raw ratio (float) and a formatted percentage string.

- **Threshold Validation:** A `validate_compression()` method that checks whether a given `CompressionMetrics` result meets a configurable minimum ratio (default: 0.3, i.e., 30% compression). Returns a structured result with pass/fail status, the actual ratio, the threshold, and a human-readable message.

- **Baseline Comparison:** A `compare_with_baseline()` method that calculates metrics for both the Haiku output and a baseline-compressed version (e.g., from LLMLingua) against the same original text. Returns a comparison dictionary identifying which approach achieved better compression.

- **Convenience Functions:** Top-level `calculate_compression()` and `count_tokens()` functions for one-call usage without instantiating the validator class.

#### Features NOT In Scope

- **Semantic similarity scoring** — measuring whether the CNL preserves the *meaning* of the original (e.g., via cosine similarity of embeddings) is a critical quality metric, but it requires embedding infrastructure (ChromaDB or similar) that belongs to Phase 3. v0.2.4 measures **compression quantity** (how many tokens were saved), not **compression quality** (how much meaning was retained).
- **Automated LLMLingua benchmarking** — the `compare_with_baseline()` method accepts pre-compressed baseline text, but it does not invoke LLMLingua itself. Running LLMLingua requires its own setup and execution, which is a Phase 3 task.
- **Per-chunk metrics** — v0.2.4 calculates metrics on the full document level (original text vs. full CNL output). Per-chunk compression metrics (how much each individual chunk compressed) are a useful diagnostic but deferred.
- **Quality scoring beyond token counting** — information density, readability scores, entity coverage ratios, and other quality metrics are interesting but out of scope. v0.2.4 focuses on the core metric that demonstrates the thesis: token compression ratio.
- **Metric persistence / reporting** — metrics are returned as Python objects. Writing them to files, databases, or dashboard displays is a Phase 3 concern.

#### Key Design Constraints

1. **Tokenizer consistency.** The validator uses the same `tiktoken` encoding (`gpt-4` / `cl100k_base`) everywhere. Mixing tokenizers would produce meaningless comparisons.
2. **No side effects.** The validator is a pure calculation module. It does not modify inputs, call APIs, or write files.
3. **Edge case safety.** Empty strings, `None` values, and strings containing only whitespace are handled gracefully without raising exceptions.
4. **Metric accuracy.** Compression ratio is rounded to 4 decimal places. Savings percentage is rounded to the nearest integer. These precision levels match the benchmark reporting format established in v0.0.3d.

---

## 8. End-to-End Pipeline: `encoder.py`

While each sub-part (v0.2.1–v0.2.4) is designed, tested, and delivered independently, the complete Phase 2 deliverable includes `src/encoder.py` — the orchestrator that chains all four stages together.

### Pipeline Flow

```
encoder.py
│
├── Input: Raw Markdown string
│
├── Stage 1: chunker.chunk_document(markdown)
│   └── Output: List[Chunk]
│
├── Stage 2: extractor.extract_batch(chunks)
│   └── Output: List[ExtractedEntities]
│
├── Stage 3: synthesizer.synthesize_cnl(entities)
│   └── Output: str (CNL)
│
├── Stage 4: validator.calculate_metrics(original, cnl)
│   └── Output: CompressionMetrics
│
└── Output: JSON with CNL string + metrics
```

### Encoder Scope

The encoder orchestrator is intentionally thin. It:

- Chains the four stages in sequence.
- Passes the output of each stage as input to the next.
- Collects and returns the final CNL string alongside compression metrics.
- Provides a single `encode()` function as the public API.

It does **not**:

- Implement its own logic beyond orchestration.
- Add preprocessing, postprocessing, or transformation steps not covered by the four stages.
- Provide CLI, web, or API interfaces (those are Phase 3).
- Handle persistence, logging to files, or external reporting.

---

## 9. Cross-Cutting Constraints

These constraints apply to all sub-parts in Phase 2:

### 9.1 — Testing

- All modules must have unit tests achieving meaningful coverage of their public API.
- All LLM-dependent tests must use mocks. No real API calls in the test suite.
- Tests follow the naming conventions in [Testing Standards](../../standards/testing_standards.md).
- Integration tests against the Phase 0 benchmark samples (`simple.md`, `medium.md`, `complex.md`) are required for v0.2.1d and v0.2.2e.

### 9.2 — Logging

- All modules must use Python's `logging` module, following [Logging Standards](../../standards/logging_standards.md).
- Log levels: `DEBUG` for internal state, `INFO` for pipeline stage transitions, `WARNING` for degraded quality or retries, `ERROR` for failures that skip a chunk.

### 9.3 — Documentation

- All public classes and functions must have docstrings following [Commenting Standards](../../standards/commenting_standards.md).
- Each sub-part's design spec is a prerequisite for implementation (docs-first methodology).
- CHANGELOG.md is updated with each sub-part completion.

### 9.4 — Error Handling

- No module may raise unhandled exceptions during normal operation.
- LLM failures degrade gracefully (empty results with confidence 0.0).
- Validation failures (e.g., compression below threshold) are reported in the return value, not raised as exceptions.

### 9.5 — Data Flow Contracts

Each stage's output must be directly consumable by the next stage's input without transformation:

| From | To | Contract |
|---|---|---|
| `chunker.chunk_document()` | `extractor.extract_batch()` | Returns `List[Chunk]` where each `Chunk.content` is a non-empty string |
| `extractor.extract_batch()` | `synthesizer.synthesize_cnl()` | Returns `List[ExtractedEntities]` (or `BatchResult.results`) with per-chunk entity containers |
| `synthesizer.synthesize_cnl()` | `validator.calculate_metrics()` | Returns a `str` (the CNL output) |
| `validator.calculate_metrics()` | `encoder.encode()` return value | Returns `CompressionMetrics` with `to_dict()` for JSON serialization |

---

## 10. Version Roadmap

```
v0.2.0 — Phase 2: Encoder Development
│
├── v0.2.1 — Chunking Module (105–160 min)
│   ├── v0.2.1a — Chunk Data Model & Interfaces (20–30 min)
│   ├── v0.2.1b — MarkdownChunker Core Implementation (30–45 min)
│   ├── v0.2.1c — Advanced Chunking Features (30–45 min)
│   └── v0.2.1d — Integration Testing & Benchmark Validation (25–35 min)
│
├── v0.2.2 — Entity Extraction (125–180 min)
│   ├── v0.2.2a — Entity Data Model & Interfaces (20–30 min)
│   ├── v0.2.2b — Extraction Prompt Engineering (25–35 min)
│   ├── v0.2.2c — EntityExtractor Core Implementation (30–45 min)
│   ├── v0.2.2d — Batch Extraction & Error Resilience (25–35 min)
│   └── v0.2.2e — Integration Testing & Accuracy Validation (25–35 min)
│
├── v0.2.3 — CNL Synthesis Engine (60–90 min)
│   ├── v0.2.3a — CNL Statement Data Model (15–25 min)
│   ├── v0.2.3b — Identifier Formatting & Synthesis Rules (20–30 min)
│   ├── v0.2.3c — CNL Synthesis Engine Core (20–30 min)
│   └── v0.2.3d — Integration Testing & Pipeline Handoff (15–25 min)
│
├── v0.2.4 — Validation & Metrics (30–45 min)
│   ├── v0.2.4a — Compression Metrics Data Model (10–15 min)
│   ├── v0.2.4b — CompressionValidator Core Implementation (15–20 min)
│   └── v0.2.4c — Integration Testing & Pipeline Completion (10–15 min)
│
└── encoder.py — End-to-End Pipeline Orchestrator
    └── Assembled after all sub-parts complete
```

**Total Estimated Duration:** 320–475 minutes (~5.5–8 hours)

---

## 11. Phase Exit Criteria

Phase 2 is complete when **all** of the following are true:

- [ ] `chunker.py` splits Markdown by headers correctly for all 3 benchmark samples
- [ ] `extractor.py` identifies entities with ≥90% accuracy on the golden test set
- [ ] `synthesizer.py` outputs valid CNL strings conforming to v0.0.2b grammar rules
- [ ] `validator.py` calculates token counts and compression ratios accurately
- [ ] `encoder.py` runs end-to-end: Markdown input → JSON output with CNL string and metrics
- [ ] All unit tests pass (`pytest` exits with code 0)
- [ ] Integration tests pass against `simple.md`, `medium.md`, and `complex.md`
- [ ] No module raises unhandled exceptions during normal operation
- [ ] All public APIs have docstrings
- [ ] CHANGELOG.md updated with v0.2.x entries

---

## 12. Risk Register

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| GPT-4 extraction quality is inconsistent | Entities are incomplete or incorrectly formatted | Medium | Confidence scoring, retry logic, few-shot examples, fallback to empty entities |
| Compression ratio below 30% on benchmark samples | Thesis is not demonstrated | Low | Grammar designed for high compression; ratio below 30% indicates extraction gaps, not grammar failure |
| Token counting discrepancies between dev and production | Metrics are unreliable | Low | Single tokenizer (`tiktoken` with `cl100k_base`) used everywhere |
| Chunking produces fragments too small for extraction | Extractor receives meaningless input | Medium | Configurable minimum chunk size and merge strategy in v0.2.1c |
| Scope creep into decoder, demo, or multi-format support | Phase 2 never completes | Medium | This document. If it's not listed here, it's not in Phase 2. |

---

## 13. Decision Log (Phase 2 Level)

| ID | Decision | Rationale | Status |
|---|---|---|---|
| P2-001 | Markdown-only input for v0.2.0 | Simplifies chunking; other formats require preprocessing layers | Approved |
| P2-002 | GPT-4 as sole extraction model | Best quality; LangChain abstraction allows future model additions | Approved |
| P2-003 | Rule-based synthesis (no LLM) | Grammar is deterministic; LLM adds cost and non-determinism | Approved |
| P2-004 | Token-only metrics (no semantic similarity) | Embedding infrastructure deferred to Phase 3 | Approved |
| P2-005 | In-memory cache only | Disk persistence adds complexity without PoC benefit | Approved |
| P2-006 | Mock all LLM calls in tests | Deterministic, free, CI-compatible testing | Approved |
| P2-007 | 5 core entity types only (no VERIFY, REF, META, etc.) | Compositional/metadata operators handled by synthesis rules, not raw extraction | Approved |
| P2-008 | Per-chunk extraction (no cross-chunk context) | Keeps extraction scoped and testable; cross-chunk is a future enhancement | Approved |

---

## 14. Glossary

| Term | Definition |
|---|---|
| **Chunk** | A semantically bounded segment of a Markdown document, defined by header boundaries. |
| **Entity** | A structured semantic element extracted from a chunk (Action, State, Command, Warning, or Dependency). |
| **CNL** | Controlled Natural Language — the grammar-defined shorthand format that is the output of the encoder. |
| **Compression ratio** | `1 - (compressed_tokens / original_tokens)`. A ratio of 0.5 means 50% of tokens were removed. |
| **Encode** | Transform a human-readable document into compressed CNL. |
| **Golden test** | A hand-annotated test sample with known-correct expected output, used to measure extraction accuracy. |
| **Graceful degradation** | When a component fails (e.g., LLM returns bad JSON), it returns a safe default (empty entities) instead of crashing the pipeline. |
| **Flow operators** | The `->` symbol indicating sequential causation (distinct from `;` which indicates simple sequence). |

---

**Document Version:** 1.0
**Last Updated:** 2026-02-09
**Author:** Haiku Protocol Project
**Status:** Pending Review
