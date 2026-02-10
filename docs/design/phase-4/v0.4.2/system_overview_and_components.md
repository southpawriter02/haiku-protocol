# v0.4.2a — System Overview & Component Architecture

**Design Specification for ARCHITECTURE.md (Part 1/3)**

> **Phase:** 4 — Documentation & Release
> **Version:** v0.4.2a
> **Status:** Design Specification
> **Duration:** 10–15 minutes (implementation)
> **Audience:** Senior engineers, hiring managers, architecture reviewers
> **Deliverable:** First section of ARCHITECTURE.md

---

## Document Purpose

This specification defines the **System Overview and Component Architecture** sections of the final `ARCHITECTURE.md` document. These sections provide the foundational conceptual model: what the Haiku Protocol is, what principles guide its design, how its components relate, and what each module contributes to the overall pipeline.

This is Part 1 of a 3-part ARCHITECTURE.md specification:
- **Part 1 (this file):** System Overview, Key Principles, System Components, Component Responsibilities, Table of Contents
- **Part 2 (dataflow_and_module_reference.md):** Data Flow Documentation, Module Reference
- **Part 3 (design_decisions_and_style_guide.md):** Design Decisions, Future Considerations, Style Guide Finalization

---

## User Stories

### Story 1: Senior Engineer Evaluating System Design

> As a senior engineer reviewing the Haiku Protocol for adoption or learning, I want to understand the system's conceptual architecture without reading individual source files. I need to see the component boundaries, the flow of data, and the design principles so I can assess whether the system meets our standards for clarity, maintainability, and extensibility.

**Acceptance Criteria:**
- The Overview section succinctly describes the Haiku Protocol in one paragraph
- The Key Principles table conveys the core guarantees the system makes
- The System Components diagram visually shows the four-layer architecture
- The Component Responsibilities table maps each `.py` file to its role with one-sentence clarity
- I can trace how a document flows through the pipeline without reading code

### Story 2: Hiring Manager Assessing Technical Depth

> As a hiring manager reviewing the candidate's portfolio, I want ARCHITECTURE.md to demonstrate that the author understands system design beyond "it works." I'm looking for evidence that the author thought about principles, boundaries, data models, and trade-offs. I should finish reading this section confident that the author has engineering maturity.

**Acceptance Criteria:**
- The document makes intentional design choices visible (not just "here are the modules")
- Principles are named explicitly (Lossless, Deterministic, Parseable, Extensible)
- The component diagram is clean and professional — ASCII but polished
- Design decisions include rationale and trade-offs (not just features)
- The author's reasoning is audible throughout

---

## Content Specification

### Overview Section

**Format:** One paragraph (3–5 sentences)

**Content Requirements:**
- Identify the Haiku Protocol as a **semantic compression pipeline**
- Explain the core value proposition: lossless, machine-optimized compression via CNL
- Position it in the broader context: addresses expensive LLM context windows
- Avoid marketing ("revolutionary," "game-changing") — use precise technical language
- Use first-person perspective: "The Haiku Protocol is…" or "The system works by…"

**Example Structure (not prescriptive word-for-word):**
```
The Haiku Protocol is a lossless semantic compression pipeline that transforms
verbose technical documentation into dense, machine-readable Controlled Natural
Language (CNL) while preserving 100% semantic meaning. The system operates as a
four-stage pipeline: documents are segmented into semantic chunks, key entities
and relationships are extracted via LLM-assisted analysis, compressed statements
are synthesized according to formal CNL grammar rules, and the output is
validated against compression metrics. The design prioritizes deterministic,
reproducible compression suitable for deployment in LLM context-window management
systems and archival applications.
```

**Accuracy Requirements:**
- "Semantic compression" — verified against encoder.py docstring and README
- "CNL" — verified against synthesizer.py docstring and STYLE_GUIDE.md
- "Four-stage pipeline" — verified against encoder.py class structure
- "LLM-assisted" — verified against extractor.py docstring
- "Lossless" — verified against validator.py and design decisions

---

### Key Principles Table

**Format:** A 2-column Markdown table with 4 rows

**Exact Principles (from v0.4.2 README template and actual implementation):**

| Principle | Description |
|-----------|-------------|
| **Lossless** | Compression preserves 100% semantic content. No information is discarded; only redundancy and presentation formatting are removed. Round-trip from CNL back to natural language recovers the original meaning. |
| **Deterministic** | Same input always produces same output. No probabilistic generation, randomization, or non-deterministic LLM sampling. Enables caching, reproducibility, and testing. |
| **Parseable** | Output conforms to formal CNL grammar (EBNF specification) with unambiguous syntax. Can be validated, parsed, and processed by tools without semantic interpretation. |
| **Extensible** | New operators, grammar rules, and validation criteria can be added without breaking existing CNL. Designed for expansion without migration costs. |

**Accuracy Requirements:**
- **Lossless:** Verified against validator.py information_retention metric design
- **Deterministic:** Verified against synthesizer.py design (no sampling) and chunker.py strategy model
- **Parseable:** Verified against STYLE_GUIDE.md BNF specification and v0.0.2c formalization
- **Extensible:** Verified against modular architecture (chunker, extractor, synthesizer, validator as separate modules) and STYLE_GUIDE.md operator definitions

**Key Design Constraint:** These four principles are the **authoritative statement** of what the system guarantees. Every design decision and trade-off must align with these principles. If future work violates one of these principles, it requires explicit Decision Log entry and Design Review.

---

### System Components ASCII Diagram

**Format:** ASCII box diagram (4 layers, aligned, universal rendering)

**Rendering Requirements:**
- Use `+`, `-`, `|`, `*` for box drawing (compatible with all terminals and GitHub)
- No Mermaid, PlantUML, or external rendering
- Align vertically to show layer progression
- Include labels and flow arrows
- Must render correctly on GitHub without rendering plugins

**Exact Diagram Structure:**

```
╔════════════════════════════════════════════════════════════════════════╗
║                         HAIKU PROTOCOL PIPELINE                        ║
╚════════════════════════════════════════════════════════════════════════╝

    INPUT LAYER
    ───────────────────────────────────────────────────────────────────
    │  Raw Document Text                                              │
    │  (Markdown, plaintext, or structured prose)                    │
    └───────────────────────────────────────────────────────────────────┘
                                  ↓
    PROCESSING LAYER
    ───────────────────────────────────────────────────────────────────
    │  ┌──────────────────────┐  ┌────────────────────────────────┐ │
    │  │  Document Chunker    │  │  Entity Extraction (LLM)       │ │
    │  │  • Semantic segments │  │  • Entity identification       │ │
    │  │  • Token-aware       │  │  • Relationship mapping       │ │
    │  │  • Overlap handling  │  │  • Confidence scoring         │ │
    │  └──────────────────────┘  └────────────────────────────────┘ │
    │          [chunker.py]               [extractor.py]             │
    └───────────────────────────────────────────────────────────────────┘
                                  ↓
    SYNTHESIS LAYER
    ───────────────────────────────────────────────────────────────────
    │  ┌──────────────────────────────────────────────────────────┐   │
    │  │  CNL Synthesizer                                         │   │
    │  │  • Grammar application                                  │   │
    │  │  • Statement generation                                 │   │
    │  │  • Operator selection                                   │   │
    │  └──────────────────────────────────────────────────────────┘   │
    │               [synthesizer.py]                                   │
    └───────────────────────────────────────────────────────────────────┘
                                  ↓
    VALIDATION LAYER
    ───────────────────────────────────────────────────────────────────
    │  ┌──────────────────────┐  ┌────────────────────────────────┐ │
    │  │  CNL Validator       │  │  Metrics Computation           │ │
    │  │  • Grammar check     │  │  • Compression ratio           │ │
    │  │  • Syntax verify     │  │  • Semantic similarity         │ │
    │  │  • Error detection   │  │  • Information retention       │ │
    │  └──────────────────────┘  └────────────────────────────────┘ │
    │          [validator.py]      [validator.py + encoder.py]       │
    └───────────────────────────────────────────────────────────────────┘
                                  ↓
    OUTPUT
    ───────────────────────────────────────────────────────────────────
    │  Compressed CNL Statement + Validation Metrics                  │
    │  [encoder.py orchestrates entire pipeline]                      │
    └───────────────────────────────────────────────────────────────────┘
```

**Diagram Annotations:**
- **INPUT LAYER:** Accepts raw documents in any prose format
- **PROCESSING LAYER:** Splits into two parallel concerns (chunking + extraction) but flow is sequential in implementation
- **SYNTHESIS LAYER:** Converts entities/relations into formal CNL statements
- **VALIDATION LAYER:** Confirms output correctness and measures compression effectiveness
- **OUTPUT:** Final CNL + metrics; encoder.py is the orchestrator

**Construction Guidelines (for implementer):**
- Use monospace font in the output document
- Ensure box widths don't exceed 76 characters (safe for most terminals)
- Keep ASCII characters universal (no fancy Unicode box-drawing if rendering elsewhere)
- Preserve indentation exactly as shown (4 spaces per level)
- Test rendering on GitHub before merging

---

### Component Responsibilities Table

**Format:** Markdown table mapping each module file to its responsibilities

**Table Structure:**

| Module File | Primary Class(es)/Function | Primary Responsibility | Key Inputs | Key Outputs |
|---|---|---|---|---|
| `chunker.py` | `DocumentChunker`, `Chunk` | Segment documents into semantic chunks; manage overlap and size constraints | Raw document text, config (chunk_size, overlap, strategy) | List of `Chunk` objects with text, position, token count |
| `extractor.py` | `EntityExtractor`, `Entity`, `ExtractedEntities` | Extract entities and relationships using LLM-assisted NLP; maintain confidence scores | Chunk text, chunk_id, config (model, threshold) | `ExtractedEntities` with entity list and relations dict |
| `synthesizer.py` | `CNLSynthesizer`, `CNLStatement` | Apply formal CNL grammar rules to generate compressed statements from entities | Entities list, relations dict, config (grammar rules) | CNL-formatted statement string + confidence score |
| `validator.py` | `HaikuValidator`, `ValidationResult`, `CompressionMetrics` | Validate grammar correctness, compute compression metrics, and quality assessment | Original text, compressed CNL, config (similarity model) | `ValidationResult` and `CompressionMetrics` objects |
| `encoder.py` | `HaikuEncoder` | Orchestrate complete pipeline: chunk → extract → synthesize → validate | Document text, config (API keys, model names) | Compressed CNL output and optional metrics |

**Table Accuracy Requirements:**
- **Module Files:** Verify against actual filenames in `src/`
- **Class Names:** Verify against class definitions in each `src/*.py` file
- **Responsibility:** One-sentence summary matching the module docstring (lines 1–20)
- **Key Inputs:** Match the `__init__` and method signature parameters
- **Key Outputs:** Match the return types documented in method docstrings
- **No Private Classes:** Exclude internal-only classes (those prefixed `_` or marked as implementation details)

**Example Verification Process:**
```python
# src/chunker.py
class DocumentChunker:
    """Segments documents into chunks for processing."""
    def __init__(self, chunk_size: int = 512, ...):
    def chunk(self, document: str) -> List[Chunk]:
        # Returns List[Chunk]
# ✓ Module Name: chunker.py
# ✓ Class: DocumentChunker
# ✓ Responsibility: "Segment documents into semantic chunks; manage overlap and size constraints"
# ✓ Key Inputs: Document text, config
# ✓ Key Outputs: List of Chunk objects
```

---

### Table of Contents (Full ARCHITECTURE.md)

**Purpose:** Provide a roadmap for the complete ARCHITECTURE.md document. This sub-part defines structure; the actual TOC will be generated when full ARCHITECTURE.md is written.

**Expected Structure:**

```
# ARCHITECTURE.md

1. Overview
   - System Description (one paragraph)
   - Key Principles (table)

2. System Components
   - Component Diagram (ASCII)
   - Component Responsibilities (table)

3. Data Flow
   - Pipeline Stages (walkthrough with examples)
   - Data Shape Verification (table)

4. Module Reference
   - Public API Signatures
   - encode() [HaikuEncoder]
   - MarkdownChunker.chunk()
   - EntityExtractor.extract()
   - synthesize_cnl() [CNLSynthesizer]
   - CompressionValidator.calculate_metrics() [HaikuValidator]
   - count_tokens() [if exposed in encoder]

5. Design Decisions
   - Decision 1: LLM-assisted vs. Rule-based Extraction
   - Decision 2: Custom CNL vs. JSON-LD/RDF

6. Future Considerations
   - Enhancement Candidates (numbered list)
   - Scalability Table

7. Related Documents
   - Links to STYLE_GUIDE.md, DESIGN_LOG.md, research artifacts
```

---

## Acceptance Criteria

### General Criteria (All Sections)

1. All text is accurate to the **actual implemented code**, not aspirational or idealized versions
2. No Mermaid diagrams, PlantUML, or proprietary rendering tools — ASCII only
3. All component names match actual filenames and class definitions in `src/`
4. All principles are derived from actual system behavior as evidenced in code and tests
5. The document is self-contained — a reader needs no external reference to understand the architecture
6. Markdown is valid GitHub-Flavored Markdown (GFM) and renders correctly on GitHub
7. No typos, grammatical errors, or inconsistent terminology
8. Future tense avoided; present tense used throughout ("The system does…" not "The system will…")

### Overview Section Criteria

9. One paragraph, 3–5 sentences
10. Describes the Haiku Protocol as a semantic compression pipeline
11. Mentions the four-stage processing model (chunking, extraction, synthesis, validation)
12. Explains the CNL output format
13. Identifies the use case (LLM context-window management, archival)
14. No marketing language; technical precision throughout

### Key Principles Criteria

15. Exactly four principles: Lossless, Deterministic, Parseable, Extensible
16. Each principle has a clear one-sentence definition and 2–3 sentence explanation
17. Principle descriptions match the v0.4.2 README template exactly
18. Table is properly formatted Markdown (pipes, hyphens, alignment)
19. Each principle is verified against at least one code file or design decision

### System Components Diagram Criteria

20. Diagram shows four layers: Input, Processing, Synthesis, Validation
21. All ASCII characters are universal (no fancy Unicode requiring special fonts)
22. Diagram aligns properly in monospace (tested in GitHub)
23. Layer progression flows top-to-bottom with vertical arrows
24. Each layer includes 1–3 example activities or classes
25. Module filenames appear in brackets (e.g., `[chunker.py]`)
26. Width does not exceed 76 characters per line (standard terminal width)

### Component Responsibilities Table Criteria

27. Five rows (one per module file)
28. Five columns: Module File, Primary Class(es)/Function, Primary Responsibility, Key Inputs, Key Outputs
29. Module file names are exact (chunker.py, extractor.py, synthesizer.py, validator.py, encoder.py)
30. Class names match actual class definitions in source code
31. Responsibility is a single sentence (one-liner)
32. Key Inputs describe the parameters passed to __init__ and primary methods
33. Key Outputs describe the return type of primary methods
34. No private classes, no implementation details, no stubs
35. Each row is verifiable by reading the corresponding source file

### Table of Contents Criteria

36. Identifies all major sections of the full ARCHITECTURE.md
37. Aligns with the v0.4.2 scope definition
38. Is itself no longer than one printed page
39. Includes subheadings for Data Flow, Module Reference, Design Decisions, Future Considerations
40. Includes "Related Documents" link list

---

## Content Accuracy Requirements

### Verification Checklist

Before considering the Overview & Components sections complete, verify each claim:

| Claim | Source File(s) | Verification Method |
|---|---|---|
| "Four-stage pipeline: chunk, extract, synthesize, validate" | `src/encoder.py` docstring (lines 40–45) | Read HaikuEncoder.encode() doc; confirm it describes these four stages in order |
| "Document chunking via DocumentChunker" | `src/chunker.py` | Confirm class exists, has chunk() method, returns List[Chunk] |
| "Entity extraction via LLM" | `src/extractor.py` | Confirm EntityExtractor.__init__() takes model name parameter; docstring mentions NLP |
| "CNL synthesis via CNLSynthesizer" | `src/synthesizer.py` | Confirm class exists, has synthesize() method, returns str (CNL) |
| "Validation via HaikuValidator" | `src/validator.py` | Confirm class exists, has validate() and compute_metrics() methods |
| "Encoder orchestrates pipeline" | `src/encoder.py` lines 40–50 | Confirm docstring describes coordination of chunker, extractor, synthesizer |
| "Lossless compression" | `src/validator.py` lines 53–62 | Confirm information_retention metric is documented as design goal |
| "Deterministic" | `src/synthesizer.py` + `src/chunker.py` | Confirm no random sampling; strategy-based determinism |
| "Parseable per CNL grammar" | `STYLE_GUIDE.md` + `src/synthesizer.py` | Confirm synthesizer applies grammar rules; STYLE_GUIDE defines operators |
| "Extensible via modular design" | `src/` directory structure | Confirm five independent modules can be updated without breaking others |

### Accuracy Verification Instructions

1. Open each source file listed above
2. Find the specific docstring or code section mentioned
3. Verify the claim matches what's actually written (not what you wish were written)
4. If discrepancy found, update the ARCHITECTURE.md content OR log as a bug for Phase 3 to fix
5. Never guess or assume; always verify in the source

---

## Dependencies

### Input Artifacts

| Artifact | Source | Purpose |
|---|---|---|
| `chunker.py` | Phase 2 (v0.2.1) | Defines DocumentChunker and Chunk dataclass |
| `extractor.py` | Phase 2 (v0.2.2) | Defines EntityExtractor, Entity, ExtractedEntities |
| `synthesizer.py` | Phase 2 (v0.2.3) | Defines CNLSynthesizer and CNLStatement |
| `validator.py` | Phase 2 (v0.2.4) | Defines HaikuValidator, ValidationResult, CompressionMetrics |
| `encoder.py` | Phase 2 (v0.2.0) | Defines HaikuEncoder (orchestrator) |
| `README.md` | Existing (v0.1.3b) | Current project overview; v0.4.2 uses its principles/framing |
| `STYLE_GUIDE.md` | Phase 0 (v0.0.2c draft) | CNL grammar specification; informs design principles |

### Output Artifacts

| Artifact | Purpose |
|---|---|
| System Overview & Components sections (draft) | First sections of ARCHITECTURE.md to be finalized in v0.4.2 implementation |

---

## Decision Log

### D-v0.4.2a-001: ASCII Diagrams Over Mermaid/PlantUML

**Decision:** Use ASCII art exclusively for all system diagrams (component layout, data flow, etc.). Do not use Mermaid, PlantUML, or other rendering-engine-dependent tools.

**Rationale:**
- ASCII diagrams render universally on GitHub without requiring plugins or JavaScript
- ASCII is version-controllable in Git diffs (can see exactly what changed)
- ASCII respects the principle that documentation should work offline and in any text editor
- No external dependencies or build tools needed to view diagrams
- Professional-looking ASCII is achievable with `+`, `-`, `|`, and box-drawing characters

**Trade-off:**
- ASCII diagrams require more careful formatting to align properly
- More difficult to generate automatically; must be hand-crafted or created with ASCII-friendly tools
- Less "polished" visual appearance compared to rendered diagrams, but more technically sound for a developer audience

**Decision Status:** FINAL — This constraint applies to all ARCHITECTURE.md diagrams.

**Related Decisions:** P4-003 from broader v0.4.0 decision log references this constraint.

---

### D-v0.4.2a-002: Four Key Principles from Actual System Behavior

**Decision:** Define the system's design principles as: Lossless, Deterministic, Parseable, Extensible. These are derived from observable behavior and design choices in the implemented code, not aspirational goals.

**Rationale:**
- **Lossless:** Validator tracks information_retention metric; semantic similarity is measured, not assumed
- **Deterministic:** Chunker uses strategy-based segmentation (not random); synthesizer applies grammar rules (not probabilistic sampling)
- **Parseable:** CNL output must conform to STYLE_GUIDE.md grammar; validator checks syntax
- **Extensible:** Modular architecture (chunker, extractor, synthesizer, validator as separate, composable units) allows new operators/rules without rewriting core

**Trade-off:**
- Limiting to four principles loses nuance (e.g., "efficient," "privacy-preserving," "explainable" are also design goals, but not as fundamental)
- Four principles are chosen for their impact on the public API and user experience; secondary goals are documented in design decisions, not as top-level principles

**Decision Status:** FINAL — These four principles are the system's guarantee to users.

**Verification:** Each principle must be verifiable by examining source code or test results.

---

## Quality Checklist

This checklist replaces traditional "Unit Testing Requirements" (not applicable to documentation) and ensures content accuracy.

### Pre-Publication Checklist

- [ ] All five module files (chunker.py, extractor.py, synthesizer.py, validator.py, encoder.py) are listed in Component Responsibilities table
- [ ] No stub modules, no future-tense code ("will implement"), no unimplemented methods documented
- [ ] Overview paragraph is 3–5 sentences
- [ ] All four principles (Lossless, Deterministic, Parseable, Extensible) appear in the Key Principles table
- [ ] Principle descriptions match the v0.4.2 README template word-for-word
- [ ] System Components diagram renders correctly in monospace (copy-paste into a text editor and verify alignment)
- [ ] All ASCII box-drawing characters are universally supported (+, -, |, no fancy Unicode)
- [ ] Diagram shows four layers: Input, Processing, Synthesis, Validation
- [ ] Module filenames in diagram match actual filenames (e.g., [chunker.py] not [chunking_module.py])
- [ ] Component Responsibilities table has exactly 5 rows (one per module)
- [ ] Each row's "Key Inputs" matches parameters to __init__ or primary method
- [ ] Each row's "Key Outputs" matches return type of primary method
- [ ] All module names, class names, and method names are exact matches to source code
- [ ] Table of Contents aligns with v0.4.2 scope definition (covers Overview, Components, Data Flow, Module Reference, Design Decisions, Future Considerations)
- [ ] No typos or grammatical errors in any section
- [ ] All internal links are valid (e.g., links within ARCHITECTURE.md section references)
- [ ] Markdown is valid GitHub-Flavored Markdown; tested on GitHub
- [ ] Document is self-contained (reader needs no external files to understand architecture)
- [ ] No marketing language ("revolutionary," "cutting-edge"); technical precision throughout
- [ ] All claims are verified against source code using the Verification Checklist above
- [ ] Decision Log entries reference actual design choices, not hypothetical ones
- [ ] Related documents (STYLE_GUIDE.md, RESEARCH_REPORT.md, etc.) are listed in the full ARCHITECTURE.md once written

---

## Implementation Notes

### For the Implementer

1. **Start with Code Review:** Before writing any section, read each of the five source files (chunker.py, extractor.py, synthesizer.py, validator.py, encoder.py) completely. Understand the actual API, not what you assume it to be.

2. **Verify Every Claim:** Use the Accuracy Verification Checklist. Cross-reference your documentation against the source code line-by-line. If documentation says something the code doesn't do, update the documentation (not the code — Phase 4 does not modify src/).

3. **ASCII Diagram Rendering:** Test your ASCII diagrams in multiple environments:
   - Copy the diagram into a GitHub markdown preview
   - Paste it into VS Code with a monospace font
   - Verify alignment is consistent
   - Share with a colleague to confirm it looks right on their system

4. **Component Responsibilities Table:** This table is the hardest to get right. For each row:
   - Open the source file
   - Find the class definition
   - Read the __init__ parameters → these become "Key Inputs"
   - Read the primary method's return type → this becomes "Key Outputs"
   - Write a one-sentence responsibility summary
   - Verify the class name matches exactly

5. **Design Principles:** These are not aspirational. If the code doesn't currently implement "lossless" compression (e.g., if it drops some information), don't claim losslessness. If it does, document it. Honesty is more valuable than optimism in technical architecture docs.

6. **Cross-Linking:** Once all sections are drafted, ensure links between Overview/Principles/Components are consistent. The Principles should be referenced in the Design Decisions section later.

---

## Related Documents

- **Authoritative Scope:** [v0.4.0 SCOPE_BREAKDOWN.md](../v0.4.0/SCOPE_BREAKDOWN.md) — sections 7.2 and 8 define v0.4.2 scope
- **Part 2 Specification:** [v0.4.2b — Data Flow & Module Reference](dataflow_and_module_reference.md)
- **Part 3 Specification:** [v0.4.2c — Design Decisions & Style Guide](design_decisions_and_style_guide.md)
- **Grammar Reference:** [STYLE_GUIDE.md](../../../../STYLE_GUIDE.md) — authoritative CNL specification
- **Project Overview:** [README.md](../../../../README.md) — public-facing project description
- **Decision Log:** [Broader Phase 4 ADRs](../v0.4.0/SCOPE_BREAKDOWN.md#8-relationship-to-style_guidemd) — decisions affecting Phase 4 architecture docs

---

## Appendix: Example Verification (chunker.py)

**Source Code:**
```python
# src/chunker.py, lines 35–100

class DocumentChunker:
    """
    Segments documents into chunks for processing.

    Supports multiple chunking strategies:
    - fixed_size: Fixed character/token count
    - semantic: Sentence/paragraph boundaries
    - sliding_window: Overlapping windows

    Attributes:
        config: Configuration (chunk_size, overlap, strategy)
        strategy: Chunking strategy ('fixed_size', 'semantic', 'sliding_window')
    """

    def __init__(
        self,
        chunk_size: int = 512,
        overlap: int = 50,
        strategy: str = "semantic",
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize DocumentChunker."""
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.strategy = strategy
        self.config = config or {}

    def chunk(self, document: str) -> List[Chunk]:
        """Segment document into chunks.

        Args:
            document: Full document text

        Returns:
            List of Chunk objects with metadata
        """
        raise NotImplementedError(...)
```

**ARCHITECTURE.md Table Entry (What We Write):**

| Module File | Primary Class(es)/Function | Primary Responsibility | Key Inputs | Key Outputs |
|---|---|---|---|---|
| `chunker.py` | `DocumentChunker`, `Chunk` | Segment documents into semantic chunks; manage overlap and size constraints | Raw document text, config (chunk_size, overlap, strategy) | List of `Chunk` objects with text, position, token count |

**Verification:**
- ✓ Module File: `chunker.py` (exact)
- ✓ Primary Class: `DocumentChunker` (line 35)
- ✓ Dataclass: `Chunk` (line 26–32)
- ✓ Responsibility: Matches docstring (line 37–42)
- ✓ Key Inputs: chunk_size, overlap, strategy from __init__ (lines 55–60); document param from chunk() (line 78)
- ✓ Key Outputs: List[Chunk] from chunk() return type (line 78)

---

**End of v0.4.2a Specification**
