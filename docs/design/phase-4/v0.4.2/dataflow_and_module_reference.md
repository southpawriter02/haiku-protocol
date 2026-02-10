# v0.4.2b — Data Flow Documentation & Module Reference

**Design Specification for ARCHITECTURE.md (Part 2/3)**

> **Phase:** 4 — Documentation & Release
> **Version:** v0.4.2b
> **Status:** Design Specification
> **Duration:** 10–15 minutes (implementation)
> **Audience:** Developers tracing documents through the pipeline; code reviewers
> **Deliverable:** Data Flow and Module Reference sections of ARCHITECTURE.md

---

## Document Purpose

This specification defines the **Data Flow Documentation** and **Module Reference** sections of the final `ARCHITECTURE.md`. These sections provide the "how it works" level of detail: the stage-by-stage transformation of data as it moves through the pipeline, concrete examples of data shapes at each stage, and the public API surface for each module.

This is Part 2 of a 3-part ARCHITECTURE.md specification:
- **Part 1 (system_overview_and_components.md):** System Overview, Key Principles, System Components, Component Responsibilities
- **Part 2 (this file):** Data Flow Documentation, Module Reference, Data Shape Verification
- **Part 3 (design_decisions_and_style_guide.md):** Design Decisions, Future Considerations, Style Guide Finalization

---

## User Stories

### Story 1: Developer Tracing a Document Through the Pipeline

> As a developer integrating the Haiku Protocol into my application, I need to understand what data shapes flow between stages. If I have a raw document, I need to know: what does the chunker output? What does the extractor expect as input and what does it output? What's the format of CNL statements from the synthesizer? I should be able to mentally trace a 5-sentence paragraph from input to compressed output without reading source code.

**Acceptance Criteria:**
- Each pipeline stage is documented with input and output data shapes
- Data shapes are shown as concrete examples (e.g., actual Chunk object structure, not just "list of chunks")
- Stage descriptions include one or two realistic examples
- I can understand the data format at each boundary
- No ambiguity about what the next stage expects

### Story 2: Code Reviewer Understanding Public API Surface

> As a code reviewer or open-source contributor, I want to know the public API of each module without reading implementation details. I need: function/class names, parameters, return types, and a one-sentence description. This helps me understand what I can call and what I must not depend on (because it's internal).

**Acceptance Criteria:**
- Each public module has a reference section with primary classes/functions
- Function signatures show parameter types and return types
- Only public API is documented (no private methods, no `_internal_` functions)
- One-sentence description for each signature
- Follows abbreviated signature format (not exhaustive docstring)

---

## Content Specification

### Data Flow Documentation Section

**Format:** Four-part walkthrough with textual descriptions and inline code blocks

**Purpose:** Trace a single document through each stage of the pipeline, showing input/output at each boundary.

**Stage 1: Input Validation and Chunking**

**Title:** "Stage 1: Document Input → Chunking"

**Description Paragraph:**
```
The pipeline begins with raw document text. The HaikuEncoder receives the
document and immediately delegates to the DocumentChunker. The chunker
segments the document based on its configured strategy (semantic, fixed-size,
or sliding-window) and returns a list of Chunk objects. Each Chunk contains
the segment text, metadata (position in original document), and token count.
```

**Input Example:**
```
Input Type: str (raw document text)
Example Input:
  "# Configuration Management

   To configure the application, you must first ensure that the configuration
   file is present in the designated directory. Then, you can load the
   configuration using the load_config function."
```

**Processing Activity:**
```
Processing: DocumentChunker.chunk(document_text)
  • Strategy applied: "semantic" (split on paragraphs/sentences)
  • Chunk size target: 512 characters
  • Overlap: 50 characters between adjacent chunks
```

**Output Example:**
```
Output Type: List[Chunk] where Chunk is:
  Chunk(
    text="# Configuration Management\n\nTo configure the application, you must
           first ensure that the configuration file is present in the designated
           directory.",
    chunk_id=0,
    start_char=0,
    end_char=187,
    token_count=34
  )
```

---

**Stage 2: Entity Extraction**

**Title:** "Stage 2: Chunked Text → Entity Extraction"

**Description Paragraph:**
```
The Chunk text is passed to the EntityExtractor, which uses an LLM and NLP
techniques to identify key entities (nouns, verbs, relations) and their
relationships. The extractor returns an ExtractedEntities object containing
a list of Entity objects (each with text, type, and confidence) and a
relations dictionary mapping relationships to entity pairs.
```

**Input Example:**
```
Input Type: str (from Chunk.text) and int (chunk_id)
Example Input:
  chunk_text = "To configure the application, you must first ensure that the
                configuration file is present in the designated directory."
  chunk_id = 0
```

**Processing Activity:**
```
Processing: EntityExtractor.extract(chunk_text, chunk_id)
  • NLP Model: en_core_web_sm (SpaCy)
  • Confidence Threshold: 0.7
  • Techniques: POS tagging, dependency parsing, NER
  • Identified entities:
    - "configure" (VERB, confidence=0.95)
    - "application" (NOUN, confidence=0.92)
    - "configuration file" (NOUN, confidence=0.88)
    - "directory" (NOUN, confidence=0.91)
```

**Output Example:**
```
Output Type: ExtractedEntities containing:
  entities = [
    Entity(text="configure", entity_type="VERB", confidence=0.95, position=3),
    Entity(text="application", entity_type="NOUN", confidence=0.92, position=29),
    Entity(text="configuration file", entity_type="NOUN", confidence=0.88, position=65),
    Entity(text="directory", entity_type="NOUN", confidence=0.91, position=128)
  ]
  relations = {
    "require_presence": ["configuration file", "directory"],
    "action_on": ["configure", "application"]
  }
  chunk_id = 0
```

---

**Stage 3: CNL Synthesis**

**Title:** "Stage 3: Entities & Relations → CNL Synthesis"

**Description Paragraph:**
```
The entities and relations are passed to the CNLSynthesizer, which applies
formal grammar rules from the STYLE_GUIDE.md specification. The synthesizer
generates CNL statements using the 12 operators (Action, State, REQUIRES,
EXEC, IF/THEN/ELSE, WARN, VERIFY, SEQ, REF, META, LOOP, NOTE). The output
is a single CNL statement (string) that encodes the entities and their
relationships according to formal grammar.
```

**Input Example:**
```
Input Type: List[Dict[str, Any]] (entities), Dict[str, List[str]] (relations)
Example Input:
  entities = [
    {"text": "configure", "type": "VERB"},
    {"text": "application", "type": "NOUN"},
    {"text": "configuration file", "type": "NOUN"}
  ]
  relations = {
    "require_presence": ["configuration file", "directory"],
    "action_on": ["configure", "application"]
  }
```

**Processing Activity:**
```
Processing: CNLSynthesizer.synthesize(entities, relations)
  • Grammar source: STYLE_GUIDE.md (BNF specification)
  • Operators applied: Action, State, REQUIRES
  • Template matching: Finding the best operators for entity types
  • Output formatting: Ensuring unambiguous, parseable syntax
```

**Output Example:**
```
Output Type: str (CNL-formatted statement)
Example Output:
  "Action:Configure_Application REQUIRES State:Config_File_Present -> EXEC:load_config;
   VERIFY:Application_Ready"
```

---

**Stage 4: Validation and Metrics**

**Title:** "Stage 4: CNL → Validation & Metrics"

**Description Paragraph:**
```
The synthesized CNL statement is passed to the HaikuValidator, which performs
two tasks. First, it validates the CNL syntax against the grammar rules from
STYLE_GUIDE.md, ensuring the output is unambiguous and parseable. Second, it
computes compression metrics by comparing the original text and compressed
output: compression ratio, token counts, semantic similarity, and information
retention. These metrics are collected in a CompressionMetrics object.
```

**Input Example:**
```
Input Type: str (original document), str (compressed CNL)
Example Input:
  original = "To configure the application, you must first ensure that the
              configuration file is present in the designated directory..."
  compressed = "Action:Configure_Application REQUIRES State:Config_File_Present
                -> EXEC:load_config; VERIFY:Application_Ready"
```

**Processing Activity:**
```
Processing: HaikuValidator.compute_metrics(original, compressed)
  • Token counting: Using tiktoken (OpenAI's tokenizer)
  • Semantic similarity: Cosine similarity of sentence embeddings
  • Information retention: Compared against baseline (e.g., LLMLingua)

  Computed metrics:
    - original_tokens: 28
    - compressed_tokens: 12
    - compression_ratio: (28 - 12) / 28 = 0.571 (57.1% reduction)
    - semantic_similarity: 0.89 (embeddings cosine similarity)
    - information_retention: 0.92 (92% of key facts preserved)
    - processing_time_ms: 1240
```

**Output Example:**
```
Output Type: CompressionMetrics dataclass
CompressionMetrics(
  compression_ratio=0.571,
  original_tokens=28,
  compressed_tokens=12,
  semantic_similarity=0.89,
  information_retention=0.92,
  processing_time_ms=1240
)
```

---

### Data Shape Verification Table

**Format:** 4-column table showing each stage's input type, output type, and verification status

**Purpose:** Provide a quick reference for developers; confirm all data shapes match actual types in the code.

| Stage | Input Type | Output Type | Verified Against |
|---|---|---|---|
| Input | `str` (raw document) | — | encoder.py `encode()` parameter |
| Chunking | `str` | `List[Chunk]` | chunker.py `chunk()` return type, Chunk dataclass |
| Extraction | `str`, `int` | `ExtractedEntities` | extractor.py `extract()` return type, ExtractedEntities dataclass |
| Synthesis | `List[Dict[str, Any]]`, `Dict[str, List[str]]` | `str` | synthesizer.py `synthesize()` return type and parameters |
| Validation | `str`, `str` | `CompressionMetrics` | validator.py `compute_metrics()` return type, CompressionMetrics dataclass |

**Accuracy Requirements:**
- **Input Type:** Exactly matches the first parameter to the stage's primary method
- **Output Type:** Exactly matches the return type annotation in source code
- **Verified Against:** Points to specific line/method in source file where type is defined
- **All types are from actual code, not paraphrased or guessed**

---

### Module Reference Section

**Format:** Subsection for each module with:
1. Module name
2. Primary class/function signatures
3. Parameter and return type information
4. One-sentence description
5. Example usage (optional, brief)

**Purpose:** Provide a public API reference without reading docstrings or implementation.

---

#### Module: encoder.py

**Primary Class:** `HaikuEncoder`

**Primary Methods:**

**Method 1: `encode()`**
```
Signature:
  def encode(self, document: str) -> str

Parameters:
  document (str): Raw document text to compress

Returns:
  str: CNL-formatted compressed text

Description:
  Orchestrates the complete compression pipeline (chunking, extraction,
  synthesis, validation) and returns the compressed CNL output.

Example:
  >>> encoder = HaikuEncoder()
  >>> cnl = encoder.encode("Long document text...")
  >>> print(cnl)  # [CNL: ...]
```

**Method 2: `encode_with_metrics()`**
```
Signature:
  def encode_with_metrics(self, document: str, include_timing: bool = True)
    -> tuple

Parameters:
  document (str): Raw document text to compress
  include_timing (bool, optional): Whether to include processing time in metrics
                                   (default: True)

Returns:
  tuple: (compressed_cnl: str, metrics: CompressionMetrics)

Description:
  Compresses a document and returns both the CNL output and detailed
  compression metrics (ratio, semantic similarity, information retention).

Example:
  >>> cnl, metrics = encoder.encode_with_metrics("Long doc...")
  >>> print(f"Compression: {metrics.compression_ratio:.1%}")
```

**Method 3: `encode_batch()`**
```
Signature:
  def encode_batch(self, documents: List[str]) -> List[str]

Parameters:
  documents (List[str]): List of documents to compress

Returns:
  List[str]: List of compressed CNL outputs (order preserved)

Description:
  Compresses multiple documents in batch, potentially using parallel
  processing. Returns one CNL output per input document.
```

---

#### Module: chunker.py

**Primary Class:** `DocumentChunker`

**Constructor:**
```
Signature:
  def __init__(self, chunk_size: int = 512, overlap: int = 50,
               strategy: str = "semantic",
               config: Optional[Dict[str, Any]] = None)

Parameters:
  chunk_size (int, optional): Target chunk size in characters or tokens
                              (default: 512)
  overlap (int, optional): Overlapping characters between consecutive chunks
                          (default: 50)
  strategy (str, optional): Chunking strategy ('fixed_size', 'semantic',
                           'sliding_window') (default: 'semantic')
  config (Optional[Dict[str, Any]], optional): Additional configuration

Description:
  Initializes the chunker with a segmentation strategy and size parameters.
```

**Primary Method: `chunk()`**
```
Signature:
  def chunk(self, document: str) -> List[Chunk]

Parameters:
  document (str): Full document text to segment

Returns:
  List[Chunk]: List of chunk objects with metadata

Description:
  Segments a document into semantic chunks respecting size constraints and
  overlaps. Returns metadata including position, token count, and chunk ID.

Example:
  >>> chunker = DocumentChunker(chunk_size=512, strategy='semantic')
  >>> chunks = chunker.chunk("Long document...")
  >>> for chunk in chunks:
  ...     print(f"Chunk {chunk.chunk_id}: {chunk.token_count} tokens")
```

**Data Class: `Chunk`**
```
Signature:
  @dataclass
  class Chunk:
    text: str
    chunk_id: int
    start_char: int
    end_char: int
    token_count: int

Description:
  Represents a single document segment with position and token metadata.
```

---

#### Module: extractor.py

**Primary Class:** `EntityExtractor`

**Constructor:**
```
Signature:
  def __init__(self, model: str = "en_core_web_sm",
               confidence_threshold: float = 0.7,
               config: Optional[Dict[str, Any]] = None)

Parameters:
  model (str, optional): NLP model name (e.g., SpaCy model identifier)
                        (default: 'en_core_web_sm')
  confidence_threshold (float, optional): Minimum confidence score for
                                         entity extraction (0.0 to 1.0)
                                         (default: 0.7)
  config (Optional[Dict[str, Any]], optional): Additional configuration

Description:
  Initializes the extractor with an NLP model and confidence threshold.
```

**Primary Method: `extract()`**
```
Signature:
  def extract(self, chunk_text: str, chunk_id: int = 0) -> ExtractedEntities

Parameters:
  chunk_text (str): Text from a document chunk
  chunk_id (int, optional): Index of the chunk for tracking (default: 0)

Returns:
  ExtractedEntities: Object containing entities list and relations dictionary

Description:
  Extracts key entities (nouns, verbs, relations) from chunk text using NLP
  techniques (POS tagging, dependency parsing, NER).

Example:
  >>> extractor = EntityExtractor()
  >>> extracted = extractor.extract("Alice uses Python.", chunk_id=0)
  >>> print(extracted.entities)  # [Entity(...), Entity(...)]
  >>> print(extracted.relations)  # {"uses": ["Alice", "Python"]}
```

**Data Class: `Entity`**
```
Signature:
  @dataclass
  class Entity:
    text: str
    entity_type: str  # e.g., "NOUN", "VERB", "ENTITY", "RELATION"
    confidence: float
    position: int

Description:
  Represents a single extracted entity with its type, confidence score,
  and position in the source text.
```

**Data Class: `ExtractedEntities`**
```
Signature:
  @dataclass
  class ExtractedEntities:
    entities: List[Entity]
    chunk_id: int
    relations: Dict[str, List[str]]

Description:
  Container for all entities extracted from a single chunk, including
  relationships mapped as {relation_name: [entity1, entity2, ...]}.
```

---

#### Module: synthesizer.py

**Primary Class:** `CNLSynthesizer`

**Constructor:**
```
Signature:
  def __init__(self, config: Optional[Dict[str, Any]] = None)

Parameters:
  config (Optional[Dict[str, Any]], optional): Configuration including
                                              grammar rules, model name
                                              (default: None)

Description:
  Initializes the synthesizer with CNL grammar rules from STYLE_GUIDE.md.
```

**Primary Method: `synthesize_cnl()` OR `synthesize()`**
```
Signature:
  def synthesize(self, entities: List[Dict[str, Any]],
                relations: Dict[str, List[str]]) -> str

Parameters:
  entities (List[Dict[str, Any]]): List of extracted entities with metadata
  relations (Dict[str, List[str]]): Relationships between entities
                                   (e.g., {"uses": ["A", "B"]})

Returns:
  str: CNL-formatted statement

Description:
  Generates CNL-formatted statements from entities and relations by applying
  grammar rules from STYLE_GUIDE.md. Output follows the 12-operator CNL
  specification.

Example:
  >>> synthesizer = CNLSynthesizer()
  >>> cnl = synthesizer.synthesize(
  ...     entities=[{"text": "deploy", "type": "VERB"}],
  ...     relations={"action_on": ["deploy", "service"]}
  ... )
  >>> print(cnl)  # Action:Deploy_Service -> EXEC:...
```

**Data Class: `CNLStatement`**
```
Signature:
  @dataclass
  class CNLStatement:
    statement: str
    confidence: float
    source_entities: List[str]

Description:
  Represents a single CNL statement with its confidence score and source
  entities that contributed to its generation.
```

---

#### Module: validator.py

**Primary Class:** `HaikuValidator`

**Constructor:**
```
Signature:
  def __init__(self,
               similarity_model: str = "sentence-transformers/all-MiniLM-L6-v2",
               config: Optional[Dict[str, Any]] = None)

Parameters:
  similarity_model (str, optional): Embedding model for semantic similarity
                                   (default: sentence-transformers model)
  config (Optional[Dict[str, Any]], optional): Configuration (thresholds,
                                              tokenizer name)
                                              (default: None)

Description:
  Initializes the validator with an embedding model for semantic similarity
  measurement and metric computation.
```

**Primary Method: `compute_metrics()`**
```
Signature:
  def compute_metrics(self, original: str, compressed: str)
    -> CompressionMetrics

Parameters:
  original (str): Original document text
  compressed (str): Compressed CNL text

Returns:
  CompressionMetrics: Detailed compression effectiveness measurements

Description:
  Computes compression metrics by comparing original and compressed text:
  compression ratio, token counts, semantic similarity, and information
  retention score.

Example:
  >>> validator = HaikuValidator()
  >>> metrics = validator.compute_metrics(original_text, compressed_cnl)
  >>> print(f"Ratio: {metrics.compression_ratio:.1%}")
  >>> print(f"Semantic Similarity: {metrics.semantic_similarity:.2f}")
```

**Data Class: `CompressionMetrics`**
```
Signature:
  @dataclass
  class CompressionMetrics:
    compression_ratio: float
    original_tokens: int
    compressed_tokens: int
    semantic_similarity: float  # 0.0 to 1.0
    information_retention: float  # 0.0 to 1.0
    processing_time_ms: float

Description:
  Container for all compression quality measurements. compression_ratio is
  expressed as a fraction (0.0 to 1.0, where 0.5 means 50% reduction).
```

**Other Primary Method: `validate()`**
```
Signature:
  def validate(self, original: str, compressed: str) -> ValidationResult

Parameters:
  original (str): Original document text
  compressed (str): Compressed CNL text

Returns:
  ValidationResult: Grammar correctness, semantic preservation, and errors

Description:
  Validates compressed CNL against grammar rules and checks semantic
  preservation. Returns a ValidationResult with confidence and any error
  messages or warnings.
```

**Data Class: `ValidationResult`**
```
Signature:
  @dataclass
  class ValidationResult:
    is_valid: bool
    confidence: float
    error_messages: list
    warnings: list

Description:
  Result of validating compressed CNL. Contains pass/fail status, confidence
  score, and lists of any errors or warnings encountered.
```

---

## Acceptance Criteria

### General Criteria (All Sections)

1. All data shapes match actual types in source code (verified by line reference)
2. All method signatures are exact matches to source code (no paraphrasing)
3. No methods are documented that don't exist in the code
4. No private methods (prefixed `_`) are documented
5. All return types match the actual return type annotations in code
6. All parameter types are documented with their default values
7. No stub methods or unimplemented functions are documented
8. All examples are syntactically correct Python that could actually run
9. Markdown is valid GitHub-Flavored Markdown

### Data Flow Documentation Criteria

10. Four stages are documented: Input → Chunking → Extraction → Synthesis → Validation
11. Each stage has a title, description, input example, processing activity, and output example
12. Input and output examples are realistic (not abstract; could be actual data)
13. Input examples show concrete data structures (not just "string" or "list")
14. Output examples match the actual data class fields from source code
15. Token counts in examples are reasonable (not 1000 tokens for "hello world")
16. The progression makes sense: each stage's output matches the next stage's input
17. No forward-referencing or hand-waving ("next, magic happens")
18. Processing activity section explains which techniques/libraries are used
19. All class names and types in examples match actual code

### Data Shape Verification Table Criteria

20. Exactly five rows (one per pipeline stage)
21. Input Type column exactly matches method parameter type annotation
22. Output Type column exactly matches method return type annotation
23. Verified Against column references specific source file and method/class
24. Types use actual code notation (List[Chunk], Dict[str, Any], etc.)
25. No guessing or paraphrasing; all types from actual annotations

### Module Reference Criteria

26. Exactly five modules documented: encoder, chunker, extractor, synthesizer, validator
27. Each module has primary class name identified
28. Each primary method has: signature, parameters, returns, description, example
29. Method signatures are exact code (including type annotations)
30. Parameter descriptions explain the purpose and default value (if any)
31. Return descriptions are concise (one-liner), not exhaustive
32. Examples are short (2–3 lines) and show common usage
33. Data classes are documented with their @dataclass decorator and fields
34. Data class field types are listed with actual type annotations
35. No private methods or internal functions documented
36. One-sentence descriptions for methods and classes

### Example Code Criteria

37. All code examples are valid Python 3.10+ syntax
38. All examples could actually run (assuming imports available)
39. Example inputs/outputs use realistic, small datasets
40. No ellipsis (...) except where NotImplementedError is being shown
41. All class and function names in examples match actual source code exactly

---

## Content Accuracy Requirements

### Verification Process for Data Flow Section

For each stage, verify:

| Claim | Source | Verification |
|---|---|---|
| "Chunker returns List[Chunk]" | `src/chunker.py` line 78 | Read chunk() method return type: List[Chunk] ✓ |
| "Chunk has fields: text, chunk_id, start_char, end_char, token_count" | `src/chunker.py` lines 25–32 | Read @dataclass Chunk definition ✓ |
| "Extractor takes chunk_text and chunk_id" | `src/extractor.py` line 83 | Read extract() parameters ✓ |
| "ExtractedEntities has entities, chunk_id, relations" | `src/extractor.py` lines 35–39 | Read @dataclass ExtractedEntities ✓ |
| "Synthesizer takes entities and relations" | `src/synthesizer.py` line 76 | Read synthesize() parameters ✓ |
| "Validator.compute_metrics returns CompressionMetrics" | `src/validator.py` line 127 | Read return type annotation ✓ |
| "CompressionMetrics has 6 fields" | `src/validator.py` lines 38–46 | Count fields in @dataclass ✓ |

### Verification Process for Module Reference

For each method signature, verify:

1. Open source file
2. Find method definition
3. Copy exact signature (including type annotations and defaults)
4. Compare against spec
5. If different, update spec (never the code)

Example:
```python
# src/encoder.py, line 75
def encode(self, document: str) -> str:

# Spec should show:
# def encode(self, document: str) -> str
# ✓ Exact match
```

---

## Dependencies

### Input Artifacts

| Artifact | Source | Purpose |
|---|---|---|
| `chunker.py` | Phase 2 (v0.2.1) | Source for DocumentChunker, Chunk class |
| `extractor.py` | Phase 2 (v0.2.2) | Source for EntityExtractor, Entity, ExtractedEntities classes |
| `synthesizer.py` | Phase 2 (v0.2.3) | Source for CNLSynthesizer, CNLStatement class |
| `validator.py` | Phase 2 (v0.2.4) | Source for HaikuValidator, CompressionMetrics, ValidationResult classes |
| `encoder.py` | Phase 2 (v0.2.0) | Source for HaikuEncoder (orchestrator) |
| `STYLE_GUIDE.md` | Phase 0 (v0.0.2c) | Grammar specification; used in synthesizer/validator descriptions |

### Output Artifacts

| Artifact | Purpose |
|---|---|
| Data Flow and Module Reference sections (draft) | Sections of ARCHITECTURE.md to be finalized in v0.4.2 implementation |

---

## Decision Log

### D-v0.4.2b-001: Abbreviated Signatures, Not Exhaustive API Docs

**Decision:** Module reference shows primary methods only (encode, chunk, extract, synthesize, compute_metrics) with abbreviated signatures. Does not document every method, every optional parameter, or full docstring text.

**Rationale:**
- Exhaustive API docs should be in docstrings or generated by documentation tools (pdoc, Sphinx)
- ARCHITECTURE.md serves as a high-level reference, not an API manual
- Abbreviated format keeps the document readable and focused
- Readers wanting full details can read the source code docstrings

**Trade-off:**
- Some methods and parameters are not documented
- A developer must still read source code for complete information
- But the module reference answers: "What can I call?" and "What does it return?"

**Decision Status:** FINAL — This constraint applies to the Module Reference section.

---

### D-v0.4.2b-002: Data Shapes Show Concrete Examples, Not Just Type Definitions

**Decision:** Data flow section includes realistic example values (actual Chunk objects with sample text, actual token counts), not just "List[Chunk]" type definitions.

**Rationale:**
- Concrete examples make data structures tangible and understandable
- Reader can see what a Chunk looks like with actual field values
- Bridges the gap between "what is it?" and "what does it look like?"
- Prevents confusion about field interpretation (e.g., is chunk_id a string or int?)

**Trade-off:**
- Concrete examples take more space in the document
- Examples must be kept realistic and accurate (token counts, field values)
- Readers may expect all examples to be copy-paste-runnable (they won't be, due to abbreviation)

**Decision Status:** FINAL — All data flow examples use concrete values.

---

## Quality Checklist

### Pre-Publication Checklist

- [ ] All method signatures copied exactly from source code (including type annotations and defaults)
- [ ] All return types match source code return type annotations
- [ ] All parameter types match source code parameter annotations
- [ ] No stub methods (NotImplementedError) documented as if implemented
- [ ] No private methods (_private_method) documented
- [ ] No internal-only classes documented
- [ ] Data flow section covers four stages: Input → Chunking → Extraction → Synthesis → Validation
- [ ] Each stage has: Title, Description, Input Example, Processing Activity, Output Example
- [ ] Input examples are realistic (not abstract like "Document text")
- [ ] Output examples show actual dataclass fields with sample values
- [ ] Token counts in examples are reasonable and realistic
- [ ] No magic; each stage clearly shows what it receives and produces
- [ ] Data Shape Verification table has exactly five rows
- [ ] Each row's Input Type and Output Type are exact type annotations from code
- [ ] Each row's Verified Against references specific source file and line/method
- [ ] Module reference documents exactly five modules: encoder, chunker, extractor, synthesizer, validator
- [ ] Each module section lists the primary class name
- [ ] Each primary method has signature, parameters, returns, description, and brief example
- [ ] All method signatures are exact code (can copy-paste)
- [ ] All parameter descriptions include purpose and default value
- [ ] All return descriptions are one-sentence
- [ ] All examples are valid Python and wouldn't crash
- [ ] All class names and types in examples match actual code
- [ ] Data classes show @dataclass decorator and all fields with type annotations
- [ ] One-sentence descriptions for all methods and classes
- [ ] No typos or grammatical errors
- [ ] Markdown is valid GFM and renders on GitHub
- [ ] All internal references are consistent (e.g., method names used in multiple places match)
- [ ] Decision Log entries explain design choices for this section

---

## Implementation Notes

### For the Implementer

1. **Start with Code Review:** Open each of the five source files. Read every method in the classes you're documenting. Copy method signatures directly from the code (no paraphrasing).

2. **Trace the Data Flow:** Start with encoder.py. Follow the `encode()` method. See what it calls and what data flows between calls. This is your guide for the four-stage walkthrough.

3. **Data Shape Accuracy:** For each stage:
   - Read the return type annotation of the previous stage's method
   - Verify it matches the input type of the next stage's method
   - Create a realistic example with actual values (not lorem ipsum)
   - Include realistic token counts (use a tokenizer to compute if unsure)

4. **Module Reference Precision:** For each method:
   - Copy the signature exactly (don't reformat or simplify)
   - Include default parameter values
   - Write a one-sentence description (not a full docstring)
   - Provide a 2–3 line example (not a full tutorial)

5. **Example Values:** When creating examples:
   - Use realistic entity types (NOUN, VERB, ENTITY)
   - Use realistic confidence scores (0.7–0.95)
   - Use realistic token counts (5–50 tokens for short examples)
   - Use realistic chunk IDs (0, 1, 2, not arbitrary numbers)

6. **Cross-Check:** For every type, method name, or class name:
   - Find it in the source code
   - Verify it matches exactly (capitalization, underscores, etc.)
   - If it doesn't match, update your spec, not the code

---

## Related Documents

- **Part 1 Specification:** [v0.4.2a — System Overview & Components](system_overview_and_components.md)
- **Part 3 Specification:** [v0.4.2c — Design Decisions & Style Guide](design_decisions_and_style_guide.md)
- **Authoritative Scope:** [v0.4.0 SCOPE_BREAKDOWN.md](../v0.4.0/SCOPE_BREAKDOWN.md) — sections 7.2 defines v0.4.2 scope
- **Grammar Reference:** [STYLE_GUIDE.md](../../../../STYLE_GUIDE.md) — CNL operators referenced in synthesizer documentation
- **Project README:** [README.md](../../../../README.md) — mentions the pipeline stages

---

**End of v0.4.2b Specification**
