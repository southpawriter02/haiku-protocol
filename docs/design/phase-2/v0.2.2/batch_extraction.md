# v0.2.2d — Batch Extraction & Error Resilience

<aside>

**Version:** v0.2.2d

**Parent:** v0.2.2 — Entity Extraction

**Status:** ⬜ Not Started

**Duration:** 25–35 minutes

**Deliverable:** Batch extraction pipeline with per-chunk error isolation, progress tracking, result aggregation, and extraction caching

</aside>

---

## Objective

Extend the `EntityExtractor` to process multiple chunks in sequence (batch mode), isolating failures to individual chunks without crashing the entire pipeline. This sub-part adds:

1. **Batch Extraction** — Process a list of chunk dictionaries and return enriched chunks with entities attached.
2. **Error Isolation** — Failures on individual chunks are logged and skipped; remaining chunks continue processing.
3. **Progress Tracking** — Callbacks and logging for monitoring batch progress.
4. **Result Aggregation** — Combine per-chunk results into a summary with statistics.
5. **Extraction Caching** — Cache extraction results to avoid re-processing unchanged chunks.

---

## User Stories

> As a pipeline operator processing a 50-section document, I want extraction failures on one section (e.g., a timeout) to not crash the entire run — the failed chunk should be logged and skipped, and all other chunks should still be processed.

> As a developer iterating on prompt engineering, I want extraction results cached so that re-running the pipeline on unchanged chunks doesn't burn API credits.

---

## Batch Processing Architecture

```
┌────────────────────────────────────────────────────────────────┐
│              BATCH EXTRACTION PIPELINE                         │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  INPUT: List[dict] from chunk_document() or chunk.to_dict()    │
│                          │                                     │
│                          ▼                                     │
│   FOR each chunk_dict in batch:                                │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │  Try:                                                    │ │
│   │    1. Check cache for existing extraction                │ │
│   │    2. If cached → use cached result                      │ │
│   │    3. Else → extractor.extract(chunk["content"])         │ │
│   │    4. Attach entities to chunk_dict                      │ │
│   │    5. Cache result                                       │ │
│   │    6. Update progress                                    │ │
│   │  Except:                                                 │ │
│   │    Log error, mark chunk as failed, continue             │ │
│   └──────────────────────────────────────────────────────────┘ │
│                          │                                     │
│                          ▼                                     │
│   OUTPUT: BatchResult                                          │
│   ┌──────────────────────────────────────────────────────────┐ │
│   │  results: List[dict]     (chunks with entities attached) │ │
│   │  failures: List[dict]    (chunks that failed + errors)   │ │
│   │  stats: BatchStats       (counts, timing, confidence)    │ │
│   └──────────────────────────────────────────────────────────┘ │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Implementation

### BatchResult and BatchStats

```python
@dataclass
class BatchStats:
    """Statistics for a batch extraction run.

    Attributes:
        total_chunks: Number of chunks in the batch.
        successful: Number of chunks successfully extracted.
        failed: Number of chunks that failed extraction.
        cached: Number of chunks served from cache.
        total_entities: Sum of all entities across successful chunks.
        avg_confidence: Mean confidence score across successful chunks.
        elapsed_seconds: Total wall-clock time for the batch.
        entities_per_type: Breakdown of entity counts by type.
    """
    total_chunks: int = 0
    successful: int = 0
    failed: int = 0
    cached: int = 0
    total_entities: int = 0
    avg_confidence: float = 0.0
    elapsed_seconds: float = 0.0
    entities_per_type: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to JSON-compatible dictionary."""
        return {
            "total_chunks": self.total_chunks,
            "successful": self.successful,
            "failed": self.failed,
            "cached": self.cached,
            "total_entities": self.total_entities,
            "avg_confidence": round(self.avg_confidence, 3),
            "elapsed_seconds": round(self.elapsed_seconds, 3),
            "entities_per_type": self.entities_per_type,
            "success_rate": f"{self.successful / max(self.total_chunks, 1) * 100:.0f}%",
        }


@dataclass
class BatchResult:
    """Complete result of a batch extraction run.

    Attributes:
        results: List of chunk dicts with 'entities' key added.
        failures: List of dicts with 'chunk_id', 'error', 'chunk' keys.
        stats: Aggregated statistics for the batch.
    """
    results: List[Dict] = field(default_factory=list)
    failures: List[Dict] = field(default_factory=list)
    stats: BatchStats = field(default_factory=BatchStats)

    def to_dict(self) -> dict:
        """Serialize full result."""
        return {
            "results": self.results,
            "failures": [
                {"chunk_id": f["chunk_id"], "error": str(f["error"])}
                for f in self.failures
            ],
            "stats": self.stats.to_dict(),
        }
```

### Batch Extraction Method

```python
class EntityExtractor:
    # ...existing methods from v0.2.2c...

    def extract_batch(
        self,
        chunks: List[Dict],
        on_progress: Optional[Callable[[int, int, str], None]] = None,
        use_cache: bool = True,
    ) -> BatchResult:
        """Extract entities from a batch of chunk dictionaries.

        Processes each chunk independently, isolating failures.
        Attaches an 'entities' key to each successful chunk dict.

        Args:
            chunks: List of chunk dicts (from chunk_document() or Chunk.to_dict()).
                Each dict must have 'id' and 'content' keys.
            on_progress: Optional callback(current, total, chunk_id) for
                progress reporting. Called after each chunk completes.
            use_cache: If True, check/populate extraction cache.

        Returns:
            BatchResult with results, failures, and aggregated stats.
        """
        ...

    def _aggregate_stats(
        self,
        results: List[Dict],
        failures: List[Dict],
        cached_count: int,
        elapsed: float,
    ) -> BatchStats:
        """Compute aggregated statistics from batch results.

        Args:
            results: Successful extraction results.
            failures: Failed extraction records.
            cached_count: Number of cache hits.
            elapsed: Total elapsed time in seconds.

        Returns:
            BatchStats with all fields populated.
        """
        ...
```

### Extraction Cache

```python
import hashlib


class ExtractionCache:
    """In-memory cache for extraction results.

    Caches extraction results keyed by a hash of the chunk content
    and prompt version. Avoids re-extracting unchanged chunks during
    iterative development.

    Attributes:
        _cache: Dictionary mapping cache keys to ExtractedEntities.
        _prompt_version: Active prompt version (cache is invalidated
            when prompt changes).
    """

    def __init__(self, prompt_version: str = "") -> None:
        self._cache: Dict[str, ExtractedEntities] = {}
        self._prompt_version = prompt_version

    def _make_key(self, content: str) -> str:
        """Generate cache key from content + prompt version.

        Args:
            content: Chunk content string.

        Returns:
            SHA-256 hash string.
        """
        raw = f"{self._prompt_version}:{content}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, content: str) -> Optional[ExtractedEntities]:
        """Look up cached extraction for content.

        Args:
            content: Chunk content string.

        Returns:
            Cached ExtractedEntities or None if not found.
        """
        key = self._make_key(content)
        result = self._cache.get(key)
        if result:
            logger.debug("Cache hit: key=%s", key[:12])
        return result

    def put(self, content: str, entities: ExtractedEntities) -> None:
        """Store extraction result in cache.

        Args:
            content: Chunk content string.
            entities: Extraction result to cache.
        """
        key = self._make_key(content)
        self._cache[key] = entities
        logger.debug("Cache stored: key=%s, entities=%d", key[:12], entities.total_entities)

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
        logger.info("Extraction cache cleared")

    @property
    def size(self) -> int:
        """Number of cached entries."""
        return len(self._cache)
```

---

## Unit Testing Requirements

### Test Categories and Minimums

| Category | Tests | Description |
|----------|-------|-------------|
| **Batch Happy Path** | 4 | Batch of 3 chunks all succeed, entities attached to output, stats correct, results length matches input |
| **Error Isolation** | 4 | One failure doesn't stop batch, failure recorded in failures list, other chunks still processed, stats count failures |
| **Progress** | 3 | Callback called for each chunk, callback receives correct (current, total), no callback doesn't crash |
| **Cache** | 5 | Cache hit avoids LLM call, cache miss invokes LLM, cache key includes prompt version, cache clear works, stats count cached |
| **Stats** | 4 | Entity counts by type, average confidence, elapsed time > 0, success rate percentage |
| **Edge Cases** | 3 | Empty batch returns empty result, single-chunk batch, all chunks fail |
| **Aggregation** | 2 | Total entities sums correctly, per-type breakdown correct |
| **Logging** | 1 | Batch completion logged with stats |

### Example Test Code

```python
class TestBatchExtraction:
    """Tests for batch extraction. (v0.2.2d)"""

    @patch("src.extractor.ChatOpenAI")
    def test_batch_extracts_all_chunks(self, mock_llm_class):
        """Batch of 3 chunks produces 3 results."""
        mock_response = Mock()
        mock_response.content = '{"actions": ["A"], "states": [], "commands": [], "warnings": [], "dependencies": []}'
        mock_llm_class.return_value.invoke.return_value = mock_response

        extractor = EntityExtractor()
        chunks = [
            {"id": "chunk-001", "content": "Do A"},
            {"id": "chunk-002", "content": "Do B"},
            {"id": "chunk-003", "content": "Do C"},
        ]
        batch_result = extractor.extract_batch(chunks)

        assert len(batch_result.results) == 3
        assert batch_result.stats.successful == 3
        assert batch_result.stats.failed == 0

    @patch("src.extractor.ChatOpenAI")
    def test_batch_isolates_failure(self, mock_llm_class):
        """One failing chunk doesn't stop the batch."""
        responses = [
            Mock(content='{"actions": ["A"], "states": [], "commands": [], "warnings": [], "dependencies": []}'),
            Exception("API timeout"),
            Mock(content='{"actions": ["C"], "states": [], "commands": [], "warnings": [], "dependencies": []}'),
        ]
        mock_llm_class.return_value.invoke.side_effect = responses

        extractor = EntityExtractor(max_retries=0)
        chunks = [
            {"id": "chunk-001", "content": "Do A"},
            {"id": "chunk-002", "content": "Do B"},
            {"id": "chunk-003", "content": "Do C"},
        ]
        batch_result = extractor.extract_batch(chunks)

        assert batch_result.stats.successful == 2
        assert batch_result.stats.failed == 1
        assert len(batch_result.failures) == 1
        assert batch_result.failures[0]["chunk_id"] == "chunk-002"

    @patch("src.extractor.ChatOpenAI")
    def test_batch_progress_callback(self, mock_llm_class):
        """Progress callback is called for each chunk."""
        mock_response = Mock(content='{"actions": [], "states": [], "commands": [], "warnings": [], "dependencies": []}')
        mock_llm_class.return_value.invoke.return_value = mock_response

        progress_log = []
        def on_progress(current, total, chunk_id):
            progress_log.append((current, total, chunk_id))

        extractor = EntityExtractor()
        chunks = [
            {"id": "chunk-001", "content": "A"},
            {"id": "chunk-002", "content": "B"},
        ]
        extractor.extract_batch(chunks, on_progress=on_progress)

        assert len(progress_log) == 2
        assert progress_log[0] == (1, 2, "chunk-001")
        assert progress_log[1] == (2, 2, "chunk-002")


class TestExtractionCache:
    """Tests for extraction caching. (v0.2.2d)"""

    def test_cache_hit_returns_stored_result(self):
        """Cached result is returned without re-extraction."""
        cache = ExtractionCache(prompt_version="1.0.0")
        entities = ExtractedEntities(actions=["Cached_Action"])
        cache.put("some content", entities)

        result = cache.get("some content")
        assert result is not None
        assert "Cached_Action" in result.actions

    def test_cache_miss_returns_none(self):
        """Unknown content returns None."""
        cache = ExtractionCache(prompt_version="1.0.0")
        assert cache.get("never seen") is None

    def test_cache_key_includes_prompt_version(self):
        """Different prompt versions produce different cache keys."""
        cache_v1 = ExtractionCache(prompt_version="1.0.0")
        cache_v2 = ExtractionCache(prompt_version="2.0.0")
        assert cache_v1._make_key("same text") != cache_v2._make_key("same text")

    def test_cache_clear(self):
        """clear() empties the cache."""
        cache = ExtractionCache()
        cache.put("content", ExtractedEntities())
        assert cache.size == 1
        cache.clear()
        assert cache.size == 0
```

---

## Logging Requirements

| Level | When | Example Message |
|-------|------|-----------------|
| **INFO** | Batch started | `"Batch extraction started: %d chunks"` |
| **INFO** | Batch complete | `"Batch complete: %d/%d successful, %d cached, %.1fs elapsed"` |
| **DEBUG** | Chunk processing started | `"Processing chunk %d/%d: id=%s"` |
| **DEBUG** | Cache hit | `"Cache hit: key=%s"` |
| **DEBUG** | Cache stored | `"Cache stored: key=%s, entities=%d"` |
| **WARNING** | Chunk extraction failed | `"Chunk %s extraction failed: %s. Continuing batch."` |
| **ERROR** | All chunks failed | `"Batch extraction: all %d chunks failed"` |

---

## Acceptance Criteria

- [ ] `extract_batch()` processes list of chunk dicts and returns `BatchResult`
- [ ] Failures on individual chunks are isolated — batch continues
- [ ] Failed chunks recorded in `BatchResult.failures` with chunk_id and error
- [ ] `on_progress` callback invoked after each chunk with (current, total, chunk_id)
- [ ] `ExtractionCache` stores/retrieves results keyed by content + prompt version
- [ ] Cache key changes when prompt version changes
- [ ] `BatchStats` computes entity counts by type, average confidence, elapsed time
- [ ] Empty batch returns empty `BatchResult` (no errors)
- [ ] Single-chunk batch works correctly
- [ ] `BatchResult.to_dict()` serializes to JSON-compatible format
- [ ] ≥26 tests pass (all mocked, no real API calls)
- [ ] No `print()` statements

---

## Dependencies

**Must be completed before v0.2.2d:**
- v0.2.2c — EntityExtractor Core (`extract()` method)
- v0.2.2a — Entity Data Model (`ExtractedEntities`)

---

## Outputs to Next Sub-Part

**For v0.2.2e — Integration Testing:**
- `extract_batch()` is the primary batch API to test
- `BatchResult` provides structured test assertions
- `ExtractionCache` is testable independently

**For v0.2.3 — CNL Synthesis:**
- `BatchResult.results` list feeds directly into the synthesizer
- Each result dict has `id`, `content`, `title`, `level`, and `entities` keys

---

## Decision Log

| Decision | Rationale | Status |
|----------|-----------|--------|
| In-memory cache only (no disk persistence) | Keeps implementation simple; disk caching adds filesystem concerns | ✅ Approved |
| Cache key = SHA-256(prompt_version + content) | Prompt changes invalidate cache automatically; content changes detected | ✅ Approved |
| Error isolation via try/except per chunk | Industry standard for batch APIs; one poisoned item shouldn't kill the batch | ✅ Approved |
| Progress callback instead of events/observers | Simplest pattern; callbacks are composable and don't require pub/sub infrastructure | ✅ Approved |
| `BatchStats` as separate dataclass | Enables independent serialization and testing of statistics logic | ✅ Approved |
