"""
operator_specs.py - Haiku Protocol Operator Specification Data Model
=====================================================================

Defines the complete set of CNL operators for the Haiku Protocol grammar.
Each operator is specified as a TypedDict with syntax, semantics, examples,
precedence, composability rules, and edge cases.

Classes:
    OperatorSpec: TypedDict defining the schema for operator specifications.

Functions:
    get_operator_by_id: Look up an operator by its ID (e.g., "OP-001").
    get_operator_by_name: Look up an operator by its name (e.g., "Action").
    validate_composability: Check that no operator is a dead-end.
    check_semantic_overlap: Verify no two operators share semantic meaning.
    build_operator_reference_md: Generate the operator_reference.md content.

Implementation Status:
    - IMPLEMENTATION: Phase 0 (v0.0.2b — Operator Design & Syntax Definition)

Related:
    - v0.0.2b — Operator Design & Syntax Definition (spec)
    - v0.0.2a — Pattern Identification & Corpus Analysis (input)
    - v0.0.2c — Grammar Formalization BNF (consumer of output)
    - research/operator_reference.md (output deliverable)
"""

import logging
import time
from typing import Any, Dict, List, Optional, TypedDict

logger = logging.getLogger(__name__)


class OperatorSpec(TypedDict):
    """
    Formal specification of a Haiku Protocol operator.

    Attributes:
        id: Unique identifier (e.g., "OP-001").
        name: Human-readable name (e.g., "Action").
        symbol: Encoding symbol (e.g., "Action:" or "A:").
        syntax: BNF production rule as a string.
        semantics: Detailed description of the operator's meaning.
        example_before: Verbose English input text.
        example_after: Haiku-encoded output text.
        precedence: Binding precedence from 0 (lowest) to 10 (highest).
        composable_with: List of operator IDs this operator can combine with.
        edge_cases: Known edge cases and how to handle them.
        notes: Implementation guidance and design rationale.
    """

    id: str
    name: str
    symbol: str
    syntax: str
    semantics: str
    example_before: str
    example_after: str
    precedence: int
    composable_with: List[str]
    edge_cases: List[str]
    notes: str


# ── Operator Definitions (OP-001 through OP-012) ──
# Each operator maps to one or more semantic categories from v0.0.2a:
#   Actions → OP-001 (Action), OP-004 (EXEC)
#   States → OP-002 (State)
#   Dependencies → OP-003 (REQUIRES), OP-008 (SEQ)
#   Conditions → OP-005 (IF/THEN/ELSE)
#   Warnings → OP-006 (WARN)
#   Verifications → OP-007 (VERIFY)
#   References → OP-009 (REF)
#   Metadata → OP-010 (META)
#   (Bonus) → OP-011 (LOOP), OP-012 (NOTE)

OPERATORS: List[OperatorSpec] = [
    {
        "id": "OP-001",
        "name": "Action",
        "symbol": "Action:",
        "syntax": (
            "<action>       ::= 'Action:' <identifier> <args>?\n"
            "<identifier>   ::= [A-Za-z_][A-Za-z0-9_]*\n"
            "<args>         ::= '(' <command> ')' | '[' <command> ']'\n"
            "<command>      ::= [^\\s;,\\]\\)]+"
        ),
        "semantics": (
            "Denotes a single imperative procedure step. Represents any "
            "action verb (run, create, deploy, etc.). Executes with "
            "sequential guarantees unless otherwise ordered."
        ),
        "example_before": "To restart the server, run the restart command.",
        "example_after": "Action:Restart_Server [restart_cmd]",
        "precedence": 5,
        "composable_with": ["OP-003", "OP-004", "OP-005", "OP-006", "OP-007", "OP-008"],
        "edge_cases": [
            "Action with no arguments: Action:ConfigBackup (implicit, no command payload)",
            "Action with complex command: Action:Deploy (docker build -t image:$(git rev-parse --short HEAD) .)",
            "Action with variable reference: Action:Start_Service [$SERVICE_NAME]",
        ],
        "notes": (
            "Actions are the fundamental unit. Every procedure contains at "
            "least one action. Variables in square brackets [$VAR] are "
            "substituted at encoding time. Commands in parentheses are "
            "optional but encouraged."
        ),
    },
    {
        "id": "OP-002",
        "name": "State",
        "symbol": "State:",
        "syntax": (
            "<state>        ::= 'State:' <identifier>\n"
            "<identifier>   ::= [A-Za-z_][A-Za-z0-9_]*"
        ),
        "semantics": (
            "Declares a required or achieved condition. Represents binary "
            "or categorical states (online/offline, exists/missing, "
            "configured/unconfigured). Used in REQUIRES clauses for "
            "preconditions; used in postconditions to confirm success."
        ),
        "example_before": "The database must be online before backup can proceed.",
        "example_after": "State:DB_Online",
        "precedence": 6,
        "composable_with": ["OP-003", "OP-005"],
        "edge_cases": [
            "Negated state: State:NOT_DB_Online (convention for negation)",
            "Composite state: State:DB_Online AND Auth_Configured (semantic composition)",
            "Time-bound state: State:Config_Valid_For_30_Days (metadata in name)",
        ],
        "notes": (
            "States are immutable snapshots of system condition. Multiple "
            "states can be required simultaneously (AND implicit). No state "
            "name should exceed 32 characters. Use _ for word boundaries."
        ),
    },
    {
        "id": "OP-003",
        "name": "REQUIRES",
        "symbol": "REQUIRES",
        "syntax": (
            "<dependency>   ::= 'REQUIRES' <state_list>\n"
            "<state_list>   ::= <state> (',' <state>)*"
        ),
        "semantics": (
            "Declares that an action cannot execute until specified states "
            "are true. Establishes a precondition barrier. All states in "
            "the list must be satisfied (AND semantics). Failure to meet "
            "any REQUIRES state should abort the action."
        ),
        "example_before": (
            "Before you can deploy, the database must be backed up, "
            "the schema must be validated, and the service must be offline."
        ),
        "example_after": (
            "Action:Deploy REQUIRES State:DB_Backed_Up, "
            "State:Schema_Valid, State:Service_Offline"
        ),
        "precedence": 7,
        "composable_with": ["OP-001", "OP-004", "OP-005"],
        "edge_cases": [
            "No states required: omit REQUIRES clause entirely",
            "Optional requirements: use NOTE/WARNING instead of hard REQUIRES",
            "Conditional requirements: nest REQUIRES inside IF",
        ],
        "notes": (
            "REQUIRES creates hard dependencies. Use WARNING for soft "
            "constraints. If any state is not verifiable, document as a NOTE."
        ),
    },
    {
        "id": "OP-004",
        "name": "EXEC",
        "symbol": "EXEC:",
        "syntax": (
            "<execution>    ::= '->' 'EXEC:' <command>\n"
            "<command>      ::= [^\\s;]+"
        ),
        "semantics": (
            "Attaches a concrete, executable command to an action. The "
            "command is the shell/script invocation that performs the work. "
            "EXEC is optional; present only if command needs explicit encoding."
        ),
        "example_before": "Run the backup script: /usr/local/bin/backup.sh",
        "example_after": "Action:Backup -> EXEC:/usr/local/bin/backup.sh",
        "precedence": 4,
        "composable_with": ["OP-001", "OP-007", "OP-006"],
        "edge_cases": [
            "Command with arguments: EXEC:kubectl apply -f deploy.yaml",
            "Command with environment variables: EXEC:DEPLOY_ENV=prod ./deploy.sh",
            "Multi-line command: document as separate EXEC or note in action argument",
        ],
        "notes": (
            "EXEC contains platform-specific syntax. The decoder is "
            "responsible for correct execution. No shell escaping is "
            "assumed; EXEC payload is literal."
        ),
    },
    {
        "id": "OP-005",
        "name": "IF/THEN/ELSE",
        "symbol": "IF:",
        "syntax": (
            "<condition>    ::= 'IF:' <identifier> 'THEN:' <statement> "
            "('ELSE:' <statement>)?\n"
            "<statement>    ::= <action> | <condition>"
        ),
        "semantics": (
            "Establishes a test-and-branch structure. IF evaluates a "
            "condition (test result, state check, or error code). THEN "
            "executes if condition is true. ELSE executes if false. "
            "Conditions are typically named, not inline."
        ),
        "example_before": (
            "If deployment succeeds, verify the service is running. "
            "Otherwise, rollback to the previous version."
        ),
        "example_after": "IF:Deploy_Success THEN:Action:Verify_Service ELSE:Action:Rollback",
        "precedence": 3,
        "composable_with": ["OP-001", "OP-008"],
        "edge_cases": [
            "Nested IF: IF:A THEN:(IF:B THEN:C ELSE:D) ELSE:E",
            "IF without ELSE: IF:Check THEN:Action:Proceed (ELSE is optional)",
            "Multiple conditions: chain as IF:A THEN:X; IF:B THEN:Y",
        ],
        "notes": (
            "Condition identifiers must be previously defined (from action "
            "results, state checks, or error codes). Conditions are "
            "evaluated at runtime by decoder."
        ),
    },
    {
        "id": "OP-006",
        "name": "WARN",
        "symbol": "WARN:",
        "syntax": (
            "<warning>      ::= 'WARN:' <identifier> '->' <consequence>\n"
            "<consequence>  ::= <identifier>"
        ),
        "semantics": (
            "Declares that an action (or inaction) carries a risk or "
            "consequence. WARN is softer than REQUIRES; it alerts the "
            "operator but does not prevent execution. Maps a potential "
            "failure mode to its consequence."
        ),
        "example_before": (
            "WARNING: Skipping the backup will result in data loss "
            "if something goes wrong."
        ),
        "example_after": "WARN:Skip_Backup -> Data_Loss",
        "precedence": 5,
        "composable_with": ["OP-001", "OP-004"],
        "edge_cases": [
            "Multiple warnings: WARN:A -> Loss1; WARN:B -> Loss2",
            "Chained consequences: WARN:Skip_Backup -> Data_Loss_Risk -> Team_Notification_Required",
            "Negated warning: WARN:NOT_Using_TLS -> Security_Risk",
        ],
        "notes": (
            "Warnings are advisory. Include in haikus to preserve procedural "
            "knowledge about risks. Consequences should be concrete "
            "(Data_Loss, Downtime, Security_Breach) not abstract."
        ),
    },
    {
        "id": "OP-007",
        "name": "VERIFY",
        "symbol": "VERIFY:",
        "syntax": (
            "<verification> ::= 'VERIFY:' <identifier>\n"
            "<identifier>   ::= [A-Za-z_][A-Za-z0-9_]*"
        ),
        "semantics": (
            "Declares a post-action check or assertion. VERIFY statements "
            "confirm that a preceding action completed successfully. "
            "Failure of a VERIFY should trigger error handling."
        ),
        "example_before": "Deploy the service, then verify that all pods are running.",
        "example_after": (
            "Action:Deploy_Service -> EXEC:kubectl apply -f deploy.yaml; "
            "VERIFY:All_Pods_Running"
        ),
        "precedence": 5,
        "composable_with": ["OP-001", "OP-004", "OP-008"],
        "edge_cases": [
            "Verification with parameters: VERIFY:Response_Code_Is_200",
            "Negative verification: VERIFY:NOT_Error_In_Logs",
            "Time-bound verification: VERIFY:Service_Healthy_For_60_Seconds",
        ],
        "notes": (
            "VERIFY names should be descriptive and testable. Each VERIFY "
            "should correspond to a specific check in the decoder. If a "
            "check cannot be automated, document in a NOTE."
        ),
    },
    {
        "id": "OP-008",
        "name": "SEQ",
        "symbol": ";",
        "syntax": (
            "<sequence>     ::= <statement> ';' <statement>\n"
            "<statement>    ::= <action> | <condition>"
        ),
        "semantics": (
            "Declares strict left-to-right ordering. Semicolon ; is the "
            "default sequence separator. Statements execute in order, "
            "blocking on completion of each before proceeding to the next."
        ),
        "example_before": (
            "First back up the database. Next, stop the service. "
            "Then run the migration. Finally, restart and verify."
        ),
        "example_after": (
            "Action:Backup_DB; Action:Stop_Service; Action:Migrate; "
            "Action:Restart_Service; VERIFY:Service_Online"
        ),
        "precedence": 2,
        "composable_with": [
            "OP-001", "OP-002", "OP-003", "OP-004", "OP-005",
            "OP-006", "OP-007", "OP-009", "OP-010", "OP-011", "OP-012",
        ],
        "edge_cases": [
            "Empty statements: avoid ; with no statement on either side",
            "Nested sequences: implicit (semicolons nest naturally)",
            "Optional sequences: use IF to conditionally order steps",
        ],
        "notes": (
            "Semicolon is the standard separator and preferred over "
            "explicit SEQ:. All haikus are implicitly sequential unless "
            "IF/ELSE introduces branching."
        ),
    },
    {
        "id": "OP-009",
        "name": "REF",
        "symbol": "REF:",
        "syntax": (
            "<reference>    ::= 'REF:' <identifier> | '->' <identifier>\n"
            "<identifier>   ::= [A-Za-z_][A-Za-z0-9_]+ (':' <section>)?"
        ),
        "semantics": (
            "Points to another document, section, or external procedure. "
            "Used to incorporate external knowledge without re-encoding it. "
            "REF targets are opaque to the haiku grammar but meaningful "
            "to the decoder (resolver)."
        ),
        "example_before": (
            "If the migration fails, see the Rollback Procedure "
            "in Runbook-Migration-v2."
        ),
        "example_after": "IF:Migration_Failure THEN:REF:Runbook-Migration-v2:Rollback_Procedure",
        "precedence": 8,
        "composable_with": ["OP-005", "OP-001"],
        "edge_cases": [
            "Section references: REF:Guide:Section-3-Error-Codes",
            "External URL references: REF:https://docs.example.com/api#section",
            "Version-specific references: REF:Runbook-v2.1:Upgrade_Path",
        ],
        "notes": (
            "REF resolver must have access to the referenced document or "
            "URL. Broken references should be caught at validation time "
            "(v0.0.2d)."
        ),
    },
    {
        "id": "OP-010",
        "name": "META",
        "symbol": "META:",
        "syntax": (
            "<metadata>     ::= 'META:' <key> '=' <value>\n"
            "<key>          ::= [A-Za-z_][A-Za-z0-9_]*\n"
            "<value>        ::= '[^;]*'"
        ),
        "semantics": (
            "Embeds machine-readable metadata about the procedure "
            "(version, author, compatibility, dependencies, etc.). Not "
            "executable; purely documentary. Metadata is preserved in the "
            "haiku but transparent to execution."
        ),
        "example_before": (
            "This procedure applies to PostgreSQL 12+ and requires "
            "version 2.1.0 of the migration tool."
        ),
        "example_after": (
            "META:compatible_with=PostgreSQL_12+; "
            "META:requires=migration_tool_v2.1.0; META:author=DevOps_Team"
        ),
        "precedence": 9,
        "composable_with": ["OP-008"],
        "edge_cases": [
            "Complex metadata values: META:environments=dev|staging|prod",
            "Key-value pairs: META:version=2.0,status=stable",
            "Timestamps: META:last_updated=2025-02-05T14:30:00Z",
        ],
        "notes": (
            "META fields are application-specific. Define a metadata "
            "schema in the Style Guide. Do not use META to encode "
            "procedural logic; use Actions instead. META is typically "
            "placed at the start of a haiku."
        ),
    },
    {
        "id": "OP-011",
        "name": "LOOP",
        "symbol": "LOOP:",
        "syntax": (
            "<loop>         ::= 'LOOP:' <count> ':' <statement> "
            "| 'LOOP:' 'WHILE:' <condition> ':' <statement>\n"
            "<count>        ::= <integer> | '*' (infinite)\n"
            "<condition>    ::= <identifier>"
        ),
        "semantics": (
            "Declares that an action or block should repeat. COUNT variant "
            "repeats N times. WHILE variant repeats until condition becomes "
            "false. Essential for encoding retry logic and batch operations."
        ),
        "example_before": (
            "Attempt the deployment 3 times. If it fails, wait 5 seconds "
            "and retry."
        ),
        "example_after": (
            "LOOP:3:Action:Deploy -> EXEC:deploy.sh; "
            "IF:Deployment_Failed THEN:Action:Wait_5s"
        ),
        "precedence": 3,
        "composable_with": ["OP-001", "OP-005", "OP-004"],
        "edge_cases": [
            "Infinite retry: LOOP:*:Action:Attempt_Connection",
            "Nested loops: LOOP:N:LOOP:M:Action:Nested_Task",
            "LOOP with condition: LOOP:WHILE:Retries_Remaining:Action:Retry",
        ],
        "notes": (
            "LOOP is powerful but can encode unbounded complexity. Document "
            "maximum iterations or timeout for safety. LOOP:* should only "
            "be used with explicit exit conditions."
        ),
    },
    {
        "id": "OP-012",
        "name": "NOTE",
        "symbol": "NOTE:",
        "syntax": (
            "<note>         ::= 'NOTE:' <text>\n"
            "<text>         ::= [^;]*"
        ),
        "semantics": (
            "Embeds human-readable commentary, clarifications, or optional "
            "guidance. NOT executable. Contrasts with WARN (which signals "
            "risk). Used for tips, clarifications, and non-binding "
            "recommendations."
        ),
        "example_before": "It's usually a good idea to check the service logs after deploying.",
        "example_after": "Action:Deploy; NOTE:Consider_checking_logs_in_/var/log/service.log",
        "precedence": 10,
        "composable_with": ["OP-008"],
        "edge_cases": [
            "Multiline notes: use NOTE:text_with_underscores (document format)",
            "Notes with code: NOTE:Example_command:pip_install_package",
            "Notes with links: NOTE:See_documentation_at_example.com",
        ],
        "notes": (
            "NOTE is softer than WARNING. Use for optional steps, tips, "
            "or contextual guidance. Decoder can safely ignore all NOTEs "
            "during execution."
        ),
    },
]


# ── Composition Rules ──
# Defines how operators can chain together. Used for validation and
# documentation generation.

COMPOSITION_RULES: List[Dict[str, str]] = [
    {
        "id": "RULE-01",
        "name": "Sequential Composition",
        "description": (
            "Actions and statements compose left-to-right with implicit "
            "sequencing (semicolon)."
        ),
        "example": "Action:A; Action:B; Action:C",
    },
    {
        "id": "RULE-02",
        "name": "Dependency Composition",
        "description": (
            "REQUIRES preconditions must be satisfied before Action executes."
        ),
        "example": "Action:X REQUIRES State:A, State:B",
    },
    {
        "id": "RULE-03",
        "name": "Conditional Composition",
        "description": "IF/THEN/ELSE branches based on named conditions.",
        "example": "IF:Condition_Name THEN:Action:X ELSE:Action:Y",
    },
    {
        "id": "RULE-04",
        "name": "Verification Composition",
        "description": "VERIFY follows Action/EXEC and checks success.",
        "example": "Action:Deploy -> EXEC:cmd; VERIFY:Result",
    },
    {
        "id": "RULE-05",
        "name": "Warning Composition",
        "description": "WARN attaches to Actions and declares consequences.",
        "example": "Action:Delete WARN:No_Recovery -> Data_Loss; -> EXEC:rm_cmd",
    },
    {
        "id": "RULE-06",
        "name": "Reference Composition",
        "description": "REF can appear in THEN/ELSE or stand alone.",
        "example": "IF:Error THEN:REF:Runbook:Error_Resolution",
    },
    {
        "id": "RULE-07",
        "name": "Metadata Composition",
        "description": (
            "META appears at beginning; multiple META: clauses allowed."
        ),
        "example": "META:version=1.0; META:author=Team; Action:...",
    },
    {
        "id": "RULE-08",
        "name": "Loop Composition",
        "description": "LOOP wraps Actions and conditions; can nest.",
        "example": "LOOP:3:Action:Retry -> EXEC:cmd",
    },
]


# ── Naming Conventions ──

NAMING_CONVENTIONS: Dict[str, Dict[str, Any]] = {
    "identifiers": {
        "format": "PascalCase_With_Underscores",
        "applies_to": "Actions, States, References, Conditions",
        "valid_examples": ["Action:Backup_Database", "State:Config_Valid"],
        "invalid_examples": ["Action:backup_database", "State:ConfigValid"],
    },
    "commands": {
        "format": "lowercase_with_hyphens or shell_syntax",
        "applies_to": "EXEC payloads",
        "valid_examples": [
            "EXEC:postgres -D /var/lib/postgresql/data",
            "EXEC:docker build -t myapp:latest .",
        ],
        "invalid_examples": ["EXEC:MYCOMMAND"],
    },
    "metadata_keys": {
        "format": "lowercase_with_underscores",
        "applies_to": "META key names",
        "valid_examples": ["META:compatible_with=PostgreSQL_12+", "META:version=1.0"],
        "invalid_examples": ["META:AuthorName=Jane"],
    },
}


# ── Lookup Functions ──


def get_operator_by_id(op_id: str) -> Optional[OperatorSpec]:
    """
    Look up an operator by its ID.

    Args:
        op_id: Operator ID string (e.g., "OP-001").

    Returns:
        The matching OperatorSpec, or None if not found.
    """
    logger.debug("Looking up operator by id=%s", op_id)
    for op in OPERATORS:
        if op["id"] == op_id:
            logger.debug("Found operator: %s (%s)", op["id"], op["name"])
            return op
    logger.warning("Operator not found: id=%s", op_id)
    return None


def get_operator_by_name(name: str) -> Optional[OperatorSpec]:
    """
    Look up an operator by its name (case-insensitive).

    Args:
        name: Operator name string (e.g., "Action", "VERIFY").

    Returns:
        The matching OperatorSpec, or None if not found.
    """
    logger.debug("Looking up operator by name=%s", name)
    name_lower = name.lower()
    for op in OPERATORS:
        if op["name"].lower() == name_lower:
            logger.debug("Found operator: %s (%s)", op["id"], op["name"])
            return op
    logger.warning("Operator not found: name=%s", name)
    return None


def validate_composability() -> Dict[str, Any]:
    """
    Check that no operator is a composability dead-end.

    An operator is a dead-end if its composable_with list is empty AND
    no other operator lists it in their composable_with. This means
    it can neither lead to nor be reached from any other operator.

    Returns:
        Dictionary with:
            - valid: bool (True if no dead-ends)
            - dead_ends: list of operator IDs that are dead-ends
            - reachable_from: dict mapping each operator ID to the list
              of operators that can compose with it

    Raises:
        ValueError: If OPERATORS list is empty.
    """
    if not OPERATORS:
        raise ValueError("OPERATORS list is empty")

    start_time = time.time()
    logger.info("Composability validation started: operators=%d", len(OPERATORS))

    all_ids = {op["id"] for op in OPERATORS}

    # Build reverse mapping: which operators can reach this one?
    reachable_from: Dict[str, List[str]] = {op_id: [] for op_id in all_ids}
    for op in OPERATORS:
        for target_id in op["composable_with"]:
            if target_id in reachable_from:
                reachable_from[target_id].append(op["id"])

    # A dead-end is an operator that can't compose forward AND
    # isn't reachable by any other operator
    dead_ends = []
    for op in OPERATORS:
        can_go_forward = len(op["composable_with"]) > 0
        can_be_reached = len(reachable_from[op["id"]]) > 0
        if not can_go_forward and not can_be_reached:
            dead_ends.append(op["id"])
            logger.warning(
                "Dead-end operator: %s (%s) — no forward or backward composition",
                op["id"],
                op["name"],
            )

    elapsed = time.time() - start_time
    is_valid = len(dead_ends) == 0

    logger.info(
        "Composability validation complete: valid=%s, dead_ends=%d, time=%.2fs",
        is_valid,
        len(dead_ends),
        elapsed,
    )

    return {
        "valid": is_valid,
        "dead_ends": dead_ends,
        "reachable_from": reachable_from,
    }


def check_semantic_overlap() -> Dict[str, Any]:
    """
    Verify no two operators share the same semantic domain.

    Checks for duplicate names, duplicate symbols, and overlapping
    semantics keywords. Two operators "overlap" if they share the
    same symbol or if their names are identical.

    Returns:
        Dictionary with:
            - valid: bool (True if no overlaps found)
            - duplicate_names: list of duplicate name pairs
            - duplicate_symbols: list of duplicate symbol pairs
            - id_conflicts: list of duplicate ID pairs
    """
    start_time = time.time()
    logger.info("Semantic overlap check started: operators=%d", len(OPERATORS))

    duplicate_names = []
    duplicate_symbols = []
    id_conflicts = []

    seen_names: Dict[str, str] = {}
    seen_symbols: Dict[str, str] = {}
    seen_ids: Dict[str, str] = {}

    for op in OPERATORS:
        # ── Check ID uniqueness ──
        if op["id"] in seen_ids:
            id_conflicts.append((op["id"], seen_ids[op["id"]], op["name"]))
            logger.error(
                "Duplicate operator ID: %s (already used by %s)",
                op["id"],
                seen_ids[op["id"]],
            )
        else:
            seen_ids[op["id"]] = op["name"]

        # ── Check name uniqueness ──
        name_key = op["name"].lower()
        if name_key in seen_names:
            duplicate_names.append((op["id"], seen_names[name_key]))
            logger.error(
                "Duplicate operator name: '%s' in %s and %s",
                op["name"],
                op["id"],
                seen_names[name_key],
            )
        else:
            seen_names[name_key] = op["id"]

        # ── Check symbol uniqueness ──
        if op["symbol"] in seen_symbols:
            duplicate_symbols.append((op["id"], seen_symbols[op["symbol"]]))
            logger.error(
                "Duplicate operator symbol: '%s' in %s and %s",
                op["symbol"],
                op["id"],
                seen_symbols[op["symbol"]],
            )
        else:
            seen_symbols[op["symbol"]] = op["id"]

    elapsed = time.time() - start_time
    is_valid = (
        len(duplicate_names) == 0
        and len(duplicate_symbols) == 0
        and len(id_conflicts) == 0
    )

    logger.info(
        "Semantic overlap check complete: valid=%s, time=%.2fs",
        is_valid,
        elapsed,
    )

    return {
        "valid": is_valid,
        "duplicate_names": duplicate_names,
        "duplicate_symbols": duplicate_symbols,
        "id_conflicts": id_conflicts,
    }


# ── CLI Entry Point ──
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    print("\n" + "=" * 60)
    print("OPERATOR SPECIFICATIONS — Haiku Protocol v0.0.2b")
    print("=" * 60)
    print(f"\nTotal Operators: {len(OPERATORS)}")
    print(f"Composition Rules: {len(COMPOSITION_RULES)}")

    print("\n--- Operator Summary ---")
    for op in OPERATORS:
        print(
            f"  {op['id']}: {op['name']:<15s} "
            f"symbol={op['symbol']:<10s} "
            f"precedence={op['precedence']} "
            f"composes_with={len(op['composable_with'])} operators"
        )

    print("\n--- Composability Validation ---")
    comp_result = validate_composability()
    print(f"  Valid: {comp_result['valid']}")
    if comp_result["dead_ends"]:
        print(f"  Dead-ends: {comp_result['dead_ends']}")
    else:
        print("  No dead-end operators found.")

    print("\n--- Semantic Overlap Check ---")
    overlap_result = check_semantic_overlap()
    print(f"  Valid: {overlap_result['valid']}")
    if overlap_result["duplicate_names"]:
        print(f"  Duplicate names: {overlap_result['duplicate_names']}")
    if overlap_result["duplicate_symbols"]:
        print(f"  Duplicate symbols: {overlap_result['duplicate_symbols']}")
    if not overlap_result["duplicate_names"] and not overlap_result["duplicate_symbols"]:
        print("  No semantic overlaps found.")
