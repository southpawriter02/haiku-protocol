# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Pattern extraction tool (`research/pattern_extractor.py`) with `PatternExtractor` class for semantic analysis of procedural documentation (v0.0.2a)
- Corpus of 11 procedural document samples in `research/corpus/` covering man pages, READMEs, API guides, runbooks, troubleshooting guides, and tutorials (v0.0.2a)
- Pattern taxonomy document (`research/pattern_taxonomy.md`) with 8 semantic categories, frequency analysis, decision tree, and operator design recommendations (v0.0.2a)
- Extraction results JSON (`research/pattern_extraction_results.json`) for machine-readable downstream consumption (v0.0.2a)
- Unit test suite for PatternExtractor with 30 tests covering happy path, edge cases, error paths, ambiguity resolution, and log output verification (v0.0.2a)
- Test infrastructure: `tests/` directory with `conftest.py` shared fixtures (v0.0.2a)
- CHANGELOG.md following Keep a Changelog convention (v0.0.2a)
- Operator specification data model (`research/operator_specs.py`) with `OperatorSpec` TypedDict, 12 operators, 8 composition rules, naming conventions, and validation functions (v0.0.2b)
- Complete operator reference document (`research/operator_reference.md`) with BNF syntax, before/after examples, edge cases, precedence, composition rules, naming conventions, decision tree, and 5 end-to-end encoding examples (v0.0.2b)
- Composability validation: programmatic check confirming no dead-end operators (v0.0.2b)
- Semantic overlap check: programmatic check confirming no duplicate IDs, names, or symbols (v0.0.2b)
- Unit test suite for operator specs with 30 tests covering happy path, composability, semantic overlap, edge cases, pattern mapping, logging, and full use case workflow (v0.0.2b)

## [0.0.1] - 2026-02-06

### Added

- Academic research survey with annotated bibliography (`research/academic_sources.json`) (v0.0.1a)
- Competitive analysis matrix for 5 prompt compression tools (`research/competitive_analysis.md`) (v0.0.1b)
- CNL & Information Architecture theoretical foundations (`research/cnl_ia_foundations.md`) (v0.0.1c)
- Gap analysis and project positioning (`LITERATURE_REVIEW.md`) (v0.0.1d)
- Project scaffolding: `.gitignore`, initial README (v0.0.1)
