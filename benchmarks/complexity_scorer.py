#!/usr/bin/env python3
"""
complexity_scorer.py - Automated Complexity Scoring for Benchmark Documents
===========================================================================

Score benchmark sample documents on procedural density and structural
indicators. Used during v0.0.3a (Sample Document Selection & Curation)
to validate that selected documents match their expected complexity tier.

Functions:
    score_document_complexity: Score a document's procedural complexity (0.0-1.0)
    classify_by_score: Map a complexity score to a tier label
    estimate_tokens: Estimate token count using 4-char rule of thumb
    score_all_samples: Score all documents in benchmarks/samples/

Implementation Status:
    - IMPLEMENTATION: Phase 0 (v0.0.3a)

Related:
    - v0.0.3a — Sample Document Selection & Curation
    - v0.0.2a — Pattern taxonomy (procedural markers)
"""

import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def score_document_complexity(text: str) -> Tuple[float, Dict[str, int]]:
    """
    Score document complexity based on procedural markers.

    Analyzes the input text for structural indicators of procedural
    documentation complexity: step markers, command blocks, warnings,
    conditionals, prerequisites, and cross-references. Returns a
    normalized score between 0.0 and 1.0 along with raw indicator counts.

    Args:
        text: Raw document text to analyze

    Returns:
        Tuple of (normalized_score, indicators_dict) where score is
        0.0-1.0 and indicators_dict maps indicator names to counts.

    Raises:
        ValueError: If text is empty or whitespace-only
    """
    if not text or not text.strip():
        raise ValueError("Cannot score empty or whitespace-only document")

    logger.info("Scoring document complexity: %d chars", len(text))

    indicators = {
        "step_markers": len(
            re.findall(r'\b(?:step|part|section)\s+\d+', text, re.I)
        ),
        "command_blocks": len(
            re.findall(r'```[\s\S]*?```', text)
        ),
        "warnings": len(
            re.findall(
                r'\b(?:warning|caution|note|important)\b', text, re.I
            )
        ),
        "conditionals": len(
            re.findall(
                r'\b(?:if|else|when|unless|depending)\b', text, re.I
            )
        ),
        "prerequisites": len(
            re.findall(
                r'\b(?:prerequisite|require|before|first)\b', text, re.I
            )
        ),
        "cross_references": len(
            re.findall(
                r'(?:see also|refer|link to|read|documentation:)',
                text, re.I
            )
        ),
    }

    logger.debug("Raw indicators: %s", indicators)

    # Weighted scoring (weights from v0.0.3a spec)
    score = (
        (indicators["step_markers"] * 0.2)
        + (indicators["command_blocks"] * 0.15)
        + (indicators["warnings"] * 0.15)
        + (indicators["conditionals"] * 0.2)
        + (indicators["prerequisites"] * 0.15)
        + (indicators["cross_references"] * 0.15)
    )

    # Normalize to 0.0-1.0
    score = min(score / 10.0, 1.0)

    logger.info("Complexity score: %.2f", score)
    return score, indicators


def classify_by_score(score: float) -> str:
    """
    Classify complexity tier by normalized score.

    Args:
        score: Normalized complexity score between 0.0 and 1.0

    Returns:
        Tier label: "SIMPLE", "MEDIUM", or "COMPLEX"
    """
    if score < 0.35:
        return "SIMPLE"
    elif score < 0.70:
        return "MEDIUM"
    else:
        return "COMPLEX"


def estimate_tokens(text: str) -> int:
    """
    Estimate token count using 4-char approximation rule.

    This is a rough heuristic (4 characters ≈ 1 token) used for
    preliminary validation. Precise counts via tiktoken are deferred
    to v0.0.3b.

    Args:
        text: Raw document text

    Returns:
        Estimated token count (integer)
    """
    return len(text) // 4


def score_all_samples(samples_dir: Path) -> List[Dict]:
    """
    Score all markdown documents in the samples directory.

    Reads each .md file, computes complexity score and indicators,
    estimates token count, and returns a list of result dictionaries.

    Args:
        samples_dir: Path to directory containing sample .md files

    Returns:
        List of dictionaries, each containing document name, score,
        tier classification, indicators, and token estimate.

    Raises:
        FileNotFoundError: If samples_dir does not exist
    """
    if not samples_dir.exists():
        raise FileNotFoundError(
            "Samples directory not found: %s" % samples_dir
        )

    logger.info("Scoring all samples in: %s", samples_dir)

    results = []
    for md_file in sorted(samples_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        score, indicators = score_document_complexity(text)
        tier = classify_by_score(score)
        token_estimate = estimate_tokens(text)

        result = {
            "document": md_file.stem,
            "file": md_file.name,
            "character_count": len(text),
            "word_count": len(text.split()),
            "token_estimate": token_estimate,
            "complexity_score": round(score, 4),
            "tier_classification": tier,
            "indicators": indicators,
            "scored_at": datetime.now(timezone.utc).isoformat(),
        }
        results.append(result)

        logger.info(
            "Scored %s: score=%.2f, tier=%s, ~%d tokens",
            md_file.name, score, tier, token_estimate
        )

    logger.info("Scoring complete: %d documents processed", len(results))
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

    # ── Resolve Paths ──
    project_root = Path(__file__).parent.parent
    samples_dir = project_root / "benchmarks" / "samples"

    logger.info("Project root: %s", project_root)
    logger.info("Samples directory: %s", samples_dir)

    # ── Score All Samples ──
    results = score_all_samples(samples_dir)

    # ── Output Results ──
    output_path = project_root / "benchmarks" / "complexity_scores.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logger.info("Results saved to: %s", output_path)

    # ── Print Summary ──
    print("\n" + "=" * 60)
    print("COMPLEXITY SCORING RESULTS")
    print("=" * 60)
    for r in results:
        print(
            "\n  %s (%s)" % (r["document"].upper(), r["file"])
        )
        print("    Score:       %.4f" % r["complexity_score"])
        print("    Tier:        %s" % r["tier_classification"])
        print("    Tokens:      ~%d (4-char estimate)" % r["token_estimate"])
        print("    Characters:  %d" % r["character_count"])
        print("    Words:       %d" % r["word_count"])
        print("    Indicators:  %s" % r["indicators"])
    print("\n" + "=" * 60)
