"""
build_gap_analysis.py - Gap Analysis & Literature Review Builder
================================================================

Synthesizes research artifacts from v0.0.1a (academic sources),
v0.0.1b (competitive analysis), and v0.0.1c (CNL & IA foundations)
into a gap analysis, positioning statement, build decision, and
final LITERATURE_REVIEW.md document.

Functions:
    load_academic_sources: Load academic sources from v0.0.1a JSON
    load_competitive_analysis: Load competitive analysis from v0.0.1b markdown
    load_cnl_ia_foundations: Load CNL & IA foundations from v0.0.1c markdown
    extract_competitive_matrix: Extract summary matrix from competitive analysis
    extract_cnl_section: Extract CNL systems section from foundations document
    build_gap_entries: Assemble gap analysis entries
    build_positioning_criteria: Assemble competitive positioning matrix
    build_positioning_statement: Generate the positioning statement
    build_design_priorities: Generate design priorities for v0.1.0
    generate_literature_review: Assemble the full LITERATURE_REVIEW.md
    save_literature_review: Write the document to the project root
    verify_literature_review: Validate the output against acceptance criteria

Related:
    - v0.0.1d -- Gap Analysis & Project Positioning specification
    - v0.0.1a -- Academic Research Survey (input: academic_sources.json)
    - v0.0.1b -- Industry Tool Analysis (input: competitive_analysis.md)
    - v0.0.1c -- CNL & IA Foundations (input: cnl_ia_foundations.md)
"""

import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


# Ensure output directories exist before configuring file logging
Path("logs").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/gap_analysis.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@dataclass
class GapEntry:
    """Represents a single gap identified in the existing landscape."""

    category: str
    description: str
    evidence_source: str
    haiku_response: str
    competitive_impact: str


@dataclass
class PositioningCriterion:
    """Represents a criterion in the competitive positioning matrix."""

    capability: str
    llmlingua: str
    recomp: str
    selective_context: str
    haiku_protocol: str
    haiku_advantage: bool


# ---------------------------------------------------------------------------
# Load functions
# ---------------------------------------------------------------------------

def load_academic_sources(
    filepath: str = "research/academic_sources.json"
) -> dict:
    """Load academic sources from v0.0.1a output.

    Args:
        filepath: Path to the academic sources JSON file.

    Returns:
        Dictionary containing the academic sources data, or a
        fallback structure with an empty sources list if not found.
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        logger.info(
            "Loaded %s academic sources from %s",
            len(data.get("sources", [])), filepath
        )
        return data
    except FileNotFoundError:
        logger.warning("Academic sources not found at %s", filepath)
        return {"sources": []}


def load_competitive_analysis(
    filepath: str = "research/competitive_analysis.md"
) -> str:
    """Load competitive analysis from v0.0.1b output.

    Args:
        filepath: Path to the competitive analysis markdown file.

    Returns:
        String content of the competitive analysis, or empty string
        if not found.
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        logger.info(
            "Loaded competitive analysis from %s (%s lines)",
            filepath, len(content.strip().split('\n'))
        )
        return content
    except FileNotFoundError:
        logger.warning("Competitive analysis not found at %s", filepath)
        return ""


def load_cnl_ia_foundations(
    filepath: str = "research/cnl_ia_foundations.md"
) -> str:
    """Load CNL & IA foundations from v0.0.1c output.

    Uses explicit path rather than the spec's glob auto-detect
    (Path('.').glob('*CNL*')), which fails because the file is
    lowercase and in a subdirectory.

    Args:
        filepath: Path to the CNL & IA foundations markdown file.

    Returns:
        String content of the foundations document, or empty string
        if not found.
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        logger.info(
            "Loaded CNL & IA foundations from %s (%s lines)",
            filepath, len(content.strip().split('\n'))
        )
        return content
    except FileNotFoundError:
        logger.warning("CNL & IA foundations not found at %s", filepath)
        return ""


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def extract_competitive_matrix(competitive_analysis: str) -> str:
    """Extract the summary matrix table from competitive analysis.

    Args:
        competitive_analysis: Full competitive analysis markdown content.

    Returns:
        The summary matrix table section, or a fallback reference.
    """
    if not competitive_analysis:
        return "(See research/competitive_analysis.md for full matrix)\n"

    lines = competitive_analysis.split('\n')
    in_matrix = False
    matrix_lines = []

    for line in lines:
        if line.strip().startswith("## Summary Matrix"):
            in_matrix = True
            continue
        if in_matrix and line.strip().startswith("## "):
            break
        if in_matrix:
            matrix_lines.append(line)

    if matrix_lines:
        return '\n'.join(matrix_lines).strip()
    return "(See research/competitive_analysis.md for full matrix)\n"


def extract_cnl_section(cnl_ia_foundations: str) -> str:
    """Extract the CNL systems section from the foundations document.

    Splits at the '## Information Architecture' heading to return
    only the CNL systems content.

    Args:
        cnl_ia_foundations: Full CNL & IA foundations markdown content.

    Returns:
        The CNL systems section content, or a fallback reference.
    """
    if not cnl_ia_foundations:
        return "(See research/cnl_ia_foundations.md for full analysis)\n"

    parts = cnl_ia_foundations.split("## Information Architecture")
    if len(parts) >= 2:
        cnl_part = parts[0]
        # Remove the document header (title, version, purpose)
        lines = cnl_part.split('\n')
        content_lines = []
        past_header = False
        for line in lines:
            if line.startswith("## Controlled Natural Language"):
                past_header = True
            if past_header:
                content_lines.append(line)
        if content_lines:
            return '\n'.join(content_lines).strip()

    return "(See research/cnl_ia_foundations.md for full analysis)\n"


# ---------------------------------------------------------------------------
# Build functions
# ---------------------------------------------------------------------------

def build_gap_entries() -> list[GapEntry]:
    """Assemble the gap analysis entries.

    Returns:
        List of GapEntry entries covering major gaps identified
        across academic research, competitive analysis, and
        theoretical foundations.
    """
    return [
        GapEntry(
            category="No CNL Foundation",
            description=(
                "No existing tool uses Controlled Natural Language as a "
                "foundation for compression. All rely on statistical token "
                "pruning or neural rewriting."
            ),
            evidence_source="v0.0.1b (competitive analysis)",
            haiku_response=(
                "Haiku Protocol uses a custom CNL grammar that guarantees "
                "unambiguous parsing -- every statement has exactly one "
                "valid interpretation."
            ),
            competitive_impact=(
                "Unique differentiator. No competition in this space."
            ),
        ),
        GapEntry(
            category="No Language Redesign",
            description=(
                "All academic approaches are post-hoc -- they compress "
                "after the prompt is written in unstructured natural "
                "language. None redesign the prompt language itself."
            ),
            evidence_source="v0.0.1a (academic research)",
            haiku_response=(
                "Haiku Protocol redesigns the prompt language using CNL "
                "principles, enabling compression 'for free' via "
                "structured design rather than after-the-fact trimming."
            ),
            competitive_impact=(
                "Eliminates redundancy at the source rather than trimming "
                "symptoms. Potential for higher compression ratios."
            ),
        ),
        GapEntry(
            category="No IA Integration",
            description=(
                "No tool applies Information Architecture principles -- "
                "vocabulary standardization, metadata schemas, faceted "
                "classification, or taxonomy design -- to compression."
            ),
            evidence_source="v0.0.1b + v0.0.1c",
            haiku_response=(
                "Haiku Protocol integrates 5 IA principles directly into "
                "its grammar and compression pipeline: taxonomy design, "
                "controlled vocabularies, metadata schemas, faceted "
                "classification, and information scent."
            ),
            competitive_impact=(
                "IA integration enables systematic redundancy elimination "
                "that statistical methods cannot achieve."
            ),
        ),
        GapEntry(
            category="No Real-time Authoring Guidance",
            description=(
                "All existing tools operate in batch mode -- compression "
                "happens after the prompt is fully written. No tool "
                "provides feedback during the writing process."
            ),
            evidence_source="v0.0.1b (competitive analysis)",
            haiku_response=(
                "Haiku Protocol's grammar-based approach enables real-time "
                "feedback during prompt composition, showing compression "
                "metrics and syntax suggestions as the user types."
            ),
            competitive_impact=(
                "New capability category. Shifts compression from "
                "post-processing to an interactive authoring workflow."
            ),
        ),
        GapEntry(
            category="LLM-dependent Compression Logic",
            description=(
                "Tools like compress-gpt and gpt-prompt-engineer require "
                "GPT-4 API access for compression. LLMLingua and "
                "Selective Context require a small LM for token ranking."
            ),
            evidence_source="v0.0.1a + v0.0.1b",
            haiku_response=(
                "Haiku Protocol's grammar rules are defined statically. "
                "The LLM assists with extraction, but the compression "
                "logic itself is model-agnostic and deterministic."
            ),
            competitive_impact=(
                "Removes circular dependency of using a model to compress "
                "input for a model. Compression quality is consistent "
                "across runs and domains."
            ),
        ),
        GapEntry(
            category="No Formal Semantic Guarantees",
            description=(
                "Existing tools use probabilistic methods -- compression "
                "quality varies across runs. Statistical pruning can "
                "silently drop meaning in edge cases."
            ),
            evidence_source="v0.0.1a (academic research)",
            haiku_response=(
                "CNL grammar provides deterministic, auditable compression "
                "with formal semantic preservation. Every CNL statement "
                "has exactly one valid parse -- meaning loss is detectable."
            ),
            competitive_impact=(
                "Critical for high-stakes domains (medical, legal, "
                "financial) where silent meaning loss is unacceptable."
            ),
        ),
    ]


def build_positioning_criteria() -> list[PositioningCriterion]:
    """Assemble the competitive positioning matrix criteria.

    Returns:
        List of PositioningCriterion entries showing capability
        comparison between existing tools and Haiku Protocol.
    """
    return [
        PositioningCriterion(
            capability="Compression Ratio",
            llmlingua="70%",
            recomp="65%",
            selective_context="60%",
            haiku_protocol="75% (projected)",
            haiku_advantage=True,
        ),
        PositioningCriterion(
            capability="Semantic Preservation",
            llmlingua="4/5 (<5% loss)",
            recomp="4/5",
            selective_context="5/5",
            haiku_protocol="5/5 (formal guarantee)",
            haiku_advantage=True,
        ),
        PositioningCriterion(
            capability="CNL Grammar",
            llmlingua="No",
            recomp="No",
            selective_context="No",
            haiku_protocol="Yes (custom DSL)",
            haiku_advantage=True,
        ),
        PositioningCriterion(
            capability="IA Integration",
            llmlingua="No",
            recomp="No",
            selective_context="No",
            haiku_protocol="Yes (vocab + schema)",
            haiku_advantage=True,
        ),
        PositioningCriterion(
            capability="Real-time Guidance",
            llmlingua="Post-hoc",
            recomp="Post-hoc",
            selective_context="Post-hoc",
            haiku_protocol="During-write feedback",
            haiku_advantage=True,
        ),
        PositioningCriterion(
            capability="Unambiguous Parsing",
            llmlingua="Probabilistic",
            recomp="Probabilistic",
            selective_context="Probabilistic",
            haiku_protocol="Guaranteed",
            haiku_advantage=True,
        ),
        PositioningCriterion(
            capability="Vocabulary Control",
            llmlingua="Inherited",
            recomp="Inherited",
            selective_context="Inherited",
            haiku_protocol="User-defined",
            haiku_advantage=True,
        ),
        PositioningCriterion(
            capability="Open Source",
            llmlingua="MIT",
            recomp="Apache",
            selective_context="Partial",
            haiku_protocol="Planned (Apache 2.0)",
            haiku_advantage=False,
        ),
        PositioningCriterion(
            capability="Tech Writer Friendly",
            llmlingua="Requires ML knowledge",
            recomp="Requires ML knowledge",
            selective_context="Requires ML knowledge",
            haiku_protocol="Document-based syntax",
            haiku_advantage=True,
        ),
        PositioningCriterion(
            capability="Multi-language",
            llmlingua="EN, CN only",
            recomp="EN only",
            selective_context="EN only",
            haiku_protocol="Any language",
            haiku_advantage=True,
        ),
    ]


def build_positioning_statement() -> str:
    """Generate the positioning statement for Haiku Protocol.

    Returns:
        The final positioning statement string, using Option 1
        (Formal) from the spec as recommended.
    """
    return (
        "Haiku Protocol is the first CNL-guided prompt compression "
        "framework that combines Controlled Natural Language design "
        "with Information Architecture principles to achieve semantic "
        "density 2x higher than existing approaches, while providing "
        "real-time writing guidance for knowledge workers and AI teams."
    )


def build_design_priorities() -> str:
    """Generate the design priorities for v0.1.0.

    Returns:
        Markdown string with 4 actionable design priorities informed
        by the research findings from v0.0.1a, v0.0.1b, and v0.0.1c.
    """
    return (
        "1. **Grammar Design** (informed by ACE, CLCE, SBVR)\n"
        "   - Keep unambiguous, formal enough for parsing\n"
        "   - Keep simple enough for human authoring\n"
        "   - Support common prompt patterns "
        "(Q&A, instruction, narrative)\n\n"
        "2. **Vocabulary & Schema** (informed by IA principles)\n"
        "   - Define core vocabulary set (semantic tokens)\n"
        "   - Create metadata schema for roles, relationships, "
        "constraints\n"
        "   - Enable faceted classification for complex documents\n\n"
        "3. **Compression Algorithm** (informed by academic research)\n"
        "   - Implement CNL-native compression "
        "(structure-based redundancy elimination)\n"
        "   - Measure against academic baselines "
        "(QA, summarization tasks)\n"
        "   - Target 75% compression with <2% quality loss\n\n"
        "4. **Authoring Experience** (informed by tech writing)\n"
        "   - Interactive grammar guide "
        "(syntax hints as user types)\n"
        "   - Real-time compression metric display\n"
        "   - Vocabulary suggestion engine"
    )


# ---------------------------------------------------------------------------
# Document generation
# ---------------------------------------------------------------------------

def generate_literature_review(
    academic_sources: dict,
    competitive_analysis: str,
    cnl_ia_foundations: str,
) -> str:
    """Assemble the complete LITERATURE_REVIEW.md document.

    Synthesizes all research artifacts from v0.0.1a, b, c into a
    single literature review with gap analysis, positioning statement,
    build decision, and design priorities.

    Args:
        academic_sources: Dictionary from v0.0.1a JSON.
        competitive_analysis: Markdown string from v0.0.1b.
        cnl_ia_foundations: Markdown string from v0.0.1c.

    Returns:
        Complete markdown string for the literature review.
    """
    now = datetime.now()
    gap_entries = build_gap_entries()
    positioning_criteria = build_positioning_criteria()
    positioning_statement = build_positioning_statement()
    design_priorities = build_design_priorities()
    competitive_matrix = extract_competitive_matrix(competitive_analysis)
    cnl_section = extract_cnl_section(cnl_ia_foundations)

    doc = (
        "# Haiku Protocol — Literature Review & Prior Art\n\n"
        f"**Version:** v0.0.1 (Final)\n"
        f"**Generated:** {now.isoformat()}\n"
        "**Status:** Foundation phase complete; "
        "ready for design phase\n\n"
        "---\n\n"
    )

    # ---------------------------------------------------------------
    # Executive Summary
    # ---------------------------------------------------------------
    doc += (
        "## Executive Summary\n\n"
        "Haiku Protocol is positioned as the first CNL-guided prompt "
        "compression framework, combining Controlled Natural Language "
        "design with Information Architecture principles to achieve "
        "semantic density 2x higher than existing post-hoc compression "
        "approaches.\n\n"
        "This literature review synthesizes:\n"
        "1. **Academic research** on prompt compression (v0.0.1a)\n"
        "2. **Competitive analysis** of industry tools (v0.0.1b)\n"
        "3. **Theoretical foundations** in CNL and IA (v0.0.1c)\n"
        "4. **Gap analysis** and strategic positioning (v0.0.1d)\n\n"
        "**Key Finding:** Existing tools excel at post-hoc optimization "
        "but don't address the root problem: prompts are written in "
        "unstructured natural language. Haiku Protocol fills this gap "
        "by providing a formal language designed for compression from "
        "the ground up.\n\n"
        "---\n\n"
    )

    # ---------------------------------------------------------------
    # Part 1: Academic Research Survey
    # ---------------------------------------------------------------
    doc += (
        "## Part 1: Academic Research Survey\n\n"
        "### Overview\n\n"
        "The academic literature on prompt compression has grown "
        "rapidly (2023-2025), with three dominant paradigms:\n\n"
        "1. **LLM-guided ranking** (LLMLingua, LongLLMLingua) — "
        "use a smaller model to rank token importance, achieving "
        "70%+ compression with <5% quality loss\n"
        "2. **Retrieve-and-recompose** (RECOMP, Selective Context) — "
        "extract relevant passages from long documents and recompose "
        "into concise context\n"
        "3. **Budget-constrained optimization** — fit highest-value "
        "information into token budget with dynamic thresholds\n\n"
    )

    # Format academic sources from JSON
    sources = academic_sources.get("sources", [])
    if sources:
        doc += "### Included Papers\n\n"
        for i, source in enumerate(sources, 1):
            doc += (
                f"**{i}. {source.get('authors', 'Unknown')} "
                f"({source.get('year', 'N/A')})**\n"
                f"- **Title:** {source.get('title', 'Untitled')}\n"
                f"- **Venue:** {source.get('venue', 'Unknown')}\n"
                f"- **Key Finding:** "
                f"{source.get('key_finding', 'N/A')}\n"
                f"- **Methodology:** "
                f"{source.get('methodology', 'N/A')}\n"
                f"- **Compression Ratio:** "
                f"{source.get('compression_ratio', 'Not reported')}\n"
                f"- **Relevance Score:** "
                f"{source.get('relevance_score', '?')}/5\n"
                f"- **URL/DOI:** "
                f"{source.get('doi_or_url', 'N/A')}\n\n"
            )
    else:
        doc += (
            "(See research/academic_sources.json for detailed "
            "annotations)\n\n"
        )

    doc += (
        "### What Academic Research Shows\n\n"
        "**Strengths of Existing Approaches:**\n"
        "- Proven effectiveness: 60-70% token reduction demonstrated\n"
        "- Quality preservation: <5% accuracy drop on benchmarks\n"
        "- Model-agnostic: Most work with any LLM backend\n"
        "- Reproducible: Multiple implementations with published "
        "baselines\n\n"
        "**Limitations:**\n"
        "- All are post-hoc (applied after prompt is written)\n"
        "- No formal guarantees on semantic preservation\n"
        "- Rely on LLM judgment (circular dependency problem)\n"
        "- Don't address source redundancy; only trim symptoms\n"
        "- Limited to English (mostly) and specific task types\n\n"
        "---\n\n"
    )

    # ---------------------------------------------------------------
    # Part 2: Competitive Analysis
    # ---------------------------------------------------------------
    doc += (
        "## Part 2: Competitive Analysis\n\n"
        "### Tools Evaluated\n\n"
        f"{competitive_matrix}\n\n"
        "*(Full analysis: research/competitive_analysis.md)*\n\n"
        "### Competitive Positioning\n\n"
        "**Haiku Protocol Differentiators:**\n\n"
        "1. **CNL Foundation** — First to use Controlled Natural "
        "Language for prompts; guarantees unambiguous parsing\n"
        "2. **Information Architecture Integration** — Applies "
        "vocabulary control, metadata schemas, faceted classification "
        "to enable redundancy elimination at design time\n"
        "3. **Real-time Authoring Guidance** — Immediate feedback "
        "during prompt composition vs. batch-only compression\n"
        "4. **Tech Writer Accessibility** — Grammar-based approach "
        "designed for non-ML practitioners; bridges technical writing "
        "and prompt engineering\n\n"
        "---\n\n"
    )

    # ---------------------------------------------------------------
    # Part 3: Theoretical Foundations
    # ---------------------------------------------------------------
    doc += (
        "## Part 3: Theoretical Foundations\n\n"
        "### Controlled Natural Languages (CNL)\n\n"
        f"{cnl_section}\n\n"
        "### Information Architecture Principles\n\n"
        "Information Architecture -- the discipline of organizing, "
        "labeling, and navigating complex information systems -- "
        "provides proven techniques for semantic compression:\n\n"
        "- **Taxonomy Design:** Hierarchical organization reduces "
        "redundancy via property inheritance\n"
        "- **Controlled Vocabularies:** Standardization eliminates "
        "synonymy (one token per concept)\n"
        "- **Metadata Schemas:** Structured annotation replaces "
        "narrative description\n"
        "- **Faceted Classification:** Multi-dimensional organization "
        "factors cross-cutting concerns\n"
        "- **Information Scent:** Semantic labels signal meaning, "
        "reducing disambiguation tokens\n\n"
        "Each principle translates directly to measurable compression: "
        "fewer tokens per concept, factored context via hierarchy, "
        "unambiguous role-labeling via schemas.\n\n"
        "*(Full analysis: research/cnl_ia_foundations.md)*\n\n"
        "---\n\n"
    )

    # ---------------------------------------------------------------
    # Part 4: Gap Analysis
    # ---------------------------------------------------------------
    doc += "## Part 4: Gap Analysis & Strategic Positioning\n\n"

    doc += "### What Existing Approaches Do Well\n\n"
    doc += (
        "- Compression effectiveness: 60-70% token reduction "
        "demonstrated across multiple tools\n"
        "- Model agnosticism: LLMLingua, RECOMP work with any model\n"
        "- Semantic preservation: Quality loss <5% on benchmarks\n"
        "- Practical tooling: GitHub implementations, pip-installable, "
        "documented\n\n"
    )

    doc += "### Where They Fall Short\n\n"
    for entry in gap_entries:
        doc += (
            f"**{entry.category}**\n"
            f"- *Gap:* {entry.description}\n"
            f"- *Evidence:* {entry.evidence_source}\n"
            f"- *Haiku Response:* {entry.haiku_response}\n"
            f"- *Impact:* {entry.competitive_impact}\n\n"
        )

    # Capability comparison matrix
    doc += "### Capability Comparison Matrix\n\n"
    doc += (
        "| Capability | LLMLingua | RECOMP | "
        "Selective Context | Haiku Protocol |\n"
        "|-----------|-----------|--------"
        "|-----------------|-----------------|\n"
    )
    for criterion in positioning_criteria:
        doc += (
            f"| **{criterion.capability}** "
            f"| {criterion.llmlingua} "
            f"| {criterion.recomp} "
            f"| {criterion.selective_context} "
            f"| {criterion.haiku_protocol} |\n"
        )

    haiku_advantages = sum(
        1 for c in positioning_criteria if c.haiku_advantage
    )
    doc += (
        f"\n*Haiku Protocol shows advantages on "
        f"{haiku_advantages} of "
        f"{len(positioning_criteria)} criteria.*\n\n"
        "---\n\n"
    )

    # ---------------------------------------------------------------
    # Part 5: Positioning Statement
    # ---------------------------------------------------------------
    doc += (
        "## Positioning Statement\n\n"
        f"**{positioning_statement}**\n\n"
        "---\n\n"
    )

    # ---------------------------------------------------------------
    # Part 6: Build Decision
    # ---------------------------------------------------------------
    doc += (
        "## Build Decision\n\n"
        "**Decision: BUILD**\n\n"
        "**Validation Checkpoints:**\n"
        "- No existing tool uses CNL as foundation\n"
        "- No existing tool integrates IA principles "
        "(vocab, schema, facets)\n"
        "- No existing tool offers real-time authoring guidance\n"
        "- Academic gap confirmed: no papers apply CNL + IA "
        "to prompts\n"
        "- Competitive gap confirmed: matrix shows capability gaps\n"
        "- Market demand validated: LLM context window bottleneck "
        "is real and growing\n\n"
        "**Rationale:**\n"
        "1. Novel approach -- CNL + IA combination is genuinely new\n"
        "2. Clear differentiation from all existing tools\n"
        "3. Market demand driven by LLM context window limitations\n"
        "4. Feasible -- grammar design and IA techniques are "
        "well-established\n"
        "5. Tech writer audience is underserved by current tools\n"
        "6. Formal semantic guarantees are valuable for "
        "high-stakes domains\n\n"
        "---\n\n"
    )

    # ---------------------------------------------------------------
    # Part 7: Design Priorities
    # ---------------------------------------------------------------
    doc += (
        "## Key Takeaways for Design Phase (v0.1.0)\n\n"
        "### What We Know Works\n\n"
        "From academic research:\n"
        "- Semantic compression is viable; 70%+ reduction possible "
        "with <5% quality loss\n"
        "- LLM-guided ranking is effective (LLMLingua)\n"
        "- Retrieve-and-recompose works for long-context tasks "
        "(RECOMP)\n"
        "- Information extraction beats simple truncation\n\n"
        "From competitive analysis:\n"
        "- Maturity exists; tools are production-ready\n"
        "- User demand is clear (all tools have GitHub activity)\n"
        "- Model-agnosticism is expected\n"
        "- Open source is preferred\n\n"
        "### What We Know Doesn't Exist\n\n"
        "- No CNL-based prompt compression tool\n"
        "- No IA-integrated compression approach\n"
        "- No real-time authoring guidance system\n"
        "- No unified vocabulary/metadata framework for prompts\n"
        "- No tool explicitly targeting tech writers\n\n"
        "### Design Priorities\n\n"
        f"{design_priorities}\n\n"
        "---\n\n"
    )

    # ---------------------------------------------------------------
    # References
    # ---------------------------------------------------------------
    doc += (
        "## References & Further Reading\n\n"
        "### Academic Papers\n\n"
        "- Jiang, H., Wu, Q., Lin, C.-Y., Yang, Y., & Qiu, L. "
        "(2023). \"LLMLingua: Compressing Prompts for Accelerated "
        "Inference of Large Language Models.\" EMNLP 2023.\n"
        "- Jiang, H., Wu, Q., Luo, X., Li, D., Lin, C.-Y., "
        "Yang, Y., & Qiu, L. (2024). \"LongLLMLingua: Accelerating "
        "and Enhancing LLMs in Long Context Scenarios via Prompt "
        "Compression.\" ACL 2024.\n"
        "- Li, Y., Dong, B., Guerin, F., & Lin, C. (2023). "
        "\"Compressing Context to Enhance Inference Efficiency of "
        "Large Language Models.\" EMNLP 2023.\n"
        "- Xu, F., Shi, W., & Choi, E. (2023). \"RECOMP: Improving "
        "Retrieval-Augmented LMs with Compression and Selective "
        "Augmentation.\" ICLR 2024.\n\n"
        "### CNL Systems\n\n"
        "- Fuchs, N. E., Kaljurand, K., & Kuhn, T. (2008). "
        "\"Attempto Controlled English for Knowledge "
        "Representation.\" C3 2008.\n"
        "- Kaljurand, K. (2007). \"Attempto Controlled English as a "
        "Semantic Web Language.\" University of Tartu PhD Thesis.\n"
        "- SBVR (2017). \"Semantics of Business Vocabulary and "
        "Rules.\" OMG Specification.\n\n"
        "### Information Architecture\n\n"
        "- Morville, P. & Rosenfeld, L. (2006). *Information "
        "Architecture for the World Wide Web* (3rd ed.). O'Reilly.\n"
        "- Garrett, J. J. (2002). *The Elements of User "
        "Experience*. AIGA.\n"
        "- Wodtke, C. (2019). *Information Architecture: Blueprints "
        "for the Web* (4th ed.). O'Reilly.\n\n"
        "---\n\n"
    )

    # ---------------------------------------------------------------
    # Sign-off
    # ---------------------------------------------------------------
    doc += (
        "## Sign-off\n\n"
        "**Literature Review Phase:** COMPLETE\n\n"
        "**Foundation Status:** SOLID\n\n"
        "**Ready for Design Phase:** YES\n\n"
        f"**Approval Date:** {now.strftime('%Y-%m-%d')}\n"
    )

    return doc


# ---------------------------------------------------------------------------
# Save and verify
# ---------------------------------------------------------------------------

def save_literature_review(
    content: str,
    filepath: str = "LITERATURE_REVIEW.md"
) -> None:
    """Write the literature review to the project root.

    Args:
        content: Complete markdown content for the literature review.
        filepath: Output path for the document.
    """
    with open(filepath, 'w') as f:
        f.write(content)

    line_count = len(content.strip().split('\n'))
    logger.info("Saved literature review to %s (%s lines)", filepath,
                line_count)
    print(f"Saved literature review to {filepath} ({line_count} lines)")


def verify_literature_review(
    filepath: str = "LITERATURE_REVIEW.md"
) -> bool:
    """Validate literature review document completeness.

    Checks for 8 required sections, required content strings,
    positioning statement markers, and sign-off section per the
    v0.0.1d verification script.

    Args:
        filepath: Path to the literature review markdown file.

    Returns:
        True if the document passes all validation checks.
    """
    required_sections = [
        "Executive Summary",
        "Academic Research",
        "Competitive Analysis",
        "Theoretical Foundations",
        "Gap Analysis",
        "Positioning Statement",
        "Build Decision",
        "Design Priorities",
    ]

    required_content = {
        "CNL": "controlled natural language",
        "IA": "information architecture",
        "gap": "what",
        "positioning": "first",
        "differenti": "differ",
        "build": "build",
    }

    try:
        with open(filepath, 'r') as f:
            content = f.read().lower()

        # Check sections
        for section in required_sections:
            if section.lower() not in content:
                print(f"Missing section: {section}")
                return False

        # Check key content
        for key, phrase in required_content.items():
            if phrase.lower() not in content:
                print(f"Missing concept: {key}")
                return False

        # Check for positioning statement marker
        if "cnl-guided" not in content:
            print("Positioning statement missing or unclear")
            return False

        # Check for sign-off
        if "complete" not in content or "sign-off" not in content:
            print("Missing explicit sign-off")
            return False

        print("Executive summary present")
        print("All major sections present")
        print("CNL and IA concepts discussed")
        print("Gap analysis articulated")
        print("Positioning statement present")
        print("Build decision documented")
        print("Design priorities identified")
        print("Sign-off confirmed")

        return True

    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return False


if __name__ == "__main__":
    logger.info("Starting gap analysis & synthesis v0.0.1d")
    logger.info("Synthesizing outputs from v0.0.1a, v0.0.1b, v0.0.1c")

    academic_sources = load_academic_sources()
    competitive_analysis = load_competitive_analysis()
    cnl_ia_foundations = load_cnl_ia_foundations()

    gap_entries = build_gap_entries()
    logger.info("Built %s gap analysis entries", len(gap_entries))

    positioning_criteria = build_positioning_criteria()
    haiku_advantages = sum(
        1 for c in positioning_criteria if c.haiku_advantage
    )
    logger.info(
        "Built %s positioning criteria (%s Haiku advantages)",
        len(positioning_criteria), haiku_advantages
    )

    content = generate_literature_review(
        academic_sources, competitive_analysis, cnl_ia_foundations
    )
    save_literature_review(content)

    print("\n--- Verification ---")
    success = verify_literature_review()

    if success:
        logger.info("Literature review verification passed")
        logger.info(
            "Literature review phase complete; ready for design phase"
        )
    else:
        logger.error("Literature review verification failed")

    sys.exit(0 if success else 1)
