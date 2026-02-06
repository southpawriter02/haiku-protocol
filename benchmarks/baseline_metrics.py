#!/usr/bin/env python3
"""
baseline_metrics.py - Raw Metrics Collection for Haiku Protocol Benchmarking
=============================================================================

Reads three curated sample documents and computes comprehensive token and
content analysis metrics. Outputs structured JSON to benchmarks/raw_metrics.json.

Functions:
    get_tokenizer: Obtain a tokenizer instance (tiktoken or regex fallback)
    count_tokens: Count tokens in a text string
    get_unique_token_count: Count distinct token IDs in a text string
    count_sentences: Count sentences using sentence-end markers
    count_procedures: Count procedural step/part/section markers
    count_prerequisites: Count prerequisite-related keywords
    count_commands: Count backtick-enclosed code/command blocks
    count_warnings: Count warning/caution/note/important markers
    count_conditions: Count conditional keywords (if, else, when, etc.)
    count_cross_references: Count cross-reference markers (see also, etc.)
    compute_primary_metrics: Compute all primary metrics for a document
    compute_content_analysis: Compute all content analysis metrics
    analyze_document: Analyze a single document and return full metrics dict
    analyze_all_samples: Analyze all sample documents in a directory
    main: Entry point for CLI execution

Implementation Status:
    - IMPLEMENTATION: Phase 0 (v0.0.3b)

Related:
    - v0.0.3b — Token Counting & Raw Metrics Collection
    - v0.0.3a — Sample Document Selection & Curation
"""

import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Tokenizer Configuration ──
# The Haiku Protocol uses cl100k_base (GPT-4 compatible) as the standard
# token counting encoding. When tiktoken is available with network access
# to download its BPE data, it is used. Otherwise, a well-characterized
# regex-based approximation is provided as a fallback.
#
# The fallback uses the same regex pattern as cl100k_base to split text
# into pre-token chunks, then counts those chunks. This closely tracks
# tiktoken's actual output for English procedural documentation (the
# domain of all Haiku Protocol benchmarks).
#
# Decision recorded: v0.0.3b Decision Log — "Regex Fallback Tokenizer"

TOKENIZER_MODE = "uninitialized"  # Set to "tiktoken" or "regex_fallback"

# cl100k_base regex pattern (from OpenAI's tiktoken source)
# This splits text into the same pre-token units that cl100k_base uses
# before applying BPE merges.
CL100K_PATTERN = (
    r"'(?i:[sdmt]|ll|ve|re)"
    r"|[^\r\n\p{L}\p{N}]?+\p{L}+"
    r"|\p{N}{1,3}"
    r"| ?[^\s\p{L}\p{N}]++[\r\n]*"
    r"|\s*[\r\n]"
    r"|\s+(?!\S)"
    r"|\s+"
)

# Module-level encoder (initialized lazily by get_tokenizer)
_tiktoken_encoder = None
_regex_pattern = None


def get_tokenizer() -> Tuple[str, Any]:
    """
    Obtain a tokenizer instance, preferring tiktoken with cl100k_base.

    Attempts to load the tiktoken cl100k_base encoding. If tiktoken is
    not installed or cannot download its BPE data file (e.g., in an
    air-gapped environment), falls back to a regex-based approximation
    using the same pre-tokenization pattern as cl100k_base.

    Returns:
        Tuple of (mode_string, tokenizer_object) where mode_string is
        either "tiktoken" or "regex_fallback", and tokenizer_object is
        the tiktoken Encoding instance or compiled regex pattern.

    Raises:
        RuntimeError: If neither tiktoken nor regex can be initialized
    """
    global TOKENIZER_MODE, _tiktoken_encoder, _regex_pattern

    if TOKENIZER_MODE != "uninitialized":
        if TOKENIZER_MODE == "tiktoken":
            return TOKENIZER_MODE, _tiktoken_encoder
        return TOKENIZER_MODE, _regex_pattern

    # Attempt 1: tiktoken with cl100k_base
    try:
        import tiktoken
        _tiktoken_encoder = tiktoken.get_encoding("cl100k_base")
        TOKENIZER_MODE = "tiktoken"
        logger.info(
            "Tokenizer initialized: tiktoken %s with cl100k_base encoding",
            tiktoken.__version__
        )
        return TOKENIZER_MODE, _tiktoken_encoder
    except ImportError:
        logger.warning("tiktoken not installed; falling back to regex tokenizer")
    except Exception as exc:
        logger.warning(
            "tiktoken cl100k_base unavailable (%s: %s); "
            "falling back to regex tokenizer",
            type(exc).__name__, exc
        )

    # Attempt 2: Regex fallback using cl100k_base pre-tokenization pattern
    try:
        import regex
        _regex_pattern = regex.compile(CL100K_PATTERN)
        TOKENIZER_MODE = "regex_fallback"
        logger.info(
            "Tokenizer initialized: regex fallback using cl100k_base pattern"
        )
        return TOKENIZER_MODE, _regex_pattern
    except ImportError:
        logger.error("Neither tiktoken nor regex library available")
        raise RuntimeError(
            "Cannot initialize tokenizer: install tiktoken or regex"
        )


def count_tokens(text: str) -> int:
    """
    Count tokens in a text string using the active tokenizer.

    Uses tiktoken cl100k_base encoding when available, or a regex-based
    approximation that splits on the same pre-tokenization pattern.

    Args:
        text: Input text to tokenize

    Returns:
        Number of tokens (int)

    Raises:
        ValueError: If text is None
    """
    if text is None:
        raise ValueError("Cannot tokenize None input")

    mode, tokenizer = get_tokenizer()

    if mode == "tiktoken":
        tokens = tokenizer.encode(text)
        logger.debug("Token count (tiktoken): %d", len(tokens))
        return len(tokens)
    else:
        # Regex fallback: count pre-token chunks
        chunks = tokenizer.findall(text)
        logger.debug("Token count (regex fallback): %d", len(chunks))
        return len(chunks)


def get_unique_token_count(text: str) -> int:
    """
    Count distinct token IDs in a text string.

    For tiktoken mode, returns the number of unique token IDs.
    For regex fallback mode, returns the number of unique string chunks.

    Args:
        text: Input text to analyze

    Returns:
        Number of unique tokens (int)

    Raises:
        ValueError: If text is None
    """
    if text is None:
        raise ValueError("Cannot tokenize None input")

    mode, tokenizer = get_tokenizer()

    if mode == "tiktoken":
        tokens = tokenizer.encode(text)
        unique_count = len(set(tokens))
        logger.debug("Unique token count (tiktoken): %d", unique_count)
        return unique_count
    else:
        # Regex fallback: count unique string chunks
        chunks = tokenizer.findall(text)
        unique_count = len(set(chunks))
        logger.debug("Unique token count (regex fallback): %d", unique_count)
        return unique_count


def count_sentences(text: str) -> int:
    """
    Count sentences by splitting on sentence-end markers.

    Uses a simple regex split on period, exclamation mark, and question
    mark sequences. Known limitation: abbreviations (e.g., "e.g.") and
    ellipses ("...") may cause miscounts.

    Args:
        text: Input text to analyze

    Returns:
        Number of non-empty sentences (int)

    Raises:
        ValueError: If text is None or empty
    """
    if not text or not text.strip():
        raise ValueError("Cannot count sentences in empty text")

    sentences = re.split(r'[.!?]+', text)
    count = len([s for s in sentences if s.strip()])
    logger.debug("Sentence count: %d", count)
    return count


def count_procedures(text: str) -> int:
    """
    Count procedural markers (Step N, Part N, Section N headers).

    Matches patterns like "Step 1:", "Part 2", "Section 3" using
    case-insensitive regex.

    Args:
        text: Document text to analyze

    Returns:
        Count of procedural markers (int)
    """
    count = len(re.findall(
        r'\b(?:step|part|section)\s+\d+', text, re.IGNORECASE
    ))
    logger.debug("Procedure markers: %d", count)
    return count


def count_prerequisites(text: str) -> int:
    """
    Count prerequisite-related keywords.

    Matches: prerequisite, require, before, first, ensure.
    Case-insensitive.

    Args:
        text: Document text to analyze

    Returns:
        Count of prerequisite markers (int)
    """
    count = len(re.findall(
        r'\b(?:prerequisite|require|before|first|ensure)\b',
        text, re.IGNORECASE
    ))
    logger.debug("Prerequisite markers: %d", count)
    return count


def count_commands(text: str) -> int:
    """
    Count backtick-enclosed code snippets and command blocks.

    Matches both inline code (single backtick pairs) and fenced code
    blocks (triple backtick pairs). Each inline `code` match counts as
    one command; each fenced block counts as one command.

    Args:
        text: Document text to analyze

    Returns:
        Count of code/command blocks (int)
    """
    # Count fenced code blocks (```...```)
    fenced = len(re.findall(r'```[\s\S]*?```', text))
    # Count inline code (`...`) that are NOT part of fenced blocks
    # Simple approach: count all backtick pairs, subtract fenced
    inline = len(re.findall(r'`[^`]+`', text))
    count = fenced + inline
    logger.debug("Command blocks: %d (fenced=%d, inline=%d)", count, fenced, inline)
    return count


def count_warnings(text: str) -> int:
    """
    Count warning, caution, note, important, and critical markers.

    Case-insensitive keyword match.

    Args:
        text: Document text to analyze

    Returns:
        Count of warning markers (int)
    """
    count = len(re.findall(
        r'\b(?:warning|caution|note|important|critical)\b',
        text, re.IGNORECASE
    ))
    logger.debug("Warning markers: %d", count)
    return count


def count_conditions(text: str) -> int:
    """
    Count conditional keywords.

    Matches: if, else, when, unless, depending, otherwise.
    Case-insensitive.

    Args:
        text: Document text to analyze

    Returns:
        Count of conditional keywords (int)
    """
    count = len(re.findall(
        r'\b(?:if|else|when|unless|depending|otherwise)\b',
        text, re.IGNORECASE
    ))
    logger.debug("Conditional markers: %d", count)
    return count


def count_cross_references(text: str) -> int:
    """
    Count cross-reference markers.

    Matches: see also, refer, reference, link, consult.
    Case-insensitive.

    Args:
        text: Document text to analyze

    Returns:
        Count of cross-reference markers (int)
    """
    count = len(re.findall(
        r'\b(?:see also|refer|reference|link|consult)\b',
        text, re.IGNORECASE
    ))
    logger.debug("Cross-reference markers: %d", count)
    return count


def compute_primary_metrics(text: str) -> Dict[str, Any]:
    """
    Compute all primary metrics for a document.

    Calculates character count, word count, sentence count, token count,
    unique token count, and derived ratios (avg tokens per sentence,
    avg tokens per word, content density score).

    Args:
        text: Document text to analyze

    Returns:
        Dictionary with all primary metric fields

    Raises:
        ValueError: If text is empty or None
    """
    if not text or not text.strip():
        raise ValueError("Cannot compute metrics for empty text")

    char_count = len(text)
    word_count = len(text.split())
    sentence_count = count_sentences(text)
    token_count = count_tokens(text)
    unique_token_count = get_unique_token_count(text)

    # Derived metrics with safe division and 2-decimal rounding
    avg_tokens_per_sentence = (
        round(token_count / sentence_count, 2) if sentence_count > 0 else 0.0
    )
    avg_tokens_per_word = (
        round(token_count / word_count, 2) if word_count > 0 else 0.0
    )
    content_density_score = (
        round((token_count / word_count) * 10, 2) if word_count > 0 else 0.0
    )

    metrics = {
        "character_count": char_count,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "token_count": token_count,
        "unique_token_count": unique_token_count,
        "avg_tokens_per_sentence": avg_tokens_per_sentence,
        "avg_tokens_per_word": avg_tokens_per_word,
        "content_density_score": content_density_score,
    }

    logger.info(
        "Primary metrics computed: chars=%d, words=%d, tokens=%d, sentences=%d",
        char_count, word_count, token_count, sentence_count
    )
    return metrics


def compute_content_analysis(text: str) -> Dict[str, int]:
    """
    Compute all content analysis metrics for a document.

    Counts procedural markers, prerequisites, commands, warnings,
    conditions, and cross-references.

    Args:
        text: Document text to analyze

    Returns:
        Dictionary with all content analysis metric fields
    """
    analysis = {
        "number_of_procedures": count_procedures(text),
        "number_of_prerequisites": count_prerequisites(text),
        "number_of_commands": count_commands(text),
        "number_of_warnings": count_warnings(text),
        "number_of_conditions": count_conditions(text),
        "number_of_cross_references": count_cross_references(text),
    }

    logger.info(
        "Content analysis computed: procedures=%d, prerequisites=%d, "
        "commands=%d, warnings=%d, conditions=%d, cross_refs=%d",
        analysis["number_of_procedures"],
        analysis["number_of_prerequisites"],
        analysis["number_of_commands"],
        analysis["number_of_warnings"],
        analysis["number_of_conditions"],
        analysis["number_of_cross_references"],
    )
    return analysis


def analyze_document(
    file_path: Path,
    tier: str,
) -> Dict[str, Any]:
    """
    Analyze a single document and return complete metrics dictionary.

    Reads the document from disk, computes primary metrics and content
    analysis, and returns a structured result dictionary matching the
    raw_metrics.json schema.

    Args:
        file_path: Path to the markdown document file
        tier: Complexity tier label (e.g., "Simple", "Medium", "Complex")

    Returns:
        Dictionary with tier, file_path, metrics, and content_analysis
        sub-dictionaries. If reading fails, returns a dict with an
        "error" key instead.
    """
    logger.info("Analyzing document: %s (tier=%s)", file_path.name, tier)

    try:
        text = file_path.read_text(encoding="utf-8")
    except (OSError, IOError) as exc:
        logger.error("Failed to read %s: %s", file_path, exc)
        return {"error": "Failed to read %s: %s" % (file_path, exc)}

    primary = compute_primary_metrics(text)
    content = compute_content_analysis(text)

    result = {
        "tier": tier,
        "file_path": str(file_path),
        "metrics": primary,
        "content_analysis": content,
    }

    logger.info(
        "Document analysis complete: %s — %d tokens, tier=%s",
        file_path.name, primary["token_count"], tier
    )
    return result


def analyze_all_samples(samples_dir: Path) -> Dict[str, Any]:
    """
    Analyze all three sample documents and return the full results structure.

    Reads simple.md, medium.md, and complex.md from the samples directory,
    computes metrics for each, and returns a dictionary matching the
    raw_metrics.json schema with version metadata.

    Args:
        samples_dir: Path to the directory containing sample .md files

    Returns:
        Dictionary with version, encoding, tokenizer, tokenizer_mode,
        and documents list ready for JSON serialization.

    Raises:
        FileNotFoundError: If samples_dir does not exist
    """
    if not samples_dir.exists():
        raise FileNotFoundError(
            "Samples directory not found: %s" % samples_dir
        )

    logger.info("Analyzing all samples in: %s", samples_dir)

    # Initialize tokenizer and record which mode we're using
    mode, _ = get_tokenizer()

    # Define the expected sample files and their tiers
    sample_files = [
        (samples_dir / "simple.md", "Simple"),
        (samples_dir / "medium.md", "Medium"),
        (samples_dir / "complex.md", "Complex"),
    ]

    results = {
        "version": "0.0.3b",
        "encoding": "cl100k_base",
        "tokenizer": "tiktoken" if mode == "tiktoken" else "regex_fallback",
        "tokenizer_mode": mode,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "documents": [],
    }

    # Record tiktoken version if available
    if mode == "tiktoken":
        try:
            import tiktoken
            results["tiktoken_version"] = tiktoken.__version__
        except ImportError:
            pass

    for file_path, tier in sample_files:
        if not file_path.exists():
            logger.warning("Sample file not found: %s (skipping)", file_path)
            continue

        doc_result = analyze_document(file_path, tier)

        if "error" not in doc_result:
            results["documents"].append(doc_result)
        else:
            logger.error("Skipping %s due to error: %s", file_path, doc_result["error"])

    logger.info(
        "Analysis complete: %d documents processed in %s mode",
        len(results["documents"]), mode
    )
    return results


def main() -> Dict[str, Any]:
    """
    Entry point for CLI execution: analyze all samples and write JSON output.

    Returns:
        The results dictionary (also saved to benchmarks/raw_metrics.json)
    """
    # ── Resolve Paths ──
    project_root = Path(__file__).parent.parent
    samples_dir = project_root / "benchmarks" / "samples"
    output_path = project_root / "benchmarks" / "raw_metrics.json"

    logger.info("Project root: %s", project_root)
    logger.info("Samples directory: %s", samples_dir)

    # ── Verify Prerequisites ──
    if not samples_dir.exists():
        logger.error("Samples directory not found: %s", samples_dir)
        print("ERROR: %s not found. Run v0.0.3a first." % samples_dir)
        sys.exit(1)

    # ── Analyze All Samples ──
    results = analyze_all_samples(samples_dir)

    # ── Write Output ──
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logger.info("Results saved to: %s", output_path)

    # ── Print Summary ──
    print("\n" + "=" * 60)
    print("RAW METRICS COLLECTION RESULTS (v0.0.3b)")
    print("=" * 60)
    print("\nTokenizer mode: %s" % results["tokenizer_mode"])
    if "tiktoken_version" in results:
        print("tiktoken version: %s" % results["tiktoken_version"])

    for doc in results["documents"]:
        m = doc["metrics"]
        print(
            "\n  %s (%s)" % (doc["tier"].upper(), Path(doc["file_path"]).name)
        )
        print("    Characters:           %d" % m["character_count"])
        print("    Words:                %d" % m["word_count"])
        print("    Sentences:            %d" % m["sentence_count"])
        print("    Tokens:               %d" % m["token_count"])
        print("    Unique Tokens:        %d" % m["unique_token_count"])
        print("    Avg Tokens/Sentence:  %.2f" % m["avg_tokens_per_sentence"])
        print("    Avg Tokens/Word:      %.2f" % m["avg_tokens_per_word"])
        print("    Content Density:      %.2f" % m["content_density_score"])

        ca = doc["content_analysis"]
        print("    Procedures:           %d" % ca["number_of_procedures"])
        print("    Prerequisites:        %d" % ca["number_of_prerequisites"])
        print("    Commands:             %d" % ca["number_of_commands"])
        print("    Warnings:             %d" % ca["number_of_warnings"])
        print("    Conditions:           %d" % ca["number_of_conditions"])
        print("    Cross-References:     %d" % ca["number_of_cross_references"])

    print("\n" + "=" * 60)
    print("Output saved to: %s" % output_path)
    print("=" * 60)

    return results


if __name__ == "__main__":
    # ── Logging Setup ──
    logging.basicConfig(
        level=logging.DEBUG,
        format=(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d"
            " | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    main()
