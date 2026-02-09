# v0.2.1c — Advanced Chunking Features

<aside>

**Version:** v0.2.1c

**Parent:** v0.2.1 — Chunking Module

**Status:** ⬜ Not Started

**Duration:** 30–45 minutes

**Deliverable:** Parent-child hierarchy resolution, content-aware chunk merging for undersized chunks, and chunk metadata enrichment

</aside>

---

## Objective

Extend the `MarkdownChunker` with three advanced capabilities that improve chunking quality for real-world documents:

1. **Parent-Child Resolution** — Populate the `parent_id` field by associating deeper-level chunks (e.g., `###`) with their nearest ancestor at a shallower level (e.g., `##`).
2. **Small Chunk Merging** — Merge chunks below a configurable word-count threshold into their nearest sibling or parent to prevent semantic fragmentation.
3. **Chunk Metadata Enrichment** — Attach optional metadata (header depth path, section index within parent, document-level position) that aids downstream processing.

These features improve the quality of input to the entity extractor (v0.2.2) by ensuring chunks are semantically coherent and neither too large nor too small.

---

## User Stories

> As a pipeline developer, I want chunks to know their parent section so that the entity extractor can use hierarchical context (e.g., "this action belongs to the Installation section") when generating CNL output.

> As a documentation author, I want very short sections (e.g., a single-sentence note under a `###` header) to be merged into their parent chunk rather than creating isolated fragments that lack enough context for entity extraction.

---

## Feature 1: Parent-Child Resolution

### Algorithm

```
┌────────────────────────────────────────────────────────────────┐
│              PARENT-CHILD RESOLUTION                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  INPUT: flat List[Chunk] from MarkdownChunker.chunk()          │
│                                                                │
│  Maintain a STACK of (level, chunk_id) pairs:                  │
│                                                                │
│  FOR each chunk in chunklist:                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Pop stack entries with level >= chunk.level              │  │
│  │  If stack is not empty:                                   │  │
│  │    chunk.parent_id = stack[-1].chunk_id                   │  │
│  │  Push (chunk.level, chunk.id) onto stack                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  OUTPUT: same List[Chunk] with parent_id fields populated      │
│                                                                │
│  EXAMPLE:                                                      │
│  Input:  [## A, ### A.1, ### A.2, ## B, ### B.1]               │
│  Output: [## A (parent=None),                                  │
│           ### A.1 (parent=A),                                  │
│           ### A.2 (parent=A),                                  │
│           ## B (parent=None),                                  │
│           ### B.1 (parent=B)]                                  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
def resolve_hierarchy(self, chunks: List[Chunk]) -> List[Chunk]:
    """Populate parent_id fields based on header level nesting.

    Uses a stack-based approach: each chunk's parent is the most
    recent ancestor with a strictly lower header level.

    Args:
        chunks: Flat list of Chunk objects from chunk().

    Returns:
        Same list with parent_id fields populated. Chunks
        at the shallowest level in the list have parent_id=None.
    """
    ...
```

---

## Feature 2: Small Chunk Merging

### Configuration Extension

```python
@dataclass
class ChunkingConfig:
    # ... existing fields from v0.2.1a ...
    merge_threshold: int = 15  # minimum words to keep a chunk standalone
    merge_strategy: str = "parent"  # "parent" | "sibling" | "none"
```

### Merge Strategies

| Strategy | Behavior | When to Use |
|----------|----------|-------------|
| `"parent"` | Merge undersized chunk's content into its parent chunk | Default. Best for hierarchical docs where subsections are thin |
| `"sibling"` | Merge undersized chunk into the previous chunk at same level | Best for flat docs with many short sections |
| `"none"` | No merging; keep all chunks regardless of size | When every section matters, even short ones |

### Algorithm

```
┌────────────────────────────────────────────────────────────────┐
│              SMALL CHUNK MERGING                               │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  INPUT: List[Chunk] (with parent_id populated)                 │
│                                                                │
│  IF merge_strategy == "none": RETURN unchanged                 │
│                                                                │
│  FOR each chunk in chunklist (reverse order for parent merge): │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  IF chunk.word_count < merge_threshold:                   │  │
│  │    Find merge target:                                     │  │
│  │      parent → chunk with id == chunk.parent_id            │  │
│  │      sibling → previous chunk at same level               │  │
│  │    Append chunk.content to target.content                 │  │
│  │    Recompute target.word_count and target.char_count      │  │
│  │    Mark chunk for removal                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  Remove marked chunks. Renumber remaining chunk IDs.           │
│                                                                │
│  OUTPUT: List[Chunk] (potentially shorter)                     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
def merge_small_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
    """Merge chunks below the word-count threshold.

    Chunks with fewer than config.merge_threshold words are merged
    into a target chunk determined by config.merge_strategy.

    Args:
        chunks: List of Chunk objects with parent_id populated.

    Returns:
        New list with undersized chunks merged and IDs renumbered.

    Raises:
        ValueError: If merge_strategy is not one of
            'parent', 'sibling', 'none'.
    """
    ...

def _renumber_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
    """Reassign sequential IDs after merge operations.

    Args:
        chunks: List of chunks with potentially non-sequential IDs.

    Returns:
        Same chunks with IDs renumbered chunk-001, chunk-002, etc.
    """
    ...
```

---

## Feature 3: Chunk Metadata Enrichment

### Metadata Fields

```python
@dataclass
class ChunkMetadata:
    """Optional enrichment data attached to a Chunk.

    Attributes:
        breadcrumb: List of ancestor titles from root to this chunk.
            Example: ["Main Title", "Installation", "Prerequisites"]
        section_index: 0-based index of this chunk among its siblings.
        total_siblings: Total number of sibling chunks (same parent_id).
        depth: Nesting depth (0 for top-level, 1 for subsections, etc.).
        document_position: 0.0–1.0 float indicating position within
            the original document (0.0 = start, 1.0 = end).
    """
    breadcrumb: List[str] = field(default_factory=list)
    section_index: int = 0
    total_siblings: int = 1
    depth: int = 0
    document_position: float = 0.0
```

### Implementation

```python
def enrich_metadata(self, chunks: List[Chunk]) -> List[tuple[Chunk, ChunkMetadata]]:
    """Compute metadata for each chunk based on hierarchy and position.

    Args:
        chunks: List of Chunk objects with parent_id populated.

    Returns:
        List of (Chunk, ChunkMetadata) tuples in same order as input.
    """
    ...
```

---

## Updated Pipeline Method

```python
class MarkdownChunker:
    # ...existing methods...

    def chunk_with_hierarchy(self, document: str) -> List[Chunk]:
        """Chunk, resolve hierarchy, optionally merge small chunks.

        This is the recommended entry point for production use.
        It combines all three features:
        1. Split document into chunks (v0.2.1b)
        2. Resolve parent-child hierarchy (v0.2.1c)
        3. Merge undersized chunks (v0.2.1c)

        Args:
            document: Raw markdown string.

        Returns:
            List of Chunk objects with parent_id populated and
            small chunks merged according to config.

        Raises:
            TypeError: If document is not a string.
        """
        chunks = self.chunk(document)
        chunks = self.resolve_hierarchy(chunks)
        if self.config.merge_strategy != "none":
            chunks = self.merge_small_chunks(chunks)
        return chunks
```

---

## Unit Testing Requirements

### Test Categories and Minimums

| Category | Tests | Description |
|----------|-------|-------------|
| **Hierarchy** | 6 | Simple parent-child, multi-level nesting, flat (no parents), single chunk, preamble has no parent, mixed levels |
| **Merging** | 7 | Merge below threshold, keep above threshold, parent merge strategy, sibling merge strategy, none strategy, merge recomputes stats, IDs renumbered |
| **Metadata** | 5 | Breadcrumb generation, section index, total siblings, depth, document position |
| **Edge Cases** | 4 | All chunks below threshold, orphan chunk (parent merged first), single-chunk document, empty list |
| **Integration** | 3 | `chunk_with_hierarchy()` full pipeline, config forwarding, real document sample |
| **Logging** | 2 | Merge operation logged, hierarchy resolution logged |

### Example Test Code

```python
class TestParentChildResolution:
    """Tests for hierarchy resolution. (v0.2.1c)"""

    # Acceptance Criterion: "### chunks are children of preceding ## chunks"
    def test_resolve_simple_hierarchy(self):
        """### chunk has parent_id pointing to preceding ## chunk."""
        doc = "## Parent\nContent A\n### Child\nContent B"
        chunker = MarkdownChunker(ChunkingConfig(min_level=2, max_level=3))
        chunks = chunker.chunk(doc)
        chunks = chunker.resolve_hierarchy(chunks)
        assert chunks[0].parent_id is None
        assert chunks[1].parent_id == chunks[0].id

    # Acceptance Criterion: "Parent resets when new ## appears"
    def test_resolve_hierarchy_parent_reset(self):
        """New ## ends previous ##'s scope."""
        doc = "## A\n### A.1\n## B\n### B.1"
        chunker = MarkdownChunker(ChunkingConfig(min_level=2, max_level=3))
        chunks = chunker.chunk(doc)
        chunks = chunker.resolve_hierarchy(chunks)
        assert chunks[1].parent_id == chunks[0].id  # A.1 → A
        assert chunks[3].parent_id == chunks[2].id  # B.1 → B


class TestSmallChunkMerging:
    """Tests for chunk merging. (v0.2.1c)"""

    # Acceptance Criterion: "Chunks below threshold are merged"
    def test_merge_below_threshold(self):
        """Chunk with < 15 words merged into parent."""
        doc = "## Parent\nLots of content here to exceed threshold. " * 5 + \
              "\n### Tiny\nShort."
        config = ChunkingConfig(min_level=2, max_level=3, merge_threshold=15)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(doc)
        chunks = chunker.resolve_hierarchy(chunks)
        original_count = len(chunks)
        merged = chunker.merge_small_chunks(chunks)
        assert len(merged) < original_count

    # Acceptance Criterion: "Merge strategy 'none' preserves all chunks"
    def test_merge_none_strategy_preserves_all(self):
        """No merging when strategy is 'none'."""
        config = ChunkingConfig(merge_strategy="none")
        chunker = MarkdownChunker(config)
        chunks = [
            Chunk(id="chunk-001", title="A", level=2, content="Short", word_count=1),
        ]
        merged = chunker.merge_small_chunks(chunks)
        assert len(merged) == 1


class TestChunkMetadata:
    """Tests for metadata enrichment. (v0.2.1c)"""

    # Acceptance Criterion: "Breadcrumb includes ancestor titles"
    def test_breadcrumb_generation(self):
        """Breadcrumb lists ancestor titles in order."""
        doc = "## Installation\n### Prerequisites\nContent"
        chunker = MarkdownChunker(ChunkingConfig(min_level=2, max_level=3))
        chunks = chunker.chunk(doc)
        chunks = chunker.resolve_hierarchy(chunks)
        enriched = chunker.enrich_metadata(chunks)
        _, meta = enriched[1]  # Prerequisites
        assert meta.breadcrumb == ["Installation", "Prerequisites"]
```

---

## Logging Requirements

| Level | When | Example Message |
|-------|------|-----------------|
| **INFO** | Hierarchy resolved | `"Hierarchy resolved: %d parent-child relationships"` |
| **INFO** | Merge complete | `"Chunk merging complete: %d chunks merged (%d → %d)"` |
| **DEBUG** | Parent assigned | `"Chunk %s parent set to %s (level %d → %d)"` |
| **DEBUG** | Chunk merged | `"Chunk %s (%d words) merged into %s"` |
| **DEBUG** | Metadata computed | `"Metadata computed: breadcrumb=%s, depth=%d"` |
| **WARNING** | Merge target not found | `"Merge target not found for chunk %s, keeping standalone"` |

---

## Acceptance Criteria

- [ ] `resolve_hierarchy()` populates `parent_id` using stack-based algorithm
- [ ] `###` chunks correctly reference their nearest `##` ancestor
- [ ] Parent scope resets when a new header at the same or shallower level appears
- [ ] `merge_small_chunks()` merges chunks below `merge_threshold` word count
- [ ] `merge_strategy="parent"` merges into parent chunk
- [ ] `merge_strategy="sibling"` merges into previous same-level chunk
- [ ] `merge_strategy="none"` makes no changes
- [ ] Chunk IDs are renumbered after merge
- [ ] `enrich_metadata()` computes breadcrumbs, section index, depth, document position
- [ ] `chunk_with_hierarchy()` combines chunking + hierarchy + merging in one call
- [ ] ≥27 tests across hierarchy, merging, metadata, edge cases, and integration
- [ ] All tests pass: `python -m pytest tests/test_chunker.py -v`
- [ ] No `print()` statements; all output via `logger`

---

## Dependencies

**Must be completed before v0.2.1c:**
- v0.2.1a — Chunk Data Model & Interfaces
- v0.2.1b — MarkdownChunker Core Implementation

---

## Outputs to Next Sub-Part

**For v0.2.1d — Integration Testing & Benchmark Validation:**
- `chunk_with_hierarchy()` is the production entry point
- Parent-child relationships are testable
- Merge behavior is configurable

**For v0.2.2 — Entity Extraction:**
- Chunks have breadcrumb context for better entity extraction
- Small fragments are merged, improving LLM prompt quality

---

## Decision Log

| Decision | Rationale | Status |
|----------|-----------|--------|
| Stack-based hierarchy resolution | O(n) algorithm; avoids quadratic lookups; well-understood approach | ✅ Approved |
| Default merge threshold of 15 words | Based on entity extraction needing ≥1 sentence of context; 15 words ≈ 1 short sentence | ✅ Approved |
| Three merge strategies | "parent" and "sibling" cover hierarchical and flat docs; "none" is an escape hatch | ✅ Approved |
| `ChunkMetadata` as separate dataclass | Keeps `Chunk` dataclass focused; metadata is optional enrichment | ✅ Approved |
| `chunk_with_hierarchy()` as combined pipeline method | Reduces boilerplate for users who want the full feature set | ✅ Approved |
