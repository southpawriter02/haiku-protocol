#!/usr/bin/env python3
"""
pattern_extractor.py - Semantic Pattern Extraction for Procedural Documentation
================================================================================

Analyzes procedural documentation to identify recurring structural patterns
and semantic elements. Produces frequency analysis and categorized examples
that inform operator design for the Haiku Protocol CNL grammar.

Classes:
    PatternExtractor: Core extraction engine that classifies sentences into
        semantic categories using regex-based recognition markers.

Functions:
    run_corpus_analysis: Convenience function to analyze an entire corpus
        directory and produce a consolidated results dictionary.

Implementation Status:
    - IMPLEMENTATION: Phase 0 (v0.0.2a — Pattern Identification & Corpus Analysis)

Related:
    - v0.0.2a — Pattern Identification & Corpus Analysis (spec)
    - v0.0.2b — Operator Design & Syntax Definition (consumer of output)
    - research/pattern_taxonomy.md (output deliverable)
"""

import json
import logging
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Semantic Category Definitions ──
# Each category maps a human-readable name to a compiled regex pattern.
# Recognition markers are drawn from the v0.0.2a spec's "Semantic Categories
# to Identify" section. The patterns match word boundaries to avoid partial
# matches (e.g., "list" shouldn't match "listening").

CATEGORY_PATTERNS: Dict[str, re.Pattern] = {
    "Actions": re.compile(
        r"\b(start|run|execute|apply|create|delete|install|build|deploy|"
        r"configure|restart|reload|verify|check|test|list|get|post|put|"
        r"stop|push|pull|tag|flush|connect|activate|commit|update|"
        r"monitor|back\s+up|backup|revert|recover|abort|reset|request|"
        r"remove|add|set|initialize|describe)\b",
        re.IGNORECASE,
    ),
    "States": re.compile(
        r"\b(ensure|must be|should be|should show|is owned|exists|"
        r"enabled|disabled|configured|installed|active|running|"
        r"is correctly|are not|remain|stabilizes)\b",
        re.IGNORECASE,
    ),
    "Dependencies": re.compile(
        r"\b(first|then|after|before|once|until|requires|depends|"
        r"prerequisite|prerequisites|following order|step \d+|"
        r"in the following)\b",
        re.IGNORECASE,
    ),
    "Warnings": re.compile(
        r"\b(WARNING|WARN|caution|be careful|do not|never|risk|danger|"
        r"irreversible|will lose|data loss|will delete|breaking changes|"
        r"maintenance window|coordinate with)\b",
        re.IGNORECASE,
    ),
    "Conditions": re.compile(
        r"\b(if|then|else|otherwise|in case|when|unless|on error|"
        r"assuming|if not|if still)\b",
        re.IGNORECASE,
    ),
    "Verifications": re.compile(
        r"\b(verify|validate|confirm|check|test|assert|"
        r"should show|should return|expect|"
        r"ensure .+ (is|are|exists))\b",
        re.IGNORECASE,
    ),
    "References": re.compile(
        r"\b(see|refer to|for more|documentation|section|guide|"
        r"procedure|link|follow|review)\b",
        re.IGNORECASE,
    ),
    "Metadata": re.compile(
        r"\b(version|author|date|updated|prerequisites|requirements|"
        r"applies to|compatible|compatible with)\b",
        re.IGNORECASE,
    ),
}

# ── Ambiguity Resolution Priority ──
# When a sentence matches multiple categories, the spec's decision tree
# (v0.0.2a) defines this priority ordering for the PRIMARY classification.
# Lower index = higher priority for primary assignment.
AMBIGUITY_PRIORITY: List[str] = [
    "Warnings",       # Safety-critical — always takes priority
    "Verifications",  # "verify" preferred over "Actions" per spec
    "Conditions",     # "if/then" preferred over other matches
    "Dependencies",   # "then/after" preferred over "Actions"
    "States",         # Precondition descriptions
    "References",     # Cross-references
    "Metadata",       # Document-level annotations
    "Actions",        # Default catch-all for imperative verbs
]


class PatternExtractor:
    """
    Extract and classify semantic patterns from procedural documentation.

    Scans input text sentence-by-sentence, matching each against regex-based
    recognition markers for 8 semantic categories. Produces frequency counts,
    categorized examples, and a primary classification for each sentence
    based on the ambiguity resolution priority defined in v0.0.2a.

    Attributes:
        patterns: Dictionary mapping category names to compiled regex patterns.
        frequencies: Running count of sentences matching each category.
        examples: Up to max_examples_per_category real-world excerpts per category.
        primary_classifications: Count of sentences where each category is the
            primary (highest-priority) match.
        sentences_analyzed: Total number of non-empty sentences processed.
        max_examples: Maximum examples to retain per category.

    Example:
        >>> extractor = PatternExtractor()
        >>> results = extractor.extract_patterns("Run the build. Verify output.")
        >>> print(results["frequencies"]["Actions"])
        '50.0%'
    """

    def __init__(
        self,
        patterns: Optional[Dict[str, re.Pattern]] = None,
        max_examples: int = 5,
    ):
        """
        Initialize PatternExtractor with category patterns.

        Args:
            patterns: Custom category-to-regex mapping. If None, uses the
                default CATEGORY_PATTERNS from v0.0.2a spec.
            max_examples: Maximum number of example sentences to store per
                category. Defaults to 5 (spec requires minimum 3).
        """
        self.patterns = patterns or CATEGORY_PATTERNS
        self.max_examples = max_examples

        # ── Mutable State (reset per extraction run) ──
        self.frequencies: Dict[str, int] = defaultdict(int)
        self.examples: Dict[str, List[str]] = defaultdict(list)
        self.primary_classifications: Dict[str, int] = defaultdict(int)
        self.sentences_analyzed: int = 0
        self._multi_match_count: int = 0

        logger.debug(
            "PatternExtractor initialized: categories=%d, max_examples=%d",
            len(self.patterns),
            self.max_examples,
        )

    def reset(self) -> None:
        """
        Clear all accumulated state for a fresh extraction run.

        Call this between documents if you want per-document results,
        or leave state accumulated for corpus-wide analysis.
        """
        self.frequencies = defaultdict(int)
        self.examples = defaultdict(list)
        self.primary_classifications = defaultdict(int)
        self.sentences_analyzed = 0
        self._multi_match_count = 0
        logger.debug("PatternExtractor state reset")

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using punctuation and newline boundaries.

        Handles procedural documentation quirks like numbered steps,
        colon-terminated labels, and line-per-instruction formats.

        Args:
            text: Raw procedural documentation text.

        Returns:
            List of non-empty, stripped sentence strings.
        """
        # Split on sentence-ending punctuation or newlines
        # (procedural docs often use one instruction per line)
        raw_splits = re.split(r"[.!?\n]+", text)
        sentences = [s.strip() for s in raw_splits if s.strip()]
        logger.debug("Split text into %d sentences", len(sentences))
        return sentences

    def _classify_sentence(self, sentence: str) -> Dict[str, bool]:
        """
        Check which categories match a single sentence.

        Args:
            sentence: A single sentence or instruction line.

        Returns:
            Dictionary mapping category name to True/False match status.
        """
        matches = {}
        for category, pattern in self.patterns.items():
            matches[category] = bool(pattern.search(sentence))
        return matches

    def _resolve_primary(self, matches: Dict[str, bool]) -> Optional[str]:
        """
        Determine the primary category for a sentence with multiple matches.

        Uses the ambiguity resolution priority from the v0.0.2a spec's
        decision tree. If a sentence matches "Verifications" and "Actions",
        "Verifications" wins because it has higher priority.

        Args:
            matches: Category match results from _classify_sentence.

        Returns:
            The primary category name, or None if no categories matched.
        """
        matched_categories = [cat for cat, matched in matches.items() if matched]
        if not matched_categories:
            return None

        # Use priority ordering to pick the primary
        for priority_cat in AMBIGUITY_PRIORITY:
            if priority_cat in matched_categories:
                return priority_cat

        # Fallback (shouldn't happen if AMBIGUITY_PRIORITY covers all categories)
        return matched_categories[0]

    def extract_patterns(self, text: str) -> Dict[str, Any]:
        """
        Extract semantic patterns from procedural documentation text.

        Splits the input into sentences, classifies each against all 8
        semantic categories, resolves ambiguities, and accumulates results.
        State is additive — call reset() first if you want fresh results.

        Args:
            text: Input procedural documentation (plain text, any length).

        Returns:
            Dictionary containing:
                - frequencies: Category → percentage string (e.g., "35.2%")
                - raw_counts: Category → absolute match count
                - primary_counts: Category → primary classification count
                - examples: Category → list of example sentences
                - total_sentences_analyzed: int
                - multi_match_percentage: Percentage of sentences matching 2+ categories

        Raises:
            ValueError: If text is empty or whitespace-only.
        """
        if not text or not text.strip():
            raise ValueError("Input text is empty or whitespace-only")

        start_time = time.time()
        logger.info("Pattern extraction started: input_length=%d chars", len(text))

        sentences = self._split_sentences(text)
        new_sentences = len(sentences)

        for sentence in sentences:
            self.sentences_analyzed += 1

            # ── Classify against all categories ──
            matches = self._classify_sentence(sentence)
            matched_categories = [cat for cat, hit in matches.items() if hit]

            if len(matched_categories) > 1:
                self._multi_match_count += 1

            # ── Accumulate frequency counts (all matches) ──
            for category in matched_categories:
                self.frequencies[category] += 1
                if len(self.examples[category]) < self.max_examples:
                    self.examples[category].append(sentence)

            # ── Resolve primary classification ──
            primary = self._resolve_primary(matches)
            if primary:
                self.primary_classifications[primary] += 1

            logger.debug(
                "Sentence %d: matches=%s, primary=%s",
                self.sentences_analyzed,
                matched_categories or ["UNCLASSIFIED"],
                primary or "NONE",
            )

        elapsed = time.time() - start_time
        result = self._format_results()

        logger.info(
            "Pattern extraction complete: sentences=%d, categories=%d, time=%.2fs",
            new_sentences,
            len([c for c in self.frequencies if self.frequencies[c] > 0]),
            elapsed,
        )

        return result

    def _format_results(self) -> Dict[str, Any]:
        """
        Format accumulated results into the output dictionary.

        Returns:
            Structured results with frequencies as percentages,
            raw counts, examples, and summary statistics.
        """
        total = self.sentences_analyzed
        if total == 0:
            return {
                "frequencies": {},
                "raw_counts": {},
                "primary_counts": {},
                "examples": {},
                "total_sentences_analyzed": 0,
                "multi_match_percentage": "0.0%",
            }

        # Sort by frequency descending for readability
        sorted_categories = sorted(
            self.frequencies.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        frequencies_pct = {
            cat: f"{(count / total * 100):.1f}%"
            for cat, count in sorted_categories
        }

        raw_counts = {cat: count for cat, count in sorted_categories}

        primary_sorted = sorted(
            self.primary_classifications.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        primary_counts = {cat: count for cat, count in primary_sorted}

        multi_pct = (
            f"{(self._multi_match_count / total * 100):.1f}%"
            if total > 0
            else "0.0%"
        )

        return {
            "frequencies": frequencies_pct,
            "raw_counts": raw_counts,
            "primary_counts": primary_counts,
            "examples": dict(self.examples),
            "total_sentences_analyzed": total,
            "multi_match_percentage": multi_pct,
        }

    def extract_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract patterns from a single file on disk.

        Args:
            file_path: Path to a plain-text procedural document.

        Returns:
            Results dictionary (same format as extract_patterns).

        Raises:
            FileNotFoundError: If file_path does not exist.
            ValueError: If file is empty.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Corpus file not found: {file_path}")

        logger.info("Reading corpus file: %s", path.name)
        text = path.read_text(encoding="utf-8")
        return self.extract_patterns(text)


def run_corpus_analysis(
    corpus_dir: str,
    file_pattern: str = "*.txt",
) -> Dict[str, Any]:
    """
    Analyze all documents in a corpus directory.

    Creates a single PatternExtractor instance and feeds every matching
    file through it, accumulating results across the entire corpus.

    Args:
        corpus_dir: Path to the directory containing corpus text files.
        file_pattern: Glob pattern for matching corpus files. Defaults to "*.txt".

    Returns:
        Dictionary with corpus-wide results plus a "documents_analyzed" count
        and a "document_list" of filenames processed.

    Raises:
        FileNotFoundError: If corpus_dir does not exist.
        ValueError: If no files match file_pattern in corpus_dir.
    """
    corpus_path = Path(corpus_dir)
    if not corpus_path.exists():
        raise FileNotFoundError(f"Corpus directory not found: {corpus_dir}")

    files = sorted(corpus_path.glob(file_pattern))
    if not files:
        raise ValueError(
            f"No files matching '{file_pattern}' found in {corpus_dir}"
        )

    logger.info(
        "Corpus analysis started: directory=%s, files=%d",
        corpus_path.name,
        len(files),
    )

    start_time = time.time()
    extractor = PatternExtractor()

    for file_path in files:
        logger.info("Processing: %s", file_path.name)
        text = file_path.read_text(encoding="utf-8")
        extractor.extract_patterns(text)

    elapsed = time.time() - start_time
    results = extractor._format_results()
    results["documents_analyzed"] = len(files)
    results["document_list"] = [f.name for f in files]

    logger.info(
        "Corpus analysis complete: documents=%d, sentences=%d, time=%.2fs",
        len(files),
        results["total_sentences_analyzed"],
        elapsed,
    )

    return results


# ── CLI Entry Point ──
if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Default corpus path relative to this script's location
    script_dir = Path(__file__).parent
    corpus_dir = script_dir / "corpus"

    if not corpus_dir.exists():
        logger.error("Corpus directory not found: %s", corpus_dir)
        raise SystemExit(1)

    results = run_corpus_analysis(str(corpus_dir))

    # ── Print human-readable summary ──
    print("\n" + "=" * 60)
    print("PATTERN EXTRACTION RESULTS — Haiku Protocol v0.0.2a")
    print("=" * 60)
    print(f"\nDocuments Analyzed: {results['documents_analyzed']}")
    print(f"Total Sentences:   {results['total_sentences_analyzed']}")
    print(f"Multi-Match Rate:  {results['multi_match_percentage']}")

    print("\n--- Frequency Analysis (all matches) ---")
    for cat, pct in results["frequencies"].items():
        raw = results["raw_counts"][cat]
        print(f"  {cat:<20s} {pct:>6s}  ({raw} sentences)")

    print("\n--- Primary Classification Counts ---")
    for cat, count in results["primary_counts"].items():
        pct = f"{(count / results['total_sentences_analyzed'] * 100):.1f}%"
        print(f"  {cat:<20s} {pct:>6s}  ({count} sentences)")

    print("\n--- Examples (up to 5 per category) ---")
    for cat, exs in results["examples"].items():
        print(f"\n  [{cat}]")
        for i, ex in enumerate(exs, 1):
            # Truncate long examples for readability
            display = ex[:100] + "..." if len(ex) > 100 else ex
            print(f"    {i}. {display}")

    # ── Save JSON results for downstream consumption ──
    output_path = script_dir / "pattern_extraction_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    logger.info("Results saved to %s", output_path.name)
    print(f"\nResults saved to: {output_path}")
