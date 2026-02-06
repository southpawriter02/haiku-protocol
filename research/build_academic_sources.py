"""
build_academic_sources.py - Academic Research Survey Builder
============================================================

Builds the annotated bibliography for v0.0.1a by defining academic
source metadata, applying the evaluation rubric, and saving the
results to research/academic_sources.json.

Functions:
    build_sources: Assemble the list of AcademicSource entries
    save_bibliography: Serialize sources to JSON
    filter_by_relevance: Filter sources by minimum relevance score
    verify_bibliography: Validate the output JSON file

Related:
    - v0.0.1a -- Academic Research Survey specification
    - v0.0.1b -- Industry Tool Analysis (consumes this output)
"""

import json
import logging
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


# Ensure output directories exist before configuring file logging
Path("logs").mkdir(parents=True, exist_ok=True)
Path("research").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/academic_research.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


EVALUATION_RUBRIC = {
    "relevance_to_compression": {
        "weight": 0.30,
        "scale": (1, 5),
        "criteria": "How directly does the paper address prompt/context compression?"
    },
    "methodology_rigor": {
        "weight": 0.25,
        "scale": (1, 5),
        "criteria": "Is the approach well-grounded? Peer-reviewed? Reproducible?"
    },
    "empirical_results": {
        "weight": 0.20,
        "scale": (1, 5),
        "criteria": "Are compression ratios, latency, and quality metrics clearly reported?"
    },
    "reproducibility": {
        "weight": 0.15,
        "scale": (1, 5),
        "criteria": "Is code available? Are baselines clear? Can results be replicated?"
    },
    "semantic_preservation": {
        "weight": 0.10,
        "scale": (1, 5),
        "criteria": "How well does the approach maintain meaning (not just token reduction)?"
    }
}


@dataclass
class AcademicSource:
    """Represents a single academic source with evaluation metadata."""

    authors: str
    year: int
    title: str
    venue: str
    doi_or_url: str
    key_finding: str
    methodology: str  # e.g., "Extractive", "Abstractive", "Hybrid"
    compression_ratio: Optional[str]  # e.g., "70.3%" or "Not reported"
    relevance_score: int  # 1-5
    relevance_justification: str
    reproducibility_status: str  # "Code available", "Partially available", "None"
    summary: str
    limitations: list[str]
    haiku_relevance: str
    date_reviewed: str = None

    def __post_init__(self):
        if self.date_reviewed is None:
            self.date_reviewed = datetime.now().isoformat()


def build_sources() -> list[AcademicSource]:
    """Assemble the list of evaluated academic sources.

    Returns:
        List of AcademicSource entries for papers on LLM prompt
        compression, context optimization, and semantic condensation.
    """
    return [
        AcademicSource(
            authors="Huiqiang Jiang, Qianhui Wu, Chin-Yew Lin, Yuqing Yang, Lili Qiu",
            year=2023,
            title="LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models",
            venue="EMNLP 2023 (Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing), pages 13358-13376",
            doi_or_url="https://doi.org/10.18653/v1/2023.emnlp-main.825",
            key_finding="Coarse-to-fine prompt compression using budget controller, token-level iterative compression, and instruction tuning achieves up to 20x compression with minimal performance loss.",
            methodology="Hybrid (extractive + LLM-guided token selection). Uses small LM (GPT-2/LLaMA-7B) to rank token importance via iterative compression with budget control.",
            compression_ratio="Up to 20x compression (95% token reduction); 1.7x-5.7x inference speedup across GSM8K, BBH, ShareGPT, and Arxiv-March23 benchmarks.",
            relevance_score=5,
            relevance_justification="Weighted rubric score: 4.90/5.00 (relevance_to_compression=5, methodology_rigor=5, empirical_results=5, reproducibility=5, semantic_preservation=4). Most directly addresses prompt compression with semantic preservation; most cited work in the field.",
            reproducibility_status="Code available (MIT license) at github.com/microsoft/LLMLingua; pip install llmlingua",
            summary="LLMLingua uses a pre-trained small language model to rank token importance and selectively prune low-information tokens through iterative compression. A budget controller maintains semantic integrity under high compression ratios, while instruction tuning aligns the distribution between the small ranking model and the target LLM. Evaluated on question answering, reasoning, and summarization tasks.",
            limitations=[
                "Requires access to a small LM for token-level importance ranking",
                "Assumes certain prompt structure (demonstrations + question + context)",
                "Performance varies significantly by task type and domain",
                "Token-level decisions may miss inter-sentence semantic dependencies"
            ],
            haiku_relevance="Pioneering work that validates semantic compression over naive truncation. LLMLingua's statistical token pruning contrasts with Haiku Protocol's grammar-driven CNL approach -- LLMLingua removes tokens while Haiku restructures information into a controlled natural language. Their compression ratios (up to 20x) set the benchmark to match or exceed."
        ),
        AcademicSource(
            authors="Yucheng Li, Bo Dong, Frank Guerin, Chenghua Lin",
            year=2023,
            title="Compressing Context to Enhance Inference Efficiency of Large Language Models",
            venue="EMNLP 2023 (Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing), pages 6342-6353",
            doi_or_url="https://doi.org/10.18653/v1/2023.emnlp-main.391",
            key_finding="Self-information-based pruning of lexical units identifies and removes redundant tokens, achieving 50% context cost reduction with minimal quality loss (0.023 BERTScore drop).",
            methodology="Extractive. Computes self-information via causal LM (GPT-2/OPT/LLaMA), merges tokens into lexical units (sentences, phrases, or tokens), and eliminates low-information content.",
            compression_ratio="50% context cost reduction (retains 57.2% of tokens); 36% reduction in inference memory; 32% reduction in inference time.",
            relevance_score=4,
            relevance_justification="Weighted rubric score: 4.35/5.00 (relevance_to_compression=5, methodology_rigor=4, empirical_results=4, reproducibility=5, semantic_preservation=3). Directly validates the redundancy hypothesis central to Haiku Protocol but uses purely statistical methods without semantic restructuring.",
            reproducibility_status="Code available (MIT license) at github.com/liyucheng09/Selective_Context; pip install selective-context",
            summary="Selective Context enhances LLM inference efficiency by computing self-information scores for lexical units using a base language model, then pruning units below an informativeness threshold. Evaluated on summarization, QA, code generation, and conversational tasks, showing that substantial context can be removed with minimal quality degradation.",
            limitations=[
                "Self-information metric is purely statistical with no semantic understanding",
                "Evaluation focused primarily on English-language tasks",
                "Extractive only -- cannot restructure or rewrite content",
                "May remove contextually important but statistically redundant tokens"
            ],
            haiku_relevance="Validates the hypothesis that human-written text contains significant redundancy from an LLM's perspective (~40-50% removable). The self-information approach is purely statistical -- Haiku Protocol's CNL grammar could achieve similar or better compression with guaranteed semantic preservation through structured rewriting rather than blind pruning."
        ),
        AcademicSource(
            authors="Fangyuan Xu, Weijia Shi, Eunsol Choi",
            year=2023,
            title="RECOMP: Improving Retrieval-Augmented LMs with Compression and Selective Augmentation",
            venue="arXiv 2023 (arXiv:2310.04408); published at ICLR 2024 (The Twelfth International Conference on Learning Representations)",
            doi_or_url="https://arxiv.org/abs/2310.04408",
            key_finding="Compresses retrieved documents into textual summaries using trained extractive and abstractive compressors, achieving compression to as low as 6% of original length with minimal performance loss.",
            methodology="Hybrid (extractive sentence selection + abstractive summary generation). Both compressors are trained end-to-end to optimize downstream task performance rather than generic summarization quality.",
            compression_ratio="As low as 6% of original document length (94% reduction); significantly outperforms off-the-shelf summarization models on downstream tasks.",
            relevance_score=4,
            relevance_justification="Weighted rubric score: 4.25/5.00 (relevance_to_compression=4, methodology_rigor=5, empirical_results=4, reproducibility=4, semantic_preservation=4). Dual extractive/abstractive approach parallels Haiku Protocol's pipeline, but focused on RAG context rather than general prompt compression.",
            reproducibility_status="Code available at github.com/carriex/recomp",
            summary="RECOMP trains two types of compressors for retrieval-augmented LMs: an extractive compressor that selects useful sentences from retrieved documents, and an abstractive compressor that generates concise summaries synthesizing information across multiple documents. Includes selective augmentation that returns an empty string when retrieval adds no value. Evaluated on language modeling and open-domain QA.",
            limitations=[
                "Focused on retrieval-augmented generation (RAG) context, not general prompt compression",
                "Requires task-specific training data for compressor models",
                "Abstractive compressor may introduce hallucinated content",
                "Evaluated primarily on language modeling and open-domain QA tasks"
            ],
            haiku_relevance="RECOMP's dual extractive/abstractive pipeline parallels Haiku Protocol's Extractor + Synthesizer architecture. The selective augmentation concept (returning empty when compression adds no value) informs the Validator's quality gates. Key difference: RECOMP trains neural compressors while Haiku Protocol uses grammar-defined CNL rules, making our approach more interpretable and deterministic."
        ),
        AcademicSource(
            authors="Huiqiang Jiang, Qianhui Wu, Xufang Luo, Dongsheng Li, Chin-Yew Lin, Yuqing Yang, Lili Qiu",
            year=2024,
            title="LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression",
            venue="ACL 2024 (Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics, Volume 1: Long Papers), pages 1658-1677",
            doi_or_url="https://doi.org/10.18653/v1/2024.acl-long.91",
            key_finding="Addresses long-context prompt compression by improving key information density with question-aware compression, achieving up to 21.4% performance improvement with 4x fewer tokens.",
            methodology="Hybrid (question-aware compression + key information density optimization). Extends LLMLingua with document reordering to address position bias and contrastive perplexity for improved key information retention in long contexts.",
            compression_ratio="2x-6x compression on ~10k token prompts; 1.4x-2.6x end-to-end latency acceleration; up to 94% cost reduction on LooGLE benchmark.",
            relevance_score=5,
            relevance_justification="Weighted rubric score: 4.90/5.00 (relevance_to_compression=5, methodology_rigor=5, empirical_results=5, reproducibility=5, semantic_preservation=4). Extends the compression paradigm to long-context scenarios, directly validating the growing need that Haiku Protocol addresses.",
            reproducibility_status="Code available (MIT license) at github.com/microsoft/LLMLingua; part of the LLMLingua project",
            summary="LongLLMLingua extends the LLMLingua framework to long-context scenarios (10k+ tokens). It introduces question-aware compression that uses contrastive perplexity to better identify key information, document reordering to mitigate position bias in long contexts, and dynamic compression ratios across prompt components. Evaluated on NaturalQuestions, LongBench, and LooGLE benchmarks.",
            limitations=[
                "Optimized for long-context question-answering scenarios specifically",
                "Compression quality depends on having the downstream query available at compression time",
                "Inherits LLMLingua's requirement for a small ranking LM",
                "Position bias mitigation via document reordering is heuristic-based"
            ],
            haiku_relevance="Demonstrates that long-context compression is a growing concern, validating Haiku Protocol's problem space. LongLLMLingua's question-aware approach highlights a key limitation: it requires knowing the downstream query at compression time. Haiku Protocol's CNL compression is query-independent -- the grammar preserves all semantic content regardless of future use, making it more versatile for stored knowledge bases."
        ),
    ]


def save_bibliography(sources: list[AcademicSource], filepath: str = "research/academic_sources.json") -> None:
    """Serialize annotated bibliography to JSON.

    Args:
        sources: List of evaluated academic sources.
        filepath: Output path for the JSON file.
    """
    data = {
        "meta": {
            "total_sources": len(sources),
            "generated_at": datetime.now().isoformat(),
            "inclusion_threshold": 3.5
        },
        "sources": [asdict(source) for source in sources]
    }
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(sources)} sources to {filepath}")


def filter_by_relevance(sources: list[AcademicSource], min_score: int = 3) -> list[AcademicSource]:
    """Filter bibliography by minimum relevance score.

    Args:
        sources: List of academic sources to filter.
        min_score: Minimum relevance_score threshold (inclusive).

    Returns:
        Filtered list containing only sources meeting the threshold.
    """
    return [s for s in sources if s.relevance_score >= min_score]


def verify_bibliography(filepath: str = "research/academic_sources.json") -> bool:
    """Validate bibliography JSON structure and content.

    Args:
        filepath: Path to the bibliography JSON file.

    Returns:
        True if the bibliography passes all validation checks.
    """
    required_fields = {
        "authors", "year", "title", "venue", "doi_or_url", "key_finding",
        "methodology", "compression_ratio", "relevance_score",
        "reproducibility_status", "summary", "limitations", "haiku_relevance"
    }

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        sources = data.get("sources", [])
        print(f"Found {len(sources)} sources")

        if len(sources) < 3:
            print("Error: Minimum 3 sources required")
            return False

        for i, source in enumerate(sources):
            missing = required_fields - set(source.keys())
            if missing:
                print(f"Source {i+1} missing fields: {missing}")
                return False

            if not (1 <= source.get("relevance_score", 0) <= 5):
                print(f"Source {i+1}: Invalid relevance score")
                return False

            if source.get("year", 0) < 2020:
                print(f"Warning: Source {i+1} published before 2020 (OK if highly relevant)")

        print("All sources have required fields")
        print("All relevance scores valid (1-5)")
        return True

    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return False
    except json.JSONDecodeError:
        print(f"Invalid JSON in {filepath}")
        return False


if __name__ == "__main__":
    logger.info("Starting academic research survey v0.0.1a")
    logger.info("Search scope: 2023-2025, focus on LLM prompt compression")
    logger.info("Target databases: Google Scholar, Semantic Scholar, arXiv, ACL Anthology")

    sources = build_sources()
    logger.info("Built %s academic source entries", len(sources))

    for source in sources:
        logger.info("Source: %s (%s) - relevance_score=%s",
                     source.title, source.year, source.relevance_score)

    save_bibliography(sources)

    high_relevance = filter_by_relevance(sources, min_score=4)
    print(f"High-relevance sources (score >= 4): {len(high_relevance)}")

    print("\n--- Verification ---")
    success = verify_bibliography()

    if success:
        logger.info("Bibliography verification passed")
    else:
        logger.error("Bibliography verification failed")

    sys.exit(0 if success else 1)
