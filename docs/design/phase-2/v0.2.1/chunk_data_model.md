# v0.2.1a — Chunk Data Model & Interfaces

<aside>

**Version:** v0.2.1a

**Parent:** v0.2.1 — Chunking Module

**Status:** ⬜ Not Started

**Duration:** 20–30 minutes

**Deliverable:** `Chunk` dataclass, `ChunkingConfig` configuration, type definitions, and comprehensive unit tests in `src/chunker.py` and `tests/test_chunker.py`

</aside>

---

## Objective

Define the foundational data structures and interfaces for the chunking module. This sub-part creates the `Chunk` dataclass that represents a segment of a markdown document, the `ChunkingConfig` configuration dataclass that controls chunking behavior, and the abstract interface that all chunker implementations must satisfy. These structures are consumed by every downstream module in the encoder pipeline (v0.2.2 Entity Extraction, v0.2.3 CNL Synthesis, v0.2.4 Validation & Metrics).

---

## User Story

> As a pipeline developer, I want a well-defined `Chunk` data model with clear fields, type hints, and serialization support so that every stage of the encoder pipeline (extractor, synthesizer, validator) can consume chunked documents through a consistent interface without guessing field names or types.

---

## Data Model Design

### Chunk Dataclass

```python
@dataclass
class Chunk:
    """A semantically bounded segment of a markdown document.

    Each Chunk represents a section of text extracted from a markdown
    document, identified by its header. Chunks form the atomic unit
    of processing in the encoder pipeline.

    Attributes:
        id: Unique identifier in format 'chunk-NNN' (zero-padded).
        title: Header text that introduced this chunk (stripped of '#' markers).
        level: Markdown header depth (1–6), or 0 for headerless content.
        content: Body text below the header, stripped of leading/trailing
            whitespace. Does not include the header line itself.
        parent_id: ID of the parent chunk (nearest ancestor header of a
            lower level number), or None if top-level.
        word_count: Number of whitespace-delimited words in content.
        char_count: Number of characters in content.
        source_line: 1-based line number in the original document where
            this chunk's header appeared.
    """
    id: str
    title: str
    level: int
    content: str
    parent_id: Optional[str] = None
    word_count: int = 0
    char_count: int = 0
    source_line: int = 0
```

### ChunkingConfig Dataclass

```python
@dataclass
class ChunkingConfig:
    """Configuration for markdown chunking behavior.

    Attributes:
        min_level: Minimum header level to split on (inclusive).
            Default 2 means '##' headers and below trigger new chunks.
        max_level: Maximum header level to split on (inclusive).
            Default 3 means '###' is the deepest split point.
        include_preamble: If True, text before the first matching header
            is captured as a chunk with title '(Preamble)' and level 0.
            Default True.
        compute_stats: If True, populate word_count and char_count fields.
            Default True.
        track_source_lines: If True, populate source_line field.
            Default True.
    """
    min_level: int = 2
    max_level: int = 3
    include_preamble: bool = True
    compute_stats: bool = True
    track_source_lines: bool = True
```

### Serialization Methods

```python
class Chunk:
    # ...existing fields...

    def to_dict(self) -> dict:
        """Serialize Chunk to a JSON-compatible dictionary.

        Returns:
            Dictionary with all Chunk fields. None values are included
            to maintain schema consistency.
        """
        return {
            "id": self.id,
            "title": self.title,
            "level": self.level,
            "content": self.content,
            "parent_id": self.parent_id,
            "word_count": self.word_count,
            "char_count": self.char_count,
            "source_line": self.source_line,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Chunk":
        """Deserialize a dictionary into a Chunk instance.

        Args:
            data: Dictionary with Chunk field names as keys.

        Returns:
            Chunk instance.

        Raises:
            KeyError: If required fields (id, title, level, content) are missing.
            TypeError: If field types do not match expected types.
        """
        return cls(
            id=data["id"],
            title=data["title"],
            level=data["level"],
            content=data["content"],
            parent_id=data.get("parent_id"),
            word_count=data.get("word_count", 0),
            char_count=data.get("char_count", 0),
            source_line=data.get("source_line", 0),
        )

    def __repr__(self) -> str:
        return (
            f"Chunk(id={self.id!r}, title={self.title!r}, "
            f"level={self.level}, words={self.word_count})"
        )
```

---

## File Structure

```
src/
└── chunker.py          # Chunk, ChunkingConfig dataclasses + logger

tests/
└── test_chunker.py     # Unit tests for data model
```

---

## Implementation Workflow

```
┌────────────────────────────────────────────────────────────────┐
│              v0.2.1a IMPLEMENTATION FLOW                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  STEP 1: Create src/chunker.py skeleton                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Module docstring + logger declaration                  │  │
│  │ • Chunk dataclass with all fields + type hints           │  │
│  │ • ChunkingConfig dataclass with defaults                 │  │
│  │ • to_dict(), from_dict(), __repr__() methods             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│  STEP 2: Create tests/test_chunker.py                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Happy path: construction, field access, defaults       │  │
│  │ • Serialization: to_dict roundtrip, from_dict roundtrip  │  │
│  │ • Edge cases: empty content, level 0, special chars      │  │
│  │ • Error paths: missing required fields, wrong types      │  │
│  │ • Config: default values, custom overrides, validation   │  │
│  │ • Logging: logger initialization verified                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│  STEP 3: Run tests + verify                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ $ python -m pytest tests/test_chunker.py -v              │  │
│  │ • All tests green                                        │  │
│  │ • No import errors                                       │  │
│  │ • Logger present in module                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Unit Testing Requirements

### Test Categories and Minimums

| Category | Tests | Description |
|----------|-------|-------------|
| **Happy Path** | 5 | Chunk construction, field access, default values, repr output, config defaults |
| **Serialization** | 5 | `to_dict()` output keys, `from_dict()` roundtrip, missing optional fields, `None` parent, JSON compatibility |
| **Edge Cases** | 5 | Empty string content, level 0 (no header), Unicode title, very long content, special characters in title |
| **Error Paths** | 3 | `from_dict()` missing required field, wrong type for level, `None` for required field |
| **Config** | 3 | Default config values, custom overrides, min_level > max_level edge |
| **Logging** | 1 | Logger initialized with `__name__` |
| **Use Case** | 1 | Full lifecycle: create → serialize → deserialize → compare |

### Test Naming Convention

```python
# Pattern: test_{class}_{method_or_aspect}_{scenario}_{expected}
def test_chunk_init_all_fields_populated():
def test_chunk_to_dict_returns_all_keys():
def test_chunk_from_dict_missing_id_raises_key_error():
def test_chunk_repr_includes_id_and_title():
def test_chunking_config_defaults_min_level_2():
```

### Example Test Code

```python
import pytest
from src.chunker import Chunk, ChunkingConfig


class TestChunkDataModel:
    """Tests for the Chunk dataclass. (v0.2.1a)"""

    # --- Happy Path ---

    # Acceptance Criterion: "Chunk dataclass has all required fields with correct types"
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

    # Acceptance Criterion: "Optional fields default to sensible zero values"
    def test_chunk_init_defaults_zero_stats(self):
        """Optional stats fields default to 0 / None."""
        chunk = Chunk(id="chunk-001", title="T", level=2, content="C")
        assert chunk.parent_id is None
        assert chunk.word_count == 0
        assert chunk.char_count == 0
        assert chunk.source_line == 0

    # --- Serialization ---

    # Acceptance Criterion: "to_dict() returns all fields as JSON-compatible dict"
    def test_chunk_to_dict_returns_all_keys(self):
        """to_dict() includes every field."""
        chunk = Chunk(id="chunk-001", title="T", level=2, content="C")
        d = chunk.to_dict()
        assert set(d.keys()) == {
            "id", "title", "level", "content",
            "parent_id", "word_count", "char_count", "source_line",
        }

    # Acceptance Criterion: "from_dict(to_dict()) roundtrip preserves all data"
    def test_chunk_roundtrip_preserves_data(self):
        """Serialize then deserialize produces equal Chunk."""
        original = Chunk(
            id="chunk-042", title="Deploy", level=3,
            content="Do the thing.", parent_id="chunk-041",
            word_count=3, char_count=13, source_line=99,
        )
        restored = Chunk.from_dict(original.to_dict())
        assert restored == original

    # --- Edge Cases ---

    # Acceptance Criterion: "Chunk handles empty content gracefully"
    def test_chunk_empty_content_allowed(self):
        """Empty string content is valid."""
        chunk = Chunk(id="chunk-001", title="Empty", level=2, content="")
        assert chunk.content == ""
        assert chunk.to_dict()["content"] == ""

    # Acceptance Criterion: "Chunk handles Unicode titles"
    def test_chunk_unicode_title(self):
        """Unicode characters in title are preserved."""
        chunk = Chunk(id="chunk-001", title="日本語セクション", level=2, content="C")
        assert chunk.title == "日本語セクション"
        roundtrip = Chunk.from_dict(chunk.to_dict())
        assert roundtrip.title == "日本語セクション"

    # --- Error Paths ---

    # Acceptance Criterion: "from_dict() raises KeyError for missing required fields"
    def test_chunk_from_dict_missing_id_raises_key_error(self):
        """Missing 'id' key raises KeyError."""
        with pytest.raises(KeyError):
            Chunk.from_dict({"title": "T", "level": 2, "content": "C"})


class TestChunkingConfig:
    """Tests for the ChunkingConfig dataclass. (v0.2.1a)"""

    # Acceptance Criterion: "ChunkingConfig defaults match spec"
    def test_config_defaults(self):
        """Default config uses level 2–3, includes preamble, computes stats."""
        config = ChunkingConfig()
        assert config.min_level == 2
        assert config.max_level == 3
        assert config.include_preamble is True
        assert config.compute_stats is True
        assert config.track_source_lines is True

    # Acceptance Criterion: "ChunkingConfig accepts custom overrides"
    def test_config_custom_overrides(self):
        """Custom values override defaults."""
        config = ChunkingConfig(min_level=1, max_level=4, include_preamble=False)
        assert config.min_level == 1
        assert config.max_level == 4
        assert config.include_preamble is False
```

---

## Logging Requirements

| Level | When | Example Message |
|-------|------|-----------------|
| **INFO** | Module imported / logger initialized | `"chunker module loaded"` |
| **DEBUG** | Chunk created | `"Chunk created: id=%s, title=%s, level=%d"` |
| **DEBUG** | Chunk serialized | `"Chunk serialized to dict: id=%s"` |
| **DEBUG** | Chunk deserialized | `"Chunk deserialized from dict: id=%s"` |
| **WARNING** | Chunk content exceeds threshold | `"Chunk %s content exceeds %d chars: %d"` |

```python
import logging

logger = logging.getLogger(__name__)

# In Chunk.to_dict():
logger.debug("Chunk serialized to dict: id=%s", self.id)

# In Chunk.from_dict():
logger.debug("Chunk deserialized from dict: id=%s", data.get("id"))
```

---

## Acceptance Criteria

- [ ] `src/chunker.py` created with module docstring referencing v0.2.1a
- [ ] `Chunk` dataclass defined with all 8 fields and full type hints
- [ ] `ChunkingConfig` dataclass defined with 5 fields and sensible defaults
- [ ] `to_dict()` returns JSON-serializable dictionary with all fields
- [ ] `from_dict()` class method reconstructs Chunk from dictionary
- [ ] `from_dict()` raises `KeyError` when required fields are missing
- [ ] `__repr__()` returns readable summary including id, title, level
- [ ] Logger initialized with `logging.getLogger(__name__)`
- [ ] `tests/test_chunker.py` created with ≥23 tests across all categories
- [ ] All tests pass: `python -m pytest tests/test_chunker.py -v`
- [ ] No `print()` statements in `src/chunker.py`
- [ ] All public methods have Google-style docstrings with Args/Returns/Raises

---

## Limitations & Constraints

1. **No Chunking Logic Yet:** This sub-part only defines the data model and configuration. The actual splitting algorithm is v0.2.1b.
2. **No File I/O:** Chunks are created from strings, not files. File reading is the caller's responsibility.
3. **No Token Counting:** Token counts are deferred to v0.2.4 (Validation & Metrics). Word and character counts are simple `len()` / `split()` operations.
4. **Flat Structure Only:** `parent_id` field is defined but parent-child relationship resolution is deferred to v0.2.1c.

---

## Dependencies

**Must be completed before v0.2.1a:**
- v0.1.3c — Source Module Stubs (establishes `src/` package structure)
- v0.1.3 — Project Scaffolding (confirms directory layout)

**No dependencies on:**
- v0.2.2 — Entity Extraction (consumes Chunks but does not influence their design)
- v0.2.3 — CNL Synthesis (consumes Chunks indirectly through extracted entities)

---

## Outputs to Next Sub-Part

**For v0.2.1b — MarkdownChunker Core Implementation:**
- `Chunk` dataclass is importable from `src.chunker`
- `ChunkingConfig` is importable from `src.chunker`
- Serialization methods (`to_dict`, `from_dict`) are tested and working
- Logger is initialized and ready for chunking-level log messages

---

## Decision Log

| Decision | Rationale | Status |
|----------|-----------|--------|
| Use `@dataclass` over `TypedDict` for Chunk | Dataclasses provide `__eq__`, `__repr__`, `__init__` for free; TypedDict is dict-like but lacks methods | ✅ Approved |
| Include `word_count` and `char_count` on Chunk | Avoids re-counting downstream; cheap to compute during chunking | ✅ Approved |
| Include `source_line` field | Enables error messages and debugging to reference original document location | ✅ Approved |
| Separate `ChunkingConfig` from `MarkdownChunker` | Config can be serialized/logged independently; supports future config-file loading | ✅ Approved |
| Defer parent-child resolution to v0.2.1c | Keeps v0.2.1a focused on data structures; relationship logic adds complexity | ✅ Approved |
