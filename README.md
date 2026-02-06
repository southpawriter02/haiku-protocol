# Haiku Protocol

**Lossless semantic compression for LLM context windows.**

The Haiku Protocol is a Controlled Natural Language (CNL) compression system that transforms verbose technical documentation into dense, machine-optimized strings while preserving 100% semantic meaning. It works like "minification" for natural language — just as developers minify JavaScript to make websites faster, Haiku Protocol minifies prose to make AI context denser.

```
Original (23 tokens):
  "To restart the server, you must first ensure that the configuration
   file is saved, and then you can execute the reboot command."

Haiku Protocol (10 tokens):
  Action:Restart_Server REQUIRES State:Config_Saved -> EXEC:Reboot_Cmd
```

## The Problem

LLM context windows are expensive and finite. A 128k-token window isn't actually 128k tokens of *knowledge* — it's closer to 70k tokens of knowledge wrapped in 58k tokens of human-readable packaging: articles, transitions, filler phrases, and polite grammar. Technical documentation wastes roughly 40% of tokens on structural "fluff" that machines don't need.

## The Solution

A two-stage compression pipeline that encodes human-readable documentation into a structured, grammar-defined shorthand — then decodes it back on demand.

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

**The Encoder** breaks documents into semantic chunks, extracts key entities and relationships, and synthesizes them into CNL statements governed by a formal grammar. **The Decoder** teaches the LLM to interpret CNL and expand it back into natural language answers.

## Planned Features

- **Custom CNL grammar** with formally defined operators, syntax rules, and validation — designed by a Technical Writer, not just an algorithm
- **Multi-strategy document chunking** that respects semantic boundaries rather than arbitrary token limits
- **LLM-assisted entity extraction** to identify the nouns, verbs, and relationships that carry actual meaning
- **Compression quality metrics** including token reduction ratio, semantic similarity scoring, and information retention measurement
- **Benchmark comparison** against LLMLingua and other compression baselines to prove effectiveness
- **Interactive web demo** for live compression with a visual metrics dashboard
- **Round-trip fidelity** — compressed CNL can be decoded back to human-readable text without information loss

## Development Roadmap

The project follows a phased, spec-first development methodology:

| Phase | Focus | Description |
|-------|-------|-------------|
| Research | CNL Design | Literature review, grammar specification, benchmarking strategy |
| Environment | Foundation | Development environment, dependencies, API configuration, project scaffolding |
| Encoder | Core Engine | Document processing pipeline — chunking, extraction, synthesis, validation |
| Demo | Integration | Web interface, comprehensive test suite, benchmark integration |
| Release | Polish | Documentation, architecture write-up, public release |

## Goals

- Compression ratio of 50%+ on procedural technical documentation
- Semantic similarity above 0.85 between original and decoded output
- Competitive or superior results vs. LLMLingua baseline
- Working web demo with live compression and metrics dashboard

## License

MIT
