# v0.3.3c — Report Generation & CLI Entry Point

<aside>

**Version:** v0.3.3c

**Parent:** v0.3.3 — Benchmark Integration

**Status:** ⬜ Not Started

**Duration:** 15–20 minutes

**Deliverable:** `generate_report()` method in `BenchmarkRunner`, `run_benchmarks()` standalone function, JSON output file (`benchmarks/results.json`), CLI entry point (`if __name__ == "__main__"`) in `benchmarks/llmlingua_comparison.py`

</aside>

---

## Objective

Implement report aggregation and JSON output for the benchmark runner. This sub-part adds a `generate_report()` method to `BenchmarkRunner` that transforms a list of `BenchmarkResult` instances into a structured report with summary statistics and per-document details. It provides a `run_benchmarks()` standalone function that orchestrates the entire pipeline (create runner, run suite, generate report, save JSON, print summary) and an `if __name__ == "__main__"` block that allows the script to be executed directly. The goal is to produce publishable, machine-readable benchmark results that can be embedded in documentation or consumed by downstream tools.

---

## User Stories

**Story 1: Developer Generates Shareable Benchmark Report**

> As a developer, I want to run `python benchmarks/llmlingua_comparison.py` and get a JSON report in `benchmarks/results.json` that I can commit to version control, share with collaborators, or embed in a README—with a human-readable summary printed to the console.

**Story 2: Portfolio Reviewer Inspects Quantified Comparison Data**

> As a hiring manager reviewing the Haiku Protocol project, I want to open `benchmarks/results.json` and see structured data showing document names, token counts, compression ratios for both systems, and a clear "winner" indicator—all without running any code myself.

---

## Implementation Design

This section covers the `generate_report()` method and the `run_benchmarks()` function and CLI entry point.

### 1. BenchmarkRunner.generate_report() Method

```python
def generate_report(self, results: List[BenchmarkResult]) -> Dict:
    """
    Aggregate a list of BenchmarkResult instances into a structured report
    with summary statistics and per-document details.

    Args:
        results (List[BenchmarkResult]): Results from run_benchmark_suite().

    Returns:
        Dict: A dictionary with two top-level keys:
            - "summary": Aggregated statistics across all documents
            - "details": Per-document breakdown (list of dicts)

    Report Structure:
        The returned dict has this schema:

        {
            "summary": {
                "total_benchmarks": int,
                "haiku_wins": int,
                "llmlingua_wins": int,
                "ties": int,
                "avg_haiku_compression": str,  # e.g., "29.2%"
                "avg_llmlingua_compression": str,  # e.g., "40.1%"
                "avg_improvement": str,  # e.g., "+10.9%"
            },
            "details": [
                {
                    "document_name": str,
                    "original_tokens": int,
                    "haiku": {
                        "tokens": int,
                        "ratio": float,  # 0.0-1.0
                    },
                    "llmlingua": {
                        "tokens": int,
                        "ratio": float,  # 0.0-1.0
                    },
                    "winner": str,  # "haiku", "llmlingua", or "tie"
                },
                # ... more documents ...
            ]
        }

    Calculation Details:
        - avg_haiku_compression: Mean of haiku_ratio across all documents, formatted as percentage
        - avg_llmlingua_compression: Mean of llmlingua_ratio across all documents, formatted as percentage
        - avg_improvement: Mean of improvement across all documents, formatted as percentage
        - ties: Count of results where haiku_ratio == llmlingua_ratio (usually 0)

    Example:
        >>> runner = BenchmarkRunner()
        >>> results = runner.run_benchmark_suite(DEFAULT_DOCUMENTS)
        >>> report = runner.generate_report(results)
        >>> print(report["summary"]["haiku_wins"])
        2
    """
    if not results:
        # Empty results; return a blank report
        return {
            "summary": {
                "total_benchmarks": 0,
                "haiku_wins": 0,
                "llmlingua_wins": 0,
                "ties": 0,
                "avg_haiku_compression": "0.0%",
                "avg_llmlingua_compression": "0.0%",
                "avg_improvement": "0.0%",
            },
            "details": [],
        }

    # Count wins by winner
    haiku_wins = sum(1 for r in results if r.winner == "haiku")
    llmlingua_wins = sum(1 for r in results if r.winner == "llmlingua")
    ties = sum(1 for r in results if r.winner == "tie")

    # Calculate averages
    avg_haiku_ratio = sum(r.haiku_ratio for r in results) / len(results)
    avg_llmlingua_ratio = sum(r.llmlingua_ratio for r in results) / len(results)
    avg_improvement = sum(r.improvement for r in results) / len(results)

    # Format percentages for display
    avg_haiku_pct = f"{avg_haiku_ratio * 100:.1f}%"
    avg_llmlingua_pct = f"{avg_llmlingua_ratio * 100:.1f}%"
    avg_improvement_pct = f"{avg_improvement * 100:+.1f}%"  # + sign for positive

    # Build summary object
    summary = {
        "total_benchmarks": len(results),
        "haiku_wins": haiku_wins,
        "llmlingua_wins": llmlingua_wins,
        "ties": ties,
        "avg_haiku_compression": avg_haiku_pct,
        "avg_llmlingua_compression": avg_llmlingua_pct,
        "avg_improvement": avg_improvement_pct,
    }

    # Build details array (one entry per document)
    details = []
    for result in results:
        detail_entry = {
            "document_name": result.document_name,
            "original_tokens": result.original_tokens,
            "haiku": {
                "tokens": result.haiku_tokens,
                "ratio": round(result.haiku_ratio, 4),
            },
            "llmlingua": {
                "tokens": result.llmlingua_tokens,
                "ratio": round(result.llmlingua_ratio, 4),
            },
            "winner": result.winner,
        }
        details.append(detail_entry)

    return {
        "summary": summary,
        "details": details,
    }
```

### 2. run_benchmarks() Standalone Function

```python
def run_benchmarks(
    documents: Optional[Dict[str, str]] = None,
    output_file: str = "benchmarks/results.json",
) -> Dict:
    """
    Execute the complete benchmark pipeline: initialize runner, run suite,
    generate report, save to JSON, and print summary to console.

    This is the main entry point for the benchmark. It orchestrates all steps
    and is called by the CLI (if __name__ == "__main__" block).

    Args:
        documents (Dict[str, str] | None): Documents to benchmark.
                                           Defaults to DEFAULT_DOCUMENTS if None.
        output_file (str): Path to write results.json. Defaults to "benchmarks/results.json".

    Returns:
        Dict: The generated report (summary + details).

    Algorithm:
        1. Use DEFAULT_DOCUMENTS if no documents provided
        2. Create BenchmarkRunner instance
        3. Call run_benchmark_suite(documents) → List[BenchmarkResult]
        4. Call generate_report(results) → Dict with summary and details
        5. Write report dict to output_file as JSON (indent=2 for readability)
        6. Print formatted summary to console
        7. Return report dict

    Console Output:
        After benchmarking completes, print:
        - A header line ("Benchmark Results")
        - Summary statistics (total benchmarks, wins, average compression)
        - Per-document summary table (one row per document)

    Raises:
        FileNotFoundError: If output_file's parent directory does not exist.
        IOError: If JSON write fails.
        Exception: If encode() fails during benchmarking (benchmark aborts).

    Example:
        >>> report = run_benchmarks()
        >>> print(report["summary"]["total_benchmarks"])
        3
        >>> # Also writes to benchmarks/results.json
    """
    # Use default documents if none provided
    if documents is None:
        documents = DEFAULT_DOCUMENTS

    # Create runner instance
    runner = BenchmarkRunner()

    # Run the benchmark suite
    print("\n" + "=" * 70)
    print("Haiku Protocol vs. LLMLingua Benchmark")
    print("=" * 70 + "\n")
    results = runner.run_benchmark_suite(documents)

    # Generate report
    report = runner.generate_report(results)

    # Write report to JSON file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nResults saved to: {output_path}\n")

    # Print summary to console
    summary = report["summary"]
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Benchmarks: {summary['total_benchmarks']}")
    print(f"Haiku Wins: {summary['haiku_wins']}")
    print(f"LLMLingua Wins: {summary['llmlingua_wins']}")
    print(f"Ties: {summary['ties']}")
    print(f"\nAverage Compression:")
    print(f"  Haiku Protocol: {summary['avg_haiku_compression']}")
    print(f"  LLMLingua: {summary['avg_llmlingua_compression']}")
    print(f"  Improvement: {summary['avg_improvement']}")
    print("=" * 70 + "\n")

    # Print detailed results table
    print("DOCUMENT-BY-DOCUMENT RESULTS")
    print("=" * 70)
    print(f"{'Document':<20} {'Original':<10} {'Haiku':<10} {'LLMLingua':<12} {'Winner':<12}")
    print("-" * 70)
    for detail in report["details"]:
        doc_name = detail["document_name"]
        orig = detail["original_tokens"]
        haiku_ratio = detail["haiku"]["ratio"] * 100
        llm_ratio = detail["llmlingua"]["ratio"] * 100
        winner = detail["winner"]
        print(f"{doc_name:<20} {orig:<10} {haiku_ratio:<10.1f}% {llm_ratio:<12.1f}% {winner:<12}")
    print("=" * 70 + "\n")

    return report


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """
    Allow the benchmark to be run directly from the command line:

        python benchmarks/llmlingua_comparison.py

    This calls run_benchmarks() with default arguments (DEFAULT_DOCUMENTS,
    output to benchmarks/results.json).
    """
    report = run_benchmarks()
```

---

## Report Schema

The JSON report output has a fixed schema designed for both human readability and programmatic consumption:

| Field | Type | Description | Example |
|---|---|---|---|
| **summary** | Object | Aggregated statistics across all documents | (see below) |
| **summary.total_benchmarks** | Integer | Number of documents benchmarked | `3` |
| **summary.haiku_wins** | Integer | Count of documents where Haiku had better compression | `2` |
| **summary.llmlingua_wins** | Integer | Count of documents where LLMLingua had better compression | `1` |
| **summary.ties** | Integer | Count of documents with equal compression ratios | `0` |
| **summary.avg_haiku_compression** | String | Mean Haiku compression ratio formatted as percentage | `"29.2%"` |
| **summary.avg_llmlingua_compression** | String | Mean LLMLingua compression ratio formatted as percentage | `"40.1%"` |
| **summary.avg_improvement** | String | Mean difference in compression ratios (Haiku vs. LLMLingua), signed percentage | `"+10.9%"` |
| **details** | Array | Per-document breakdown; one object per document | (see below) |
| **details[].document_name** | String | Document identifier | `"complex"` |
| **details[].original_tokens** | Integer | Token count of original uncompressed text | `487` |
| **details[].haiku** | Object | Haiku compression metrics for this document | (see below) |
| **details[].haiku.tokens** | Integer | Token count of Haiku output | `142` |
| **details[].haiku.ratio** | Float | Compression ratio (tokens / original); rounded to 4 decimals | `0.2917` |
| **details[].llmlingua** | Object | LLMLingua compression metrics for this document | (see below) |
| **details[].llmlingua.tokens** | Integer | Token count of LLMLingua output; equals original_tokens if unavailable | `195` |
| **details[].llmlingua.ratio** | Float | Compression ratio; rounded to 4 decimals | `0.4005` |
| **details[].winner** | String | Which system achieved better compression | `"haiku"` |

---

## Console Output Format

When `run_benchmarks()` executes, it prints the following to console:

```
======================================================================
Haiku Protocol vs. LLMLingua Benchmark
======================================================================

Benchmarking: simple...
  simple: Haiku=30.0% | LLMLingua=40.0% | Winner: haiku
Benchmarking: medium...
  medium: Haiku=28.5% | LLMLingua=42.0% | Winner: haiku
Benchmarking: complex...
  complex: Haiku=29.2% | LLMLingua=40.1% | Winner: haiku

Results saved to: benchmarks/results.json

======================================================================
SUMMARY
======================================================================
Total Benchmarks: 3
Haiku Wins: 3
LLMLingua Wins: 0
Ties: 0

Average Compression:
  Haiku Protocol: 29.2%
  LLMLingua: 40.7%
  Improvement: +11.5%
======================================================================

DOCUMENT-BY-DOCUMENT RESULTS
======================================================================
Document             Original   Haiku      LLMLingua    Winner
------================================================================
simple               50         30.0%      40.0%        haiku
medium               210        28.5%      42.0%        haiku
complex              487        29.2%      40.1%        haiku
======================================================================

```

The format is designed to be scannable in a terminal and informative without being overwhelming.

---

## File Structure

The complete `benchmarks/llmlingua_comparison.py` file now includes:

```
benchmarks/
├── llmlingua_comparison.py
│   ├── Module docstring
│   ├── Imports (json, Path, from src.encoder, src.validator)
│   ├── LLMLINGUA_AVAILABLE flag & import guard (v0.3.3a)
│   ├── BenchmarkResult dataclass (v0.3.3a)
│   ├── DEFAULT_DOCUMENTS corpus (v0.3.3a)
│   ├── BenchmarkRunner class (v0.3.3b)
│   │   ├── __init__()
│   │   ├── compress_with_llmlingua()
│   │   ├── run_benchmark()
│   │   ├── run_benchmark_suite()
│   │   └── generate_report()  ← (THIS SUB-PART)
│   ├── run_benchmarks() function ← (THIS SUB-PART)
│   └── if __name__ == "__main__": ← (THIS SUB-PART)
│
└── results.json  ← Generated output
    {
        "summary": { ... },
        "details": [ ... ]
    }
```

---

## Implementation Workflow

```
┌──────────────────────────────────────────────────────────────────────┐
│ Report Generation & CLI (v0.3.3c) Workflow                           │
└──────────────────────────────────────────────────────────────────────┘

User executes:
    python benchmarks/llmlingua_comparison.py
            │
            ▼
    if __name__ == "__main__"
            │
            ▼
    run_benchmarks()
            │
            ├─► DEFAULT_DOCUMENTS = DEFAULT_DOCUMENTS
            │
            ├─► runner = BenchmarkRunner()
            │
            ├─► results = runner.run_benchmark_suite(documents)
            │   └─► [BenchmarkResult, BenchmarkResult, ...]
            │
            ├─► report = runner.generate_report(results)
            │   ├─ Count wins (haiku_wins, llmlingua_wins, ties)
            │   ├─ Calculate averages (avg_haiku_ratio, avg_llmlingua_ratio)
            │   └─ Build summary + details objects
            │
            ├─► Write report to benchmarks/results.json
            │   └─ json.dump(report, indent=2)
            │
            ├─► Print summary to console
            │   ├─ Header
            │   ├─ Summary statistics
            │   └─ Document-by-document table
            │
            └─► Return report

Benchmark Complete
    │
    ├─ JSON file: benchmarks/results.json (machine-readable)
    └─ Console output (human-readable summary)
```

---

## Acceptance Criteria Verification

The v0.3.3c report generation is complete when:

- [ ] `BenchmarkRunner.generate_report()` accepts a `List[BenchmarkResult]` parameter
- [ ] `generate_report()` returns a Dict with "summary" and "details" keys
- [ ] `summary` dict contains all 7 required fields (total_benchmarks, haiku_wins, llmlingua_wins, ties, avg_haiku_compression, avg_llmlingua_compression, avg_improvement)
- [ ] `details` is a list with one entry per input result
- [ ] Each details entry contains all required fields (document_name, original_tokens, haiku, llmlingua, winner)
- [ ] `haiku` and `llmlingua` objects contain "tokens" and "ratio" fields
- [ ] Numeric ratios are rounded to 4 decimal places
- [ ] Percentage strings are formatted correctly (e.g., "29.2%", "+10.9%")
- [ ] `run_benchmarks()` creates a BenchmarkRunner instance
- [ ] `run_benchmarks()` calls `run_benchmark_suite()` with provided or default documents
- [ ] `run_benchmarks()` calls `generate_report()` on the results
- [ ] `run_benchmarks()` writes valid JSON to the specified output file
- [ ] JSON output is properly indented and human-readable
- [ ] `run_benchmarks()` prints a formatted summary to console
- [ ] `run_benchmarks()` returns the generated report dict
- [ ] Script is executable: `python benchmarks/llmlingua_comparison.py` runs without errors
- [ ] `if __name__ == "__main__"` block exists and calls `run_benchmarks()`
- [ ] After execution, `benchmarks/results.json` exists and contains valid JSON

**Verification Method:** Run the script and inspect console output + JSON file. Parse JSON to verify schema.

---

## Limitations & Constraints

1. **No HTML or Chart Output:** The benchmark produces JSON and console text only. There is no HTML report, no PNG charts, and no Streamlit dashboard for result visualization. Visual presentation of results is a Phase 4 concern (README, portfolio site).

2. **No Multiple Runs or Variance Analysis:** The benchmark runs once and produces one report. It does not repeat the benchmark multiple times to measure variance or compute confidence intervals. Three documents is too small a corpus for statistical rigor anyway.

3. **Results File Is Overwritten:** Each execution of `run_benchmarks()` overwrites `benchmarks/results.json`. There is no append mode, no history, and no timestamped versions. If you want to keep old results, you must manually rename `results.json` or version-control commit the file after each run.

4. **No Custom Output Path Validation:** The function creates parent directories for the output file if they don't exist, but does not validate that the path is reasonable (e.g., no check that it's under the project root). Providing an absolute path like `/etc/results.json` is technically possible.

5. **Percentage Formatting Is Locale-Agnostic:** Percentages are formatted using `f"{value * 100:.1f}%"` which uses the locale's decimal separator (`.` in English, `,` in some European locales). The JSON output is not localized; this is acceptable for a developer-facing tool.

---

## Dependencies

**Core Dependencies:**
- `json` (standard library) — for JSON serialization in `generate_report()` output
- `pathlib.Path` (standard library) — for `output_path.parent.mkdir()` and file operations
- `src.encoder` — imported dynamically by `BenchmarkRunner.__init__()`
- `src.validator` — imported dynamically by `BenchmarkRunner.__init__()`
- `benchmarks.llmlingua_comparison` — `BenchmarkResult`, `DEFAULT_DOCUMENTS`, `BenchmarkRunner` (same file)

**Optional Dependencies:**
- None (v0.3.3c uses only standard library and previously defined classes)

---

## Outputs: Complete v0.3.3 Deliverable

When v0.3.3 is finalized, the following files are generated and committed:

1. **`benchmarks/llmlingua_comparison.py`** — Complete benchmark script containing:
   - BenchmarkResult dataclass
   - DEFAULT_DOCUMENTS corpus
   - BenchmarkRunner class
   - generate_report() method
   - run_benchmarks() function
   - CLI entry point

2. **`benchmarks/results.json`** — Generated output containing:
   - Summary statistics (total benchmarks, wins, averages)
   - Per-document details (tokens, ratios, winner)

Both files are committed to version control, making the benchmark results transparent and reproducible (within the constraints of non-deterministic LLM outputs).

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| v0.3.3c-001 | Use JSON instead of CSV for report format | JSON is structured, self-documenting, and easier to parse programmatically. CSV is simpler but lacks hierarchy (hard to represent summary + details in one file). JSON is standard for machine-readable reports. | Approved |
| v0.3.3c-002 | Flat summary + details array instead of nested structure per document | Separating summary (aggregate stats) from details (per-document) makes the report easier to consume. Tools can read just the summary without processing all details, and the details are self-contained (not nested under summary). | Approved |
| v0.3.3c-003 | Print detailed console output even though JSON is saved | Users need immediate feedback from the command line. Printing summary and document-by-document results to console makes the benchmark interactive and trustworthy. Users can see progress and results without opening the JSON file. | Approved |

---

## Glossary

| Term | Definition |
|---|---|
| **generate_report()** | A method that aggregates a list of BenchmarkResult instances into a summary object and details array, both of which are returned as a dict. |
| **run_benchmarks()** | A standalone function that orchestrates the entire benchmark pipeline: initialize runner, run suite, generate report, save JSON, print summary. |
| **CLI Entry Point** | The `if __name__ == "__main__"` block that allows the script to be executed directly from the command line. |
| **results.json** | The machine-readable output file containing the benchmark report in JSON format. |
| **Improvement** | The absolute difference in compression ratios (LLMLingua ratio - Haiku ratio). Positive = Haiku is better; negative = LLMLingua is better. |
| **Tie** | When two systems achieve the same compression ratio (ratio difference = 0). Rare in practice due to floating-point precision. |

---

**Document Version:** 1.0
**Last Updated:** 2026-02-09
**Author:** Haiku Protocol Project
**Status:** Pending Review
