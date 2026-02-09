# v0.2.0 — Phase 2: Encoder Development

<aside>

**Phase:** 2 — Encoder Development

**Version:** v0.2.0

**Status:** Core Development

**Duration:** 4-5 hours

**Objective:** Build the semantic compression pipeline

</aside>

---

## Phase Overview

This is the **heart of the project**. You will build the encoder pipeline that transforms verbose human documentation into dense, machine-optimized CNL.

The encoder has **four stages**:

1. **Chunking** — Split documents by semantic boundaries
2. **Entity Extraction** — Identify Actions, States, Commands
3. **CNL Synthesis** — Apply grammar rules to generate Haiku strings
4. **Validation** — Verify compression and semantic fidelity

---

## Version Roadmap

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ENCODER PIPELINE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐            │
│   │   INPUT     │    │  CHUNKER    │    │  EXTRACTOR  │            │
│   │  (Markdown) │───▶│ (by header) │───▶│   (LLM)     │            │
│   └─────────────┘    └─────────────┘    └─────────────┘            │
│                                                │                    │
│                                                ▼                    │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐            │
│   │   OUTPUT    │◀───│  VALIDATOR  │◀───│ SYNTHESIZER │            │
│   │   (JSON)    │    │  (metrics)  │    │   (CNL)     │            │
│   └─────────────┘    └─────────────┘    └─────────────┘            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase Exit Criteria

- [ ]  [`chunker.py`](http://chunker.py) splits markdown by `##` headers correctly
- [ ]  [`extractor.py`](http://extractor.py) identifies entities with ≥90% accuracy on test set
- [ ]  [`synthesizer.py`](http://synthesizer.py) outputs valid CNL strings
- [ ]  [`validator.py`](http://validator.py) calculates token counts and compression ratio
- [ ]  End-to-end test: Input markdown → Output JSON with metrics

---

## User Stories

---

## Decision Tree: Extraction Strategy

```
┌─────────────────────────────────────────┐
│  Is the document procedural (steps)?    │
└─────────────────────────────────────────┘
          │                    │
         YES                   NO
          │                    │
          ▼                    ▼
┌─────────────────┐   ┌─────────────────────┐
│ Extract:        │   │ Is it conceptual?   │
│ - Actions       │   └─────────────────────┘
│ - Prerequisites │        │           │
│ - Commands      │       YES          NO
└─────────────────┘        │           │
                           ▼           ▼
              ┌─────────────────┐  ┌──────────┐
              │ Extract:        │  │ Skip or  │
              │ - Definitions   │  │ flag for │
              │ - Relationships │  │ review   │
              └─────────────────┘  └──────────┘
```

---

## Test Cases

---

## Sub-Pages

[v0.2.1 — Chunking Module](../../phase-2/v0.2.1/README.md)

[v0.2.2 — Entity Extraction](../../phase-2/v0.2.2/README.md)

[v0.2.3 — CNL Synthesis Engine](../../phase-2/v0.2.3/README.md)

[v0.2.4 — Validation & Metrics](../../phase-2/v0.2.4/README.md)