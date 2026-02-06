# Operator Reference for Haiku Protocol v0.0.2b

## Summary

- **Total Operators:** 12 (10 required + 2 bonus)
- **Coverage:** Maps all 8 semantic categories from v0.0.2a corpus analysis
- **Precedence Levels:** 2–10
- **Design Principle:** Minimal ambiguity, maximum composability
- **Implementation Status:** Complete specification with syntax, semantics, examples, and composition rules

---

## Methodology

The operators defined in this reference were systematically derived from v0.0.2a's analysis of procedural documentation. The Pattern Taxonomy identified 8 core semantic categories through corpus analysis of 11 technical documents covering PostgreSQL, Docker, AWS, Kubernetes, Python, SSH, certificate management, and more.

Each operator maps directly to one or more of these semantic categories, ensuring that Haiku Protocol operators encode real, observable patterns from actual technical procedures rather than theoretical constructs.

---

## Pattern-to-Operator Mapping

The following table shows how each v0.0.2a semantic category maps to operator(s):

| v0.0.2a Pattern | Frequency | Primary % | Mapped Operator(s) | Notes |
|---|---|---|---|---|
| Actions | 60.0% | 20.0% | `Action:` | Core unit of all procedures; can combine with EXEC |
| Verifications | 24.8% | 24.8% | `VERIFY:` | Post-action checks; highest primary frequency |
| Dependencies | 14.3% | 6.7% | `REQUIRES` | Ordering and prerequisites; often co-occurs with Actions |
| Conditions | 13.3% | 11.4% | `IF:`/`THEN:`/`ELSE:` | Branching logic; distinctive pattern |
| States | 12.4% | 2.9% | `State:` | Preconditions/postconditions; usually co-occurs with Dependencies |
| Warnings | 6.7% | 6.7% | `WARN:` | Safety-critical; 100% unambiguous pattern |
| Metadata | 4.8% | 1.9% | `META:` | Version, author, prerequisites; document-level |
| References | 3.8% | 0.0% | `REF:` | Cross-references; always co-occurs with higher-priority patterns |

**Additional Operators** (not mapped to primary patterns but essential for composition):

| Operator | Purpose | Rationale |
|---|---|---|
| `EXEC:` | Command execution payload | Separates action name from executable command |
| `SEQ:` | Sequential ordering | Explicit sequencing (semicolon is implicit form) |
| `LOOP:` (bonus) | Repetition/retry logic | Encodes retry patterns observed in procedures |
| `NOTE:` (bonus) | Non-critical documentation | Distinguishes tips from warnings |

---

## Operator Catalog

### OP-001: Action

**Name:** Action (Procedural Step)

**Symbol:** `Action:` or `A:`

**Syntax:**
```
<action>       ::= 'Action:' <identifier> <args>?
<identifier>   ::= [A-Za-z_][A-Za-z0-9_]*
<args>         ::= '(' <command> ')' | '[' <command> ']'
<command>      ::= [^\s;,\]\)]+ (optional executable code)
```

**Semantics:**

Denotes a single imperative procedure step. Represents any action verb (run, create, deploy, etc.). Actions are the fundamental building blocks of Haiku procedures. Every procedure contains at least one action. Actions execute with sequential guarantees unless otherwise modified by REQUIRES, IF, or LOOP operators.

**Example 1:**
```
BEFORE:
"To restart the server, run the restart command."

AFTER:
Action:Restart_Server [restart_cmd]
```

**Example 2:**
```
BEFORE:
"Install all dependencies from requirements file."

AFTER:
Action:Install_Dependencies (pip install -r requirements.txt)
```

**Precedence:** 5

**Composable With:** REQUIRES, EXEC, THEN, SEQ, VERIFY, WARN, IF, LOOP, META

**Edge Cases:**

1. **Action with no arguments:** `Action:ConfigBackup` (implicit action name, no command payload; used when procedure step is implied)
2. **Action with complex command:** `Action:Deploy (docker build -t image:$(git rev-parse --short HEAD) .)`  (variables and subshells in command)
3. **Action with variable reference:** `Action:Start_Service [$SERVICE_NAME]` (variable substitution at encoding time)

**Notes:**

Actions are the fundamental unit. Every procedure contains at least one action. Variables in square brackets `[$VAR]` are substituted at encoding time. Commands in parentheses are optional but encouraged for clarity. Actions without EXEC are implicitly named procedures whose execution is defined elsewhere (e.g., in a runbook reference or external script).

**Composition Example:**
```
Action:Backup REQUIRES State:DB_Online -> Action:Deploy
Action:Install_Dependencies; Action:Build_Service; Action:Deploy
```

---

### OP-002: State

**Name:** State (Precondition/Postcondition)

**Symbol:** `State:` or `S:`

**Syntax:**
```
<state>        ::= 'State:' <identifier>
<identifier>   ::= [A-Za-z_][A-Za-z0-9_]*
```

**Semantics:**

Declares a required or achieved condition. Represents binary or categorical states (online/offline, exists/missing, configured/unconfigured). Used in REQUIRES clauses to specify preconditions; used in postcondition verification to confirm success. States are immutable snapshots of system condition.

**Example 1:**
```
BEFORE:
"The database must be online before backup can proceed."

AFTER:
State:DB_Online
```

**Example 2:**
```
BEFORE:
"After successful installation, the service is active and running."

AFTER:
State:Service_Active, State:Service_Running
```

**Precedence:** 6

**Composable With:** REQUIRES, IF, THEN, VERIFY, WARN

**Edge Cases:**

1. **Negated state:** `State:NOT_DB_Online` (convention for negation; negation convention is underscore-prefixed NOT_)
2. **Composite state:** `State:DB_Online AND Auth_Configured` (semantic composition implied by multiple states)
3. **Time-bound state:** `State:Config_Valid_For_30_Days` (metadata embedded in state name)

**Notes:**

States are immutable snapshots of system condition. Multiple states can be required simultaneously (AND implicit). No state name should exceed 32 characters. Use `_` for word boundaries. State names should describe observable conditions, not the process of checking them.

**Composition Example:**
```
Action:Backup REQUIRES State:DB_Online, State:Storage_Available
IF:Migration_Success THEN:State:Schema_Valid ELSE:Action:Restore_Backup
```

---

### OP-003: REQUIRES

**Name:** Dependency Declaration

**Symbol:** `REQUIRES`

**Syntax:**
```
<dependency>   ::= 'REQUIRES' <state_list>
<state_list>   ::= <state> (',' <state>)*
```

**Semantics:**

Declares that an action cannot execute until specified states are true. Establishes a precondition barrier. All states in the list must be satisfied (AND semantics). Failure to meet any REQUIRES state should abort the action and trigger error handling. REQUIRES creates hard dependencies unlike softer WARN advisories.

**Example 1:**
```
BEFORE:
"Before you can deploy, the database must be backed up,
the schema must be validated, and the service must be offline."

AFTER:
Action:Deploy REQUIRES State:DB_Backed_Up, State:Schema_Valid, State:Service_Offline
```

**Example 2:**
```
BEFORE:
"Configuration requires that the user has sudo privileges and
the config file exists."

AFTER:
Action:Configure REQUIRES State:User_Has_Sudo, State:Config_File_Exists
```

**Precedence:** 7 (binds tighter than action)

**Composable With:** Action, EXEC, IF, LOOP

**Edge Cases:**

1. **No states required:** Omit REQUIRES clause entirely; no error results
2. **Optional requirements:** Use NOTE or conditional REQUIRES (inside IF) instead of hard REQUIRES
3. **Conditional requirements:** Nest REQUIRES inside IF: `IF:Production THEN:Action:Deploy REQUIRES State:Backup_Complete`

**Notes:**

REQUIRES creates hard dependencies. Use WARNING for soft constraints. If any state is not verifiable, document as a NOTE. The absence of REQUIRES does not imply no dependencies; it implies the decoder must determine dependencies from context or external configuration.

**Composition Example:**
```
Action:Upgrade_DB REQUIRES State:Backup_Complete, State:DB_Idle -> EXEC:migration_script
```

---

### OP-004: EXEC

**Name:** Command Execution

**Symbol:** `EXEC:` or `->`

**Syntax:**
```
<execution>    ::= '->' 'EXEC:' <command>
<command>      ::= [^\s;]+
```

**Semantics:**

Attaches a concrete, executable command to an action. The command is the shell/script invocation that performs the work. Syntax varies by platform (bash, Python, SQL, etc.). EXEC is optional; present if command needs explicit encoding. EXEC payload is literal and platform-specific.

**Example 1:**
```
BEFORE:
"Run the backup script: /usr/local/bin/backup.sh"

AFTER:
Action:Backup -> EXEC:/usr/local/bin/backup.sh
```

**Example 2:**
```
BEFORE:
"Deploy the Docker image to the registry:
docker push registry.example.com/myapp:latest"

AFTER:
Action:Push_Image -> EXEC:docker push registry.example.com/myapp:latest
```

**Precedence:** 4 (tightest binding; attaches directly to action)

**Composable With:** Action, VERIFY, WARN, IF

**Edge Cases:**

1. **Command with arguments:** `EXEC:kubectl apply -f deploy.yaml` (complex arguments preserved)
2. **Command with environment variables:** `EXEC:DEPLOY_ENV=prod ./deploy.sh` (environment setup)
3. **Multi-line command:** Document as separate EXEC or note in action argument (single-line preferred)

**Notes:**

EXEC contains platform-specific syntax. The decoder is responsible for correct execution environment. No shell escaping is assumed; EXEC payload is literal. Commands should be deterministic and idempotent when possible.

**Composition Example:**
```
Action:Start_Server -> EXEC:systemctl start postgresql; VERIFY:PostgreSQL_Listening_On_5432
```

---

### OP-005: IF / THEN / ELSE

**Name:** Conditional Branching

**Symbol:** `IF:`, `THEN:`, `ELSE:`

**Syntax:**
```
<condition>    ::= 'IF:' <identifier> 'THEN:' <statement> ('ELSE:' <statement>)?
<statement>    ::= <action> | <condition>
```

**Semantics:**

Establishes a test-and-branch structure. IF evaluates a condition (test result, state check, or error code). THEN executes if condition is true. ELSE executes if condition is false. Conditions are typically named (reference to prior state check or action result), not inline boolean expressions.

**Example 1:**
```
BEFORE:
"If deployment succeeds, verify the service is running.
Otherwise, rollback to the previous version."

AFTER:
IF:Deploy_Success THEN:Action:Verify_Service ELSE:Action:Rollback
```

**Example 2:**
```
BEFORE:
"Check if the configuration file exists. If it does, skip initialization.
If not, create it."

AFTER:
IF:Config_Exists THEN:Action:Skip_Init ELSE:Action:Create_Config
```

**Precedence:** 3 (controls statement flow; lower precedence than actions)

**Composable With:** Action, VERIFY, ; (semicolon for sequence), LOOP, REF

**Edge Cases:**

1. **Nested IF:** `IF:A THEN:(IF:B THEN:C ELSE:D) ELSE:E` (conditions can nest)
2. **IF without ELSE:** `IF:Check THEN:Action:Proceed` (ELSE is optional)
3. **Multiple conditions:** Chain as `IF:A THEN:X; IF:B THEN:Y` (sequential conditionals)

**Notes:**

Condition identifiers must be previously defined (from action results, state checks, or error codes). THEN and ELSE are required if IF is present (though ELSE is semantically optional, omitting it means "no action on false"). Conditions are evaluated at runtime by decoder. Condition names should match recognizable states or outcomes (Success, Failure, Exists, etc.).

**Composition Example:**
```
Action:Migrate -> EXEC:migrate.sh; IF:Migration_Success THEN:Action:Verify_Schema ELSE:Action:Restore_Backup
```

---

### OP-006: WARN

**Name:** Warning / Consequence Declaration

**Symbol:** `WARN:` or `⚠`

**Syntax:**
```
<warning>      ::= 'WARN:' <identifier> '->' <consequence>
<consequence>  ::= <identifier>
```

**Semantics:**

Declares that an action (or inaction) carries a risk or consequence. WARN is softer than REQUIRES; it alerts the operator but does not prevent execution. Maps a potential failure mode to its consequence. Essential for capturing procedural hazards and safety-critical information.

**Example 1:**
```
BEFORE:
"WARNING: Skipping the backup will result in data loss if something goes wrong."

AFTER:
WARN:Skip_Backup -> Data_Loss
```

**Example 2:**
```
BEFORE:
"Caution: Restarting the service will cause brief downtime for all users."

AFTER:
WARN:Restart_Service -> Brief_Downtime
```

**Precedence:** 5

**Composable With:** Action, EXEC, IF, THEN

**Edge Cases:**

1. **Multiple warnings:** `WARN:A -> Loss1; WARN:B -> Loss2` (multiple independent risks)
2. **Chained consequences:** `WARN:Skip_Backup -> Data_Loss_Risk -> Team_Notification_Required` (cascading effects)
3. **Negated warning:** `WARN:NOT_Using_TLS -> Security_Risk` (warning about missing safeguard)

**Notes:**

Warnings are advisory but safety-critical. Include in haikus to preserve procedural knowledge about risks. Consequences should be concrete (Data_Loss, Downtime, Security_Breach) not abstract (Bad_Thing). Warnings have 100% primary classification in v0.0.2a, making them the most distinctive and unambiguous pattern in procedural documentation.

**Composition Example:**
```
Action:Upgrade_DB REQUIRES State:Backup_Complete WARN:Skip_Backup -> Data_Loss -> EXEC:upgrade.sh
```

---

### OP-007: VERIFY

**Name:** Verification / Validation

**Symbol:** `VERIFY:` or `✓`

**Syntax:**
```
<verification> ::= 'VERIFY:' <identifier>
<identifier>   ::= [A-Za-z_][A-Za-z0-9_]*
```

**Semantics:**

Declares a post-action check or assertion. VERIFY statements confirm that a preceding action completed successfully. Named verifications are tested by the decoder; failure of a VERIFY should trigger error handling (retry, rollback, alert). Verifications represent the highest primary frequency in v0.0.2a (24.8%), indicating procedural documentation emphasizes validation.

**Example 1:**
```
BEFORE:
"Deploy the service, then verify that all pods are running."

AFTER:
Action:Deploy_Service -> EXEC:kubectl apply -f deploy.yaml; VERIFY:All_Pods_Running
```

**Example 2:**
```
BEFORE:
"Create the backup and confirm the file exists on storage."

AFTER:
Action:Backup -> EXEC:backup.sh; VERIFY:Backup_File_Exists
```

**Precedence:** 5

**Composable With:** Action, EXEC, ; (semicolon), IF, LOOP

**Edge Cases:**

1. **Verification with parameters:** `VERIFY:Response_Code_Is_200` (parameterized verification)
2. **Negative verification:** `VERIFY:NOT_Error_In_Logs` (checking for absence)
3. **Time-bound verification:** `VERIFY:Service_Healthy_For_60_Seconds` (temporal constraint)

**Notes:**

VERIFY names should be descriptive and testable. Each VERIFY should correspond to a specific check in the decoder. If a check cannot be automated, document in a NOTE. VERIFY differs from State because it represents an action (checking) while State represents a condition (being true). Verifications should always follow actions they validate.

**Composition Example:**
```
Action:Start_Server -> EXEC:systemctl start postgresql; VERIFY:PostgreSQL_Listening_On_5432; VERIFY:Data_Directory_Online
```

---

### OP-008: SEQ

**Name:** Sequential Ordering (Explicit)

**Symbol:** `SEQ:` or `;` (implicit)

**Syntax:**
```
<sequence>     ::= <statement> ';' <statement>
<statement>    ::= <action> | <condition>
```

**Semantics:**

Declares strict left-to-right ordering. Semicolon `;` is the default sequence separator; SEQ is explicit when ordering needs to be highlighted for clarity. Statements execute in order, blocking on completion of each statement before proceeding to the next.

**Example 1:**
```
BEFORE:
"First back up the database. Next, stop the service.
Then run the migration. Finally, restart and verify."

AFTER:
Action:Backup_DB; Action:Stop_Service; Action:Migrate; Action:Restart_Service; VERIFY:Service_Online
```

**Example 2:**
```
BEFORE:
"Install dependencies, then build the project, then run tests in sequence."

AFTER:
SEQ:Action:Install, Action:Build, Action:Test
```

**Precedence:** 2 (lowest; acts as statement separator)

**Composable With:** All operators (binds everything together)

**Edge Cases:**

1. **Empty statements:** Avoid `;` with no statement; whitespace-only statements should be ignored
2. **Nested sequences:** Implicit (semicolons nest naturally without explicit nesting operators)
3. **Optional sequences:** Use IF to conditionally order steps; sequence itself is always deterministic

**Notes:**

Semicolon is the standard separator and preferred over explicit SEQ. SEQ is mainly documentary. All haikus are implicitly sequential unless IF/ELSE introduces branching. LOOP may interrupt pure sequencing by repeating blocks.

**Composition Example:**
```
Action:Prepare; Action:Execute; IF:Success THEN:Action:Cleanup ELSE:Action:Alert_Team
```

---

### OP-009: REF

**Name:** Cross-Reference

**Symbol:** `REF:` or `→ref`

**Syntax:**
```
<reference>    ::= 'REF:' <identifier> | '→' <identifier>
<identifier>   ::= [A-Za-z_][A-Za-z0-9_]+ (':' <section>)?
```

**Semantics:**

Points to another document, section, or external procedure. Used to incorporate external knowledge without re-encoding it. REF targets are opaque to the haiku grammar but meaningful to the decoder (resolver). References should be used sparingly for truly external content, not for decomposing large procedures.

**Example 1:**
```
BEFORE:
"If the migration fails, see the Rollback Procedure in Runbook-Migration-v2."

AFTER:
IF:Migration_Failure THEN:REF:Runbook-Migration-v2:Rollback_Procedure
```

**Example 2:**
```
BEFORE:
"For detailed troubleshooting steps, refer to the Troubleshooting Guide."

AFTER:
REF:Troubleshooting_Guide
```

**Precedence:** 8 (high; references are terminal)

**Composable With:** THEN, ELSE, Action (as argument)

**Edge Cases:**

1. **Section references:** `REF:Guide:Section-3-Error-Codes` (specific section pointer)
2. **External URL references:** `REF:https://docs.example.com/api#section` (absolute URL)
3. **Version-specific references:** `REF:Runbook-v2.1:Upgrade_Path` (versioned document reference)

**Notes:**

REF resolver must have access to the referenced document or URL. Document all REF targets in the Deliverable. Broken references should be caught at validation time (v0.0.2d). REF never receives primary classification in v0.0.2a (0.0% primary), indicating references are always subordinate to higher-priority patterns and should be used for truly external procedures.

**Composition Example:**
```
IF:Error_Not_Caught THEN:REF:Troubleshooting_Guide ELSE:Action:Continue
```

---

### OP-010: META

**Name:** Metadata Annotation

**Symbol:** `META:` or `@`

**Syntax:**
```
<metadata>     ::= 'META:' <key> '=' <value>
<key>          ::= [A-Za-z_][A-Za-z0-9_]*
<value>        ::= '[^;]*'  (any string until semicolon)
```

**Semantics:**

Embeds machine-readable metadata about the procedure (version, author, compatibility, dependencies, etc.). Not executable; purely documentary. Metadata is preserved in the haiku but transparent to execution. Used for system-level annotations and configuration information.

**Example 1:**
```
BEFORE:
"This procedure applies to PostgreSQL 12+ and requires version 2.1.0 of the migration tool."

AFTER:
META:compatible_with=PostgreSQL_12+; META:requires=migration_tool_v2.1.0; META:author=DevOps_Team
```

**Example 2:**
```
BEFORE:
"Prerequisites: Python 3.9, pip, and git."

AFTER:
META:prerequisites=Python_3.9,pip,git; META:estimated_duration=30_minutes
```

**Precedence:** 9 (metadata is declarative, not procedural)

**Composable With:** Beginning of haikus (as annotations)

**Edge Cases:**

1. **Complex metadata values:** `META:environments=dev|staging|prod` (pipe-separated alternatives)
2. **Key-value pairs:** `META:version=2.0,status=stable` (comma-separated pairs)
3. **Timestamps:** `META:last_updated=2025-02-05T14:30:00Z` (ISO 8601 format)

**Notes:**

META fields are application-specific. Define a metadata schema in the Style Guide. Do not use META to encode procedural logic; use Actions instead. META is typically placed at the start of a haiku and should not be inline with procedural statements. Metadata appears in only 4.8% of v0.0.2a sentences, confirming its role as document-level annotation rather than inline procedure.

**Composition Example:**
```
META:version=1.0; META:author=SRE_Team; Action:Deploy; VERIFY:Health_Check
```

---

### OP-011: LOOP (Bonus)

**Name:** Repetition / Iteration

**Symbol:** `LOOP:` or `⟳`

**Syntax:**
```
<loop>         ::= 'LOOP:' <count> ':' <statement> | 'LOOP:' 'WHILE:' <condition> ':' <statement>
<count>        ::= <integer> | '*' (infinite)
<condition>    ::= <identifier>
```

**Semantics:**

Declares that an action or block should repeat. COUNT variant repeats N times. WHILE variant repeats until condition becomes false. Essential for encoding retry logic and batch operations. LOOP is powerful but should include explicit bounds or timeout conditions.

**Example 1:**
```
BEFORE:
"Attempt the deployment 3 times. If it fails, wait 5 seconds and retry."

AFTER:
LOOP:3:Action:Deploy -> EXEC:deploy.sh; IF:Deployment_Failed THEN:Action:Wait_5s
```

**Example 2:**
```
BEFORE:
"Keep checking the service status every 10 seconds until it reports healthy."

AFTER:
LOOP:WHILE:Service_Unhealthy:Action:Check_Status; Action:Wait_10s
```

**Precedence:** 3

**Composable With:** Action, IF, EXEC, VERIFY

**Edge Cases:**

1. **Infinite retry:** `LOOP:*:Action:Attempt_Connection` (unbounded repetition; requires explicit exit condition)
2. **Nested loops:** `LOOP:N:LOOP:M:Action:Nested_Task` (loops can nest; be careful of exponential growth)
3. **LOOP with condition:** `LOOP:WHILE:Retries_Remaining:Action:Retry` (condition-based termination)

**Notes:**

LOOP is powerful but can encode unbounded complexity. Document maximum iterations or timeout for safety. LOOP:* should only be used with explicit exit conditions (IF statements checking success or timeout). Infinite loops without safeguards are dangerous in production; prefer COUNT-based loops with explicit maximum retries.

**Composition Example:**
```
LOOP:3:Action:Deploy -> EXEC:deploy.sh; IF:Deployment_Failed THEN:Action:Rollback_Previous ELSE:VERIFY:Service_Running
```

---

### OP-012: NOTE (Bonus)

**Name:** Non-Critical Information / Documentation

**Symbol:** `NOTE:` or `#`

**Syntax:**
```
<note>         ::= 'NOTE:' <text>
<text>         ::= [^;]*
```

**Semantics:**

Embeds human-readable commentary, clarifications, or optional guidance. NOT executable. Contrasts with WARN (which signals risk). Used for tips, clarifications, and non-binding recommendations. Decoder can safely ignore all NOTEs during execution.

**Example 1:**
```
BEFORE:
"It's usually a good idea to check the service logs after deploying."

AFTER:
Action:Deploy; NOTE:Consider_checking_logs_in_/var/log/service.log
```

**Example 2:**
```
BEFORE:
"For better performance, you might want to enable caching."

AFTER:
Action:Configure REQUIRES State:App_Running; NOTE:Caching_option_available_in_config.yaml
```

**Precedence:** 10 (lowest; purely informational)

**Composable With:** Any (typically at end of haiku)

**Edge Cases:**

1. **Multiline notes:** Use `NOTE:text_with_newlines` (document format supports newlines in note text)
2. **Notes with code:** `NOTE:Example_command:pip_install_package` (code references in notes)
3. **Notes with links:** `NOTE:See_documentation_at_example.com` (documentation pointers)

**Notes:**

NOTE is softer than WARNING. Use for optional steps, tips, or contextual guidance. Decoder can safely ignore all NOTEs during execution without changing procedure semantics. Notes are useful for preserving human knowledge that is not procedure-critical.

**Composition Example:**
```
Action:Deploy; VERIFY:Service_Running; NOTE:Check_logs_if_performance_degrades
```

---

## Naming Conventions

### Identifiers (Actions, States, References)

**Format:** PascalCase_With_Underscores

**Valid Examples:**
- `Action:Backup_Database` — clear, multi-word action name
- `State:Config_Valid` — state with multiple words
- `REF:Troubleshooting_Guide` — reference with spaces converted to underscores
- `Action:Deploy_v2_Production` — version and context in name

**Invalid Examples:**
- `Action:backup_database` — lowercase not allowed (use PascalCase)
- `State:ConfigValid` — missing underscore separators
- `Action:Install-Dependencies` — hyphens not allowed (use underscores)
- `State:db_is_online` — lowercase mixed case

---

### Commands (in EXEC)

**Format:** lowercase_with_hyphens or shell_syntax

**Valid Examples:**
- `EXEC:postgres -D /var/lib/postgresql/data` — shell command with arguments
- `EXEC:docker build -t myapp:latest .` — full docker command
- `EXEC:kubectl apply -f deploy.yaml` — kubernetes command with file
- `EXEC:./deploy.sh --production` — shell script with flags

**Invalid Examples:**
- `EXEC:MYCOMMAND` — uppercase not preferred (commands are lowercase)
- `EXEC:MyCommand` — mixed case (commands are lowercase)

---

### Metadata Keys (in META:)

**Format:** lowercase_with_underscores

**Valid Examples:**
- `META:compatible_with=PostgreSQL_12+` — key lowercase, value can include symbols
- `META:version=1.0` — simple key-value
- `META:prerequisites=Python_3.9,pip,git` — list values use commas or pipes
- `META:last_updated=2025-02-05T14:30:00Z` — ISO 8601 timestamps

**Invalid Examples:**
- `META:CompatibleWith=PostgreSQL_12+` — mixed case key (use lowercase)
- `META:version 1.0` — space instead of equals (use =)
- `META:AuthorName=Jane` — mixed case key (use lowercase with underscores)

---

### Consequences (in WARN:)

**Format:** Concrete_Outcome_Name (PascalCase_With_Underscores)

**Valid Examples:**
- `WARN:Skip_Backup -> Data_Loss`
- `WARN:Restart_Service -> Brief_Downtime`
- `WARN:NOT_Using_TLS -> Security_Risk`
- `WARN:Insufficient_Disk_Space -> Migration_Failure`

**Invalid Examples:**
- `WARN:Skip_Backup -> bad_thing` — abstract, not concrete
- `WARN:restart -> downtime` — lowercase (use PascalCase)
- `WARN:Skip_Backup -> DataLoss` — missing underscores

---

## Composition Rules

Haiku operators compose according to the following rules:

### Rule 1: Sequential Composition

Actions and statements compose left-to-right with implicit sequencing (semicolon).

```
Action:A; Action:B; Action:C
→ Execute A, then B, then C in order
```

**Example:**
```
Action:Backup_DB; Action:Stop_Service; Action:Migrate; Action:Restart_Service
```

---

### Rule 2: Dependency Composition

REQUIRES preconditions must be satisfied before Action executes.

```
Action:X REQUIRES State:A, State:B
→ Before X, ensure A AND B are true; abort if not
```

**Example:**
```
Action:Deploy REQUIRES State:DB_Backed_Up, State:Schema_Valid, State:Service_Offline
```

---

### Rule 3: Conditional Composition

IF/THEN/ELSE branches based on named conditions.

```
IF:Condition_Name THEN:Action:X ELSE:Action:Y
→ If Condition_Name is true, do X; else do Y
```

**Example:**
```
IF:Migration_Success THEN:Action:Verify_Schema ELSE:Action:Restore_Backup
```

---

### Rule 4: Verification Composition

VERIFY follows Action/EXEC and checks success.

```
Action:Deploy -> EXEC:cmd; VERIFY:Result
→ Run cmd, then check Result; fail if check fails
```

**Example:**
```
Action:Deploy_Service -> EXEC:kubectl apply -f deploy.yaml; VERIFY:All_Pods_Running
```

---

### Rule 5: Warning Composition

WARN attaches to Actions and declares consequences.

```
Action:Delete WARN:No_Recovery -> Data_Loss; -> EXEC:rm_cmd
→ Deleting will cause data loss if not backed up; execute anyway but alert operator
```

**Example:**
```
Action:Flush_Cache WARN:No_Persistence -> Data_Loss; -> EXEC:redis-cli FLUSHALL
```

---

### Rule 6: Reference Composition

REF can appear in THEN/ELSE or stand alone.

```
IF:Error THEN:REF:Runbook:Error_Resolution
→ If error occurs, follow external runbook section
```

**Example:**
```
IF:Deployment_Failed THEN:REF:Runbook-Troubleshooting:Deployment_Failures
```

---

### Rule 7: Metadata Composition

META appears at beginning; multiple META: clauses allowed.

```
META:version=1.0; META:author=Team; Action:...
→ Metadata is first, then procedure; metadata is not executable
```

**Example:**
```
META:version=2.0; META:author=SRE_Team; META:compatible_with=PostgreSQL_12+; Action:Deploy; VERIFY:Health_Check
```

---

### Rule 8: Loop Composition

LOOP wraps Actions and conditions; can nest.

```
LOOP:3:Action:Retry -> EXEC:cmd
→ Try 3 times; on failure, proceed to next statement
```

**Example:**
```
LOOP:3:Action:Deploy -> EXEC:deploy.sh; IF:Deployment_Failed THEN:Action:Rollback ELSE:VERIFY:Service_Running
```

---

## Decision Tree: When to Use Which Operator

```
START: I want to encode a procedural element

├─ Is it a concrete executable command?
│  └─ YES → Use Action: + EXEC:
│     Example: Action:Backup -> EXEC:/usr/local/bin/backup.sh
│
├─ Is it a required precondition or state?
│  └─ YES → Use State: inside REQUIRES:
│     Example: Action:Deploy REQUIRES State:DB_Backed_Up
│
├─ Does it need branching logic (if-then-else)?
│  └─ YES → Use IF: THEN: ELSE:
│     Example: IF:Deploy_Success THEN:Action:Verify ELSE:Action:Rollback
│
├─ Is it a verification or check of success?
│  └─ YES → Use VERIFY:
│     Example: VERIFY:All_Pods_Running
│
├─ Does it describe a risk or consequence?
│  └─ YES → Use WARN:
│     Example: WARN:Skip_Backup -> Data_Loss
│
├─ Should I reference another document or procedure?
│  └─ YES → Use REF:
│     Example: IF:Error THEN:REF:Troubleshooting_Guide
│
├─ Is it metadata (version, author, prerequisites)?
│  └─ YES → Use META:
│     Example: META:version=1.0; META:compatible_with=PostgreSQL_12+
│
├─ Is it a tip or optional note?
│  └─ YES → Use NOTE:
│     Example: NOTE:Enable_caching_for_better_performance
│
├─ Does it repeat or retry?
│  └─ YES → Use LOOP:
│     Example: LOOP:3:Action:Deploy
│
└─ Default: Action: (most general procedural step)
```

---

## Composition Examples

### Example 1: Simple Backup Procedure

**Verbose Procedure:**
"To back up the database, first ensure the database is online and storage is available. Then run the backup script located at /usr/local/bin/backup.sh. Finally, verify that the backup file exists on storage."

**Haiku Encoding:**
```
Action:Backup_DB REQUIRES State:DB_Online, State:Storage_Available -> EXEC:/usr/local/bin/backup.sh; VERIFY:Backup_File_Exists
```

**Operators Used:** Action, REQUIRES, State (×2), EXEC, VERIFY

**Composition:** Sequential execution with upfront dependency check and post-action verification.

---

### Example 2: Conditional Rollback

**Verbose Procedure:**
"Deploy the service by running the deployment script. If deployment succeeds, verify that the service is healthy. If deployment fails, alert the team and rollback to the previous version."

**Haiku Encoding:**
```
Action:Deploy -> EXEC:deploy.sh; IF:Deploy_Success THEN:VERIFY:Service_Healthy ELSE:Action:Alert_Team; Action:Rollback
```

**Operators Used:** Action, EXEC, IF, THEN, ELSE, VERIFY

**Composition:** Branching on condition with verification on success path and remedial actions on failure.

---

### Example 3: Full Migration Runbook (Multi-Operator)

**Verbose Procedure:**
"This migration procedure applies to PostgreSQL 12+ and requires version 2.1.0 of the migration tool. Estimated duration is 30 minutes. WARNING: This procedure requires a 15-minute maintenance window.

Step 1: Back up the current database to external storage.
Step 2: Stop the application service.
Step 3: Run the migration script: ./scripts/migrate.sh --version 2.1.0
Step 4: If migration succeeds, verify schema integrity by running ./scripts/validate-schema.sh. If migration fails, restore from the backup created in Step 1 and alert the team.
Step 5: Restart application services in the following order: API > Worker > Cache.
Step 6: Verify all services are healthy for 60 seconds.
Note: Check application logs in /var/log/app/ if performance issues occur."

**Haiku Encoding:**
```
META:version=2.0; META:compatible_with=PostgreSQL_12+; META:requires=migration_tool_v2.1.0; META:estimated_duration=30_minutes; WARN:Maintenance_Window -> Service_Downtime;
Action:Backup_DB -> EXEC:/usr/bin/pg_dump mydb > backup.sql; VERIFY:Backup_File_Exists;
Action:Stop_Service -> EXEC:systemctl stop app;
Action:Migrate -> EXEC:./scripts/migrate.sh --version 2.1.0; IF:Migration_Success THEN:VERIFY:Schema_Valid ELSE:Action:Restore_From_Backup; Action:Alert_Team;
Action:Restart_Services -> EXEC:systemctl start app-api; EXEC:systemctl start app-worker; EXEC:systemctl start app-cache;
VERIFY:Service_Health_60_Seconds;
NOTE:Check_logs_at_/var/log/app_if_performance_degrades
```

**Operators Used:** META, WARN, Action (×5), EXEC (×6), VERIFY (×3), IF, THEN, ELSE, NOTE

**Composition:** Document-level metadata and warnings, followed by sequential deployment steps with conditional error handling, post-action verification, and guidance notes.

---

### Example 4: Certificate Renewal with Warnings

**Verbose Procedure:**
"Before renewing the SSL certificate, ensure that the old certificate has been backed up. Run the renewal tool: certbot renew --force-renewal. Verify that the new certificate has been deployed to all servers. WARNING: Do not delete the old certificate before confirming the new certificate works. If verification fails, restore the old certificate and alert the security team."

**Haiku Encoding:**
```
Action:Renew_Certificate REQUIRES State:Old_Cert_Backed_Up -> EXEC:certbot renew --force-renewal; WARN:Cert_Not_Tested -> Service_Downtime;
VERIFY:New_Cert_Valid; VERIFY:Cert_Deployed_All_Servers;
IF:Verification_Failed THEN:Action:Restore_Old_Cert; Action:Alert_Security_Team ELSE:Action:Delete_Old_Cert
```

**Operators Used:** Action, REQUIRES, State, EXEC, WARN, VERIFY (×2), IF, THEN, ELSE

**Composition:** Dependency check before main action, post-action verifications, warnings about common mistakes, and conditional recovery.

---

### Example 5: Retry Loop with Verification

**Verbose Procedure:**
"Attempt to connect to the database server up to 5 times. After each attempt, wait 10 seconds before retrying. If connection succeeds, verify that the database is responsive by running a simple query. If all retries fail, alert the DBA team and log the error."

**Haiku Encoding:**
```
LOOP:5:Action:Connect_To_DB -> EXEC:psql -h dbhost -U user -d mydb; Action:Wait_10s;
IF:Connection_Success THEN:VERIFY:DB_Responsive -> EXEC:SELECT 1; ELSE:Action:Alert_DBA; Action:Log_Error
```

**Operators Used:** LOOP, Action (×4), EXEC (×3), IF, THEN, ELSE, VERIFY

**Composition:** Bounded retry loop with backoff delay, success verification, and failure notification.

---

## Decision Log

**v0.0.2b-001:** Action/EXEC separated to allow actions without explicit command encoding (implicit actions).

*Rationale:* Some procedures reference named actions whose implementation is defined elsewhere (e.g., "Run the backup procedure"). Separating Action from EXEC allows encoding these without requiring inline command payloads.

*Alternative Considered:* Require all actions to have EXEC payloads. This would be more explicit but would make transcoding more difficult when external procedures are referenced.

---

**v0.0.2b-002:** WARN uses arrow notation (→) to match semantic flow (cause → effect).

*Rationale:* The arrow notation `WARN:Skip_Backup -> Data_Loss` visually represents the causal relationship (if you do X, Y happens). This makes warnings more intuitive to read.

*Alternative Considered:* Use different syntax like `WARN:Skip_Backup|Data_Loss`. The arrow notation was chosen for clarity.

---

**v0.0.2b-003:** LOOP and NOTE added as bonus operators after corpus analysis revealed repetition and documentation needs.

*Rationale:* While LOOP and NOTE were not in the initial 10 required operators, corpus analysis (v0.0.2a) indicated that retry logic and guidance notes are frequent patterns in real procedural documentation. Including them improves coverage to ~98% of observable patterns.

*Alternative Considered:* Encode retry logic as nested IF/THEN conditions. This would be more verbose and less readable.

---

## Operator Precedence Summary

Operators are listed by precedence level (higher number = tighter binding):

| Precedence | Operators | Behavior |
|---|---|---|
| 10 | NOTE | Purely informational; no precedence effect |
| 9 | META | Document-level annotation; not procedural |
| 8 | REF | Terminal references; cannot compose further |
| 7 | REQUIRES | Precondition barrier; tight binding to Action |
| 6 | State | Used within REQUIRES or IF; standalone declarations |
| 5 | Action, VERIFY, WARN | Core procedural operators; equal precedence |
| 4 | EXEC | Tightest execution binding; attaches to Action |
| 3 | IF/THEN/ELSE, LOOP | Control flow; lower precedence than actions |
| 2 | SEQ (semicolon) | Statement separator; lowest procedural precedence |

---

## Edge Cases & Common Pitfalls

### Pitfall 1: Confusing VERIFY with State

**Wrong:**
```
Action:Deploy -> VERIFY:Service_Running
(reads as: "deploy, then verify that service is running" — but Service_Running is a state, not a check)
```

**Correct:**
```
Action:Deploy -> EXEC:deploy.sh; VERIFY:Service_Running
(reads as: "deploy using script, then verify that service is running now")
```

**Guidance:** VERIFY is an action (checking); State is a condition (being true).

---

### Pitfall 2: Hard REQUIRES vs. Soft WARN

**Wrong:**
```
Action:Restart REQUIRES State:Backup_Complete
(if backup not done, action aborts — but maybe we want to warn instead)
```

**Correct (if backup is truly required):**
```
Action:Restart REQUIRES State:Backup_Complete
```

**Correct (if backup is advisory):**
```
Action:Restart WARN:Skip_Backup -> Data_Loss
```

**Guidance:** REQUIRES aborts; WARN alerts. Choose based on whether the condition is hard or soft.

---

### Pitfall 3: Multiple VERIFY statements in sequence

**Wrong:**
```
Action:Deploy -> EXEC:deploy.sh; VERIFY:Health_Check; VERIFY:All_Pods_Running
(unclear if both verifications must pass or if they're alternatives)
```

**Better:**
```
Action:Deploy -> EXEC:deploy.sh; VERIFY:Health_Check; VERIFY:All_Pods_Running
(both VERIFY statements must pass; they compose sequentially)
```

**Guidance:** Multiple VERIFYs are AND-ed together (all must pass).

---

### Pitfall 4: Forgetting ELSE in IF

**Valid:**
```
IF:Check_Passed THEN:Action:Continue
(ELSE is optional; implicitly means "do nothing")
```

**Also Valid:**
```
IF:Check_Passed THEN:Action:Continue ELSE:Action:Recover
(ELSE is explicit)
```

**Guidance:** ELSE is optional but recommended for clarity about failure case.

---

### Pitfall 5: Infinite LOOP without bounds

**Dangerous:**
```
LOOP:*:Action:Connect_To_Service
(will retry forever; needs explicit exit condition)
```

**Better:**
```
LOOP:*:Action:Connect_To_Service; IF:Connected THEN:VERIFY:Service_Responsive ELSE:Action:Alert
(infinite loop but with explicit exit condition)
```

**Guidance:** LOOP:* should only be used with explicit IF conditions to break out.

---

## Composition Compatibility Matrix

| Operator | Can Follow | Can Be Followed By |
|---|---|---|
| Action | SEQ, IF | EXEC, VERIFY, WARN, REQUIRES, SEQ |
| EXEC | Action, VERIFY | VERIFY, WARN, SEQ |
| VERIFY | Action, EXEC, SEQ | VERIFY, WARN, SEQ, IF |
| IF | SEQ, META | THEN (required) |
| THEN | IF (required) | Action, VERIFY, REF, SEQ |
| ELSE | THEN (required) | Action, VERIFY, REF, SEQ |
| REQUIRES | Action (required) | (end of action, not followed) |
| WARN | Action (required), ELSE | EXEC, SEQ |
| REF | IF, THEN, ELSE | SEQ |
| STATE | REQUIRES (required), IF | (end of clause, not followed) |
| META | Start of haiku | Action, SEQ |
| LOOP | SEQ, META | Action, VERIFY, IF, SEQ |
| NOTE | Any (typically end) | (end of haiku) |

---

## Operator Statistics from v0.0.2a Corpus

| Operator | Corpus Frequency | Primary % | Reliability | Use Case |
|---|---|---|---|---|
| Action | 60.0% | 20.0% | High | Core procedural unit |
| VERIFY | 24.8% | 24.8% | Very High | Post-action validation |
| REQUIRES | 14.3% | 6.7% | High | Precondition barriers |
| IF/THEN/ELSE | 13.3% | 11.4% | Very High | Branching logic |
| State | 12.4% | 2.9% | High | Condition description |
| WARN | 6.7% | 6.7% | Excellent (100% primary) | Risk annotation |
| META | 4.8% | 1.9% | High | Document metadata |
| REF | 3.8% | 0.0% | Moderate | External references |
| EXEC | (derived) | (derived) | High | Command attachment |
| SEQ | (implicit) | (implicit) | Excellent | Sequencing |
| LOOP | (inferred) | (inferred) | Medium | Retry patterns |
| NOTE | (inferred) | (inferred) | Low | Optional guidance |

---

## Validation Checklist

When encoding a procedure into Haiku format, verify:

- [ ] Every action has a name in PascalCase_With_Underscores
- [ ] Every EXEC command is provided in platform-specific syntax
- [ ] Every VERIFY statement has a name and corresponds to a testable condition
- [ ] Every REQUIRES clause contains only State: declarations
- [ ] Every WARN statement has both cause and consequence
- [ ] Every IF has a corresponding THEN (ELSE is optional but recommended)
- [ ] No state name exceeds 32 characters
- [ ] All LOOP statements have explicit bounds or exit conditions
- [ ] All REF targets are documented and resolvable
- [ ] All META keys are lowercase_with_underscores
- [ ] No contradictions between REQUIRES and WARN (both shouldn't forbid same action)
- [ ] Procedure is readable by domain experts familiar with the system

---

## References

This operator reference is derived from:
- **v0.0.2a Pattern Taxonomy:** 8 semantic categories identified from corpus analysis of 11 procedural documents (105 sentences)
- **Operator Design Principles:** 5 core principles (minimal ambiguity, maximum expressiveness, consistent syntax, composability, human readability)
- **Corpus Sources:** PostgreSQL startup, Docker build/push, AWS S3 configuration, database migration, Python environment setup, SSH troubleshooting, Kubernetes deployment, Node.js dependency management, SSL certificate renewal, Redis cache operation, Git recovery

---

## Next Steps (v0.0.2c)

The operator specifications in this reference will serve as input to **v0.0.2c — Grammar Formalization**, which will:

1. Convert each operator's BNF syntax rule into formal grammar productions
2. Define composition rules as grammar constraints
3. Generate a complete EBNF grammar for Haiku Protocol v0.0.2b
4. Implement a reference parser and semantic validator

---

**Document Version:** 0.0.2b
**Last Updated:** 2025-02-06
**Status:** Complete
**Acceptance Criteria:** All 12 operators fully specified with syntax, semantics, examples, edge cases, and composition rules
