# v0.3.3b — BenchmarkRunner Core Implementation

<aside>

**Version:** v0.3.3b

**Parent:** v0.3.3 — Benchmark Integration

**Status:** ⬜ Not Started

**Duration:** 20–30 minutes

**Deliverable:** `BenchmarkRunner` class with `__init__()`, `compress_with_llmlingua()`, `run_benchmark()`, and `run_benchmark_suite()` methods in `benchmarks/llmlingua_comparison.py`

</aside>

---

## Objective

Implement the `BenchmarkRunner` class that orchestrates the head-to-head compression benchmark. The runner initializes a `CompressionValidator` for consistent token counting and optionally creates an LLMLingua `PromptCompressor` (with graceful degradation if not available). It provides methods to compress a single document through both systems, compare results, and run a full suite of benchmarks with console progress reporting. The goal is a clean, testable compression pipeline that produces `BenchmarkResult` instances and prints human-readable progress updates.

---

## User Stories

**Story 1: Developer Runs Head-to-Head Benchmark**

> As a developer, I want to instantiate a `BenchmarkRunner`, call `run_benchmark_suite()` with a dictionary of documents, and get back a list of `BenchmarkResult` objects that I can analyze, serialize, or display—all with a single command that prints progress to the console.

**Story 2: Developer Without LLMLingua Still Gets Haiku-Only Results**

> As a developer who hasn't installed LLMLingua, I want the `BenchmarkRunner` to detect its absence during initialization and gracefully degrade: calling `compress_with_llmlingua()` returns the original text unchanged, `BenchmarkResult` shows LLMLingua metrics as "no data," and the suite completes without crashing, allowing me to still validate Haiku's compression quality.

---

## Architecture & Design

### The BenchmarkRunner Class

The `BenchmarkRunner` class serves as the central orchestration point for all compression operations. It manages tokenizer and compressor instances and provides four key methods:

```python
# ============================================================================
# BENCHMARK RUNNER CLASS
# ============================================================================

class BenchmarkRunner:
    """
    Orchestrates a head-to-head compression benchmark comparing Haiku Protocol
    against LLMLingua on a standardized document corpus.

    This class handles:
    - Initialization of the CompressionValidator (tokenizer) and LLMLingua PromptCompressor
    - Individual document compression via encode() and LLMLingua
    - Aggregation of results into BenchmarkResult instances
    - Graceful degradation if LLMLingua is unavailable

    Attributes:
        validator (CompressionValidator): Instance for consistent token counting.
        compressor (PromptCompressor | None): LLMLingua compressor; None if unavailable.
        llmlingua_available (bool): Whether LLMLingua was successfully imported.

    Example:
        >>> runner = BenchmarkRunner()
        >>> results = runner.run_benchmark_suite({
        ...     "test_doc": "Some markdown text..."
        ... })
        >>> print(len(results))  # Number of benchmarked documents
        1
    """

    def __init__(self) -> None:
        """
        Initialize the BenchmarkRunner with a CompressionValidator and optional
        LLMLingua PromptCompressor.

        Creates a CompressionValidator instance (which internally uses tiktoken
        with "gpt-4" encoding for consistent token counting). Attempts to create
        a PromptCompressor if LLMLingua is available; silently skips if missing.

        Raises:
            Unlikely. If CompressionValidator fails to initialize, that is a
            Phase 2 deficiency (missing tiktoken, invalid encoder, etc.).

        Example:
            >>> runner = BenchmarkRunner()
            >>> print(f"LLMLingua available: {runner.llmlingua_available}")
            LLMLingua available: True  # or False
        """
        # Import encoder for compression (Phase 2 dependency)
        from src.encoder import encode
        from src.validator import CompressionValidator

        # Initialize the tokenizer/validator for consistent token counting
        self.validator = CompressionValidator()
        self.encode = encode

        # Attempt to create LLMLingua compressor if available
        self.compressor: Optional[PromptCompressor] = None
        self.llmlingua_available = LLMLINGUA_AVAILABLE

        if self.llmlingua_available and PromptCompressor is not None:
            try:
                self.compressor = PromptCompressor()
            except Exception as e:
                # Silently degrade if PromptCompressor initialization fails
                # (e.g., invalid config, missing credentials for optional LLM backend)
                print(f"Warning: LLMLingua initialization failed: {e}")
                self.compressor = None
                self.llmlingua_available = False

    def compress_with_llmlingua(self, text: str) -> str:
        """
        Compress text using LLMLingua's PromptCompressor.

        If LLMLingua is not available or if compression fails, returns the
        original text unchanged. This is graceful degradation: the benchmark
        continues even without LLMLingua, reporting Haiku metrics alone.

        Args:
            text (str): The text to compress.

        Returns:
            str: The LLMLingua-compressed text, or original text if unavailable/failed.

        Implementation Notes:
            - LLMLingua's API: compressor.compress_prompt(text) returns compressed text.
            - If the compressor is None, returns text unchanged.
            - If compression raises any exception, prints a warning and returns text unchanged.
            - Does NOT retry on failure; a single exception triggers fallback.

        Example:
            >>> runner = BenchmarkRunner()
            >>> original = "Some long documentation..."
            >>> if runner.llmlingua_available:
            ...     compressed = runner.compress_with_llmlingua(original)
            ... else:
            ...     compressed = original
        """
        if not self.llmlingua_available or self.compressor is None:
            # LLMLingua not available; return original unchanged
            return text

        try:
            # Call LLMLingua's API to compress the prompt
            # PromptCompressor.compress_prompt(text) returns the compressed string
            compressed = self.compressor.compress_prompt(text)
            return compressed
        except Exception as e:
            # If compression fails for any reason, degrade gracefully
            print(f"Warning: LLMLingua compression failed: {e}. Using original text.")
            return text

    def run_benchmark(self, name: str, document: str) -> BenchmarkResult:
        """
        Run a single document through both Haiku Protocol and LLMLingua,
        compare results, and return a BenchmarkResult.

        Args:
            name (str): Document identifier (e.g., 'simple', 'complex').
            document (str): The text to compress.

        Returns:
            BenchmarkResult: An object containing:
                - document_name: The input name
                - original_tokens: Token count of the input
                - haiku_tokens: Token count of Haiku output
                - haiku_ratio: Haiku compression ratio (0.0-1.0)
                - llmlingua_tokens: Token count of LLMLingua output (or original if unavailable)
                - llmlingua_ratio: LLMLingua compression ratio (or 1.0 if unavailable)
                - winner: Which system achieved better compression ("haiku", "llmlingua", or "tie")
                - improvement: Absolute difference in ratios (llmlingua_ratio - haiku_ratio)

        Algorithm:
            1. Count tokens in the original document
            2. Call encode() to get Haiku compression result (includes haiku_tokens)
            3. Call compress_with_llmlingua() to get LLMLingua output
            4. Count tokens in LLMLingua output
            5. Calculate ratios for both systems
            6. Determine winner by comparing ratios (lower ratio = better)
            7. Calculate improvement (positive = Haiku is better)
            8. Return BenchmarkResult instance

        Raises:
            Exception: If encode() fails, the exception propagates. This is intentional—
                      if the Haiku encoder breaks, the benchmark should fail noisily.

        Example:
            >>> runner = BenchmarkRunner()
            >>> result = runner.run_benchmark(
            ...     "test_doc",
            ...     "Here is some text to compress..."
            ... )
            >>> print(result.winner)  # "haiku" or "llmlingua"
            haiku
        """
        # Step 1: Get original token count
        original_tokens = self.validator.count_tokens(document)

        # Step 2: Compress with Haiku Protocol
        haiku_result = self.encode(document)
        haiku_text = haiku_result["haiku"]
        haiku_tokens = haiku_result["compressed_tokens"]
        haiku_ratio = haiku_tokens / original_tokens if original_tokens > 0 else 1.0

        # Step 3: Compress with LLMLingua
        llmlingua_text = self.compress_with_llmlingua(document)

        # Step 4: Count tokens in LLMLingua output
        llmlingua_tokens = self.validator.count_tokens(llmlingua_text)
        llmlingua_ratio = llmlingua_tokens / original_tokens if original_tokens > 0 else 1.0

        # Step 5: Determine winner (lower ratio = better compression)
        if haiku_ratio < llmlingua_ratio:
            winner = "haiku"
        elif llmlingua_ratio < haiku_ratio:
            winner = "llmlingua"
        else:
            winner = "tie"

        # Step 6: Calculate improvement (positive = Haiku is better)
        improvement = llmlingua_ratio - haiku_ratio

        # Step 7: Return result
        return BenchmarkResult(
            document_name=name,
            original_tokens=original_tokens,
            haiku_tokens=haiku_tokens,
            haiku_ratio=haiku_ratio,
            llmlingua_tokens=llmlingua_tokens,
            llmlingua_ratio=llmlingua_ratio,
            winner=winner,
            improvement=improvement,
        )

    def run_benchmark_suite(
        self, documents: Dict[str, str]
    ) -> List[BenchmarkResult]:
        """
        Run the benchmark on a suite of documents, printing progress to console.

        Iterates over the documents dict, runs run_benchmark() on each, and
        prints progress updates. Returns a list of results in document order.

        Args:
            documents (Dict[str, str]): A mapping of {document_name: document_text}.
                                        Typically DEFAULT_DOCUMENTS from v0.3.3a.

        Returns:
            List[BenchmarkResult]: Results in the same order as the input documents dict.

        Console Output:
            For each document, prints:
                Benchmarking: {name}...

            After each document, prints a one-line summary:
                {name}: Haiku={ratio}% | LLMLingua={ratio}% | Winner: {winner}

        Algorithm:
            1. Initialize empty results list
            2. For each (name, document) in documents dict:
                a. Print "Benchmarking: {name}..."
                b. Call run_benchmark(name, document)
                c. Print summary line
                d. Append result to list
            3. Return results list

        Example:
            >>> runner = BenchmarkRunner()
            >>> results = runner.run_benchmark_suite({
            ...     "simple": "short text",
            ...     "complex": "longer documentation..."
            ... })
            >>> len(results)
            2
        """
        results: List[BenchmarkResult] = []

        for name, document in documents.items():
            # Print progress indicator
            print(f"Benchmarking: {name}...")

            # Run the benchmark for this document
            result = self.run_benchmark(name, document)
            results.append(result)

            # Print per-document summary line
            haiku_pct = result.haiku_ratio * 100
            llmlingua_pct = result.llmlingua_ratio * 100
            print(
                f"  {name}: Haiku={haiku_pct:.1f}% | "
                f"LLMLingua={llmlingua_pct:.1f}% | Winner: {result.winner}"
            )

        return results
```

---

## Benchmark Pipeline Diagram

```
Document Input
    │
    ├────────────────────────────────────────────────────────┐
    │                                                         │
    ▼                                                         ▼
Count Tokens                                    compress_with_llmlingua()
(validator)                                            │
    │                                                  ├─ Check LLMLINGUA_AVAILABLE
    │                                                  │
    ▼                                                  ├─ If True:
original_tokens                                       │   └─ Call PromptCompressor.compress_prompt()
    │                                                  │
    ├─────────────────────────┐                        ├─ If False:
    │                         │                        │   └─ Return original text unchanged
    ▼                         ▼                        │
encode()            (fallback path)                    ▼
    │                         │                    llmlingua_text
    ├─ Haiku encoder          │
    │  returns dict           ▼
    │  with "haiku" + Count Tokens
    │  "compressed_tokens"
    │                         │
    ▼                         ▼
haiku_result          llmlingua_tokens
    │
    ├─ haiku_text
    ├─ haiku_tokens
    └─ Extract compressed_tokens

    │
    ├─────────────────────────┐
    │                         │
    ▼                         ▼
Calculate Ratios:   Compare & Determine Winner
haiku_ratio =           │
  haiku_tokens /        ├─ If haiku_ratio < llmlingua_ratio: "haiku"
  original_tokens       ├─ Else if llmlingua_ratio < haiku_ratio: "llmlingua"
                        └─ Else: "tie"
llmlingua_ratio =
  llmlingua_tokens /    Calculate Improvement:
  original_tokens       improvement = llmlingua_ratio - haiku_ratio

    │
    └──────────────────────────┐
                               │
                               ▼
                        Create BenchmarkResult
                               │
                               └─► Return to run_benchmark_suite()
```

---

## Graceful Degradation Matrix

This matrix defines the exact behavior when LLMLingua is unavailable:

| Condition | Behavior | Console Output |
|---|---|---|
| **LLMLingua not installed** | `LLMLINGUA_AVAILABLE = False` at module load | (None — silent degradation) |
| **LLMLingua import fails** | PromptCompressor = None | (None — silent degradation) |
| **PromptCompressor() init fails** | Exception caught in `__init__`; `compressor = None` | `Warning: LLMLingua initialization failed: {error}` |
| **compress_with_llmlingua() called when unavailable** | Returns original text unchanged | (None — silent in normal flow) |
| **compress_with_llmlingua() raises exception** | Exception caught; returns original text unchanged | `Warning: LLMLingua compression failed: {error}. Using original text.` |
| **BenchmarkResult with no LLMLingua** | `llmlingua_tokens = original_tokens`, `llmlingua_ratio = 1.0` (no compression) | (Reported in results.json and console summary) |
| **Benchmark suite completes without LLMLingua** | Results list contains `BenchmarkResult` with valid Haiku metrics but "no compression" LLMLingua metrics | Results printed; comparison shows Haiku vs. baseline (100%) |

**Key Principle:** When LLMLingua is unavailable, the benchmark does NOT crash. It reports Haiku compression against a baseline (original text at 100% ratio), allowing the user to still validate that Haiku is compressing effectively.

---

## File Structure

The `BenchmarkRunner` class appears in the `benchmarks/llmlingua_comparison.py` file:

```
benchmarks/llmlingua_comparison.py
├── Module docstring
├── Imports (src.encoder, src.validator, dataclasses, json, typing)
├── LLMLINGUA_AVAILABLE flag and import guard
├── BenchmarkResult dataclass (v0.3.3a)
├── DEFAULT_DOCUMENTS corpus (v0.3.3a)
├── BenchmarkRunner class (THIS SUB-PART)
│   ├── __init__()
│   ├── compress_with_llmlingua()
│   ├── run_benchmark()
│   └── run_benchmark_suite()
├── generate_report() method (v0.3.3c)
├── run_benchmarks() function (v0.3.3c)
└── if __name__ == "__main__": block (v0.3.3c)
```

---

## Implementation Workflow

```
┌──────────────────────────────────────────────────────────────────────┐
│ BenchmarkRunner (v0.3.3b) Implementation Workflow                    │
└──────────────────────────────────────────────────────────────────────┘

Start: run_benchmark_suite(documents)
    │
    ├─► For each (name, document) in documents:
    │
    │   a) Print "Benchmarking: {name}..."
    │   │
    │   b) Call run_benchmark(name, document)
    │   │   │
    │   │   ├─► Count original_tokens via validator
    │   │   │
    │   │   ├─► Call encode() → haiku_result
    │   │   │   ├─ Extract haiku text and compressed_tokens
    │   │   │   └─ Calculate haiku_ratio
    │   │   │
    │   │   ├─► Call compress_with_llmlingua(document)
    │   │   │   ├─ If available: call PromptCompressor.compress_prompt()
    │   │   │   └─ If unavailable: return original text (ratio=1.0)
    │   │   │
    │   │   ├─► Count llmlingua_tokens via validator
    │   │   │   └─ Calculate llmlingua_ratio
    │   │   │
    │   │   ├─► Compare ratios to determine winner
    │   │   │
    │   │   └─► Return BenchmarkResult(...)
    │   │
    │   c) Print summary line: "{name}: Haiku={%} | LLMLingua={%} | Winner: {}"
    │   │
    │   d) Append result to results list
    │
    └─► Return results list

All Results Ready ──► Next: v0.3.3c (report generation)
```

---

## Acceptance Criteria Verification

The v0.3.3b BenchmarkRunner is complete when:

- [ ] `BenchmarkRunner.__init__()` initializes without raising exceptions
- [ ] `__init__()` creates a valid `CompressionValidator` instance
- [ ] `__init__()` optionally creates a `PromptCompressor` if `LLMLINGUA_AVAILABLE` is True
- [ ] `__init__()` catches and silently degrades if `PromptCompressor()` init fails
- [ ] `compress_with_llmlingua()` returns a string (never None)
- [ ] `compress_with_llmlingua()` returns original text if LLMLingua is unavailable (graceful degradation)
- [ ] `compress_with_llmlingua()` catches exceptions and returns original text on failure
- [ ] `run_benchmark()` returns a valid `BenchmarkResult` instance
- [ ] `run_benchmark()` populates all 8 BenchmarkResult fields correctly
- [ ] `run_benchmark()` correctly calculates compression ratios (compressed / original)
- [ ] `run_benchmark()` correctly determines winner (lower ratio = better)
- [ ] `run_benchmark_suite()` processes all documents in the input dict
- [ ] `run_benchmark_suite()` returns a list of `BenchmarkResult` with one entry per document
- [ ] `run_benchmark_suite()` prints "Benchmarking: {name}..." for each document
- [ ] `run_benchmark_suite()` prints a summary line after each document
- [ ] Console output is readable and provides clear progress indication

**Verification Method:** Execute `run_benchmark_suite(DEFAULT_DOCUMENTS)` and verify output, then inspect returned results list.

---

## Limitations & Constraints

1. **Single-Threaded Execution:** Documents are benchmarked sequentially, one at a time. No parallel execution, no async, no threading. This simplifies the implementation and makes console output linear and predictable.

2. **No Retry Logic:** If `encode()` fails, the exception propagates and halts the benchmark suite. There is no automatic retry. This is intentional—encoder failures should be visible.

3. **No Progress Bar:** Progress is indicated via `print()` statements ("Benchmarking: {name}..."). No external libraries like `tqdm` or Streamlit's `st.progress()`. This keeps dependencies minimal.

4. **LLMLingua Uses Default Settings Only:** The `PromptCompressor()` is initialized with no arguments, so it uses LLMLingua's defaults. There is no way to customize compression parameters (target ratio, token budget, etc.). This ensures fair default-vs-default comparison.

5. **Consistent Tokenizer Assumption:** Both Haiku and LLMLingua results are measured using the same `CompressionValidator` (tiktoken, gpt-4 encoding). If this tokenizer differs from what LLMLingua internally uses, there may be minor discrepancies, but this is acceptable for a PoC.

---

## Dependencies

**Core Dependencies:**
- `src.encoder` — `encode()` function (imported dynamically in `__init__`)
- `src.validator` — `CompressionValidator` class (imported dynamically in `__init__`)
- `benchmarks.llmlingua_comparison` — `BenchmarkResult` dataclass and `DEFAULT_DOCUMENTS` (defined in same file)

**Optional Dependencies:**
- `llmlingua` — `PromptCompressor` class (imported at module level with try/except; may be None)

**Standard Library:**
- `typing` — `Dict`, `List`, `Optional`

---

## Outputs to Next Sub-Part

The `BenchmarkRunner` class outputs are used by v0.3.3c (Report Generation):

1. **List[BenchmarkResult]** — Returned by `run_benchmark_suite()`. This list is passed to `generate_report()` in v0.3.3c to produce the final summary and JSON output.

2. **Console Progress Output** — The print statements during `run_benchmark_suite()` provide real-time feedback to the user. This output is consumed by the user (not by code), but signals successful benchmark execution.

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| v0.3.3b-001 | Graceful degradation (return original text) instead of hard failure if LLMLingua unavailable | Hard failure would block the entire Phase 3 deliverable on a missing optional dependency. Graceful degradation allows the benchmark to run with Haiku-only metrics, which is still valuable for validation. | Approved |
| v0.3.3b-002 | Use print() for console output instead of logging module | Logging would require configuration (handlers, formatters, levels). For a script-style benchmark runner, print() is simpler and acceptable per scope breakdown Section 8.4. | Approved |
| v0.3.3b-003 | Single-threaded sequential execution instead of parallel compression | Parallel execution adds complexity (threading/async, result aggregation, console output ordering). Sequential execution is slower but simpler, more predictable, and sufficient for three documents. | Approved |
| v0.3.3b-004 | Determine winner by comparing compression ratios (lower is better) | Compression ratio (compressed_tokens / original_tokens) is the standard metric. Lower ratio = better compression. This is simpler than trying to account for semantic fidelity or other factors. | Approved |

---

**Document Version:** 1.0
**Last Updated:** 2026-02-09
**Author:** Haiku Protocol Project
**Status:** Pending Review
