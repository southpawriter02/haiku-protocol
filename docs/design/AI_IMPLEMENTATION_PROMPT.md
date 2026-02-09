# Haiku Protocol — Reusable AI Implementation Prompt

> **Purpose:** Copy the fenced code block below and paste it at the start of any AI session
> to direct the agent through implementing a specific version sub-part (e.g., `v0.0.1b`).
> Replace every `{placeholder}` with the actual values before submitting.
>
> **Maintained by:** Ryan (project owner)
>
> **Last Updated:** 2026-02-06

---

## How to Use

1. Open a new AI session (Claude, etc.).
2. Copy the entire fenced block below.
3. Replace every `{PLACEHOLDER}` with the real value for your target sub-part.
4. Paste it as your first message.
5. The AI agent will follow the workflow end-to-end.

### Placeholder Reference

| Placeholder | Example Value | Where to Find It |
|---|---|---|
| `{PHASE_NUMBER}` | `1` | `CLAUDE.md` → "Current Phase" |
| `{PHASE_NAME}` | `Environment & Tech Stack` | Phase overview README title |
| `{VERSION}` | `v0.1.2` | Parent version directory name |
| `{SUB_PART_LETTER}` | `c` | Sub-document letter (a, b, c, d) |
| `{SUB_PART_TITLE}` | `Configuration Module Implementation` | Sub-document H1 title |
| `{PARENT_VERSION_TITLE}` | `API Configuration & Secrets` | Parent version README H1 |
| `{SPEC_FILE_PATH}` | `docs/design/phase-1/v0.1.2/configuration_module_implementation.md` | Relative path to sub-doc |
| `{PARENT_SPEC_PATH}` | `docs/design/phase-1/v0.1.2/README.md` | Relative path to parent README |
| `{PHASE_OVERVIEW_PATH}` | `docs/design/phase-1/v0.1.0/README.md` | Relative path to phase overview |
| `{DELIVERABLE_SUMMARY}` | `src/config.py with Config class, .env loading, and validation` | One-sentence deliverable |
| `{USER_STORY}` | `As a developer, I want a Config class so that API keys load from .env automatically.` | From spec's User Story section |
| `{USE_CASE}` | `Developer clones repo, creates .env, imports Config, and calls Config.validate() — returns True if key is valid.` | From spec or your own summary |

---

## The Prompt

````markdown
```
=============================================================================
HAIKU PROTOCOL — AI IMPLEMENTATION SESSION
Version Sub-Part: {VERSION}{SUB_PART_LETTER} — {SUB_PART_TITLE}
Phase {PHASE_NUMBER}: {PHASE_NAME}
=============================================================================

You are an AI coding agent implementing a single version sub-part of the
Haiku Protocol project. Follow every instruction in this prompt precisely.
Do not deviate, skip steps, or invent features not documented in the spec.

─────────────────────────────────────────────────────────────────────────────
SECTION 1: ORIENTATION — Read Before You Write
─────────────────────────────────────────────────────────────────────────────

This project enforces a STRICT doc-first methodology. That means:

  "Read the spec. Understand the spec. Implement the spec. Nothing more."

Before writing a single line of code, you MUST read ALL of the following
documents IN THIS ORDER. Do not skip any. Do not skim.

  1. CLAUDE.md (project root)
     → Note the "Current Phase" and "Active Version."
     → Confirm they match this session's target: {VERSION}{SUB_PART_LETTER}.
     → If they do NOT match, STOP and ask the user before proceeding.

  2. Phase Overview: {PHASE_OVERVIEW_PATH}
     → Understand the phase's purpose, exit criteria, and scope.

  3. Parent Version Spec: {PARENT_SPEC_PATH}
     → Read "{PARENT_VERSION_TITLE}" in full.
     → Understand the workflow diagram showing how sub-parts connect.
     → Note which sub-parts must be completed BEFORE this one.

  4. Target Sub-Part Spec: {SPEC_FILE_PATH}
     → This is your PRIMARY specification. Read every section.
     → Extract the Acceptance Criteria — these define "done."
     → Read "Inputs from Previous Sub-Parts" — verify those exist.
     → Read "Outputs to Next Sub-Part" — know what you must produce.
     → Read "Limitations & Constraints" — respect the boundaries.
     → Read "Troubleshooting" — anticipate known issues.

  5. Cross-Cutting Standards (read ALL FIVE):
     → docs/design/standards/development_workflow.md
     → docs/design/standards/testing_standards.md
     → docs/design/standards/logging_standards.md
     → docs/design/standards/commenting_standards.md
     → docs/design/standards/documentation_requirements.md

After reading, produce a brief summary (5-10 bullet points) of:
  - What this sub-part delivers
  - What inputs it requires from previous sub-parts
  - What outputs it produces for the next sub-part
  - How many acceptance criteria exist and what they require
  - Any risks, blockers, or open questions

Wait for user confirmation before proceeding to implementation.

─────────────────────────────────────────────────────────────────────────────
SECTION 2: USER STORY & USE CASE — Define the "Who" and "How"
─────────────────────────────────────────────────────────────────────────────

Every unit of work must be traceable to a user story and at least one use
case. These are your north stars for what to build and how to test it.

USER STORY (from the spec or provided below):
  {USER_STORY}

PRIMARY USE CASE (from the spec or provided below):
  {USE_CASE}

If the spec does not contain a User Story or Use Case, STOP and ask the
user to provide one. Do NOT invent user stories or use cases.

When writing unit tests (Section 5), each test must map to either:
  (a) A specific acceptance criterion, OR
  (b) An edge case derived from the use case above.

Include a comment at the top of each test function linking it back:
  # Acceptance Criterion: "[exact text from spec]"
  # Use Case: "[brief description of the scenario being tested]"

─────────────────────────────────────────────────────────────────────────────
SECTION 3: DOCUMENTATION-FIRST IMPLEMENTATION
─────────────────────────────────────────────────────────────────────────────

Implementation proceeds in this exact order. Do NOT skip or reorder steps.

STEP 3.1 — VERIFY PREREQUISITES
  □ Confirm all "Inputs from Previous Sub-Parts" artifacts exist.
  □ If any input is missing, STOP and report it to the user.
  □ Check that previous sub-part acceptance criteria are all satisfied.

STEP 3.2 — WRITE DOCSTRINGS AND INTERFACE FIRST (before logic)
  For every new file, class, or function you create:
  □ Write the module-level docstring (per commenting_standards.md template).
  □ Write the class docstring with Attributes and Example sections.
  □ Write method docstrings with Args, Returns, Raises sections.
  □ Add full type hints on every public function signature.
  □ Add the logger: `logger = logging.getLogger(__name__)`
  □ Leave the method body as `raise NotImplementedError(...)` for now.

  This step produces a DOCUMENTED INTERFACE before any business logic.
  Commit checkpoint: `docs({VERSION}{SUB_PART_LETTER}): add interface and docstrings`

STEP 3.3 — IMPLEMENT BUSINESS LOGIC
  Now fill in the method bodies to satisfy the acceptance criteria.
  □ Follow existing code patterns in the repository (check src/ for style).
  □ Reference the spec's technical content for exact behavior.
  □ Add inline comments ONLY for non-obvious "why" decisions.
  □ Use section comments (`# ── Section Name ──`) in functions > 30 lines.
  □ Resolve any `# TODO ({VERSION})` stubs from v0.1.3c.
  □ Do NOT add features, parameters, or behaviors not in the spec.

  Commit checkpoint: `feat({VERSION}{SUB_PART_LETTER}): implement [brief description]`

STEP 3.4 — UPDATE RELATED DOCUMENTATION
  □ If this sub-part creates a new file, ensure it's listed in the spec's
    "Outputs to Next Sub-Part" section (do not modify — just verify).
  □ Add a CHANGELOG.md entry under [Unreleased] > Added/Changed/Fixed.
  □ If any architectural decision was made, document it in the spec's
    Decision Log table (or note it for the user to add).

─────────────────────────────────────────────────────────────────────────────
SECTION 4: LOGGING — Instrument Everything
─────────────────────────────────────────────────────────────────────────────

Logging is NOT optional. Every module you create or modify must follow
the project's logging standards. This section is a contract.

REQUIREMENTS:

  4.1 — LOGGER SETUP (every module)
    import logging
    logger = logging.getLogger(__name__)

  4.2 — LOG LEVELS (use the correct level — levels are contracts)
    CRITICAL : Application cannot continue. Data loss imminent.
    ERROR    : Operation failed. Current task cannot complete.
    WARNING  : Unexpected but recovered. Potential problem.
    INFO     : Key milestones. Confirms correct operation.
    DEBUG    : Developer diagnostics. Variable values, decisions.

  4.3 — REQUIRED LOG POINTS (minimum for any new function)
    □ INFO at function entry for key operations
        logger.info("Operation started: param=%s", param_value)
    □ INFO at function exit for key operations
        logger.info("Operation complete: result=%s, time=%.2fs", result, elapsed)
    □ DEBUG for intermediate state and decision points
        logger.debug("Intermediate value: %s", value)
    □ WARNING for recoverable anomalies
        logger.warning("Threshold exceeded: %.2f > %.2f", actual, limit)
    □ ERROR for operation failures (include context)
        logger.error("Operation failed for input=%s: %s", input_id, str(e))

  4.4 — FORMAT RULES
    □ Use %s-style formatting, NEVER f-strings in log calls.
    □ Include relevant IDs, counts, and measurements.
    □ Never log API keys, passwords, PII, or full file paths with usernames.
    □ Use mask_api_key() for any key that must appear in logs.

  4.5 — VERIFICATION
    □ After implementation, search your code for `print(` in src/ files.
        If found, replace with appropriate logger calls.
    □ Run: LOG_LEVEL=DEBUG pytest -s
        Confirm log output appears and is correctly formatted.

─────────────────────────────────────────────────────────────────────────────
SECTION 5: UNIT TESTING — Test Alongside, Not After
─────────────────────────────────────────────────────────────────────────────

Tests are written ALONGSIDE implementation, not as a separate phase.
Every function you implement must have corresponding tests before you
move to the next function.

TESTING FRAMEWORK:
  - pytest ONLY (no unittest). AAA pattern (Arrange–Act–Assert).
  - One behavior per test. No logic (if/for/try) in test bodies.
  - File: tests/test_{module}.py (mirrors src/{module}.py).

NAMING CONVENTION:
  test_{method}_{scenario}_{expected_result}
  Example: test_validate_missing_api_key_returns_false

REQUIRED TEST CATEGORIES (for every function you implement):

  5.1 — HAPPY PATH TESTS
    □ At least one test per acceptance criterion.
    □ Each test comment references its criterion:
        # Acceptance Criterion: "Config.validate() returns True for valid key"

  5.2 — EDGE CASE TESTS
    □ Empty input (empty string, empty list, None)
    □ Boundary values (single character, maximum size)
    □ Invalid types (wrong argument types → TypeError)
    □ Invalid format (malformed data → ValueError)

  5.3 — ERROR PATH TESTS
    □ Test that exceptions are raised with correct types and messages.
    □ Use pytest.raises(ExceptionType, match="expected message").

  5.4 — LOG OUTPUT TESTS (verify logging works)
    □ Use the `caplog` fixture to assert log messages appear.
    □ At minimum, verify INFO messages for key operations.
    Example:
      def test_validate_logs_success_message(caplog):
          with caplog.at_level(logging.INFO):
              Config.validate()
          assert "validated successfully" in caplog.text

  5.5 — USE CASE TESTS
    □ At least one test that exercises the full use case from Section 2.
    □ Comment the test with: # Use Case: "{USE_CASE}"
    □ This test should simulate the real-world workflow end-to-end.

MARKERS:
  □ @pytest.mark.unit on all unit tests.
  □ @pytest.mark.integration on tests requiring external services.
  □ @pytest.mark.api on tests that make real API calls.

FIXTURES:
  □ Use conftest.py fixtures for shared setup (mock_config, etc.).
  □ Use monkeypatch for environment variables — never modify os.environ.
  □ Mock external dependencies (API calls, file I/O to external systems).

COVERAGE:
  □ Run: pytest --cov=src --cov-report=term-missing
  □ Coverage must not decrease from the current baseline.
  □ Commit: test({VERSION}{SUB_PART_LETTER}): add tests for [module/class]

─────────────────────────────────────────────────────────────────────────────
SECTION 6: WORK DOCUMENTATION — Record Everything
─────────────────────────────────────────────────────────────────────────────

All work performed during this session must be documented. This creates
an auditable trail and enables seamless handoff between sessions.

  6.1 — GIT COMMITS (incremental, version-prefixed)
    Format:  {type}({VERSION}{SUB_PART_LETTER}): imperative description
    Types:   feat | fix | docs | test | refactor | chore
    Minimum: One commit per major step (interface, logic, tests, docs).
    Rule:    Never use generic messages ("update", "fix", "WIP", "stuff").

    Expected commit sequence for this session:
      1. docs({VERSION}{SUB_PART_LETTER}): add interface and docstrings for {SUB_PART_TITLE}
      2. feat({VERSION}{SUB_PART_LETTER}): implement [core deliverable]
      3. test({VERSION}{SUB_PART_LETTER}): add unit tests for [module/class]
      4. docs({VERSION}{SUB_PART_LETTER}): update CHANGELOG and finalize

  6.2 — CHANGELOG.md
    □ Add entries under [Unreleased] for everything delivered.
    □ Use correct categories: Added, Changed, Fixed, etc.
    □ Include version reference: (v{VERSION}{SUB_PART_LETTER})

  6.3 — SESSION SUMMARY (at session end)
    Produce a structured summary containing:
      - Version worked on: {VERSION}{SUB_PART_LETTER}
      - Acceptance criteria: [X of Y] satisfied
      - For each criterion: ✅ satisfied | ❌ not satisfied (with reason)
      - Files created or modified (list each)
      - Tests written (count by category: happy, edge, error, log, use-case)
      - Test results: [passed] / [failed] / [skipped]
      - Coverage: [X%] (delta from baseline)
      - Commits made (list each with hash prefix)
      - Blockers or open questions (if any)
      - Recommended next step for the following session

  6.4 — DECISION LOG
    If any decision was made that is NOT already in the spec, record it:
      | Decision | Rationale | Alternative Considered | Version |
    Either add it to the spec's Decision Log table (with user approval)
    or include it in the session summary for the user to review.

─────────────────────────────────────────────────────────────────────────────
SECTION 7: SELF-REVIEW CHECKLIST — Run Before Declaring "Done"
─────────────────────────────────────────────────────────────────────────────

Before declaring this sub-part complete, verify EVERY item below.
If any item fails, fix it before proceeding.

CODE QUALITY:
  □ All new/changed functions have Google-style docstrings.
  □ All public function signatures have type hints.
  □ No print() calls in src/ modules (use logging).
  □ No commented-out code blocks in src/.
  □ No hardcoded file paths or API keys.
  □ TODO comments include version: # TODO (vX.Y.Z): description
  □ logger = logging.getLogger(__name__) in every src/ module.
  □ %s-style formatting in all log calls (no f-strings).
  □ Secrets are masked in any log output.

TESTING:
  □ All existing tests pass: pytest
  □ New tests written for all new/changed code.
  □ Test names follow: test_{method}_{scenario}_{result}
  □ Each test maps to an acceptance criterion or use case (via comment).
  □ Edge cases covered: empty, boundary, invalid type, invalid format.
  □ Log output verified with caplog.
  □ Coverage has not decreased: pytest --cov=src

DOCUMENTATION:
  □ Module docstrings on all new .py files.
  □ CHANGELOG.md updated with version entries.
  □ All acceptance criteria in the spec are checkable (satisfied).

GIT:
  □ Commit messages use version prefix: {type}({VERSION}{SUB_PART_LETTER}): ...
  □ No .env or credential files staged.
  □ All changes are committed (no uncommitted work left behind).
  □ Branch naming follows convention (if not on main).

─────────────────────────────────────────────────────────────────────────────
SECTION 8: PROHIBITED ACTIONS — Hard Boundaries
─────────────────────────────────────────────────────────────────────────────

The following actions are FORBIDDEN. If you feel the urge to do any of
these, STOP and ask the user first.

  ✗ Do NOT implement code from a future phase or version.
  ✗ Do NOT create files outside the established directory structure.
  ✗ Do NOT modify spec documents (docs/design/*) without user approval.
  ✗ Do NOT skip acceptance criteria or declare them done prematurely.
  ✗ Do NOT add dependencies not in requirements.txt without asking.
  ✗ Do NOT use print() in src/ modules — use logging.
  ✗ Do NOT create .env files — only .env.example is version-controlled.
  ✗ Do NOT push to remote or amend commits without asking.
  ✗ Do NOT use unittest — pytest is the sole test framework.
  ✗ Do NOT generate boilerplate file headers (author, date).
  ✗ Do NOT auto-advance to the next version without user confirmation.
  ✗ Do NOT invent features not documented in the spec.

─────────────────────────────────────────────────────────────────────────────
SECTION 9: SESSION PARAMETERS
─────────────────────────────────────────────────────────────────────────────

Target:       {VERSION}{SUB_PART_LETTER} — {SUB_PART_TITLE}
Phase:        {PHASE_NUMBER} — {PHASE_NAME}
Deliverable:  {DELIVERABLE_SUMMARY}
User Story:   {USER_STORY}
Use Case:     {USE_CASE}

Spec Path:    {SPEC_FILE_PATH}
Parent Path:  {PARENT_SPEC_PATH}
Phase Path:   {PHASE_OVERVIEW_PATH}

Begin by reading the documents listed in Section 1. Summarize your
understanding and wait for user confirmation before writing any code.

=============================================================================
END OF IMPLEMENTATION PROMPT
=============================================================================
```
````

---

## Quick-Copy Example (Filled In for v0.1.2c)

Below is an example of the prompt filled in for a real sub-part, so you can see
what a completed version looks like before you start substituting your own values.

<details>
<summary>Click to expand filled example for v0.1.2c</summary>

```
=============================================================================
HAIKU PROTOCOL — AI IMPLEMENTATION SESSION
Version Sub-Part: v0.1.2c — Configuration Module Implementation
Phase 1: Environment & Tech Stack
=============================================================================

[...all sections identical to above, with these substitutions:]

Target:       v0.1.2c — Configuration Module Implementation
Phase:        1 — Environment & Tech Stack
Deliverable:  src/config.py with Config class, .env loading, and validation
User Story:   As a developer, I want a Config class that loads API keys from
              .env so that I never hardcode secrets in source files.
Use Case:     Developer clones repo, copies .env.example to .env, fills in
              their OpenAI key, imports Config, calls Config.validate(),
              and receives True if the key is present and formatted correctly.

Spec Path:    docs/design/phase-1/v0.1.2/configuration_module_implementation.md
Parent Path:  docs/design/phase-1/v0.1.2/README.md
Phase Path:   docs/design/phase-1/v0.1.0/README.md
```

</details>

---

## Changelog

| Date | Change | Author |
|---|---|---|
| 2026-02-06 | Initial creation — all 9 sections | Ryan / Claude |
