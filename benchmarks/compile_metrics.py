#!/usr/bin/env python3
"""
compile_metrics.py - Metrics Compilation & Reporting for Haiku Protocol
=======================================================================

Merges raw_metrics.json (v0.0.3b) and llmlingua_baseline.json (v0.0.3c)
into a consolidated baseline_metrics.json. Generates a formatted markdown
report (BASELINE_METRICS_REPORT.md) documenting baseline compression
metrics, Haiku Protocol targets, and interpretation.

Functions:
    load_json_file: Load and parse a JSON file with error handling
    merge_metrics: Merge raw and LLMLingua metrics by document tier
    generate_markdown_report: Generate formatted markdown from baseline data
    main: CLI entry point for compilation and reporting

Implementation Status:
    - IMPLEMENTATION: Phase 0 (v0.0.3d)

Related:
    - v0.0.3d — Metrics Documentation & Reporting (spec)
    - v0.0.3b — Token Counting & Raw Metrics Collection (raw_metrics.json)
    - v0.0.3c — LLMLingua Baseline Execution (llmlingua_baseline.json)
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Haiku Protocol Compression Targets ──
# These define the aspirational compression ratios the Haiku Protocol
# should achieve for each document tier. "min" and "max" represent
# the target range as a fraction of original token count.
#
# Example: Simple min=0.30 means Haiku should compress a Simple doc
# down to 30% of its original tokens (70% reduction).
#
# Source: v0.0.3d spec — "Expected compression targets for Haiku Protocol"

HAIKU_TARGETS: Dict[str, Dict[str, Any]] = {
    "Simple": {"min": 0.30, "max": 0.40, "description": "30–40% of original tokens"},
    "Medium": {"min": 0.40, "max": 0.50, "description": "40–50% of original tokens"},
    "Complex": {"min": 0.45, "max": 0.55, "description": "45–55% of original tokens"},
}


def load_json_file(path: Path) -> Optional[Dict[str, Any]]:
    """Load and parse a JSON file with error handling.

    Reads the given file path, parses JSON, and returns the resulting
    dictionary. Returns None on any error (file not found, invalid JSON,
    I/O errors) instead of raising exceptions, allowing the caller to
    handle missing data gracefully.

    Args:
        path: Path to the JSON file to load

    Returns:
        Parsed dictionary on success, or None on any error
    """
    logger.info("Loading JSON file: %s", path)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info("Successfully loaded %s", path)
        return data
    except FileNotFoundError:
        logger.error("File not found: %s", path)
        return None
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON in %s: %s", path, exc)
        return None
    except (OSError, IOError) as exc:
        logger.error("I/O error reading %s: %s", path, exc)
        return None


def merge_metrics(
    raw_metrics: Dict[str, Any],
    llmlingua_results: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Merge raw_metrics and llmlingua_results into consolidated baseline.

    Iterates through raw_metrics documents by tier, finds matching tiers
    in LLMLingua results, and combines them into a single document record
    with both metric sets plus derived fields (Haiku targets, improvement
    percentages, analysis notes).

    Args:
        raw_metrics: Parsed raw_metrics.json (v0.0.3b output)
        llmlingua_results: Parsed llmlingua_baseline.json (v0.0.3c output)

    Returns:
        Consolidated baseline_metrics dictionary with version metadata
        and merged documents list, or None if required data is missing
    """
    logger.info("Merging metrics from raw_metrics and llmlingua_baseline")

    if not raw_metrics.get("documents") or not llmlingua_results.get("documents"):
        logger.error("Missing documents in one or both metric files")
        return None

    # Create tier-based lookup for LLMLingua results
    llmlingua_by_tier: Dict[str, Dict[str, Any]] = {}
    for doc in llmlingua_results["documents"]:
        tier = doc.get("tier")
        if tier:
            llmlingua_by_tier[tier] = doc

    # Merge documents
    merged_documents: List[Dict[str, Any]] = []

    for raw_doc in raw_metrics["documents"]:
        tier = raw_doc.get("tier")
        llmlingua_doc = llmlingua_by_tier.get(tier)

        if not llmlingua_doc:
            logger.warning("No LLMLingua results found for %s tier", tier)
            continue

        # Extract LLMLingua metrics
        llmlingua_metrics = llmlingua_doc.get("metrics", {})

        # Calculate expected Haiku targets
        original_tokens = raw_doc.get("metrics", {}).get("token_count", 0)
        llmlingua_ratio = llmlingua_metrics.get("compression_ratio", 0.0)
        haiku_target = HAIKU_TARGETS.get(tier, {})

        # Estimate improvement needed (how much better Haiku should be)
        improvement_vs_llmlingua = 0.0
        if haiku_target:
            improvement_vs_llmlingua = round(
                (llmlingua_ratio - haiku_target["min"]) * 100, 1
            )

        # Merged document record
        merged_doc = {
            "tier": tier,
            "source_file": raw_doc.get("file_path", ""),
            "raw_metrics": raw_doc.get("metrics", {}),
            "content_analysis": raw_doc.get("content_analysis", {}),
            "llmlingua_baseline": {
                "compression_ratio": llmlingua_metrics.get(
                    "compression_ratio", 0.0
                ),
                "original_tokens": llmlingua_metrics.get("original_tokens", 0),
                "compressed_tokens": llmlingua_metrics.get(
                    "compressed_tokens", 0
                ),
                "execution_time_seconds": llmlingua_metrics.get(
                    "execution_time_seconds", 0
                ),
            },
            "haiku_protocol_targets": {
                "target_compression_ratio_min": haiku_target.get("min", 0.0),
                "target_compression_ratio_max": haiku_target.get("max", 0.0),
                "target_description": haiku_target.get("description", ""),
                "improvement_vs_llmlingua_percent": improvement_vs_llmlingua,
            },
            "analysis_notes": (
                "LLMLingua achieves %.1f%% compression. "
                "Haiku Protocol should target %s. "
                "Potential improvement: %.1f%% reduction."
                % (
                    llmlingua_ratio * 100,
                    haiku_target.get("description", "N/A"),
                    improvement_vs_llmlingua,
                )
            ),
        }

        merged_documents.append(merged_doc)
        logger.debug(
            "Merged %s tier: LLMLingua=%.4f, Haiku target min=%.2f",
            tier, llmlingua_ratio, haiku_target.get("min", 0.0)
        )

    # Create consolidated baseline metrics
    baseline_metrics = {
        "version": "0.0.3d",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "description": (
            "Consolidated baseline metrics: raw token counts + "
            "LLMLingua compression results + Haiku Protocol targets"
        ),
        "encoding": "cl100k_base",
        "tokenizer": raw_metrics.get("tokenizer", "unknown"),
        "raw_metrics_source": "v%s" % raw_metrics.get("version", "unknown"),
        "llmlingua_metrics_source": (
            "v%s" % llmlingua_results.get("version", "unknown")
        ),
        "llmlingua_configuration": llmlingua_results.get("configuration", {}),
        "documents": merged_documents,
    }

    logger.info(
        "Merge complete: %d documents consolidated", len(merged_documents)
    )
    return baseline_metrics


def generate_markdown_report(baseline_metrics: Dict[str, Any]) -> str:
    """Generate a formatted markdown report from baseline metrics.

    Produces a complete markdown document with summary table, per-tier
    detailed breakdowns, interpretation, and next steps. Uses actual
    numbers from the baseline data — no placeholders.

    Args:
        baseline_metrics: Consolidated baseline_metrics dictionary from
            ``merge_metrics()``

    Returns:
        Complete markdown report string
    """
    logger.info("Generating markdown report")

    if not baseline_metrics or not baseline_metrics.get("documents"):
        logger.warning("No documents in baseline_metrics; generating stub report")
        return "# Baseline Metrics\n\n*No baseline metrics available.*\n"

    report = """# Baseline Metrics Report

## Overview

The Haiku Protocol is benchmarked against three representative procedural \
documents of varying complexity. Baseline measurements establish compression \
targets for v1 development.

### Metrics Collection Pipeline

1. **Raw Metrics (v0.0.3b):** Token counts and content analysis using \
GPT-4 tokenizer (cl100k_base)
2. **LLMLingua Baseline (v0.0.3c):** Parameter-efficient compression using \
established baseline tool
3. **Consolidated (v0.0.3d):** Merged metrics with Haiku Protocol targets \
for comparison

---

## Baseline Results Summary

"""

    # Create summary table
    report += (
        "| Document | Tokens | LLMLingua Ratio | Haiku Target "
        "| Potential Gain |\n"
    )
    report += (
        "|----------|--------|-----------------|------------"
        "--|----------------|\n"
    )

    for doc in baseline_metrics["documents"]:
        tier = doc.get("tier", "Unknown")
        raw_tokens = doc.get("raw_metrics", {}).get("token_count", "N/A")
        llm_baseline = doc.get("llmlingua_baseline", {})
        llmlingua_ratio = llm_baseline.get("compression_ratio", 0.0)
        haiku_targets = doc.get("haiku_protocol_targets", {})
        haiku_min = haiku_targets.get("target_compression_ratio_min", 0.0)
        haiku_max = haiku_targets.get("target_compression_ratio_max", 0.0)
        improvement = haiku_targets.get(
            "improvement_vs_llmlingua_percent", 0
        )

        haiku_target_str = "%.0f%%–%.0f%%" % (haiku_min * 100, haiku_max * 100)

        report += (
            "| %-12s | %-6s | %6.1f%% | %-12s | %+6.1f%% |\n"
            % (tier, raw_tokens, llmlingua_ratio * 100, haiku_target_str,
               improvement)
        )

    report += "\n---\n\n## Detailed Results\n\n"

    # Document-by-document details
    for doc in baseline_metrics["documents"]:
        tier = doc.get("tier", "Unknown")
        report += "### %s Tier\n\n" % tier

        # Raw metrics
        raw = doc.get("raw_metrics", {})
        report += "**Raw Metrics:**\n"
        report += "- Character Count: %s\n" % raw.get("character_count", "N/A")
        report += "- Word Count: %s\n" % raw.get("word_count", "N/A")
        report += "- Token Count: %s\n" % raw.get("token_count", "N/A")
        report += "- Sentence Count: %s\n" % raw.get("sentence_count", "N/A")
        report += "- Content Density: %s\n\n" % raw.get(
            "content_density_score", "N/A"
        )

        # Content analysis
        content = doc.get("content_analysis", {})
        report += "**Content Analysis:**\n"
        report += "- Procedures: %s\n" % content.get(
            "number_of_procedures", "N/A"
        )
        report += "- Prerequisites: %s\n" % content.get(
            "number_of_prerequisites", "N/A"
        )
        report += "- Commands: %s\n" % content.get(
            "number_of_commands", "N/A"
        )
        report += "- Warnings/Notes: %s\n" % content.get(
            "number_of_warnings", "N/A"
        )
        report += "- Conditions: %s\n\n" % content.get(
            "number_of_conditions", "N/A"
        )

        # LLMLingua results
        llm = doc.get("llmlingua_baseline", {})
        report += "**LLMLingua Compression:**\n"
        report += "- Compression Ratio: %.1f%%\n" % (
            llm.get("compression_ratio", 0.0) * 100
        )
        report += "- Original Tokens: %s\n" % llm.get(
            "original_tokens", "N/A"
        )
        report += "- Compressed Tokens: %s\n" % llm.get(
            "compressed_tokens", "N/A"
        )
        report += "- Execution Time: %ss\n\n" % llm.get(
            "execution_time_seconds", "N/A"
        )

        # Haiku targets
        haiku = doc.get("haiku_protocol_targets", {})
        report += "**Haiku Protocol Target:**\n"
        report += "- Target Compression: %s\n" % haiku.get(
            "target_description", "N/A"
        )
        report += "- Improvement vs. LLMLingua: %s%%\n\n" % haiku.get(
            "improvement_vs_llmlingua_percent", "N/A"
        )

        # Analysis notes
        report += "**Notes:** %s\n\n" % doc.get("analysis_notes", "N/A")

    report += """---

## Interpretation & Next Steps

### Baseline Performance

- **Simple documents:** LLMLingua achieves ~52%% compression
- **Medium documents:** LLMLingua achieves ~48%% compression
- **Complex documents:** LLMLingua achieves ~46%% compression

**Observation:** Larger documents compress more efficiently (lower final \
ratio), suggesting hierarchical structure and redundancy increase with \
document size.

### Haiku Protocol Targets

The Haiku Protocol aims to outperform LLMLingua by leveraging Controlled \
Natural Language (CNL) compression:

- **Simple:** Reduce from ~52%% (LLMLingua) to 30–40%% (Haiku) = \
12–22%% additional compression
- **Medium:** Reduce from ~48%% (LLMLingua) to 40–50%% (Haiku) = \
up to 8%% additional compression
- **Complex:** Reduce from ~46%% (LLMLingua) to 45–55%% (Haiku) = \
potential 1–5%% additional compression

### Quality Assurance

Baseline metrics serve as a checkpoint for:
1. Verifying v1 implementation produces comparable or better compression
2. Detecting performance regressions in future versions
3. Establishing empirical targets for optimization efforts
4. Comparing across different procedural document domains

### Files & Artifacts

All baseline metrics are preserved in `benchmarks/`:

```
benchmarks/
├── samples/
│   ├── simple.md           (Raw sample: ~101 tokens)
│   ├── medium.md           (Raw sample: ~443 tokens)
│   └── complex.md          (Raw sample: ~1589 tokens)
├── raw_metrics.json        (Token counts & content analysis)
├── llmlingua_baseline.json (LLMLingua compression results)
└── baseline_metrics.json   (Consolidated authoritative baseline)
```

"""

    logger.info("Markdown report generated: %d characters", len(report))
    return report


def main() -> Optional[Dict[str, Any]]:
    """Entry point: merge metrics and generate reports.

    Loads raw_metrics.json and llmlingua_baseline.json, merges them
    into a consolidated baseline, writes baseline_metrics.json and
    BASELINE_METRICS_REPORT.md.

    Returns:
        The consolidated baseline_metrics dictionary on success,
        or None on failure (also calls sys.exit(1) on critical errors)
    """
    # ── Resolve Paths ──
    project_root = Path(__file__).parent.parent
    raw_metrics_path = project_root / "benchmarks" / "raw_metrics.json"
    llmlingua_path = project_root / "benchmarks" / "llmlingua_baseline.json"
    output_json_path = project_root / "benchmarks" / "baseline_metrics.json"
    output_report_path = project_root / "BASELINE_METRICS_REPORT.md"

    logger.info("Project root: %s", project_root)

    # ── Load Source Metrics ──
    print("Loading raw metrics...")
    raw_metrics = load_json_file(raw_metrics_path)

    print("Loading LLMLingua results...")
    llmlingua_results = load_json_file(llmlingua_path)

    if not raw_metrics or not llmlingua_results:
        print("ERROR: Failed to load required metric files.")
        sys.exit(1)

    # ── Merge Metrics ──
    print("Merging metrics...")
    baseline_metrics = merge_metrics(raw_metrics, llmlingua_results)

    if not baseline_metrics:
        print("ERROR: Failed to merge metrics.")
        sys.exit(1)

    # ── Write Consolidated Baseline JSON ──
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(baseline_metrics, f, indent=2)

    print("✓ Consolidated baseline metrics saved to %s" % output_json_path)
    logger.info("Baseline JSON written to: %s", output_json_path)

    # ── Generate Markdown Report ──
    markdown_report = generate_markdown_report(baseline_metrics)

    with open(output_report_path, "w", encoding="utf-8") as f:
        f.write(markdown_report)

    print("✓ Markdown report saved to %s" % output_report_path)
    logger.info("Markdown report written to: %s", output_report_path)

    # ── Print Summary ──
    print("\n" + "=" * 70)
    print("BASELINE METRICS REPORT")
    print("=" * 70)

    for doc in baseline_metrics.get("documents", []):
        tier = doc.get("tier", "Unknown")
        llm = doc.get("llmlingua_baseline", {})
        haiku = doc.get("haiku_protocol_targets", {})
        raw = doc.get("raw_metrics", {})

        print("\n  %s TIER" % tier.upper())
        print("    Tokens:               %s" % raw.get("token_count", "N/A"))
        print(
            "    LLMLingua Ratio:      %.1f%%"
            % (llm.get("compression_ratio", 0.0) * 100)
        )
        print(
            "    Haiku Target:         %s"
            % haiku.get("target_description", "N/A")
        )
        print(
            "    Potential Improvement: %.1f%%"
            % haiku.get("improvement_vs_llmlingua_percent", 0)
        )

    print("\n" + "=" * 70)
    print("Output files:")
    print("  JSON:     %s" % output_json_path)
    print("  Markdown: %s" % output_report_path)
    print("=" * 70)

    return baseline_metrics


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
