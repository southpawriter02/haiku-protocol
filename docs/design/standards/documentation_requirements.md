# Documentation Requirements — Haiku Protocol

<aside>

**Scope:** All phases (v0.1.x through v0.4.x)

**Status:** Active

**Applies To:** All project documentation — README files, architecture docs, decision logs, API references, and user-facing help

**Deliverable:** Templates, content standards, and maintenance rules for every documentation artifact in the project

</aside>

---

## Purpose

This document defines what documentation the Haiku Protocol project must produce, what each document must contain, and how documentation is maintained over the project lifecycle. Code comments and docstrings are covered separately in [Commenting Standards](commenting_standards.md); this document covers everything *outside* the code itself.

---

## Documentation Philosophy

### Core Principles

1. **Documentation is a deliverable, not an afterthought.** Each phase includes documentation tasks alongside code tasks.
2. **Write for the newcomer.** Every document should be understandable by someone encountering the project for the first time.
3. **One source of truth.** Every fact lives in exactly one place. Other documents link to it rather than duplicating it.
4. **Keep it current or delete it.** Outdated documentation is worse than no documentation. If a document can't be maintained, remove it.
5. **Show, don't just tell.** Include code examples, command-line invocations, and expected output wherever possible.

---

## Documentation Inventory

### Required Documents

```
haiku-protocol/
├── README.md                      # Project overview and quick start
├── ARCHITECTURE.md                # System design and module relationships
├── STYLE_GUIDE.md                 # CNL grammar specification
├── LICENSE                        # MIT license (created in v0.1.3b)
├── CHANGELOG.md                   # Version history and release notes
├── docs/
│   ├── standards/                 # Engineering standards (this directory)
│   │   ├── testing_standards.md
│   │   ├── logging_standards.md
│   │   ├── commenting_standards.md
│   │   └── documentation_requirements.md  (this file)
│   ├── LITERATURE_REVIEW.md       # Research summary (from v0.0.1)
│   ├── DECISION_LOG.md            # Architectural decision records
│   └── phase-{0..4}/             # Phase specifications (existing)
```

### Document Ownership by Phase

| Document | Created | Updated | Owner Phase |
|----------|---------|---------|-------------|
| README.md | v0.1.3b (stub) | v0.4.1 (final) | Phase 4 |
| ARCHITECTURE.md | v0.2.0 (initial) | v0.4.2 (final) | Phase 4 |
| STYLE_GUIDE.md | v0.0.2 (draft) | v0.2.3 (final) | Phase 2 |
| CHANGELOG.md | v0.2.0 (first entry) | Every release | All phases |
| DECISION_LOG.md | v0.1.0 (started) | Ongoing | All phases |
| LITERATURE_REVIEW.md | v0.0.1 (complete) | Rarely | Phase 0 |
| Standards docs | v0.1.x (this effort) | As needed | All phases |

---

## README.md — Project Overview

### Purpose

The README is the first thing anyone sees. It must answer in under 60 seconds: *What is this project? How do I run it? Where do I learn more?*

### Required Sections

```markdown
# Haiku Protocol

One-paragraph description of what the project does.

## Quick Start

Step-by-step instructions to get running in under 5 minutes.
Must include: clone, install, configure, run.

## What It Does

Brief explanation of the compression pipeline with a
before/after example showing input → CNL output.

## Architecture Overview

High-level diagram (ASCII or Mermaid) showing the pipeline:
Document → Chunker → Extractor → Synthesizer → CNL Output

## Installation

### Prerequisites
- Python 3.10+
- OpenAI API key

### Setup
Exact commands to install and configure.

## Usage

### CLI
How to run compression from the command line.

### Streamlit Demo
How to launch and use the web interface.

### Python API
How to import and use programmatically.

## Project Structure

Directory tree showing key files and their purposes.

## Benchmarks

Summary table: compression ratio, semantic similarity,
comparison with LLMLingua baseline.

## Contributing

Link to contributing guidelines or brief instructions.

## License

MIT — link to LICENSE file.
```

### README Quality Checklist

- [ ] First sentence explains what the project does (no jargon)
- [ ] Quick Start section works for a fresh clone (tested)
- [ ] At least one code example showing input → output
- [ ] Installation instructions include all prerequisites
- [ ] All commands are copy-pasteable (no placeholders without explanation)
- [ ] No broken links
- [ ] Badges (optional): build status, coverage, license

---

## ARCHITECTURE.md — System Design

### Purpose

Explains *how* the system works at a level above individual modules. Target audience: a developer who needs to understand the design before contributing.

### Required Sections

```markdown
# Architecture

## System Overview

One paragraph + high-level diagram showing the full pipeline.

## Module Relationships

Diagram showing which modules depend on which:

  encoder.py
    ├── chunker.py
    ├── extractor.py
    └── synthesizer.py

  validator.py (independent)
  decoder.py (inverse of encoder)
  app.py (integrates all)

## Data Flow

Step-by-step description of how data moves through the system:
1. User provides document text
2. Encoder receives text, passes to Chunker
3. Chunker splits into Chunk objects
4. Each Chunk → Extractor → ExtractedEntities
5. All entities → Synthesizer → CNL statements
6. CNL output returned to user
7. Optional: Validator measures quality

## Key Data Structures

Table of dataclasses and what they represent:
- Chunk: document segment with metadata
- Entity: extracted noun/verb/relation
- CNLStatement: single compressed statement
- CompressionMetrics: quality measurements

## Design Decisions

Link to DECISION_LOG.md for detailed ADRs.
Summarize the most important decisions here:
- Why CNL over extractive summarization
- Why LangChain over direct API calls
- Why semantic chunking as default strategy

## Configuration

How configuration flows from .env → Config → modules.

## External Dependencies

What external services are required (OpenAI API)
and how the system handles their failure.
```

### Architecture Diagrams

Use ASCII art or Mermaid syntax (renders on GitHub):

```markdown
## Pipeline Diagram (Mermaid)

​```mermaid
graph LR
    A[Document] --> B[Chunker]
    B --> C[Extractor]
    C --> D[Synthesizer]
    D --> E[CNL Output]
    E --> F[Validator]
    F --> G[Metrics]
​```
```

### ASCII Fallback

For environments that don't render Mermaid, include ASCII diagrams (as already used in the spec documents):

```
INPUT DOCUMENT
     │
     ▼
┌──────────┐
│ Chunker  │──▶ List[Chunk]
└──────────┘
     │
     ▼
┌──────────┐
│Extractor │──▶ List[ExtractedEntities]
└──────────┘
     │
     ▼
┌────────────┐
│Synthesizer │──▶ CNL Output (str)
└────────────┘
```

---

## CHANGELOG.md — Version History

### Purpose

Tracks what changed in each version. Essential for users who upgrade and need to know what's new, changed, or broken.

### Format: Keep a Changelog

Follow the [Keep a Changelog](https://keepachangelog.com/) convention:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Items that are new

### Changed
- Items that changed behavior

### Fixed
- Bug fixes

## [0.2.0] - 2026-XX-XX

### Added
- HaikuEncoder compression pipeline (v0.2.0)
- DocumentChunker with semantic, fixed_size, sliding_window strategies (v0.2.1)
- EntityExtractor with NLP-based extraction (v0.2.2)
- CNLSynthesizer with grammar rules from v0.0.2c (v0.2.3)
- HaikuValidator with compression metrics (v0.2.4)

### Changed
- Config class now supports multiple LLM providers

## [0.1.0] - 2026-02-XX

### Added
- Project scaffolding and directory structure (v0.1.3)
- Configuration module with .env support (v0.1.2)
- Core dependency installation (v0.1.1)
- API connection testing (v0.1.2d)
```

### Rules

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for features that will be removed
- **Removed** for features that have been removed
- **Fixed** for bug fixes
- **Security** for vulnerability fixes
- Update `[Unreleased]` section as work progresses
- Move `[Unreleased]` items to a versioned section on release

---

## DECISION_LOG.md — Architectural Decision Records

### Purpose

Records significant technical decisions, their context, and their rationale. Prevents re-litigating settled decisions and helps future contributors understand *why* things are the way they are.

### Template: Lightweight ADR

```markdown
# Decision Log

## ADR-001: Use CNL for Compression Output

**Date:** 2026-02-05
**Status:** Accepted
**Phase:** v0.0.2

### Context
We needed a format for compressed document output that is both
human-readable and machine-parseable.

### Options Considered
1. **Extractive summarization** — select key sentences
2. **Abstractive summarization** — LLM generates summary
3. **Controlled Natural Language** — structured grammar with operators

### Decision
Use CNL (option 3) because it provides:
- Defined grammar (parseable, validatable)
- Higher compression ratio than extractive
- Better semantic preservation than abstractive
- Unique research contribution

### Consequences
- Must define and formalize CNL grammar (v0.0.2b, v0.0.2c)
- Requires custom validation rules (v0.0.2d)
- Learning curve for users reading CNL output

---

## ADR-002: Use LangChain for LLM Integration

**Date:** 2026-02-05
**Status:** Accepted
**Phase:** v0.1.1

### Context
...
```

### When to Write an ADR

Write a decision record when:

- Choosing between multiple valid approaches
- Selecting a library or framework
- Defining a data format or protocol
- Making a trade-off that affects multiple modules
- Reversing or amending a previous decision

### When NOT to Write an ADR

- Implementation details within a single function
- Formatting or style choices (covered by standards docs)
- Temporary workarounds (use TODO comments instead)

---

## STYLE_GUIDE.md — CNL Grammar Specification

### Purpose

Documents the Controlled Natural Language grammar that defines valid compression output. This is a project-specific document, not a general coding style guide.

### Required Content

- BNF grammar rules (from v0.0.2c)
- Operator definitions and semantics
- Valid CNL statement patterns with examples
- Validation rules (from v0.0.2d)
- Edge cases and error handling

### Ownership

- Drafted during Phase 0 research (v0.0.2)
- Finalized during Phase 2 implementation (v0.2.3)
- Referenced by validator.py and synthesizer.py

---

## Spec Document Standards (docs/phase-{N}/v{X}.{Y}.{Z}/)

### Existing Convention

The project already has a strong spec document convention established across Phase 0 and Phase 1. The following rules codify and enforce that convention.

### Required Spec Document Sections

Every version README.md must include:

```markdown
# vX.Y.Z — Brief Title

<aside>
**Phase:** N — Phase Name
**Version:** vX.Y.Z
**Status:** Not Started | In Progress | Complete
**Duration:** Estimated time
**Deliverable:** One-sentence description of what this version produces
</aside>

---

## Objective
What this version accomplishes and why.

## [Technical Content]
Main body — varies by document type.

## Acceptance Criteria
- [ ] Checkbox list of verifiable completion criteria

## Limitations & Constraints
Numbered list of known limitations.

## Dependencies
What must be completed before this version.

## Troubleshooting
Common issues with symptoms and solutions.

## User Story
> As a [role], I want to [action] so that [benefit].

## Inputs from Previous Sub-Parts
What this version receives from prior work.

## Outputs to Next Sub-Part
What this version produces for subsequent work.

## Decision Log
Table of decisions made during this version.
```

### Sub-Document Standards

For sub-documents (e.g., `python_environment_setup.md`):

```markdown
# vX.Y.Za — Sub-Part Title

<aside>
**Version:** vX.Y.Za
**Parent:** vX.Y.Z — Parent Title
**Status:** Not Started
**Duration:** Estimated time
**Deliverable:** What this sub-part produces
</aside>

## Objective
## [Technical Content]
## Acceptance Criteria
## Limitations & Constraints
## Dependencies
## Troubleshooting
## User Story
## Inputs from Previous Sub-Parts
## Outputs to Next Sub-Part
## Decision Log
```

---

## Documentation Maintenance

### Update Triggers

| Event | Documents to Update |
|-------|-------------------|
| New feature implemented | CHANGELOG.md, relevant spec README |
| Architecture change | ARCHITECTURE.md, DECISION_LOG.md |
| Bug fix | CHANGELOG.md |
| New dependency added | README.md (prerequisites), requirements.txt |
| API change | README.md (usage), ARCHITECTURE.md |
| Grammar rule change | STYLE_GUIDE.md |
| Version released | CHANGELOG.md (move Unreleased → version) |

### Staleness Prevention

- Review ARCHITECTURE.md at the start of each new phase
- Review README.md Quick Start section monthly (or when deps change)
- Run all Quick Start commands on a fresh clone before each release
- Delete documents that no longer apply (don't just mark "deprecated")

---

## Documentation Quality Standards

### Writing Style

- **Active voice:** "The encoder compresses documents" not "Documents are compressed by the encoder"
- **Present tense:** "The function returns a string" not "The function will return a string"
- **Second person for instructions:** "Run `pytest`" not "The user should run pytest"
- **Concise:** Remove filler words. "In order to" → "To". "Basically" → delete.
- **Consistent terminology:** Use the same term for the same concept everywhere

### Terminology Table

| Term | Meaning | Don't Use |
|------|---------|-----------|
| CNL | Controlled Natural Language output | compressed text, summary |
| Chunk | Segment of a document | piece, section, part |
| Entity | Extracted noun, verb, or relation | word, token, term |
| Compression ratio | (original - compressed) / original | reduction, savings |
| Encode | Compress a document to CNL | compress, summarize |
| Decode | Expand CNL back to natural language | decompress, expand |

### Formatting Rules

- Use `code blocks` for file paths, commands, function names, and config values
- Use **bold** for key terms being defined
- Use tables for comparisons and option matrices
- Use numbered lists for sequential steps
- Use bullet lists for unordered items
- Use `> blockquotes` for user stories and important callouts
- Include language identifier on fenced code blocks (```python, ```bash, etc.)

---

## Workflow: Writing a New Document

```
1. Identify the document type (README, ADR, spec, etc.)
       │
       ▼
2. Copy the relevant template from this file
       │
       ▼
3. Fill in all required sections
       │
       ▼
4. Add code examples and expected output
       │
       ▼
5. Test all commands and code examples
       │
       ▼
6. Review for consistent terminology (see table above)
       │
       ▼
7. Check for broken links to other docs
       │
       ▼
8. Add to CHANGELOG.md if it's a new document
       │
       ▼
9. Update README_DOCS_STRUCTURE.md if structure changed
```

---

## Dos and Don'ts

### Do

- Write documentation alongside code, not after
- Include a Quick Start that works on a fresh clone
- Test every command you include in documentation
- Use templates for consistency across documents
- Link to related documents rather than duplicating content
- Include diagrams for system-level concepts
- Update CHANGELOG.md with every version
- Write decision records for significant technical choices

### Don't

- Write documentation you won't maintain
- Duplicate the same information in multiple places
- Use screenshots for command-line output (use text blocks)
- Write walls of text without structure (use headers and lists)
- Assume the reader has context (link to prerequisites)
- Leave placeholder sections empty ("TBD", "TODO: fill in later")
- Use relative dates ("recently", "soon") — use version numbers
- Create documentation files not listed in the project structure

---

## Acceptance Criteria (for this document)

- [ ] README.md template defined with all required sections
- [ ] ARCHITECTURE.md requirements specified with diagram standards
- [ ] CHANGELOG.md format defined (Keep a Changelog convention)
- [ ] DECISION_LOG.md ADR template provided
- [ ] STYLE_GUIDE.md scope and ownership documented
- [ ] Spec document section requirements match existing conventions
- [ ] Documentation maintenance triggers defined
- [ ] Writing style guide with terminology table provided
- [ ] Workflow for creating new documents outlined
- [ ] All four standards documents cross-reference each other

---

## Related Documents

- [Commenting Standards](commenting_standards.md) — In-code documentation (docstrings, comments)
- [Testing Standards](testing_standards.md) — Test documentation and naming conventions
- [Logging Standards](logging_standards.md) — Operational documentation via log output
- [README_DOCS_STRUCTURE.md](../../README_DOCS_STRUCTURE.md) — Project documentation structure map
- [v0.4.1 — README & Quick Start](../phase-4/v0.4.1/README.md) — Phase where README is finalized
- [v0.4.2 — Architecture Documentation](../phase-4/v0.4.2/README.md) — Phase where ARCHITECTURE.md is finalized
