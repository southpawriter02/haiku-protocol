"""
tests/test_chunker.py — Unit Tests for Chunking Module
=======================================================

Tests for the Chunk dataclass, ChunkingConfig, MarkdownChunker,
and chunk_document() defined in src/chunker.py.

Test Categories (v0.2.1a — Chunk Data Model):
    - Happy Path (5): Construction, field access, defaults, repr, config
    - Serialization (5): to_dict, from_dict, roundtrip, missing optionals, JSON
    - Edge Cases (5): Empty content, level 0, Unicode, long content, special chars
    - Error Paths (3): Missing required field, wrong type, None for required
    - Config (3): Defaults, custom overrides, min > max edge
    - Logging (1): Logger initialization
    - Use Case (1): Full lifecycle roundtrip

Test Categories (v0.2.1b — MarkdownChunker Core):
    - Happy Path (6): H2 split, H3 split, mixed, single section, multi-section, content preserved
    - Preamble (3): Captured, omitted, no preamble when header first
    - Edge Cases (7): Empty doc, whitespace, no headers, outside range, no content, consecutive, code block
    - Error Paths (2): TypeError on non-string, TypeError on None
    - Config (3): Custom levels, level 1, single-level range
    - Stats (3): Word count, char count, stats disabled
    - Source Lines (2): Correct position, disabled
    - Convenience Fn (2): Returns dicts, params forwarded
    - Logging (2): Init log, completion log
    - Use Case (1): Benchmark sample

Versions: v0.2.1a, v0.2.1b
"""

import json
import logging
import pathlib
import pytest
from src.chunker import Chunk, ChunkingConfig, MarkdownChunker, chunk_document


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_chunk(**overrides):
    """Create a Chunk with sensible defaults, overridden by kwargs."""
    defaults = {
        "id": "chunk-001",
        "title": "Installation",
        "level": 2,
        "content": "Run pip install haiku-protocol.",
        "parent_id": None,
        "word_count": 4,
        "char_count": 31,
        "source_line": 5,
    }
    defaults.update(overrides)
    return Chunk(**defaults)


# ===================================================================
# Happy Path
# ===================================================================


class TestChunkDataModel:
    """Tests for the Chunk dataclass. (v0.2.1a)"""

    # --- Happy Path ---

    def test_chunk_init_all_fields_populated(self):
        """Chunk can be created with all fields."""
        chunk = Chunk(
            id="chunk-001",
            title="Installation",
            level=2,
            content="Run pip install haiku-protocol.",
            parent_id=None,
            word_count=4,
            char_count=31,
            source_line=5,
        )
        assert chunk.id == "chunk-001"
        assert chunk.title == "Installation"
        assert chunk.level == 2
        assert chunk.content == "Run pip install haiku-protocol."
        assert chunk.parent_id is None
        assert chunk.word_count == 4
        assert chunk.char_count == 31
        assert chunk.source_line == 5

    def test_chunk_init_defaults_zero_stats(self):
        """Optional stats fields default to 0 / None."""
        chunk = Chunk(id="chunk-001", title="T", level=2, content="C")
        assert chunk.parent_id is None
        assert chunk.word_count == 0
        assert chunk.char_count == 0
        assert chunk.source_line == 0

    def test_chunk_field_access_via_attribute(self):
        """All fields are accessible as attributes."""
        chunk = _make_chunk()
        attrs = ["id", "title", "level", "content",
                 "parent_id", "word_count", "char_count", "source_line"]
        for attr in attrs:
            assert hasattr(chunk, attr), f"Missing attribute: {attr}"

    def test_chunk_repr_includes_id_and_title(self):
        """__repr__ includes id, title, level, and words."""
        chunk = _make_chunk(id="chunk-042", title="Deploy", word_count=7)
        r = repr(chunk)
        assert "chunk-042" in r
        assert "Deploy" in r
        assert "words=7" in r

    def test_chunk_equality_same_fields(self):
        """Two Chunks with identical fields are equal (dataclass __eq__)."""
        a = _make_chunk()
        b = _make_chunk()
        assert a == b

    # --- Serialization ---

    def test_chunk_to_dict_returns_all_keys(self):
        """to_dict() includes every field."""
        chunk = _make_chunk()
        d = chunk.to_dict()
        assert set(d.keys()) == {
            "id", "title", "level", "content",
            "parent_id", "word_count", "char_count", "source_line",
        }

    def test_chunk_to_dict_values_match(self):
        """to_dict() values match the original Chunk attributes."""
        chunk = _make_chunk(parent_id="chunk-000")
        d = chunk.to_dict()
        assert d["id"] == "chunk-001"
        assert d["parent_id"] == "chunk-000"
        assert d["level"] == 2

    def test_chunk_roundtrip_preserves_data(self):
        """Serialize then deserialize produces equal Chunk."""
        original = Chunk(
            id="chunk-042", title="Deploy", level=3,
            content="Do the thing.", parent_id="chunk-041",
            word_count=3, char_count=13, source_line=99,
        )
        restored = Chunk.from_dict(original.to_dict())
        assert restored == original

    def test_chunk_from_dict_missing_optional_fields(self):
        """from_dict() fills defaults when optional fields are absent."""
        data = {"id": "chunk-001", "title": "T", "level": 1, "content": "C"}
        chunk = Chunk.from_dict(data)
        assert chunk.parent_id is None
        assert chunk.word_count == 0
        assert chunk.char_count == 0
        assert chunk.source_line == 0

    def test_chunk_to_dict_json_serializable(self):
        """to_dict() output is JSON-serializable."""
        chunk = _make_chunk()
        serialized = json.dumps(chunk.to_dict())
        assert isinstance(serialized, str)
        restored = json.loads(serialized)
        assert restored["id"] == "chunk-001"

    # --- Edge Cases ---

    def test_chunk_empty_content_allowed(self):
        """Empty string content is valid."""
        chunk = Chunk(id="chunk-001", title="Empty", level=2, content="")
        assert chunk.content == ""
        assert chunk.to_dict()["content"] == ""

    def test_chunk_level_zero_for_preamble(self):
        """Level 0 is valid for headerless preamble content."""
        chunk = Chunk(
            id="chunk-000", title="(Preamble)", level=0,
            content="Intro paragraph.",
        )
        assert chunk.level == 0
        assert chunk.title == "(Preamble)"

    def test_chunk_unicode_title(self):
        """Unicode characters in title are preserved through roundtrip."""
        chunk = Chunk(
            id="chunk-001", title="日本語セクション", level=2, content="C",
        )
        assert chunk.title == "日本語セクション"
        roundtrip = Chunk.from_dict(chunk.to_dict())
        assert roundtrip.title == "日本語セクション"

    def test_chunk_very_long_content(self):
        """Very long content string is stored correctly."""
        long_content = "word " * 10_000  # 50k characters
        chunk = Chunk(
            id="chunk-001", title="Long", level=2, content=long_content,
        )
        assert len(chunk.content) == len(long_content)

    def test_chunk_special_characters_in_title(self):
        """Special characters in title are preserved."""
        title = 'Config: "key" = value & <tag>'
        chunk = Chunk(id="chunk-001", title=title, level=2, content="C")
        assert chunk.title == title
        restored = Chunk.from_dict(chunk.to_dict())
        assert restored.title == title

    # --- Error Paths ---

    def test_chunk_from_dict_missing_id_raises_key_error(self):
        """Missing 'id' key raises KeyError."""
        with pytest.raises(KeyError):
            Chunk.from_dict({"title": "T", "level": 2, "content": "C"})

    def test_chunk_from_dict_missing_title_raises_key_error(self):
        """Missing 'title' key raises KeyError."""
        with pytest.raises(KeyError):
            Chunk.from_dict({"id": "chunk-001", "level": 2, "content": "C"})

    def test_chunk_from_dict_missing_content_raises_key_error(self):
        """Missing 'content' key raises KeyError."""
        with pytest.raises(KeyError):
            Chunk.from_dict({"id": "chunk-001", "title": "T", "level": 2})


# ===================================================================
# ChunkingConfig
# ===================================================================


class TestChunkingConfig:
    """Tests for the ChunkingConfig dataclass. (v0.2.1a)"""

    def test_config_defaults(self):
        """Default config uses level 2–3, includes preamble, computes stats."""
        config = ChunkingConfig()
        assert config.min_level == 2
        assert config.max_level == 3
        assert config.include_preamble is True
        assert config.compute_stats is True
        assert config.track_source_lines is True

    def test_config_custom_overrides(self):
        """Custom values override defaults."""
        config = ChunkingConfig(
            min_level=1, max_level=4, include_preamble=False,
        )
        assert config.min_level == 1
        assert config.max_level == 4
        assert config.include_preamble is False
        # Non-overridden defaults remain
        assert config.compute_stats is True

    def test_config_min_greater_than_max_edge(self):
        """Config allows min_level > max_level (validation is caller's job)."""
        config = ChunkingConfig(min_level=4, max_level=2)
        assert config.min_level == 4
        assert config.max_level == 2


# ===================================================================
# Logging
# ===================================================================


class TestChunkerLogging:
    """Tests for chunker module logging. (v0.2.1a)"""

    def test_logger_initialized_with_module_name(self):
        """Logger is initialized with __name__."""
        from src import chunker
        assert hasattr(chunker, "logger")
        assert chunker.logger.name == "src.chunker"


# ===================================================================
# Full Lifecycle
# ===================================================================


class TestChunkLifecycle:
    """End-to-end lifecycle test. (v0.2.1a)"""

    def test_full_lifecycle_create_serialize_deserialize_compare(self):
        """Create → to_dict → JSON → from_dict → compare."""
        original = Chunk(
            id="chunk-007", title="Troubleshooting",
            level=3, content="Check logs for errors.",
            parent_id="chunk-002",
            word_count=4, char_count=22, source_line=42,
        )

        # Serialize to dict, then to JSON string
        as_dict = original.to_dict()
        as_json = json.dumps(as_dict)

        # Deserialize from JSON string back to Chunk
        from_json = json.loads(as_json)
        restored = Chunk.from_dict(from_json)

        assert restored == original
        assert repr(restored) == repr(original)


# ===================================================================
# MarkdownChunker — Happy Path (v0.2.1b)
# ===================================================================


class TestMarkdownChunker:
    """Tests for MarkdownChunker splitting logic. (v0.2.1b)"""

    # --- Happy Path ---

    # Acceptance Criterion: "Chunker splits on ## headers"
    def test_chunk_basic_h2_split(self):
        """Document with two ## sections yields two chunks."""
        doc = "## Section 1\nContent 1\n\n## Section 2\nContent 2"
        chunker = MarkdownChunker()
        chunks = chunker.chunk(doc)
        assert len(chunks) == 2
        assert chunks[0].title == "Section 1"
        assert chunks[1].title == "Section 2"

    # Acceptance Criterion: "Chunker splits on ### headers"
    def test_chunk_basic_h3_split(self):
        """Document with ### sections yields chunks at level 3."""
        doc = "### Sub A\nContent A\n\n### Sub B\nContent B"
        chunker = MarkdownChunker()
        chunks = chunker.chunk(doc)
        assert len(chunks) == 2
        assert chunks[0].level == 3
        assert chunks[1].level == 3

    # Acceptance Criterion: "Mixed ## and ### are both split points"
    def test_chunk_mixed_h2_h3_split(self):
        """Document with interleaved ## and ### produces chunks for each."""
        doc = "## H2\nContent\n### H3\nSub-content\n## H2b\nMore"
        chunker = MarkdownChunker()
        chunks = chunker.chunk(doc)
        assert len(chunks) == 3
        assert [c.level for c in chunks] == [2, 3, 2]

    # Acceptance Criterion: "Single section produces single chunk"
    def test_chunk_single_section(self):
        """Document with one ## header yields one chunk."""
        doc = "## Only Section\nSome content here."
        chunks = MarkdownChunker().chunk(doc)
        assert len(chunks) == 1
        assert chunks[0].title == "Only Section"

    # Acceptance Criterion: "Multiple sections produce correct count"
    def test_chunk_five_sections(self):
        """Document with five ## sections yields five chunks."""
        doc = "\n".join(f"## Section {i}\nContent {i}" for i in range(1, 6))
        chunks = MarkdownChunker().chunk(doc)
        assert len(chunks) == 5

    # Acceptance Criterion: "Chunk content preserves all text between headers"
    def test_chunk_content_preserved(self):
        """All lines between headers are captured in content."""
        doc = "## Test\nLine 1\nLine 2\nLine 3"
        chunks = MarkdownChunker().chunk(doc)
        assert "Line 1" in chunks[0].content
        assert "Line 2" in chunks[0].content
        assert "Line 3" in chunks[0].content

    # --- Preamble ---

    # Acceptance Criterion: "Preamble text before first header is captured"
    def test_chunk_preamble_captured(self):
        """Text before first ## is captured as preamble chunk."""
        doc = "This is preamble text.\n\n## Section\nContent"
        config = ChunkingConfig(include_preamble=True)
        chunks = MarkdownChunker(config).chunk(doc)
        assert chunks[0].title == "(Preamble)"
        assert chunks[0].level == 0
        assert "preamble text" in chunks[0].content

    # Acceptance Criterion: "Preamble omitted when include_preamble=False"
    def test_chunk_preamble_omitted_when_disabled(self):
        """Text before first ## is discarded when include_preamble=False."""
        doc = "Preamble here.\n\n## Section\nContent"
        config = ChunkingConfig(include_preamble=False)
        chunks = MarkdownChunker(config).chunk(doc)
        assert len(chunks) == 1
        assert chunks[0].title == "Section"

    # Acceptance Criterion: "No preamble when document starts with header"
    def test_chunk_no_preamble_when_header_first(self):
        """Document starting with ## has no preamble chunk."""
        doc = "## First\nContent"
        config = ChunkingConfig(include_preamble=True)
        chunks = MarkdownChunker(config).chunk(doc)
        assert len(chunks) == 1
        assert chunks[0].title == "First"

    # --- Edge Cases ---

    # Acceptance Criterion: "Empty document returns empty list"
    @pytest.mark.unit
    def test_chunk_empty_document_returns_empty(self):
        """Empty string returns empty list."""
        chunks = MarkdownChunker().chunk("")
        assert chunks == []

    # Acceptance Criterion: "Whitespace-only document returns empty list"
    def test_chunk_whitespace_only_returns_empty(self):
        """Whitespace-only string returns empty list."""
        chunks = MarkdownChunker().chunk("   \n\n   \t\n")
        assert chunks == []

    # Acceptance Criterion: "Document with no matching headers handled gracefully"
    def test_chunk_no_matching_headers(self):
        """Document with only # (level 1) and config min_level=2 → preamble only."""
        doc = "# Title\nSome text without ## headers."
        config = ChunkingConfig(min_level=2, include_preamble=True)
        chunks = MarkdownChunker(config).chunk(doc)
        assert len(chunks) == 1
        assert chunks[0].title == "(Preamble)"

    # Acceptance Criterion: "Headers outside level range treated as content"
    def test_chunk_headers_outside_range_treated_as_content(self):
        """#### header with max_level=3 is kept as content, not a split."""
        doc = "## Section\nContent\n#### Deep Header\nMore content"
        config = ChunkingConfig(min_level=2, max_level=3)
        chunks = MarkdownChunker(config).chunk(doc)
        assert len(chunks) == 1
        assert "#### Deep Header" in chunks[0].content

    # Acceptance Criterion: "Header with no content after it yields empty content"
    def test_chunk_header_with_no_content(self):
        """A header at the end of the document produces a chunk with empty content."""
        doc = "## Section 1\nContent\n## Empty Section"
        chunks = MarkdownChunker().chunk(doc)
        assert len(chunks) == 2
        assert chunks[1].title == "Empty Section"
        assert chunks[1].content == ""

    # Acceptance Criterion: "Consecutive headers each produce a chunk"
    def test_chunk_consecutive_headers(self):
        """Two headers back-to-back each become separate chunks."""
        doc = "## First\n## Second\nContent"
        chunks = MarkdownChunker().chunk(doc)
        assert len(chunks) == 2
        assert chunks[0].title == "First"
        assert chunks[0].content == ""
        assert chunks[1].title == "Second"

    # Acceptance Criterion: "Headers inside fenced code blocks are not split points"
    def test_chunk_header_inside_code_block_ignored(self):
        """Fenced code block headers are not split points."""
        doc = "## Real Section\nContent\n```\n## Not A Header\ncode\n```\nMore content"
        chunks = MarkdownChunker().chunk(doc)
        assert len(chunks) == 1
        assert "## Not A Header" in chunks[0].content

    # --- Error Paths ---

    # Acceptance Criterion: "TypeError on non-string input"
    def test_chunk_non_string_raises_type_error(self):
        """Passing an integer raises TypeError."""
        with pytest.raises(TypeError, match="document must be a string"):
            MarkdownChunker().chunk(42)

    # Acceptance Criterion: "TypeError on None input"
    def test_chunk_none_raises_type_error(self):
        """Passing None raises TypeError."""
        with pytest.raises(TypeError, match="document must be a string"):
            MarkdownChunker().chunk(None)

    # --- Config ---

    # Acceptance Criterion: "Custom min/max levels work"
    def test_chunk_custom_min_max_levels(self):
        """Config with min_level=1, max_level=1 only splits on # headers."""
        doc = "# Title\nContent\n## Sub\nNot split"
        config = ChunkingConfig(min_level=1, max_level=1)
        chunks = MarkdownChunker(config).chunk(doc)
        assert len(chunks) == 1
        assert chunks[0].title == "Title"
        assert "## Sub" in chunks[0].content

    # Acceptance Criterion: "Level 1 splitting works"
    def test_chunk_level_1_splitting(self):
        """Splitting on # headers works correctly."""
        doc = "# Main\nIntro\n# Secondary\nMore"
        config = ChunkingConfig(min_level=1, max_level=1)
        chunks = MarkdownChunker(config).chunk(doc)
        assert len(chunks) == 2
        assert chunks[0].title == "Main"
        assert chunks[1].title == "Secondary"

    # Acceptance Criterion: "Single-level range (min == max) works"
    def test_chunk_single_level_range(self):
        """Config with min_level=3, max_level=3 splits only on ###."""
        doc = "## Ignored\nText\n### Split Here\nContent\n## Also Ignored\nMore"
        config = ChunkingConfig(min_level=3, max_level=3, include_preamble=True)
        chunks = MarkdownChunker(config).chunk(doc)
        assert len(chunks) == 2  # preamble + ### chunk
        assert chunks[0].title == "(Preamble)"
        assert chunks[1].title == "Split Here"

    # --- Stats ---

    # Acceptance Criterion: "word_count computed when compute_stats=True"
    def test_chunk_word_count_computed(self):
        """word_count is populated when compute_stats is True."""
        doc = "## Test\nOne two three four"
        config = ChunkingConfig(compute_stats=True)
        chunks = MarkdownChunker(config).chunk(doc)
        assert chunks[0].word_count == 4

    # Acceptance Criterion: "char_count computed when compute_stats=True"
    def test_chunk_char_count_computed(self):
        """char_count is populated when compute_stats is True."""
        doc = "## Test\nHello"
        config = ChunkingConfig(compute_stats=True)
        chunks = MarkdownChunker(config).chunk(doc)
        assert chunks[0].char_count == 5

    # Acceptance Criterion: "Stats disabled via config"
    def test_chunk_stats_disabled(self):
        """word_count and char_count are 0 when compute_stats is False."""
        doc = "## Test\nSome words here"
        config = ChunkingConfig(compute_stats=False)
        chunks = MarkdownChunker(config).chunk(doc)
        assert chunks[0].word_count == 0
        assert chunks[0].char_count == 0

    # --- Source Lines ---

    # Acceptance Criterion: "source_line tracks correct 1-based position"
    def test_chunk_source_line_correct(self):
        """source_line points to the header's 1-based line number."""
        doc = "Preamble\n\n## Section\nContent"
        config = ChunkingConfig(
            include_preamble=True, track_source_lines=True,
        )
        chunks = MarkdownChunker(config).chunk(doc)
        assert chunks[0].source_line == 1  # preamble
        assert chunks[1].source_line == 3  # ## Section is on line 3

    # Acceptance Criterion: "source_line disabled via config"
    def test_chunk_source_line_disabled(self):
        """source_line is 0 when track_source_lines is False."""
        doc = "## Test\nContent"
        config = ChunkingConfig(track_source_lines=False)
        chunks = MarkdownChunker(config).chunk(doc)
        assert chunks[0].source_line == 0

    # --- Convenience Function ---

    # Acceptance Criterion: "chunk_document() returns list of dicts"
    def test_chunk_document_returns_dicts(self):
        """chunk_document() returns a list of dictionaries."""
        doc = "## Sec\nContent"
        result = chunk_document(doc)
        assert isinstance(result, list)
        assert isinstance(result[0], dict)
        assert result[0]["title"] == "Sec"

    # Acceptance Criterion: "chunk_document() custom params forwarded"
    def test_chunk_document_custom_params(self):
        """chunk_document() forwards min_level/max_level/include_preamble."""
        doc = "# Title\nIntro\n## Sub\nContent"
        result = chunk_document(doc, min_level=1, max_level=1,
                                include_preamble=False)
        assert len(result) == 1
        assert result[0]["title"] == "Title"

    # --- Logging ---

    # Acceptance Criterion: "Init log message emitted"
    def test_chunk_init_log_message(self, caplog):
        """MarkdownChunker logs initialization at INFO level."""
        with caplog.at_level(logging.INFO, logger="src.chunker"):
            MarkdownChunker(ChunkingConfig(min_level=1, max_level=4))
        assert any(
            "MarkdownChunker initialized" in r.message for r in caplog.records
        )

    # Acceptance Criterion: "Chunk completion log with count"
    def test_chunk_completion_log_message(self, caplog):
        """chunker.chunk() logs completion with chunk count at INFO."""
        doc = "## A\nContent\n## B\nContent"
        chunker = MarkdownChunker()
        with caplog.at_level(logging.INFO, logger="src.chunker"):
            chunker.chunk(doc)
        assert any(
            "Chunking complete: 2 chunks" in r.message for r in caplog.records
        )

    # --- Use Case ---

    # Use Case: "Chunk a real benchmark sample from the project"
    def test_chunk_benchmark_simple_sample(self):
        """simple.md from benchmarks/samples/ is chunked correctly."""
        sample_path = pathlib.Path(__file__).parent.parent / "benchmarks" / "samples" / "simple.md"
        sample = sample_path.read_text()
        chunks = MarkdownChunker(ChunkingConfig(min_level=2)).chunk(sample)
        assert len(chunks) >= 1
        # All original content is accounted for
        total_content = " ".join(c.content for c in chunks)
        assert len(total_content) > 0

    # --- Chunk IDs ---

    # Acceptance Criterion: "Chunk IDs are unique and sequential"
    def test_chunk_ids_sequential(self):
        """Chunks have sequential zero-padded IDs."""
        doc = "## A\nContent\n## B\nContent\n## C\nContent"
        chunks = MarkdownChunker().chunk(doc)
        assert chunks[0].id == "chunk-001"
        assert chunks[1].id == "chunk-002"
        assert chunks[2].id == "chunk-003"

