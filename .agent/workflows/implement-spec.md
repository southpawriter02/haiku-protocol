---
description: Comprehensive workflow for implementing a design or product specification
---

# /implement-spec — Design/Product Specification Implementation Workflow

> **Scope:** Generic template — applicable to any project with versioned design specs.
> **Purpose:** Ensures every implementation session maintains context, produces documentation,
> includes tests, implements proper logging, and creates an auditable trail of work.

---

## Prerequisites

Before beginning, confirm you have:

- [ ] Access to the specification document(s) for the target version
- [ ] Access to any parent/phase-level overview documents
- [ ] A working development environment (compiles/runs without errors)
- [ ] All tests passing on the current branch
- [ ] Knowledge of the project's standards documents (testing, logging, documentation, etc.)

---

## Phase 1: Orientation — Read Before You Write

**Goal:** Build full contextual understanding before touching any code.

### Step 1.1 — Identify the Target

1. Determine the exact version/feature to implement.
2. Locate the primary specification document.
3. Locate the parent-level overview (phase, epic, milestone).
4. Confirm the project's "current version" or "active work item" marker matches your target.
   - If they do NOT match, **STOP** and clarify with the user before proceeding.

### Step 1.2 — Read the Full Specification

Read the spec documents **in this order**. Do not skip or skim.

1. **Project rules file** (e.g., `CLAUDE.md`, `CONTRIBUTING.md`, `.cursor/rules`)
   - Note current phase, active version, prohibited actions.
2. **Parent/phase overview**
   - Understand scope, exit criteria, and how this version fits the bigger picture.
3. **Target version spec** (the primary document you're implementing)
   - Extract **acceptance criteria** — these define "done."
   - Note **inputs from prior work** — verify they exist.
   - Note **outputs to subsequent work** — know what you must produce.
   - Note **limitations & constraints** — respect the boundaries.
   - Note **troubleshooting** — anticipate known issues.
4. **Cross-cutting standards** (testing, logging, commenting, documentation)
   - These are contracts, not suggestions.

### Step 1.3 — Produce an Orientation Summary

Before writing any code, produce a structured summary:

- What this version delivers (one sentence)
- What inputs it requires from previous work (list each)
- What outputs it produces for subsequent work (list each)
- How many acceptance criteria exist and what they require
- Any risks, blockers, or open questions

**Wait for user confirmation before proceeding to implementation.**

---

## Phase 2: Planning — Define Scope and Approach

**Goal:** Create a clear implementation plan before writing production code.

### Step 2.1 — Verify Prerequisites

- [ ] Confirm all inputs from prior work actually exist (files, modules, configs).
- [ ] If any input is missing, **STOP** and report it to the user.
- [ ] Confirm all prior acceptance criteria are satisfied.
- [ ] Confirm the build is clean and all existing tests pass.

### Step 2.2 — Create an Implementation Plan

Write a concise plan covering:

| Section                     | Contents                                                                 |
| --------------------------- | ------------------------------------------------------------------------ |
| **Goal**                    | One-sentence description of the deliverable                              |
| **User Story**              | Who benefits and how — trace every test back to this                     |
| **Files to Create/Modify**  | List every file with the expected change type (new, modify, delete)      |
| **Dependency Order**        | If files depend on each other, specify the build order                   |
| **Acceptance Criteria Map** | Map each acceptance criterion to the file(s) and test(s) that satisfy it |
| **Risk/Unknowns**           | Anything that could block or change the approach                         |
| **Verification Plan**       | Exact commands to run, expected outputs                                  |

### Step 2.3 — Confirm the Plan

Present the plan to the user. Wait for approval before proceeding.

> **DO:** Ask targeted questions. "Should X use pattern A or B?"
> **DON'T:** Ask for blanket approval. "Is this okay?" is too vague.

---

## Phase 3: Documentation-First Implementation

**Goal:** Write interfaces and documentation before business logic.

### Step 3.1 — Write Interfaces First (Skeleton Pass)

For every new file, class, or function:

- [ ] Write the module-level docstring (purpose, author intent, version reference).
- [ ] Write class docstrings with Attributes and Example sections.
- [ ] Write method docstrings with Args, Returns, Raises sections.
- [ ] Add full type hints on every public function signature and return type.
- [ ] Add the logger declaration (language-specific).
- [ ] Leave method bodies as `raise NotImplementedError(...)` or equivalent stubs.

This step produces a **documented interface** before any business logic.

**Commit checkpoint:**

```
docs({version}): add interface and docstrings for {feature}
```

### Step 3.2 — Implement Business Logic

Now fill in the method bodies to satisfy the acceptance criteria:

- [ ] Follow existing code patterns in the repository (consistency > novelty).
- [ ] Reference the spec's technical content for exact behavior.
- [ ] Add inline comments ONLY for non-obvious "why" decisions.
- [ ] Use section comments in functions > 30 lines.
- [ ] Resolve any `TODO` stubs from prior versions.
- [ ] **Do NOT add features, parameters, or behaviors not in the spec.**

**Commit checkpoint:**

```
feat({version}): implement {brief description}
```

### Step 3.3 — Write Tests Alongside (Not After)

Tests are written **alongside** implementation, not as a separate phase.
Every function you implement must have corresponding tests before you
move to the next function.

#### Required Test Categories

| Category                   | Description                                                                  | Minimum                 |
| -------------------------- | ---------------------------------------------------------------------------- | ----------------------- |
| **Happy Path**             | One test per acceptance criterion, linked via comment                        | 1 per criterion         |
| **Edge Cases**             | Empty input, boundary values, invalid types/format                           | 3–5 per function        |
| **Error Paths**            | Exceptions raised with correct types and messages                            | 1–2 per error condition |
| **Log Output**             | Verify log messages appear at expected levels (use appropriate test fixture) | 1–2 per key operation   |
| **Use Case / Integration** | Full end-to-end workflow matching the user story                             | 1 per user story        |

#### Test Rules

- **One behavior per test.** No logic (`if`/`for`/`try`) in test bodies.
- **Descriptive names:** `test_{method}_{scenario}_{expected_result}`
- **AAA pattern:** Arrange → Act → Assert.
- **Link to criteria:** Each test comment references its acceptance criterion or use case.
- **Markers/tags:** Categorize tests (unit, integration, api, slow) for selective running.
- **Fixtures:** Use shared fixtures for repeated setup; mock external dependencies.
- **Coverage:** Must not decrease from the current baseline.

**Commit checkpoint:**

```
test({version}): add unit tests for {module/class}
```

---

## Phase 4: Logging — Instrument Everything

**Goal:** Every module has structured, level-appropriate log output.

### Required Log Points

For every new or modified function:

| Level        | When                                    | Example                                       |
| ------------ | --------------------------------------- | --------------------------------------------- |
| **INFO**     | Function entry for key operations       | `"Operation started: param=%s"`               |
| **INFO**     | Function exit for key operations        | `"Operation complete: result=%s, time=%.2fs"` |
| **DEBUG**    | Intermediate state and decision points  | `"Intermediate value: %s"`                    |
| **WARNING**  | Recoverable anomalies                   | `"Threshold exceeded: %.2f > %.2f"`           |
| **ERROR**    | Operation failures (include context)    | `"Operation failed for input=%s: %s"`         |
| **CRITICAL** | Application cannot continue / data loss | `"Fatal: cannot write to %s"`                 |

### Logging Rules

- [ ] Use parameterized formatting (e.g., `%s`-style, structured logging), **never** string interpolation in log calls.
- [ ] Include relevant IDs, counts, and measurements in log messages.
- [ ] **Never** log secrets, API keys, PII, or full file paths containing usernames.
- [ ] Use a masking utility for any sensitive value that must appear in logs.
- [ ] No `print()` or `console.log()` for diagnostic output in production code — use the logger.

### Logging Verification

- [ ] Search for `print(` / `console.log(` in source files. Replace any found.
- [ ] Run with verbose/debug log level and confirm output is correctly formatted.

---

## Phase 5: Documentation Updates

**Goal:** All documentation artifacts are current before declaring "done."

### Required Documentation Updates

| Artifact                    | Action                                                                                  |
| --------------------------- | --------------------------------------------------------------------------------------- |
| **Changelog**               | Add entries under `[Unreleased]` → `Added` / `Changed` / `Fixed` with version reference |
| **Help Guides / README**    | If user-facing behavior changed, update usage instructions                              |
| **Architecture / Overview** | If module relationships changed, update diagrams and text                               |
| **Decision Log / ADR**      | If a technical decision was made, document it with context, options, and rationale      |
| **API Reference**           | If public interfaces changed, update signatures and examples                            |
| **Configuration Docs**      | If new config values were added, document defaults, types, and constraints              |

### Changelog Entry Format

Follow [Keep a Changelog](https://keepachangelog.com/) conventions:

```markdown
## [Unreleased]

### Added

- Description of new feature with function/class names and version reference (vX.Y.Za)

### Changed

- Description of changed behavior (vX.Y.Za)

### Fixed

- Description of bug fix with root cause (vX.Y.Za)
```

**Commit checkpoint:**

```
docs({version}): update changelog and finalize
```

---

## Phase 6: Self-Review Checklist

**Goal:** Verify completeness before declaring the version done.

Run this checklist **before** marking any acceptance criteria as complete.

### Code Quality

- [ ] All new/changed functions have complete docstrings.
- [ ] All public function signatures have type hints / type annotations.
- [ ] No `print()` / `console.log()` in production source code.
- [ ] No commented-out code blocks in production source code.
- [ ] No hardcoded file paths, API keys, or credentials.
- [ ] TODO comments include version references: `# TODO (vX.Y.Z): description`
- [ ] Logger initialized in every production source module.
- [ ] Parameterized formatting in all log calls (no string interpolation).
- [ ] Secrets masked in any log output.

### Testing

- [ ] All existing tests pass.
- [ ] New tests written for all new/changed code.
- [ ] Test names follow naming convention.
- [ ] Each test maps to an acceptance criterion or use case (via comment).
- [ ] Edge cases covered: empty, boundary, invalid type, invalid format.
- [ ] Log output verified with appropriate test fixture.
- [ ] Coverage has not decreased from baseline.

### Documentation

- [ ] Module/file-level docstrings on all new files.
- [ ] Changelog updated with version entries.
- [ ] All acceptance criteria in the spec are satisfiable and verified.
- [ ] Help guides / README updated if user-facing behavior changed.
- [ ] Decision log updated if architectural decisions were made.

### Version Control

- [ ] Commit messages use version prefix: `{type}({version}): description`
- [ ] No secrets or credential files staged.
- [ ] All changes are committed (no uncommitted work left behind).
- [ ] Branch naming follows project convention.

---

## Phase 7: Session Summary

**Goal:** Produce a structured handoff document for continuity.

At the end of every implementation session, produce:

| Field                         | Contents                                                  |
| ----------------------------- | --------------------------------------------------------- |
| **Version Worked On**         | Exact version identifier                                  |
| **Acceptance Criteria**       | `[X of Y]` satisfied — list each with ✅ or ❌ and reason |
| **Files Created / Modified**  | List each with change type                                |
| **Tests Written**             | Count by category: happy, edge, error, log, use-case      |
| **Test Results**              | `[passed] / [failed] / [skipped]`                         |
| **Coverage**                  | `[X%]` (delta from baseline)                              |
| **Commits Made**              | List each with hash prefix and message                    |
| **Blockers / Open Questions** | Anything unresolved                                       |
| **Recommended Next Step**     | What the next session should start with                   |
| **Decisions Made**            | Any decisions not already in the spec's Decision Log      |

---

## Dos and Don'ts

### ✅ Do

- Read the spec **before** writing any code.
- Follow acceptance criteria as your definition of done.
- Ask the user before deviating from the spec.
- Write tests alongside implementation, not after.
- Commit at logical checkpoints with version-prefixed messages.
- Use existing patterns from the codebase as templates.
- Verify prerequisites exist before starting.
- Update the changelog with every version's deliverables.
- Keep project tracking markers (active version, current phase) current.
- Reference version numbers in TODO comments, commit messages, and log messages.
- End sessions with a clear summary and next-step recommendation.
- Write documentation as you go — it's a deliverable, not an afterthought.
- Use structured logging at every lifecycle boundary (entry, exit, error, decision).
- Map every test to an acceptance criterion or user story.

### ❌ Don't

- Implement features from a future phase or version.
- Create files outside the established directory structure without approval.
- Modify specification documents without user approval.
- Skip acceptance criteria or mark them done prematurely.
- Add dependencies without asking.
- Make architectural decisions not covered by the spec without asking.
- Leave uncommitted work at session end without documenting it.
- Use generic commit messages ("update", "fix stuff", "WIP").
- Assume context from a previous session — re-read the spec.
- Ignore test failures and proceed to the next version.
- Auto-advance to the next phase without explicit user confirmation.
- Use `print()` / `console.log()` for diagnostics — use the logger.
- Generate boilerplate file headers (author, date) — use VCS metadata.
- Invent features not documented in the spec.
- Write documentation you won't maintain.
- Duplicate information across multiple documents — link instead.
- Skip the self-review checklist.

---

## Quick Reference: Commit Message Convention

```
{type}({version}): imperative description (<72 chars)

Optional body with details:
- Detail bullet 1
- Detail bullet 2
```

| Type       | When                                    |
| ---------- | --------------------------------------- |
| `feat`     | New functionality                       |
| `fix`      | Bug fix                                 |
| `docs`     | Documentation only                      |
| `test`     | Test additions/changes                  |
| `refactor` | Code restructuring (no behavior change) |
| `chore`    | Build, config, tooling                  |

---

## Quick Reference: Acceptance Criteria Traceability

Every acceptance criterion should be traceable through:

```
Spec Criterion → Implementation Code → Unit Test → Changelog Entry
```

In tests, link back with comments:

```
# Acceptance Criterion: "[exact text from spec]"
# Use Case: "[brief description of the scenario being tested]"
```

---

## Quick Reference: What to Do When Stuck

| Situation                            | Action                                                              |
| ------------------------------------ | ------------------------------------------------------------------- |
| Spec is ambiguous                    | Re-read the Objective and User Story. Still unclear → ask the user. |
| Prerequisite missing                 | Go back and complete it before proceeding.                          |
| Criterion seems impossible           | Document why, propose an alternative, get user approval.            |
| External dependency broken           | Check the spec's Troubleshooting section. If no entry, add one.     |
| Test suite is failing                | Fix failing tests before writing new code.                          |
| Don't know which version to work on  | Check the project's "active version" marker.                        |
| Session ending with work in progress | Commit what you have, summarize status, note next step.             |
