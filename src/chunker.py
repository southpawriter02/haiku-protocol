"""
chunker.py - Document Chunking and Segmentation
================================================

Segments markdown documents into semantically bounded chunks
based on header boundaries for processing through the encoder
pipeline.

Classes:
    Chunk: Dataclass representing a document segment (v0.2.1a)
    ChunkingConfig: Configuration for chunking behavior (v0.2.1a)
    DocumentChunker: Document segmentation orchestrator (stub, v0.2.1b)

Implementation Status:
    - v0.2.1a: Chunk data model, ChunkingConfig, serialization
    - STUB: DocumentChunker (v0.2.1b — MarkdownChunker Core)

Related: v0.2.1 — Chunking Module
"""

import logging
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
