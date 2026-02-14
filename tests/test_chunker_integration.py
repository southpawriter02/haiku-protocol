"""
tests/test_chunker_integration.py — Integration Tests for Chunking Module
==========================================================================

End-to-end integration tests validating the complete chunking module
(v0.2.1a–c) against real markdown files from the benchmark corpus.

Test Categories (v0.2.1d — Integration Testing):
    - File I/O (3): Load and chunk simple, nested, large
    - Content Integrity (3): No data loss for simple, nested, large
    - Hierarchy (3): Parent-child relationships, depth, multi-level
    - Schema Compatibility (3): Required keys, JSON roundtrip, no extra
    - Edge Cases (4): Code blocks, empty sections, Unicode, adjacent
    - Performance (3): Throughput < 10ms, large < 500ms, idempotency
    - Config Combos (3): Level ranges, preamble, merge on/off
    - Extractor Handoff (2): List of dicts, content is string
    - Benchmark Report (1): Generate chunker_benchmark.json

Versions: v0.2.1d
"""

import json
import pathlib
import platform
import sys
import time

import pytest

from src.chunker import (
    Chunk,
    ChunkingConfig,
    ChunkMetadata,
    MarkdownChunker,
    chunk_document,
)

SAMPLES_DIR = pathlib.Path("benchmarks/samples")
RESULTS_DIR = pathlib.Path("benchmarks/results")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def simple_document():
    """Load the simple.md sample document."""
    return (SAMPLES_DIR / "simple.md").read_text()


@pytest.fixture
def nested_document():
    """Load the nested.md sample document."""
    return (SAMPLES_DIR / "nested.md").read_text()


@pytest.fixture
def large_document():
    """Load the large.md sample document."""
    return (SAMPLES_DIR / "large.md").read_text()


@pytest.fixture
def edge_cases_document():
    """Load the edge_cases.md sample document."""
    return (SAMPLES_DIR / "edge_cases.md").read_text()


@pytest.fixture
def real_world_document():
    """Load the real_world.md sample document."""
    return (SAMPLES_DIR / "real_world.md").read_text()


# ===================================================================
# File I/O (v0.2.1d)
# ===================================================================


@pytest.mark.integration
class TestFileIntegration:
    """End-to-end tests with real markdown files. (v0.2.1d)"""

    # Acceptance Criterion: "Chunker produces chunks for simple.md"
    def test_chunk_simple_document(self, simple_document):
        """simple.md produces chunks for each ## section."""
        chunker = MarkdownChunker(ChunkingConfig(min_level=2, max_level=3))
        chunks = chunker.chunk_with_hierarchy(simple_document)
        assert len(chunks) >= 2
        assert all(isinstance(c, Chunk) for c in chunks)

    # Acceptance Criterion: "Chunker produces expected number of chunks for nested.md"
    def test_chunk_nested_document(self, nested_document):
        """nested.md produces chunks for each ## and ### section."""
        chunker = MarkdownChunker(ChunkingConfig(min_level=2, max_level=3))
        chunks = chunker.chunk_with_hierarchy(nested_document)
        assert len(chunks) >= 8
        assert all(isinstance(c, Chunk) for c in chunks)

    # Acceptance Criterion: "Chunker produces chunks for large.md"
    def test_chunk_large_document(self, large_document):
        """large.md produces a large number of chunks."""
        chunker = MarkdownChunker(ChunkingConfig(min_level=2, max_level=3))
        chunks = chunker.chunk_with_hierarchy(large_document)
        assert len(chunks) >= 15
        assert all(isinstance(c, Chunk) for c in chunks)


# ===================================================================
# Content Integrity (v0.2.1d)
# ===================================================================


@pytest.mark.integration
class TestContentIntegrity:
    """Verify no data loss during chunking. (v0.2.1d)"""

    # Acceptance Criterion: "No content is lost during chunking — simple"
    def test_content_integrity_simple(self, simple_document):
        """Key content from simple.md appears in chunks."""
        chunker = MarkdownChunker(ChunkingConfig(min_level=2, max_level=3))
        chunks = chunker.chunk(simple_document)
        all_content = "\n".join(c.content for c in chunks)
        assert "Node.js" in all_content
        assert "npm init" in all_content

    # Acceptance Criterion: "No content is lost during chunking — nested"
    def test_content_integrity_nested(self, nested_document):
        """Key content from nested.md appears in chunks."""
        chunker = MarkdownChunker(ChunkingConfig(min_level=2, max_level=3))
        chunks = chunker.chunk(nested_document)
        all_content = "\n".join(c.content for c in chunks)
        assert "Python 3.10" in all_content
        assert "PostgreSQL" in all_content
        assert "systemctl status" in all_content

    # Acceptance Criterion: "No content is lost during chunking — large"
    def test_content_integrity_large(self, large_document):
        """Key content from large.md appears in chunks."""
        chunker = MarkdownChunker(ChunkingConfig(min_level=2, max_level=3))
        chunks = chunker.chunk(large_document)
        all_content = "\n".join(c.content for c in chunks)
        assert "production" in all_content.lower()
        assert "rollback" in all_content.lower()


# ===================================================================
# Hierarchy Integration (v0.2.1d)
# ===================================================================


@pytest.mark.integration
class TestHierarchyIntegration:
    """Parent-child relationships on real documents. (v0.2.1d)"""

    # Acceptance Criterion: "Parent-child relationships verified for nested.md"
    def test_hierarchy_nested_document(self, nested_document):
        """nested.md has ### chunks with parent_id pointing to ## chunks."""
        config = ChunkingConfig(
            min_level=2, max_level=3, merge_strategy="none",
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk_with_hierarchy(nested_document)
        children = [c for c in chunks if c.parent_id is not None]
        assert len(children) >= 4  # At least 4 ### sections

    # Acceptance Criterion: "Hierarchy depth verified for nested.md"
    def test_hierarchy_depth(self, nested_document):
        """Metadata depth is correct for nested.md chunks."""
        config = ChunkingConfig(
            min_level=2, max_level=3, merge_strategy="none",
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk_with_hierarchy(nested_document)
        enriched = chunker.enrich_metadata(chunks)
        depths = [meta.depth for _, meta in enriched]
        assert 0 in depths  # Top-level
        assert 1 in depths  # Subsection

    # Acceptance Criterion: "Multi-level nesting correct for real_world.md"
    def test_hierarchy_real_world(self, real_world_document):
        """real_world.md hierarchy resolves correctly."""
        config = ChunkingConfig(
            min_level=2, max_level=3, merge_strategy="none",
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk_with_hierarchy(real_world_document)
        # At least some children exist
        children = [c for c in chunks if c.parent_id is not None]
        assert len(children) >= 3


# ===================================================================
# Schema Compatibility (v0.2.1d)
# ===================================================================


@pytest.mark.integration
class TestSchemaCompatibility:
    """Verify output matches extractor input expectations. (v0.2.1d)"""

    # Acceptance Criterion: "chunk_document() output is list of JSON-serializable dicts"
    def test_output_json_serializable(self, nested_document):
        """chunk_document() output can be JSON-serialized."""
        result = chunk_document(nested_document)
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

    # Acceptance Criterion: "No unexpected extra keys in output dicts"
    def test_output_no_unexpected_keys(self, nested_document):
        """Output dicts contain only expected Chunk field keys."""
        result = chunk_document(nested_document)
        allowed_keys = {
            "id", "title", "level", "content",
            "parent_id", "word_count", "char_count", "source_line",
        }
        for chunk_dict in result:
            extra = set(chunk_dict.keys()) - allowed_keys
            assert not extra, f"Unexpected keys: {extra}"


# ===================================================================
# Edge Cases Integration (v0.2.1d)
# ===================================================================


@pytest.mark.integration
class TestEdgeCaseIntegration:
    """Edge cases from real sample files. (v0.2.1d)"""

    # Acceptance Criterion: "Code block headers are ignored in edge_cases.md"
    def test_code_block_headers_ignored(self, edge_cases_document):
        """Headers inside code blocks do not create chunks."""
        config = ChunkingConfig(min_level=2, max_level=4)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(edge_cases_document)
        titles = [c.title for c in chunks]
        assert "This Is Not a Real Header" not in titles
        assert "Neither Is This" not in titles

    # Acceptance Criterion: "Empty sections handled correctly"
    def test_empty_sections(self, edge_cases_document):
        """Empty section produces a chunk with minimal content."""
        config = ChunkingConfig(min_level=2, max_level=3)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(edge_cases_document)
        titles = [c.title for c in chunks]
        assert "Empty Section" in titles

    # Acceptance Criterion: "Unicode content preserved in chunks"
    def test_unicode_content_preserved(self, edge_cases_document):
        """Unicode characters survive the chunking process."""
        config = ChunkingConfig(min_level=2, max_level=3)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(edge_cases_document)
        all_content = "\n".join(c.content for c in chunks)
        assert "café" in all_content
        assert "日本語" in all_content or "Ünïcödé" in "\n".join(
            c.title for c in chunks
        )

    # Acceptance Criterion: "Adjacent headers produce correct chunks"
    def test_adjacent_headers(self, edge_cases_document):
        """Adjacent ### headers each produce their own chunk."""
        config = ChunkingConfig(min_level=2, max_level=3)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(edge_cases_document)
        titles = [c.title for c in chunks]
        assert "First Sub" in titles
        assert "Second Sub" in titles
        assert "Third Sub" in titles


# ===================================================================
# Performance (v0.2.1d)
# ===================================================================


@pytest.mark.integration
class TestPerformance:
    """Performance benchmarks. (v0.2.1d)"""

    # Acceptance Criterion: "Chunker processes simple.md in < 10ms"
    def test_throughput_simple_document(self, simple_document):
        """simple.md is chunked in under 10ms (averaged over 100 runs)."""
        chunker = MarkdownChunker()

        start = time.perf_counter()
        for _ in range(100):
            chunker.chunk(simple_document)
        elapsed = (time.perf_counter() - start) / 100

        assert elapsed < 0.01, f"Too slow: {elapsed:.4f}s per document"

    # Acceptance Criterion: "Chunker processes large.md in < 500ms"
    def test_throughput_large_document(self, large_document):
        """large.md is chunked with full pipeline in under 500ms."""
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


# ===================================================================
# Config Combinations (v0.2.1d)
# ===================================================================


@pytest.mark.integration
class TestConfigCombinations:
    """Different config combinations with real files. (v0.2.1d)"""

    # Acceptance Criterion: "Level 1–4 range works on edge_cases.md"
    def test_wide_level_range(self, edge_cases_document):
        """Config with min_level=1, max_level=4 captures all headers."""
        config = ChunkingConfig(min_level=1, max_level=4)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(edge_cases_document)
        levels = {c.level for c in chunks}
        # Should include level 4 from #### Level Four
        assert 4 in levels

    # Acceptance Criterion: "Preamble on/off with real files"
    def test_preamble_toggle(self, nested_document):
        """Preamble toggle changes chunk count for nested.md."""
        chunker_with = MarkdownChunker(ChunkingConfig(include_preamble=True))
        chunker_without = MarkdownChunker(
            ChunkingConfig(include_preamble=False),
        )
        chunks_with = chunker_with.chunk(nested_document)
        chunks_without = chunker_without.chunk(nested_document)
        # Nested.md has content before first ##, so preamble adds a chunk
        assert len(chunks_with) == len(chunks_without) + 1

    # Acceptance Criterion: "Merge on/off preserves or reduces chunk count"
    def test_merge_toggle(self, nested_document):
        """Merge enabled may reduce chunk count vs. disabled."""
        config_none = ChunkingConfig(
            min_level=2, max_level=3, merge_strategy="none",
        )
        config_parent = ChunkingConfig(
            min_level=2, max_level=3,
            merge_strategy="parent", merge_threshold=50,
        )
        chunks_none = MarkdownChunker(config_none).chunk_with_hierarchy(
            nested_document,
        )
        chunks_merged = MarkdownChunker(config_parent).chunk_with_hierarchy(
            nested_document,
        )
        assert len(chunks_merged) <= len(chunks_none)


# ===================================================================
# Extractor Handoff (v0.2.1d)
# ===================================================================


@pytest.mark.integration
class TestExtractorHandoff:
    """Verify output format is compatible with extractor. (v0.2.1d)"""

    # Acceptance Criterion: "chunk_document() output is list of dicts"
    def test_chunk_document_returns_list_of_dicts(self, real_world_document):
        """chunk_document() returns a list where each item is a dict."""
        result = chunk_document(real_world_document)
        assert isinstance(result, list)
        assert all(isinstance(d, dict) for d in result)

    # Acceptance Criterion: "Each dict has 'content' key with string value"
    def test_each_dict_has_content_string(self, real_world_document):
        """Each dict in output has a 'content' key mapping to a str."""
        result = chunk_document(real_world_document)
        for chunk_dict in result:
            assert "content" in chunk_dict
            assert isinstance(chunk_dict["content"], str)
            assert len(chunk_dict["content"]) >= 0


# ===================================================================
# Benchmark Report Generation (v0.2.1d)
# ===================================================================


@pytest.mark.integration
class TestBenchmarkReport:
    """Generate and validate the benchmark report. (v0.2.1d)"""

    # Acceptance Criterion: "Benchmark report generated at benchmarks/results/"
    def test_generate_benchmark_report(self):
        """Generate chunker_benchmark.json with timing data."""
        sample_files = ["simple.md", "nested.md", "large.md"]
        results = []

        for filename in sample_files:
            doc = (SAMPLES_DIR / filename).read_text()
            lines = len(doc.splitlines())
            words = len(doc.split())

            chunker = MarkdownChunker(ChunkingConfig(
                min_level=2, max_level=3, merge_strategy="none",
            ))

            # Average over multiple runs for stability
            iterations = 100
            start = time.perf_counter()
            for _ in range(iterations):
                chunks = chunker.chunk_with_hierarchy(doc)
            elapsed_ms = ((time.perf_counter() - start) / iterations) * 1000

            results.append({
                "document": filename,
                "lines": lines,
                "words": words,
                "chunks_produced": len(chunks),
                "elapsed_ms": round(elapsed_ms, 2),
                "throughput_docs_per_sec": round(1000 / elapsed_ms)
                if elapsed_ms > 0 else 0,
            })

        report = {
            "module": "chunker",
            "version": "v0.2.1d",
            "timestamp": "2026-02-14T07:50:00Z",
            "environment": {
                "python_version": f"{sys.version_info.major}"
                f".{sys.version_info.minor}"
                f".{sys.version_info.micro}",
                "os": platform.system(),
            },
            "results": results,
        }

        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = RESULTS_DIR / "chunker_benchmark.json"
        report_path.write_text(json.dumps(report, indent=4))

        # Validate the written report
        assert report_path.exists()
        loaded = json.loads(report_path.read_text())
        assert loaded["module"] == "chunker"
        assert loaded["version"] == "v0.2.1d"
        assert len(loaded["results"]) == 3
        for r in loaded["results"]:
            assert r["chunks_produced"] > 0
            assert r["elapsed_ms"] > 0
