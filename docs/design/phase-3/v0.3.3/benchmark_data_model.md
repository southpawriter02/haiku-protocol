# v0.3.3a — Benchmark Data Model & Configuration

<aside>

**Version:** v0.3.3a

**Parent:** v0.3.3 — Benchmark Integration

**Status:** ⬜ Not Started

**Duration:** 10–15 minutes

**Deliverable:** `BenchmarkResult` dataclass, `LLMLINGUA_AVAILABLE` import guard, default document corpus in `benchmarks/llmlingua_comparison.py`

</aside>

---

## Objective

Define the core data structures and configuration for the LLMLingua benchmark runner. This sub-part specifies the `BenchmarkResult` dataclass that holds per-document compression results, the module-level import guard that gracefully handles missing LLMLingua, and the default document corpus (three inline test documents of varying complexity). The goal is to establish a consistent, JSON-serializable data model for benchmark results and ensure the benchmark runner can function even if LLMLingua is not installed.

---

## User Stories

**Story 1: Benchmark Author Defines Result Structure**

> As a benchmark developer, I want a standardized `BenchmarkResult` dataclass with clear fields (`document_name`, `original_tokens`, `haiku_tokens`, `haiku_ratio`, `llmlingua_tokens`, `llmlingua_ratio`, `winner`, `improvement`) so that all benchmark results follow the same structure, can be serialized to JSON, and can be compared programmatically.

**Story 2: Developer Runs Benchmark Without LLMLingua**

> As a developer who hasn't installed LLMLingua, I want the benchmark runner to check for its availability at import time and set a module-level flag (`LLMLINGUA_AVAILABLE`) so that my code can gracefully degrade if the library is missing—reporting Haiku-only results instead of crashing.

---

## Implementation Design

### 1. BenchmarkResult Dataclass

The `BenchmarkResult` dataclass is the atomic unit of benchmark reporting. It captures all metrics for a single document compressed by both systems.

```python
"""
benchmarks/llmlingua_comparison.py - LLMLingua vs. Haiku Benchmark Runner
========================================================================

This module implements a head-to-head benchmark comparing Haiku Protocol
compression against Microsoft's LLMLingua on a standardized document corpus.

The module provides:
- BenchmarkResult: A dataclass for per-document benchmark results
- BenchmarkRunner: The orchestration class that runs comparisons
- Default document corpus: Three inline test documents (simple, medium, complex)
- generate_report(): Method to aggregate results into summary + details
- run_benchmarks(): Standalone function for CLI execution

Usage:
    python benchmarks/llmlingua_comparison.py

    Or programmatically:
    runner = BenchmarkRunner()
    results = runner.run_benchmark_suite(documents)
    report = runner.generate_report(results)

Environment:
    Requires OPENAI_API_KEY in .env for live encoding.
    LLMLingua is optional; graceful degradation if not installed.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
import json
import sys
from pathlib import Path

# ============================================================================
# LLMLINGUA AVAILABILITY CHECK
# ============================================================================
# Import guard: check if LLMLingua is installed. Set a module-level flag
# that subsequent code can check. This allows graceful degradation if the
# library is missing.

LLMLINGUA_AVAILABLE = False
try:
    from llmlingua import PromptCompressor
    LLMLINGUA_AVAILABLE = True
except ImportError:
    PromptCompressor = None  # type: ignore


# ============================================================================
# BENCHMARK RESULT DATA MODEL
# ============================================================================

@dataclass
class BenchmarkResult:
    """
    Represents the compression results for a single document benchmarked
    against both Haiku Protocol and LLMLingua.

    Attributes:
        document_name (str): Identifier for the document (e.g., 'simple', 'medium').
        original_tokens (int): Token count of the original uncompressed text.
        haiku_tokens (int): Token count of Haiku Protocol compressed output.
        haiku_ratio (float): Compression ratio for Haiku (0.0-1.0).
                            Formula: haiku_tokens / original_tokens.
        llmlingua_tokens (int): Token count of LLMLingua compressed output.
                               Set to original_tokens if LLMLingua unavailable.
        llmlingua_ratio (float): Compression ratio for LLMLingua (0.0-1.0).
                                Set to 1.0 if LLMLingua unavailable.
        winner (str): Which system achieved better compression.
                     Values: "haiku", "llmlingua", or "tie".
        improvement (float): Absolute difference in compression ratios.
                           Formula: llmlingua_ratio - haiku_ratio.
                           Positive means Haiku is better; negative means LLMLingua is better.

    Examples:
        >>> result = BenchmarkResult(
        ...     document_name="simple",
        ...     original_tokens=150,
        ...     haiku_tokens=45,
        ...     haiku_ratio=0.30,
        ...     llmlingua_tokens=60,
        ...     llmlingua_ratio=0.40,
        ...     winner="haiku",
        ...     improvement=0.10
        ... )
        >>> result.to_dict()
        {'document_name': 'simple', 'original_tokens': 150, ...}
    """

    document_name: str
    original_tokens: int
    haiku_tokens: int
    haiku_ratio: float
    llmlingua_tokens: int
    llmlingua_ratio: float
    winner: str  # "haiku", "llmlingua", or "tie"
    improvement: float  # llmlingua_ratio - haiku_ratio

    def to_dict(self) -> Dict:
        """
        Convert the BenchmarkResult to a dictionary suitable for JSON serialization.

        Returns:
            Dict: A dictionary representation with keys matching dataclass fields.
                  Numeric values (ratios) are rounded to 4 decimal places.

        Example:
            >>> result = BenchmarkResult(...)
            >>> d = result.to_dict()
            >>> json.dumps(d)  # Produces valid JSON
        """
        return {
            "document_name": self.document_name,
            "original_tokens": self.original_tokens,
            "haiku_tokens": self.haiku_tokens,
            "haiku_ratio": round(self.haiku_ratio, 4),
            "llmlingua_tokens": self.llmlingua_tokens,
            "llmlingua_ratio": round(self.llmlingua_ratio, 4),
            "winner": self.winner,
            "improvement": round(self.improvement, 4),
        }

    def __repr__(self) -> str:
        """
        Provide a human-readable string representation for console output.

        Returns:
            str: A formatted string showing key metrics in a readable layout.

        Example:
            >>> print(result)
            BenchmarkResult(document_name='simple', haiku_ratio=0.30,
                           llmlingua_ratio=0.40, winner='haiku',
                           improvement=+0.10)
        """
        improvement_sign = "+" if self.improvement >= 0 else ""
        return (
            f"BenchmarkResult("
            f"document_name='{self.document_name}', "
            f"haiku_ratio={self.haiku_ratio:.4f}, "
            f"llmlingua_ratio={self.llmlingua_ratio:.4f}, "
            f"winner='{self.winner}', "
            f"improvement={improvement_sign}{self.improvement:.4f})"
        )


# ============================================================================
# DEFAULT DOCUMENT CORPUS
# ============================================================================
# Three inline test documents representing simple, medium, and complex scenarios.
# These match the complexity levels established in Phase 0's benchmark samples
# but are shorter, purpose-built documents suitable for quick benchmarking.
#
# Corpus Design Rationale:
# - SIMPLE: A single, straightforward action with minimal detail.
#   Tests baseline compression on sparse text.
# - MEDIUM: A multi-step procedure with a warning and state dependencies.
#   Tests compression of procedural text with safety-critical information.
# - COMPLEX: A full Markdown document with headers, code blocks, prerequisites,
#   and warnings. Tests compression of rich, nested technical documentation.

DEFAULT_DOCUMENTS: Dict[str, str] = {
    "simple": """\
To restart the server, run the command `systemctl restart haiku-server`. \
This will stop the running process and start a new instance.
""",

    "medium": """\
Prerequisites: You must have root access to the system.

Steps:
1. Stop the running server by executing `systemctl stop haiku-server`.
2. Verify the process has terminated by checking `ps aux | grep haiku`.
3. Start the server with `systemctl start haiku-server`.
4. Confirm the server is running by checking `systemctl status haiku-server`.

WARNING: Do not force-kill the process with `kill -9` as this may corrupt the database. \
Always use systemctl stop to allow graceful shutdown.
""",

    "complex": """\
# Database Migration Procedure

## Prerequisites

- PostgreSQL 13 or later must be installed and running
- You must have administrative credentials for the database
- The application server must be offline during migration (no active connections)
- Backup the current database before proceeding: `pg_dump mydb > backup.sql`

## Step 1: Prepare the Database

Connect to the database using `psql mydb` and verify the schema version:
```
SELECT version FROM schema_versions ORDER BY id DESC LIMIT 1;
```

Expected output: The current version number. If the schema is incompatible (version < 5.0), \
abort the migration.

## Step 2: Run the Migration Script

Execute the migration script with elevated privileges:
```
psql -U postgres -d mydb -f migration_v5_to_v6.sql
```

WARNING: This operation may take several minutes depending on table size. \
Do not interrupt the process or close the connection, as this will rollback all changes \
and may leave the database in an inconsistent state.

## Step 3: Verify the Migration

After the script completes, verify the schema version again:
```
SELECT version FROM schema_versions ORDER BY id DESC LIMIT 1;
```

Expected output: version = 6.0. If the version is not 6.0, the migration failed. \
Check the error log and restore from backup.

## Step 4: Restart the Application

Once verification passes, restart the application server:
```
systemctl restart myapp-server
systemctl status myapp-server
```

Confirm the service is running without errors.
""",
}

---

## Data Model Fields Reference

| Field | Type | Description | Example Value |
|---|---|---|---|
| `document_name` | `str` | Document identifier; appears in reports and JSON output | `"complex"` |
| `original_tokens` | `int` | Token count of uncompressed input | `487` |
| `haiku_tokens` | `int` | Token count of Haiku compressed output | `142` |
| `haiku_ratio` | `float` | Compression ratio: `haiku_tokens / original_tokens` | `0.2917` |
| `llmlingua_tokens` | `int` | Token count of LLMLingua output; equals `original_tokens` if LLMLingua unavailable | `195` |
| `llmlingua_ratio` | `float` | Compression ratio: `llmlingua_tokens / original_tokens`; equals `1.0` if unavailable | `0.4005` |
| `winner` | `str` | Which system achieved better compression; values: `"haiku"`, `"llmlingua"`, `"tie"` | `"haiku"` |
| `improvement` | `float` | Absolute improvement: `llmlingua_ratio - haiku_ratio`; positive = Haiku better | `0.1088` |

---

## File Structure

The benchmark runner is organized in a single file:

```
benchmarks/
├── llmlingua_comparison.py    # Main benchmark module (contains all code)
└── results.json               # Generated output: aggregated benchmark results
```

The `llmlingua_comparison.py` file contains (in order):
1. Module docstring
2. Imports
3. LLMLINGUA_AVAILABLE flag and graceful import guard
4. BenchmarkResult dataclass (this sub-part)
5. DEFAULT_DOCUMENTS corpus (this sub-part)
6. BenchmarkRunner class (v0.3.3b)
7. report generation and run_benchmarks() function (v0.3.3c)
8. `if __name__ == "__main__":` block (v0.3.3c)

---

## Implementation Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ Benchmark Data Model (v0.3.3a) Workflow                         │
└─────────────────────────────────────────────────────────────────┘

Start
  │
  ├─► Import LLMLingua (with try/except)
  │   └─► Set LLMLINGUA_AVAILABLE = True/False
  │
  ├─► Define BenchmarkResult dataclass
  │   ├─► Fields: document_name, token counts, ratios, winner, improvement
  │   ├─► to_dict() method for JSON serialization
  │   └─► __repr__() method for console display
  │
  └─► Define DEFAULT_DOCUMENTS corpus
      ├─► "simple": 1 short sentence
      ├─► "medium": Multi-step with warning
      └─► "complex": Full Markdown with headers, code, prerequisites

Data Model Ready ──► Next: v0.3.3b (BenchmarkRunner class)
```

---

## Acceptance Criteria Verification

The v0.3.3a data model is complete when:

- [ ] `BenchmarkResult` dataclass is defined with all 8 fields
- [ ] `BenchmarkResult` is instantiable with positional or keyword arguments
- [ ] `BenchmarkResult.to_dict()` returns a valid Python dict
- [ ] `to_dict()` output is JSON-serializable (no circular refs, only base types)
- [ ] `BenchmarkResult.__repr__()` returns a readable string for console output
- [ ] `LLMLINGUA_AVAILABLE` flag is set to `True` if import succeeds, `False` otherwise
- [ ] Import guard uses try/except and does not raise exceptions even if LLMLingua is missing
- [ ] `DEFAULT_DOCUMENTS` dict contains exactly 3 documents: "simple", "medium", "complex"
- [ ] Each document in `DEFAULT_DOCUMENTS` is non-empty (len > 0)
- [ ] Corpus documents match complexity levels described (simple=1-2 sentences, medium=procedural, complex=full Markdown)

**Verification Method:** Manual inspection of code + attempting to instantiate `BenchmarkResult` and serialize to JSON.

---

## Limitations & Constraints

1. **No Custom LLMLingua Configuration:** The corpus does not provide configuration options for LLMLingua's `PromptCompressor`. The benchmark always uses default settings.

2. **Three-Document Corpus Is Demonstrative, Not Statistical:** A three-document corpus is too small for statistical significance testing. The benchmark is a proof-of-concept demonstration, not a peer-reviewed study.

3. **Numeric Precision:** All float values (ratios, improvement) are rounded to 4 decimal places in `to_dict()` output. This is sufficient for reporting and JSON serialization.

4. **Document Order Is Fixed:** The `DEFAULT_DOCUMENTS` dict is ordered in Python 3.7+. When iterated, documents will always appear in the order: "simple", "medium", "complex". This ensures reproducible report ordering.

5. **No Tokenizer Selection:** Both systems must use the same tokenizer (tiktoken with "gpt-4" encoding). The corpus does not parameterize this choice.

---

## Dependencies

**Core Dependencies:**
- `dataclasses` (Python 3.7+) — provides the `@dataclass` decorator
- `typing` — provides type hints (`Dict`, `List`, `Optional`)
- `json` — required by v0.3.3c for `results.json` serialization

**Optional Dependencies:**
- `llmlingua` — imported with try/except; graceful degradation if missing

**Code Dependencies:**
- `src/encoder.py` — `encode()` function (used by BenchmarkRunner in v0.3.3b)
- `src/validator.py` — `CompressionValidator` class (used by BenchmarkRunner in v0.3.3b)

---

## Outputs to Next Sub-Part

The v0.3.3a data model serves as the input to v0.3.3b (BenchmarkRunner):

1. **BenchmarkResult** — Used by `BenchmarkRunner.run_benchmark()` as the return type. Each document processed returns one `BenchmarkResult` instance.

2. **LLMLINGUA_AVAILABLE flag** — Used by `BenchmarkRunner.__init__()` to conditionally create a `PromptCompressor` instance (or skip it if unavailable).

3. **DEFAULT_DOCUMENTS corpus** — Used by `run_benchmarks()` function in v0.3.3c as the default documents passed to `BenchmarkRunner.run_benchmark_suite()`.

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| v0.3.3a-001 | Use `@dataclass` instead of plain Python dict for `BenchmarkResult` | Dataclass provides type safety, field validation (via post_init if needed), and explicit structure. Dicts are flexible but error-prone for structured data. | Approved |
| v0.3.3a-002 | Use try/except import guard for LLMLingua instead of checking `requirements.txt` | try/except allows graceful degradation even if the package is listed as optional. A requirements check would require reading the file and parsing versions, which is brittle. | Approved |
| v0.3.3a-003 | Embed DEFAULT_DOCUMENTS as inline strings instead of loading from files | Inline documents are self-contained, require no file I/O at runtime, and are easier to version-control. File-based documents would add I/O complexity and a dependency on file paths. For three small documents, inlining is acceptable. | Approved |

---

## Glossary

| Term | Definition |
|---|---|
| **BenchmarkResult** | A dataclass that captures compression metrics for a single document benchmarked against both Haiku and LLMLingua. |
| **LLMLINGUA_AVAILABLE** | A module-level boolean flag indicating whether the `llmlingua` library is installed and importable. Used for graceful degradation. |
| **Graceful Degradation** | When a component (LLMLingua) is missing, the system continues with reduced functionality (Haiku-only results) rather than crashing. |
| **Corpus** | A set of standard test documents used for consistent benchmarking. The DEFAULT_DOCUMENTS corpus has 3 documents. |
| **Compression Ratio** | A float between 0.0 and 1.0 representing the fraction of the original size retained after compression. Formula: `compressed_tokens / original_tokens`. |
| **Improvement** | The absolute difference in compression ratios between two systems. Positive means system A (Haiku) is better; negative means system B (LLMLingua) is better. |

---

**Document Version:** 1.0
**Last Updated:** 2026-02-09
**Author:** Haiku Protocol Project
**Status:** Pending Review

