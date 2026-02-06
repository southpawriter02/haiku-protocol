"""
Unit tests for haiku_validator.py — HaikuValidator validation pipeline.

Tests are organized by the 5 categories required by the testing standards:
  5.1 — Happy Path Tests (valid haiku strings pass all 5 stages)
  5.2 — Edge Case Tests (empty input, boundary values, invalid types)
  5.3 — Error Path Tests (each validation rule catches its target errors)
  5.4 — Log Output Tests (verify logging with caplog fixture)
  5.5 — Use Case Tests (end-to-end developer workflow from spec)

Each test maps to either an acceptance criterion from v0.0.2d or an edge
case derived from the spec's use case scenarios.

Test naming convention:
    test_{method}_{scenario}_{expected_result}

Implementation Status:
    - VERSION: v0.0.2d — Validation Rules & Error Handling
    - FRAMEWORK: pytest (AAA pattern)
    - MARKERS: @pytest.mark.unit
"""

import logging
import sys
from pathlib import Path

import pytest

# Ensure research/ is importable
project_root = Path(__file__).parent.parent
research_dir = project_root / "research"
if str(research_dir) not in sys.path:
    sys.path.insert(0, str(research_dir))

from haiku_validator import (
    ErrorSeverity,
    HaikuValidator,
    ValidationError,
    ValidationResult,
    VAGUE_VERIFY_TERMS,
    VALID_OPERATORS,
    _find_closest_operator,
    _levenshtein_distance,
    suggest_fix,
    validate_haiku_string,
)


# ════════════════════════════════════════════════════════════════════
# FIXTURES
# ════════════════════════════════════════════════════════════════════


@pytest.fixture
def validator_simple():
    """HaikuValidator for a simple, fully valid haiku."""
    return HaikuValidator("Action:Deploy REQUIRES State:Online")


@pytest.fixture
def validator_complex():
    """HaikuValidator for a complex, multi-statement haiku."""
    return HaikuValidator(
        "META:version=1.0; "
        "Action:Backup REQUIRES State:Online -> EXEC:backup.sh; "
        "IF:Success THEN:Action:Verify ELSE:Action:Alert; "
        "VERIFY:Backup_Exists"
    )


# ════════════════════════════════════════════════════════════════════
# 5.1 — HAPPY PATH TESTS
# ════════════════════════════════════════════════════════════════════


class TestHappyPath:
    """Tests for valid haiku strings that should pass all validation stages."""

    @pytest.mark.unit
    def test_run_simple_action_returns_valid(self, validator_simple):
        # Acceptance Criterion: "Python validator implementation provided"
        result = validator_simple.run()
        assert result.is_valid is True
        assert len(result.errors) == 0

    @pytest.mark.unit
    def test_run_simple_action_runs_all_five_stages(self, validator_simple):
        # Acceptance Criterion: "Validation pipeline diagram created"
        result = validator_simple.run()
        assert result.stages_run == 5

    @pytest.mark.unit
    def test_run_complex_haiku_returns_valid(self, validator_complex):
        # Acceptance Criterion: "All test cases pass/fail as specified"
        result = validator_complex.run()
        assert result.is_valid is True
        assert result.stages_run == 5

    @pytest.mark.unit
    def test_run_sequential_actions_valid(self):
        # Acceptance Criterion: "All test cases pass/fail as specified"
        validator = HaikuValidator("Action:Prepare; Action:Deploy; Action:Verify")
        result = validator.run()
        assert result.is_valid is True
        assert result.stages_run == 5

    @pytest.mark.unit
    def test_run_action_with_exec_valid(self):
        # Acceptance Criterion: "All test cases pass/fail as specified"
        validator = HaikuValidator("Action:Backup -> EXEC:backup.sh")
        result = validator.run()
        assert result.is_valid is True

    @pytest.mark.unit
    def test_run_conditional_with_both_branches_valid(self):
        # Acceptance Criterion: "All test cases pass/fail as specified"
        validator = HaikuValidator(
            "IF:Success THEN:Action:Continue ELSE:Action:Rollback"
        )
        result = validator.run()
        assert result.is_valid is True

    @pytest.mark.unit
    def test_run_loop_with_action_valid(self):
        # Acceptance Criterion: "All test cases pass/fail as specified"
        validator = HaikuValidator("LOOP:3:Action:Retry -> EXEC:attempt.sh")
        result = validator.run()
        assert result.is_valid is True

    @pytest.mark.unit
    def test_run_metadata_with_action_valid(self):
        # Acceptance Criterion: "All test cases pass/fail as specified"
        validator = HaikuValidator("META:version=1.0; Action:Execute -> EXEC:script.sh")
        result = validator.run()
        assert result.is_valid is True

    @pytest.mark.unit
    def test_run_action_with_verify_valid(self):
        # Acceptance Criterion: "All test cases pass/fail as specified"
        validator = HaikuValidator(
            "Action:Deploy -> EXEC:deploy.sh; VERIFY:Service_Running"
        )
        result = validator.run()
        assert result.is_valid is True

    @pytest.mark.unit
    def test_run_ref_statement_valid(self):
        # Acceptance Criterion: "All test cases pass/fail as specified"
        validator = HaikuValidator(
            "Action:Deploy; REF:Runbook_Deployment:Recovery_Section"
        )
        result = validator.run()
        assert result.is_valid is True

    @pytest.mark.unit
    def test_result_has_elapsed_seconds(self, validator_simple):
        # Acceptance Criterion: "Validation pipeline diagram created"
        result = validator_simple.run()
        assert result.elapsed_seconds >= 0

    @pytest.mark.unit
    def test_validate_haiku_string_convenience_function(self):
        # Acceptance Criterion: "Python validator implementation provided"
        is_valid, findings = validate_haiku_string("Action:Deploy")
        assert is_valid is True
        assert isinstance(findings, list)


# ════════════════════════════════════════════════════════════════════
# 5.2 — EDGE CASE TESTS
# ════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests for boundary conditions and unusual inputs."""

    @pytest.mark.unit
    def test_run_empty_string_returns_invalid(self):
        # Edge Case: empty input
        validator = HaikuValidator("")
        result = validator.run()
        assert result.is_valid is False
        assert len(result.errors) > 0

    @pytest.mark.unit
    def test_run_whitespace_only_returns_invalid(self):
        # Edge Case: whitespace-only input
        validator = HaikuValidator("   \t\n  ")
        result = validator.run()
        assert result.is_valid is False

    @pytest.mark.unit
    def test_run_single_semicolon_returns_invalid(self):
        # Edge Case: minimal invalid input
        validator = HaikuValidator(";")
        result = validator.run()
        assert result.is_valid is False

    @pytest.mark.unit
    def test_run_very_long_haiku_valid(self):
        # Edge Case: boundary value (long input)
        long_haiku = "; ".join(
            ["Action:Step_%d" % i for i in range(50)]
        )
        validator = HaikuValidator(long_haiku)
        result = validator.run()
        assert result.is_valid is True
        assert result.stages_run == 5

    @pytest.mark.unit
    def test_run_stop_on_error_halts_pipeline(self):
        # Edge Case: stop_on_error flag behavior
        validator = HaikuValidator("", stop_on_error=True)
        result = validator.run()
        assert result.is_valid is False
        assert result.stages_run == 1

    @pytest.mark.unit
    def test_build_context_excerpt_at_start(self):
        # Edge Case: position at start of string
        validator = HaikuValidator("Action:Deploy")
        excerpt = validator._build_context_excerpt(0)
        assert "▶" in excerpt
        assert "◀" in excerpt

    @pytest.mark.unit
    def test_build_context_excerpt_at_end(self):
        # Edge Case: position at end of string
        validator = HaikuValidator("Action:Deploy")
        excerpt = validator._build_context_excerpt(12)
        assert "▶" in excerpt

    @pytest.mark.unit
    def test_build_context_excerpt_empty_input(self):
        # Edge Case: empty input for context building
        validator = HaikuValidator("")
        excerpt = validator._build_context_excerpt(0)
        assert excerpt == "(empty input)"

    @pytest.mark.unit
    def test_build_context_excerpt_position_beyond_string(self):
        # Edge Case: position beyond string length
        validator = HaikuValidator("short")
        excerpt = validator._build_context_excerpt(100)
        assert "▶" in excerpt

    @pytest.mark.unit
    def test_validation_error_dataclass_defaults(self):
        # Edge Case: ValidationError with default fields
        error = ValidationError(
            code="TEST-001",
            severity=ErrorSeverity.ERROR,
            message="Test error",
            position=0,
        )
        assert error.suggestion == ""
        assert error.context == ""

    @pytest.mark.unit
    def test_error_severity_enum_values(self):
        # Edge Case: enum ordering
        assert ErrorSeverity.INFO.value < ErrorSeverity.WARNING.value
        assert ErrorSeverity.WARNING.value < ErrorSeverity.ERROR.value


# ════════════════════════════════════════════════════════════════════
# 5.3 — ERROR PATH TESTS (one per validation rule)
# ════════════════════════════════════════════════════════════════════


class TestRule001Syntactic:
    """VAL-001: Syntactic Well-Formedness (Stage 1)."""

    @pytest.mark.unit
    def test_validate_syntactic_invalid_character_returns_error(self):
        # Acceptance Criterion: "Minimum 5 validation rules specified"
        validator = HaikuValidator("Action:Deploy [broken")
        result = validator.run()
        assert result.is_valid is False
        errors = [e for e in result.errors if e.code == "VAL-001"]
        assert len(errors) > 0

    @pytest.mark.unit
    def test_validate_syntactic_error_has_position(self):
        # Acceptance Criterion: "Each rule includes at least one passing and one failing example"
        validator = HaikuValidator("Action:Deploy [broken")
        result = validator.run()
        errors = [e for e in result.errors if e.code == "VAL-001"]
        assert len(errors) > 0
        assert errors[0].position >= 0

    @pytest.mark.unit
    def test_validate_syntactic_error_has_suggestion(self):
        # Acceptance Criterion: "Error messages are user-friendly and actionable"
        validator = HaikuValidator("Action:Deploy [broken")
        result = validator.run()
        errors = [e for e in result.errors if e.code == "VAL-001"]
        assert len(errors) > 0
        assert errors[0].suggestion != ""

    @pytest.mark.unit
    def test_validate_syntactic_error_has_context(self):
        # Acceptance Criterion: "Error messages are user-friendly and actionable"
        validator = HaikuValidator("Action:Deploy [broken")
        result = validator.run()
        errors = [e for e in result.errors if e.code == "VAL-001"]
        assert len(errors) > 0
        assert errors[0].context != ""

    @pytest.mark.unit
    def test_validate_syntactic_missing_identifier_returns_error(self):
        # Acceptance Criterion: "Each rule includes at least one failing example"
        validator = HaikuValidator("Action:")
        result = validator.run()
        assert result.is_valid is False


class TestRule002Semantic:
    """VAL-002: Operator Completeness (Stage 2)."""

    @pytest.mark.unit
    def test_validate_semantic_if_without_then_returns_error(self):
        # Acceptance Criterion: "Each rule has Rule ID, Name, Severity, Description, Check Method"
        # IF:Condition alone gets caught by the parser (Stage 1) as structural error
        validator = HaikuValidator("IF:Condition")
        result = validator.run()
        assert result.is_valid is False

    @pytest.mark.unit
    def test_validate_semantic_requires_without_state_returns_error(self):
        # Acceptance Criterion: "Each rule includes at least one failing example"
        validator = HaikuValidator("REQUIRES State:Online")
        result = validator.run()
        assert result.is_valid is False

    @pytest.mark.unit
    def test_validate_semantic_valid_if_then_passes(self):
        # Acceptance Criterion: "Each rule includes at least one passing example"
        validator = HaikuValidator(
            "IF:Success THEN:Action:Continue ELSE:Action:Rollback"
        )
        result = validator.run()
        assert result.is_valid is True


class TestRule003Referential:
    """VAL-003: Reference Definition (Stage 3)."""

    @pytest.mark.unit
    def test_validate_referential_undefined_condition_warns(self):
        # Acceptance Criterion: "Each rule includes at least one failing example"
        validator = HaikuValidator(
            "IF:Undefined_Condition THEN:Action:Continue"
        )
        result = validator.run()
        # Undefined conditions produce warnings, not errors
        warnings = [w for w in result.warnings if w.code == "VAL-003"]
        assert len(warnings) > 0
        assert "Undefined_Condition" in warnings[0].message

    @pytest.mark.unit
    def test_validate_referential_defined_condition_no_warning(self):
        # Acceptance Criterion: "Each rule includes at least one passing example"
        # When IF condition matches a defined Action, no warning
        validator = HaikuValidator(
            "Action:Success; IF:Success THEN:Action:Continue"
        )
        result = validator.run()
        ref_warnings = [w for w in result.warnings if w.code == "VAL-003"]
        assert len(ref_warnings) == 0

    @pytest.mark.unit
    def test_validate_referential_warn_consequence_undefined(self):
        # Acceptance Criterion: "Each rule includes at least one failing example"
        validator = HaikuValidator(
            "Action:Delete WARN:No_Recovery -> Data_Loss"
        )
        result = validator.run()
        warnings = [w for w in result.warnings if w.code == "VAL-003"]
        assert len(warnings) > 0
        assert "Data_Loss" in warnings[0].message


class TestRule004Completeness:
    """VAL-004: Circular Dependency Detection (Stage 4)."""

    @pytest.mark.unit
    def test_validate_completeness_self_reference_returns_error(self):
        # Acceptance Criterion: "Each rule includes at least one failing example"
        validator = HaikuValidator("Action:Deploy REQUIRES State:Deploy")
        result = validator.run()
        errors = [e for e in result.errors if e.code == "VAL-004"]
        assert len(errors) > 0
        assert "Self-referential" in errors[0].message

    @pytest.mark.unit
    def test_validate_completeness_mutual_dependency_returns_error(self):
        # Acceptance Criterion: "Each rule includes at least one failing example"
        validator = HaikuValidator(
            "Action:A REQUIRES State:B; Action:B REQUIRES State:A"
        )
        result = validator.run()
        errors = [e for e in result.errors if e.code == "VAL-004"]
        assert len(errors) > 0
        assert "Circular" in errors[0].message

    @pytest.mark.unit
    def test_validate_completeness_linear_chain_passes(self):
        # Acceptance Criterion: "Each rule includes at least one passing example"
        validator = HaikuValidator(
            "Action:Init REQUIRES State:Empty; "
            "Action:Populate REQUIRES State:Initialized"
        )
        result = validator.run()
        errors = [e for e in result.errors if e.code == "VAL-004"]
        assert len(errors) == 0

    @pytest.mark.unit
    def test_validate_completeness_no_requires_passes(self):
        # Acceptance Criterion: "Each rule includes at least one passing example"
        validator = HaikuValidator("Action:Deploy; Action:Verify")
        result = validator.run()
        errors = [e for e in result.errors if e.code == "VAL-004"]
        assert len(errors) == 0


class TestRule005Verification:
    """VAL-005: Verifiable Checks (Stage 5)."""

    @pytest.mark.unit
    def test_validate_execution_vague_verify_warns(self):
        # Acceptance Criterion: "Each rule includes at least one failing example"
        validator = HaikuValidator("Action:Deploy; VERIFY:Deployment_OK")
        result = validator.run()
        warnings = [w for w in result.warnings if w.code == "VAL-005"]
        assert len(warnings) > 0
        assert "automatable" in warnings[0].message

    @pytest.mark.unit
    def test_validate_execution_specific_verify_no_warning(self):
        # Acceptance Criterion: "Each rule includes at least one passing example"
        validator = HaikuValidator("Action:Deploy; VERIFY:Service_Running")
        result = validator.run()
        warnings = [w for w in result.warnings if w.code == "VAL-005"]
        assert len(warnings) == 0

    @pytest.mark.unit
    def test_validate_execution_short_verify_warns(self):
        # Acceptance Criterion: "Each rule includes at least one failing example"
        validator = HaikuValidator("Action:Deploy; VERIFY:Up")
        result = validator.run()
        warnings = [w for w in result.warnings if w.code == "VAL-005"]
        assert len(warnings) > 0
        assert "short" in warnings[0].message

    @pytest.mark.unit
    def test_validate_execution_all_vague_terms_detected(self):
        # Acceptance Criterion: "Each rule includes at least one failing example"
        for term in VAGUE_VERIFY_TERMS:
            validator = HaikuValidator("Action:Deploy; VERIFY:%s" % term)
            result = validator.run()
            warnings = [w for w in result.warnings if w.code == "VAL-005"]
            assert len(warnings) > 0, "VAGUE_VERIFY_TERMS '%s' not detected" % term


class TestRule006RefResolution:
    """VAL-006: REF Target Resolution (Stage 5)."""

    @pytest.mark.unit
    def test_validate_execution_valid_ref_format_passes(self):
        # Acceptance Criterion: "Each rule includes at least one passing example"
        validator = HaikuValidator(
            "Action:Deploy; REF:Runbook_Deploy:Recovery"
        )
        result = validator.run()
        errors = [e for e in result.errors if e.code == "VAL-006"]
        assert len(errors) == 0

    @pytest.mark.unit
    def test_validate_execution_short_ref_warns(self):
        # Acceptance Criterion: "Each rule includes at least one failing example"
        validator = HaikuValidator("Action:Deploy; REF:AB")
        result = validator.run()
        warnings = [w for w in result.warnings if w.code == "VAL-006"]
        assert len(warnings) > 0
        assert "short" in warnings[0].message


# ════════════════════════════════════════════════════════════════════
# 5.3 (continued) — ERROR TAXONOMY & ERROR CODE TESTS
# ════════════════════════════════════════════════════════════════════


class TestErrorTaxonomy:
    """Verify error codes and severity levels match the v0.0.2d taxonomy."""

    @pytest.mark.unit
    def test_val001_is_error_severity(self):
        # Acceptance Criterion: "Error codes assigned (1xx-5xx range)"
        validator = HaikuValidator("Action:Deploy [broken")
        result = validator.run()
        for error in result.errors:
            if error.code == "VAL-001":
                assert error.severity == ErrorSeverity.ERROR

    @pytest.mark.unit
    def test_val003_is_warning_severity(self):
        # Acceptance Criterion: "Error codes assigned (1xx-5xx range)"
        validator = HaikuValidator(
            "IF:Unknown THEN:Action:Continue"
        )
        result = validator.run()
        for warning in result.warnings:
            if warning.code == "VAL-003":
                assert warning.severity == ErrorSeverity.WARNING

    @pytest.mark.unit
    def test_val005_is_warning_severity(self):
        # Acceptance Criterion: "Error codes assigned (1xx-5xx range)"
        validator = HaikuValidator("Action:Deploy; VERIFY:Deployment_OK")
        result = validator.run()
        for warning in result.warnings:
            if warning.code == "VAL-005":
                assert warning.severity == ErrorSeverity.WARNING

    @pytest.mark.unit
    def test_all_errors_have_suggestion(self):
        # Acceptance Criterion: "Error messages are user-friendly and actionable"
        validator = HaikuValidator("Action:Deploy [broken")
        result = validator.run()
        for error in result.errors:
            assert error.suggestion != "", (
                "Error %s missing suggestion" % error.code
            )

    @pytest.mark.unit
    def test_all_warnings_have_suggestion(self):
        # Acceptance Criterion: "Error messages are user-friendly and actionable"
        validator = HaikuValidator("Action:Deploy; VERIFY:Deployment_OK")
        result = validator.run()
        for warning in result.warnings:
            assert warning.suggestion != "", (
                "Warning %s missing suggestion" % warning.code
            )


# ════════════════════════════════════════════════════════════════════
# 5.3 (continued) — RECOVERY STRATEGY TESTS
# ════════════════════════════════════════════════════════════════════


class TestRecoveryStrategies:
    """Tests for auto-correction and error aggregation strategies."""

    @pytest.mark.unit
    def test_suggest_fix_misspelled_operator_returns_correction(self):
        # Acceptance Criterion: "Recovery strategies documented (auto-correct)"
        result = suggest_fix("VAL-101", "Acton:")
        assert "Action:" in result

    @pytest.mark.unit
    def test_suggest_fix_unknown_code_returns_empty(self):
        # Acceptance Criterion: "Recovery strategies documented"
        result = suggest_fix("VAL-999", "anything")
        assert result == ""

    @pytest.mark.unit
    def test_suggest_fix_val102_bracket_returns_advice(self):
        # Acceptance Criterion: "Recovery strategies documented"
        result = suggest_fix("VAL-102")
        assert "bracket" in result.lower()

    @pytest.mark.unit
    def test_suggest_fix_val201_if_returns_then_advice(self):
        # Acceptance Criterion: "Recovery strategies documented"
        result = suggest_fix("VAL-201", "IF")
        assert "THEN" in result

    @pytest.mark.unit
    def test_suggest_fix_val301_returns_define_advice(self):
        # Acceptance Criterion: "Recovery strategies documented"
        result = suggest_fix("VAL-301", "Missing_State")
        assert "Missing_State" in result

    @pytest.mark.unit
    def test_error_aggregation_collects_all_stages(self):
        # Acceptance Criterion: "Recovery strategies documented (aggregation)"
        # A haiku with multiple problems across stages
        validator = HaikuValidator(
            "Action:Deploy REQUIRES State:Deploy; VERIFY:Done"
        )
        result = validator.run()
        # Should have VAL-004 (self-ref) + VAL-005 (vague verify)
        all_codes = set()
        for e in result.errors:
            all_codes.add(e.code)
        for w in result.warnings:
            all_codes.add(w.code)
        assert len(all_codes) >= 2, "Aggregation should collect errors from multiple stages"


# ════════════════════════════════════════════════════════════════════
# 5.3 (continued) — LEVENSHTEIN & AUTO-CORRECTION TESTS
# ════════════════════════════════════════════════════════════════════


class TestLevenshteinAutoCorrection:
    """Tests for the Levenshtein distance and operator correction logic."""

    @pytest.mark.unit
    def test_levenshtein_identical_strings_returns_zero(self):
        assert _levenshtein_distance("Action", "Action") == 0

    @pytest.mark.unit
    def test_levenshtein_empty_second_string(self):
        assert _levenshtein_distance("Action", "") == 6

    @pytest.mark.unit
    def test_levenshtein_single_char_difference(self):
        assert _levenshtein_distance("Action", "Acton") == 1

    @pytest.mark.unit
    def test_levenshtein_completely_different(self):
        assert _levenshtein_distance("abc", "xyz") == 3

    @pytest.mark.unit
    def test_find_closest_operator_acton_returns_action(self):
        result = _find_closest_operator("Acton")
        assert result is not None
        assert "Action" in result

    @pytest.mark.unit
    def test_find_closest_operator_veify_returns_verify(self):
        result = _find_closest_operator("VEIFY")
        assert result is not None
        assert "VERIFY" in result

    @pytest.mark.unit
    def test_find_closest_operator_completely_wrong_returns_none(self):
        result = _find_closest_operator("XYZZYPLUGH")
        assert result is None


# ════════════════════════════════════════════════════════════════════
# 5.4 — LOG OUTPUT TESTS
# ════════════════════════════════════════════════════════════════════


class TestLogOutput:
    """Verify logging output using caplog fixture."""

    @pytest.mark.unit
    def test_run_logs_pipeline_started(self, caplog):
        # Acceptance Criterion: "Python validator implementation provided"
        with caplog.at_level(logging.INFO, logger="haiku_validator"):
            validator = HaikuValidator("Action:Deploy")
            validator.run()
        assert "Validation pipeline started" in caplog.text

    @pytest.mark.unit
    def test_run_logs_pipeline_complete(self, caplog):
        # Acceptance Criterion: "Python validator implementation provided"
        with caplog.at_level(logging.INFO, logger="haiku_validator"):
            validator = HaikuValidator("Action:Deploy")
            validator.run()
        assert "Validation pipeline complete" in caplog.text

    @pytest.mark.unit
    def test_run_logs_stage_1_syntactic(self, caplog):
        # Acceptance Criterion: "Validation pipeline diagram created"
        with caplog.at_level(logging.INFO, logger="haiku_validator"):
            validator = HaikuValidator("Action:Deploy")
            validator.run()
        assert "Stage 1 (Syntactic)" in caplog.text

    @pytest.mark.unit
    def test_run_logs_stage_2_semantic(self, caplog):
        # Acceptance Criterion: "Validation pipeline diagram created"
        with caplog.at_level(logging.INFO, logger="haiku_validator"):
            validator = HaikuValidator("Action:Deploy")
            validator.run()
        assert "Stage 2 (Semantic)" in caplog.text

    @pytest.mark.unit
    def test_run_logs_stage_5_execution(self, caplog):
        # Acceptance Criterion: "Validation pipeline diagram created"
        with caplog.at_level(logging.INFO, logger="haiku_validator"):
            validator = HaikuValidator("Action:Deploy")
            validator.run()
        assert "Stage 5 (Execution)" in caplog.text

    @pytest.mark.unit
    def test_error_logged_at_error_level(self, caplog):
        # Acceptance Criterion: "Error messages are user-friendly and actionable"
        with caplog.at_level(logging.ERROR, logger="haiku_validator"):
            validator = HaikuValidator("Action:Deploy [broken")
            validator.run()
        assert "VAL-001" in caplog.text

    @pytest.mark.unit
    def test_warning_logged_at_warning_level(self, caplog):
        # Acceptance Criterion: "Error messages are user-friendly and actionable"
        with caplog.at_level(logging.WARNING, logger="haiku_validator"):
            validator = HaikuValidator("Action:Deploy; VERIFY:Deployment_OK")
            validator.run()
        assert "VAL-005" in caplog.text

    @pytest.mark.unit
    def test_convenience_function_logs_call(self, caplog):
        # Acceptance Criterion: "Python validator implementation provided"
        with caplog.at_level(logging.INFO, logger="haiku_validator"):
            validate_haiku_string("Action:Deploy")
        assert "validate_haiku_string called" in caplog.text


# ════════════════════════════════════════════════════════════════════
# 5.5 — USE CASE TESTS
# ════════════════════════════════════════════════════════════════════


class TestUseCase:
    """End-to-end tests simulating the developer workflow from the spec."""

    @pytest.mark.unit
    def test_developer_validates_haiku_receives_all_errors(self):
        # Use Case: "Developer writes a haiku string, runs it through
        # HaikuValidator, receives a list of all validation errors."
        haiku = (
            "Action:Deploy REQUIRES State:Deploy; "  # Self-referential (VAL-004)
            "VERIFY:Done"                             # Vague verify (VAL-005)
        )
        is_valid, findings = validate_haiku_string(haiku)

        # Should not be valid (self-ref is an error)
        assert is_valid is False

        # Should have findings from multiple stages
        codes = {f.code for f in findings}
        assert "VAL-004" in codes, "Should detect self-referential dependency"
        assert "VAL-005" in codes, "Should detect vague verification check"

        # Each finding should have actionable fields
        for finding in findings:
            assert finding.code != ""
            assert finding.message != ""
            assert finding.suggestion != ""
            assert finding.context != ""
            assert isinstance(finding.severity, ErrorSeverity)

    @pytest.mark.unit
    def test_developer_validates_clean_haiku_gets_empty_findings(self):
        # Use Case: "If valid, the validator returns (True, [])."
        haiku = "Action:Deploy REQUIRES State:Online -> EXEC:deploy.sh; VERIFY:Service_Running"
        is_valid, findings = validate_haiku_string(haiku)

        assert is_valid is True
        # There might be warnings, but no errors
        error_findings = [f for f in findings if f.severity == ErrorSeverity.ERROR]
        assert len(error_findings) == 0

    @pytest.mark.unit
    def test_developer_uses_stop_on_error_for_fast_feedback(self):
        # Use Case: Developer wants quick fail-fast validation
        haiku = "this is not a valid haiku at all"
        is_valid, findings = validate_haiku_string(haiku, stop_on_error=True)

        assert is_valid is False
        assert len(findings) > 0
        # With stop_on_error, only stage 1 should run
        # Can't directly check stages_run from convenience function,
        # but we can verify errors exist

    @pytest.mark.unit
    def test_developer_gets_fix_suggestion_for_misspelling(self):
        # Use Case: "each error includes a suggested fix"
        suggestion = suggest_fix("VAL-101", "Acton:")
        assert suggestion != ""
        assert "Action:" in suggestion

    @pytest.mark.unit
    def test_full_pipeline_complex_composition(self):
        # Use Case: Full end-to-end with the most complex haiku from v0.0.2c spec
        haiku = (
            "META:author=DevOps; "
            "Action:Backup REQUIRES State:Online -> EXEC:backup.sh; "
            "IF:Success THEN:Action:Verify ELSE:Action:Alert; "
            "VERIFY:Backup_Exists"
        )
        validator = HaikuValidator(haiku)
        result = validator.run()

        assert result.stages_run == 5
        assert result.elapsed_seconds >= 0
        assert isinstance(result.errors, list)
        assert isinstance(result.warnings, list)
        assert isinstance(result.info, list)
