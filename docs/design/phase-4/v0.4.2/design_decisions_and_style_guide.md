# v0.4.2c — Design Decisions, Future Considerations & Style Guide Finalization

**Design Specification for ARCHITECTURE.md (Part 3/3) + STYLE_GUIDE.md Finalization**

> **Phase:** 4 — Documentation & Release
> **Version:** v0.4.2c
> **Status:** Design Specification
> **Duration:** 10–15 minutes (implementation)
> **Audience:** Technical interviewers, grammar implementers, architects
> **Deliverables:** Final sections of ARCHITECTURE.md + Finalized STYLE_GUIDE.md

---

## Document Purpose

This specification defines:

1. **Part 3 of ARCHITECTURE.md:** Design Decisions (2 key decisions with rationale and trade-offs) and Future Considerations (5 potential enhancements + scalability analysis)
2. **STYLE_GUIDE.md Finalization:** Review-and-polish pass on the existing draft, ensuring accuracy against implemented synthesizer and marking as "Final"

This is Part 3 of a 3-part ARCHITECTURE.md specification:
- **Part 1 (system_overview_and_components.md):** System Overview, Key Principles, System Components, Component Responsibilities
- **Part 2 (dataflow_and_module_reference.md):** Data Flow Documentation, Module Reference
- **Part 3 (this file):** Design Decisions, Future Considerations, Style Guide Finalization

---

## User Stories

### Story 1: Technical Interviewer Assessing Design Thinking

> As a hiring manager or technical interviewer, I want to see evidence that the author understands software architecture beyond "make it work." I'm looking for visibility into the decisions that shaped the system: Why was LLM-assisted extraction chosen over rules-based NLP? Why a custom CNL instead of existing standards like JSON-LD? These decisions should reveal the author's reasoning, their willingness to acknowledge trade-offs, and their ability to justify technical choices.

**Acceptance Criteria:**
- Design decisions are explained with clear rationale
- Trade-offs are honestly acknowledged (not glossed over)
- Alternative approaches are mentioned and evaluated
- The author understands why the chosen path was better for *this* project
- Future considerations demonstrate forward-thinking without over-engineering

### Story 2: Grammar Implementer Referencing Authoritative CNL Spec

> As a developer implementing a parser or tools for the Haiku CNL, I need STYLE_GUIDE.md to be the authoritative, complete, unambiguous specification of the grammar. I should be able to implement a parser by reading this document alone, with zero ambiguity about operators, syntax, precedence, or naming conventions. It must match the actual synthesizer implementation in v0.2.3, not a theoretical ideal.

**Acceptance Criteria:**
- All 12 operators are documented with identical names to the synthesizer
- Naming conventions exactly match the synthesizer's output (PascalCase_With_Underscores, etc.)
- BNF productions match the actual grammar (if a production is in code, it's in the spec)
- Operator precedence is correct and internally consistent
- Examples in the guide can be parsed by the actual synthesizer without error
- Document status is marked "Final" with a version number

---

## Content Specification

### Design Decisions Section (ARCHITECTURE.md Part 3.1)

**Format:** 2 design decisions, each with: Title, Context, Decision, Rationale, Trade-offs, Alternatives Considered

**Purpose:** Justify the two major architectural choices that define the system's character.

---

#### Decision 1: LLM-Assisted Entity Extraction vs. Rule-Based NLP

**Title:** "Decision 1: Why LLM-Assisted Extraction Over Rule-Based NLP"

**Context Paragraph:**
```
Entity extraction is the bridge between raw text and semantic compression. The
system must identify which parts of a document are essential (entities, relations)
and which are elaboration or filler. This extraction directly impacts compression
ratio and information retention. Two primary approaches exist: (1) rule-based NLP
using hand-crafted patterns and dependency parsing, and (2) LLM-assisted extraction
using GPT-4 or similar models guided by prompts.
```

**Decision Paragraph:**
```
The Haiku Protocol chose LLM-assisted extraction. Entity identification is performed
via an LLM (with optional fallback to SpaCy/NLTK for cost-constrained environments)
guided by carefully crafted prompts. This approach prioritizes semantic accuracy and
recall over strict determinism.
```

**Rationale Section:**

- **Semantic Accuracy:** LLMs understand context and domain knowledge. A rule-based system would struggle to recognize that "configure the database" and "set up the DB" represent the same action. LLMs handle this naturally.
- **Relation Discovery:** Extracting relationships requires understanding sentence structure and conceptual links that go beyond POS tags. LLMs excel at inferring "configure the application requires the config file to exist" as a dependency relation, which a rule system would miss or misinterpret.
- **Adaptability:** LLM approaches generalize across domains (technical docs, procedure manuals, scientific papers, regulatory text) without retraining. A rule-based system requires domain-specific patterns.
- **Information Retention:** By delegating extraction to an LLM, the system preserves more subtle semantic information (causality, temporality, conditionality) that a rule-based heuristic might lose.

**Trade-offs Section:**

- **Latency:** LLM calls add processing time (typically 500ms–2s per chunk). Rule-based extraction is near-instantaneous. This is acceptable for document compression (not real-time) but affects batch throughput.
- **Cost:** LLM API calls incur per-token charges. Large-scale compression requires budget allocation. Rule-based extraction has only one-time development cost.
- **Determinism:** LLM outputs can vary slightly between calls (despite temperature=0 attempts). Rule-based extraction is 100% deterministic. This affects reproducibility and testing.
- **Dependency:** The system requires external API access (OpenAI, Anthropic, or local LLM). Rule-based extraction has zero dependencies.

**Alternatives Considered Section:**

| Approach | Pros | Cons | Why Not Chosen |
|---|---|---|---|
| Pure Rule-Based (hand-crafted patterns) | Deterministic, fast, zero cost | Low recall, domain-specific, requires pattern engineering | Cannot generalize across document types; manually maintaining patterns is unsustainable |
| Hybrid (rules + LLM fallback) | Best-of-both (fast path + semantic accuracy) | Complex to implement and maintain | Increases complexity; adds debugging overhead; not worth it for v0.4.2 scope |
| Fine-Tuned BERT or SpaCy | Accurate, deterministic, lower cost than GPT | Requires training data; one-time setup cost; domain-specific | Training data not available; LLM approach is "good enough" for portfolio project |

**Decision Status:** FINAL — Core architectural choice, unlikely to change in v1.x.

---

#### Decision 2: Custom CNL vs. Existing Standards (JSON-LD, RDF, OWL)

**Title:** "Decision 2: Why a Custom CNL Instead of JSON-LD or RDF"

**Context Paragraph:**
```
Compression output needs a format that is: human-readable (for auditing), parseable
(for downstream processing), and efficient (to justify the compression effort). Three
candidates exist: (1) JSON-LD (JSON + linked data semantics), (2) RDF/Turtle (semantic
web standard), (3) Custom CNL (domain-optimized grammar). Each represents a different
trade-off between standardization, tooling, and compactness.
```

**Decision Paragraph:**
```
The Haiku Protocol defined a custom Controlled Natural Language (CNL) with 12
operators (Action, State, REQUIRES, EXEC, IF/THEN/ELSE, WARN, VERIFY, SEQ, REF,
META, LOOP, NOTE) and formal EBNF grammar. This custom approach was chosen to
maximize information density and readability while maintaining formal syntax.
```

**Rationale Section:**

- **Human Readability:** A statement like "Action:Deploy REQUIRES State:DB_Online -> EXEC:deploy.sh" is immediately understandable to a human and a parser. JSON-LD and RDF are more verbose and require domain knowledge to interpret.
- **Information Density:** The CNL syntax encodes relationships, dependencies, and commands compactly. "Action:X REQUIRES State:Y" is 4 tokens. The JSON-LD equivalent (`{"@context": {...}, "action": {...}, "requires": [...]}`) is 10+ tokens.
- **Operator Expressiveness:** The 12 operators were designed specifically for procedural documentation compression. REQUIRES captures dependencies, EXEC captures shell commands, VERIFY captures assertions. Existing standards are generic, losing domain specificity.
- **Parsing Simplicity:** Custom CNL can be parsed with a hand-written recursive descent parser (~200 lines). JSON-LD and RDF require external libraries and semantic reasoning. Simpler parsing = fewer dependencies, smaller deployment footprint.
- **Design Control:** A custom CNL allows the grammar to evolve with the system. Adding a new operator or syntax rule is a straightforward change. Adopting JSON-LD or RDF locks us into external standardization processes.

**Trade-offs Section:**

- **Standardization:** JSON-LD and RDF are W3C standards with ecosystem tools. Custom CNL is proprietary to this project, requiring custom parsers/tooling. The investment in learning RDF/JSON-LD transfers to other projects; custom CNL does not.
- **Interoperability:** RDF/JSON-LD documents can be queried using SPARQL, federated with other RDF datasets, and reasoned over with ontology tools. Custom CNL has no such ecosystem. For a portfolio project, this is acceptable; for enterprise adoption, this is a significant limitation.
- **Validation:** SHACL shapes and SPARQL can validate RDF/JSON-LD documents. Custom CNL requires a custom validator. The validator is implemented (v0.2.4), so this is not a blocker, but it's additional maintenance burden.
- **Extensibility:** Adding new semantics to RDF/JSON-LD is well-defined (define new predicates, add to ontology). Extending CNL requires grammar changes and parser updates. Custom CNL is less extensible by design.

**Alternatives Considered Section:**

| Approach | Pros | Cons | Why Not Chosen |
|---|---|---|---|
| JSON-LD | Standard, tool ecosystem, semantic web compatible | Verbose, requires @context, steep learning curve | Overkill for procedural docs; sacrifices density for standardization |
| RDF/Turtle | W3C standard, queryable, machine-interpretable | Complex, verbose, requires ontology engineering | Too heavyweight for a portfolio project; adds unnecessary complexity |
| XML-based Markup | Structured, validatable, hierarchical | Verbose, requires DTD/schema, parsing overhead | More verbose than CNL; JSON-LD solves the same problem better |
| Custom Text Format | Compact, human-readable, domain-optimized | Non-standard, custom parsing, no ecosystem | Chosen approach — best fit for Haiku's goals |

**Decision Status:** FINAL — This decision defines the output format and is unlikely to change.

**Note on Future:** If the project expands to require SPARQL querying or federation with RDF datasets (post-v1.0), consider an RDF export layer that converts CNL to RDF triples. This maintains the CNL-first architecture while enabling interoperability.

---

### Future Considerations Section (ARCHITECTURE.md Part 3.2)

**Format:** 5 numbered enhancements + 1 scalability table

**Purpose:** Signal that the author thinks beyond the current scope and understands growth paths without over-engineering the MVP.

---

#### Enhancement 1: Batch Processing with Parallel Execution

**Description:**
```
Current implementation processes documents sequentially. Enhancement: add
parallel processing for large batches (100+ documents). Implementation:
  - Use Python multiprocessing or asyncio for I/O-bound LLM calls
  - Implement a queue-based job processor with configurable worker pools
  - Track per-document metrics and aggregate results
  - Handle failed documents gracefully (retry, error reporting)

Technical Feasibility: HIGH
  - encoder.py already has encode_batch() method stub
  - Each document is independent; embarrassingly parallel
  - Requires minor refactoring of config management (thread-safe)

Effort: 2–3 days | Risk: Medium (concurrency bugs) | Benefit: 5–10x throughput
```

---

#### Enhancement 2: Caching Layer (Redis/SQLite)

**Description:**
```
Same document chunks produce same extracted entities and CNL statements.
Enhancement: add caching to avoid re-processing identical chunks.
Implementation:
  - Implement a chunk hash-based cache using Redis (production) or SQLite (local)
  - Cache at the extraction stage (most expensive)
  - Add cache invalidation policy (TTL, semantic change detection)
  - Measure cache hit rate and adjust strategy

Technical Feasibility: HIGH
  - Chunking is deterministic; hashing is reliable
  - Extraction is expensive; caching here has high ROI
  - Redis client libraries are mature and well-documented

Effort: 1–2 days | Risk: Low | Benefit: 2–3x faster for repeated docs
```

---

#### Enhancement 3: Custom Models (Fine-Tuned Extractors)

**Description:**
```
LLM extraction works well for general text but may underperform on specialized
domains (e.g., medical, legal, financial). Enhancement: allow fine-tuning of
entity extraction models on domain-specific corpora.
Implementation:
  - Implement a training pipeline that ingests labeled entity examples
  - Fine-tune a smaller LLM (e.g., Llama 2) on domain-specific extraction
  - Support model selection: "use GPT-4 for general, use fine-tuned-medical for medical docs"
  - Benchmark domain-specific models against GPT-4

Technical Feasibility: MEDIUM
  - Fine-tuning infrastructure exists (OpenAI API, Hugging Face)
  - Requires labeled training data (not available yet)
  - Parameter management becomes more complex

Effort: 3–5 days | Risk: Medium (training instability) | Benefit: Higher accuracy in specialized domains
```

---

#### Enhancement 4: RAG Integration with ChromaDB or Pinecone

**Description:**
```
Compressed CNL statements could be stored in a vector database to enable
retrieval-augmented generation (RAG): given a query, retrieve relevant CNL
statements and generate a response. Enhancement: integrate ChromaDB or Pinecone
as a backing store.
Implementation:
  - Generate vector embeddings for each CNL statement using sentence-transformers
  - Store CNL + embedding in vector DB
  - Implement a retrieval endpoint: query → top-k relevant statements → context for LLM
  - Add a demo interface showing RAG in action

Technical Feasibility: MEDIUM
  - Vector DB libraries are mature
  - Requires a separate service (Pinecone) or local deployment (ChromaDB)
  - Integration is straightforward but adds operational complexity

Effort: 2–3 days | Risk: Medium (query performance) | Benefit: Enables semantic search and retrieval over corpus
```

---

#### Enhancement 5: Decoder Module (CNL → Natural Language Expansion)

**Description:**
```
Currently, the system compresses documents. Enhancement: build a decoder that
expands CNL statements back into natural language. This enables a full round-trip:
document → compress → CNL → expand → expanded_document (with ~100% semantic fidelity).
Implementation:
  - Parse CNL statements using the grammar from STYLE_GUIDE.md
  - Map CNL operators to natural language templates ("Action:X" → "The system performs X")
  - Generate fluent English from templates + extracted entities
  - Benchmark round-trip fidelity (measure similarity: original → compressed → expanded)

Technical Feasibility: MEDIUM
  - Parser is straightforward (EBNF is clear)
  - Template generation is well-studied (NLG)
  - Main challenge: ensuring expanded output reads naturally

Effort: 3–4 days | Risk: Low | Benefit: Enables lossless round-trip; validates compression quality
```

---

#### Scalability Considerations Table

**Purpose:** Show how the system would handle increasing document volumes.

| Scale | Docs/Day | Processing Latency | Key Bottleneck | Mitigation Strategy |
|---|---|---|---|---|
| **100 docs/day** | Current (MVP) | ~5–10s per doc | LLM API rate limits | Sequential processing; batch calls in 10-doc chunks |
| **1000 docs/day** | 10x growth | ~1–2s per doc (with caching) | Infrastructure scaling | Parallel processing (10 workers); caching layer active; dedicated GPU for embeddings |
| **10000+ docs/day** | 100x growth | ~0.5s per doc (ideal) | Cost, concurrency | Batch API endpoints; fine-tuned local models; distributed system (queue + workers); data pipeline (Kafka) |

**Notes on Scalability:**

1. **Rate Limiting:** At 1000+ docs/day, OpenAI API rate limits become a constraint. Mitigation: (a) use Azure OpenAI for higher limits, (b) implement queuing with backoff, (c) use fine-tuned local models.

2. **Cost:** At 10000+ docs/day with GPT-4, costs approach $100–1000/day. Mitigation: (a) use cheaper models (GPT-3.5, Llama) for less critical documents, (b) implement cost-aware batching, (c) consider on-premises LLM deployment.

3. **Infrastructure:** At 100+ docs/day, a single server is sufficient. At 1000+ docs/day, consider: (a) horizontal scaling (multiple workers), (b) database for result storage (PostgreSQL), (c) message queue (RabbitMQ, Kafka).

4. **Caching ROI:** Caching becomes valuable at 1000+ docs/day when repeated documents become common. At 100 docs/day, caching overhead may exceed benefit.

---

### STYLE_GUIDE.md Finalization (Part 3.3)

**Scope:** Review-and-polish the existing STYLE_GUIDE.md draft (from Phase 0, v0.0.2c) to ensure accuracy against the implemented synthesizer (v0.2.3) and mark as "Final."

**Key Constraint:** This is finalization, NOT rewriting. The existing draft content is preserved; only corrections for accuracy and consistency are made.

---

#### Style Guide Review Checklist

**Verification Process:** For each item below, check the current STYLE_GUIDE.md against the actual synthesizer (src/synthesizer.py) and supporting files.

| Item | Location in STYLE_GUIDE.md | What to Verify | Source(s) to Check |
|---|---|---|---|
| **Operator Count** | Grammar Overview section | "12 operators" — are all 12 documented? | src/synthesizer.py, STYLE_GUIDE.md Operator Quick Reference table |
| **Operator Names** | Operator Quick Reference table | Each operator name matches actual synthesizer implementation | src/synthesizer.py code + docstring; look for references to "Action:", "State:", "REQUIRES", etc. |
| **Operator Symbols** | Operator Quick Reference table | Symbols (e.g., "->", "REQUIRES", ";") match actual grammar | research/haiku_grammar.bnf (if exists) or STYLE_GUIDE.md BNF section |
| **Operator Precedence** | Operator Quick Reference table | Precedence numbers (1–10) are correct and internally consistent | STYLE_GUIDE.md Ambiguity Resolution section (rules 1–5) |
| **Naming Convention: Identifiers** | Naming Conventions section | "PascalCase_With_Underscores" examples match actual synthesizer output | src/synthesizer.py; check example outputs in tests or docstrings |
| **Naming Convention: Commands** | Naming Conventions section | "lowercase shell syntax" for EXEC clauses | STYLE_GUIDE.md example: "EXEC:docker build -t myapp:latest ." |
| **Naming Convention: Metadata** | Naming Conventions section | "lowercase_with_underscores" for META keys | STYLE_GUIDE.md example: "META:compatible_with=PostgreSQL_12+" |
| **Composition Rules (8 rules)** | Composition Rules section | All 8 rules are implemented and correctly described | STYLE_GUIDE.md rules 1–8; verify against synthesizer logic |
| **Encoding Examples (3 examples)** | Encoding Examples section | Each example's CNL output could be parsed by the actual synthesizer | Try parsing each example's "After" output; verify it's valid CNL |
| **Ambiguity Resolution Rules (5 rules)** | Ambiguity Resolution section | Rules 1–5 match actual parsing precedence | STYLE_GUIDE.md; cross-check with synthesizer implementation |
| **BNF Grammar Reference** | Related Documents / "Formal Grammar" link | BNF file exists and is complete | research/haiku_grammar.bnf (or reference path is correct) |
| **Operator Reference Link** | Related Documents / "Operator Reference" link | operator_reference.md exists and is comprehensive | research/operator_reference.md (or reference path is correct) |

---

#### Accuracy Verification Instructions

**For Each Operator in the Quick Reference Table:**

1. Open the STYLE_GUIDE.md Operator Quick Reference table
2. For each operator (Action, State, REQUIRES, etc.):
   - Find the operator name in src/synthesizer.py
   - Verify the symbol/syntax matches (e.g., "Action:" in code)
   - Check the description matches what the synthesizer actually does
   - Verify precedence value is consistent with parsing rules

**Example Verification (Action operator):**
```
STYLE_GUIDE.md states:
  | Action | `Action:` / `A:` | Procedural step (imperative verb) | 5 |

Check:
  - src/synthesizer.py docstring mentions "Action:" prefix ✓
  - Precedence 5 is higher than State (6)? No, should be same or higher.
    Look at composition rules to verify precedence makes sense.
  - Description "Procedural step (imperative verb)" matches synthesizer design ✓
```

**For Composition Rules:**

1. Read each rule (1–8)
2. Find a test case or example that exercises that rule
3. Verify the rule description is accurate

**Example (Rule 1: Sequential Composition):**
```
Rule 1 states: "Statements compose left-to-right with semicolons."
Example: "Action:Backup; Action:Deploy; VERIFY:Running"
Verification: Is semicolon really the separator? Check synthesizer code.
              Do statements execute left-to-right? Check STYLE_GUIDE.md examples.
```

---

#### Corrections and Adjustments

**During Review, if Discrepancies Are Found:**

| Discrepancy | Action |
|---|---|
| Operator listed in STYLE_GUIDE but not in synthesizer | Remove from STYLE_GUIDE (or add to synthesizer if it's a missing feature) |
| Operator in synthesizer but not documented in STYLE_GUIDE | Add to STYLE_GUIDE with accurate description and precedence |
| Symbol mismatch (e.g., STYLE_GUIDE says "->" but code uses "=>") | Update STYLE_GUIDE to match actual code |
| Precedence mismatch | Recalculate precedence based on parsing rules; update both STYLE_GUIDE and code comments |
| Example output is invalid CNL | Correct the example or correct the synthesizer (prefer correcting example for Phase 4) |
| Naming convention describes ideal but code produces something different | Update STYLE_GUIDE to match actual behavior |

**Example Scenario:**
```
STYLE_GUIDE.md says: "Action identifiers use PascalCase_With_Underscores"
But synthesizer outputs: "Action:backup_database" (all lowercase)
Resolution: Update STYLE_GUIDE to document actual behavior
            OR update synthesizer to follow convention (unlikely in Phase 4)
            Prefer: Update STYLE_GUIDE (Phase 4 does not modify src/)
```

---

#### Final Status Marker

**Current Status (in draft):**
```
> **Status:** Draft (v0.0.2c)
```

**Update To:**
```
> **Status:** Final (v1.0.0)
```

**Rationale for Status Change:**
- All 12 operators documented and verified against synthesizer
- Naming conventions match actual implementation
- BNF grammar is complete and correct
- Composition rules are tested and accurate
- Document is ready for public use (open-source release)

---

## Acceptance Criteria

### Design Decisions Criteria

1. Exactly two design decisions documented
2. Decision 1 is about LLM-assisted vs. rule-based extraction
3. Decision 2 is about custom CNL vs. JSON-LD/RDF
4. Each decision has: Context, Decision, Rationale, Trade-offs, Alternatives Considered
5. Context paragraph explains the problem space
6. Decision paragraph clearly states what was chosen
7. Rationale section has 3–5 bullet points with concrete reasons
8. Trade-offs section honestly acknowledges downsides (no sugar-coating)
9. Alternatives table has 3–4 rows with Pros, Cons, Why Not Chosen
10. Decision status is marked FINAL
11. Each decision reflects actual architectural choices (not hypothetical)
12. Both decisions are traceable to actual code decisions

### Future Considerations Criteria

13. Exactly five enhancements documented (1–5)
14. Each enhancement has: Description, Technical Feasibility, Effort estimate, Risk level, Benefit
15. Technical Feasibility is rated HIGH/MEDIUM/LOW with justification
16. Effort estimate is realistic (1–5 days, not "TBD" or "unknown")
17. Risk level is assigned (Low/Medium/High) with rationale
18. Benefit describes the value (throughput, accuracy, cost savings, etc.)
19. All enhancements are technically feasible (not fantasy)
20. Enhancements build on current architecture (not rewrites)
21. Scalability table has three scale tiers (100, 1000, 10000+ docs/day)
22. Each tier shows: docs/day, latency, bottleneck, mitigation strategy
23. Scalability notes include considerations for rate-limiting, cost, infrastructure, caching

### STYLE_GUIDE.md Finalization Criteria

24. Review Checklist is completed (all items verified)
25. All 12 operators are documented in the Quick Reference table
26. Operator names match synthesizer implementation exactly
27. Operator symbols match actual syntax (e.g., "->" in code)
28. Operator descriptions match synthesizer behavior
29. Operator precedence is correct and internally consistent
30. All eight Composition Rules are documented and accurate
31. Naming conventions match actual synthesizer output (PascalCase_With_Underscores, lowercase, etc.)
32. All three Encoding Examples produce valid CNL that can be parsed
33. Ambiguity Resolution rules (1–5) match actual parsing precedence
34. Related Documents links are valid (BNF grammar, operator reference, pattern taxonomy)
35. Document status is updated from "Draft (v0.0.2c)" to "Final (v1.0.0)"
36. No grammar or spelling errors
37. Markdown renders correctly on GitHub

### Cross-Document Criteria

38. Design decisions in ARCHITECTURE.md are referenced in the decision log
39. Future considerations are realistic and achievable (not fantasy enhancements)
40. Scalability table is consistent with encoder.py's design (can actually handle these scales)
41. STYLE_GUIDE.md examples use operators mentioned in future considerations
42. All document sections are internally consistent (no contradictions)

---

## Content Accuracy Requirements

### Design Decisions Verification

For Decision 1 (LLM-assisted extraction):

| Claim | Source | Verification Method |
|---|---|---|
| "Entity extraction is LLM-assisted" | `src/extractor.py` docstring | Read class docstring; verify it mentions LLM/NLP model |
| "LLM approach prioritizes semantic accuracy" | Design rationale | Review actual synthesizer behavior; does it achieve high semantic similarity? |
| "Latency is 500ms–2s per chunk" | Performance characteristics | Check benchmark results or test output; are LLM calls indeed slow? |
| "Determinism trade-off is real" | Actual behavior | Does encode(same_doc) sometimes produce different results? Test it. |

For Decision 2 (Custom CNL vs. JSON-LD):

| Claim | Source | Verification Method |
|---|---|---|
| "12 operators in custom CNL" | `STYLE_GUIDE.md` Quick Reference | Count operators in table; verify exact 12 |
| "JSON-LD is verbose" | Example comparison | Create an equivalent JSON-LD statement; count tokens; compare to CNL |
| "RDF requires external tools" | Domain knowledge | Verify this is true; RDF does require SPARQL, ontologies, etc. |
| "Custom CNL parser is ~200 lines" | Code inspection | Write or estimate parser size; is it reasonable? |

### STYLE_GUIDE.md Finalization Verification

For Each Operator:

1. Find the operator in STYLE_GUIDE.md Quick Reference table
2. Search for that operator in src/synthesizer.py
3. Verify the name, symbol, and description match
4. Confirm it's used in actual CNL examples

**Example (REQUIRES operator):**
```
STYLE_GUIDE.md:
  | REQUIRES | `REQUIRES` | Dependency declaration | 7 |

Check src/synthesizer.py:
  - Does synthesizer output "REQUIRES" clauses? YES (in docstring examples)
  - Is "Dependency declaration" accurate? YES (prevents action unless conditions met)
  - Is precedence 7 correct? Check Ambiguity Resolution rules

Result: ✓ Operator documented correctly
```

---

## Dependencies

### Input Artifacts

| Artifact | Source | Purpose |
|---|---|---|
| `synthesizer.py` | Phase 2 (v0.2.3) | Source for operator definitions and actual grammar implementation |
| `validator.py` | Phase 2 (v0.2.4) | Validator implements some CNL semantics; cross-check for consistency |
| `STYLE_GUIDE.md` (draft) | Phase 0 (v0.0.2c) | Existing draft to be finalized (not rewritten) |
| `haiku_grammar.bnf` | Research (v0.0.2c) | BNF specification; verify STYLE_GUIDE.md matches this |
| `operator_reference.md` | Research | Referenced in STYLE_GUIDE.md; verify it exists and is comprehensive |
| Benchmark results | Phase 3 (v0.3.3) | Design decisions should reference actual performance characteristics |

### Output Artifacts

| Artifact | Purpose |
|---|---|
| Design Decisions and Future Considerations sections (draft) | Final sections of ARCHITECTURE.md |
| Finalized STYLE_GUIDE.md | Complete, accurate CNL specification for public release |

---

## Decision Log

### D-v0.4.2c-001: Two Design Decisions From Broader ADR Catalog

**Decision:** ARCHITECTURE.md documents two specific design decisions (LLM-assisted extraction, custom CNL) chosen from a broader architectural decision record (ADR) catalog. These two were selected because they have the highest impact on the public API and user experience.

**Rationale:**
- A complete ADR catalog would include 10+ decisions (async vs sync, caching strategy, error handling, deployment model, etc.)
- ARCHITECTURE.md is not the place for exhaustive ADR documentation
- Two high-impact decisions are sufficient to demonstrate design thinking
- The README-level audience (hiring managers, technical reviewers) cares most about core decisions

**Trade-off:**
- Other design decisions (caching strategy, error handling, deployment) are not visible in ARCHITECTURE.md
- Readers may miss nuance in secondary decisions
- But this keeps ARCHITECTURE.md focused and readable

**Decision Status:** FINAL — These two decisions are the ones to document.

---

### D-v0.4.2c-002: Scalability Table Uses Round Numbers for Readability

**Decision:** The scalability table (100, 1000, 10000+ docs/day) uses convenient round numbers rather than realistic projections based on current infrastructure.

**Rationale:**
- Round numbers (100, 1000, 10000) are easier to remember and compare
- Realistic numbers would require assumptions about infrastructure, costs, and API quotas (which vary)
- The table's purpose is to show "growth considerations," not precise predictions
- Round numbers still convey the scaling challenges and mitigation strategies

**Trade-off:**
- The numbers don't exactly match real-world deployment targets
- Readers may mistake these for performance guarantees or projections
- But for a portfolio project, round numbers are acceptable

**Decision Status:** FINAL — Use 100/1000/10000 tiers.

---

### D-v0.4.2c-003: Style Guide Finalization is Review-and-Polish, Not Rewrite

**Decision:** The STYLE_GUIDE.md finalization process is a review-and-polish pass, not a rewrite. Existing content is preserved; only corrections for accuracy and consistency are applied.

**Rationale:**
- A rewrite would contradict the Phase 4 "documentation only" constraint
- The existing STYLE_GUIDE.md draft (v0.0.2c) is well-structured and comprehensive
- Phase 4's role is to verify accuracy against implemented synthesizer, not redesign the grammar
- The grammar itself (12 operators, composition rules, naming conventions) is stable

**Trade-off:**
- If the draft contains fundamental errors, they remain (unless they're documented in code)
- The document reflects the current implementation, not an ideal design
- But this honesty is appropriate for a public specification

**Decision Status:** FINAL — No rewrites; accuracy corrections only.

---

## Quality Checklist

### Pre-Publication Checklist

#### Design Decisions

- [ ] Decision 1 title: "Why LLM-Assisted Extraction Over Rule-Based NLP"
- [ ] Decision 1 has Context, Decision, Rationale (3–5 bullets), Trade-offs, Alternatives table
- [ ] Decision 2 title: "Why a Custom CNL Instead of JSON-LD or RDF"
- [ ] Decision 2 has Context, Decision, Rationale (3–5 bullets), Trade-offs, Alternatives table
- [ ] Each Rationale section lists 3–5 concrete reasons with explanation
- [ ] Each Trade-offs section honestly acknowledges 2–4 downsides
- [ ] Each Alternatives table has 3–4 rows with Pros, Cons, Why Not Chosen columns
- [ ] Both decisions are marked "Decision Status: FINAL"
- [ ] Both decisions reference actual code or architectural choices
- [ ] No aspirational language ("would allow," "should enable") — present tense only
- [ ] Alternatives table explains why the chosen path was better

#### Future Considerations

- [ ] Exactly five enhancements documented (numbered 1–5)
- [ ] Enhancement 1: Batch Processing with Parallel Execution
- [ ] Enhancement 2: Caching Layer (Redis/SQLite)
- [ ] Enhancement 3: Custom Models (Fine-Tuned Extractors)
- [ ] Enhancement 4: RAG Integration with ChromaDB
- [ ] Enhancement 5: Decoder Module (CNL → Natural Language)
- [ ] Each enhancement has: Description, Technical Feasibility, Effort, Risk, Benefit
- [ ] Technical Feasibility is rated HIGH/MEDIUM/LOW with justification
- [ ] Effort is realistic (1–5 days) and detailed
- [ ] Risk level assigned (Low/Medium/High)
- [ ] Benefit describes real value (throughput, accuracy, cost, capability)
- [ ] All enhancements are technically feasible (not fantasy features)
- [ ] Scalability table has three tiers: 100, 1000, 10000+ docs/day
- [ ] Each tier shows: Processing Latency, Key Bottleneck, Mitigation Strategy
- [ ] Scalability notes cover rate-limiting, cost, infrastructure, caching considerations
- [ ] All numbers are realistic (even if using round figures)

#### STYLE_GUIDE.md Finalization

- [ ] Review Checklist is completed (all items checked)
- [ ] Quick Reference table verified against synthesizer: all operator names match
- [ ] Quick Reference table verified against synthesizer: all symbols match (e.g., "->" is correct)
- [ ] Quick Reference table verified against synthesizer: descriptions match behavior
- [ ] Operator Precedence values (1–10) are correct and internally consistent
- [ ] All eight Composition Rules (Rules 1–8) are present and accurate
- [ ] Naming Conventions section verified:
  - [ ] PascalCase_With_Underscores examples match actual synthesizer output
  - [ ] lowercase shell syntax examples are correct
  - [ ] lowercase_with_underscores examples are correct
- [ ] All three Encoding Examples are valid CNL (could be parsed by synthesizer)
- [ ] Ambiguity Resolution section (Rules 1–5) matches actual parsing precedence
- [ ] Related Documents links are valid (point to real files/resources)
- [ ] Status updated from "Draft (v0.0.2c)" to "Final (v1.0.0)"
- [ ] No grammar or spelling errors in entire document
- [ ] Markdown renders correctly on GitHub
- [ ] Document is self-contained (reader needs no external reference)

#### Cross-Document Consistency

- [ ] Design Decisions in ARCHITECTURE.md align with actual implementation choices
- [ ] Future Considerations are realistic and technically feasible
- [ ] Scalability table is consistent with encoder.py's architecture
- [ ] STYLE_GUIDE.md examples use only operators listed in Quick Reference
- [ ] No contradictions between ARCHITECTURE.md and STYLE_GUIDE.md
- [ ] All three parts of ARCHITECTURE.md (Parts 1, 2, 3) reference each other correctly
- [ ] Decision Log entries are accurate and complete

---

## Implementation Notes

### For the Implementer

#### Writing Design Decisions

1. **Do not invent decisions.** Both design decisions must be traceable to actual code choices. If the system doesn't use LLM extraction, don't claim it does.

2. **Be honest about trade-offs.** If the chosen approach is slower, say so. If it's more expensive, acknowledge it. Credibility comes from honesty, not spin.

3. **Explain the reasoning.** A reader should understand not just what was chosen, but why it was better than the alternatives for this specific project.

4. **Verify with code.** Before writing a decision, search the source code and tests to confirm the choice was actually made.

#### Writing Future Considerations

1. **Realistic enhancements.** Each enhancement should be a natural extension of the current system, not a complete redesign. "Batch processing" is realistic. "Rewrite in Rust" is not.

2. **Feasibility justification.** For each enhancement, ask: "Could I implement this in 1–5 days with the team's current skills?" If the answer is "no," it's not ready for Future Considerations.

3. **Effort estimates.** Be honest. If fine-tuning a model would take a week of experimentation, say "3–5 days" not "1 day." Underestimating is worse than overestimating.

4. **Risk assessment.** Assign a risk level (Low/Medium/High) and explain it. Parallelization has Medium risk (concurrency bugs). Caching has Low risk (well-understood problem).

#### Finalizing STYLE_GUIDE.md

1. **Verify every operator.** For each of the 12 operators in the Quick Reference table:
   - Find it in src/synthesizer.py
   - Verify the name is exact (including case and punctuation)
   - Verify the symbol is exact (e.g., "->", "REQUIRES")
   - Verify the description matches actual behavior

2. **Test examples.** For each of the three Encoding Examples:
   - Try to parse the "After" output using the grammar
   - Does it parse without errors?
   - Does it produce the intended statement?

3. **Check consistency.** Verify that:
   - Operator precedence in the table matches the Ambiguity Resolution rules
   - Naming conventions match actual synthesizer output
   - Composition rules don't contradict each other

4. **Update status.** Change the status marker from "Draft (v0.0.2c)" to "Final (v1.0.0)".

---

## Related Documents

- **Part 1 Specification:** [v0.4.2a — System Overview & Components](system_overview_and_components.md)
- **Part 2 Specification:** [v0.4.2b — Data Flow & Module Reference](dataflow_and_module_reference.md)
- **Authoritative Scope:** [v0.4.0 SCOPE_BREAKDOWN.md](../v0.4.0/SCOPE_BREAKDOWN.md) — section 8 defines Style Guide finalization
- **Existing Style Guide (to be finalized):** [STYLE_GUIDE.md](../../../../STYLE_GUIDE.md)
- **Synthesizer Source (for verification):** [src/synthesizer.py](../../../../src/synthesizer.py)
- **Grammar Spec (for BNF reference):** [research/haiku_grammar.bnf](../../../../research) (if exists)

---

## Appendix: Operator Verification Template

**Use this template for each operator in the Quick Reference table:**

```markdown
### Operator: [Name]

**Quick Reference Entry:**
| Operator | Symbol | Purpose | Precedence |
|[name] | [symbol] | [purpose] | [precedence] |

**Verification Checklist:**
- [ ] Operator name appears in src/synthesizer.py docstring or code
- [ ] Symbol matches actual synthesizer output (e.g., "Action:" not "act:")
- [ ] Description matches synthesizer behavior
- [ ] Precedence is consistent with Ambiguity Resolution rules
- [ ] At least one Composition Rule or Example uses this operator

**Verification Results:**
[VERIFIED] or [NEEDS CORRECTION]

**Notes:**
[Any discrepancies or clarifications]
```

---

**End of v0.4.2c Specification**
