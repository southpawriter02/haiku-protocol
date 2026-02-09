# v0.2.1b — MarkdownChunker Core Implementation

<aside>

**Version:** v0.2.1b

**Parent:** v0.2.1 — Chunking Module

**Status:** ⬜ Not Started

**Duration:** 30–45 minutes

**Deliverable:** `MarkdownChunker` class with header-based splitting, `chunk_document()` convenience function, and comprehensive unit tests

</aside>

---

## Objective

Implement the core `MarkdownChunker` class that splits markdown documents into `Chunk` objects based on header boundaries. This is the primary splitting algorithm of the encoder pipeline's first stage. The chunker scans a markdown string line-by-line, detects header patterns (`#` through `######`), and emits a list of `Chunk` objects — each containing the text between consecutive headers at the configured depth range. Content before the first matching header is optionally captured as a preamble chunk.

---

## User Story

> As an encoder pipeline developer, I want to split a markdown document into semantically bounded chunks at header boundaries so that each chunk can be independently processed by the entity extractor (v0.2.2) without losing context about which section the content belongs to.

---

## Algorithm Design

### Header Detection Strategy

```
┌────────────────────────────────────────────────────────────────┐
│              MARKDOWN CHUNKING ALGORITHM                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  INPUT: raw markdown string + ChunkingConfig                   │
│                                                                │
│  FOR each line in document:                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Match line against HEADER_PATTERN: ^(#{1,6})\s+(.+)$   │  │
│  │                                                          │  │
│  │  ┌─── Is it a header?                                    │  │
│  │  │                                                       │  │
│  │  ├── YES: Is level within [min_level, max_level]?        │  │
│  │  │   ├── YES: Flush current buffer → emit Chunk          │  │
│  │  │   │        Start new buffer with this header          │  │
│  │  │   └── NO:  Append header line to current buffer       │  │
│  │  │            (treat as content, not a split point)      │  │
│  │  │                                                       │  │
│  │  └── NO: Append line to current buffer                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  After all lines: flush final buffer → emit last Chunk         │
│                                                                │
│  OUTPUT: List[Chunk]                                           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Preamble Handling

```
┌──────────────────────────────────────────────────────────────┐
│  PREAMBLE DECISION                                           │
│                                                              │
│  Text before first matching header?                          │
│           │                                                  │
│  ┌───────┴────────┐                                         │
│  ▼ YES             ▼ NO                                      │
│  Is config.include_preamble True?     → No preamble chunk   │
│           │                                                  │
│  ┌───────┴────────┐                                         │
│  ▼ YES             ▼ NO                                      │
│  Emit Chunk with:  → Discard preamble text                  │
│    id="chunk-001"                                            │
│    title="(Preamble)"                                       │
│    level=0                                                   │
│    source_line=1                                             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Implementation Details

### Class: MarkdownChunker

```python
class MarkdownChunker:
    """Split markdown documents into Chunk objects at header boundaries.

    The chunker scans a markdown string line-by-line, identifies headers
    using a regex pattern, and emits Chunk objects for each section of
    text bounded by consecutive headers within the configured depth range.

    Attributes:
        config: ChunkingConfig controlling split behavior.

    Example:
        >>> chunker = MarkdownChunker(ChunkingConfig(min_level=2, max_level=3))
        >>> chunks = chunker.chunk("## Intro\\nHello\\n## Next\\nWorld")
        >>> len(chunks)
        2
        >>> chunks[0].title
        'Intro'
    """

    HEADER_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    def __init__(self, config: Optional[ChunkingConfig] = None) -> None:
        """Initialize the chunker.

        Args:
            config: Chunking configuration. If None, uses default
                ChunkingConfig (split on ## and ###).
        """
        self.config = config or ChunkingConfig()
        logger.info(
            "MarkdownChunker initialized: min_level=%d, max_level=%d",
            self.config.min_level, self.config.max_level
        )

    def chunk(self, document: str) -> List[Chunk]:
        """Split a markdown document into chunks.

        Scans the document line by line. Each header within the
        configured level range triggers a new chunk. Text between
        headers becomes the chunk's content.

        Args:
            document: Raw markdown string to split.

        Returns:
            List of Chunk objects in document order. Empty documents
            return an empty list. Documents with no matching headers
            return a single preamble chunk (if include_preamble is True)
            or an empty list.

        Raises:
            TypeError: If document is not a string.
        """
        ...

    def _compute_stats(self, content: str) -> tuple[int, int]:
        """Compute word and character counts for content.

        Args:
            content: Text content to analyze.

        Returns:
            Tuple of (word_count, char_count).
        """
        ...

    def _make_chunk_id(self, index: int) -> str:
        """Generate a zero-padded chunk ID.

        Args:
            index: 1-based chunk sequence number.

        Returns:
            String in format 'chunk-NNN'.
        """
        return f"chunk-{index:03d}"
```

### Convenience Function

```python
def chunk_document(
    document: str,
    min_level: int = 2,
    max_level: int = 3,
    include_preamble: bool = True,
) -> List[dict]:
    """Chunk a markdown document and return dictionaries.

    Convenience wrapper around MarkdownChunker for quick usage.

    Args:
        document: Raw markdown string.
        min_level: Minimum header level to split on.
        max_level: Maximum header level to split on.
        include_preamble: Whether to capture text before first header.

    Returns:
        List of chunk dictionaries (via Chunk.to_dict()).
    """
    config = ChunkingConfig(
        min_level=min_level,
        max_level=max_level,
        include_preamble=include_preamble,
    )
    chunker = MarkdownChunker(config)
    return [c.to_dict() for c in chunker.chunk(document)]
```

---

## Unit Testing Requirements

### Test Categories and Minimums

| Category | Tests | Description |
|----------|-------|-------------|
| **Happy Path** | 6 | Basic splitting on `##`, splitting on `###`, mixed `##` and `###`, single section, multiple sections, content preserved |
| **Preamble** | 3 | Preamble captured when `include_preamble=True`, preamble omitted when `False`, no preamble when document starts with header |
| **Edge Cases** | 7 | Empty document, whitespace-only document, no headers at all, headers outside range (e.g., `#` and `####`), header with no content, consecutive headers, header in code block (fenced) |
| **Error Paths** | 2 | `TypeError` on non-string input, `None` input |
| **Config** | 3 | Custom min/max levels, level 1 splitting, single-level range |
| **Stats** | 3 | Word count computed, char count computed, stats disabled via config |
| **Source Lines** | 2 | `source_line` tracks correct 1-based position, disabled via config |
| **Convenience Fn** | 2 | `chunk_document()` returns list of dicts, custom params forwarded |
| **Logging** | 2 | Init log message, chunk completion log with count |
| **Use Case** | 1 | Real benchmark sample (`benchmarks/samples/simple.md`) chunked correctly |

### Example Test Code

```python
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

    # Acceptance Criterion: "Chunk content preserves all text between headers"
    def test_chunk_content_preserved(self):
        """All lines between headers are captured in content."""
        doc = "## Test\nLine 1\nLine 2\nLine 3"
        chunks = MarkdownChunker().chunk(doc)
        assert "Line 1" in chunks[0].content
        assert "Line 2" in chunks[0].content
        assert "Line 3" in chunks[0].content

    # Acceptance Criterion: "Chunk IDs are unique and sequential"
    def test_chunk_ids_sequential(self):
        """Chunks have sequential zero-padded IDs."""
        doc = "## A\nContent\n## B\nContent\n## C\nContent"
        chunks = MarkdownChunker().chunk(doc)
        assert chunks[0].id == "chunk-001"
        assert chunks[1].id == "chunk-002"
        assert chunks[2].id == "chunk-003"

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

    # --- Edge Cases ---

    # Acceptance Criterion: "Empty document returns empty list"
    @pytest.mark.unit
    def test_chunk_empty_document_returns_empty(self):
        """Empty string returns empty list."""
        chunks = MarkdownChunker().chunk("")
        assert chunks == []

    # Acceptance Criterion: "Document with no matching headers handled gracefully"
    def test_chunk_no_matching_headers(self):
        """Document with only # (level 1) and config min_level=2 → preamble only."""
        doc = "# Title\nSome text without ## headers."
        config = ChunkingConfig(min_level=2, include_preamble=True)
        chunks = MarkdownChunker(config).chunk(doc)
        assert len(chunks) == 1
        assert chunks[0].title == "(Preamble)"

    # Acceptance Criterion: "Headers inside fenced code blocks are not treated as split points"
    def test_chunk_header_inside_code_block_ignored(self):
        """Fenced code block headers are not split points."""
        doc = "## Real Section\nContent\n```\n## Not A Header\ncode\n```\nMore content"
        chunks = MarkdownChunker().chunk(doc)
        assert len(chunks) == 1
        assert "## Not A Header" in chunks[0].content

    # --- Use Case ---

    # Use Case: "Chunk a real benchmark sample from the project"
    def test_chunk_benchmark_simple_sample(self):
        """simple.md from benchmarks/samples/ is chunked correctly."""
        import pathlib
        sample = pathlib.Path("benchmarks/samples/simple.md").read_text()
        chunks = MarkdownChunker(ChunkingConfig(min_level=2)).chunk(sample)
        assert len(chunks) >= 1
        # All original content is accounted for
        total_content = " ".join(c.content for c in chunks)
        assert len(total_content) > 0
```

---

## Logging Requirements

| Level | When | Example Message |
|-------|------|-----------------|
| **INFO** | Chunker initialized | `"MarkdownChunker initialized: min_level=%d, max_level=%d"` |
| **INFO** | Chunking complete | `"Chunking complete: %d chunks from %d-line document"` |
| **DEBUG** | New chunk started | `"New chunk started: id=%s, title=%s, level=%d at line %d"` |
| **DEBUG** | Preamble chunk created | `"Preamble chunk created: %d chars"` |
| **DEBUG** | Header outside range skipped | `"Header at level %d outside range [%d, %d], treating as content"` |
| **WARNING** | Empty document | `"Empty document provided, returning empty chunk list"` |
| **WARNING** | Code block header detected | `"Header-like line inside code block at line %d, skipping as split point"` |

---

## Acceptance Criteria

- [ ] `MarkdownChunker` class implemented in `src/chunker.py` with Google-style docstrings
- [ ] `chunk()` method splits markdown by headers within configured level range
- [ ] `chunk()` raises `TypeError` for non-string input
- [ ] Preamble text captured as level-0 chunk when `include_preamble=True`
- [ ] Preamble text discarded when `include_preamble=False`
- [ ] Headers inside fenced code blocks (` ``` `) are NOT treated as split points
- [ ] `word_count` and `char_count` computed when `compute_stats=True`
- [ ] `source_line` tracks 1-based line number of each header
- [ ] Chunk IDs are sequential and zero-padded (`chunk-001`, `chunk-002`, ...)
- [ ] `chunk_document()` convenience function returns list of dictionaries
- [ ] All content between headers is preserved with no data loss
- [ ] `tests/test_chunker.py` has ≥31 tests across all categories
- [ ] All tests pass: `python -m pytest tests/test_chunker.py -v`
- [ ] All logging uses `%s`-style formatting, no f-strings in log calls
- [ ] No `print()` statements in source code
- [ ] Successfully chunks `benchmarks/samples/simple.md`

---

## Limitations & Constraints

1. **Fenced Code Block Handling:** The chunker must track `` ``` `` fence state to avoid splitting on headers inside code blocks. This adds a small state machine to the line-by-line scan.
2. **No Nested Header Resolution:** Headers are split flatly — a `###` chunk does not "know" it's inside a `##` chunk. Parent-child relationships are deferred to v0.2.1c.
3. **No Indented Code Blocks:** Only fenced (backtick) code blocks are detected. Indented code blocks (4-space prefix) are not tracked, as markdown headers require no indentation.
4. **Single Document Only:** The chunker processes one document string at a time. Batch/directory processing is the caller's responsibility.

---

## Dependencies

**Must be completed before v0.2.1b:**
- v0.2.1a — Chunk Data Model & Interfaces (`Chunk` and `ChunkingConfig` dataclasses)

**No dependencies on:**
- v0.2.1c — Advanced Chunking Features
- v0.2.2 — Entity Extraction

---

## Outputs to Next Sub-Part

**For v0.2.1c — Advanced Chunking Features:**
- `MarkdownChunker` is functional and tested
- `chunk()` returns a flat list of `Chunk` objects
- Parent-child resolution can now be layered on top

**For v0.2.2 — Entity Extraction:**
- `chunk_document()` produces list of dicts suitable for entity extraction input
- Each dict has `id`, `title`, `level`, `content` keys

---

## Decision Log

| Decision | Rationale | Status |
|----------|-----------|--------|
| Track fenced code block state during scanning | Prevents false splits on headers inside code examples, which are common in documentation | ✅ Approved |
| Capture preamble as level-0 chunk | Top-of-document text before any header often contains important context (intro, warnings) | ✅ Approved |
| Use ` ``` ` as sole code fence marker | Standard markdown; ATX-style `~~~` is rare in practice and can be added in v0.2.1c if needed | ✅ Approved |
| Accept `ChunkingConfig` in constructor, not per-call | Configuration is typically set once per pipeline run, not per document | ✅ Approved |
| Raise `TypeError` for non-string input | Fail-fast is better than silent empty output for wrong types | ✅ Approved |
