# v0.2.3a — CNL Statement Data Model

<aside>

**Version:** v0.2.3a

**Parent:** v0.2.3 — CNL Synthesis Engine

**Status:** ⬜ Not Started

**Duration:** 15–25 minutes

**Deliverable:** `CNLStatement` dataclass, `SynthesisConfig` configuration, `OperatorType` enum, type definitions, and comprehensive unit tests in `src/synthesizer.py` and `tests/test_synthesizer.py`

</aside>

---

## Objective

Define the foundational data structures for the CNL synthesis module. This sub-part creates the `CNLStatement` dataclass that represents a single operator expression ready for rendering as a CNL string, the `SynthesisConfig` configuration dataclass that controls synthesis behavior, and the `OperatorType` enum that defines all supported operators in the Haiku Protocol grammar. These structures serve as the contract between entity extraction (v0.2.2) and CNL string rendering (v0.2.3b–c), enabling a clean transformation pipeline: extracted entities → CNL statements → compressed CNL strings.

---

## User Stories

> As a CNL synthesizer developer, I want a well-typed `CNLStatement` container that represents a single operator expression so that I can compose extracted entities into valid Haiku Protocol statements without manual string concatenation.

> As a pipeline integrator, I want `CNLStatement` instances to be serializable and deserializable so that I can log, cache, and inspect intermediate synthesis results at every stage.

---

## Data Model Design

### CNLStatement Dataclass

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class CNLStatement:
    """A single CNL statement ready for string rendering.

    Each CNLStatement represents one complete operator expression
    in the Haiku Protocol grammar. Statements are composed into
    full CNL strings by the synthesizer (v0.2.3b–c).

    Attributes:
        operator: Operator keyword from grammar (e.g., 'Action', 'State',
            'EXEC', 'WARN', 'VERIFY', 'IF', 'META', 'NOTE', 'LOOP', 'REF').
        value: Primary operand — the identifier or content for this statement.
            Must follow naming conventions: PascalCase_With_Underscores for
            identifiers, lowercase for commands.
        modifier: Optional relationship modifier (e.g., 'REQUIRES', '->').
            Connects this statement to another statement or state list.
        target: Optional target of the modifier. For REQUIRES, this is a
            comma-separated list of State identifiers. For WARN, this is
            the consequence identifier.
        source_chunk_id: Optional chunk ID this statement was derived from.
            Used for traceability back to the original document.
        confidence: Confidence score inherited from extraction (0.0–1.0).
            Statements with confidence below threshold may be flagged.
    """
    operator: str
    value: str
    modifier: Optional[str] = None
    target: Optional[str] = None
    source_chunk_id: Optional[str] = None
    confidence: float = 1.0

    def to_cnl(self) -> str:
        """Render CNLStatement as a CNL string fragment.

        Produces a single operator expression conforming to the Haiku
        Protocol grammar. The format depends on the operator and modifier.

        Examples:
            Action only: "Action:Restart_Server"
            Action with REQUIRES: "Action:Restart_Server REQUIRES State:Config_Saved"
            Action with flow: "Action:Backup -> EXEC:rsync -a /data /backup"
            WARN with consequence: "WARN:Data_Loss"
            State standalone: "State:Config_Saved"

        Returns:
            String representation ready to be joined with other statements.
        """
        base = f"{self.operator}:{self.value}"

        if self.modifier and self.target:
            # Composite expression: operator:value modifier target
            return f"{base} {self.modifier} {self.target}"
        elif self.modifier:
            # Modifier without target (edge case, returned as-is)
            return f"{base} {self.modifier}"
        else:
            # Simple operator:value
            return base

    def to_dict(self) -> dict:
        """Serialize CNLStatement to a JSON-compatible dictionary.

        Returns:
            Dictionary with all CNLStatement fields. None values are included
            to maintain schema consistency.
        """
        return {
            "operator": self.operator,
            "value": self.value,
            "modifier": self.modifier,
            "target": self.target,
            "source_chunk_id": self.source_chunk_id,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CNLStatement":
        """Deserialize a dictionary into a CNLStatement instance.

        Args:
            data: Dictionary with CNLStatement field names as keys.

        Returns:
            CNLStatement instance.

        Raises:
            KeyError: If required fields (operator, value) are missing.
            TypeError: If field types do not match expected types.
        """
        return cls(
            operator=data["operator"],
            value=data["value"],
            modifier=data.get("modifier"),
            target=data.get("target"),
            source_chunk_id=data.get("source_chunk_id"),
            confidence=data.get("confidence", 1.0),
        )

    def __repr__(self) -> str:
        """Human-readable representation of the statement."""
        parts = [f"op={self.operator!r}", f"val={self.value!r}"]
        if self.modifier:
            parts.append(f"mod={self.modifier!r}")
        if self.target:
            parts.append(f"tgt={self.target!r}")
        return f"CNLStatement({', '.join(parts)})"

    @property
    def is_valid(self) -> bool:
        """Check if statement has all required fields and valid values.

        Returns:
            True if operator is non-empty string and value is non-empty string.
        """
        return (
            isinstance(self.operator, str)
            and self.operator.strip() != ""
            and isinstance(self.value, str)
            and self.value.strip() != ""
        )
```

### SynthesisConfig Dataclass

```python
@dataclass
class SynthesisConfig:
    """Configuration for CNL synthesis behavior.

    Controls how extracted entities are transformed into CNL statements
    and how those statements are rendered into final CNL strings.

    Attributes:
        use_flow_operators: If True, use '->' for sequential flow between
            actions and their EXEC commands. If False, use ';' only.
            Default True.
        include_standalone_states: If True, emit State: declarations for
            states not consumed by a REQUIRES clause. Default True.
        warn_on_empty_entities: If True, log a warning when entities dict
            has no extractable content. Default True.
        statement_separator: Character(s) used to join statements.
            Default '; '.
        max_identifier_length: Maximum length for formatted identifiers.
            Default 32 (from grammar spec).
    """
    use_flow_operators: bool = True
    include_standalone_states: bool = True
    warn_on_empty_entities: bool = True
    statement_separator: str = "; "
    max_identifier_length: int = 32
```

### OperatorType Enum

```python
from enum import Enum

class OperatorType(str, Enum):
    """CNL operators supported by the synthesizer.

    Maps to the 12 operators defined in the Haiku Protocol grammar (v0.0.2b).
    The synthesizer in v0.2.3 handles a subset of these: the 5 core entity
    types plus SEQ (implicit via ';') and flow ('->'). IF/THEN/ELSE, LOOP,
    VERIFY, REF, META, and NOTE are defined here for forward compatibility
    but not synthesized in v0.2.0.

    Attributes:
        ACTION: Procedural step (core entity type)
        STATE: Precondition or postcondition (core entity type)
        EXEC: Executable command (core entity type)
        WARN: Risk/consequence declaration (core entity type)
        REQUIRES: Dependency relationship (core entity type)
        VERIFY: Verification step (forward compatible, not synthesized yet)
        IF: Conditional operator (forward compatible, not synthesized yet)
        THEN: Consequent of IF (forward compatible, not synthesized yet)
        ELSE: Alternative consequent (forward compatible, not synthesized yet)
        SEQ: Sequential composition (implicit via ';')
        REF: Reference to another statement (forward compatible)
        META: Metadata declaration (forward compatible)
        LOOP: Iterative composition (forward compatible, not synthesized yet)
        NOTE: Commentary or annotation (forward compatible, not synthesized yet)
    """
    ACTION = "Action"
    STATE = "State"
    EXEC = "EXEC"
    WARN = "WARN"
    REQUIRES = "REQUIRES"
    VERIFY = "VERIFY"
    IF = "IF"
    THEN = "THEN"
    ELSE = "ELSE"
    SEQ = "SEQ"
    REF = "REF"
    META = "META"
    LOOP = "LOOP"
    NOTE = "NOTE"
```

### Naming Conventions

The following naming conventions (from the Haiku Protocol grammar) are enforced during synthesis:

```python
import re

# Actions and States: PascalCase_With_Underscores
# Examples: Restart_Server, Config_Saved, Database_Active
IDENTIFIER_PATTERN = re.compile(r'^[A-Z][A-Za-z0-9]*(_[A-Z][A-Za-z0-9]*)*$')

# Commands: lowercase shell syntax
# Examples: systemctl restart app-server, curl https://example.com
COMMAND_PATTERN = re.compile(r'^[a-z0-9]')

# META keys: lowercase_with_underscores
# Examples: compatible_with, version, author
META_KEY_PATTERN = re.compile(r'^[a-z][a-z0-9]*(_[a-z0-9]+)*$')


def validate_identifier(name: str) -> bool:
    """Check if name follows PascalCase_With_Underscores convention.

    Args:
        name: Entity name to validate.

    Returns:
        True if name matches the Haiku Protocol identifier format.

    Examples:
        >>> validate_identifier("Restart_Server")
        True
        >>> validate_identifier("restart_server")
        False
        >>> validate_identifier("ConfigValid")
        False  # missing underscore between words
    """
    return bool(IDENTIFIER_PATTERN.match(name))


def validate_command(command: str) -> bool:
    """Check if command follows lowercase shell syntax convention.

    Args:
        command: Command string to validate.

    Returns:
        True if command starts with lowercase letter or digit.
    """
    return bool(command and COMMAND_PATTERN.match(command))


def validate_meta_key(key: str) -> bool:
    """Check if META key follows lowercase_with_underscores convention.

    Args:
        key: META key to validate.

    Returns:
        True if key matches the lowercase_with_underscores format.
    """
    return bool(META_KEY_PATTERN.match(key))
```

---

## File Structure

```
src/
└── synthesizer.py          # CNLStatement, SynthesisConfig, OperatorType + validators + logger

tests/
└── test_synthesizer.py     # Unit tests for data model
```

---

## Implementation Workflow

```
┌────────────────────────────────────────────────────────────────┐
│              v0.2.3a IMPLEMENTATION FLOW                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  STEP 1: Create src/synthesizer.py skeleton                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Module docstring + logger declaration                  │  │
│  │ • OperatorType enum (14 operators)                       │  │
│  │ • CNLStatement dataclass with all fields                 │  │
│  │ • to_cnl(), to_dict(), from_dict(), __repr__()           │  │
│  │ • is_valid property                                      │  │
│  │ • SynthesisConfig dataclass with defaults                │  │
│  │ • Naming convention validators                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│  STEP 2: Create tests/test_synthesizer.py                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Happy path: construction, field access, defaults       │  │
│  │ • to_cnl() rendering: simple, REQUIRES, ->, WARN         │  │
│  │ • Serialization: to_dict, from_dict, roundtrip           │  │
│  │ • is_valid property: valid/invalid cases                 │  │
│  │ • Edge cases: empty value, long identifier, Unicode      │  │
│  │ • Error paths: missing required field, type errors       │  │
│  │ • Config: defaults, overrides                            │  │
│  │ • Validators: identifier, command, meta_key formats      │  │
│  │ • Logging: logger initialization                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│  STEP 3: Run tests + verify                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ $ python -m pytest tests/test_synthesizer.py -v          │  │
│  │ • All tests green (≥25 tests)                            │  │
│  │ • No import errors                                       │  │
│  │ • Logger present in module                               │  │
│  │ • to_cnl() outputs match grammar spec                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Unit Testing Requirements

### Test Categories and Minimums

| Category | Tests | Description |
|----------|-------|-------------|
| **Happy Path** | 5 | CNLStatement construction, field access, defaults, repr output, config defaults |
| **Serialization** | 5 | `to_dict()` keys, `from_dict()` roundtrip, `to_cnl()` output, missing optional fields, JSON compatibility |
| **to_cnl() Rendering** | 5 | Action only, Action+REQUIRES, Action+EXEC (->), WARN with consequence, State standalone |
| **Edge Cases** | 4 | Empty value, very long identifier, Unicode content, operator not in enum |
| **Error Paths** | 3 | `from_dict()` missing required field, empty operator string, None for required field |
| **Config** | 2 | Default values, custom overrides |
| **Validators** | 2 | Identifier format validation, command format validation |
| **Logging** | 1 | Logger initialized with `__name__` |

**Total minimum: 27 tests**

### Test Naming Convention

```python
# Pattern: test_{class}_{method_or_aspect}_{scenario}_{expected}
def test_cnl_statement_init_all_fields_populated():
def test_cnl_statement_to_cnl_action_only_renders_operator_colon_value():
def test_cnl_statement_to_cnl_action_requires_state_includes_modifier_and_target():
def test_cnl_statement_from_dict_missing_operator_raises_key_error():
def test_synthesis_config_defaults_use_flow_operators_true():
def test_validate_identifier_pascal_case_with_underscores_valid():
def test_validate_command_lowercase_shell_syntax_valid():
```

### Example Test Code

```python
import pytest
from src.synthesizer import (
    CNLStatement,
    SynthesisConfig,
    OperatorType,
    validate_identifier,
    validate_command,
    validate_meta_key,
)


class TestCNLStatementDataModel:
    """Tests for the CNLStatement dataclass. (v0.2.3a)"""

    # --- Happy Path ---

    # Acceptance Criterion: "CNLStatement has all required and optional fields"
    def test_cnl_statement_init_all_fields_populated(self):
        """CNLStatement can be created with all fields."""
        stmt = CNLStatement(
            operator="Action",
            value="Restart_Server",
            modifier="REQUIRES",
            target="State:Config_Saved",
            source_chunk_id="chunk-042",
            confidence=0.95,
        )
        assert stmt.operator == "Action"
        assert stmt.value == "Restart_Server"
        assert stmt.modifier == "REQUIRES"
        assert stmt.target == "State:Config_Saved"
        assert stmt.source_chunk_id == "chunk-042"
        assert stmt.confidence == 0.95

    # Acceptance Criterion: "Optional fields default to sensible values"
    def test_cnl_statement_init_defaults(self):
        """Optional fields default to None and confidence defaults to 1.0."""
        stmt = CNLStatement(operator="State", value="Config_Saved")
        assert stmt.modifier is None
        assert stmt.target is None
        assert stmt.source_chunk_id is None
        assert stmt.confidence == 1.0

    # Acceptance Criterion: "CNLStatement repr is human-readable"
    def test_cnl_statement_repr_includes_operator_and_value(self):
        """repr() output is concise and informative."""
        stmt = CNLStatement(operator="Action", value="Restart_Server")
        repr_str = repr(stmt)
        assert "op='Action'" in repr_str
        assert "val='Restart_Server'" in repr_str

    # --- to_cnl() Rendering ---

    # Acceptance Criterion: "to_cnl() renders simple operator:value statements"
    def test_cnl_statement_to_cnl_action_only(self):
        """Simple action renders as 'Action:Restart_Server'."""
        stmt = CNLStatement(operator="Action", value="Restart_Server")
        assert stmt.to_cnl() == "Action:Restart_Server"

    # Acceptance Criterion: "to_cnl() renders REQUIRES relationships"
    def test_cnl_statement_to_cnl_action_requires_state(self):
        """Action with REQUIRES renders full relationship."""
        stmt = CNLStatement(
            operator="Action",
            value="Restart_Server",
            modifier="REQUIRES",
            target="State:Config_Saved",
        )
        assert stmt.to_cnl() == "Action:Restart_Server REQUIRES State:Config_Saved"

    # Acceptance Criterion: "to_cnl() renders flow operators"
    def test_cnl_statement_to_cnl_action_flow_exec(self):
        """Action with -> to EXEC renders flow."""
        stmt = CNLStatement(
            operator="Action",
            value="Backup",
            modifier="->",
            target="EXEC:rsync -a /data /backup",
        )
        assert stmt.to_cnl() == "Action:Backup -> EXEC:rsync -a /data /backup"

    # Acceptance Criterion: "to_cnl() renders WARN statements"
    def test_cnl_statement_to_cnl_warn_with_consequence(self):
        """WARN renders with consequence as value."""
        stmt = CNLStatement(operator="WARN", value="Data_Loss")
        assert stmt.to_cnl() == "WARN:Data_Loss"

    # Acceptance Criterion: "to_cnl() renders State declarations"
    def test_cnl_statement_to_cnl_state_standalone(self):
        """State renders as simple operator:value."""
        stmt = CNLStatement(operator="State", value="Config_Saved")
        assert stmt.to_cnl() == "State:Config_Saved"

    # --- Serialization ---

    # Acceptance Criterion: "to_dict() includes all fields"
    def test_cnl_statement_to_dict_includes_all_keys(self):
        """to_dict() output has expected keys."""
        stmt = CNLStatement(
            operator="Action",
            value="Restart_Server",
            modifier="REQUIRES",
            target="State:Config_Saved",
            source_chunk_id="chunk-042",
            confidence=0.95,
        )
        d = stmt.to_dict()
        assert set(d.keys()) == {
            "operator", "value", "modifier", "target",
            "source_chunk_id", "confidence",
        }

    # Acceptance Criterion: "from_dict(to_dict()) roundtrip preserves all data"
    def test_cnl_statement_roundtrip_preserves_data(self):
        """Serialize then deserialize produces equal statement."""
        original = CNLStatement(
            operator="Action",
            value="Deploy_Application",
            modifier="REQUIRES",
            target="State:Database_Ready,State:Config_Valid",
            source_chunk_id="chunk-123",
            confidence=0.88,
        )
        restored = CNLStatement.from_dict(original.to_dict())
        assert restored == original

    # Acceptance Criterion: "to_dict() is JSON-compatible"
    def test_cnl_statement_to_dict_json_serializable(self):
        """to_dict() output can be JSON serialized."""
        import json
        stmt = CNLStatement(operator="State", value="Config_Saved")
        d = stmt.to_dict()
        json_str = json.dumps(d)
        assert isinstance(json_str, str)

    # --- is_valid Property ---

    # Acceptance Criterion: "is_valid returns True for valid statements"
    def test_cnl_statement_is_valid_true_for_valid_statement(self):
        """Valid statement with non-empty operator and value."""
        stmt = CNLStatement(operator="Action", value="Restart_Server")
        assert stmt.is_valid is True

    # Acceptance Criterion: "is_valid returns False for empty value"
    def test_cnl_statement_is_valid_false_for_empty_value(self):
        """Statement with empty value is invalid."""
        stmt = CNLStatement(operator="Action", value="")
        assert stmt.is_valid is False

    # Acceptance Criterion: "is_valid returns False for empty operator"
    def test_cnl_statement_is_valid_false_for_empty_operator(self):
        """Statement with empty operator is invalid."""
        stmt = CNLStatement(operator="", value="Restart_Server")
        assert stmt.is_valid is False

    # --- Edge Cases ---

    # Acceptance Criterion: "CNLStatement handles very long identifiers"
    def test_cnl_statement_long_identifier_allowed(self):
        """Long identifiers are stored as-is (truncation is synthesizer's job)."""
        long_value = "Very_Long_Identifier_With_Many_Words_In_It"
        stmt = CNLStatement(operator="Action", value=long_value)
        assert stmt.value == long_value

    # Acceptance Criterion: "CNLStatement preserves Unicode content"
    def test_cnl_statement_unicode_content(self):
        """Unicode in value is preserved through roundtrip."""
        stmt = CNLStatement(operator="State", value="Café_Système")
        roundtrip = CNLStatement.from_dict(stmt.to_dict())
        assert roundtrip.value == "Café_Système"

    # --- Error Paths ---

    # Acceptance Criterion: "from_dict() raises KeyError for missing operator"
    def test_cnl_statement_from_dict_missing_operator_raises_key_error(self):
        """Missing 'operator' key raises KeyError."""
        with pytest.raises(KeyError):
            CNLStatement.from_dict({"value": "Restart_Server"})

    # Acceptance Criterion: "from_dict() raises KeyError for missing value"
    def test_cnl_statement_from_dict_missing_value_raises_key_error(self):
        """Missing 'value' key raises KeyError."""
        with pytest.raises(KeyError):
            CNLStatement.from_dict({"operator": "Action"})

    # Acceptance Criterion: "from_dict() handles missing optional fields"
    def test_cnl_statement_from_dict_missing_optional_fields(self):
        """Optional fields are populated with defaults."""
        stmt = CNLStatement.from_dict({"operator": "Action", "value": "Test"})
        assert stmt.modifier is None
        assert stmt.target is None
        assert stmt.source_chunk_id is None
        assert stmt.confidence == 1.0


class TestSynthesisConfig:
    """Tests for the SynthesisConfig dataclass. (v0.2.3a)"""

    # Acceptance Criterion: "SynthesisConfig defaults match spec"
    def test_synthesis_config_defaults(self):
        """Default config has expected values."""
        config = SynthesisConfig()
        assert config.use_flow_operators is True
        assert config.include_standalone_states is True
        assert config.warn_on_empty_entities is True
        assert config.statement_separator == "; "
        assert config.max_identifier_length == 32

    # Acceptance Criterion: "SynthesisConfig accepts custom overrides"
    def test_synthesis_config_custom_overrides(self):
        """Custom values override defaults."""
        config = SynthesisConfig(
            use_flow_operators=False,
            statement_separator=" ; ",
            max_identifier_length=64,
        )
        assert config.use_flow_operators is False
        assert config.statement_separator == " ; "
        assert config.max_identifier_length == 64
        # Verify non-overridden defaults remain
        assert config.include_standalone_states is True


class TestOperatorType:
    """Tests for the OperatorType enum. (v0.2.3a)"""

    # Acceptance Criterion: "OperatorType enum includes all 14 operators"
    def test_operator_type_has_all_operators(self):
        """Enum contains expected operator values."""
        expected = {
            "ACTION", "STATE", "EXEC", "WARN", "REQUIRES",
            "VERIFY", "IF", "THEN", "ELSE", "SEQ", "REF", "META", "LOOP", "NOTE",
        }
        actual = {member.name for member in OperatorType}
        assert actual == expected

    # Acceptance Criterion: "OperatorType members have correct string values"
    def test_operator_type_string_values(self):
        """Enum string values match grammar spec."""
        assert OperatorType.ACTION.value == "Action"
        assert OperatorType.STATE.value == "State"
        assert OperatorType.EXEC.value == "EXEC"
        assert OperatorType.WARN.value == "WARN"
        assert OperatorType.REQUIRES.value == "REQUIRES"


class TestNamingValidators:
    """Tests for naming convention validators. (v0.2.3a)"""

    # Acceptance Criterion: "validate_identifier accepts PascalCase_With_Underscores"
    def test_validate_identifier_valid_cases(self):
        """Valid identifier patterns are accepted."""
        valid = [
            "Restart_Server",
            "Config_Saved",
            "Data_Loss",
            "Database_Active",
            "A",
            "Single_Letter_Words",
        ]
        for name in valid:
            assert validate_identifier(name) is True, f"Failed for {name}"

    # Acceptance Criterion: "validate_identifier rejects invalid patterns"
    def test_validate_identifier_invalid_cases(self):
        """Invalid identifier patterns are rejected."""
        invalid = [
            "restart_server",  # lowercase
            "ConfigSaved",  # missing underscore
            "Restart-Server",  # hyphen instead of underscore
            "_Restart_Server",  # leading underscore
            "restart_Server",  # starts lowercase
        ]
        for name in invalid:
            assert validate_identifier(name) is False, f"Should fail for {name}"

    # Acceptance Criterion: "validate_command accepts lowercase shell syntax"
    def test_validate_command_valid_cases(self):
        """Valid command patterns are accepted."""
        valid = [
            "systemctl restart app",
            "rsync -a /src /dst",
            "curl https://example.com",
            "s",
            "0restart",  # starts with digit
        ]
        for cmd in valid:
            assert validate_command(cmd) is True, f"Failed for {cmd}"

    # Acceptance Criterion: "validate_command rejects invalid patterns"
    def test_validate_command_invalid_cases(self):
        """Invalid command patterns are rejected."""
        invalid = [
            "Systemctl restart app",  # starts uppercase
            "",  # empty string
        ]
        for cmd in invalid:
            assert validate_command(cmd) is False, f"Should fail for {cmd}"

    # Acceptance Criterion: "validate_meta_key checks lowercase_with_underscores"
    def test_validate_meta_key_valid_cases(self):
        """Valid META key patterns are accepted."""
        valid = [
            "compatible_with",
            "version",
            "author",
            "release_date",
        ]
        for key in valid:
            assert validate_meta_key(key) is True, f"Failed for {key}"

    # Acceptance Criterion: "validate_meta_key rejects invalid patterns"
    def test_validate_meta_key_invalid_cases(self):
        """Invalid META key patterns are rejected."""
        invalid = [
            "Compatible_With",  # uppercase
            "version-key",  # hyphen
            "_version",  # leading underscore
        ]
        for key in invalid:
            assert validate_meta_key(key) is False, f"Should fail for {key}"


class TestLogging:
    """Tests for logger initialization. (v0.2.3a)"""

    # Acceptance Criterion: "Logger is initialized with __name__"
    def test_logger_initialized(self):
        """Module logger is present."""
        from src import synthesizer
        assert hasattr(synthesizer, "logger")
        assert synthesizer.logger.name == "src.synthesizer"
```

---

## Logging Requirements

| Level | When | Example Message |
|-------|------|-----------------|
| **INFO** | Module imported / logger initialized | `"synthesizer module loaded"` |
| **DEBUG** | CNLStatement created | `"CNLStatement created: op=%s, val=%s, conf=%f"` |
| **DEBUG** | Statement rendered to CNL | `"CNLStatement rendered: %s"` |
| **DEBUG** | Statement serialized | `"CNLStatement serialized to dict: op=%s"` |
| **DEBUG** | Statement deserialized | `"CNLStatement deserialized from dict: op=%s"` |
| **WARNING** | Identifier exceeds max length | `"Identifier truncated: %s (%d > %d chars)"` |
| **WARNING** | Validation failure | `"Invalid statement value: %s"` |

```python
import logging

logger = logging.getLogger(__name__)

# At module load:
logger.info("synthesizer module loaded")

# In CNLStatement.__init__():
logger.debug("CNLStatement created: op=%s, val=%s, conf=%f", self.operator, self.value, self.confidence)

# In CNLStatement.to_cnl():
cnl_str = self.to_cnl()
logger.debug("CNLStatement rendered: %s", cnl_str)

# In CNLStatement.to_dict():
logger.debug("CNLStatement serialized to dict: op=%s", self.operator)

# In CNLStatement.from_dict():
logger.debug("CNLStatement deserialized from dict: op=%s", data.get("operator"))

# When identifier exceeds threshold:
if len(identifier) > config.max_identifier_length:
    logger.warning("Identifier truncated: %s (%d > %d chars)", identifier, len(identifier), config.max_identifier_length)
```

---

## Acceptance Criteria

- [ ] `src/synthesizer.py` created with module docstring referencing v0.2.3a
- [ ] `OperatorType` enum defined with all 14 operators and correct string values
- [ ] `CNLStatement` dataclass defined with all 6 fields and full type hints
- [ ] `SynthesisConfig` dataclass defined with 5 fields and sensible defaults
- [ ] `to_cnl()` renders statements correctly (simple, REQUIRES, ->, WARN, State)
- [ ] `to_dict()` returns JSON-serializable dictionary with all fields
- [ ] `from_dict()` class method reconstructs CNLStatement from dictionary
- [ ] `from_dict()` raises `KeyError` when required fields are missing
- [ ] `__repr__()` returns readable summary including operator and value
- [ ] `is_valid` property returns True for valid statements, False for empty operator/value
- [ ] `validate_identifier()` enforces PascalCase_With_Underscores convention
- [ ] `validate_command()` enforces lowercase shell syntax convention
- [ ] `validate_meta_key()` enforces lowercase_with_underscores convention
- [ ] Logger initialized with `logging.getLogger(__name__)`
- [ ] `tests/test_synthesizer.py` created with ≥27 tests across all categories
- [ ] All tests pass: `python -m pytest tests/test_synthesizer.py -v`
- [ ] No `print()` statements in `src/synthesizer.py`
- [ ] All public methods have Google-style docstrings with Args/Returns/Raises sections

---

## Limitations & Constraints

1. **No Synthesis Logic Yet:** This sub-part only defines the data model for individual statements. The transformation from extracted entities to statement lists is v0.2.3b, and string rendering is v0.2.3c.
2. **No Operator Validation in Constructor:** CNLStatement accepts any string as operator. Validation against `OperatorType` enum is the synthesizer's responsibility (v0.2.3b).
3. **No Automatic Identifier Formatting:** The statement stores identifiers as-is. Truncation to `max_identifier_length` is deferred to the synthesizer (v0.2.3b).
4. **No Dependency Resolution:** While `modifier` and `target` fields support relationship expressions, resolving multiple dependencies or complex conditions is deferred to v0.2.3b–c.
5. **Confidence Score is Inherited Only:** The confidence field is populated by the extractor (v0.2.2). The synthesizer does not adjust it based on statement validity.

---

## Dependencies

**Must be completed before v0.2.3a:**
- v0.1.3c — Source Module Stubs (establishes `src/` package structure)
- v0.2.2a — Entity Data Model (defines `ExtractedEntities`, `Dependency` as inputs to synthesizer)
- v0.2.1a — Chunk Data Model (provides chunk IDs for traceability)

**No dependencies on:**
- v0.2.3b — CNL Statement Synthesis (consumes CNLStatement but does not influence its design)
- v0.2.3c — CNL String Rendering (consumes CNLStatement but does not influence its design)

---

## Outputs to Next Sub-Part

**For v0.2.3b — CNL Statement Synthesis:**
- `CNLStatement` dataclass is importable from `src.synthesizer`
- `SynthesisConfig` is importable from `src.synthesizer`
- `OperatorType` enum is importable from `src.synthesizer`
- Naming convention validators (`validate_identifier`, `validate_command`, `validate_meta_key`) are importable and working
- `to_cnl()` method is tested for all core operator types (Action, State, EXEC, WARN, REQUIRES)
- `to_dict()` and `from_dict()` serialization methods are tested and working
- Logger is initialized and ready for synthesis-level log messages

---

## Decision Log

| Decision | Rationale | Status |
|----------|-----------|--------|
| `CNLStatement` as separate dataclass from `ExtractedEntities` | Allows pipeline transformation (entities → statements → string) without conflating input and intermediate representations | ✅ Approved |
| `OperatorType` enum defined for all 14 operators | Forward compatibility: v0.2.3 only synthesizes core types (Action, State, EXEC, WARN, REQUIRES), but enum prevents runtime errors when expanded in future versions | ✅ Approved |
| Confidence field on `CNLStatement` | Enables downstream filtering by extraction quality without re-accessing the extractor; supports error reporting that correlates statements to source confidence | ✅ Approved |
| `SynthesisConfig` separate from `CNLSynthesizer` | Config can be serialized/logged independently; supports future config-file loading and swappable synthesis strategies | ✅ Approved |
| `to_cnl()` method instead of `__str__()` | Explicit method name signals "render to protocol string"; allows subclasses or wrappers to override formatting without breaking `__str__` expectations | ✅ Approved |
| `is_valid` as property, not method | Lightweight validity check; read-like semantics for a state query; consistent with Python conventions (e.g., `str.isalnum()`) | ✅ Approved |
| Naming validators as module-level functions | Reusable across synthesizer, renderer, and validation stages; easier to test and extend than methods on the dataclass | ✅ Approved |
| Defer operator validation to synthesizer | Keeps v0.2.3a data model free of circular dependencies and enum coupling; allows synthesizer to manage strict vs. lenient modes | ✅ Approved |
