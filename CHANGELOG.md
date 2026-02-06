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
- Complete EBNF grammar specification (`research/haiku_grammar.bnf`) with all 12 operators, precedence table, 5 ambiguity resolution rules, and shared terminals (v0.0.2c)
- Research-phase tokenizer and validator (`research/haiku_parser.py`) with `HaikuParser` class, `Token`/`ParseResult` dataclasses, regex-based tokenizer, and structural validation (v0.0.2c)
- CNL Grammar Style Guide (`STYLE_GUIDE.md`) with operator quick reference, naming conventions, 8 composition rules, encoding examples, ambiguity resolution rules, and terminology (v0.0.2c)
- Unit test suite for HaikuParser with 45 tests covering 10 valid spec strings, 5 invalid spec strings, tokenizer behavior, edge cases, ambiguity resolution, grammar completeness, logging, and use case integration (v0.0.2c)
- Multi-stage validation pipeline (`research/haiku_validator.py`) with `HaikuValidator` class implementing 6 rules (VAL-001 through VAL-006) across 5 sequential stages: syntactic, semantic, referential, completeness, and execution (v0.0.2d)
- Validation rules specification (`research/validation_rules.md`) with error taxonomy (1xx-5xx codes), 3 recovery strategies (auto-correction, aggregation, interactive repair), validation pipeline diagram, and pass/fail examples for all 6 rules (v0.0.2d)
- `ErrorSeverity` enum, `ValidationError`/`ValidationResult` dataclasses, Levenshtein-based auto-correction via `suggest_fix()`, and `VAGUE_VERIFY_TERMS` constant for non-automatable check detection (v0.0.2d)
- Unit test suite for HaikuValidator with 75 tests covering happy path, edge cases, error paths for all 6 rules, log output verification, recovery strategies, and end-to-end use case workflow (v0.0.2d)
- Benchmarking directory structure (`benchmarks/`, `benchmarks/samples/`) establishing the file layout for Phase 0 compression baseline testing (v0.0.3a)
- Simple-tier benchmark document (`benchmarks/samples/simple.md`): npm project initialization procedure, ~103 tokens, 3 sequential steps, 1 prerequisite, no branching — domain: Package Management (v0.0.3a)
- Medium-tier benchmark document (`benchmarks/samples/medium.md`): Git stash save-and-restore workflow, ~488 tokens, 5 sequential steps with conditional branches (conflict handling, optional stash inspection), 3 prerequisites, 1 warning block, 1 note block, troubleshooting section with 3 scenarios — domain: Version Control (v0.0.3a)
- Complex-tier benchmark document (`benchmarks/samples/complex.md`): Kubernetes stateless application deployment guide, ~1977 tokens, 7 steps (create manifest, apply, verify rollout, expose service, update image, scale, clean up), YAML manifest with resource limits and health probes, 4 prerequisites, 4+ warning/note blocks, troubleshooting table with 6 symptom-resolution pairs, 4 cross-references to external documentation — domain: Container Orchestration (v0.0.3a)
- Automated complexity scoring tool (`benchmarks/complexity_scorer.py`) with `score_document_complexity()` (weighted procedural marker analysis across 6 indicator categories: step markers, command blocks, warnings, conditionals, prerequisites, cross-references), `classify_by_score()` (tier classification with thresholds at 0.35 and 0.70), `estimate_tokens()` (4-char heuristic for preliminary token estimation), and `score_all_samples()` (batch scoring with ISO-8601 timestamps and JSON output) (v0.0.3a)
- Complexity scoring results (`benchmarks/complexity_scores.json`) confirming all 3 documents match expected tier classifications — simple.md scored 0.045/SIMPLE, medium.md scored 0.375/MEDIUM, complex.md scored 0.835/COMPLEX (v0.0.3a)
- Curation checklist (`benchmarks/curation_checklist.json`) documenting source URL, source license, tool domain, complexity tier, 6-point verification matrix (procedural, public, English, clean encoding, token range, uniqueness), preliminary token estimates, and domain diversity check for each sample document (v0.0.3a)
- Unit test suite for complexity scorer (`tests/test_complexity_scorer.py`) with 30 tests: 6 happy path (simple/medium/complex scoring, return type, indicator keys, normalization), 5 edge cases (empty string, whitespace, None, single word, no markers), 9 classification boundary tests (parametrized across all tier thresholds), 3 token estimation tests, 4 integration tests (score_all_samples with valid/empty/missing directories and required keys), 2 logging tests (caplog verification for scoring and completion messages), 1 end-to-end use case workflow test simulating full curation-and-score pipeline (v0.0.3a)

## [0.0.1] - 2026-02-06

### Added

- Academic research survey with annotated bibliography (`research/academic_sources.json`) (v0.0.1a)
- Competitive analysis matrix for 5 prompt compression tools (`research/competitive_analysis.md`) (v0.0.1b)
- CNL & Information Architecture theoretical foundations (`research/cnl_ia_foundations.md`) (v0.0.1c)
- Gap analysis and project positioning (`LITERATURE_REVIEW.md`) (v0.0.1d)
- Project scaffolding: `.gitignore`, initial README (v0.0.1)
