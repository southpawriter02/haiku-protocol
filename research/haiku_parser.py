#!/usr/bin/env python3
"""
haiku_parser.py - Research-Phase Tokenizer and Validator for Haiku Protocol Grammar
====================================================================================

Provides a regex-based tokenizer and basic syntactic validator for haiku strings
as defined by the EBNF grammar in research/haiku_grammar.bnf. This is a Phase 0
research prototype — production parser implementation is planned for v1.2.

The tokenizer breaks haiku strings into typed Token objects. The validator
performs structural checks: statement presence, operator balance, and basic
well-formedness. Full semantic validation (identifier references, circular
dependencies, REF target resolution) is specified in v0.0.2d.

Classes:
    Token: Dataclass representing a single lexical token.
    HaikuParser: Tokenizer and basic validator for haiku protocol strings.

Functions:
    validate_haiku: Convenience function wrapping HaikuParser.parse().

Implementation Status:
    - IMPLEMENTATION: Phase 0 (v0.0.2c — Grammar Formalization)
    - SCOPE: Tokenization + basic statement validation (research sketch)
    - NOT IN SCOPE: Recursive-descent parsing, AST construction, semantic checks

Related:
    - research/haiku_grammar.bnf — Formal EBNF grammar this parser implements
    - research/operator_specs.py — Operator definitions (v0.0.2b)
    - v0.0.2d — Validation Rules & Error Handling (consumer of this tokenizer)
"""

import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Token Type Constants ──
# These correspond to the operator keywords in haiku_grammar.bnf.
TOKEN_METADATA = "METADATA"
TOKEN_ACTION = "ACTION"
TOKEN_STATE = "STATE"
TOKEN_REQUIRES = "REQUIRES"
TOKEN_EXEC = "EXEC"
TOKEN_IF = "IF"
TOKEN_THEN = "THEN"
TOKEN_ELSE = "ELSE"
TOKEN_VERIFY = "VERIFY"
TOKEN_WARN = "WARN"
TOKEN_LOOP = "LOOP"
TOKEN_REF = "REF"
TOKEN_NOTE = "NOTE"
TOKEN_SEMICOLON = "SEMICOLON"
TOKEN_COMMA = "COMMA"

# All recognized statement-starting token types
STATEMENT_TOKENS = {TOKEN_ACTION, TOKEN_IF, TOKEN_LOOP, TOKEN_REF, TOKEN_NOTE, TOKEN_VERIFY}

# All recognized token types (for validation)
ALL_TOKEN_TYPES = {
    TOKEN_METADATA, TOKEN_ACTION, TOKEN_STATE, TOKEN_REQUIRES, TOKEN_EXEC,
    TOKEN_IF, TOKEN_THEN, TOKEN_ELSE, TOKEN_VERIFY, TOKEN_WARN, TOKEN_LOOP,
    TOKEN_REF, TOKEN_NOTE, TOKEN_SEMICOLON, TOKEN_COMMA,
}


@dataclass
class Token:
    """
    Represents a single lexical token in a haiku string.

    Attributes:
        type: Token type string (e.g., "ACTION", "VERIFY", "SEMICOLON").
        value: The raw text matched by the tokenizer.
        position: Zero-based character offset in the source string.
        groups: Captured regex groups (e.g., identifier, command payload).

    Example:
        >>> token = Token(type="ACTION", value="Action:Deploy", position=0, groups=("Deploy",))
        >>> token.type
        'ACTION'
    """

    type: str
    value: str
    position: int
    groups: tuple = field(default_factory=tuple)


@dataclass
class ParseResult:
    """
    Result of parsing a haiku string.

    Attributes:
        valid: True if the haiku is syntactically well-formed.
        tokens: List of Token objects produced by tokenization.
        statements: Count of top-level statements found.
        errors: List of error message strings (empty if valid).

    Example:
        >>> result = ParseResult(valid=True, tokens=[], statements=1, errors=[])
    """

    valid: bool
    tokens: List[Token]
    statements: int
    errors: List[str]


class HaikuParser:
    """
    Tokenizer and basic validator for Haiku Protocol strings.

    Implements regex-based lexical analysis against the EBNF grammar
    defined in research/haiku_grammar.bnf. Produces Token objects and
    performs basic structural validation.

    This is a research-phase prototype. The tokenizer is functional;
    the validator checks structure but does not perform full recursive-
    descent parsing or semantic analysis.

    Attributes:
        token_patterns: Ordered list of (name, regex) tuples for tokenization.
        compiled_patterns: Pre-compiled regex patterns for performance.

    Example:
        >>> parser = HaikuParser()
        >>> result = parser.parse("Action:Deploy; VERIFY:Service_Running")
        >>> result.valid
        True
        >>> result.statements
        2
    """

    def __init__(self) -> None:
        """
        Initialize HaikuParser with compiled token patterns.

        Token patterns are ordered by specificity — longer/more-specific
        patterns are tried first to avoid partial matches. This ordering
        follows the EBNF grammar's operator precedence.
        """
        # ── Token Patterns (order matters: most specific first) ──
        # Each tuple is (token_type, regex_pattern).
        # Patterns use named groups where captures are needed.
        self.token_patterns: List[Tuple[str, str]] = [
            (TOKEN_METADATA, r'META:\s*([A-Za-z_]\w*)\s*=\s*([^;]+)'),
            (TOKEN_ACTION,   r'(?:Action|A):\s*([A-Za-z_]\w*)'),
            (TOKEN_STATE,    r'(?:State|S):\s*([A-Za-z_]\w*)'),
            (TOKEN_REQUIRES, r'REQUIRES'),
            (TOKEN_THEN,     r'THEN:'),
            (TOKEN_ELSE,     r'ELSE:'),
            (TOKEN_IF,       r'IF:\s*([A-Za-z_]\w*)'),
            (TOKEN_EXEC,     r'->\s*(?:EXEC:)?\s*(.+?)(?=\s*;|\s*VERIFY|\s*WARN|\s*REF|\s*IF|\s*LOOP|\s*NOTE|\s*$)'),
            (TOKEN_VERIFY,   r'VERIFY:\s*([A-Za-z_]\w*)'),
            (TOKEN_WARN,     r'WARN:\s*([A-Za-z_]\w*)\s*->\s*([A-Za-z_]\w*)'),
            (TOKEN_LOOP,     r'LOOP:\s*(.+?)\s*:'),
            (TOKEN_REF,      r'REF:\s*([A-Za-z_][\w:.-]*)'),
            (TOKEN_NOTE,     r'NOTE:\s*(.+?)(?=\s*;|\s*$)'),
            (TOKEN_SEMICOLON, r';'),
            (TOKEN_COMMA,    r','),
        ]

        self.compiled_patterns: List[Tuple[str, re.Pattern]] = [
            (name, re.compile(pattern))
            for name, pattern in self.token_patterns
        ]

        logger.debug(
            "HaikuParser initialized: patterns=%d",
            len(self.compiled_patterns),
        )

    def tokenize(self, text: str) -> List[Token]:
        """
        Break a haiku string into a list of typed tokens.

        Scans the input left-to-right, matching each position against
        the ordered token patterns. Whitespace is skipped. Unrecognized
        characters raise SyntaxError with position information.

        Args:
            text: Input haiku string to tokenize.

        Returns:
            Ordered list of Token objects.

        Raises:
            SyntaxError: If an unrecognized character is encountered,
                with message including the character and its position.
            ValueError: If text is empty or None.
        """
        if not text or not text.strip():
            raise ValueError("Input text is empty or whitespace-only")

        start_time = time.time()
        logger.info("Tokenization started: input_length=%d", len(text))

        tokens: List[Token] = []
        pos = 0

        while pos < len(text):
            # ── Skip whitespace ──
            if text[pos].isspace():
                pos += 1
                continue

            # ── Try each pattern in priority order ──
            matched = False
            for token_type, pattern in self.compiled_patterns:
                match = pattern.match(text, pos)
                if match:
                    groups = match.groups() if match.groups() else ()
                    token = Token(
                        type=token_type,
                        value=match.group(0).strip(),
                        position=pos,
                        groups=groups,
                    )
                    tokens.append(token)
                    pos = match.end()
                    matched = True

                    logger.debug(
                        "Token matched: type=%s, value=%s, pos=%d",
                        token_type,
                        match.group(0).strip()[:50],
                        token.position,
                    )
                    break

            if not matched:
                error_msg = (
                    f"Unexpected character at position {pos}: "
                    f"'{text[pos]}'"
                )
                logger.error("Tokenization failed: %s", error_msg)
                raise SyntaxError(error_msg)

        elapsed = time.time() - start_time
        logger.info(
            "Tokenization complete: tokens=%d, time=%.4fs",
            len(tokens),
            elapsed,
        )
        return tokens

    def parse(self, text: str) -> ParseResult:
        """
        Parse a haiku string and return a structured result.

        Tokenizes the input and performs basic structural validation:
        1. At least one statement must exist.
        2. IF must have a matching THEN.
        3. ELSE must be preceded by THEN.
        4. REQUIRES must follow an ACTION.

        This is NOT a full recursive-descent parser — it validates
        structure at the token-sequence level. Full parsing and AST
        construction are planned for v1.2.

        Args:
            text: Input haiku string to parse.

        Returns:
            ParseResult with validity, tokens, statement count, and errors.
        """
        start_time = time.time()
        logger.info("Parse started: input_length=%d", len(text))

        errors: List[str] = []

        # ── Step 1: Tokenize ──
        try:
            tokens = self.tokenize(text)
        except (SyntaxError, ValueError) as e:
            elapsed = time.time() - start_time
            logger.error("Parse failed at tokenization: %s", str(e))
            return ParseResult(
                valid=False,
                tokens=[],
                statements=0,
                errors=[str(e)],
            )

        if not tokens:
            errors.append("No tokens produced from input")
            return ParseResult(valid=False, tokens=tokens, statements=0, errors=errors)

        # ── Step 2: Count statements ──
        statement_count = sum(
            1 for t in tokens if t.type in STATEMENT_TOKENS
        )

        # ── Step 3: Structural validation ──
        # Check: at least one statement
        if statement_count == 0:
            # META-only haikus are allowed per grammar (metadata_block only)
            meta_count = sum(1 for t in tokens if t.type == TOKEN_METADATA)
            if meta_count == 0:
                errors.append("No valid statements found")

        # Check: IF must have THEN
        token_types = [t.type for t in tokens]
        if_count = token_types.count(TOKEN_IF)
        then_count = token_types.count(TOKEN_THEN)
        if if_count > then_count:
            errors.append(
                "IF without matching THEN: found %d IF but %d THEN"
                % (if_count, then_count)
            )

        # Check: ELSE without THEN
        for i, t in enumerate(tokens):
            if t.type == TOKEN_ELSE:
                preceding_types = [tokens[j].type for j in range(i)]
                if TOKEN_THEN not in preceding_types:
                    errors.append(
                        "ELSE without preceding THEN at position %d"
                        % t.position
                    )

        # Check: REQUIRES without preceding ACTION
        for i, t in enumerate(tokens):
            if t.type == TOKEN_REQUIRES:
                preceding_types = [
                    tokens[j].type for j in range(i)
                    if tokens[j].type != TOKEN_SEMICOLON
                ]
                # Walk backward to find the nearest statement token
                found_action = False
                for j in range(i - 1, -1, -1):
                    if tokens[j].type == TOKEN_SEMICOLON:
                        break
                    if tokens[j].type == TOKEN_ACTION:
                        found_action = True
                        break
                if not found_action:
                    errors.append(
                        "REQUIRES without preceding Action at position %d"
                        % t.position
                    )

        elapsed = time.time() - start_time
        valid = len(errors) == 0

        logger.info(
            "Parse complete: valid=%s, statements=%d, errors=%d, time=%.4fs",
            valid,
            statement_count,
            len(errors),
            elapsed,
        )

        return ParseResult(
            valid=valid,
            tokens=tokens,
            statements=statement_count,
            errors=errors,
        )


def validate_haiku(text: str) -> Tuple[bool, List[str]]:
    """
    Convenience function to validate a haiku string.

    Args:
        text: Input haiku string to validate.

    Returns:
        Tuple of (is_valid, error_list).

    Example:
        >>> valid, errors = validate_haiku("Action:Deploy; VERIFY:Running")
        >>> valid
        True
    """
    parser = HaikuParser()
    result = parser.parse(text)
    return (result.valid, result.errors)


# ── CLI Entry Point ──
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    parser = HaikuParser()

    # ── Spec Test Cases: 10 Valid Strings ──
    valid_cases = [
        "Action:Restart_Service",
        "Action:Deploy REQUIRES State:Config_Valid",
        "Action:Backup -> EXEC:backup.sh",
        "Action:Prepare; Action:Deploy; Action:Verify",
        "IF:Success THEN:Action:Continue ELSE:Action:Rollback",
        "Action:Deploy -> EXEC:deploy.sh; VERIFY:Service_Running",
        "Action:Delete WARN:No_Recovery -> Data_Loss",
        "META:version=1.0; Action:Execute -> EXEC:script.sh",
        "LOOP:3:Action:Retry -> EXEC:attempt.sh",
        "META:author=DevOps; Action:Backup REQUIRES State:Online -> EXEC:backup.sh; IF:Success THEN:Action:Verify ELSE:Action:Alert; VERIFY:Backup_Exists",
    ]

    # ── Spec Test Cases: 5 Invalid Strings ──
    invalid_cases = [
        "Action:",                                    # Missing identifier
        "REQUIRES State:Online",                      # REQUIRES without Action
        "Action:Deploy THEN Action:Verify",           # THEN without IF
        "WARN:Unknown_Identifier -> Consequence",     # WARN without Action context
        "Action:Deploy [broken_bracket",              # Unbalanced brackets
    ]

    print("=" * 60)
    print("HAIKU PARSER VALIDATION — v0.0.2c")
    print("=" * 60)

    print("\n--- Valid Test Cases (expect PASS) ---\n")
    for i, case in enumerate(valid_cases, 1):
        result = parser.parse(case)
        status = "PASS" if result.valid else f"FAIL: {result.errors}"
        print(f"  {i:2d}. [{status}] {case[:70]}")

    print("\n--- Invalid Test Cases (expect FAIL) ---\n")
    for i, case in enumerate(invalid_cases, 1):
        result = parser.parse(case)
        status = "FAIL" if not result.valid else "UNEXPECTED PASS"
        errors = ", ".join(result.errors) if result.errors else "none"
        print(f"  {i:2d}. [{status}] {case[:70]}")
        if result.errors:
            print(f"      Errors: {errors}")
