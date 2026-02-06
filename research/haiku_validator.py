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
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


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
        raise NotImplementedError(
            "HaikuValidator.__init__() implementation in Step 3.3"
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
        raise NotImplementedError(
            "HaikuValidator.run() implementation in Step 3.3"
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
        raise NotImplementedError(
            "HaikuValidator._validate_syntactic() implementation in Step 3.3"
        )

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
        raise NotImplementedError(
            "HaikuValidator._validate_semantic() implementation in Step 3.3"
        )

    def _validate_referential(self) -> None:
        """
        Stage 3: Reference Definition (RULE-003 / VAL-003).

        Extracts all referenced identifiers (States, Actions, conditions,
        consequences) and checks that each is defined within the haiku
        or documented as external via REF: or META:.

        Undefined references produce WARNING-severity findings (not
        ERROR) because they may be externally resolvable.
        """
        raise NotImplementedError(
            "HaikuValidator._validate_referential() implementation in Step 3.3"
        )

    def _validate_completeness(self) -> None:
        """
        Stage 4: Circular Dependency Detection (RULE-004 / VAL-004).

        Builds a dependency graph from Action→REQUIRES→State relationships
        and runs depth-first search to detect cycles. Circular dependencies
        make the haiku unsatisfiable and produce ERROR-severity findings.
        """
        raise NotImplementedError(
            "HaikuValidator._validate_completeness() implementation in Step 3.3"
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
        raise NotImplementedError(
            "HaikuValidator._validate_execution() implementation in Step 3.3"
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
        raise NotImplementedError(
            "HaikuValidator._build_context_excerpt() implementation in Step 3.3"
        )

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
        raise NotImplementedError(
            "HaikuValidator._add_error() implementation in Step 3.3"
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
        raise NotImplementedError(
            "HaikuValidator._add_warning() implementation in Step 3.3"
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
        raise NotImplementedError(
            "HaikuValidator._add_info() implementation in Step 3.3"
        )


# ── Auto-Correction Suggestion Mapping ──
# Maps error codes to fix-suggestion functions. Used by suggest_fix()
# and the interactive repair flow (v2.1 Streamlit Dashboard).

# Vague VERIFY terms that RULE-005 flags as non-automatable.
# Kept as a module-level constant so tests and the validator share
# the same source of truth.
VAGUE_VERIFY_TERMS = frozenset({
    "OK", "Working", "Good", "Done", "Successful", "Fine", "Ready",
    "Complete", "Finished", "Correct",
})


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
    raise NotImplementedError(
        "validate_haiku_string() implementation in Step 3.3"
    )


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
    raise NotImplementedError(
        "suggest_fix() implementation in Step 3.3"
    )


# ── CLI Entry Point ──
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Usage demonstration deferred until Step 3.3 implementation
    print("HaikuValidator — interface defined, implementation pending.")
