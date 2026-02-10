# v0.3.0 — Scope Breakdown: Demo & Visualization

<aside>

**Phase:** 3 — Demo & Visualization

**Version:** v0.3.0

**Status:** Scope Definition

**Parent:** [v0.0.0 — Project Overview](../../phase-0/v0.0.0-OVERVIEW.md)

**Depends On:** Phase 2 (v0.2.0) — Encoder Development fully complete

**Purpose:** Define the boundaries, limitations, and high-level feature inventory for every sub-part in v0.3.0, preventing scope creep and undocumented feature invention

</aside>

---

## 1. Document Purpose

This scope breakdown serves as the **authoritative boundary contract** for Phase 3 of the Haiku Protocol project. It follows the same structure and conventions as the [v0.2.0 Scope Breakdown](../../phase-2/v0.2.0/SCOPE_BREAKDOWN.md) to maintain consistency across phases.

Every feature described here traces to an existing design document, wireframe, test strategy, or deferred-item reference from Phases 0–2. If a capability is not listed in this document, it is explicitly out of scope for v0.3.0.

This document does **not** contain implementation-level detail. Each sub-part will receive its own dedicated design specification and implementation specification after scope approval. This is the "what and why" — those specs will be the "how."

---

## 2. Phase 3 Mission Statement

> Build an interactive Streamlit web demo that showcases the encoder pipeline from Phase 2, implement a comprehensive hypothesis-validation test suite proving the project's thesis, and run head-to-head benchmark comparisons against Microsoft's LLMLingua.

Phase 2 built the engine. Phase 3 **proves it works and makes it visible.** A compression pipeline that only runs from a Python import is an engineering artifact. A compression pipeline with a live demo, quantified test results, and a published benchmark comparison is a **portfolio piece**.

---

## 3. What Phase 3 IS

Phase 3 wraps the Phase 2 encoder pipeline in three presentation layers:

- A **Streamlit web application** (`app.py`) that provides a visual, interactive interface for compressing documents and viewing metrics in real time.
- A **hypothesis-validation test suite** (`test_validation.py`) that tests the three core hypotheses from the original Technical Design Document (Prerequisite Test, Context Overflow Test, Semantic Fidelity Test), alongside expanded module-level tests and shared test fixtures.
- A **benchmark runner** (`llmlingua_comparison.py`) that compares Haiku Protocol compression against Microsoft's LLMLingua on the same document corpus, producing a structured results report.

Together, these three sub-parts transform the encoder from "code that works" into "code that demonstrably works, with visual proof and quantified evidence."

---

## 4. What Phase 3 IS NOT

The following capabilities are **explicitly out of scope** for v0.3.0. Each exclusion references the phase or milestone where it belongs.

| Excluded Capability | Reason | Deferred To |
|---|---|---|
| **Decoder / Expansion Module** | The v0.2.0 scope breakdown listed the decoder as "Phase 3 or later." After evaluating Phase 3's scope, the decoder is **deferred beyond Phase 3**. Phase 3 focuses on proving the encoder works, not building the reverse pipeline. The Semantic Fidelity Test (v0.3.2) tests expansion via a direct LLM prompt, not a dedicated decoder module. | Future (post-v0.4.0) |
| **RAG Integration / ChromaDB Storage** | The v0.2.0 scope breakdown deferred this to "v0.3.0 (Phase 3)." However, embedding and vector retrieval infrastructure is a downstream application of compressed CNL, not a demonstration of compression itself. Phase 3 demonstrates compression quality through metrics and tests, not through a retrieval pipeline. | Future (post-v0.4.0) |
| **CLI Tool / Entry Point Script** | The v0.2.0 scope breakdown deferred this to "v0.3.0 (Phase 3)." Phase 3 provides the Streamlit demo as the user-facing interface. A standalone CLI (`haiku compress file.md`) is a convenience tool that adds no demonstration value for a portfolio. | Future (post-v0.4.0) |
| **Production Deployment** | The Streamlit app runs locally via `streamlit run`. There is no Docker containerization, cloud deployment (Heroku, AWS, Streamlit Cloud), or CI/CD pipeline. | Future |
| **User Authentication / Multi-user** | The demo is a single-user local application. No login, sessions, or user management. | Future |
| **Multi-format Input in the UI** | The Streamlit demo accepts pasted text (Markdown/plain text). File upload, URL fetching, or drag-and-drop are not in scope. | Future |
| **Semantic Similarity Scoring** | The test suite validates compression ratio and information preservation through structural tests (keyword presence, operator presence). Embedding-based semantic similarity (e.g., cosine similarity of sentence embeddings) requires infrastructure not built in this phase. | Future |
| **Automated Regression Testing / CI** | Tests are run manually via `pytest`. GitHub Actions, pre-commit hooks, and automated test runners are Phase 4 or future concerns. | v0.4.0 or Future |
| **Documentation Finalization** | README, ARCHITECTURE.md, and CHANGELOG.md receive incremental updates but are not finalized until Phase 4 (v0.4.x). | v0.4.0 (Phase 4) |
| **Performance Optimization** | The Streamlit app and benchmark runner are functional, not optimized. No async processing, background workers, caching layers, or response-time targets. | Future |

### Clarification: Items Deferred FROM Phase 2 That Remain Deferred

The v0.2.0 scope breakdown's exclusion table listed several items as "v0.3.0 (Phase 3)." Three of those items — Decoder, RAG/ChromaDB, and CLI — are **not included in Phase 3** despite that earlier reference. The reasoning is documented above and in the Decision Log (Section 13). The v0.2.0 scope breakdown's language was "Phase 3 or later," and "later" is the operative word here. Phase 3's scope is fully consumed by the three sub-parts that actually appear in the v0.3.0 README (Streamlit UI, Test Suite, Benchmark Integration).

---

## 5. Phase 3 Input Assumptions

Phase 3 assumes the following artifacts exist and are functional from earlier phases:

| Artifact | Source Phase | What It Provides |
|---|---|---|
| `src/encoder.py` | v0.2.0 | The `encode()` function that accepts Markdown and returns a dict with `haiku`, `original_tokens`, `compressed_tokens`, `compression_ratio`, `savings_percent`, `token_savings` |
| `src/chunker.py` | v0.2.1 | `chunk_document()` for document segmentation |
| `src/extractor.py` | v0.2.2 | `EntityExtractor` and `extract_batch()` for LLM-powered entity extraction |
| `src/synthesizer.py` | v0.2.3 | `synthesize_cnl()` for CNL string generation |
| `src/validator.py` | v0.2.4 | `CompressionValidator`, `calculate_compression()`, `count_tokens()` for metrics |
| `src/config.py` | v0.1.2c | Configuration class that loads `.env` variables |
| `.env` with `OPENAI_API_KEY` | v0.1.2a | API credentials for live encoding in the demo and LLM-dependent tests |
| `requirements.txt` including `streamlit` | v0.1.1c | Streamlit is already listed as a project dependency |
| Benchmark samples | v0.0.3a | `benchmarks/samples/simple.md`, `medium.md`, `complex.md` |
| Phase 0 test strategy | Semantic Zip Protocol §4 | Three hypothesis tests (Prerequisite, Context Overflow, Semantic Fidelity) |
| Phase 2 unit tests | v0.2.1–v0.2.4 | Existing `tests/test_chunker.py`, `test_extractor.py`, `test_synthesizer.py`, `test_validator.py` |
| `tests/conftest.py` | v0.1.3a / v0.2.x | Shared test fixtures and configuration |

If any of these artifacts are missing or broken, that is a **Phase 2 deficiency** (or earlier) to be resolved before Phase 3 implementation begins.

### Critical Dependency: The `encode()` API Contract

Phase 3 depends heavily on the `encode()` function from `src/encoder.py`. The Streamlit UI, the hypothesis tests, and the benchmark runner all call `encode()` as their primary integration point. The expected return schema is:

```python
{
    "original": str,           # Original input text
    "haiku": str,              # Compressed CNL string
    "original_tokens": int,    # Token count of original
    "compressed_tokens": int,  # Token count of compressed
    "compression_ratio": float, # 0.0 to 1.0
    "savings_percent": str,    # e.g., "56%"
    "token_savings": int       # original_tokens - compressed_tokens
}
```

If this schema changes during Phase 2 implementation, all three Phase 3 sub-parts must be updated accordingly.

---

## 6. Phase 3 Output Deliverables

When Phase 3 is complete, the following artifacts will exist:

| Deliverable | Location | Description |
|---|---|---|
| `src/app.py` | Source | Streamlit web application with input, output, metrics display, sidebar settings, and error handling |
| `tests/conftest.py` | Tests | Updated shared fixtures (simple, medium, complex samples + sample entities) |
| `tests/test_validation.py` | Tests | Hypothesis-validation tests covering the 3 core theses plus compression metrics |
| `benchmarks/llmlingua_comparison.py` | Benchmarks | `BenchmarkRunner` class, `BenchmarkResult` dataclass, report generation |
| `benchmarks/results.json` | Benchmarks | Machine-readable benchmark results (generated by running the benchmark suite) |
| Updated `CHANGELOG.md` | Root | Entries documenting all v0.3.x additions |

---

## 7. Sub-Part Scope Summaries

### 7.1 — v0.3.1: Streamlit UI Development

**Deliverable:** `src/app.py`
**Duration:** 60–90 minutes
**Test Count:** Not applicable (UI component — tested manually via the acceptance criteria checklist, not via `pytest`)

#### What It Does

The Streamlit application is the **visual proof of concept** — the thing a hiring manager, recruiter, or fellow engineer can interact with in under 60 seconds to understand what the Haiku Protocol does. It wraps the `encode()` pipeline in a web interface with a text input, a compress button, a side-by-side before/after comparison, and a metrics dashboard.

The design follows the UI wireframe established in the v0.3.0 README, which defines the layout as: header/tagline, input text area with compress/clear buttons, side-by-side original vs. compressed panels with token counts, and a metrics section with compression ratio visualization.

#### Features In Scope

- **Page Configuration:** Custom page title ("The Haiku Protocol"), icon, and wide layout mode. Custom CSS for header styling, tagline styling, and metric card backgrounds. This is lightweight theming, not a design system.

- **Sidebar:** A settings panel with a model selector dropdown (`gpt-4`, `gpt-3.5-turbo`), a "Show raw CNL" toggle checkbox, an About section with project description and placeholder links (GitHub, Documentation). The model selector is a UI element only — it does not actually switch models in v0.3.0. The extractor uses whatever model `src/config.py` provides. The selector is scaffolding for a future feature and serves as a UI demonstration of configurability.

- **Input Section:** A text area pre-populated with a default sample document (the "restart server" procedure that appears throughout the project's documentation). A "Compress" primary button and a "Clear" button. The Clear button triggers a `st.rerun()` to reset the UI state.

- **Processing Flow:** When the user clicks Compress, the app calls `encode(input_text)` inside a `st.spinner()` loading indicator. Success displays a success banner (`st.success`). Failure displays an error message (`st.error`) with guidance to check the API key configuration.

- **Results Display:** A side-by-side two-column layout. The left column shows the original text in a disabled text area with a token count metric. The right column shows the compressed CNL in a code block with a token count metric and a delta indicator showing tokens saved. This is the core "before and after" comparison.

- **Metrics Dashboard:** A four-column row of `st.metric` cards showing: compression ratio (percentage), tokens saved (integer), original size (tokens), and compressed size (tokens). A progress bar visualization of the compression ratio. A caption explaining the visualization. A `st.balloons()` celebration animation when compression exceeds 50%.

- **Footer:** A centered, styled footer line with project branding.

- **Error Handling:** A `try/except` wrapper around the `encode()` call that catches any exception, displays it in `st.error`, and suggests checking the API key. An input validation check that warns if the user clicks Compress with an empty text area.

#### Features NOT In Scope

- **File upload** — the UI accepts pasted text only. No `st.file_uploader()`.
- **Multiple compression modes** — no toggle between "flat" and "flow" synthesis. The app uses whatever `encode()` returns by default.
- **History / session persistence** — each compression is independent. No history sidebar, no saved results.
- **Decoding / expansion** — no "Expand back to English" button. The decoder is not built.
- **Real model switching** — the sidebar model selector is UI scaffolding. It does not pass the selected model to `encode()`. This is explicitly a deferred feature, not a broken one.
- **Responsive mobile design** — Streamlit's default responsiveness is accepted. No custom mobile breakpoints or touch optimization.
- **Automated UI tests** — the Streamlit app is tested manually via the acceptance criteria. Selenium, Playwright, or Streamlit's built-in testing framework are not used.
- **Deployment** — no Streamlit Cloud, Docker, or Heroku deployment. The app runs locally only.

#### Key Design Constraints

1. **Single-file application.** The entire Streamlit app lives in one file (`src/app.py`). No multi-page app, no component library, no separate CSS files.
2. **Direct import.** The app imports directly from `src/encoder.py` and `src/validator.py`. No API layer, no REST endpoint, no WebSocket.
3. **Minimal custom CSS.** Styling is limited to three CSS classes (header, tagline, metric card). The rest uses Streamlit's built-in components.
4. **No caching.** The app does not use `@st.cache_data` or `@st.cache_resource`. Each compression is a fresh call. Caching the LLM responses would mask real-world latency in the demo.
5. **Sample document is hardcoded.** The default text area content is embedded in the Python file. It is not loaded from a file or configuration.

---

### 7.2 — v0.3.2: Test Suite Implementation

**Deliverable:** `tests/conftest.py` (updated), `tests/test_validation.py` (new)
**Duration:** 45–60 minutes
**Test Count:** 3 hypothesis validation test classes + additional metric tests = approximately 8–12 tests in `test_validation.py`

#### What It Does

The test suite implementation serves two purposes. First, it provides updated **shared fixtures** in `conftest.py` that all test files across the project can use. Second, it implements the **three hypothesis-validation tests** that were defined in the original Technical Design Document (the "Semantic Zip Protocol," Section 4) — these are the tests that prove the Haiku Protocol's core thesis claims.

This sub-part is about **validation testing**, not module-level unit testing. The individual module tests (`test_chunker.py`, `test_extractor.py`, `test_synthesizer.py`, `test_validator.py`) were built in Phase 2 alongside their respective modules. v0.3.2 adds the integration-level and thesis-level tests that exercise the full pipeline end-to-end.

#### Features In Scope

- **Shared Test Fixtures (conftest.py update):** Four fixtures that standardize test data across the entire project: `sample_simple_doc` (one-sentence procedure), `sample_medium_doc` (multi-step procedure with warnings), `sample_complex_doc` (full Markdown document with headers, code blocks, prerequisites, and warnings), and `sample_entities` (a pre-built entity dictionary matching the project's canonical "restart server" example). These fixtures consolidate test data that may currently be duplicated across Phase 2 test files.

- **Test Class 1 — Prerequisite Hypothesis (`TestPrerequisiteHypothesis`):** Tests the thesis that Haiku Protocol preserves dependency relationships that verbose text makes difficult for LLMs to track. `test_dependency_extraction`: encodes a medium-complexity document and asserts that the compressed output contains `REQUIRES` or `State:` operators, confirming that dependency information survived compression. `test_action_state_linking`: synthesizes CNL from sample entities and asserts that the `REQUIRES` operator links actions to states, confirming the grammar correctly encodes dependencies.

- **Test Class 2 — Context Overflow Hypothesis (`TestContextOverflowHypothesis`):** Tests the thesis that compressed documentation fits more actionable information into the same token budget. `test_compression_ratio`: encodes a complex document and asserts that the compression ratio is at least 0.4 (40%), confirming meaningful token reduction. `test_information_density`: encodes a complex document and asserts that the compressed output retains key domain concepts (action, exec, state, backup, migrate), confirming that compression did not discard critical information.

- **Test Class 3 — Semantic Fidelity Hypothesis (`TestSemanticFidelityHypothesis`):** Tests the thesis that compression is lossless — meaning is recoverable from the compressed form. `test_command_preservation`: encodes a document containing commands and asserts that `EXEC:` operators in the output contain recognizable command keywords, confirming that literal commands survived compression. `test_warning_preservation`: encodes a document containing warnings and asserts that `WARN:` operators appear in the output, confirming that safety-critical information survived compression.

- **Test Class 4 — Compression Metrics (`TestCompressionMetrics`):** Validates the metrics pipeline. `test_simple_compression`: encodes a simple document and asserts that token counts are positive and that compression actually reduced the token count. `test_metrics_accuracy`: uses `CompressionValidator` directly to verify that metric calculations (ratio between 0 and 1, compressed < original) are mathematically correct.

- **Test Coverage Target:** ≥80% code coverage across all `src/` modules when the full test suite (Phase 2 tests + Phase 3 tests) is run together.

#### Features NOT In Scope

- **Module-level unit tests** — `test_chunker.py`, `test_extractor.py`, `test_synthesizer.py`, and `test_validator.py` were delivered in Phase 2. v0.3.2 does not rewrite, replace, or duplicate them.
- **Load testing / performance testing** — no tests for response time, throughput, or resource consumption.
- **Fuzz testing** — no randomized or adversarial inputs.
- **LLM-in-the-loop tests** — the hypothesis tests call `encode()`, which calls the LLM. This means these tests are **not purely deterministic** and require a live API key. This is intentional: the hypothesis tests validate real-world behavior, not mocked behavior. However, this means they cannot run in a CI environment without API credentials. Phase 2's mocked unit tests cover CI-safe deterministic testing.
- **Embedding-based semantic similarity** — `TestSemanticFidelityHypothesis` uses structural checks (keyword presence, operator presence) as a proxy for semantic fidelity. It does not compute cosine similarity of embeddings, which would require additional infrastructure.
- **Automated test runner / CI integration** — tests are run manually with `pytest`. No GitHub Actions workflow, no pre-commit hooks.

#### Key Design Constraints

1. **Two tiers of tests.** Phase 2 tests are mocked and CI-safe. Phase 3 hypothesis tests are live and API-dependent. Both tiers coexist in the `tests/` directory and both run under `pytest`, but they have different runtime requirements.
2. **Fixtures do not replace Phase 2 fixtures.** If Phase 2 test files already define their own fixtures, v0.3.2's `conftest.py` additions do not override them. `conftest.py` fixtures are available globally, and Phase 2 files can choose to adopt them or keep their own.
3. **Test assertions are conservative.** Hypothesis tests assert structural properties ("REQUIRES is present," "compression_ratio >= 0.4") rather than exact outputs. This accommodates the non-determinism of LLM-powered extraction while still validating meaningful claims.
4. **No test data files.** All test data is embedded in fixtures (Python strings in `conftest.py`). The Phase 0 benchmark samples (`benchmarks/samples/*.md`) are used by v0.2.1d integration tests and v0.3.3 benchmarks, but v0.3.2's hypothesis tests use their own inline data.

---

### 7.3 — v0.3.3: Benchmark Integration

**Deliverable:** `benchmarks/llmlingua_comparison.py`, `benchmarks/results.json`
**Duration:** 45–60 minutes
**Test Count:** Not applicable (benchmark runner, not a test module — validated by acceptance criteria and the generated `results.json`)

#### What It Does

The benchmark integration sub-part builds a runner that compresses the same document corpus through both the Haiku Protocol encoder and Microsoft's LLMLingua, then compares the results side by side. This produces the quantitative evidence needed for the README's benchmark table, the portfolio's "outperformed LLMLingua by X%" claim, and the project's credibility as a research-backed tool.

LLMLingua (by Microsoft Research) is the current academic standard for prompt compression. Comparing against it provides citable, credible validation — or, if Haiku Protocol underperforms on certain document types, honest data about where the approach has limitations.

#### Features In Scope

- **BenchmarkResult Data Model:** A `BenchmarkResult` dataclass containing per-document results: `document_name`, `original_tokens`, `haiku_tokens`, `haiku_ratio`, `llmlingua_tokens`, `llmlingua_ratio`, `winner` (string: "haiku" or "llmlingua"), and `improvement` (float: difference in compression ratios).

- **BenchmarkRunner Class:** A class that orchestrates the comparison. It initializes a `CompressionValidator` (from v0.2.4) for consistent token counting and a `PromptCompressor` (from the `llmlingua` library) for baseline compression. A `compress_with_llmlingua()` method that wraps the LLMLingua API with error handling — if LLMLingua is not installed or fails, the method returns the original text unchanged (graceful degradation, not a crash). A `run_benchmark()` method that runs a single document through both compressors and returns a `BenchmarkResult`. A `run_benchmark_suite()` method that iterates over a dictionary of `{name: content}` documents, running each through `run_benchmark()` and printing progress. A `generate_report()` method that aggregates results into a summary (total benchmarks, wins per system, averages) and a details list (per-document breakdown).

- **Default Document Corpus:** Three inline test documents (simple, medium, complex) matching the complexity levels established in Phase 0's benchmark samples (v0.0.3a). These are short, purpose-built documents, not the full benchmark sample files. The runner can also be pointed at arbitrary documents by passing a different dictionary to `run_benchmark_suite()`.

- **JSON Report Output:** Results are serialized to `benchmarks/results.json` with a `summary` object and a `details` array. The expected output format matches the structure shown in the v0.3.3 README's "Expected Results" section.

- **Console Output:** The runner prints progress during execution (`Benchmarking: simple...`) and a formatted summary table at the end.

- **Standalone Execution:** The file includes an `if __name__ == "__main__":` block that runs the full benchmark suite, generates the report, and saves `results.json` — all in one command: `python benchmarks/llmlingua_comparison.py`.

#### Features NOT In Scope

- **Automated LLMLingua installation** — the benchmark runner checks for `llmlingua` availability at import time and degrades gracefully if it's missing. It does not install the library. The user must have run `pip install llmlingua` themselves (it is listed in `requirements.txt` from v0.1.1c).
- **Statistical significance testing** — the benchmark reports raw ratios and a simple "winner" determination. It does not compute confidence intervals, p-values, or variance analysis. Three documents is too small a corpus for statistical rigor; the benchmark is a **demonstration**, not a peer-reviewed study.
- **Multiple LLMLingua configurations** — the benchmark uses LLMLingua's default `PromptCompressor()` settings. It does not tune LLMLingua's parameters (target ratio, token budget, etc.) for optimal compression. This means the comparison is "Haiku default vs. LLMLingua default," which is the fairest apples-to-apples comparison for a PoC.
- **Visual benchmark report** — the benchmark produces JSON and console output. It does not generate charts, graphs, HTML reports, or Streamlit dashboard pages. Visual presentation of benchmark results is a Phase 4 (README/portfolio) concern.
- **Benchmark against additional baselines** — only LLMLingua is compared. Other compression baselines (extractive summarization, abstractive summarization, token-level pruning, etc.) are not included.
- **Large-scale corpus benchmarking** — the default corpus is three short documents. Running the benchmark against larger documents (the full Phase 0 sample files, or external documentation like AWS/Kubernetes manuals) is possible via the `run_benchmark_suite()` API but is not a deliverable of v0.3.3.
- **Reproducibility guarantees** — because the Haiku encoder uses LLM-powered extraction (GPT-4 with temperature=0), results are *nearly* deterministic but not guaranteed identical across runs due to API variability. The benchmark report captures one run. Reproducibility analysis (multiple runs, variance measurement) is not in scope.

#### Key Design Constraints

1. **LLMLingua is optional.** The benchmark runner must function even if LLMLingua is not installed. If missing, the runner reports the Haiku results alone and skips the comparison. This prevents a dependency installation failure from blocking the entire Phase 3 deliverable.
2. **Consistent tokenizer.** Both Haiku and LLMLingua results are measured using the same `CompressionValidator` (tiktoken, `gpt-4` encoding). This ensures the comparison is apples-to-apples at the token-counting level.
3. **No expected results hardcoded.** The v0.3.3 README shows "Expected Results" as an example, but the actual `results.json` is generated dynamically. The acceptance criteria do not require matching the example numbers — they require that the benchmark runs, produces a report, and shows Haiku as "competitive" (not necessarily superior on every document).
4. **Single-threaded execution.** Documents are benchmarked sequentially. No parallel execution, no async, no threading. Simplicity over speed.

---

## 8. Cross-Cutting Constraints

These constraints apply to all sub-parts in Phase 3:

### 8.1 — Dependency on `encode()` API

All three sub-parts consume the `encode()` function from `src/encoder.py`. Any change to that function's return schema is a breaking change for all of Phase 3. The expected schema is documented in Section 5 ("Critical Dependency: The `encode()` API Contract").

### 8.2 — API Key Requirement

Unlike Phase 2's mocked unit tests, Phase 3 deliverables involve **live LLM calls**:

- The Streamlit demo calls `encode()`, which calls the LLM extractor.
- The hypothesis validation tests call `encode()` with real documents.
- The benchmark runner calls `encode()` for Haiku compression.

All three require a valid `OPENAI_API_KEY` in the `.env` file. There is no "offline mode" or "mock mode" for Phase 3. This is intentional — Phase 3 is about demonstrating real results, not simulated ones.

### 8.3 — Testing

- v0.3.2's `test_validation.py` tests are run via `pytest` alongside Phase 2 tests.
- The Streamlit app (v0.3.1) is tested manually against its acceptance criteria checklist.
- The benchmark runner (v0.3.3) is validated by executing it and inspecting the generated `results.json`.
- Combined test coverage (Phase 2 + Phase 3) should reach ≥80% across all `src/` modules.

### 8.4 — Logging

- `app.py` uses `st.error` and `st.warning` for user-facing messages. It does not use Python's `logging` module (Streamlit has its own paradigm).
- `llmlingua_comparison.py` uses `print()` for console output during benchmark runs. This is acceptable for a script-style runner. Structured logging is not required.
- `test_validation.py` relies on pytest's output for test results. No custom logging.

### 8.5 — Documentation

- All public classes and functions must have docstrings following [Commenting Standards](../../standards/commenting_standards.md).
- CHANGELOG.md is updated with each sub-part completion.
- The Streamlit app's inline comments serve as living documentation for the UI's structure.

### 8.6 — Error Handling

- The Streamlit app catches all exceptions from `encode()` and displays them in-UI rather than crashing.
- The benchmark runner catches LLMLingua import failures and individual compression failures without aborting the suite.
- Hypothesis tests use `pytest` assertions. Failures are reported as test failures, not exceptions.

---

## 9. Data Flow: How Phase 3 Consumes Phase 2

```
Phase 2 (Engine)                          Phase 3 (Presentation)
─────────────────                         ─────────────────────

src/encoder.py ──────────────────────────▶ src/app.py (Streamlit UI)
    │                                          │
    │  encode(markdown) → dict                 │  Displays original, haiku,
    │                                          │  metrics, compression bar
    │
    ├──────────────────────────────────────▶ tests/test_validation.py
    │                                          │
    │  encode(sample_doc) → dict               │  Asserts REQUIRES present,
    │                                          │  ratio >= 0.4, commands preserved
    │
    └──────────────────────────────────────▶ benchmarks/llmlingua_comparison.py
                                               │
       encode(doc) → haiku_result              │  Compares haiku_tokens vs.
       llmlingua.compress(doc) → baseline      │  llmlingua_tokens, reports winner
```

All three Phase 3 sub-parts are **consumers** of Phase 2. They do not modify, extend, or wrap the encoder pipeline. They call it as-is and present its output in different contexts (UI, test assertions, benchmark comparison).

---

## 10. Version Roadmap

```
v0.3.0 — Phase 3: Demo & Visualization
│
├── v0.3.1 — Streamlit UI Development (60–90 min)
│   ├── v0.3.1a — Page Configuration & Layout Foundation (15–20 min)
│   ├── v0.3.1b — Input, Processing & Output Display (25–35 min)
│   └── v0.3.1c — Metrics Dashboard & Celebration (15–20 min)
│
├── v0.3.2 — Test Suite Implementation (45–60 min)
│   ├── v0.3.2a — Shared Test Fixtures (conftest.py) (10–15 min)
│   ├── v0.3.2b — Hypothesis Validation Tests (25–35 min)
│   └── v0.3.2c — Compression Metrics Tests & Coverage (10–15 min)
│
└── v0.3.3 — Benchmark Integration (45–60 min)
    ├── v0.3.3a — Benchmark Data Model & Configuration (10–15 min)
    ├── v0.3.3b — BenchmarkRunner Core Implementation (20–30 min)
    └── v0.3.3c — Report Generation & CLI Entry Point (15–20 min)
```

**Total Estimated Duration:** 150–210 minutes (~2.5–3.5 hours)

The v0.3.0 README estimates "3-4 hours." The lower bound of this roadmap (2.5 hours) accounts for the possibility that Phase 2's encoder is clean and well-tested, reducing integration friction. The upper bound (3.5 hours) accounts for debugging API integration issues, LLMLingua installation quirks, or Streamlit layout finessing.

---

## 11. Phase Exit Criteria

Phase 3 is complete when **all** of the following are true:

- [ ] `streamlit run src/app.py` launches without errors
- [ ] The UI accepts text input and displays compressed output with metrics
- [ ] Side-by-side original vs. compressed display renders correctly
- [ ] Compression metrics (ratio, tokens saved, visualization) display accurately
- [ ] The UI handles errors gracefully (API failure, empty input)
- [ ] `pytest tests/test_validation.py` passes all hypothesis validation tests
- [ ] `pytest` (full suite) exits with code 0
- [ ] Combined test coverage ≥80% across `src/` modules
- [ ] `python benchmarks/llmlingua_comparison.py` executes and produces `benchmarks/results.json`
- [ ] Benchmark report shows Haiku Protocol results alongside LLMLingua results
- [ ] All public functions and classes in new files have docstrings
- [ ] CHANGELOG.md updated with v0.3.x entries

---

## 12. Risk Register

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| `encode()` return schema differs from Phase 3 expectations | All three sub-parts break at integration time | Medium | The schema is documented in Section 5. Phase 2 implementation should conform to it. If it deviates, update Phase 3 code to match. |
| LLMLingua installation fails | Benchmark comparison cannot run | Medium | The benchmark runner degrades gracefully — it reports Haiku results alone if LLMLingua is unavailable. The acceptance criteria require the benchmark to "run," not to produce a comparison. |
| Haiku Protocol compression ratio is lower than LLMLingua | Portfolio claim ("outperformed LLMLingua") cannot be made | Low–Medium | The benchmark reports honest results. If LLMLingua wins on compression ratio, Haiku Protocol may still win on semantic fidelity or structural preservation. The portfolio narrative can be adjusted accordingly. |
| Hypothesis tests are flaky due to LLM non-determinism | Tests sometimes fail on the same input | Medium | Assertions are conservative (e.g., "ratio >= 0.4" not "ratio == 0.56"). GPT-4 with temperature=0 is nearly deterministic. If flakiness occurs, widen assertion bounds or add retry logic in the test. |
| Streamlit version incompatibility | UI components behave differently than expected | Low | Pin Streamlit version in `requirements.txt`. Use only stable, well-documented Streamlit APIs. |
| API rate limits during benchmark runs | Benchmark suite fails midway | Low | Three documents = three `encode()` calls = three LLM invocations. Well within rate limits. |

---

## 13. Decision Log (Phase 3 Level)

| ID | Decision | Rationale | Status |
|---|---|---|---|
| P3-001 | Decoder module is NOT included in Phase 3 | Phase 3 focuses on proving the encoder. The Semantic Fidelity Test validates expansion via LLM prompt, not a dedicated module. Building a decoder doubles the scope without adding portfolio demonstration value. | Approved |
| P3-002 | RAG/ChromaDB integration is NOT included in Phase 3 | RAG is a downstream application of compressed CNL, not a demonstration of compression quality. Phase 3 proves compression works; Phase 4+ can explore applications. | Approved |
| P3-003 | CLI tool is NOT included in Phase 3 | The Streamlit demo is the user-facing interface. A CLI is a convenience tool, not a portfolio showcase. | Approved |
| P3-004 | Sidebar model selector is UI scaffolding only | The dropdown exists but does not pass the selected model to `encode()`. This avoids the need to support multi-model configuration in Phase 2 while demonstrating UI configurability in the demo. | Approved |
| P3-005 | Hypothesis tests call the live LLM (not mocked) | These tests validate real-world behavior. Mocking the LLM would test the mock, not the system. The trade-off is that these tests require API credentials and are not CI-safe. | Approved |
| P3-006 | Benchmark uses LLMLingua defaults | Tuning LLMLingua's parameters for optimal compression would be unfair (or at least debatable). Default-vs-default is the most defensible comparison methodology. | Approved |
| P3-007 | No automated deployment of Streamlit app | Local-only execution. Streamlit Cloud or Docker deployment adds complexity without PoC benefit and introduces maintenance burden. | Approved |
| P3-008 | Three-document corpus for benchmarking | Sufficient for a PoC demonstration. Statistical rigor is not the goal — credible directional evidence is. | Approved |

---

## 14. Glossary

| Term | Definition |
|---|---|
| **Streamlit** | An open-source Python framework that turns Python scripts into interactive web applications. Used for the Haiku Protocol demo UI. |
| **Hypothesis test** | Not a statistical hypothesis test. Refers to the three core thesis claims from the Technical Design Document (Prerequisite, Context Overflow, Semantic Fidelity) that the test suite validates. |
| **LLMLingua** | Microsoft Research's prompt compression library. Used as the benchmark baseline for comparing compression quality. |
| **Benchmark** | A standardized test that runs the same documents through both Haiku Protocol and LLMLingua, measuring compression ratios with a consistent tokenizer. |
| **Golden test** | (Phase 2 term.) A hand-annotated test with known-correct output. Phase 3's hypothesis tests are structural (checking for operator presence), not golden (checking for exact output). |
| **Graceful degradation** | When a component is missing or fails (e.g., LLMLingua not installed), the system continues with reduced functionality rather than crashing. |
| **UI scaffolding** | A UI element that exists in the interface but is not functionally connected to the backend. The model selector dropdown is scaffolding — it renders but does not change behavior. |
| **Live test** | A test that makes real API calls (as opposed to mocked tests). Phase 3's hypothesis tests are live; Phase 2's unit tests are mocked. |

---

**Document Version:** 1.0
**Last Updated:** 2026-02-09
**Author:** Haiku Protocol Project
**Status:** Pending Review
