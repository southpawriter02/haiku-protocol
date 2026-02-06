"""Tests for research/operator_specs.py — Operator Specification Data Model for v0.0.2b."""

import logging
import sys
from pathlib import Path

import pytest

# Ensure research/ is importable
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "research"))

from operator_specs import (
    COMPOSITION_RULES,
    NAMING_CONVENTIONS,
    OPERATORS,
    OperatorSpec,
    check_semantic_overlap,
    get_operator_by_id,
    get_operator_by_name,
    validate_composability,
)


# ── Happy Path Tests ──


class TestOperatorSpecsHappyPath:
    """Happy path tests for operator specifications."""

    # Acceptance Criterion: "10+ operators fully specified with Name, Symbol, Syntax, Semantics"
    def test_minimum_ten_operators_defined(self):
        """At least 10 operators are defined in OPERATORS list."""
        # Arrange & Act & Assert
        assert len(OPERATORS) >= 10, (
            f"Expected 10+ operators, got {len(OPERATORS)}"
        )

    # Acceptance Criterion: "10+ operators fully specified with Name, Symbol, Syntax, Semantics"
    def test_all_operators_have_required_fields(self):
        """Every operator has all required OperatorSpec fields."""
        # Arrange
        required_fields = {
            "id", "name", "symbol", "syntax", "semantics",
            "example_before", "example_after", "precedence",
            "composable_with", "edge_cases", "notes",
        }

        # Act & Assert
        for op in OPERATORS:
            for field in required_fields:
                assert field in op, (
                    f"Operator {op.get('id', '?')} missing field: {field}"
                )
                # Non-empty check for string fields
                if isinstance(op[field], str):
                    assert len(op[field]) > 0, (
                        f"Operator {op['id']} has empty {field}"
                    )

    # Acceptance Criterion: "Each operator includes at least one before/after transformation example"
    def test_all_operators_have_examples(self):
        """Every operator has non-empty before/after examples."""
        for op in OPERATORS:
            assert len(op["example_before"]) > 0, (
                f"Operator {op['id']} has empty example_before"
            )
            assert len(op["example_after"]) > 0, (
                f"Operator {op['id']} has empty example_after"
            )

    # Acceptance Criterion: "Edge cases documented for all operators (minimum 2 per operator)"
    def test_all_operators_have_minimum_edge_cases(self):
        """Every operator has at least 2 documented edge cases."""
        for op in OPERATORS:
            assert len(op["edge_cases"]) >= 2, (
                f"Operator {op['id']} ({op['name']}) has only "
                f"{len(op['edge_cases'])} edge cases, need >= 2"
            )

    # Acceptance Criterion: "Operator precedence levels assigned (0-10)"
    def test_all_precedence_values_in_range(self):
        """All operator precedence values are between 0 and 10 inclusive."""
        for op in OPERATORS:
            assert 0 <= op["precedence"] <= 10, (
                f"Operator {op['id']} has precedence {op['precedence']} "
                f"outside range [0, 10]"
            )

    # Acceptance Criterion: "Composition rules defined (minimum 6-8 rules)"
    def test_minimum_composition_rules(self):
        """At least 6 composition rules are defined."""
        assert len(COMPOSITION_RULES) >= 6, (
            f"Expected 6+ composition rules, got {len(COMPOSITION_RULES)}"
        )

    # Acceptance Criterion: "Naming conventions documented"
    def test_naming_conventions_defined(self):
        """Naming conventions exist for identifiers, commands, and metadata keys."""
        assert "identifiers" in NAMING_CONVENTIONS
        assert "commands" in NAMING_CONVENTIONS
        assert "metadata_keys" in NAMING_CONVENTIONS

        for category, conventions in NAMING_CONVENTIONS.items():
            assert "format" in conventions, (
                f"Naming convention '{category}' missing 'format'"
            )
            assert "valid_examples" in conventions, (
                f"Naming convention '{category}' missing 'valid_examples'"
            )
            assert "invalid_examples" in conventions, (
                f"Naming convention '{category}' missing 'invalid_examples'"
            )

    def test_get_operator_by_id_returns_correct_operator(self):
        """get_operator_by_id returns the correct operator for a valid ID."""
        # Arrange & Act
        result = get_operator_by_id("OP-001")

        # Assert
        assert result is not None
        assert result["name"] == "Action"

    def test_get_operator_by_name_case_insensitive(self):
        """get_operator_by_name works case-insensitively."""
        # Arrange & Act
        result1 = get_operator_by_name("Action")
        result2 = get_operator_by_name("action")
        result3 = get_operator_by_name("ACTION")

        # Assert
        assert result1 is not None
        assert result2 is not None
        assert result3 is not None
        assert result1["id"] == result2["id"] == result3["id"] == "OP-001"


# ── Composability & Overlap Tests ──


class TestComposabilityValidation:
    """Tests for operator composability validation (Acceptance Criterion #9)."""

    # Acceptance Criterion: "All operators are composable (no dead-ends)"
    def test_no_dead_end_operators(self):
        """validate_composability reports no dead-end operators."""
        # Arrange & Act
        result = validate_composability()

        # Assert
        assert result["valid"] is True, (
            f"Composability validation failed — dead-ends: {result['dead_ends']}"
        )
        assert len(result["dead_ends"]) == 0

    def test_every_operator_has_at_least_one_composition_target(self):
        """Every operator can compose with at least one other operator."""
        for op in OPERATORS:
            assert len(op["composable_with"]) >= 1, (
                f"Operator {op['id']} ({op['name']}) has no composition targets"
            )

    def test_composable_with_references_valid_ids(self):
        """All IDs in composable_with actually exist in OPERATORS."""
        # Arrange
        valid_ids = {op["id"] for op in OPERATORS}

        # Act & Assert
        for op in OPERATORS:
            for target_id in op["composable_with"]:
                assert target_id in valid_ids, (
                    f"Operator {op['id']} references non-existent "
                    f"composition target: {target_id}"
                )

    def test_seq_composes_with_most_operators(self):
        """SEQ (;) is the universal glue — composes with most operators."""
        # Arrange
        seq = get_operator_by_name("SEQ")

        # Act & Assert
        assert seq is not None
        # SEQ should compose with the majority of operators
        assert len(seq["composable_with"]) >= 8, (
            f"SEQ only composes with {len(seq['composable_with'])} operators — "
            f"expected 8+ as the universal sequence separator"
        )


class TestSemanticOverlap:
    """Tests for semantic overlap checking (Acceptance Criterion #10)."""

    # Acceptance Criterion: "Operator conflicts resolved (no semantic overlap)"
    def test_no_semantic_overlaps(self):
        """check_semantic_overlap reports no overlaps."""
        # Arrange & Act
        result = check_semantic_overlap()

        # Assert
        assert result["valid"] is True, (
            f"Semantic overlap found — names: {result['duplicate_names']}, "
            f"symbols: {result['duplicate_symbols']}"
        )

    def test_all_operator_ids_unique(self):
        """All operator IDs are unique."""
        # Arrange
        ids = [op["id"] for op in OPERATORS]

        # Act & Assert
        assert len(ids) == len(set(ids)), (
            f"Duplicate operator IDs found: {[x for x in ids if ids.count(x) > 1]}"
        )

    def test_all_operator_names_unique(self):
        """All operator names are unique (case-insensitive)."""
        # Arrange
        names = [op["name"].lower() for op in OPERATORS]

        # Act & Assert
        assert len(names) == len(set(names)), (
            f"Duplicate operator names found: "
            f"{[x for x in names if names.count(x) > 1]}"
        )

    def test_all_operator_symbols_unique(self):
        """All operator symbols are unique."""
        # Arrange
        symbols = [op["symbol"] for op in OPERATORS]

        # Act & Assert
        assert len(symbols) == len(set(symbols)), (
            f"Duplicate operator symbols found: "
            f"{[x for x in symbols if symbols.count(x) > 1]}"
        )


# ── Edge Case Tests ──


class TestOperatorSpecsEdgeCases:
    """Edge case tests for operator data model."""

    def test_get_operator_by_id_nonexistent_returns_none(self):
        """Non-existent operator ID returns None."""
        # Arrange & Act
        result = get_operator_by_id("OP-999")

        # Assert
        assert result is None

    def test_get_operator_by_name_nonexistent_returns_none(self):
        """Non-existent operator name returns None."""
        # Arrange & Act
        result = get_operator_by_name("NONEXISTENT")

        # Assert
        assert result is None

    def test_get_operator_by_id_empty_string_returns_none(self):
        """Empty string ID returns None."""
        assert get_operator_by_id("") is None

    def test_get_operator_by_name_empty_string_returns_none(self):
        """Empty string name returns None."""
        assert get_operator_by_name("") is None

    def test_operators_list_not_empty(self):
        """OPERATORS list is not empty."""
        assert len(OPERATORS) > 0

    def test_composition_rules_have_required_fields(self):
        """Each composition rule has id, name, description, example."""
        for rule in COMPOSITION_RULES:
            assert "id" in rule
            assert "name" in rule
            assert "description" in rule
            assert "example" in rule


# ── Pattern-to-Operator Mapping Tests ──


class TestPatternMapping:
    """Tests verifying operators map to v0.0.2a semantic categories."""

    # Use Case: "As a documentation encoder, I need a complete, unambiguous
    #            operator reference so that I can systematically transform
    #            verbose procedures into haiku format."
    def test_all_v002a_categories_have_operators(self):
        """Every v0.0.2a semantic category maps to at least one operator."""
        # Arrange — the 8 categories from v0.0.2a
        category_to_operator = {
            "Actions": ["OP-001", "OP-004"],       # Action, EXEC
            "States": ["OP-002"],                   # State
            "Dependencies": ["OP-003", "OP-008"],   # REQUIRES, SEQ
            "Conditions": ["OP-005"],               # IF/THEN/ELSE
            "Warnings": ["OP-006"],                 # WARN
            "Verifications": ["OP-007"],            # VERIFY
            "References": ["OP-009"],               # REF
            "Metadata": ["OP-010"],                 # META
        }

        # Act & Assert
        for category, expected_ops in category_to_operator.items():
            for op_id in expected_ops:
                result = get_operator_by_id(op_id)
                assert result is not None, (
                    f"Category '{category}' expects operator {op_id}, "
                    f"but it's not defined"
                )

    def test_bonus_operators_extend_coverage(self):
        """Bonus operators (LOOP, NOTE) provide additional coverage."""
        loop = get_operator_by_id("OP-011")
        note = get_operator_by_id("OP-012")

        assert loop is not None
        assert loop["name"] == "LOOP"
        assert note is not None
        assert note["name"] == "NOTE"


# ── Log Output Tests ──


class TestOperatorSpecsLogging:
    """Tests verifying logging output from operator spec functions."""

    def test_validate_composability_logs_start(self, caplog):
        """validate_composability logs INFO when starting."""
        with caplog.at_level(logging.INFO, logger="operator_specs"):
            validate_composability()
        assert "Composability validation started" in caplog.text

    def test_validate_composability_logs_completion(self, caplog):
        """validate_composability logs INFO when complete."""
        with caplog.at_level(logging.INFO, logger="operator_specs"):
            validate_composability()
        assert "Composability validation complete" in caplog.text

    def test_check_semantic_overlap_logs_start(self, caplog):
        """check_semantic_overlap logs INFO when starting."""
        with caplog.at_level(logging.INFO, logger="operator_specs"):
            check_semantic_overlap()
        assert "Semantic overlap check started" in caplog.text

    def test_get_operator_by_id_logs_not_found(self, caplog):
        """get_operator_by_id logs WARNING for missing operator."""
        with caplog.at_level(logging.WARNING, logger="operator_specs"):
            get_operator_by_id("OP-999")
        assert "Operator not found" in caplog.text


# ── Full Use Case Test ──


class TestFullUseCaseWorkflow:
    """End-to-end test simulating the documentation encoder use case."""

    # Use Case: "As a documentation encoder, I need a complete, unambiguous
    #            operator reference so that I can systematically transform
    #            verbose procedures into haiku format without guessing
    #            about meaning or syntax."
    @pytest.mark.unit
    def test_encode_backup_procedure_uses_multiple_operators(self):
        """
        Simulate encoding a backup procedure that requires multiple operators.

        Verbose input:
            "Ensure the database is online. Back up the database using backup.sh.
             WARNING: Skipping backup may cause data loss. Verify backup file exists."

        Expected operators used: State, Action, EXEC, WARN, VERIFY, SEQ
        """
        # Arrange — look up each needed operator
        state = get_operator_by_name("State")
        action = get_operator_by_name("Action")
        exec_op = get_operator_by_name("EXEC")
        warn = get_operator_by_name("WARN")
        verify = get_operator_by_name("VERIFY")
        requires = get_operator_by_name("REQUIRES")

        # Act & Assert — all operators exist and are non-None
        assert state is not None, "State operator needed for precondition"
        assert action is not None, "Action operator needed for backup step"
        assert exec_op is not None, "EXEC operator needed for command"
        assert warn is not None, "WARN operator needed for risk"
        assert verify is not None, "VERIFY operator needed for check"
        assert requires is not None, "REQUIRES operator needed for dependency"

        # Verify they compose correctly:
        # Action REQUIRES State -> EXEC; WARN; VERIFY
        assert requires["id"] in action["composable_with"], (
            "Action should compose with REQUIRES"
        )
        assert exec_op["id"] in action["composable_with"], (
            "Action should compose with EXEC"
        )
        assert warn["id"] in action["composable_with"], (
            "Action should compose with WARN"
        )
        assert verify["id"] in action["composable_with"], (
            "Action should compose with VERIFY"
        )

        # The encoded haiku would be:
        # Action:Backup_DB REQUIRES State:DB_Online -> EXEC:backup.sh;
        # WARN:Skip_Backup -> Data_Loss; VERIFY:Backup_File_Exists
        # This test validates the operator model supports this encoding.
