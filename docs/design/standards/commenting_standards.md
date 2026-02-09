# Code Commenting & Docstring Standards — Haiku Protocol

<aside>

**Scope:** All phases (v0.1.x through v0.4.x)

**Status:** Active

**Applies To:** All Python source in `src/`, `tests/`, and scripts

**Deliverable:** Enforceable rules for docstrings, inline comments, type hints, and TODO conventions across the entire codebase

</aside>

---

## Purpose

This document establishes the commenting and code documentation standards for the Haiku Protocol project. Comments and docstrings are the primary way developers understand intent, contracts, and design decisions. These standards ensure consistency, prevent comment rot, and make the codebase navigable for current and future contributors.

---

## Commenting Philosophy

### Core Principles

1. **Code tells you *what*; comments tell you *why*.** If code is clear, don't restate it in a comment.
2. **Docstrings are mandatory; inline comments are situational.** Every public module, class, and function gets a docstring. Inline comments explain only what isn't obvious.
3. **Wrong comments are worse than no comments.** A stale comment that contradicts the code actively misleads. Maintain comments when you change code.
4. **Type hints are documentation.** Use them on all public function signatures — they tell the reader what goes in and what comes out without reading the body.
5. **Comments are not a substitute for clear code.** If you need a paragraph to explain a function, refactor the function first.

---

## Docstring Standard: Google Style

Haiku Protocol uses **Google-style docstrings** (as recognized by Sphinx, VSCode, and most Python tooling).

### Why Google Style

| Style | Verdict | Rationale |
|-------|---------|-----------|
| Google | Required | Readable, concise, widely supported |
| NumPy | Not used | More verbose than needed for this project |
| Sphinx/reST | Not used | Harder to read in source code |
| Epydoc | Not used | Outdated |

---

## Module-Level Docstrings

Every `.py` file must start with a module docstring.

### Template

```python
"""
module_name.py - Brief One-Line Description
============================================

Extended description of the module's purpose. What does this module do?
What role does it play in the Haiku Protocol pipeline?

Classes:
    ClassName: Brief description

Functions:
    function_name: Brief description (for standalone functions)

Implementation Status:
    - STUB (v0.1.3c): Interface only
    - IMPLEMENTATION: Phase X (vX.Y.Z)

Related:
    - v0.X.Y — Related specification or research document
"""
```

### Example (encoder.py)

```python
"""
encoder.py - Haiku Protocol Compression Pipeline
=================================================

Main orchestration module for document compression using semantic condensation.
Coordinates document chunking, entity extraction, and CNL synthesis.

Classes:
    HaikuEncoder: Main compression pipeline orchestrator

Typical usage:
    from src.encoder import HaikuEncoder

    encoder = HaikuEncoder()
    compressed = encoder.encode(document_text)

Implementation Status:
    - STUB (v0.1.3c): Method signatures and interface only
    - IMPLEMENTATION: Phase 2 (v0.2.0 — Encoder Development)
"""
```

### Rules

- The first line is the module filename, a dash, and a brief description
- The underline (`===`) matches the length of the first line
- Include `Classes:` and/or `Functions:` sections listing public API
- Include `Implementation Status:` for stubs (remove when implemented)
- Include `Related:` section for cross-references to spec documents

---

## Class Docstrings

Every class must have a docstring immediately after the `class` declaration.

### Template

```python
class ClassName:
    """
    Brief one-line description of the class.

    Extended description: What does this class represent?
    What is its responsibility in the system?

    Attributes:
        attribute_name: Description of the attribute
        another_attr: Description with type info if not obvious

    Example:
        >>> obj = ClassName(param="value")
        >>> result = obj.method()
    """
```

### Example (DocumentChunker)

```python
class DocumentChunker:
    """
    Segments documents into chunks for processing.

    Supports multiple chunking strategies:
    - fixed_size: Fixed character/token count
    - semantic: Sentence/paragraph boundaries
    - sliding_window: Overlapping windows

    Attributes:
        chunk_size: Target size per chunk (characters or tokens)
        overlap: Number of overlapping characters between chunks
        strategy: Chunking strategy name
        config: Additional configuration dictionary

    Example:
        >>> chunker = DocumentChunker(chunk_size=512, strategy="semantic")
        >>> chunks = chunker.chunk("Long document text...")
        >>> print(f"Created {len(chunks)} chunks")
    """
```

### Rules

- First line: single sentence, imperative mood ("Segments documents..." not "This class segments...")
- `Attributes:` section lists all public instance attributes
- `Example:` section shows basic usage (doctest-compatible syntax)
- Do NOT document `__init__` parameters here — document them in `__init__`'s own docstring

---

## Method and Function Docstrings

Every public method and function must have a docstring.

### Template

```python
def method_name(self, param1: str, param2: int = 10) -> ReturnType:
    """
    Brief one-line description in imperative mood.

    Extended description if the behavior isn't fully captured
    by the one-liner. Explain algorithm, constraints, or
    non-obvious behavior.

    Args:
        param1: Description of the parameter
        param2: Description with default noted if non-obvious

    Returns:
        Description of what is returned. For complex returns,
        describe the structure.

    Raises:
        ValueError: When param1 is empty
        RuntimeError: When the pipeline fails

    Example:
        >>> result = obj.method_name("input", param2=20)
        >>> print(result)
    """
```

### Example (encode method)

```python
def encode(self, document: str) -> str:
    """
    Compress a document into CNL-formatted text.

    Runs the full compression pipeline: chunking, entity extraction,
    CNL synthesis, and output formatting. The input document can be
    any length; it will be chunked automatically.

    Args:
        document: Input document text (plain text, any length)

    Returns:
        CNL-formatted compressed text as a single string

    Raises:
        ValueError: If document is empty or whitespace-only
        RuntimeError: If any pipeline stage fails

    Example:
        >>> encoder = HaikuEncoder()
        >>> cnl = encoder.encode("The algorithm uses Python libraries.")
        >>> print(cnl)
        [CNL: algorithm uses Python libraries]
    """
```

### Rules

- First line: imperative mood ("Compress a document" not "Compresses a document" or "This method compresses")
- `Args:` — every parameter except `self`/`cls`. Description only, type comes from signature.
- `Returns:` — describe what is returned. If None, omit the section.
- `Raises:` — list exceptions the caller should expect. Omit if none.
- `Example:` — at least one for complex methods. Optional for simple getters.
- Omit sections that don't apply (no empty `Raises:` section)

---

## Private Method Docstrings

Private methods (single underscore `_method`) require a docstring only if:
- The method is longer than 10 lines
- The method's purpose isn't obvious from its name and parameters
- The method contains complex logic or algorithms

```python
def _compute_overlap_boundaries(self, chunks: List[Chunk]) -> List[Tuple[int, int]]:
    """Calculate character boundaries where consecutive chunks overlap."""
    # Simple one-liner docstring is sufficient for private methods
    ...
```

Double-underscore methods (`__method`) are name-mangled and rarely used. Document them if they exist.

---

## Dataclass and NamedTuple Docstrings

Dataclasses get a one-line class docstring. Field descriptions are inline comments:

```python
@dataclass
class Chunk:
    """Represents a document chunk with positional metadata."""
    text: str              # The chunk's text content
    chunk_id: int          # Zero-indexed position in the document
    start_char: int        # Starting character offset in original document
    end_char: int          # Ending character offset in original document
    token_count: int       # Number of tokens (measured by tiktoken)


@dataclass
class CompressionMetrics:
    """Compression quality measurements for a single encode operation."""
    compression_ratio: float       # (original - compressed) / original, 0.0 to 1.0
    original_tokens: int           # Token count of input document
    compressed_tokens: int         # Token count of CNL output
    semantic_similarity: float     # Cosine similarity of embeddings, 0.0 to 1.0
    information_retention: float   # Measured against benchmark, 0.0 to 1.0
    processing_time_ms: float      # Wall-clock time in milliseconds
```

---

## `__init__` Docstrings

Document `__init__` parameters in the `__init__` method itself, not in the class docstring:

```python
class HaikuEncoder:
    """Main Haiku Protocol compression pipeline."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize HaikuEncoder with configuration.

        Args:
            config: Configuration dictionary with API keys, model names, etc.
                    If None, loads from environment variables via Config class.
        """
        self.config = config or {}
```

---

## Type Hints

### Requirements

- All public function signatures must have type hints for parameters and return type
- Private functions should have type hints when the types aren't obvious
- Use `from __future__ import annotations` for forward references (Python 3.8/3.9 compatibility)

### Type Hint Patterns

```python
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

# Basic types
def encode(self, document: str) -> str:

# Optional parameters
def __init__(self, config: Optional[Dict[str, Any]] = None):

# Multiple return values
def encode_with_metrics(self, document: str) -> Tuple[str, CompressionMetrics]:

# List of custom types
def chunk(self, document: str) -> List[Chunk]:

# Dictionary with typed values
def compare_with_baseline(self, ...) -> Dict[str, Any]:

# None return (void functions)
def setup_logging(level: str = None) -> None:

# Boolean returns
def validate(cls) -> bool:
```

### Type Hint Dos and Don'ts

| Do | Don't |
|----|-------|
| `def encode(self, document: str) -> str:` | `def encode(self, document):` |
| `Optional[Dict[str, Any]]` for nullable params | `dict` without specifying key/value types |
| `List[Chunk]` for typed collections | `list` without element type |
| Return type on every public function | Omit return type because "it's obvious" |

---

## Inline Comments

### When to Write Inline Comments

Write an inline comment when:

1. **The "why" isn't obvious** — business rules, design decisions, workarounds
2. **Magic numbers or constants** need explanation
3. **Algorithm steps** need annotation
4. **Workarounds** for known issues or library quirks
5. **Section separators** in long functions

### When NOT to Write Inline Comments

Do not write a comment when:

1. **The code is self-explanatory** — `count += 1  # increment count` is noise
2. **A better variable name would suffice** — rename `x` to `chunk_count` instead of commenting
3. **The docstring already covers it** — don't repeat the docstring in line comments
4. **The comment restates the code** — `return True  # returns True` adds nothing

### Good vs Bad Inline Comments

```python
# === GOOD inline comments ===

# Use semantic strategy because fixed-size splits mid-sentence,
# reducing CNL quality (measured in v0.0.3 benchmarks)
strategy = "semantic"

# OpenAI API requires max_tokens >= 1, but we use 10 as minimum
# to get meaningful test responses
max_tokens = max(10, requested_tokens)

# Sliding window overlap prevents entity loss at chunk boundaries
# (see v0.0.2b: Grammar Specification, Section 4.2)
overlap = int(chunk_size * 0.1)


# === BAD inline comments ===

# Set strategy to semantic
strategy = "semantic"

# Set max tokens
max_tokens = 10

# Calculate overlap
overlap = int(chunk_size * 0.1)

# Import os module
import os
```

### Section Comments in Long Functions

For functions longer than 30 lines, use section comments:

```python
def encode(self, document: str) -> str:
    # ── Validation ──
    if not document or not document.strip():
        raise ValueError("Document is empty")

    # ── Chunking ──
    chunks = self.chunker.chunk(document)
    logger.debug("Created %d chunks", len(chunks))

    # ── Entity Extraction ──
    all_entities = []
    for chunk in chunks:
        entities = self.extractor.extract(chunk.text, chunk.chunk_id)
        all_entities.append(entities)

    # ── CNL Synthesis ──
    cnl_statements = self.synthesizer.synthesize(all_entities)

    # ── Output Assembly ──
    return "\n".join(stmt.statement for stmt in cnl_statements)
```

---

## TODO Comments

### Format

```python
# TODO (vX.Y.Z): Description of what needs to be done
```

### Rules

1. Every TODO must include a version reference in parentheses
2. The version indicates when the TODO should be resolved
3. TODOs without version references are not allowed
4. TODOs should be actionable — describe what to do, not what's missing

### Examples

```python
# TODO (v0.2.0): Load config from environment, validate required keys
# TODO (v0.2.1): Implement chunking logic per strategy
# TODO (v0.2.3): Load CNL grammar rules from v0.0.2c BNF
# TODO (v0.2.4): Compute embedding similarity using sentence-transformers
# TODO (v0.3.1): Add file upload widget for PDF and TXT documents
```

### Cross-Reference TODOs

When a TODO depends on another specification document, include a reference:

```python
# TODO (v0.2.3): Apply grammar rules to generate statements
#   Source: docs/phase-0/v0.0.2/grammar_formalization_bnf.md
#   Artifact: research/haiku_grammar.bnf (when generated)
```

### Resolving TODOs

When implementing a TODO:
1. Remove the TODO comment entirely
2. Replace with actual implementation
3. Do NOT leave `# DONE:` or `# RESOLVED:` comments

---

## File Header Comments

### Not Required

Python files should NOT have boilerplate header comments like:

```python
# ============================================
# File: encoder.py
# Author: Developer Name
# Date: 2026-02-05
# Description: Encoder module
# ============================================
```

This information belongs in:
- **File name** — the file system already tells you the filename
- **Author** — git blame
- **Date** — git log
- **Description** — the module docstring

### Exception: Shebang Lines

Scripts intended for direct execution may include a shebang:

```python
#!/usr/bin/env python3
"""
test_api.py - API Connection Testing Module
============================================
...
"""
```

---

## Comment Formatting Rules

### Spacing

```python
# Good — space after hash
# This is a comment

# Bad — no space after hash
#This is a comment

# Good — inline comment with 2 spaces before hash
x = 10  # Maximum retry count

# Bad — inline comment too close
x = 10 # Maximum retry count
x = 10    # Maximum retry count (too far)
```

### Length

- Inline comments should not cause the line to exceed 100 characters
- Multi-line comments use separate `#` lines, not continuation

```python
# Good — multi-line comment
# The compression ratio is calculated as the difference between
# original and compressed token counts, divided by original count.
ratio = (original - compressed) / original

# Bad — single very long comment
# The compression ratio is calculated as the difference between original and compressed token counts, divided by original count.
ratio = (original - compressed) / original
```

---

## Templates

### New Module Template

```python
"""
module_name.py - Brief Description
====================================

Extended description of what this module does and its role
in the Haiku Protocol pipeline.

Classes:
    ClassName: Brief description

Implementation Status:
    - STUB (v0.1.3c): Interface only
    - IMPLEMENTATION: Phase X (vX.Y.Z)

Related:
    - vX.Y — Related specification
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ClassName:
    """
    Brief one-line description.

    Extended description of the class purpose.

    Attributes:
        attr_name: Description

    Example:
        >>> obj = ClassName()
        >>> obj.method("input")
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize ClassName.

        Args:
            config: Configuration dictionary. Defaults to env vars if None.
        """
        self.config = config or {}

    def method(self, param: str) -> str:
        """
        Brief description of what this method does.

        Args:
            param: Description of the parameter

        Returns:
            Description of the return value

        Raises:
            ValueError: When param is invalid
        """
        raise NotImplementedError(
            "ClassName.method() implementation scheduled for vX.Y.Z"
        )
```

### New Test Module Template

```python
"""Tests for src/module_name.py."""

import pytest
from src.module_name import ClassName


class TestClassName:
    """Tests for ClassName class."""

    def test_method_valid_input_returns_expected(self):
        """Method returns expected output for valid input."""
        # Arrange
        obj = ClassName()

        # Act
        result = obj.method("valid input")

        # Assert
        assert isinstance(result, str)

    def test_method_empty_input_raises_value_error(self):
        """Method raises ValueError for empty input."""
        obj = ClassName()
        with pytest.raises(ValueError):
            obj.method("")
```

---

## Linting and Enforcement

### Recommended Tools

| Tool | Purpose | Configuration |
|------|---------|---------------|
| `pydocstyle` | Docstring style checking | `--convention=google` |
| `flake8` | General Python linting (includes comment checks) | `.flake8` config file |
| `mypy` | Type hint validation | `mypy.ini` or `pyproject.toml` |

### Running Checks

```bash
# Check docstring style (Google convention)
pydocstyle src/ --convention=google

# Check type hints
mypy src/ --ignore-missing-imports

# Check general style (includes comment spacing)
flake8 src/
```

### Enforcement Priority

For Haiku Protocol, enforcement is progressive:

| Phase | Enforcement |
|-------|------------|
| v0.1.x | Manual review — follow templates in stubs |
| v0.2.x | `mypy` and `flake8` run on changed files |
| v0.3.x | `pydocstyle` added to pre-commit checks |
| v0.4.x (release) | All tools enforced, CI/CD gate |

---

## Dos and Don'ts

### Do

- Write a docstring for every public module, class, and function
- Use Google-style docstring format consistently
- Include type hints on all public function signatures
- Write inline comments for non-obvious "why" decisions
- Include version-tagged TODOs for unfinished work
- Use `Example:` sections for complex APIs
- Keep docstrings up to date when code changes
- Use section comments (`# ── Section ──`) in long functions

### Don't

- Comment obvious code (`x += 1  # add 1 to x`)
- Leave stale comments that contradict the code
- Use TODO comments without a version reference
- Write file header comments (author, date, etc.) — use git
- Repeat the function signature in the docstring
- Write multi-paragraph inline comments (use docstring instead)
- Use comments to disable code (delete it; git has history)
- Mix docstring styles (Google in one file, NumPy in another)

---

## Acceptance Criteria (for this document)

- [ ] All modules in `src/` have module-level docstrings following the template
- [ ] All public classes have docstrings with Attributes and Example sections
- [ ] All public methods have docstrings with Args, Returns, and Raises (as applicable)
- [ ] All public function signatures include type hints
- [ ] Dataclasses have one-line docstrings and inline field comments
- [ ] TODO comments include version references: `# TODO (vX.Y.Z): description`
- [ ] No file-header boilerplate (author, date, etc.)
- [ ] Inline comments explain "why" not "what"
- [ ] Google-style docstrings used consistently (no NumPy or reST style)
- [ ] `__init__` parameters documented in `__init__` docstring (not class docstring)
- [ ] Private methods documented only when non-obvious
- [ ] No commented-out code blocks in `src/` (delete, use git history)

---

## Related Documents

- [v0.1.3c — Source Module Stubs](../phase-1/v0.1.3/source_module_stubs.md) — Reference implementation of all docstring patterns
- [v0.1.2c — Configuration Module](../phase-1/v0.1.2/configuration_module_implementation.md) — Config class docstring examples
- [Testing Standards](testing_standards.md) — Test docstring and naming conventions
- [Logging Standards](logging_standards.md) — When to log vs. when to comment
- [Documentation Requirements](documentation_requirements.md) — Project-level documentation beyond code
