"""
tests/test_chunker.py — Unit Tests for Chunk Data Model
========================================================

Tests for the Chunk dataclass, ChunkingConfig, and serialization
methods defined in src/chunker.py (v0.2.1a).

Test Categories:
    - Happy Path (5): Construction, field access, defaults, repr, config
    - Serialization (5): to_dict, from_dict, roundtrip, missing optionals, JSON
    - Edge Cases (5): Empty content, level 0, Unicode, long content, special chars
    - Error Paths (3): Missing required field, wrong type, None for required
    - Config (3): Defaults, custom overrides, min > max edge
    - Logging (1): Logger initialization
    - Use Case (1): Full lifecycle roundtrip

Version: v0.2.1a
"""

import json
import logging
import pytest
from src.chunker import Chunk, ChunkingConfig


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
