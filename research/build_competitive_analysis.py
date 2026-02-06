"""
build_competitive_analysis.py - Industry Tool Competitive Analysis Builder
==========================================================================

Builds the competitive analysis matrix for v0.0.1b by defining tool
evaluation data, applying the 8-criteria weighted scoring matrix, and
saving the results to research/competitive_analysis.md.

Functions:
    build_evaluations: Assemble the list of ToolEvaluation entries
    generate_competitive_matrix: Format evaluations as a markdown table
    save_competitive_analysis: Write the analysis to markdown
    verify_competitive_analysis: Validate the output markdown file

Related:
    - v0.0.1b -- Industry Tool Analysis specification
    - v0.0.1a -- Academic Research Survey (input: academic_sources.json)
    - v0.0.1c -- CNL & Information Architecture Foundations (consumes this output)
"""

import json
import logging
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional


# Ensure output directories exist before configuring file logging
Path("logs").mkdir(parents=True, exist_ok=True)
Path("research").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/competitive_analysis.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ApproachType(Enum):
    """Compression approach classification for tool evaluation."""

    EXTRACTIVE = "Extractive"
    ABSTRACTIVE = "Abstractive"
    HYBRID = "Hybrid"
    CNL_GUIDED = "CNL-Guided"


@dataclass
class ToolEvaluation:
    """Represents evaluation of a compression tool against the 8-criteria matrix."""

    name: str
    vendor: str
    version: str
    installation_status: str  # "Not tested", "Success", "Failed"

    # Criteria scores (1-5)
    compression_ratio: int
    semantic_preservation: int
    speed_latency: int
    approach_type: ApproachType
    approach_type_score: int  # 1=Single-method, 3=Multi-method, 5=Adaptive hybrid
    language_support: int
    llm_dependency: int
    open_source: int
    documentation_quality: int

    # Additional metadata
    url: str
    license: Optional[str]
    cnl_implemented: bool = False
    notes: str = ""
    tested_date: str = ""

    # Weights for calculation
    weights: Dict[str, float] = field(default_factory=lambda: {
        "compression_ratio": 0.20,
        "semantic_preservation": 0.20,
        "speed_latency": 0.15,
        "approach_type": 0.10,
        "language_support": 0.10,
        "llm_dependency": 0.10,
        "open_source": 0.10,
        "documentation_quality": 0.05,
    })

    def __post_init__(self):
        if not self.tested_date:
            self.tested_date = datetime.now().isoformat()

    def calculate_weighted_score(self) -> float:
        """Calculate weighted overall score (1-5 scale).

        Returns:
            Weighted sum of all 8 criteria scores, rounded to 2 decimal places.
        """
        scores = {
            "compression_ratio": self.compression_ratio,
            "semantic_preservation": self.semantic_preservation,
            "speed_latency": self.speed_latency,
            "approach_type": self.approach_type_score,
            "language_support": self.language_support,
            "llm_dependency": self.llm_dependency,
            "open_source": self.open_source,
            "documentation_quality": self.documentation_quality,
        }
        weighted_sum = sum(scores[k] * self.weights[k] for k in scores)
        return round(weighted_sum, 2)

    def to_markdown_row(self) -> str:
        """Generate a markdown table row for this tool evaluation.

        Returns:
            Pipe-delimited markdown table row string.
        """
        score = self.calculate_weighted_score()
        cnl_mark = "Yes" if self.cnl_implemented else "No"
        return (
            f"| {self.name} | {self.compression_ratio}/5 | "
            f"{self.semantic_preservation}/5 | "
            f"{self.speed_latency}/5 | {self.approach_type.value} | "
            f"{self.language_support}/5 | "
            f"{self.llm_dependency}/5 | {self.open_source}/5 | "
            f"{self.documentation_quality}/5 | "
            f"**{score}** | {cnl_mark} |"
        )


def build_evaluations() -> list[ToolEvaluation]:
    """Assemble the list of evaluated industry tools.

    Returns:
        List of ToolEvaluation entries for prompt compression and
        context optimization tools, scored on the 8-criteria matrix.
    """
    return [
        ToolEvaluation(
            name="LLMLingua",
            vendor="Microsoft Research (Jiang et al.)",
            version="0.2.x",
            installation_status="Success",
            compression_ratio=5,
            semantic_preservation=4,
            speed_latency=4,
            approach_type=ApproachType.HYBRID,
            approach_type_score=5,
            language_support=3,
            llm_dependency=5,
            open_source=5,
            documentation_quality=4,
            url="https://github.com/microsoft/LLMLingua",
            license="MIT",
            cnl_implemented=False,
            notes=(
                "Most mature compression tool. Coarse-to-fine token pruning "
                "using small LM (GPT-2/LLaMA) for importance ranking. Up to "
                "20x compression with minimal performance loss. pip install "
                "llmlingua. Includes LLMLingua, LongLLMLingua, and LLMLingua-2 "
                "variants. Note: 'Microsoft Prompt Compression' referenced in "
                "industry discussions IS this tool -- no separate product exists."
            ),
        ),
        ToolEvaluation(
            name="Selective Context",
            vendor="Yucheng Li et al.",
            version="1.0.x",
            installation_status="Success",
            compression_ratio=3,
            semantic_preservation=4,
            speed_latency=3,
            approach_type=ApproachType.EXTRACTIVE,
            approach_type_score=1,
            language_support=1,
            llm_dependency=5,
            open_source=5,
            documentation_quality=3,
            url="https://github.com/liyucheng09/Selective_Context",
            license="MIT",
            cnl_implemented=False,
            notes=(
                "Self-information-based lexical unit pruning. Computes "
                "self-information via causal LM (GPT-2), merges tokens into "
                "lexical units, eliminates low-information content. 50% context "
                "cost reduction with 0.023 BERTScore drop. pip install "
                "selective-context. Purely statistical -- no semantic "
                "restructuring capability."
            ),
        ),
        ToolEvaluation(
            name="RECOMP",
            vendor="Fangyuan Xu, Weijia Shi, Eunsol Choi",
            version="N/A (research code)",
            installation_status="Not tested",
            compression_ratio=5,
            semantic_preservation=4,
            speed_latency=2,
            approach_type=ApproachType.HYBRID,
            approach_type_score=3,
            language_support=1,
            llm_dependency=3,
            open_source=5,
            documentation_quality=2,
            url="https://github.com/carriex/recomp",
            license="Not specified",
            cnl_implemented=False,
            notes=(
                "Dual extractive + abstractive compressor for RAG contexts. "
                "Extractive compressor selects useful sentences; abstractive "
                "compressor generates summaries. Compression to as low as 6% "
                "of original length (94% reduction). No PyPI package -- GitHub "
                "clone only. Requires task-specific training data. Published "
                "at ICLR 2024."
            ),
        ),
        ToolEvaluation(
            name="gpt-prompt-engineer",
            vendor="Matt Shumer (open-source community)",
            version="N/A",
            installation_status="Not tested",
            compression_ratio=1,
            semantic_preservation=1,
            speed_latency=1,
            approach_type=ApproachType.ABSTRACTIVE,
            approach_type_score=1,
            language_support=1,
            llm_dependency=1,
            open_source=5,
            documentation_quality=3,
            url="https://github.com/mshumer/gpt-prompt-engineer",
            license="MIT",
            cnl_implemented=False,
            notes=(
                "NOT a compression tool. Generates and tests prompt variations "
                "using GPT-4 with ELO rating system. Optimizes prompt quality "
                "and effectiveness, not token count. Included per evaluation "
                "scope but scores low on compression criteria. Requires OpenAI "
                "API key with GPT-4 access."
            ),
        ),
        ToolEvaluation(
            name="compress-gpt",
            vendor="Community (open-source)",
            version="0.1.x",
            installation_status="Success",
            compression_ratio=4,
            semantic_preservation=3,
            speed_latency=2,
            approach_type=ApproachType.ABSTRACTIVE,
            approach_type_score=1,
            language_support=1,
            llm_dependency=1,
            open_source=5,
            documentation_quality=2,
            url="https://github.com/yasyf/compress-gpt",
            license="MIT",
            cnl_implemented=False,
            notes=(
                "Semantic compression via GPT-4 API. Creates self-extracting "
                "prompts by decomposing content into static and dynamic chunks. "
                "~70% token savings on LangChain tool-based prompts. "
                "pip install compress-gpt. Requires GPT-4 for quality output; "
                "results are non-deterministic. Replaces 'Microsoft Prompt "
                "Compression' in evaluation (which IS LLMLingua)."
            ),
        ),
    ]


def generate_competitive_matrix(evaluations: list[ToolEvaluation]) -> str:
    """Generate markdown-formatted competitive analysis matrix.

    Args:
        evaluations: List of tool evaluations to format.

    Returns:
        Markdown string with header row, separator, and data rows
        sorted by weighted score descending.
    """
    header = (
        "| Tool | Compression | Semantics | Speed | Approach | "
        "Languages | LLM Dep | Open Src | Docs | Score | CNL |\n"
        "|------|------|------|------|------|------|------|------|------|------|------|"
    )
    rows = [e.to_markdown_row() for e in sorted(
        evaluations,
        key=lambda e: e.calculate_weighted_score(),
        reverse=True
    )]
    return header + "\n" + "\n".join(rows)


def save_competitive_analysis(
    evaluations: list[ToolEvaluation],
    filepath: str = "research/competitive_analysis.md"
) -> None:
    """Save competitive analysis to markdown file.

    Args:
        evaluations: List of tool evaluations to save.
        filepath: Output path for the markdown file.
    """
    eval_dicts = []
    for e in evaluations:
        d = asdict(e)
        d["approach_type"] = e.approach_type.value
        d["weighted_score"] = e.calculate_weighted_score()
        eval_dicts.append(d)

    content = (
        "# Competitive Analysis: Prompt Compression Tools\n\n"
        f"**Generated:** {datetime.now().isoformat()}\n"
        "**Version:** v0.0.1b\n"
        f"**Tools Evaluated:** {len(evaluations)}\n\n"
        "## Summary Matrix\n\n"
        f"{generate_competitive_matrix(evaluations)}\n\n"
        "**Legend:**\n"
        "- Score = Weighted sum across all 8 criteria "
        "(Compression 20%, Semantics 20%, Speed 15%, Approach 10%, "
        "Languages 10%, LLM Dep 10%, Open Src 10%, Docs 5%)\n"
        "- CNL = Whether tool uses Controlled Natural Language for "
        "compression logic\n"
        "- Score interpretation: 1-2 = Poor, 3-3.5 = Acceptable, "
        "4-5 = Excellent\n\n"
        "## Tool Details\n\n"
    )

    for e in sorted(evaluations,
                     key=lambda e: e.calculate_weighted_score(),
                     reverse=True):
        content += (
            f"### {e.name}\n\n"
            f"- **Vendor:** {e.vendor}\n"
            f"- **Version:** {e.version}\n"
            f"- **Installation:** `{e.installation_status}`\n"
            f"- **License:** {e.license}\n"
            f"- **URL:** {e.url}\n"
            f"- **CNL Implemented:** {'Yes' if e.cnl_implemented else 'No'}\n"
            f"- **Weighted Score:** {e.calculate_weighted_score()}\n"
            f"- **Notes:** {e.notes}\n\n"
        )

    content += (
        "## Gap Analysis\n\n"
        f"Based on evaluation of {len(evaluations)} industry tools, "
        "Haiku Protocol can differentiate by:\n\n"
        "1. **CNL-Guided Compression (Unique):** None of the evaluated "
        "tools implement Controlled Natural Language for compression. All "
        "rely on statistical token pruning (LLMLingua, Selective Context), "
        "neural abstractive rewriting (compress-gpt), or hybrid "
        "extraction + abstraction (RECOMP). Haiku Protocol's "
        "grammar-driven approach is genuinely novel.\n\n"
        "2. **Deterministic Semantic Preservation:** Existing tools use "
        "probabilistic methods -- compression quality varies across runs "
        "and domains. A CNL grammar provides deterministic, auditable "
        "compression with guaranteed semantic fidelity.\n\n"
        "3. **Query-Independent Compression:** LongLLMLingua requires the "
        "downstream query at compression time. Haiku Protocol's CNL "
        "output preserves all semantic content regardless of future use, "
        "making it suitable for stored knowledge bases.\n\n"
        "4. **Interpretable Output:** Statistical compression (LLMLingua, "
        "Selective Context) produces truncated text that is difficult to "
        "audit. Abstractive compression (compress-gpt) produces "
        "non-deterministic rewrites. CNL output follows a formal grammar "
        "that humans and machines can validate.\n\n"
        "5. **No LLM Dependency for Compression Logic:** Tools like "
        "compress-gpt and gpt-prompt-engineer require GPT-4 API access. "
        "Haiku Protocol's grammar rules are defined statically -- the LLM "
        "assists extraction but the compression logic itself is "
        "model-agnostic.\n\n"
        "## Key Observations\n\n"
        "- **Microsoft Prompt Compression IS LLMLingua.** The Microsoft "
        "offering referenced in industry discussions is the LLMLingua "
        "project itself (github.com/microsoft/LLMLingua). No separate "
        "enterprise product exists.\n"
        "- **gpt-prompt-engineer is NOT a compression tool.** It generates "
        "and tests prompt variations using GPT-4, optimizing prompt "
        "quality rather than reducing token count. Included for "
        "completeness per evaluation scope.\n"
        "- **No tool uses CNL.** This is the central finding -- the gap "
        "that Haiku Protocol is designed to fill.\n\n"
        "## Raw Evaluation Data\n\n"
        "```json\n"
        f"{json.dumps(eval_dicts, indent=2, default=str)}\n"
        "```\n"
    )

    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Saved competitive analysis to {filepath}")


def verify_competitive_analysis(
    filepath: str = "research/competitive_analysis.md"
) -> bool:
    """Validate competitive analysis markdown structure and content.

    Args:
        filepath: Path to the competitive analysis markdown file.

    Returns:
        True if the file passes all validation checks.
    """
    required_sections = [
        "Competitive Analysis",
        "Summary Matrix",
        "Gap Analysis"
    ]

    try:
        with open(filepath, 'r') as f:
            content = f.read()

        for section in required_sections:
            if section.lower() not in content.lower():
                print(f"Missing section: {section}")
                return False

        table_match = re.search(r'\|.*\|.*\|', content)
        if not table_match:
            print("No markdown table found")
            return False

        table_lines = [
            line for line in content.split('\n')
            if line.strip().startswith('|') and '---' not in line
        ]
        tool_count = len(table_lines) - 1  # Subtract header row

        if tool_count < 3:
            print(f"Found {tool_count} tools, minimum 3 required")
            return False

        print(f"Found {tool_count} tools in competitive matrix")
        print("All required sections present")
        print("Markdown table validated")
        return True

    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return False


if __name__ == "__main__":
    logger.info("Starting industry tool analysis v0.0.1b")
    logger.info("Evaluation scope: 5 public tools, 8 criteria matrix")
    logger.info("Timeline: 15-20 minutes for testing and documentation")

    evaluations = build_evaluations()
    logger.info("Built %s tool evaluation entries", len(evaluations))

    for evaluation in evaluations:
        logger.info(
            "Tool: %s (%s) - weighted_score=%s, installation=%s",
            evaluation.name,
            evaluation.vendor,
            evaluation.calculate_weighted_score(),
            evaluation.installation_status
        )

    save_competitive_analysis(evaluations)

    print("\n--- Verification ---")
    success = verify_competitive_analysis()

    if success:
        logger.info("Competitive analysis verification passed")
    else:
        logger.error("Competitive analysis verification failed")

    sys.exit(0 if success else 1)
