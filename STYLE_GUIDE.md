# Haiku Protocol — CNL Grammar Style Guide

> **Status:** Draft (v0.0.2c)
>
> **Purpose:** Documents the Controlled Natural Language grammar that defines valid
> compression output for the Haiku Protocol. This is the authoritative reference
> for how procedural documentation is encoded into haiku format.
>
> **Audience:** Grammar engineers, parser implementers, documentation encoders
>
> **Formal Grammar:** `research/haiku_grammar.bnf`
>
> **Operator Reference:** `research/operator_reference.md`

---

## Grammar Overview

The Haiku Protocol grammar uses 12 operators to encode procedural documentation
into dense, machine-optimized strings. The grammar is specified in Extended
Backus-Naur Form (EBNF) and is designed to be unambiguous, left-recursion free,
and parseable by standard tools.

A valid haiku string consists of an optional metadata block followed by one or
more statements separated by semicolons:

```
<haiku> ::= <metadata_block>? <statement_block>
```

---

## Operator Quick Reference

| Operator | Symbol | Purpose | Precedence |
|----------|--------|---------|------------|
| Action | `Action:` / `A:` | Procedural step (imperative verb) | 5 |
| State | `State:` / `S:` | Precondition or postcondition | 6 |
| REQUIRES | `REQUIRES` | Dependency declaration | 7 |
| EXEC | `-> EXEC:` / `->` | Concrete command attachment | 4 |
| IF/THEN/ELSE | `IF:` `THEN:` `ELSE:` | Conditional branching | 3 |
| WARN | `WARN:` | Risk/consequence declaration | 5 |
| VERIFY | `VERIFY:` | Post-action check | 5 |
| SEQ | `;` | Sequential statement separator | 2 |
| REF | `REF:` | Cross-reference to external doc | 8 |
| META | `META:` | Metadata annotation (key=value) | 9 |
| LOOP | `LOOP:` | Repetition/iteration | 3 |
| NOTE | `NOTE:` | Non-critical commentary | 10 |

---

## Naming Conventions

### Identifiers (Actions, States, References)

Format: `PascalCase_With_Underscores`

```
Action:Backup_Database        (valid)
State:Config_Valid            (valid)
Action:backup_database        (invalid — lowercase)
State:ConfigValid             (invalid — missing underscore)
```

### Commands (in EXEC)

Format: `lowercase shell syntax`

```
EXEC:docker build -t myapp:latest .          (valid)
EXEC:kubectl apply -f deploy.yaml            (valid)
EXEC:MYCOMMAND                               (invalid — uppercase)
```

### Metadata Keys (in META)

Format: `lowercase_with_underscores`

```
META:compatible_with=PostgreSQL_12+           (valid)
META:version=1.0                              (valid)
META:AuthorName=Jane                          (invalid — mixed case key)
```

---

## Composition Rules

### Rule 1: Sequential Composition

Statements compose left-to-right with semicolons. Execution proceeds in order.

```
Action:Backup; Action:Deploy; VERIFY:Running
```

### Rule 2: Dependency Composition

REQUIRES preconditions must be satisfied before Action executes. All states
in the list use AND semantics.

```
Action:Deploy REQUIRES State:Config_Valid, State:DB_Online
```

### Rule 3: Conditional Composition

IF/THEN/ELSE branches based on named conditions. ELSE is optional.

```
IF:Deploy_Success THEN:Action:Verify ELSE:Action:Rollback
```

### Rule 4: Command Attachment

EXEC follows Action via arrow notation. The command is greedy-matched.

```
Action:Deploy -> EXEC:docker push registry.io/myapp:latest
```

### Rule 5: Verification Composition

VERIFY follows Action/EXEC and checks success.

```
Action:Deploy -> EXEC:deploy.sh; VERIFY:Service_Running
```

### Rule 6: Warning Composition

WARN attaches to Actions and declares cause-consequence pairs.

```
Action:Delete WARN:No_Recovery -> Data_Loss
```

### Rule 7: Metadata Composition

META appears at the beginning of a haiku. Multiple META clauses allowed.

```
META:version=1.0; META:author=DevOps; Action:Deploy
```

### Rule 8: Loop Composition

LOOP wraps a statement with a count or WHILE condition.

```
LOOP:3:Action:Retry -> EXEC:attempt.sh
LOOP:WHILE:Service_Unhealthy:Action:Check_Status
```

---

## Encoding Examples

### Simple Backup Procedure

**Before:**
> Back up the database if it's online, then verify the backup exists.

**After:**
```
Action:Backup_DB REQUIRES State:DB_Online -> EXEC:backup.sh; VERIFY:Backup_File_Exists
```

### Conditional Deployment

**Before:**
> Deploy the service. If deployment succeeds, verify it's running. Otherwise, rollback.

**After:**
```
Action:Deploy -> EXEC:deploy.sh; IF:Deploy_Success THEN:Action:Verify_Service ELSE:Action:Rollback
```

### Migration Runbook

**Before:**
> WARNING: This requires a maintenance window. Back up the database, stop services,
> run the migration, and restart in order. If migration fails, restore from backup.

**After:**
```
META:requires=maintenance_window; WARN:Skip_Backup -> Data_Loss; Action:Backup -> EXEC:backup.sh; Action:Stop_Services; Action:Migrate -> EXEC:migrate.sh; IF:Migration_Fail THEN:Action:Restore_Backup ELSE:Action:Restart_Services; VERIFY:Schema_Valid
```

---

## Ambiguity Resolution

When parsing encounters overlapping operators, apply these rules in order:

1. **Operator precedence** — Higher-precedence operators bind first (EXEC tightest, NOTE loosest)
2. **Greedy command matching** — EXEC consumes all characters until next operator or semicolon
3. **State list conjunction** — Multiple REQUIRES states use AND semantics
4. **THEN/ELSE sequential** — Multiple items in THEN/ELSE execute sequentially
5. **Semicolon primacy** — Semicolon separates statements; comma separates within clauses

---

## Terminology

| Term | Definition |
|------|-----------|
| Haiku | A compressed representation of a procedural document |
| Operator | A keyword that encodes a specific semantic pattern |
| Statement | A complete instruction (Action, IF, LOOP, etc.) |
| Clause | A modifier attached to a statement (REQUIRES, EXEC, WARN) |
| Identifier | A named reference (PascalCase_With_Underscores) |
| Token | A single lexical unit produced by the tokenizer |
| Production | A rule in the BNF grammar |

---

## Related Documents

- [Operator Reference](research/operator_reference.md) — Full specifications for all 12 operators
- [BNF Grammar](research/haiku_grammar.bnf) — Formal EBNF grammar file
- [Pattern Taxonomy](research/pattern_taxonomy.md) — Corpus analysis that informed operator design
