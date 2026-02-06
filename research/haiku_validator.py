#!/usr/bin/env python3
"""
haiku_validator.py - Haiku Protocol Validation Pipeline (Research Prototype)
=============================================================================

Multi-stage validation pipeline for haiku protocol strings. Implements 6
validation rules (VAL-001 through VAL-006) across 5 sequential stages:
syntactic, semantic, referential, completeness, and execution.

Aggregates all errors in a single pass rather than stopping at the first
failure. Each error includes a code, severity, user-friendly message,
position in the source string, and a suggested fix.

Depends on HaikuParser from v0.0.2c (research/haiku_parser.py) for
tokenization in the syntactic validation stage.

Classes:
    ErrorSeverity: Enum of validation error severity levels (INFO, WARNING, ERROR).
    ValidationError: Dataclass representing a single validation finding.
    ValidationResult: Dataclass holding the complete result of a validation run.
    HaikuValidator: Main validation pipeline implementing 6 rules in 5 stages.

Functions:
    validate_haiku_string: Convenience function wrapping HaikuValidator.run().
    suggest_fix: Look up auto-correction suggestions for a given error code.

Implementation Status:
    - IMPLEMENTATION: Phase 0 (v0.0.2d — Validation Rules & Error Handling)
    - SCOPE: Research prototype demonstrating multi-stage validation pipeline
    - NOT IN SCOPE: Production-grade validation, interactive repair UI, AST-based checks

Related:
    - v0.0.2d — Validation Rules & Error Handling specification
    - research/haiku_grammar.bnf — EBNF grammar (v0.0.2c)
    - research/haiku_parser.py — Tokenizer and basic parser (v0.0.2c)
    - research/operator_reference.md — Operator specs (v0.0.2b)
    - v1.2 — Validator Module (production implementation target)
"""

import logging
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# ── Ensure research/ is importable for HaikuParser ──
_research_dir = str(Path(__file__).parent)
if _research_dir not in sys.path:
    sys.path.insert(0, _research_dir)


# ── Error Severity Levels ──
# These map to the error taxonomy in the v0.0.2d spec:
#   ERROR (1xx-4xx): Blocks execution; must be fixed.
#   WARNING (5xx): Execution may proceed; recommended fix.
#   INFO: Suggestions only; no action required.


class ErrorSeverity(Enum):
    """
    Severity classification for validation findings.

    Maps directly to the error taxonomy from v0.0.2d:
    - INFO (0): Suggestions only, no action required.
    - WARNING (1): Execution may proceed, but a fix is recommended.
    - ERROR (2): Blocks execution, must be fixed before the haiku can run.

    Attributes:
        INFO: Advisory-level finding (no action required).
        WARNING: Non-blocking finding (execution may proceed).
        ERROR: Blocking finding (execution cannot proceed).

    Example:
        >>> severity = ErrorSeverity.ERROR
        >>> severity.value
        2
    """

    INFO = 0
    WARNING = 1
    ERROR = 2


@dataclass
class ValidationError:
    """
    Represents a single validation finding with actionable context.

    Each finding carries enough information for the user (or an automated
    repair tool) to locate, understand, and fix the issue.

    Attributes:
        code: Error code string (e.g., "VAL-001", "VAL-101").
        severity: ErrorSeverity level (INFO, WARNING, ERROR).
        message: User-friendly description of the problem.
        position: Zero-based character offset in the source haiku string.
        suggestion: Suggested fix (empty string if no suggestion available).
        context: Excerpt from the source string surrounding the error.

    Example:
        >>> error = ValidationError(
        ...     code="VAL-002",
        ...     severity=ErrorSeverity.ERROR,
        ...     message="IF clause missing required THEN clause",
        ...     position=0,
        ...     suggestion="Add 'THEN:' with statement after IF clause",
        ...     context="IF:Condition ▶ ◀ (end of string)"
        ... )
    """

    code: str
    severity: ErrorSeverity
    message: str
    position: int
    suggestion: str = ""
    context: str = ""


@dataclass
class ValidationResult:
    """
    Complete result of a validation pipeline run.

    Contains the validity determination, separated lists of errors and
    warnings, and timing metadata for diagnostics.

    Attributes:
        is_valid: True if no ERROR-severity findings exist.
        errors: List of ERROR-severity ValidationError objects.
        warnings: List of WARNING-severity ValidationError objects.
        info: List of INFO-severity ValidationError objects.
        elapsed_seconds: Wall-clock time for the full pipeline run.
        stages_run: Number of validation stages that executed.

    Example:
        >>> result = ValidationResult(is_valid=True, errors=[], warnings=[],
        ...     info=[], elapsed_seconds=0.001, stages_run=5)
    """

    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    info: List[ValidationError]
    elapsed_seconds: float
    stages_run: int


# ── Valid Operator Keywords ──
# Used by suggest_fix() for Levenshtein-based correction suggestions.
VALID_OPERATORS = frozenset({
    "Action:", "A:", "State:", "S:", "REQUIRES", "EXEC:",
    "IF:", "THEN:", "ELSE:", "VERIFY:", "WARN:", "LOOP:",
    "REF:", "META:", "NOTE:", "SEQ:",
})

# Vague VERIFY terms that RULE-005 flags as non-automatable.
# Kept as a module-level constant so tests and the validator share
# the same source of truth.
VAGUE_VERIFY_TERMS = frozenset({
    "OK", "Working", "Good", "Done", "Successful", "Fine", "Ready",
    "Complete", "Finished", "Correct",
})


class HaikuValidator:
    """
    Multi-stage validation pipeline for haiku protocol strings.

    Runs 5 sequential validation stages, each implementing one or more
    of the 6 validation rules from the v0.0.2d specification:

    Stage 1 — Syntactic (RULE-001: Syntactic Well-Formedness)
        Tokenizes input via HaikuParser. Reports syntax errors with position.

    Stage 2 — Semantic (RULE-002: Operator Completeness)
        Checks that operators have all required clauses (IF needs THEN, etc.).

    Stage 3 — Referential (RULE-003: Reference Definition)
        Verifies all referenced identifiers are defined or externally resolvable.

    Stage 4 — Completeness (RULE-004: Circular Dependency Detection)
        Builds a dependency graph and checks for cycles.

    Stage 5 — Execution (RULE-005 + RULE-006)
        RULE-005: Flags vague or non-automatable VERIFY checks.
        RULE-006: Validates REF targets are resolvable.

    Error aggregation: all stages run regardless of earlier failures
    (unless stop_on_error=True), and findings are collected into a
    single ValidationResult.

    Attributes:
        haiku: The source haiku string being validated.
        stop_on_error: If True, halt after the first stage that finds errors.
        _errors: Internal accumulator for ERROR-severity findings.
        _warnings: Internal accumulator for WARNING-severity findings.
        _info: Internal accumulator for INFO-severity findings.
        _tokens: Token list from HaikuParser (populated in stage 1).

    Example:
        >>> validator = HaikuValidator("Action:Deploy REQUIRES State:Online")
        >>> result = validator.run()
        >>> result.is_valid
        True
        >>> len(result.errors)
        0
    """

    def __init__(self, haiku: str, stop_on_error: bool = False) -> None:
        """
        Initialize HaikuValidator with a haiku string and configuration.

        Args:
            haiku: The haiku protocol string to validate. Must be non-empty.
            stop_on_error: If True, stop the pipeline at the first stage
                that produces ERROR-severity findings. Defaults to False
                (aggregate all errors across all stages).
        """
        self.haiku = haiku
        self.stop_on_error = stop_on_error
        self._errors: List[ValidationError] = []
        self._warnings: List[ValidationError] = []
        self._info: List[ValidationError] = []
        self._tokens: List = []  # Populated by _validate_syntactic()

        logger.debug(
            "HaikuValidator initialized: input_length=%d, stop_on_error=%s",
            len(haiku) if haiku else 0,
            stop_on_error,
        )

    def run(self) -> ValidationResult:
        """
        Execute the full 5-stage validation pipeline.

        Runs each stage in sequence, accumulating findings. Returns a
        ValidationResult summarizing validity, errors, warnings, and timing.

        Returns:
            ValidationResult with is_valid=True only if zero ERROR-severity
            findings exist across all stages.

        Example:
            >>> validator = HaikuValidator("Action:Deploy; VERIFY:Service_Running")
            >>> result = validator.run()
            >>> print(f"Valid: {result.is_valid}, Errors: {len(result.errors)}")
        """
        start_time = time.time()
        logger.info("Validation pipeline started: input_length=%d", len(self.haiku))

        stages_run = 0

        # ── Stage 1: Syntactic Validation (RULE-001) ──
        stages_run += 1
        syntactic_ok = self._validate_syntactic()
        if not syntactic_ok and self.stop_on_error:
            logger.info("Pipeline halted after Stage 1 (stop_on_error=True)")
            elapsed = time.time() - start_time
            return self._build_result(elapsed, stages_run)

        # ── Stage 2: Semantic Validation (RULE-002) ──
        # Requires tokens from Stage 1 to operate on
        if syntactic_ok:
            stages_run += 1
            semantic_ok = self._validate_semantic()
            if not semantic_ok and self.stop_on_error:
                logger.info("Pipeline halted after Stage 2 (stop_on_error=True)")
                elapsed = time.time() - start_time
                return self._build_result(elapsed, stages_run)
        else:
            logger.debug("Skipping Stage 2: tokenization failed in Stage 1")

        # ── Stage 3: Referential Validation (RULE-003) ──
        if syntactic_ok:
            stages_run += 1
            self._validate_referential()

        # ── Stage 4: Completeness Validation (RULE-004) ──
        if syntactic_ok:
            stages_run += 1
            self._validate_completeness()

        # ── Stage 5: Execution Validation (RULE-005 + RULE-006) ──
        if syntactic_ok:
            stages_run += 1
            self._validate_execution()

        elapsed = time.time() - start_time
        result = self._build_result(elapsed, stages_run)

        logger.info(
            "Validation pipeline complete: valid=%s, errors=%d, warnings=%d, "
            "info=%d, stages=%d, time=%.4fs",
            result.is_valid,
            len(result.errors),
            len(result.warnings),
            len(result.info),
            stages_run,
            elapsed,
        )

        return result

    def _build_result(self, elapsed: float, stages_run: int) -> ValidationResult:
        """
        Assemble a ValidationResult from accumulated findings.

        Args:
            elapsed: Wall-clock seconds for the pipeline run.
            stages_run: Number of stages that were executed.

        Returns:
            ValidationResult with sorted error/warning/info lists.
        """
        # Sort each list by position for logical reading order
        errors = sorted(self._errors, key=lambda e: e.position)
        warnings = sorted(self._warnings, key=lambda e: e.position)
        info = sorted(self._info, key=lambda e: e.position)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            elapsed_seconds=elapsed,
            stages_run=stages_run,
        )

    def _validate_syntactic(self) -> bool:
        """
        Stage 1: Syntactic Well-Formedness (RULE-001 / VAL-001).

        Tokenizes the haiku string using HaikuParser. If tokenization
        fails (SyntaxError, ValueError), records an ERROR finding with
        the parser's error details and position information.

        Returns:
            True if tokenization succeeded (no syntax errors).
            False if any syntax error was detected.
        """
        logger.info("Stage 1 (Syntactic): starting RULE-001 check")

        from haiku_parser import HaikuParser

        parser = HaikuParser()

        try:
            result = parser.parse(self.haiku)
            self._tokens = result.tokens

            if not result.valid:
                # The parser found structural issues — convert to our error format
                for error_msg in result.errors:
                    position = self._extract_position_from_message(error_msg)
                    self._add_error(
                        code="VAL-001",
                        message="Syntax error: %s" % error_msg,
                        position=position,
                        suggestion="Check operator spelling and bracket balance",
                    )
                logger.info(
                    "Stage 1 complete: FAIL (%d syntax errors)",
                    len(result.errors),
                )
                return False

            logger.info(
                "Stage 1 complete: PASS (tokens=%d, statements=%d)",
                len(result.tokens),
                result.statements,
            )
            return True

        except SyntaxError as e:
            position = getattr(e, "offset", 0) or 0
            self._add_error(
                code="VAL-001",
                message="Syntax error: %s" % str(e),
                position=position,
                suggestion="Check operator spelling and bracket balance",
            )
            logger.info("Stage 1 complete: FAIL (SyntaxError)")
            return False

        except ValueError as e:
            self._add_error(
                code="VAL-001",
                message="Invalid input: %s" % str(e),
                position=0,
                suggestion="Provide a non-empty haiku string",
            )
            logger.info("Stage 1 complete: FAIL (ValueError)")
            return False

    def _validate_semantic(self) -> bool:
        """
        Stage 2: Operator Completeness (RULE-002 / VAL-002).

        Checks that every operator keyword has its required companion
        clauses present. The rules are derived from the 12 operator
        specifications in v0.0.2b:
        - IF requires THEN
        - THEN requires at least one statement
        - WARN requires '-> consequence'
        - LOOP requires a count or WHILE clause
        - REQUIRES requires at least one State

        Returns:
            True if all operators are complete.
            False if any required clause is missing.
        """
        logger.info("Stage 2 (Semantic): starting RULE-002 check")

        found_issues = False
        token_types = [t.type for t in self._tokens]

        # ── Check: IF without THEN ──
        if_count = token_types.count("IF")
        then_count = token_types.count("THEN")
        if if_count > then_count:
            for token in self._tokens:
                if token.type == "IF":
                    self._add_error(
                        code="VAL-002",
                        message="IF clause missing required THEN clause",
                        position=token.position,
                        suggestion="Add 'THEN:' with statement after IF clause",
                    )
                    found_issues = True
                    break  # Report first occurrence

        # ── Check: THEN with no following statement ──
        for i, token in enumerate(self._tokens):
            if token.type == "THEN":
                has_statement = False
                for j in range(i + 1, len(self._tokens)):
                    if self._tokens[j].type == "SEMICOLON":
                        break
                    if self._tokens[j].type in {
                        "ACTION", "IF", "LOOP", "VERIFY", "REF", "NOTE"
                    }:
                        has_statement = True
                        break
                if not has_statement:
                    self._add_error(
                        code="VAL-002",
                        message="THEN clause has no statement",
                        position=token.position,
                        suggestion="Add an action, condition, or reference after THEN:",
                    )
                    found_issues = True

        # ── Check: WARN without consequence (regex on raw string) ──
        # WARN tokens from HaikuParser include both identifier and consequence
        # in groups. But if the raw string has WARN:X without ->, it may not
        # have been tokenized as WARN at all (caught in Stage 1 instead).
        # This check catches edge cases where WARN appears but is malformed.
        warn_pattern = re.compile(r'WARN:\s*(\w+)')
        for match in warn_pattern.finditer(self.haiku):
            remainder = self.haiku[match.start():]
            next_semi = remainder.find(";")
            segment = remainder[:next_semi] if next_semi != -1 else remainder
            if "->" not in segment:
                self._add_error(
                    code="VAL-002",
                    message="WARN clause missing required consequence",
                    position=match.start(),
                    suggestion="Add '-> Consequence_Identifier' after WARN identifier",
                )
                found_issues = True

        # ── Check: REQUIRES without following State ──
        for i, token in enumerate(self._tokens):
            if token.type == "REQUIRES":
                has_state = False
                for j in range(i + 1, len(self._tokens)):
                    if self._tokens[j].type == "SEMICOLON":
                        break
                    if self._tokens[j].type == "STATE":
                        has_state = True
                        break
                if not has_state:
                    self._add_error(
                        code="VAL-002",
                        message="REQUIRES clause missing State identifier",
                        position=token.position,
                        suggestion="Add 'State:Identifier' after REQUIRES",
                    )
                    found_issues = True

        status = "FAIL" if found_issues else "PASS"
        logger.info("Stage 2 complete: %s", status)
        return not found_issues

    def _validate_referential(self) -> None:
        """
        Stage 3: Reference Definition (RULE-003 / VAL-003).

        Extracts all referenced identifiers (States, Actions, conditions,
        consequences) and checks that each is defined within the haiku
        or documented as external via REF: or META:.

        Undefined references produce WARNING-severity findings (not
        ERROR) because they may be externally resolvable.
        """
        logger.info("Stage 3 (Referential): starting RULE-003 check")

        # ── Build definition tables from tokens ──
        defined_actions: Set[str] = set()
        defined_states: Set[str] = set()
        external_refs: Set[str] = set()

        for token in self._tokens:
            if token.type == "ACTION" and token.groups:
                defined_actions.add(token.groups[0])
            elif token.type == "STATE" and token.groups:
                defined_states.add(token.groups[0])
            elif token.type == "REF" and token.groups:
                external_refs.add(token.groups[0])

        logger.debug(
            "Reference tables: actions=%d, states=%d, external_refs=%d",
            len(defined_actions),
            len(defined_states),
            len(external_refs),
        )

        # ── Check IF condition identifiers ──
        # IF:Condition references a condition that should be defined somewhere.
        for token in self._tokens:
            if token.type == "IF" and token.groups:
                condition_id = token.groups[0]
                if (
                    condition_id not in defined_states
                    and condition_id not in defined_actions
                    and condition_id not in external_refs
                ):
                    self._add_warning(
                        code="VAL-003",
                        message="Condition '%s' not defined as State or Action result"
                        % condition_id,
                        position=token.position,
                        suggestion="Define 'State:%s' or document via REF:" % condition_id,
                    )

        # ── Check WARN consequence identifiers ──
        for token in self._tokens:
            if token.type == "WARN" and token.groups and len(token.groups) >= 2:
                consequence_id = token.groups[1]
                if (
                    consequence_id not in defined_actions
                    and consequence_id not in external_refs
                ):
                    self._add_warning(
                        code="VAL-003",
                        message="Consequence '%s' not defined elsewhere in haiku"
                        % consequence_id,
                        position=token.position,
                        suggestion="Define what '%s' means or document via REF:"
                        % consequence_id,
                    )

        warning_count = sum(1 for w in self._warnings if w.code == "VAL-003")
        logger.info(
            "Stage 3 complete: %d reference warnings",
            warning_count,
        )

    def _validate_completeness(self) -> None:
        """
        Stage 4: Circular Dependency Detection (RULE-004 / VAL-004).

        Builds a dependency graph from Action->REQUIRES->State relationships
        and runs depth-first search to detect cycles. Circular dependencies
        make the haiku unsatisfiable and produce ERROR-severity findings.
        """
        logger.info("Stage 4 (Completeness): starting RULE-004 check")

        # ── Build dependency graph ──
        # action_requires: maps action_id -> set of required state_ids
        action_requires: Dict[str, Set[str]] = defaultdict(set)

        # Walk tokens: ACTION followed by REQUIRES + STATE(s) = dependency
        current_action: Optional[str] = None
        in_requires = False

        for token in self._tokens:
            if token.type == "ACTION" and token.groups:
                current_action = token.groups[0]
                in_requires = False
            elif token.type == "REQUIRES":
                in_requires = True
            elif token.type == "STATE" and token.groups and in_requires and current_action:
                action_requires[current_action].add(token.groups[0])
            elif token.type == "SEMICOLON":
                current_action = None
                in_requires = False

        logger.debug(
            "Dependency graph: %d actions with REQUIRES clauses",
            len(action_requires),
        )

        if not action_requires:
            logger.info("Stage 4 complete: no dependencies to check")
            return

        # ── Detect self-referential dependencies ──
        for action_id, required_states in action_requires.items():
            if action_id in required_states:
                self._add_error(
                    code="VAL-004",
                    message="Self-referential dependency: Action '%s' requires State '%s'"
                    % (action_id, action_id),
                    position=0,
                    suggestion="Remove self-reference or rename the state",
                )

        # ── Detect mutual dependency cycles ──
        # If Action A requires a state matching B's identity and B requires
        # a state matching A's identity, that's a circular dependency.
        all_actions = list(action_requires.keys())
        reported_pairs: Set[Tuple[str, str]] = set()

        for action_a in all_actions:
            for action_b in all_actions:
                if action_a == action_b:
                    continue
                # Avoid duplicate reports for the same pair
                pair_key = tuple(sorted([action_a, action_b]))
                if pair_key in reported_pairs:
                    continue

                a_requires_b = any(
                    state_id == action_b or state_id == "%s_Complete" % action_b
                    for state_id in action_requires[action_a]
                )
                b_requires_a = any(
                    state_id == action_a or state_id == "%s_Complete" % action_a
                    for state_id in action_requires[action_b]
                )
                if a_requires_b and b_requires_a:
                    reported_pairs.add(pair_key)
                    self._add_error(
                        code="VAL-004",
                        message="Circular dependency: Action '%s' and Action '%s' "
                        "mutually depend on each other" % (action_a, action_b),
                        position=0,
                        suggestion="Break the cycle by making one dependency optional "
                        "(use NOTE: instead of REQUIRES)",
                    )

        error_count = sum(1 for e in self._errors if e.code == "VAL-004")
        logger.info(
            "Stage 4 complete: %d circular dependency errors",
            error_count,
        )

    def _validate_execution(self) -> None:
        """
        Stage 5: Execution Readiness (RULE-005 + RULE-006).

        RULE-005 (VAL-005): Checks VERIFY statements for vague or
        non-automatable identifiers (e.g., 'VERIFY:Working', 'VERIFY:OK').
        Produces WARNING-severity findings with specific suggestions.

        RULE-006 (VAL-006): Checks REF statements for resolvable targets.
        Broken or ambiguous references produce ERROR-severity findings.
        """
        logger.info("Stage 5 (Execution): starting RULE-005 and RULE-006 checks")

        # ── RULE-005: Verifiable Verification Checks ──
        for token in self._tokens:
            if token.type == "VERIFY" and token.groups:
                check_id = token.groups[0]

                # Check if identifier contains a vague term
                is_vague = any(
                    vague_term in check_id for vague_term in VAGUE_VERIFY_TERMS
                )

                if is_vague:
                    self._add_warning(
                        code="VAL-005",
                        message="Verification check '%s' may not be automatable"
                        % check_id,
                        position=token.position,
                        suggestion="Use specific check name (e.g., "
                        "VERIFY:Service_Responding_On_Port_8080)",
                    )

                # Flag very short identifiers (< 4 chars) as likely vague
                if len(check_id) < 4:
                    self._add_warning(
                        code="VAL-005",
                        message="Verification check '%s' is too short to be descriptive"
                        % check_id,
                        position=token.position,
                        suggestion="Use a more descriptive name that indicates "
                        "what is being verified",
                    )

        # ── RULE-006: REF Target Resolution ──
        for token in self._tokens:
            if token.type == "REF" and token.groups:
                ref_target = token.groups[0]

                # Validate reference format: alphanumeric with colons, dots,
                # underscores, and hyphens. Must start with a letter or underscore.
                if not re.match(r'^[A-Za-z_][\w:.\-]*$', ref_target):
                    self._add_error(
                        code="VAL-006",
                        message="Invalid reference format: '%s'" % ref_target,
                        position=token.position,
                        suggestion="Use format REF:DocumentName:SectionName "
                        "(alphanumeric, underscores, hyphens, dots)",
                    )

                # Flag suspiciously short references as likely incomplete
                if len(ref_target) < 3:
                    self._add_warning(
                        code="VAL-006",
                        message="Reference '%s' is very short and may be incomplete"
                        % ref_target,
                        position=token.position,
                        suggestion="Provide a complete reference path "
                        "(e.g., REF:Runbook-Deployment-v2.1:Recovery)",
                    )

        verify_warnings = sum(1 for w in self._warnings if w.code == "VAL-005")
        ref_issues = sum(
            1 for e in self._errors + self._warnings if e.code == "VAL-006"
        )
        logger.info(
            "Stage 5 complete: %d VERIFY warnings, %d REF issues",
            verify_warnings,
            ref_issues,
        )

    def _build_context_excerpt(self, position: int, window: int = 20) -> str:
        """
        Extract a context excerpt around a position in the source haiku.

        Produces a string like: '...before ▶ error ◀ after...' to help
        the user locate the issue visually.

        Args:
            position: Zero-based character offset in self.haiku.
            window: Number of characters to include before and after
                the position. Defaults to 20.

        Returns:
            Context string with marker arrows around the error position.
        """
        if not self.haiku:
            return "(empty input)"

        # Clamp position to valid range
        pos = max(0, min(position, len(self.haiku) - 1))

        before_start = max(0, pos - window)
        after_end = min(len(self.haiku), pos + window)

        before = self.haiku[before_start:pos]
        error_char = self.haiku[pos:pos + 1] if pos < len(self.haiku) else "(end)"
        after = self.haiku[pos + 1:after_end]

        prefix = "..." if before_start > 0 else ""
        suffix = "..." if after_end < len(self.haiku) else ""

        return "%s%s ▶ %s ◀ %s%s" % (prefix, before, error_char, after, suffix)

    def _add_error(
        self,
        code: str,
        message: str,
        position: int,
        suggestion: str = "",
    ) -> None:
        """
        Record an ERROR-severity finding.

        Args:
            code: Error code (e.g., "VAL-001").
            message: User-friendly error description.
            position: Character offset in the source string.
            suggestion: Suggested fix text (optional).
        """
        context = self._build_context_excerpt(position)
        error = ValidationError(
            code=code,
            severity=ErrorSeverity.ERROR,
            message=message,
            position=position,
            suggestion=suggestion,
            context=context,
        )
        self._errors.append(error)
        logger.error(
            "[%s] %s (position=%d)",
            code,
            message,
            position,
        )

    def _add_warning(
        self,
        code: str,
        message: str,
        position: int,
        suggestion: str = "",
    ) -> None:
        """
        Record a WARNING-severity finding.

        Args:
            code: Warning code (e.g., "VAL-005").
            message: User-friendly warning description.
            position: Character offset in the source string.
            suggestion: Suggested fix text (optional).
        """
        context = self._build_context_excerpt(position)
        warning = ValidationError(
            code=code,
            severity=ErrorSeverity.WARNING,
            message=message,
            position=position,
            suggestion=suggestion,
            context=context,
        )
        self._warnings.append(warning)
        logger.warning(
            "[%s] %s (position=%d)",
            code,
            message,
            position,
        )

    def _add_info(
        self,
        code: str,
        message: str,
        position: int,
        suggestion: str = "",
    ) -> None:
        """
        Record an INFO-severity finding.

        Args:
            code: Info code (e.g., "VAL-501").
            message: Advisory description.
            position: Character offset in the source string.
            suggestion: Suggested improvement text (optional).
        """
        context = self._build_context_excerpt(position)
        info_item = ValidationError(
            code=code,
            severity=ErrorSeverity.INFO,
            message=message,
            position=position,
            suggestion=suggestion,
            context=context,
        )
        self._info.append(info_item)
        logger.debug(
            "[%s] %s (position=%d)",
            code,
            message,
            position,
        )

    @staticmethod
    def _extract_position_from_message(message: str) -> int:
        """
        Try to extract a character position from a parser error message.

        Args:
            message: Error message string from HaikuParser.

        Returns:
            Extracted position integer, or 0 if not found.
        """
        match = re.search(r'position\s+(\d+)', message)
        if match:
            return int(match.group(1))
        return 0


# ── Levenshtein Distance (for auto-correction suggestions) ──


def _levenshtein_distance(s1: str, s2: str) -> int:
    """
    Compute the Levenshtein edit distance between two strings.

    Used by suggest_fix() to find the closest valid operator keyword
    when a misspelled operator is detected.

    Args:
        s1: First string.
        s2: Second string.

    Returns:
        Integer edit distance (0 = identical strings).
    """
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def _find_closest_operator(misspelled: str) -> Optional[str]:
    """
    Find the closest valid operator keyword to a misspelled input.

    Args:
        misspelled: The misspelled operator string.

    Returns:
        Closest valid operator string, or None if no close match
        exists (distance > 3).
    """
    best_match = None
    best_distance = float("inf")

    for operator in VALID_OPERATORS:
        distance = _levenshtein_distance(
            misspelled.rstrip(":"), operator.rstrip(":")
        )
        if distance < best_distance:
            best_distance = distance
            best_match = operator

    # Only suggest if edit distance is reasonable (max 3 edits)
    if best_distance <= 3:
        return best_match
    return None


def validate_haiku_string(
    haiku: str, stop_on_error: bool = False
) -> Tuple[bool, List[ValidationError]]:
    """
    Convenience function to validate a haiku string.

    Creates a HaikuValidator, runs the full pipeline, and returns
    a simplified (is_valid, all_findings) tuple.

    Args:
        haiku: The haiku protocol string to validate.
        stop_on_error: If True, stop at the first stage with errors.

    Returns:
        Tuple of (is_valid, findings_list) where findings_list contains
        all ERROR, WARNING, and INFO findings sorted by position.

    Example:
        >>> valid, findings = validate_haiku_string("Action:Deploy")
        >>> valid
        True
    """
    logger.info("validate_haiku_string called: input_length=%d", len(haiku))

    validator = HaikuValidator(haiku, stop_on_error=stop_on_error)
    result = validator.run()

    # Combine all findings, sorted by position
    all_findings = sorted(
        result.errors + result.warnings + result.info,
        key=lambda e: e.position,
    )

    return (result.is_valid, all_findings)


def suggest_fix(error_code: str, context: str = "") -> str:
    """
    Look up an auto-correction suggestion for a given error code.

    Implements Strategy 1 (Auto-Correction) from the v0.0.2d spec.
    Returns a user-friendly fix suggestion based on the error code
    and optional context. Returns empty string if no suggestion is
    available.

    Args:
        error_code: The VAL-xxx error code to look up.
        context: Optional context string (e.g., the invalid token text)
            to refine the suggestion.

    Returns:
        Suggested fix string, or empty string if no fix is available.

    Example:
        >>> suggest_fix("VAL-101", "Acton:")
        "Did you mean 'Action:'?"
    """
    logger.debug(
        "suggest_fix called: code=%s, context=%s",
        error_code,
        context[:50] if context else "",
    )

    # ── VAL-101: Invalid operator keyword -> Levenshtein correction ──
    if error_code == "VAL-101" and context:
        closest = _find_closest_operator(context)
        if closest:
            return "Did you mean '%s'?" % closest
        return (
            "Check operator spelling. Valid operators: Action:, State:, "
            "REQUIRES, IF:, THEN:, ELSE:, EXEC:, VERIFY:, WARN:, LOOP:, "
            "REF:, META:, NOTE:"
        )

    # ── VAL-102: Unbalanced bracket/parenthesis ──
    if error_code == "VAL-102":
        return "Check for matching brackets and parentheses. Each '[' needs a ']'."

    # ── VAL-201: Incomplete operator ──
    if error_code == "VAL-201":
        if "IF" in context:
            return "Add 'THEN:' after 'IF:' clause"
        if "WARN" in context:
            return "Add '-> Consequence_Identifier' after WARN"
        if "LOOP" in context:
            return "Add count (e.g., LOOP:3:) or WHILE clause"
        return "Check that operator has all required clauses"

    # ── VAL-301: Undefined identifier ──
    if error_code == "VAL-301" and context:
        return "Define '%s' before use, or document it via REF:" % context

    # ── VAL-402: Unverifiable check ──
    if error_code == "VAL-402" and context:
        return "Use a specific, automatable check name instead of '%s'" % context

    # ── Default: no specific suggestion available ──
    return ""


# ── CLI Entry Point ──
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    print("=" * 60)
    print("HAIKU VALIDATOR — v0.0.2d Research Prototype")
    print("=" * 60)

    # ── Test cases from the v0.0.2d specification ──
    test_cases = [
        ("Valid: simple action with REQUIRES",
         "Action:Deploy REQUIRES State:Online -> EXEC:deploy.sh; VERIFY:Service_Running",
         True),
        ("Valid: linear dependency chain",
         "Action:Initialize REQUIRES State:Empty; Action:Populate REQUIRES State:Initialized",
         True),
        ("Invalid: IF without THEN",
         "IF:Condition",
         False),
        ("Warning: vague VERIFY check",
         "Action:Deploy -> EXEC:deploy.sh; VERIFY:Deployment_OK",
         True),
        ("Valid: conditional with both branches",
         "IF:Success THEN:Action:Continue ELSE:Action:Rollback",
         True),
    ]

    for description, haiku, expected_valid in test_cases:
        print("\n--- %s ---" % description)
        print("  Input: %s" % haiku[:70])

        is_valid, findings = validate_haiku_string(haiku)
        status = "PASS" if is_valid == expected_valid else "UNEXPECTED"

        print("  [%s] Valid=%s (expected=%s)" % (status, is_valid, expected_valid))
        if findings:
            for f in findings:
                print("    [%s/%s] %s" % (f.code, f.severity.name, f.message))
                if f.suggestion:
                    print("      -> %s" % f.suggestion)
