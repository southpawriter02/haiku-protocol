# v0.4.2 — Architecture Documentation

<aside>

**Version:** v0.4.2

**Parent:** v0.4.0 — Documentation & Release

**Status:** ⬜ Not Started

**Duration:** 30–45 minutes (across 3 sub-parts)

**Deliverable:** ARCHITECTURE.md with system design documentation + STYLE_GUIDE.md finalization

</aside>

---

## Objective

Create comprehensive architecture documentation that demonstrates technical depth and software engineering competence. Also finalize the STYLE_GUIDE.md (review-and-polish pass against implemented synthesizer, per decision P4-004).

---

## Sub-Parts

| Version | Name | Duration | Deliverable |
|---------|------|----------|-------------|
| [v0.4.2a](system_overview_and_components.md) | System Overview & Component Architecture | 10–15 min | Overview paragraph, key principles table, system components ASCII diagram, responsibilities table |
| [v0.4.2b](dataflow_and_module_reference.md) | Data Flow Documentation & Module Reference | 10–15 min | 4-stage pipeline walkthrough with concrete data shapes, public API for all 5 modules |
| [v0.4.2c](design_decisions_and_style_guide.md) | Design Decisions, Future Considerations & Style Guide | 10–15 min | 2 design decisions with trade-offs, 5 future enhancements, scalability table, STYLE_GUIDE.md finalization |

**Validation:** Quality checklist (accuracy against actual code, ASCII rendering, link verification)

---

## Template: ARCHITECTURE.md

```markdown
# Architecture: The Haiku Protocol

> Technical design documentation for the semantic compression system.

## Table of Contents
1. [Overview](#overview)
2. [System Components](#system-components)
3. [Data Flow](#data-flow)
4. [Module Reference](#module-reference)
5. [Design Decisions](#design-decisions)
6. [Future Considerations](#future-considerations)

---

## Overview

The Haiku Protocol is a **semantic compression pipeline** that transforms verbose technical documentation into a dense Controlled Natural Language (CNL) optimized for LLM context windows.

### Key Principles

| Principle | Description |
| --- | --- |
| **Lossless** | No semantic information is lost during compression |
| **Deterministic** | Same input always produces same output |
| **Parseable** | Output can be reliably interpreted by LLMs |
| **Extensible** | Grammar can be extended without breaking changes |

---

## System Components

\`\`\`
┌──────────────────────────────────────────────────────────────────────┐
│                        HAIKU PROTOCOL SYSTEM                         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐    │
│   │                      INPUT LAYER                            │    │
│   │   Raw Markdown/Text → Document Parser → Chunk List          │    │
│   └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│                              ▼                                       │
│   ┌─────────────────────────────────────────────────────────────┐    │
│   │                    PROCESSING LAYER                         │    │
│   │   Chunks → Entity Extractor (LLM) → Structured Entities     │    │
│   └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│                              ▼                                       │
│   ┌─────────────────────────────────────────────────────────────┐    │
│   │                     SYNTHESIS LAYER                         │    │
│   │   Entities → CNL Synthesizer → Haiku String                 │    │
│   └─────────────────────────────────────────────────────────────┘    │
│                              │                                       │
│                              ▼                                       │
│   ┌─────────────────────────────────────────────────────────────┐    │
│   │                    VALIDATION LAYER                         │    │
│   │   Haiku → Metrics Calculator → Compression Report           │    │
│   └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
\`\`\`

### Component Responsibilities

| Component | File | Responsibility |
| --- | --- | --- |
| Chunker | `chunker.py` | Split documents by semantic boundaries |
| Extractor | `extractor.py` | Identify Actions, States, Commands via LLM |
| Synthesizer | `synthesizer.py` | Apply CNL grammar rules |
| Validator | `validator.py` | Calculate compression metrics |
| Encoder | `encoder.py` | Orchestrate full pipeline |

---

## Data Flow

### Input → Output Transformation

**Stage 1: Chunking**
\`\`\`
Input:  "# Title\n## Section 1\nContent...\n## Section 2\nContent..."
Output: [Chunk(title="Section 1", content="..."), Chunk(title="Section 2", content="...")]
\`\`\`

**Stage 2: Entity Extraction**
\`\`\`
Input:  Chunk(content="To restart the server, save config first...")
Output: {actions: ["Restart_Server"], states: ["Config_Saved"], commands: [...]}
\`\`\`

**Stage 3: CNL Synthesis**
\`\`\`
Input:  {actions: ["Restart_Server"], states: ["Config_Saved"], ...}
Output: "Action:Restart_Server REQUIRES State:Config_Saved"
\`\`\`

**Stage 4: Validation**
\`\`\`
Input:  original_text, compressed_text
Output: {compression_ratio: 0.78, token_savings: 15, ...}
\`\`\`

---

## Module Reference

### encoder.py

The main orchestrator that chains all components.

\`\`\`python
def encode(document: str) -> dict:
    """
    Compress a document using the Haiku Protocol.
    
    Args:
        document: Raw markdown/text to compress
        
    Returns:
        dict with keys:
            - haiku: Compressed CNL string
            - original_tokens: Token count before
            - compressed_tokens: Token count after
            - compression_ratio: Float 0-1
            - savings_percent: Human-readable percentage
    """
\`\`\`

### chunker.py

Splits documents into semantic units.

\`\`\`python
class MarkdownChunker:
    def chunk(self, document: str) -> List[Chunk]
    
@dataclass
class Chunk:
    id: str
    title: str
    level: int
    content: str
\`\`\`

### extractor.py

LLM-powered entity extraction.

\`\`\`python
class EntityExtractor:
    def extract(self, text: str) -> ExtractedEntities
    
@dataclass
class ExtractedEntities:
    actions: List[str]
    states: List[str]
    commands: List[str]
    warnings: List[str]
    dependencies: List[Dict]
\`\`\`

---

## Design Decisions

### Why LLM-assisted extraction?

**Decision:** Use GPT-4 for entity extraction rather than rule-based NLP.

**Rationale:**
- Procedural language is highly variable
- Rules would require constant maintenance
- LLMs handle edge cases gracefully
- Cost is acceptable for PoC (~$0.01/document)

**Trade-off:** Requires API key, adds latency.

### Why custom CNL vs. existing formats?

**Decision:** Design a custom Controlled Natural Language.

**Rationale:**
- Existing formats (JSON-LD, RDF) optimized for data, not procedures
- Custom CNL can be optimized for token efficiency
- Demonstrates IA expertise (portfolio value)

**Trade-off:** Requires documentation, not industry standard.

---

## Future Considerations

### Potential Enhancements

1. **Batch Processing** - Process multiple documents in parallel
2. **Caching** - Cache extracted entities for repeated compressions
3. **Custom Models** - Fine-tune smaller models for extraction
4. **RAG Integration** - Use compressed docs in retrieval systems
5. **Decoder Module** - Expand CNL back to human-readable text

### Scalability Notes

| Scale | Consideration |
| --- | --- |
| 100 docs/day | Current architecture sufficient |
| 1000 docs/day | Add async processing, caching |
| 10000+ docs/day | Consider fine-tuned local models |
```

---

## Acceptance Criteria

- [ ]  [ARCHITECTURE.md](http://ARCHITECTURE.md) created
- [ ]  System diagram included
- [ ]  All modules documented
- [ ]  Design decisions explained
- [ ]  Future considerations noted