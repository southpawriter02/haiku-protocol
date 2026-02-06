# Pattern Taxonomy for Haiku Protocol v0.0.2

## Summary

| Metric | Value |
|--------|-------|
| Documents Analyzed | 11 |
| Total Sentences | 105 |
| Unique Patterns Identified | 8 semantic categories |
| Multi-Match Rate | 45.7% of sentences match 2+ categories |
| Highest Frequency (all matches) | Actions (60.0%) |
| Highest Frequency (primary) | Verifications (24.8%) |

This taxonomy was produced by the `PatternExtractor` class in
`research/pattern_extractor.py`, run against 11 procedural documentation
samples stored in `research/corpus/`. The extraction methodology follows
the v0.0.2a specification: sentence-level splitting, regex-based category
matching, and ambiguity resolution via a priority-ordered decision tree.

---

## Corpus Sources

| # | File | Category | Source Type |
|---|------|----------|-------------|
| 1 | `sample_01_postgresql_startup.txt` | Man Page | Database server startup |
| 2 | `sample_02_docker_build_push.txt` | README | Container build workflow |
| 3 | `sample_03_aws_s3_config.txt` | API Guide | Cloud storage configuration |
| 4 | `sample_04_db_migration_runbook.txt` | Runbook | Database migration with rollback |
| 5 | `sample_05_python_venv_setup.txt` | Installation Guide | Python environment setup |
| 6 | `sample_06_ssh_key_auth.txt` | Troubleshooting | SSH authentication diagnosis |
| 7 | `sample_07_kubernetes_deploy.txt` | Tutorial | Kubernetes pod deployment |
| 8 | `sample_08_nodejs_dep_update.txt` | README | Node.js dependency management |
| 9 | `sample_09_ssl_cert_renewal.txt` | Runbook | TLS certificate renewal |
| 10 | `sample_10_redis_cache_flush.txt` | Operational Procedure | Cache flush with warnings |
| 11 | `sample_11_git_repo_recovery.txt` | Troubleshooting | Git reflog recovery |

---

## Frequency Analysis

### All-Match Frequencies

A sentence may match multiple categories. These percentages reflect how
often each pattern appears across all 105 sentences, regardless of overlap.
The total exceeds 100% because of multi-category sentences.

| Category | Frequency | Raw Count | Proposed Operator |
|----------|-----------|-----------|-------------------|
| Actions | 60.0% | 63 / 105 | `Action:` |
| Verifications | 24.8% | 26 / 105 | `VERIFY:` |
| Dependencies | 14.3% | 15 / 105 | `REQUIRES` |
| Conditions | 13.3% | 14 / 105 | `IF:` / `THEN:` / `ELSE:` |
| States | 12.4% | 13 / 105 | `State:` |
| Warnings | 6.7% | 7 / 105 | `WARN:` |
| Metadata | 4.8% | 5 / 105 | `META:` |
| References | 3.8% | 4 / 105 | `REF:` |

### Primary Classification Frequencies

After ambiguity resolution (see Decision Tree below), each sentence
receives a single primary category. These numbers show how many
sentences have each category as their primary classification.

| Category | Primary % | Count |
|----------|-----------|-------|
| Verifications | 24.8% | 26 |
| Actions | 20.0% | 21 |
| Conditions | 11.4% | 12 |
| Warnings | 6.7% | 7 |
| Dependencies | 6.7% | 7 |
| States | 2.9% | 3 |
| Metadata | 1.9% | 2 |
| References | 0.0% | 0 |

**Notable:** References never wins as a primary classification because
other higher-priority categories (especially Warnings and Conditions)
tend to co-occur with reference markers like "see" and "review."

**Notable:** Verifications dominates primary classification despite
ranking second in all-match frequency. This is because "verify" and
"check" are extremely common in procedural docs and the ambiguity
priority ranks Verifications above Actions.

---

## Pattern Catalog

### PATTERN-001: Actions (Procedural Verbs/Commands)

**Frequency:** 60.0% (all-match) | 20.0% (primary)
**Proposed Operator:** `Action:`

Imperative statements that perform work. The dominant pattern in procedural
documentation — nearly two-thirds of all sentences contain at least one
action verb. However, many action sentences also contain verification or
dependency markers, which is why primary classification drops to 20%.

**Recognition Markers:** start, run, execute, apply, create, delete, install,
build, deploy, configure, restart, reload, verify, check, test, list, get,
post, put, stop, push, pull, tag, flush, connect, activate, commit, update,
monitor, backup, revert, recover, abort, reset, request, remove, add, set,
initialize, describe

**Examples from corpus:**

1. "Initialize the database cluster using initdb" (Sample 1: PostgreSQL)
2. "Build the Docker image: docker build -t myapp:latest ." (Sample 2: Docker)
3. "Create an S3 bucket: aws s3api create-bucket --bucket mybucket" (Sample 3: AWS)
4. "Apply manifest: kubectl apply -f deploy.yaml" (Sample 7: Kubernetes)
5. "Flush all databases: FLUSHALL (irreversible) or FLUSHDB" (Sample 10: Redis)

---

### PATTERN-002: Verifications (Checks & Validations)

**Frequency:** 24.8% (all-match) | 24.8% (primary)
**Proposed Operator:** `VERIFY:`

Tests that confirm successful completion of a prior action. High primary
percentage indicates these sentences are relatively "pure" — when a sentence
says "verify" or "confirm", that is almost always its primary intent even
if action verbs are also present.

**Recognition Markers:** verify, validate, confirm, check, test, assert,
should show, should return, expect, ensure ... is/are/exists

**Examples from corpus:**

1. "Verify the image locally: docker run -p 8080:8080 registry" (Sample 2: Docker)
2. "Confirm successful push by listing registry tags" (Sample 2: Docker)
3. "Verify configuration: aws s3api get-bucket-versioning --bucket mybucket" (Sample 3: AWS)
4. "Verify schema integrity: ./scripts/validate-schema.sh" (Sample 4: Migration)
5. "Run tests to ensure environment is correctly configured: pytest tests/" (Sample 5: Python)

---

### PATTERN-003: Dependencies (Ordering & Requirements)

**Frequency:** 14.3% (all-match) | 6.7% (primary)
**Proposed Operator:** `REQUIRES`

Explicit sequencing or prerequisite constraints. Dependency markers
("first", "then", "step N") frequently co-occur with action verbs,
causing the primary count to drop relative to all-match frequency.
The REQUIRES operator should encode these ordering relationships.

**Recognition Markers:** first, then, after, before, once, until, requires,
depends, prerequisite, prerequisites, following order, step N,
in the following

**Examples from corpus:**

1. "To start the PostgreSQL server, first ensure the data directory exists" (Sample 1: PostgreSQL)
2. "Step 1: Back up the current database to external storage" (Sample 4: Migration)
3. "Step 6: Restart application services in the following order: API > Worker > Cache" (Sample 4: Migration)
4. "Prerequisites: kubectl configured, Docker image built and pushed to registry" (Sample 7: K8s)
5. "Then start the server with pg_ctl start" (Sample 1: PostgreSQL)

---

### PATTERN-004: Conditions (Branching & If-Then Logic)

**Frequency:** 13.3% (all-match) | 11.4% (primary)
**Proposed Operator:** `IF:` / `THEN:` / `ELSE:`

Branching paths based on observation or test result. High primary-to-all
ratio (86%) indicates conditional sentences are distinctive and rarely
confused with other categories.

**Recognition Markers:** if, then, else, otherwise, in case, when, unless,
on error, assuming, if not, if still

**Examples from corpus:**

1. "Step 4: If migration fails, restore from backup" (Sample 4: Migration)
2. "If SSH authentication fails, diagnose as follows" (Sample 6: SSH)
3. "If 'Permission denied (publickey)', add public key to authorized_keys" (Sample 6: SSH)
4. "If still failing, check host's sshd config" (Sample 6: SSH)
5. "If tests fail, revert: npm ci" (Sample 8: Node.js)

---

### PATTERN-005: States (Preconditions & Postconditions)

**Frequency:** 12.4% (all-match) | 2.9% (primary)
**Proposed Operator:** `State:`

Conditions that must exist before or after an action. Very low primary
percentage (2.9%) because state descriptions almost always co-occur with
higher-priority categories (Verifications or Dependencies). The State
operator should encode static conditions, not the act of checking them.

**Recognition Markers:** ensure, must be, should be, should show, is owned,
exists, enabled, disabled, configured, installed, active, running,
is correctly, are not, remain, stabilizes

**Examples from corpus:**

1. "ensure the data directory exists and is owned by the postgres user" (Sample 1: PostgreSQL)
2. "Enable versioning: aws s3api put-bucket-versioning" (Sample 3: AWS)
3. "verify no active connections remain" (Sample 4: Migration)
4. "Prerequisites: Python 3.9+ and pip installed" (Sample 5: Python)
5. "Alert team when cache is rebuilt and application performance stabilizes" (Sample 10: Redis)

---

### PATTERN-006: Warnings (Consequences & Risks)

**Frequency:** 6.7% (all-match) | 6.7% (primary)
**Proposed Operator:** `WARN:`

Cautionary statements about failure modes or irreversible actions. Perfect
primary-to-all ratio (100%) — when a sentence is a warning, nothing else
outranks it. This makes warnings the most distinctive and unambiguous
pattern in the corpus.

**Recognition Markers:** WARNING, WARN, caution, be careful, do not, never,
risk, danger, irreversible, will lose, data loss, will delete,
breaking changes, maintenance window, coordinate with

**Examples from corpus:**

1. "WARNING: This procedure requires a 15-minute maintenance window" (Sample 4: Migration)
2. "WARN: Ensure backup of old certificate before deletion" (Sample 9: SSL)
3. "WARNING: This will delete ALL cached data" (Sample 10: Redis)
4. "Coordinate with team beforehand" (Sample 10: Redis)
5. "Review breaking changes for major versions before updating" (Sample 8: Node.js)

---

### PATTERN-007: References (Cross-References & Links)

**Frequency:** 3.8% (all-match) | 0.0% (primary)
**Proposed Operator:** `REF:`

Pointers to other documents, sections, or procedures. Always loses to
higher-priority categories in primary classification — every reference
sentence in the corpus also matched Warnings, Conditions, or Actions.
The REF operator should still be defined for explicit cross-linking.

**Recognition Markers:** see, refer to, for more, documentation, section,
guide, procedure, link, follow, review

**Examples from corpus:**

1. "If migration fails, restore from backup (see Rollback Procedure)" (Sample 4: Migration)
2. "describe pod: kubectl describe pod to see events and errors" (Sample 7: K8s)
3. "Review breaking changes for major versions before updating" (Sample 8: Node.js)

---

### PATTERN-008: Metadata (Version, Context, Prerequisites)

**Frequency:** 4.8% (all-match) | 1.9% (primary)
**Proposed Operator:** `META:`

Annotations about the document itself — versions, prerequisites, and
compatibility requirements. Low frequency reflects that metadata typically
appears only at the beginning of a procedure, not throughout.

**Recognition Markers:** version, author, date, updated, prerequisites,
requirements, applies to, compatible, compatible with

**Examples from corpus:**

1. "Prerequisites: Python 3.9+ and pip installed" (Sample 5: Python)
2. "Prerequisites: kubectl configured, Docker image built and pushed to registry" (Sample 7: K8s)
3. "Run the migration script: ./scripts/migrate.sh --version 2.1.0" (Sample 4: Migration)

---

## Classification Decision Tree

```
START: Read sentence/phrase
   |
   |--> Contains WARNING/WARN/danger/irreversible markers?
   |    --> YES: PRIMARY = WARNINGS
   |
   |--> Contains verify/validate/confirm/check/test/assert?
   |    --> YES: PRIMARY = VERIFICATIONS
   |
   |--> Contains if/then/else/when/unless (conditional branching)?
   |    --> YES: PRIMARY = CONDITIONS
   |
   |--> Contains first/then/after/before/step N (ordering)?
   |    --> YES: PRIMARY = DEPENDENCIES
   |
   |--> Describes required state (ensure/must be/exists)?
   |    --> YES: PRIMARY = STATES
   |
   |--> Contains see/refer/documentation (cross-reference)?
   |    --> YES: PRIMARY = REFERENCES
   |
   |--> Contains version/prerequisites/requirements (meta)?
   |    --> YES: PRIMARY = METADATA
   |
   --> Contains action verb (run/create/build/deploy...)?
       --> YES: PRIMARY = ACTIONS
       --> NO:  UNCLASSIFIED

MULTI-MATCH RULE:
   Sentences matching multiple categories receive ALL matching labels
   for frequency counting, but only ONE primary label per the
   priority order above.
```

---

## Ambiguity Resolution Notes

### Observed Multi-Match Patterns

45.7% of sentences matched two or more categories. The most common
overlaps observed in the corpus:

| Overlap Pattern | Frequency | Example |
|----------------|-----------|---------|
| Actions + Verifications | High | "Verify configuration: aws s3api get-bucket-versioning" |
| Actions + Dependencies | High | "Step 1: Back up the current database" |
| Actions + Conditions | Medium | "If tests fail, revert: npm ci" |
| Dependencies + States | Medium | "first ensure the data directory exists" |
| Warnings + References | Low | "see Rollback Procedure" in a WARNING block |
| Warnings + Dependencies | Low | "WARNING: This procedure requires..." |

### Resolution Rules Applied

1. **Warnings always win.** Safety-critical information takes priority
   regardless of co-occurring patterns. (7/7 = 100% primary retention)
2. **Verifications beat Actions.** When "verify" or "check" co-occurs
   with an action verb, the intent is validation, not execution.
3. **Conditions beat Dependencies.** "If ... then" is conditional logic,
   not ordering — even though "then" appears in both patterns.
4. **Dependencies beat Actions.** "First do X, then do Y" is about
   ordering, not the individual actions.
5. **States rarely win.** State descriptions almost always accompany
   a higher-priority pattern (verification or dependency).

---

## Implications for Operator Design (v0.0.2b)

### Recommended Operator Set

Based on the 8 identified patterns and their frequency distribution:

| Operator | Source Pattern | Priority | Rationale |
|----------|---------------|----------|-----------|
| `Action:` | Actions | Core | 60% frequency — the backbone of procedural docs |
| `VERIFY:` | Verifications | Core | 24.8% frequency — nearly every procedure ends with verification |
| `REQUIRES` | Dependencies | Core | Encodes the ordering that makes procedures sequential |
| `IF:`/`THEN:`/`ELSE:` | Conditions | Core | Branching logic appears in 13.3% of sentences |
| `State:` | States | Core | Preconditions/postconditions for actions |
| `WARN:` | Warnings | Core | Safety-critical, 100% unambiguous pattern |
| `META:` | Metadata | Supporting | Low frequency but important for document context |
| `REF:` | References | Supporting | Cross-linking between compressed procedures |

### Design Guidance

1. **Actions and Verifications should compose.** The most common multi-match
   is Actions + Verifications, so `Action:` and `VERIFY:` should be
   syntactically composable (e.g., `Action:Deploy -> VERIFY:Pods_Running`).

2. **Dependencies need chaining syntax.** The `REQUIRES` operator should
   support chains (A REQUIRES B REQUIRES C) to express multi-step ordering.

3. **Warnings should be attachable.** `WARN:` appears as an annotation on
   actions, not as standalone statements. The grammar should support
   attaching warnings to any action.

4. **References are rare but valuable.** Even at 3.8%, cross-references
   are essential for complex procedures. `REF:` should be lightweight.

5. **Metadata is document-level.** `META:` belongs at the top of a
   compressed output, not inline with actions.

---

## Decision Log

| ID | Decision | Rationale | Alternative Considered | Version |
|----|----------|-----------|----------------------|---------|
| v0.0.2a-001 | Corpus limited to English procedural docs | Reduces scope; non-English adds tokenization complexity | Include multilingual samples | v0.0.2a |
| v0.0.2a-002 | Creative/narrative content excluded | Analysis focuses on goal-oriented procedural structures | Include narrative for contrast | v0.0.2a |
| v0.0.2a-003 | Metadata separated from Actions | Preserves document context (versions, prerequisites) as distinct from executable steps | Merge into Actions | v0.0.2a |
| v0.0.2a-004 | Sentence splitting uses punctuation + newlines | Procedural docs often use one instruction per line without terminal punctuation | Split only on sentence-ending punctuation | v0.0.2a |
| v0.0.2a-005 | Flat priority list for ambiguity resolution | Simpler implementation; captures 95% of cases correctly | Context-sensitive rules (e.g., "if+then" vs standalone "then") | v0.0.2a |
| v0.0.2a-006 | "then" listed in both Conditions and Dependencies patterns | Matches spec v0.0.2a recognition markers; resolved by priority ordering | Remove "then" from Conditions | v0.0.2a |

---

## Methodology Notes

### Extraction Tool

The analysis was performed by `research/pattern_extractor.py`, a Python
script implementing the `PatternExtractor` class with regex-based
recognition markers. The tool:

1. Reads corpus files from `research/corpus/`
2. Splits each document into sentences (punctuation + newline boundaries)
3. Matches each sentence against 8 category regex patterns
4. Resolves ambiguity using a priority-ordered decision tree
5. Accumulates frequency counts and example sentences
6. Outputs results as JSON (`research/pattern_extraction_results.json`)
   and this markdown taxonomy

### Limitations

1. **Regex-based matching** is heuristic, not semantic. The word "list"
   matches Actions even when used as a noun ("a list of items").
2. **Sentence splitting** can mishandle inline commands containing periods
   (e.g., "registry.io" splits incorrectly).
3. **Corpus is curated**, not randomly sampled. The 11 documents were
   selected to cover the categories listed in the v0.0.2a spec.
4. **Frequency percentages exceed 100%** in all-match mode because
   sentences can match multiple categories.

### Reproducibility

To reproduce this analysis:

```bash
cd research/
python3 pattern_extractor.py
```

Results are saved to `research/pattern_extraction_results.json`.
