# v0.2.1d — Integration Testing & Benchmark Validation

<aside>

**Version:** v0.2.1d

**Parent:** v0.2.1 — Chunking Module

**Status:** ⬜ Not Started

**Duration:** 25–35 minutes

**Deliverable:** End-to-end integration tests, benchmark sample corpus, performance validation, and documentation updates

</aside>

---

## Objective

Validate the complete chunking module (v0.2.1a–c) through end-to-end integration tests, benchmark corpus processing, and performance profiling. This sub-part confirms that the chunker is production-ready for the encoder pipeline by testing against realistic documents of varying sizes and structures, measuring throughput, and verifying that output format is compatible with the downstream entity extractor (v0.2.2).

---

## User Stories

> As a pipeline developer, I want integration tests that prove the chunker works end-to-end on real markdown files — not just synthetic test strings — so that I can trust it in the encoder pipeline.

> As a project maintainer, I want benchmark data showing the chunker's throughput (documents/second, chunks/second) and memory behavior so I can identify performance regressions in future versions.

> As the entity extraction module's developer, I want to verify that the chunker's output schema exactly matches what my `EntityExtractor.extract_batch()` expects as input, with no missing or extra fields.

---

## Test Corpus

### Benchmark Sample Documents

Create the following test documents in `benchmarks/samples/`:

| File | Lines | Words | Headers | Description |
|------|-------|-------|---------|-------------|
| `simple.md` | ~30 | ~150 | 3–4 `##` | Basic flat document. Single topic. |
| `nested.md` | ~80 | ~500 | 6–8 `##` + 4–6 `###` | Multi-level hierarchy. Installation guide. |
| `large.md` | ~300 | ~2000 | 15–20 `##` + 10–15 `###` | Full runbook. Mixed code blocks, tables. |
| `edge_cases.md` | ~60 | ~300 | Mixed | Tricky patterns: empty sections, adjacent headers, code blocks with headers, Unicode, deeply nested `####` |
| `real_world.md` | ~150 | ~1000 | 8–12 `##` + 5–8 `###` | Adapted from a real README or operations guide |

### Example: `benchmarks/samples/nested.md`

```markdown
# Server Installation Guide

This guide covers installing and configuring the application server.

## Prerequisites

Before beginning, ensure you have:
- Python 3.10 or higher
- PostgreSQL 14+
- 2GB RAM minimum

### System Requirements

The following table details hardware requirements:

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU       | 2 cores | 4 cores     |
| RAM       | 2 GB    | 8 GB        |
| Disk      | 10 GB   | 50 GB       |

### Software Dependencies

Install required system packages:

```bash
sudo apt update
sudo apt install python3-pip postgresql-14 nginx
```

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/example/app.git
cd app
```

### Step 2: Configure Environment

Copy the example environment file and edit:

```bash
cp .env.example .env
vi .env
```

Set the following variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Random 64-character string

## Post-Installation

### Verify Service Health

After installation, check the service status:

```bash
systemctl status app-server
```

Expected output should show `active (running)`.

### Run Smoke Tests

Execute the basic test suite:

```bash
python -m pytest tests/smoke/ -v
```

All tests should pass before proceeding to production configuration.
```

---

## Integration Tests

### Test Architecture

```
┌────────────────────────────────────────────────────────────────┐
│              INTEGRATION TEST ARCHITECTURE                     │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  tests/                                                        │
│  ├── test_chunker.py         # Unit tests (v0.2.1a-c)         │
│  └── test_chunker_integration.py  # This file (v0.2.1d)       │
│                                                                │
│  Integration test flow:                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Load sample .md files from benchmarks/samples/       │  │
│  │  2. Chunk with MarkdownChunker.chunk_with_hierarchy()    │  │
│  │  3. Assert chunk count, content preservation              │  │
│  │  4. Assert hierarchy relationships                        │  │
│  │  5. Assert output schema matches extractor input          │  │
│  │  6. Measure throughput and log performance                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Test Categories and Minimums

| Category | Tests | Description |
|----------|-------|-------------|
| **File I/O** | 3 | Load and chunk each sample file (simple, nested, large) |
| **Content Integrity** | 3 | No data loss: all non-header lines present in output chunks |
| **Hierarchy** | 3 | Parent-child relationships correct for nested.md, hierarchical depth verified |
| **Schema Compat** | 3 | Output dicts have all required keys for extractor, JSON-serializable, no extra keys |
| **Edge Cases** | 4 | Code block headers, empty sections, Unicode content, adjacent headers |
| **Performance** | 3 | Throughput > 100 docs/sec for simple.md, memory stable, large.md < 500ms |
| **Config Combos** | 3 | Level 1–6 range, preamble on/off, merge on/off with real files |
| **Idempotency** | 1 | Chunking same document twice produces identical output |
| **Extractor Handoff** | 2 | `chunk_document()` output is list of dicts, each dict has `content` key with string value |

### Example Test Code

```python
"""Integration tests for the chunking module. (v0.2.1d)"""
import json
import pathlib
import time

import pytest

from src.chunker import (
    Chunk,
    ChunkingConfig,
    MarkdownChunker,
    chunk_document,
)

SAMPLES_DIR = pathlib.Path("benchmarks/samples")


@pytest.fixture
def nested_document():
    """Load the nested.md sample document."""
    return (SAMPLES_DIR / "nested.md").read_text()


@pytest.fixture
def large_document():
    """Load the large.md sample document."""
    return (SAMPLES_DIR / "large.md").read_text()


class TestFileIntegration:
    """End-to-end tests with real markdown files. (v0.2.1d)"""

    # Acceptance Criterion: "Chunker produces expected number of chunks for nested.md"
    def test_chunk_nested_document(self, nested_document):
        """nested.md produces chunks for each ## and ### section."""
        chunker = MarkdownChunker(ChunkingConfig(min_level=2, max_level=3))
        chunks = chunker.chunk_with_hierarchy(nested_document)
        assert len(chunks) >= 8  # At least 8 sections
        assert all(isinstance(c, Chunk) for c in chunks)

    # Acceptance Criterion: "No content is lost during chunking"
    def test_content_integrity_no_data_loss(self, nested_document):
        """All non-header, non-blank lines appear in exactly one chunk."""
        chunker = MarkdownChunker(ChunkingConfig(min_level=2, max_level=3))
        chunks = chunker.chunk(nested_document)
        all_content = "\n".join(c.content for c in chunks)
        # Verify key content lines are present
        assert "Python 3.10" in all_content
        assert "PostgreSQL" in all_content
        assert "systemctl status" in all_content


class TestSchemaCompatibility:
    """Verify output matches extractor input expectations. (v0.2.1d)"""

    # Acceptance Criterion: "chunk_document() output is list of JSON-serializable dicts"
    def test_output_json_serializable(self, nested_document):
        """chunk_document() output can be JSON-serialized."""
        result = chunk_document(nested_document)
        # Should not raise
        serialized = json.dumps(result)
        assert isinstance(serialized, str)
        deserialized = json.loads(serialized)
        assert len(deserialized) == len(result)

    # Acceptance Criterion: "Each chunk dict has required keys for extractor"
    def test_output_has_extractor_required_keys(self, nested_document):
        """Each dict in output has id, title, level, content keys."""
        result = chunk_document(nested_document)
        required_keys = {"id", "title", "level", "content"}
        for chunk_dict in result:
            assert required_keys.issubset(chunk_dict.keys()), \
                f"Missing keys: {required_keys - chunk_dict.keys()}"
            assert isinstance(chunk_dict["content"], str)
            assert isinstance(chunk_dict["level"], int)


class TestPerformance:
    """Performance benchmarks. (v0.2.1d)"""

    # Acceptance Criterion: "Chunker processes simple.md in < 10ms"
    def test_throughput_simple_document(self):
        """simple.md is chunked in under 10ms."""
        doc = (SAMPLES_DIR / "simple.md").read_text()
        chunker = MarkdownChunker()

        start = time.perf_counter()
        for _ in range(100):
            chunker.chunk(doc)
        elapsed = (time.perf_counter() - start) / 100

        assert elapsed < 0.01, f"Too slow: {elapsed:.4f}s per document"

    # Acceptance Criterion: "Chunker processes large.md in < 500ms"
    def test_throughput_large_document(self, large_document):
        """large.md is chunked in under 500ms."""
        chunker = MarkdownChunker()

        start = time.perf_counter()
        chunks = chunker.chunk_with_hierarchy(large_document)
        elapsed = time.perf_counter() - start

        assert elapsed < 0.5, f"Too slow: {elapsed:.4f}s"
        assert len(chunks) > 0

    # Acceptance Criterion: "Chunking is idempotent"
    def test_idempotent_output(self, nested_document):
        """Same input always produces identical output."""
        chunker = MarkdownChunker()
        result1 = [c.to_dict() for c in chunker.chunk(nested_document)]
        result2 = [c.to_dict() for c in chunker.chunk(nested_document)]
        assert result1 == result2
```

---

## Benchmark Report Format

After integration tests pass, generate a benchmark report:

```
benchmarks/
└── results/
    └── chunker_benchmark.json
```

### Report Schema

```json
{
    "module": "chunker",
    "version": "v0.2.1d",
    "timestamp": "2026-02-10T12:00:00Z",
    "environment": {
        "python_version": "3.11.x",
        "os": "macOS"
    },
    "results": [
        {
            "document": "simple.md",
            "lines": 30,
            "words": 150,
            "chunks_produced": 4,
            "elapsed_ms": 0.5,
            "throughput_docs_per_sec": 2000
        },
        {
            "document": "nested.md",
            "lines": 80,
            "words": 500,
            "chunks_produced": 10,
            "elapsed_ms": 1.2,
            "throughput_docs_per_sec": 833
        },
        {
            "document": "large.md",
            "lines": 300,
            "words": 2000,
            "chunks_produced": 25,
            "elapsed_ms": 4.5,
            "throughput_docs_per_sec": 222
        }
    ]
}
```

---

## Documentation Updates

### Files to Update

| File | Change |
|------|--------|
| `CHANGELOG.md` | Add v0.2.1 entries (a–d summary) |
| `CLAUDE.md` | Update `ACTIVE VERSION` to `v0.2.1d` |
| `v0.2.1/README.md` | Add sub-page links + mark status ✅ |
| `v0.2.0/README.md` | Mark chunker exit criterion checked |

### Module Docstring

```python
"""
chunker.py — Document Chunking Module
======================================

Splits markdown documents into semantically bounded chunks at header
boundaries. Part of the Haiku Protocol encoder pipeline (v0.2.1).

Sub-parts:
    v0.2.1a — Chunk data model (Chunk, ChunkingConfig)
    v0.2.1b — MarkdownChunker core implementation
    v0.2.1c — Advanced features (hierarchy, merging, metadata)
    v0.2.1d — Integration testing and benchmarks

Usage:
    from src.chunker import chunk_document
    chunks = chunk_document("## Hello\\nWorld", min_level=2)
"""
```

---

## Logging Requirements

| Level | When | Example Message |
|-------|------|-----------------|
| **INFO** | Integration test suite started | Via pytest output |
| **INFO** | Benchmark result recorded | `"Benchmark: %s — %d chunks in %.1fms"` |
| **DEBUG** | Sample file loaded | `"Loaded sample: %s (%d lines, %d words)"` |
| **WARNING** | Benchmark threshold exceeded | `"Performance warning: %s took %.1fms (threshold: %dms)"` |

---

## Acceptance Criteria

- [ ] All 5 benchmark sample documents created in `benchmarks/samples/`
- [ ] `tests/test_chunker_integration.py` created with ≥25 integration tests
- [ ] All sample documents chunk successfully with no errors
- [ ] No data loss: all content lines present in output chunks
- [ ] Parent-child relationships verified for `nested.md`
- [ ] Output schema exactly matches entity extractor input requirements
- [ ] JSON round-trip (`json.dumps` → `json.loads`) preserves data
- [ ] Performance: `simple.md` < 10ms, `large.md` < 500ms
- [ ] Chunking is idempotent (same input → identical output)
- [ ] Benchmark report generated at `benchmarks/results/chunker_benchmark.json`
- [ ] All tests pass: `python -m pytest tests/test_chunker_integration.py -v`
- [ ] Module docstring updated with sub-part summary
- [ ] `CHANGELOG.md` updated with v0.2.1 entries
- [ ] `CLAUDE.md` active version updated to `v0.2.1d`
- [ ] `v0.2.1/README.md` updated with sub-page links

---

## Dependencies

**Must be completed before v0.2.1d:**
- v0.2.1a — Chunk Data Model & Interfaces
- v0.2.1b — MarkdownChunker Core Implementation
- v0.2.1c — Advanced Chunking Features

---

## Outputs to v0.2.2

**For v0.2.2 — Entity Extraction:**
- Complete, tested chunking module at `src/chunker.py`
- `chunk_document()` convenience function for simple usage
- `chunk_with_hierarchy()` for full-featured usage
- Benchmark samples available for extractor testing
- Schema compatibility proven via integration tests

---

## Decision Log

| Decision | Rationale | Status |
|----------|-----------|--------|
| Separate integration tests from unit tests | Unit tests use synthetic strings; integration tests use real files. Separation enables `pytest -m unit` for fast CI | ✅ Approved |
| 5 sample documents of increasing complexity | Covers flat, nested, large, edge-case, and real-world document types | ✅ Approved |
| JSON benchmark report format | Machine-readable; can be consumed by CI dashboards in later phases | ✅ Approved |
| Performance thresholds (10ms simple, 500ms large) | Conservative thresholds; regex-based chunker should be far faster | ✅ Approved |
| Test schema compatibility explicitly | Prevents integration bugs between chunker and extractor at the handoff boundary | ✅ Approved |
