"""
chunker.py - Document Chunking and Segmentation
================================================

Segments markdown documents into semantically bounded chunks
based on header boundaries for processing through the encoder
pipeline.

Classes:
    Chunk: Dataclass representing a document segment (v0.2.1a)
    ChunkingConfig: Configuration for chunking behavior (v0.2.1a)
    MarkdownChunker: Header-based markdown splitter (v0.2.1b)
    DocumentChunker: Document segmentation orchestrator (stub)

Functions:
    chunk_document: Convenience wrapper for one-call chunking (v0.2.1b)

Implementation Status:
    - v0.2.1a: Chunk data model, ChunkingConfig, serialization
    - v0.2.1b: MarkdownChunker core, chunk_document() convenience function

Related: v0.2.1 — Chunking Module
"""

import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)
logger.info("chunker module loaded")

# --- Content size warning threshold (characters) ---
_CONTENT_WARNING_THRESHOLD = 50_000


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

    def __post_init__(self):
        """Log chunk creation and warn on oversized content."""
        logger.debug(
            "Chunk created: id=%s, title=%s, level=%d",
            self.id, self.title, self.level,
        )
        if len(self.content) > _CONTENT_WARNING_THRESHOLD:
            logger.warning(
                "Chunk %s content exceeds %d chars: %d",
                self.id, _CONTENT_WARNING_THRESHOLD, len(self.content),
            )

    def to_dict(self) -> dict:
        """Serialize Chunk to a JSON-compatible dictionary.

        Returns:
            Dictionary with all Chunk fields. None values are included
            to maintain schema consistency.
        """
        logger.debug("Chunk serialized to dict: id=%s", self.id)
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
            KeyError: If required fields (id, title, level, content)
                are missing.
            TypeError: If field types do not match expected types.
        """
        logger.debug("Chunk deserialized from dict: id=%s", data.get("id"))
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


class DocumentChunker:
    """Segments documents into chunks for processing.

    Supports multiple chunking strategies:
    - fixed_size: Fixed character/token count
    - semantic: Sentence/paragraph boundaries
    - sliding_window: Overlapping windows

    Attributes:
        config: Configuration (chunk_size, overlap, strategy)
        strategy: Chunking strategy ('fixed_size', 'semantic', 'sliding_window')

    Example:
        >>> chunker = DocumentChunker(chunk_size=512, strategy='semantic')
        >>> chunks = chunker.chunk("Long document...")
        >>> for chunk in chunks:
        ...     print(f"Chunk {chunk.id}: {len(chunk.content)} chars")
    """

    def __init__(
        self,
        chunk_size: int = 512,
        overlap: int = 50,
        strategy: str = "semantic",
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize DocumentChunker.

        Args:
            chunk_size: Target chunk size (characters or tokens)
            overlap: Overlapping characters between chunks
            strategy: Chunking strategy ('fixed_size', 'semantic',
                'sliding_window')
            config: Additional configuration

        TODO (v0.2.1b): Validate strategy parameter
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.strategy = strategy
        self.config = config or {}

    def chunk(self, document: str) -> List[Chunk]:
        """Segment document into chunks.

        Args:
            document: Full document text

        Returns:
            List of Chunk objects with metadata

        Raises:
            ValueError: If document is empty

        TODO (v0.2.1b): Implement chunking logic per strategy
        """
        raise NotImplementedError(
            "DocumentChunker.chunk() implementation scheduled for v0.2.1"
        )

    def merge_chunks(
        self, chunks: List[Chunk], merge_size: int = 2
    ) -> List[Chunk]:
        """Merge consecutive chunks (useful for reconstruction).

        Args:
            chunks: List of Chunk objects
            merge_size: Number of consecutive chunks to merge

        Returns:
            List of merged Chunk objects

        TODO (v0.2.1c): Implement chunk merging
        """
        raise NotImplementedError(
            "Chunk merging scheduled for v0.2.1"
        )


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

    HEADER_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$')

    def __init__(self, config: Optional[ChunkingConfig] = None) -> None:
        """Initialize the chunker.

        Args:
            config: Chunking configuration. If None, uses default
                ChunkingConfig (split on ## and ###).
        """
        self.config = config or ChunkingConfig()
        logger.info(
            "MarkdownChunker initialized: min_level=%d, max_level=%d",
            self.config.min_level, self.config.max_level,
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
        if not isinstance(document, str):
            raise TypeError(
                "document must be a string, got %s" % type(document).__name__
            )

        if not document.strip():
            logger.warning("Empty document provided, returning empty chunk list")
            return []

        lines = document.split("\n")
        chunks: List[Chunk] = []
        chunk_index = 1

        # --- Current chunk state ---
        current_title: Optional[str] = None
        current_level: int = 0
        current_lines: List[str] = []
        current_source_line: int = 1
        in_code_block = False

        for line_num, line in enumerate(lines, start=1):
            # --- Fenced code block state tracking ---
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block

            # --- Header detection ---
            match = self.HEADER_PATTERN.match(line)

            if match and in_code_block:
                logger.warning(
                    "Header-like line inside code block at line %d, "
                    "skipping as split point",
                    line_num,
                )
                current_lines.append(line)
                continue

            if match and not in_code_block:
                hashes, title = match.group(1), match.group(2)
                level = len(hashes)

                # --- Check if header is within configured range ---
                if self.config.min_level <= level <= self.config.max_level:
                    # Flush current buffer
                    content = "\n".join(current_lines).strip()

                    if current_title is not None:
                        # Emit the previous chunk
                        word_count, char_count = self._compute_stats(content)
                        chunk = Chunk(
                            id=self._make_chunk_id(chunk_index),
                            title=current_title,
                            level=current_level,
                            content=content,
                            word_count=word_count if self.config.compute_stats else 0,
                            char_count=char_count if self.config.compute_stats else 0,
                            source_line=(
                                current_source_line
                                if self.config.track_source_lines else 0
                            ),
                        )
                        chunks.append(chunk)
                        logger.debug(
                            "New chunk started: id=%s, title=%s, level=%d at line %d",
                            chunk.id, chunk.title, chunk.level, chunk.source_line,
                        )
                        chunk_index += 1
                    elif content and self.config.include_preamble:
                        # Emit preamble chunk
                        word_count, char_count = self._compute_stats(content)
                        preamble = Chunk(
                            id=self._make_chunk_id(chunk_index),
                            title="(Preamble)",
                            level=0,
                            content=content,
                            word_count=word_count if self.config.compute_stats else 0,
                            char_count=char_count if self.config.compute_stats else 0,
                            source_line=1 if self.config.track_source_lines else 0,
                        )
                        chunks.append(preamble)
                        logger.debug(
                            "Preamble chunk created: %d chars", char_count,
                        )
                        chunk_index += 1

                    # Start new chunk
                    current_title = title.strip()
                    current_level = level
                    current_lines = []
                    current_source_line = line_num
                    continue
                else:
                    logger.debug(
                        "Header at level %d outside range [%d, %d], "
                        "treating as content",
                        level, self.config.min_level, self.config.max_level,
                    )

            # --- Append line to current buffer ---
            current_lines.append(line)

        # --- Flush final buffer ---
        content = "\n".join(current_lines).strip()

        if current_title is not None:
            word_count, char_count = self._compute_stats(content)
            chunk = Chunk(
                id=self._make_chunk_id(chunk_index),
                title=current_title,
                level=current_level,
                content=content,
                word_count=word_count if self.config.compute_stats else 0,
                char_count=char_count if self.config.compute_stats else 0,
                source_line=(
                    current_source_line
                    if self.config.track_source_lines else 0
                ),
            )
            chunks.append(chunk)
            logger.debug(
                "New chunk started: id=%s, title=%s, level=%d at line %d",
                chunk.id, chunk.title, chunk.level, chunk.source_line,
            )
        elif content and self.config.include_preamble:
            # Entire document is preamble (no matching headers)
            word_count, char_count = self._compute_stats(content)
            preamble = Chunk(
                id=self._make_chunk_id(chunk_index),
                title="(Preamble)",
                level=0,
                content=content,
                word_count=word_count if self.config.compute_stats else 0,
                char_count=char_count if self.config.compute_stats else 0,
                source_line=1 if self.config.track_source_lines else 0,
            )
            chunks.append(preamble)
            logger.debug("Preamble chunk created: %d chars", char_count)

        logger.info(
            "Chunking complete: %d chunks from %d-line document",
            len(chunks), len(lines),
        )
        return chunks

    def _compute_stats(self, content: str) -> tuple:
        """Compute word and character counts for content.

        Args:
            content: Text content to analyze.

        Returns:
            Tuple of (word_count, char_count).
        """
        char_count = len(content)
        word_count = len(content.split()) if content.strip() else 0
        return word_count, char_count

    def _make_chunk_id(self, index: int) -> str:
        """Generate a zero-padded chunk ID.

        Args:
            index: 1-based chunk sequence number.

        Returns:
            String in format 'chunk-NNN'.
        """
        return f"chunk-{index:03d}"


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

