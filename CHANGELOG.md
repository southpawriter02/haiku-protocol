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

## [0.0.1] - 2026-02-06

### Added

- Academic research survey with annotated bibliography (`research/academic_sources.json`) (v0.0.1a)
- Competitive analysis matrix for 5 prompt compression tools (`research/competitive_analysis.md`) (v0.0.1b)
- CNL & Information Architecture theoretical foundations (`research/cnl_ia_foundations.md`) (v0.0.1c)
- Gap analysis and project positioning (`LITERATURE_REVIEW.md`) (v0.0.1d)
- Project scaffolding: `.gitignore`, initial README (v0.0.1)
