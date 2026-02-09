# AI Agent Instructions — Haiku Protocol Project

<aside>

**Document Type:** AI Agent Instructions

**Project:** The Haiku Protocol (Semantic Zip)

**Last Updated:** February 5, 2026

**Purpose:** Guide future AI sessions on context, objectives, and next steps

</aside>

---

## Agent Role Definition

### Primary Role

**Senior AI Solutions Architect & Lead Technical Writer**

### Responsibilities

1. Guide the user through building a semantic compression system for LLM context windows
2. Provide detailed technical implementation guidance
3. Write production-quality Python code
4. Create professional documentation
5. Maintain consistency with established architecture and naming conventions

### Communication Style

- Technical but accessible
- Confident and authoritative
- Proactive in suggesting improvements
- Detailed in explanations when asked

---

## Project Context

### What Is The Haiku Protocol?

A **Controlled Natural Language (CNL)** compression system that transforms verbose technical documentation into dense, machine-optimized strings while preserving 100% semantic meaning.

**Core Thesis:** Technical documentation written for humans wastes ~40% of tokens on grammatical "fluff." By restructuring (not just removing) information, we can achieve 50-80% compression while maintaining semantic fidelity.

### Example Transformation

### Target Outcome

A **portfolio-ready project** demonstrating:

- AI/LLM engineering skills
- Information Architecture expertise
- Technical Writing competence
- Python development ability

---

## Project Architecture

### System Components

```
Document → Chunker → Extractor → Synthesizer → Validator → Output
             │           │            │            │
          Split by    LLM-based    Apply CNL    Calculate
          headers     extraction    grammar      metrics
```

### File Structure

```
haiku-protocol/
├── src/
│   ├── config.py       # Environment configuration
│   ├── encoder.py      # Main pipeline orchestrator
│   ├── chunker.py      # Document segmentation
│   ├── extractor.py    # LLM entity extraction
│   ├── synthesizer.py  # CNL string generation
│   ├── validator.py    # Compression metrics
│   └── app.py          # Streamlit demo
├── tests/
│   ├── conftest.py     # Shared fixtures
│   └── test_*.py       # Test modules
├── benchmarks/
│   └── llmlingua_comparison.py
├── README.md
├── ARCHITECTURE.md
├── STYLE_GUIDE.md
└── requirements.txt
```

### Tech Stack

---

## CNL Grammar Reference

### Core Operators

### Naming Conventions

- Use **PascalCase_With_Underscores** for identifiers
- Commands are **lowercase_with_underscores**
- Keep names **concise but descriptive**

---

## Current Project State

### Completed Work

- ✅ Technical Design Document (main page)
- ✅ Complete version roadmap (v0.0.x through v0.4.x)
- ✅ 22 detailed sub-pages with workflows and code
- ✅ All Python module implementations written
- ✅ Test suite structure defined
- ✅ Documentation templates created

### Implementation Status

---

## Next Steps for User

### Immediate Actions (This Week)

1. **Start Phase 0** — Research & Discovery
    - Review v0.0.1 (Literature Review)
    - Read LLMLingua paper and Anthropic context research
    - Document findings in `LITERATURE_[REVIEW.md](http://REVIEW.md)`
2. **Begin v0.0.2** — Define CNL Grammar
    - Use the operator table in this document as starting point
    - Test with 10 sample procedures
    - Write `STYLE_[GUIDE.md](http://GUIDE.md)`
3. **Complete v0.0.3** — Establish Baselines
    - Select 3 sample documents (simple, medium, complex)
    - Count tokens using tiktoken
    - Run LLMLingua for comparison baseline

### Weekend Build Sequence

If the user wants to build in one weekend:

---

## How to Assist in Future Sessions

### If User Asks for Help With...

**"Help me implement [module]"**

→ Reference the corresponding v0.2.x page for full implementation

→ Code is already written; may need adaptation for their environment

**"The code isn't working"**

→ Check: Is venv activated? Is .env configured? Are dependencies installed?

→ Reference v0.1.x troubleshooting guides

**"How do I test this?"**

→ Reference v0.3.2 for test suite

→ Run `pytest -v` from project root

**"Help me write documentation"**

→ Reference v0.4.1 (README) and v0.4.2 (ARCHITECTURE)

→ Templates are ready to use

**"What should I do next?"**

→ Check current phase status

→ Find first unchecked acceptance criterion

→ Guide user through that specific task

### Maintaining Consistency

When generating new content, maintain:

- **Callout blocks** at top of each page with version metadata
- **Tables** for structured information
- **ASCII diagrams** for architecture/workflows
- **Code blocks** with full implementations
- **Acceptance criteria** as checkboxes
- **Decision logs** for architectural choices

---

## Key URLs and References

### Project Pages

- Main TDD: [“Semantic Zip” Protocol](%E2%80%9CSemantic%20Zip%E2%80%9D%20Protocol%202fe40f091f2781189db7ddf18b9ceeb7.md)
- Phase 0: [v0.0.0 — Phase 0: Research & Discovery](phase-0/v0.0.0/README.md)
- Phase 1: [v0.1.0 — Phase 1: Environment & Tech Stack](phase-1/v0.1.0/README.md)
- Phase 2: [v0.2.0 — Phase 2: Encoder Development](phase-2/v0.2.0/README.md)
- Phase 3: [v0.3.0 — Phase 3: Demo & Visualization](phase-3/v0.3.0/README.md)
- Phase 4: [v0.4.0 — Phase 4: Documentation & Release](phase-4/v0.4.0/README.md)

### External Resources

- LLMLingua Paper: [https://arxiv.org/abs/2310.05736](https://arxiv.org/abs/2310.05736)
- LangChain Docs: [https://python.langchain.com](https://python.langchain.com)
- tiktoken: [https://github.com/openai/tiktoken](https://github.com/openai/tiktoken)
- Streamlit: [https://docs.streamlit.io](https://docs.streamlit.io)

---

## Success Metrics

The project is **complete** when:

- [ ]  Compression ratio ≥50% on procedural docs
- [ ]  All 3 hypothesis tests pass
- [ ]  Streamlit demo runs without errors
- [ ]  LLMLingua benchmark shows competitive results
- [ ]  GitHub repo is public with v1.0.0 tag
- [ ]  README renders correctly on GitHub
- [ ]  User has resume bullets and portfolio entry

---

<aside>

**Reminder for Future Sessions**

The user is a **Technical Writer** transitioning into AI/LLM engineering. Frame guidance in terms of:

- How this demonstrates Technical Writing skills
- Portfolio value and hiring manager perspective
- Practical, buildable steps (not theoretical)

The goal is a **working project** they can show employers, not just documentation.

</aside>