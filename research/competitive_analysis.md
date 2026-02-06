# Competitive Analysis: Prompt Compression Tools

**Generated:** 2026-02-06T01:57:18.146027
**Version:** v0.0.1b
**Tools Evaluated:** 5

## Summary Matrix

| Tool | Compression | Semantics | Speed | Approach | Languages | LLM Dep | Open Src | Docs | Score | CNL |
|------|------|------|------|------|------|------|------|------|------|------|
| LLMLingua | 5/5 | 4/5 | 4/5 | Hybrid | 3/5 | 5/5 | 5/5 | 4/5 | **4.4** | No |
| RECOMP | 5/5 | 4/5 | 2/5 | Hybrid | 1/5 | 3/5 | 5/5 | 2/5 | **3.4** | No |
| Selective Context | 3/5 | 4/5 | 3/5 | Extractive | 1/5 | 5/5 | 5/5 | 3/5 | **3.2** | No |
| compress-gpt | 4/5 | 3/5 | 2/5 | Abstractive | 1/5 | 1/5 | 5/5 | 2/5 | **2.6** | No |
| gpt-prompt-engineer | 1/5 | 1/5 | 1/5 | Abstractive | 1/5 | 1/5 | 5/5 | 3/5 | **1.5** | No |

**Legend:**
- Score = Weighted sum across all 8 criteria (Compression 20%, Semantics 20%, Speed 15%, Approach 10%, Languages 10%, LLM Dep 10%, Open Src 10%, Docs 5%)
- CNL = Whether tool uses Controlled Natural Language for compression logic
- Score interpretation: 1-2 = Poor, 3-3.5 = Acceptable, 4-5 = Excellent

## Tool Details

### LLMLingua

- **Vendor:** Microsoft Research (Jiang et al.)
- **Version:** 0.2.x
- **Installation:** `Success`
- **License:** MIT
- **URL:** https://github.com/microsoft/LLMLingua
- **CNL Implemented:** No
- **Weighted Score:** 4.4
- **Notes:** Most mature compression tool. Coarse-to-fine token pruning using small LM (GPT-2/LLaMA) for importance ranking. Up to 20x compression with minimal performance loss. pip install llmlingua. Includes LLMLingua, LongLLMLingua, and LLMLingua-2 variants. Note: 'Microsoft Prompt Compression' referenced in industry discussions IS this tool -- no separate product exists.

### RECOMP

- **Vendor:** Fangyuan Xu, Weijia Shi, Eunsol Choi
- **Version:** N/A (research code)
- **Installation:** `Not tested`
- **License:** Not specified
- **URL:** https://github.com/carriex/recomp
- **CNL Implemented:** No
- **Weighted Score:** 3.4
- **Notes:** Dual extractive + abstractive compressor for RAG contexts. Extractive compressor selects useful sentences; abstractive compressor generates summaries. Compression to as low as 6% of original length (94% reduction). No PyPI package -- GitHub clone only. Requires task-specific training data. Published at ICLR 2024.

### Selective Context

- **Vendor:** Yucheng Li et al.
- **Version:** 1.0.x
- **Installation:** `Success`
- **License:** MIT
- **URL:** https://github.com/liyucheng09/Selective_Context
- **CNL Implemented:** No
- **Weighted Score:** 3.2
- **Notes:** Self-information-based lexical unit pruning. Computes self-information via causal LM (GPT-2), merges tokens into lexical units, eliminates low-information content. 50% context cost reduction with 0.023 BERTScore drop. pip install selective-context. Purely statistical -- no semantic restructuring capability.

### compress-gpt

- **Vendor:** Community (open-source)
- **Version:** 0.1.x
- **Installation:** `Success`
- **License:** MIT
- **URL:** https://github.com/yasyf/compress-gpt
- **CNL Implemented:** No
- **Weighted Score:** 2.6
- **Notes:** Semantic compression via GPT-4 API. Creates self-extracting prompts by decomposing content into static and dynamic chunks. ~70% token savings on LangChain tool-based prompts. pip install compress-gpt. Requires GPT-4 for quality output; results are non-deterministic. Replaces 'Microsoft Prompt Compression' in evaluation (which IS LLMLingua).

### gpt-prompt-engineer

- **Vendor:** Matt Shumer (open-source community)
- **Version:** N/A
- **Installation:** `Not tested`
- **License:** MIT
- **URL:** https://github.com/mshumer/gpt-prompt-engineer
- **CNL Implemented:** No
- **Weighted Score:** 1.5
- **Notes:** NOT a compression tool. Generates and tests prompt variations using GPT-4 with ELO rating system. Optimizes prompt quality and effectiveness, not token count. Included per evaluation scope but scores low on compression criteria. Requires OpenAI API key with GPT-4 access.

## Gap Analysis

Based on evaluation of 5 industry tools, Haiku Protocol can differentiate by:

1. **CNL-Guided Compression (Unique):** None of the evaluated tools implement Controlled Natural Language for compression. All rely on statistical token pruning (LLMLingua, Selective Context), neural abstractive rewriting (compress-gpt), or hybrid extraction + abstraction (RECOMP). Haiku Protocol's grammar-driven approach is genuinely novel.

2. **Deterministic Semantic Preservation:** Existing tools use probabilistic methods -- compression quality varies across runs and domains. A CNL grammar provides deterministic, auditable compression with guaranteed semantic fidelity.

3. **Query-Independent Compression:** LongLLMLingua requires the downstream query at compression time. Haiku Protocol's CNL output preserves all semantic content regardless of future use, making it suitable for stored knowledge bases.

4. **Interpretable Output:** Statistical compression (LLMLingua, Selective Context) produces truncated text that is difficult to audit. Abstractive compression (compress-gpt) produces non-deterministic rewrites. CNL output follows a formal grammar that humans and machines can validate.

5. **No LLM Dependency for Compression Logic:** Tools like compress-gpt and gpt-prompt-engineer require GPT-4 API access. Haiku Protocol's grammar rules are defined statically -- the LLM assists extraction but the compression logic itself is model-agnostic.

## Key Observations

- **Microsoft Prompt Compression IS LLMLingua.** The Microsoft offering referenced in industry discussions is the LLMLingua project itself (github.com/microsoft/LLMLingua). No separate enterprise product exists.
- **gpt-prompt-engineer is NOT a compression tool.** It generates and tests prompt variations using GPT-4, optimizing prompt quality rather than reducing token count. Included for completeness per evaluation scope.
- **No tool uses CNL.** This is the central finding -- the gap that Haiku Protocol is designed to fill.

## Raw Evaluation Data

```json
[
  {
    "name": "LLMLingua",
    "vendor": "Microsoft Research (Jiang et al.)",
    "version": "0.2.x",
    "installation_status": "Success",
    "compression_ratio": 5,
    "semantic_preservation": 4,
    "speed_latency": 4,
    "approach_type": "Hybrid",
    "approach_type_score": 5,
    "language_support": 3,
    "llm_dependency": 5,
    "open_source": 5,
    "documentation_quality": 4,
    "url": "https://github.com/microsoft/LLMLingua",
    "license": "MIT",
    "cnl_implemented": false,
    "notes": "Most mature compression tool. Coarse-to-fine token pruning using small LM (GPT-2/LLaMA) for importance ranking. Up to 20x compression with minimal performance loss. pip install llmlingua. Includes LLMLingua, LongLLMLingua, and LLMLingua-2 variants. Note: 'Microsoft Prompt Compression' referenced in industry discussions IS this tool -- no separate product exists.",
    "tested_date": "2026-02-06T01:57:18.145803",
    "weights": {
      "compression_ratio": 0.2,
      "semantic_preservation": 0.2,
      "speed_latency": 0.15,
      "approach_type": 0.1,
      "language_support": 0.1,
      "llm_dependency": 0.1,
      "open_source": 0.1,
      "documentation_quality": 0.05
    },
    "weighted_score": 4.4
  },
  {
    "name": "Selective Context",
    "vendor": "Yucheng Li et al.",
    "version": "1.0.x",
    "installation_status": "Success",
    "compression_ratio": 3,
    "semantic_preservation": 4,
    "speed_latency": 3,
    "approach_type": "Extractive",
    "approach_type_score": 1,
    "language_support": 1,
    "llm_dependency": 5,
    "open_source": 5,
    "documentation_quality": 3,
    "url": "https://github.com/liyucheng09/Selective_Context",
    "license": "MIT",
    "cnl_implemented": false,
    "notes": "Self-information-based lexical unit pruning. Computes self-information via causal LM (GPT-2), merges tokens into lexical units, eliminates low-information content. 50% context cost reduction with 0.023 BERTScore drop. pip install selective-context. Purely statistical -- no semantic restructuring capability.",
    "tested_date": "2026-02-06T01:57:18.145810",
    "weights": {
      "compression_ratio": 0.2,
      "semantic_preservation": 0.2,
      "speed_latency": 0.15,
      "approach_type": 0.1,
      "language_support": 0.1,
      "llm_dependency": 0.1,
      "open_source": 0.1,
      "documentation_quality": 0.05
    },
    "weighted_score": 3.2
  },
  {
    "name": "RECOMP",
    "vendor": "Fangyuan Xu, Weijia Shi, Eunsol Choi",
    "version": "N/A (research code)",
    "installation_status": "Not tested",
    "compression_ratio": 5,
    "semantic_preservation": 4,
    "speed_latency": 2,
    "approach_type": "Hybrid",
    "approach_type_score": 3,
    "language_support": 1,
    "llm_dependency": 3,
    "open_source": 5,
    "documentation_quality": 2,
    "url": "https://github.com/carriex/recomp",
    "license": "Not specified",
    "cnl_implemented": false,
    "notes": "Dual extractive + abstractive compressor for RAG contexts. Extractive compressor selects useful sentences; abstractive compressor generates summaries. Compression to as low as 6% of original length (94% reduction). No PyPI package -- GitHub clone only. Requires task-specific training data. Published at ICLR 2024.",
    "tested_date": "2026-02-06T01:57:18.145813",
    "weights": {
      "compression_ratio": 0.2,
      "semantic_preservation": 0.2,
      "speed_latency": 0.15,
      "approach_type": 0.1,
      "language_support": 0.1,
      "llm_dependency": 0.1,
      "open_source": 0.1,
      "documentation_quality": 0.05
    },
    "weighted_score": 3.4
  },
  {
    "name": "gpt-prompt-engineer",
    "vendor": "Matt Shumer (open-source community)",
    "version": "N/A",
    "installation_status": "Not tested",
    "compression_ratio": 1,
    "semantic_preservation": 1,
    "speed_latency": 1,
    "approach_type": "Abstractive",
    "approach_type_score": 1,
    "language_support": 1,
    "llm_dependency": 1,
    "open_source": 5,
    "documentation_quality": 3,
    "url": "https://github.com/mshumer/gpt-prompt-engineer",
    "license": "MIT",
    "cnl_implemented": false,
    "notes": "NOT a compression tool. Generates and tests prompt variations using GPT-4 with ELO rating system. Optimizes prompt quality and effectiveness, not token count. Included per evaluation scope but scores low on compression criteria. Requires OpenAI API key with GPT-4 access.",
    "tested_date": "2026-02-06T01:57:18.145815",
    "weights": {
      "compression_ratio": 0.2,
      "semantic_preservation": 0.2,
      "speed_latency": 0.15,
      "approach_type": 0.1,
      "language_support": 0.1,
      "llm_dependency": 0.1,
      "open_source": 0.1,
      "documentation_quality": 0.05
    },
    "weighted_score": 1.5
  },
  {
    "name": "compress-gpt",
    "vendor": "Community (open-source)",
    "version": "0.1.x",
    "installation_status": "Success",
    "compression_ratio": 4,
    "semantic_preservation": 3,
    "speed_latency": 2,
    "approach_type": "Abstractive",
    "approach_type_score": 1,
    "language_support": 1,
    "llm_dependency": 1,
    "open_source": 5,
    "documentation_quality": 2,
    "url": "https://github.com/yasyf/compress-gpt",
    "license": "MIT",
    "cnl_implemented": false,
    "notes": "Semantic compression via GPT-4 API. Creates self-extracting prompts by decomposing content into static and dynamic chunks. ~70% token savings on LangChain tool-based prompts. pip install compress-gpt. Requires GPT-4 for quality output; results are non-deterministic. Replaces 'Microsoft Prompt Compression' in evaluation (which IS LLMLingua).",
    "tested_date": "2026-02-06T01:57:18.145817",
    "weights": {
      "compression_ratio": 0.2,
      "semantic_preservation": 0.2,
      "speed_latency": 0.15,
      "approach_type": 0.1,
      "language_support": 0.1,
      "llm_dependency": 0.1,
      "open_source": 0.1,
      "documentation_quality": 0.05
    },
    "weighted_score": 2.6
  }
]
```
