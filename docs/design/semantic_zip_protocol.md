# “Semantic Zip” Protocol

**Focus:** Condensed Context Storage 

**The Problem:** The "Context Window" (the amount of text an AI can read at once) is expensive and finite. Technical documentation is written for humans, meaning it is full of "fluff" (polite grammar, articles, transitions) that wastes space. 

**The "Disruptive" Idea:** Create a **Controlled Natural Language (CNL) for AI**. Just as developers "minify" code to make websites faster, you can "minify" language to make AI context denser.

- **The Concept:** Develop a "shorthand" style guide that compresses text by 50% while retaining 100% of the logic.
    - *Original (23 tokens):* "To restart the server, you must first ensure that the configuration file is saved, and then you can execute the reboot command."
    - *Semantic Zip (10 tokens):* `Action:Restart_Server REQUIRES State:Config_Saved -> EXEC:Reboot_Cmd`
- **Your Writer's Edge:** You are an expert in **Conciseness** and **Logic**. You can define the rules for this "pidgin" language.
- **The Tangible Output:**
    - A **"Style Guide for AI Memory"** published on GitHub.
    - A portfolio piece titled *"I shrank the AWS Manual by 40%."* Use a library like **LLMLingua** to benchmark your manual rewriting against standard compression algorithms to prove yours is more accurate.

---

# Technical Design Document: The Haiku Protocol

<aside>

**Document Version:** 1.0

**Author:** Technical Writer & AI Solutions Architect

**Status:** Draft for PoC Development

**Build Time Estimate:** 1 Weekend (12-16 hours)

</aside>

---

## 1. Executive Summary & The "Writer's Edge"

### The Problem: Context Rot & Token Poverty

Large Language Models suffer from two critical inefficiencies:

**The Core Insight:** A 128k token context window isn't *actually* 128k tokens of knowledge—it's closer to 70k tokens of knowledge wrapped in 58k tokens of human-readable packaging.

### The Solution: Lossless Semantic Compression

The **Haiku Protocol** is a two-stage compression system:

1. **The Encoder:** A rule-based + LLM-assisted pipeline that transforms human documentation into a **Controlled Natural Language (CNL)** optimized for machine parsing.
2. **The Decoder:** A prompt-engineering layer that teaches the LLM to interpret the CNL and expand it back to human-readable answers on demand.

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Human Docs     │ ──▶  │  Haiku Encoder  │ ──▶  │  CNL Storage    │
│  (Verbose)      │      │  (Compression)  │      │  (Dense)        │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Human Answer   │ ◀──  │  Haiku Decoder  │ ◀──  │  LLM + Context  │
│  (Readable)     │      │  (Expansion)    │      │  (Query)        │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

### The Differentiator: The Writer's Edge

This project succeeds *because* of Technical Writing expertise, not despite it.

**The Thesis:** A Technical Writer can outperform a generic compression algorithm because compression isn't about *removing* information—it's about *restructuring* it. That requires understanding meaning, not just syntax.

---

## 2. The Tech Stack (The "Right" Tools)

### Recommended Stack

### Justification

- **Why LangChain over LlamaIndex?**

LlamaIndex excels at *retrieval* pipelines. But the Haiku Protocol's core innovation is *transformation*, not retrieval. LangChain's `LLMChain` and `PromptTemplate` classes provide cleaner abstractions for building an encoder-decoder pipeline.

- **Why tiktoken?**

Token counts vary by model. `tiktoken` is OpenAI's official tokenizer, ensuring your compression metrics are accurate when benchmarking against GPT-4. It's a single `pip install` with zero dependencies.

- **Why Streamlit over Flask/FastAPI?**

For a weekend PoC, Streamlit eliminates all frontend complexity. You get a functional UI in ~50 lines of Python. The goal is *demonstrating* the concept, not production deployment.

- **Why LLMLingua as Benchmark?**

Microsoft's LLMLingua is the current academic standard for prompt compression. Comparing your results against it provides credible, citable validation.

### Installation (Single Command)

```bash
pip install langchain tiktoken llmlingua chromadb streamlit python-dotenv
```

---

## 3. Implementation Roadmap (The "Build")

### Phase 1: Data Preparation (3-4 hours)

**Objective:** Transform raw documentation into structured input for the encoder.

#### Before vs. After Schema

**BEFORE: Raw Markdown (Human-Optimized)**

```markdown
## Restarting the Application Server

Before you restart the server, it's important to make sure that 
all your configuration changes have been saved. This prevents any 
loss of settings during the reboot process.

### Steps:
1. First, navigate to the settings panel and click "Save Configuration."
2. Wait for the confirmation message to appear.
3. Once confirmed, you can safely run the restart command: `systemctl restart app-server`
4. The server will take approximately 30 seconds to come back online.

**Note:** If you skip step 1, your recent changes may be lost.
```

**AFTER: Structured JSON (Machine-Optimized)**

```json
{
  "doc_id": "server-restart-001",
  "title": "Restarting the Application Server",
  "haiku": "Action:Restart_Server REQUIRES State:Config_Saved; EXEC:systemctl_restart_app-server; WAIT:30s; WARN:Skip_Save->Data_Loss",
  "original_tokens": 127,
  "compressed_tokens": 28,
  "compression_ratio": 0.78,
  "metadata": {
    "category": "Operations",
    "dependencies": ["Config_Save_Procedure"],
    "commands": ["systemctl restart app-server"]
  }
}
```

#### The CNL Grammar (Your "Style Guide")

### Phase 2: The Logic Core (4-5 hours)

**Objective:** Build the encoder pipeline.

#### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        HAIKU ENCODER                             │
├──────────────────────────────────────────────────────────────────┤
│  INPUT: Raw Markdown Document                                    │
│                          │                                       │
│                          ▼                                       │
│  ┌────────────────────────────────────────────┐                  │
│  │  STAGE 1: Chunking                         │                  │
│  │  Split by headers (##, ###)                │                  │
│  └────────────────────────────────────────────┘                  │
│                          │                                       │
│                          ▼                                       │
│  ┌────────────────────────────────────────────┐                  │
│  │  STAGE 2: Entity Extraction (LLM)          │                  │
│  │  Identify: Actions, States, Commands       │                  │
│  └────────────────────────────────────────────┘                  │
│                          │                                       │
│                          ▼                                       │
│  ┌────────────────────────────────────────────┐                  │
│  │  STAGE 3: CNL Synthesis (LLM)              │                  │
│  │  Apply grammar rules, output Haiku string  │                  │
│  └────────────────────────────────────────────┘                  │
│                          │                                       │
│                          ▼                                       │
│  ┌────────────────────────────────────────────┐                  │
│  │  STAGE 4: Validation                       │                  │
│  │  Token count, semantic diff check          │                  │
│  └────────────────────────────────────────────┘                  │
│                          │                                       │
│                          ▼                                       │
│  OUTPUT: Compressed JSON + Metrics                               │
└──────────────────────────────────────────────────────────────────┘
```

#### Pseudo-Code: [`encoder.py`](http://encoder.py)

```python
# encoder.py - The Haiku Protocol Encoder

import tiktoken
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Initialize
tokenizer = tiktoken.encoding_for_model("gpt-4")
llm = ChatOpenAI(model="gpt-4", temperature=0)

# CNL Grammar (injected into prompt)
CNL_GRAMMAR = """
You are a semantic compression engine. Convert documentation to CNL:
- Action: = User procedure
- State: = Required precondition  
- EXEC: = Literal command
- REQUIRES = Dependency
- -> = Sequence/causation
- WARN: = Failure condition
- ; = Statement separator
"""

# Prompt Template
compress_prompt = PromptTemplate(
    input_variables=["grammar", "document"],
    template="""
{grammar}

DOCUMENT TO COMPRESS:
{document}

OUTPUT FORMAT:
Return ONLY the compressed CNL string. No explanations.
"""
)

# Chain
encoder_chain = LLMChain(llm=llm, prompt=compress_prompt)

def encode(document: str) -> dict:
    """Compress a document using the Haiku Protocol."""
    
    # Count original tokens
    original_tokens = len(tokenizer.encode(document))
    
    # Run compression
    haiku = encoder_chain.run(grammar=CNL_GRAMMAR, document=document)
    
    # Count compressed tokens
    compressed_tokens = len(tokenizer.encode(haiku))
    
    # Calculate metrics
    compression_ratio = 1 - (compressed_tokens / original_tokens)
    
    return {
        "original": document,
        "haiku": haiku.strip(),
        "original_tokens": original_tokens,
        "compressed_tokens": compressed_tokens,
        "compression_ratio": round(compression_ratio, 2),
        "savings_percent": f"{round(compression_ratio * 100)}%"
    }

# Example usage
if __name__ == "__main__":
    sample_doc = """
    To restart the server, you must first ensure that the 
    configuration file is saved, and then you can execute 
    the reboot command.
    """
    result = encode(sample_doc)
    print(result)
```

### Phase 3: The Demo (3-4 hours)

**Objective:** Create a visual proof-of-concept.

#### Streamlit App: [`app.py`](http://app.py)

```python
# app.py - Haiku Protocol Demo

import streamlit as st
from encoder import encode

st.set_page_config(page_title="Haiku Protocol", page_icon="📦")

st.title("📦 The Haiku Protocol")
st.markdown("*Lossless Semantic Compression for AI Context Windows*")

# Input
st.header("1. Input: Human Documentation")
input_text = st.text_area(
    "Paste your documentation here:",
    height=200,
    value="To restart the server, you must first ensure that the configuration file is saved, and then you can execute the reboot command."
)

if st.button("🗜️ Compress", type="primary"):
    with st.spinner("Encoding..."):
        result = encode(input_text)
    
    # Output
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("2. Original")
        st.code(result["original"], language="markdown")
        st.metric("Tokens", result["original_tokens"])
    
    with col2:
        st.header("3. Haiku (Compressed)")
        st.code(result["haiku"], language="text")
        st.metric("Tokens", result["compressed_tokens"])
    
    # Metrics
    st.header("4. Compression Metrics")
    st.success(f"🎯 **Compression Ratio:** {result['savings_percent']} token reduction")
    st.balloons()
```

#### Demo Output (Terminal Alternative)

```
╔══════════════════════════════════════════════════════════════════╗
║                    THE HAIKU PROTOCOL                            ║
║                 Semantic Compression Demo                        ║
╠══════════════════════════════════════════════════════════════════╣
║  ORIGINAL (127 tokens):                                          ║
║  "Before you restart the server, it's important to make sure     ║
║   that all your configuration changes have been saved..."        ║
╠══════════════════════════════════════════════════════════════════╣
║  HAIKU (28 tokens):                                              ║
║  Action:Restart_Server REQUIRES State:Config_Saved;              ║
║  EXEC:systemctl_restart_app-server; WAIT:30s;                    ║
║  WARN:Skip_Save->Data_Loss                                       ║
╠══════════════════════════════════════════════════════════════════╣
║  📊 COMPRESSION: 78% reduction | 99 tokens saved                 ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 4. Testing & Validation Strategy

### Validation Framework

### Three Unit Tests

#### Test 1: The Prerequisite Test

**Hypothesis:** Baseline AI loses track of dependencies in verbose text. Haiku preserves them.

**Setup:**

- Feed 5,000 tokens of verbose AWS documentation to GPT-4
- Feed the equivalent Haiku-compressed version (target: ~2,000 tokens)

**Prompt:** "What must be true before I can restart the EC2 instance?"

**Why Haiku Wins:** The `REQUIRES` syntax makes dependencies machine-parseable, not buried in prose.

---

#### Test 2: The Context Overflow Test

**Hypothesis:** When context is saturated, Haiku retains more actionable information.

**Setup:**

- Fill 100k tokens with verbose documentation (covers ~50 procedures)
- Fill 100k tokens with Haiku-compressed documentation (covers ~120 procedures)

**Prompt:** "List all procedures that require sudo access."

**Why Haiku Wins:** 2.4x more procedures in the same token budget means more answers survive context rot.

---

#### Test 3: The Semantic Fidelity Test

**Hypothesis:** Compression is lossless—the meaning is fully recoverable.

**Setup:**

- Compress a 500-word procedure into Haiku format
- Ask the LLM to "expand" the Haiku back into human-readable steps

**Prompt:** "Expand this Haiku into step-by-step instructions: `Action:Deploy_App REQUIRES State:Tests_Passed, State:Build_Complete; EXEC:kubectl_apply -f deployment.yaml; VERIFY:Pod_Status=Running`"

**Why This Matters:** If the LLM can perfectly expand Haiku, the compression is provably lossless.

---

## 5. Documentation & Deliverables

### Repository Structure

```
haiku-protocol/
├── README.md              # Project overview, quick start
├── ARCHITECTURE.md        # System design (this document)
├── STYLE_GUIDE.md         # The CNL grammar specification
├── src/
│   ├── encoder.py         # Core compression logic
│   ├── decoder.py         # Expansion logic (optional)
│   └── app.py             # Streamlit demo
├── tests/
│   ├── test_compression.py
│   └── test_fidelity.py
├── benchmarks/
│   ├── llmlingua_comparison.py
│   └── results.json
├── examples/
│   ├── aws_sample_original.md
│   └── aws_sample_haiku.json
├── diagrams/
│   ├── architecture.mmd   # Mermaid source
│   └── architecture.png   # Rendered diagram
└── requirements.txt
```

### Required Artifacts

### Resume Bullet Points

After completing this project, you can add:

- **Designed and implemented** a Controlled Natural Language (CNL) protocol that achieved **78% token compression** on technical documentation while maintaining semantic fidelity, reducing LLM API costs by 40%.
- **Built a Python-based semantic compression pipeline** using LangChain and GPT-4, benchmarked against Microsoft LLMLingua, demonstrating superior accuracy on procedural Q&A tasks.
- **Published an open-source "Style Guide for AI Memory"** defining grammar rules for machine-optimized documentation, showcasing expertise in Information Architecture and LLM prompt engineering.

---

## 6. Learning Outcomes

By completing this project, you will demonstrate mastery of:

### Core Technical Concepts

### Adjacent Skills

### Portfolio Keywords

These terms will appear naturally in your project, making it discoverable:

- Semantic Compression
- Context Window Optimization
- Controlled Natural Language
- LLM Cost Reduction
- Prompt Engineering
- RAG Optimization
- Token Efficiency

---

## Appendix: Weekend Build Schedule

**Total:** ~13 hours

---

<aside>

**Success Criteria**

Your PoC is complete when you can:

1. Paste any procedural documentation and see token reduction > 50%
2. Ask the LLM a question using compressed context and get an accurate answer
3. Show a side-by-side benchmark against LLMLingua
</aside>

[AI Agent Instructions — Haiku Protocol Project](AI%20Agent%20Instructions%20%E2%80%94%20Haiku%20Protocol%20Project%202d4bc6e7f5034a42ab7648351ac6d504.md)

[Session Memory Log — 2026-02-05](Session%20Memory%20Log%20%E2%80%94%202026-02-05%20d9bfa2b12246459c88e44c536ae577a6.md)

[v0.0.0 — Phase 0: Research & Discovery](v0%200%200%20%E2%80%94%20Phase%200%20Research%20&%20Discovery%20e27ea66ce68041488ce029459383d6d3.md)

[v0.1.0 — Phase 1: Environment & Tech Stack](v0%201%200%20%E2%80%94%20Phase%201%20Environment%20&%20Tech%20Stack%20349879cc61534f8aa2b104c455d7a823.md)

[v0.2.0 — Phase 2: Encoder Development](v0%202%200%20%E2%80%94%20Phase%202%20Encoder%20Development%204da545a7cdb5484f8e08dc5fc93c5eb4.md)

[v0.3.0 — Phase 3: Demo & Visualization](v0%203%200%20%E2%80%94%20Phase%203%20Demo%20&%20Visualization%2022c9bde6bfa04275af39123066ed1e44.md)

[v0.4.0 — Phase 4: Documentation & Release](v0%204%200%20%E2%80%94%20Phase%204%20Documentation%20&%20Release%205bf1c2560ac04ee8bd13676e1feacb68.md)