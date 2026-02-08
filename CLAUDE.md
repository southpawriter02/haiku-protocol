# Haiku Protocol — Project Rules

## Project Identity

This is the **Haiku Protocol** — a Controlled Natural Language (CNL) compression system
for LLM context windows. It transforms verbose technical documentation into dense,
machine-optimized strings while preserving semantic meaning.

- Tech stack: Python 3.10+, pytest, LangChain, OpenAI, Streamlit
- Solo developer project (Technical Writer transitioning to AI/LLM engineering)
- Source code: `src/` | Tests: `tests/` | Specs: `docs/phase-{N}/v{X}.{Y}.{Z}/`

## Current Phase

<!-- UPDATE THESE TWO LINES AS YOU PROGRESS -->

CURRENT PHASE: 0 — Research & Discovery (v0.0.x)
ACTIVE VERSION: v0.1.3a — Directory Structure Creation

Roadmap: Research (v0.0.x) → Environment (v0.1.x) → Encoder (v0.2.x) → Demo (v0.3.x) → Release (v0.4.x)

## Version Discipline

- Read the spec BEFORE implementing: `docs/phase-{N}/v{X}.{Y}.{Z}/README.md`
- Each version has sub-documents with detailed requirements. Read them all.
- Every version has acceptance criteria (checkboxes). Do not advance until all are checked.
- Versions are sequential. Complete v0.0.1 before starting v0.0.2.
- Phase overviews (v{X}.{Y}.0) have exit criteria for the entire phase.
- When uncertain which version to work on, ask the user.

## File Organization

- Specs: `docs/phase-{N}/v{X}.{Y}.{Z}/` (README.md + sub-docs in snake_case)
- Standards: `docs/standards/` (cross-cutting, not phase-specific)
- Source: `src/` (encoder.py, decoder.py, chunker.py, extractor.py, synthesizer.py, validator.py, config.py, app.py)
- Tests: `tests/test_{module}.py`, `tests/conftest.py`, `tests/integration/`, `tests/fixtures/`
- Root: README.md, ARCHITECTURE.md, STYLE_GUIDE.md, LICENSE, CHANGELOG.md, requirements.txt
- Do NOT create files or directories outside this structure without asking.

## Code Conventions

- Google-style docstrings on all public modules, classes, and functions
- Type hints on all public function signatures and return types
- `logging.getLogger(__name__)` in every `src/` module. No `print()` in `src/`
- Use `%s`-style log formatting, not f-strings in log calls
- Never log API keys or secrets
- Test naming: `test_{method}_{scenario}_{expected_result}`
- pytest only. AAA pattern (Arrange–Act–Assert). One behavior per test.
- Mark tests: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.api`
- TODOs must include version: `# TODO (v0.2.1): description`
- No commented-out code in `src/`. Delete it; git has history.

## Git Conventions

- Commit messages: imperative mood, present tense, <72 char subject
- Prefix with type and version: `feat(v0.1.2c): implement Config class`
- Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`
- Never commit `.env`, API keys, or credentials
- Branch naming: `phase-{N}/v{X}.{Y}.{Z}-brief-description`
- Commit at logical checkpoints — at least once per sub-document

## Prohibited Actions

- DO NOT implement code ahead of the current phase
- DO NOT create files outside the established directory structure
- DO NOT modify spec documents (`docs/phase-*`) without asking the user
- DO NOT skip acceptance criteria or declare a version complete prematurely
- DO NOT add dependencies not in requirements.txt without asking
- DO NOT use `print()` in `src/` modules — use `logging`
- DO NOT create `.env` files — only `.env.example` is version-controlled
- DO NOT push to remote or amend commits without asking
- DO NOT use `unittest` — `pytest` is the sole test framework
- DO NOT generate boilerplate file headers (author, date) — use git metadata
- DO NOT auto-advance to the next phase without explicit user confirmation

## Standards References

For full details, see:

- Testing: `docs/standards/testing_standards.md`
- Logging: `docs/standards/logging_standards.md`
- Comments & Docstrings: `docs/standards/commenting_standards.md`
- Documentation: `docs/standards/documentation_requirements.md`
- Development Workflow: `docs/standards/development_workflow.md`
- Project context brief: `docs/ai_agent_instructions.md`

## Quick Reference

- Docs structure map: `README_DOCS_STRUCTURE.md`
- Project TDD: `docs/semantic_zip_protocol.md`
- Phase 0 overview: `docs/phase-0/v0.0.0/README.md`
- Phase 1 overview: `docs/phase-1/v0.1.0/README.md`
- Module stubs reference: `docs/phase-1/v0.1.3/source_module_stubs.md`
- Config class reference: `docs/phase-1/v0.1.2/configuration_module_implementation.md`
