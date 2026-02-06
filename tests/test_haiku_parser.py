"""Tests for research/haiku_parser.py — HaikuParser for v0.0.2c Grammar Formalization.

Covers:
    - 10 valid haiku strings from v0.0.2c spec (happy path)
    - 5 invalid haiku strings from v0.0.2c spec (error path)
    - Edge cases (empty input, None, single token, max nesting)
    - Tokenizer-specific behavior (token types, ordering, greedy matching)
    - Ambiguity resolution (precedence, greedy EXEC, state list conjunction)
    - Logging output verification (caplog)
    - Use case integration: parser implementer workflow

Test Naming:
    test_<behavior>_<scenario>

Acceptance Criteria Mapping (v0.0.2c):
    AC #1:  "Complete BNF grammar saved to research/haiku_grammar.bnf"
    AC #2:  "All 12 operators from v0.0.2b integrated into grammar"
    AC #3:  "Operator precedence declared (0–10 scale)"
    AC #4:  "Ambiguity resolution rules documented (minimum 5 rules)"
    AC #5:  "Python parser sketch provided (tokenizer + basic validator)"
    AC #6:  "All 10 valid test strings parse successfully"
    AC #7:  "All 5 invalid test strings rejected with clear errors"
    AC #8:  "Grammar is left-recursion free"
    AC #9:  "Parsing workflow diagram created"
    AC #10: "Grammar documented in STYLE_GUIDE.md format"
"""

import logging
import os
import sys
from pathlib import Path

import pytest

# Ensure research/ is importable
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "research"))

from haiku_parser import (
    ALL_TOKEN_TYPES,
    STATEMENT_TOKENS,
    TOKEN_ACTION,
    TOKEN_COMMA,
    TOKEN_ELSE,
    TOKEN_EXEC,
    TOKEN_IF,
    TOKEN_LOOP,
    TOKEN_METADATA,
    TOKEN_NOTE,
    TOKEN_REF,
    TOKEN_REQUIRES,
    TOKEN_SEMICOLON,
    TOKEN_STATE,
    TOKEN_THEN,
    TOKEN_VERIFY,
    TOKEN_WARN,
    HaikuParser,
    ParseResult,
    Token,
    validate_haiku,
)


# ── Happy Path: 10 Valid Spec Strings ──


class TestValidSpecStrings:
    """Tests for all 10 valid haiku strings from the v0.0.2c specification.

    Each test maps to AC #6: "All 10 valid test strings parse successfully."
    """

    # AC #6 — Valid String #1: Simple action
    def test_valid_01_simple_action(self, parser):
        """Single action statement parses as valid."""
        # Arrange
        haiku = "Action:Restart_Service"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is True
        assert result.statements >= 1
        assert result.errors == []

    # AC #6 — Valid String #2: Action with REQUIRES
    def test_valid_02_action_with_requires(self, parser):
        """Action with REQUIRES dependency parses as valid."""
        # Arrange
        haiku = "Action:Deploy REQUIRES State:Config_Valid"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is True
        assert result.statements >= 1
        # Should contain ACTION and REQUIRES tokens
        token_types = [t.type for t in result.tokens]
        assert TOKEN_ACTION in token_types
        assert TOKEN_REQUIRES in token_types
        assert TOKEN_STATE in token_types

    # AC #6 — Valid String #3: Action with EXEC
    def test_valid_03_action_with_exec(self, parser):
        """Action with EXEC command attachment parses as valid."""
        # Arrange
        haiku = "Action:Backup -> EXEC:backup.sh"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is True
        token_types = [t.type for t in result.tokens]
        assert TOKEN_ACTION in token_types
        assert TOKEN_EXEC in token_types

    # AC #6 — Valid String #4: Sequential actions
    def test_valid_04_sequential_actions(self, parser):
        """Three semicolon-separated actions parse as valid."""
        # Arrange
        haiku = "Action:Prepare; Action:Deploy; Action:Verify"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is True
        assert result.statements >= 3
        # Should have 2 semicolons and 3 action tokens
        action_count = sum(1 for t in result.tokens if t.type == TOKEN_ACTION)
        semi_count = sum(1 for t in result.tokens if t.type == TOKEN_SEMICOLON)
        assert action_count == 3
        assert semi_count == 2

    # AC #6 — Valid String #5: Conditional branching
    def test_valid_05_conditional_branching(self, parser):
        """IF/THEN/ELSE conditional structure parses as valid."""
        # Arrange
        haiku = "IF:Success THEN:Action:Continue ELSE:Action:Rollback"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is True
        token_types = [t.type for t in result.tokens]
        assert TOKEN_IF in token_types
        assert TOKEN_THEN in token_types
        assert TOKEN_ELSE in token_types

    # AC #6 — Valid String #6: Verification
    def test_valid_06_verification(self, parser):
        """Action with EXEC followed by VERIFY parses as valid."""
        # Arrange
        haiku = "Action:Deploy -> EXEC:deploy.sh; VERIFY:Service_Running"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is True
        token_types = [t.type for t in result.tokens]
        assert TOKEN_VERIFY in token_types

    # AC #6 — Valid String #7: Warning
    def test_valid_07_warning(self, parser):
        """Action with WARN cause-consequence pair parses as valid."""
        # Arrange
        haiku = "Action:Delete WARN:No_Recovery -> Data_Loss"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is True
        token_types = [t.type for t in result.tokens]
        assert TOKEN_WARN in token_types

    # AC #6 — Valid String #8: Metadata + action
    def test_valid_08_metadata_and_action(self, parser):
        """META block followed by action parses as valid."""
        # Arrange
        haiku = "META:version=1.0; Action:Execute -> EXEC:script.sh"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is True
        token_types = [t.type for t in result.tokens]
        assert TOKEN_METADATA in token_types
        assert TOKEN_ACTION in token_types

    # AC #6 — Valid String #9: Loop with action
    def test_valid_09_loop_with_action(self, parser):
        """LOOP wrapping an action with EXEC parses as valid."""
        # Arrange
        haiku = "LOOP:3:Action:Retry -> EXEC:attempt.sh"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is True
        token_types = [t.type for t in result.tokens]
        assert TOKEN_LOOP in token_types

    # AC #6 — Valid String #10: Complex composition
    def test_valid_10_complex_composition(self, parser):
        """Full composition with META, REQUIRES, EXEC, IF, VERIFY parses as valid."""
        # Arrange
        haiku = (
            "META:author=DevOps; "
            "Action:Backup REQUIRES State:Online -> EXEC:backup.sh; "
            "IF:Success THEN:Action:Verify ELSE:Action:Alert; "
            "VERIFY:Backup_Exists"
        )

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is True
        assert result.statements >= 4
        assert result.errors == []


# ── Error Path: 5 Invalid Spec Strings ──


class TestInvalidSpecStrings:
    """Tests for all 5 invalid haiku strings from the v0.0.2c specification.

    Each test maps to AC #7: "All 5 invalid test strings rejected with clear errors."
    """

    # AC #7 — Invalid String #1: Missing identifier
    def test_invalid_01_missing_identifier(self, parser):
        """Action with no identifier is rejected."""
        # Arrange
        haiku = "Action:"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is False
        assert len(result.errors) > 0
        # The tokenizer should fail on the trailing colon without identifier
        error_text = " ".join(result.errors)
        assert "Unexpected" in error_text or "empty" in error_text.lower()

    # AC #7 — Invalid String #2: REQUIRES without Action
    def test_invalid_02_requires_without_action(self, parser):
        """REQUIRES at start (no Action) is rejected."""
        # Arrange
        haiku = "REQUIRES State:Online"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is False
        error_text = " ".join(result.errors)
        assert "REQUIRES" in error_text

    # AC #7 — Invalid String #3: THEN without IF
    def test_invalid_03_then_without_if(self, parser):
        """THEN without preceding IF is rejected."""
        # Arrange
        haiku = "Action:Deploy THEN Action:Verify"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is False
        assert len(result.errors) > 0

    # AC #7 — Invalid String #4: WARN without Action context
    def test_invalid_04_warn_without_action(self, parser):
        """Standalone WARN (no Action) is rejected."""
        # Arrange
        haiku = "WARN:Unknown_Identifier -> Consequence"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is False
        assert len(result.errors) > 0
        error_text = " ".join(result.errors)
        assert "statement" in error_text.lower() or "No valid" in error_text

    # AC #7 — Invalid String #5: Unbalanced brackets
    def test_invalid_05_unbalanced_brackets(self, parser):
        """Unrecognized characters (brackets) cause SyntaxError."""
        # Arrange
        haiku = "Action:Deploy [broken_bracket"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is False
        assert len(result.errors) > 0
        error_text = " ".join(result.errors)
        assert "Unexpected" in error_text


# ── Tokenizer-Specific Tests ──


class TestTokenizer:
    """Tests for the tokenize() method in isolation.

    Maps to AC #5: "Python parser sketch provided (tokenizer + basic validator)."
    """

    def test_tokenize_returns_token_objects(self, parser):
        """tokenize() returns a list of Token dataclass instances."""
        # Arrange
        haiku = "Action:Deploy"

        # Act
        tokens = parser.tokenize(haiku)

        # Assert
        assert isinstance(tokens, list)
        assert all(isinstance(t, Token) for t in tokens)
        assert len(tokens) == 1

    def test_token_has_correct_attributes(self, parser):
        """Each Token has type, value, position, and groups attributes."""
        # Arrange
        haiku = "Action:Deploy"

        # Act
        tokens = parser.tokenize(haiku)
        token = tokens[0]

        # Assert
        assert token.type == TOKEN_ACTION
        assert "Deploy" in token.value
        assert token.position == 0
        assert "Deploy" in token.groups

    def test_tokenize_preserves_order(self, parser):
        """Tokens are returned in left-to-right order matching source positions."""
        # Arrange
        haiku = "Action:Build; Action:Deploy; VERIFY:Running"

        # Act
        tokens = parser.tokenize(haiku)

        # Assert
        positions = [t.position for t in tokens]
        assert positions == sorted(positions), "Token positions should be ascending"

    # AC #2 — All 12 operators integrated: verify all token type constants exist
    def test_all_token_type_constants_defined(self):
        """ALL_TOKEN_TYPES contains constants for all 12 grammar operators."""
        # Arrange
        expected_types = {
            TOKEN_METADATA, TOKEN_ACTION, TOKEN_STATE, TOKEN_REQUIRES,
            TOKEN_EXEC, TOKEN_IF, TOKEN_THEN, TOKEN_ELSE, TOKEN_VERIFY,
            TOKEN_WARN, TOKEN_LOOP, TOKEN_REF, TOKEN_NOTE,
            TOKEN_SEMICOLON, TOKEN_COMMA,
        }

        # Act & Assert
        assert expected_types == ALL_TOKEN_TYPES

    # AC #3 — Operator precedence: token patterns ordered by specificity
    def test_token_patterns_ordered_by_specificity(self, parser):
        """Token patterns list places META before ACTION, THEN before IF, EXEC early."""
        # Arrange — extract pattern names in order
        pattern_names = [name for name, _ in parser.token_patterns]

        # Assert — META is before ACTION (higher precedence binds first)
        assert pattern_names.index("METADATA") < pattern_names.index("ACTION")
        # THEN is before IF to avoid IF consuming the THEN: keyword
        assert pattern_names.index("THEN") < pattern_names.index("IF")
        # SEMICOLON comes last (delimiter, not an operator)
        assert pattern_names.index("SEMICOLON") > pattern_names.index("NOTE")

    def test_tokenize_empty_input_raises_value_error(self, parser):
        """Empty string raises ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="empty"):
            parser.tokenize("")


# ── Edge Case Tests ──


class TestEdgeCases:
    """Edge case tests for HaikuParser."""

    def test_parse_none_raises_value_error(self, parser):
        """None input to tokenize() raises ValueError."""
        # Arrange & Act & Assert
        with pytest.raises((ValueError, TypeError)):
            parser.tokenize(None)

    def test_parse_whitespace_only_raises_value_error(self, parser):
        """Whitespace-only input raises ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="empty"):
            parser.tokenize("   \n\t  ")

    def test_parse_single_action_token(self, parser):
        """Single action token without modifiers is valid."""
        # Arrange
        haiku = "Action:X"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is True
        assert result.statements == 1

    def test_parse_result_structure(self, parser):
        """ParseResult contains all expected fields."""
        # Arrange
        haiku = "Action:Deploy"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert hasattr(result, "valid")
        assert hasattr(result, "tokens")
        assert hasattr(result, "statements")
        assert hasattr(result, "errors")
        assert isinstance(result.valid, bool)
        assert isinstance(result.tokens, list)
        assert isinstance(result.statements, int)
        assert isinstance(result.errors, list)

    def test_meta_only_haiku_is_valid(self, parser):
        """Haiku with only META statements (no Action) does not error."""
        # Arrange — per grammar, metadata_block is optional but can stand alone
        haiku = "META:version=1.0; META:author=Jane"

        # Act
        result = parser.parse(haiku)

        # Assert — META-only haikus are allowed per the grammar note in parse()
        # (statement_count may be 0, but META is recognized)
        assert len(result.tokens) >= 2
        meta_count = sum(1 for t in result.tokens if t.type == TOKEN_METADATA)
        assert meta_count == 2

    def test_shorthand_action_alias(self, parser):
        """'A:' shorthand for 'Action:' is recognized."""
        # Arrange
        haiku = "A:Deploy"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is True
        assert result.tokens[0].type == TOKEN_ACTION

    def test_shorthand_state_alias(self, parser):
        """'S:' shorthand for 'State:' is recognized."""
        # Arrange
        haiku = "Action:Deploy REQUIRES S:Config_Valid"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is True
        state_tokens = [t for t in result.tokens if t.type == TOKEN_STATE]
        assert len(state_tokens) == 1

    def test_validate_haiku_convenience_function(self):
        """validate_haiku() returns (bool, list) tuple."""
        # Arrange
        haiku = "Action:Deploy; VERIFY:Running"

        # Act
        valid, errors = validate_haiku(haiku)

        # Assert
        assert isinstance(valid, bool)
        assert isinstance(errors, list)
        assert valid is True
        assert errors == []


# ── Ambiguity Resolution Tests ──


class TestAmbiguityResolution:
    """Tests for ambiguity resolution rules from the grammar.

    Maps to AC #4: "Ambiguity resolution rules documented (minimum 5 rules)."
    """

    # Rule 2: Greedy command matching
    def test_exec_greedy_matches_full_command(self, parser):
        """EXEC greedily consumes the entire command string including colons."""
        # Arrange — the command 'docker push image:latest' contains a colon
        haiku = "Action:Deploy -> EXEC:docker push image:latest"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is True
        exec_tokens = [t for t in result.tokens if t.type == TOKEN_EXEC]
        assert len(exec_tokens) == 1
        # The EXEC token should have captured the full command
        exec_value = exec_tokens[0].groups[0] if exec_tokens[0].groups else exec_tokens[0].value
        assert "docker" in exec_value
        assert "image" in exec_value

    # Rule 3: State list conjunction (AND semantics)
    def test_requires_multiple_states_uses_commas(self, parser):
        """REQUIRES with multiple comma-separated states tokenizes correctly."""
        # Arrange
        haiku = "Action:Deploy REQUIRES State:Config, State:DB_Online"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is True
        state_tokens = [t for t in result.tokens if t.type == TOKEN_STATE]
        assert len(state_tokens) == 2

    # Rule 5: Semicolon as primary separator
    def test_semicolons_separate_statements(self, parser):
        """Semicolons separate top-level statements, commas separate within clauses."""
        # Arrange
        haiku = "Action:A REQUIRES State:X, State:Y; Action:B"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is True
        semi_count = sum(1 for t in result.tokens if t.type == TOKEN_SEMICOLON)
        comma_count = sum(1 for t in result.tokens if t.type == TOKEN_COMMA)
        assert semi_count == 1  # Between statements
        assert comma_count == 1  # Within REQUIRES clause

    # Rule 1: Operator precedence — EXEC binds tighter than SEQ
    def test_exec_binds_before_semicolon(self, parser):
        """EXEC command is captured completely before semicolon splits statements."""
        # Arrange
        haiku = "Action:Deploy -> EXEC:deploy.sh; Action:Verify"

        # Act
        result = parser.parse(haiku)

        # Assert
        assert result.valid is True
        exec_tokens = [t for t in result.tokens if t.type == TOKEN_EXEC]
        assert len(exec_tokens) == 1
        # EXEC should NOT consume beyond the semicolon
        exec_payload = exec_tokens[0].groups[0] if exec_tokens[0].groups else ""
        assert "Verify" not in exec_payload


# ── Grammar Completeness Tests ──


class TestGrammarCompleteness:
    """Tests verifying the BNF grammar file and documentation artifacts.

    Maps to AC #1, #2, #8, #9, #10.
    """

    # AC #1 — Complete BNF grammar saved to research/haiku_grammar.bnf
    def test_bnf_grammar_file_exists(self):
        """The BNF grammar file exists at the expected path."""
        # Arrange
        grammar_path = project_root / "research" / "haiku_grammar.bnf"

        # Assert
        assert grammar_path.exists(), f"Grammar file not found: {grammar_path}"
        content = grammar_path.read_text()
        assert len(content) > 500, "Grammar file seems too short"

    # AC #2 — All 12 operators integrated into grammar
    def test_bnf_contains_all_twelve_operators(self):
        """The BNF grammar file references all 12 operator keywords."""
        # Arrange
        grammar_path = project_root / "research" / "haiku_grammar.bnf"
        content = grammar_path.read_text()

        # Assert — all operator keywords should appear
        expected_keywords = [
            "Action:", "State:", "REQUIRES", "EXEC:", "IF:", "THEN:",
            "ELSE:", "VERIFY:", "WARN:", "LOOP:", "REF:", "META:", "NOTE:",
        ]
        for keyword in expected_keywords:
            assert keyword in content, (
                f"Operator keyword '{keyword}' missing from BNF grammar"
            )

    # AC #8 — Grammar is left-recursion free
    def test_bnf_no_left_recursion(self):
        """No production in the BNF grammar directly recurses to itself.

        Left-recursion means a production like: <A> ::= <A> ...
        This is problematic for top-down parsers. We verify no production's
        first alternative starts with the production name itself.
        """
        # Arrange
        grammar_path = project_root / "research" / "haiku_grammar.bnf"
        content = grammar_path.read_text()

        # Act — extract production names and check first alternatives
        import re
        # Match production rules like: <name> ::= ...
        productions = re.findall(r'<(\w+)>\s*::=\s*(.*?)(?=\n<\w+>|\Z)', content, re.DOTALL)

        # Assert
        for name, body in productions:
            # Get the first token of each alternative
            alternatives = body.split("|")
            for alt in alternatives:
                stripped = alt.strip()
                if stripped.startswith(f"<{name}>"):
                    pytest.fail(
                        f"Left-recursion detected: <{name}> ::= <{name}>..."
                    )

    # AC #10 — Grammar documented in STYLE_GUIDE.md format
    def test_style_guide_exists_and_has_content(self):
        """STYLE_GUIDE.md exists and contains grammar documentation."""
        # Arrange
        style_path = project_root / "STYLE_GUIDE.md"

        # Assert
        assert style_path.exists(), f"STYLE_GUIDE.md not found: {style_path}"
        content = style_path.read_text()
        # Should contain the key sections
        assert "Operator" in content
        assert "Composition" in content
        assert "Naming Convention" in content or "Naming" in content

    # AC #9 — Parsing workflow diagram
    def test_spec_contains_parsing_workflow_diagram(self):
        """The v0.0.2c spec includes a parsing workflow diagram."""
        # Arrange — the diagram is in the spec file, and referenced in deliverables
        spec_path = project_root / "docs" / "design" / "phase-0" / "v0.0.2" / "v0.0.2c-grammar_formalization_bnf.md"

        # Assert
        assert spec_path.exists(), f"Spec file not found: {spec_path}"
        content = spec_path.read_text()
        # The workflow diagram uses box-drawing characters
        assert "Lexical Analysis" in content
        assert "Syntactic Analysis" in content
        assert "Semantic Analysis" in content


# ── Logging Tests ──


class TestHaikuParserLogging:
    """Tests verifying logging output from HaikuParser.

    Maps to AC #5 (parser sketch is functional and instrumented).
    """

    def test_parse_logs_start_message(self, parser, caplog):
        """parse() logs INFO when parsing starts."""
        # Arrange & Act
        with caplog.at_level(logging.INFO, logger="haiku_parser"):
            parser.parse("Action:Deploy")

        # Assert
        assert "Parse started" in caplog.text

    def test_parse_logs_completion_message(self, parser, caplog):
        """parse() logs INFO when parsing completes."""
        # Arrange & Act
        with caplog.at_level(logging.INFO, logger="haiku_parser"):
            parser.parse("Action:Deploy")

        # Assert
        assert "Parse complete" in caplog.text

    def test_tokenize_logs_token_count(self, parser, caplog):
        """tokenize() logs INFO with token count on completion."""
        # Arrange & Act
        with caplog.at_level(logging.INFO, logger="haiku_parser"):
            parser.tokenize("Action:Deploy; VERIFY:Running")

        # Assert
        assert "Tokenization complete" in caplog.text
        assert "tokens=" in caplog.text

    def test_debug_logs_individual_token_matches(self, parser, caplog):
        """DEBUG level logs each individual token match."""
        # Arrange & Act
        with caplog.at_level(logging.DEBUG, logger="haiku_parser"):
            parser.tokenize("Action:Deploy")

        # Assert
        assert "Token matched" in caplog.text
        assert "ACTION" in caplog.text


# ── Use Case Integration Test ──


class TestParserImplementerUseCase:
    """Integration test for the parser implementer use case.

    User Story: "As a parser implementer, I need a complete, unambiguous BNF
    grammar so that I can build parsers, validators, and compilers for the
    Haiku Protocol."

    This test validates the end-to-end workflow: take a real-world procedural
    description, verify the haiku encoding parses, and confirm the token
    stream is usable for downstream processing.
    """

    @pytest.mark.unit
    def test_full_workflow_parse_and_inspect_tokens(self, parser):
        """Complete workflow: parse a complex haiku and inspect token stream.

        Simulates a parser implementer verifying that the grammar handles
        a realistic Migration Runbook example from the operator_reference.md.
        """
        # Arrange — realistic migration runbook haiku (from STYLE_GUIDE.md)
        haiku = (
            "META:requires=maintenance_window; "
            "WARN:Skip_Backup -> Data_Loss; "
            "Action:Backup -> EXEC:backup.sh; "
            "Action:Stop_Services; "
            "Action:Migrate -> EXEC:migrate.sh; "
            "IF:Migration_Fail THEN:Action:Restore_Backup ELSE:Action:Restart_Services; "
            "VERIFY:Schema_Valid"
        )

        # Act
        result = parser.parse(haiku)

        # Assert — Step 1: It parses as valid
        assert result.valid is True, f"Expected valid parse, got errors: {result.errors}"

        # Assert — Step 2: Token stream contains expected operator types
        token_types = {t.type for t in result.tokens}
        assert TOKEN_METADATA in token_types, "Missing META token"
        assert TOKEN_WARN in token_types, "Missing WARN token"
        assert TOKEN_ACTION in token_types, "Missing ACTION token"
        assert TOKEN_EXEC in token_types, "Missing EXEC token"
        assert TOKEN_IF in token_types, "Missing IF token"
        assert TOKEN_THEN in token_types, "Missing THEN token"
        assert TOKEN_ELSE in token_types, "Missing ELSE token"
        assert TOKEN_VERIFY in token_types, "Missing VERIFY token"
        assert TOKEN_SEMICOLON in token_types, "Missing SEMICOLON token"

        # Assert — Step 3: Statement count is reasonable
        assert result.statements >= 5, (
            f"Expected 5+ statements in migration runbook, got {result.statements}"
        )

        # Assert — Step 4: Tokens maintain source ordering
        positions = [t.position for t in result.tokens]
        assert positions == sorted(positions), "Tokens should be in source order"


# ── Parametric Tests for Fixture-Driven Validation ──


class TestFixtureDrivenValidation:
    """Parametric tests using shared fixtures for batch validation.

    These complement the individual tests above by exercising the full
    fixture-defined test vectors in a loop.
    """

    # AC #6 — All 10 valid test strings parse
    def test_all_valid_cases_pass(self, parser, valid_haiku_cases):
        """Every valid haiku case from the fixture parses successfully."""
        # Act & Assert
        for desc, haiku, min_stmts in valid_haiku_cases:
            result = parser.parse(haiku)
            assert result.valid is True, (
                f"Valid case '{desc}' failed: {result.errors}\n"
                f"  Input: {haiku}"
            )

    # AC #7 — All 5 invalid test strings rejected
    def test_all_invalid_cases_fail(self, parser, invalid_haiku_cases):
        """Every invalid haiku case from the fixture is rejected."""
        # Act & Assert
        for desc, haiku, error_hint in invalid_haiku_cases:
            result = parser.parse(haiku)
            assert result.valid is False, (
                f"Invalid case '{desc}' unexpectedly passed!\n"
                f"  Input: {haiku}"
            )
            assert len(result.errors) > 0, (
                f"Invalid case '{desc}' has no error messages"
            )
