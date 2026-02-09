# v0.2.2a — Entity Data Model & Interfaces

<aside>

**Version:** v0.2.2a

**Parent:** v0.2.2 — Entity Extraction

**Status:** ⬜ Not Started

**Duration:** 20–30 minutes

**Deliverable:** `ExtractedEntities` dataclass, `EntityType` enum, `Dependency` model, type definitions, and comprehensive unit tests in `src/extractor.py` and `tests/test_extractor.py`

</aside>

---

## Objective

Define the foundational data structures that represent the output of entity extraction. These structures model the five semantic entity types identified by the Haiku Protocol grammar (Actions, States, Commands, Warnings, Dependencies) and serve as the contract between the extractor (v0.2.2) and the CNL synthesizer (v0.2.3). The data model must support serialization to JSON, validation of entity naming conventions, and round-trip fidelity.

---

## User Story

> As the CNL synthesizer developer, I want a well-typed `ExtractedEntities` container with validated entity names and a consistent serialization format so that I can consume extraction output without parsing raw LLM responses or guessing field names.

---

## Data Model Design

### Entity Types

The following entity types correspond to operators in the Haiku Protocol grammar (`research/haiku_grammar.bnf`):

```python
from enum import Enum

class EntityType(Enum):
    """Semantic entity types in the Haiku Protocol grammar.

    Each type maps to a specific operator or operator class defined
    in the BNF grammar and STYLE_GUIDE.md.

    Attributes:
        ACTION: Procedural step (maps to OP-001 Action:)
        STATE: Precondition or postcondition (maps to OP-002 State:)
        COMMAND: Literal CLI command (maps to OP-004 EXEC:)
        WARNING: Risk/consequence declaration (maps to OP-006 WARN:)
        DEPENDENCY: Relationship between entities (maps to OP-003 REQUIRES)
    """
    ACTION = "action"
    STATE = "state"
    COMMAND = "command"
    WARNING = "warning"
    DEPENDENCY = "dependency"
```

### Dependency Model

```python
@dataclass
class Dependency:
    """A directed relationship between two entities.

    Models the REQUIRES operator semantics: an action requires
    a state to be true before it can execute.

    Attributes:
        action: The action that has the dependency.
            Format: PascalCase_With_Underscores.
        requires: The state that must be satisfied.
            Format: PascalCase_With_Underscores.
        condition: Optional additional condition string.
            Example: "if database is running"
        target: Optional target action if this is an IF/THEN.
            Example: "Rollback" in "IF:Fail THEN:Rollback"
    """
    action: str
    requires: str
    condition: Optional[str] = None
    target: Optional[str] = None

    def to_dict(self) -> dict:
        """Serialize to JSON-compatible dictionary."""
        result = {"action": self.action, "requires": self.requires}
        if self.condition:
            result["condition"] = self.condition
        if self.target:
            result["target"] = self.target
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Dependency":
        """Deserialize from dictionary.

        Args:
            data: Dictionary with 'action' and 'requires' keys.

        Returns:
            Dependency instance.

        Raises:
            KeyError: If 'action' or 'requires' missing.
        """
        return cls(
            action=data["action"],
            requires=data["requires"],
            condition=data.get("condition"),
            target=data.get("target"),
        )
```

### ExtractedEntities Container

```python
@dataclass
class ExtractedEntities:
    """Container for all entities extracted from a single document chunk.

    This is the primary output of the EntityExtractor and the primary
    input to the CNL Synthesizer. Each field corresponds to one or more
    operators in the Haiku Protocol grammar.

    Attributes:
        actions: Procedural steps identified in the text.
            Format: PascalCase_With_Underscores (e.g., "Restart_Server").
        states: Preconditions or postconditions.
            Format: PascalCase_With_Underscores (e.g., "Config_Saved").
        commands: Literal CLI commands or code snippets.
            Format: lowercase shell syntax (e.g., "systemctl restart app").
        warnings: Risk conditions or failure scenarios.
            Format: PascalCase_With_Underscores (e.g., "Data_Loss").
        dependencies: Relationships between entities.
        raw_response: The raw LLM response string, retained for debugging.
        chunk_id: ID of the source chunk (links back to chunker output).
        confidence: 0.0–1.0 confidence score for the extraction quality.
    """
    actions: List[str] = field(default_factory=list)
    states: List[str] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    dependencies: List[Dependency] = field(default_factory=list)
    raw_response: Optional[str] = None
    chunk_id: Optional[str] = None
    confidence: float = 0.0

    @property
    def total_entities(self) -> int:
        """Total count of all extracted entities."""
        return (
            len(self.actions) + len(self.states) +
            len(self.commands) + len(self.warnings) +
            len(self.dependencies)
        )

    @property
    def is_empty(self) -> bool:
        """True if no entities were extracted."""
        return self.total_entities == 0

    def to_dict(self) -> dict:
        """Serialize to JSON-compatible dictionary.

        Returns:
            Dictionary with all fields. Dependencies are serialized
            as list of dicts. raw_response is excluded to keep
            output compact (use to_dict_full() to include it).
        """
        return {
            "actions": self.actions,
            "states": self.states,
            "commands": self.commands,
            "warnings": self.warnings,
            "dependencies": [d.to_dict() for d in self.dependencies],
            "chunk_id": self.chunk_id,
            "confidence": self.confidence,
            "total_entities": self.total_entities,
        }

    def to_dict_full(self) -> dict:
        """Serialize including raw_response for debugging."""
        result = self.to_dict()
        result["raw_response"] = self.raw_response
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "ExtractedEntities":
        """Deserialize from dictionary.

        Args:
            data: Dictionary with entity lists.

        Returns:
            ExtractedEntities instance.
        """
        deps = [Dependency.from_dict(d) for d in data.get("dependencies", [])]
        return cls(
            actions=data.get("actions", []),
            states=data.get("states", []),
            commands=data.get("commands", []),
            warnings=data.get("warnings", []),
            dependencies=deps,
            raw_response=data.get("raw_response"),
            chunk_id=data.get("chunk_id"),
            confidence=data.get("confidence", 0.0),
        )

    def __repr__(self) -> str:
        return (
            f"ExtractedEntities(actions={len(self.actions)}, "
            f"states={len(self.states)}, commands={len(self.commands)}, "
            f"warnings={len(self.warnings)}, deps={len(self.dependencies)})"
        )
```

### Naming Convention Validator

```python
import re

# From STYLE_GUIDE.md: PascalCase_With_Underscores
IDENTIFIER_PATTERN = re.compile(r'^[A-Z][A-Za-z0-9]*(_[A-Z][A-Za-z0-9]*)*$')

# Commands are lowercase shell syntax
COMMAND_PATTERN = re.compile(r'^[a-z]')


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
        True if command starts with lowercase letter.
    """
    return bool(command and COMMAND_PATTERN.match(command))
```

---

## File Structure

```
src/
└── extractor.py      # ExtractedEntities, Dependency, EntityType, validators + logger

tests/
└── test_extractor.py  # Unit tests for data model
```

---

## Implementation Workflow

```
┌────────────────────────────────────────────────────────────────┐
│              v0.2.2a IMPLEMENTATION FLOW                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  STEP 1: Create src/extractor.py skeleton                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Module docstring + logger declaration                  │  │
│  │ • EntityType enum                                        │  │
│  │ • Dependency dataclass with to_dict/from_dict            │  │
│  │ • ExtractedEntities dataclass with all fields            │  │
│  │ • Properties: total_entities, is_empty                   │  │
│  │ • Serialization: to_dict, to_dict_full, from_dict        │  │
│  │ • Naming validators: validate_identifier, validate_cmd   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│  STEP 2: Create tests/test_extractor.py                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Happy path: construction, fields, defaults, repr       │  │
│  │ • Serialization: to_dict roundtrip, from_dict roundtrip  │  │
│  │ • Properties: total_entities, is_empty                   │  │
│  │ • Validators: identifier format, command format          │  │
│  │ • Dependency: construction, serialization, error paths   │  │
│  │ • Edge cases: empty lists, Unicode, special chars       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│  STEP 3: Run tests + verify                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ $ python -m pytest tests/test_extractor.py -v            │  │
│  │ • All tests green                                        │  │
│  │ • No import errors                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Unit Testing Requirements

### Test Categories and Minimums

| Category | Tests | Description |
|----------|-------|-------------|
| **Happy Path** | 5 | Construction with all fields, default values, repr output, EntityType values, total_entities count |
| **Serialization** | 6 | `to_dict()` output, `to_dict_full()` includes raw_response, `from_dict()` roundtrip, missing optional fields, JSON compat, Dependency serialization |
| **Properties** | 3 | `total_entities` sums correctly, `is_empty` for empty/non-empty, confidence range |
| **Validators** | 8 | Valid identifiers (6 positive/negative), valid commands (2 positive/negative) |
| **Dependency** | 4 | Construction, serialization, missing required field raises KeyError, optional fields |
| **Edge Cases** | 4 | Empty entity lists, single entity per type, very long action name, special chars in commands |
| **Logging** | 1 | Logger initialized with `__name__` |

### Example Test Code

```python
import pytest
from src.extractor import (
    ExtractedEntities, Dependency, EntityType,
    validate_identifier, validate_command,
)


class TestExtractedEntities:
    """Tests for ExtractedEntities dataclass. (v0.2.2a)"""

    def test_init_all_fields(self):
        """ExtractedEntities can be created with all fields populated."""
        dep = Dependency(action="Restart", requires="Config_Saved")
        entities = ExtractedEntities(
            actions=["Restart_Server"],
            states=["Config_Saved"],
            commands=["systemctl restart"],
            warnings=["Data_Loss"],
            dependencies=[dep],
            raw_response='{"actions": [...]}',
            chunk_id="chunk-001",
            confidence=0.95,
        )
        assert entities.actions == ["Restart_Server"]
        assert entities.chunk_id == "chunk-001"
        assert entities.confidence == 0.95

    def test_defaults_empty_lists(self):
        """Default values are empty lists and None/0.0."""
        entities = ExtractedEntities()
        assert entities.actions == []
        assert entities.states == []
        assert entities.commands == []
        assert entities.warnings == []
        assert entities.dependencies == []
        assert entities.raw_response is None
        assert entities.chunk_id is None
        assert entities.confidence == 0.0

    def test_total_entities_sums_all_types(self):
        """total_entities counts across all entity types."""
        entities = ExtractedEntities(
            actions=["A", "B"],
            states=["S"],
            commands=["cmd1", "cmd2", "cmd3"],
            warnings=[],
            dependencies=[Dependency(action="A", requires="S")],
        )
        assert entities.total_entities == 7  # 2+1+3+0+1

    def test_is_empty_true_when_no_entities(self):
        """is_empty returns True for empty container."""
        assert ExtractedEntities().is_empty is True

    def test_is_empty_false_when_has_entities(self):
        """is_empty returns False when any entities present."""
        entities = ExtractedEntities(actions=["A"])
        assert entities.is_empty is False

    def test_to_dict_roundtrip(self):
        """Serialize then deserialize produces equal entities."""
        dep = Dependency(action="Deploy", requires="Tests_Passing")
        original = ExtractedEntities(
            actions=["Deploy_App"],
            states=["Tests_Passing"],
            commands=["docker push"],
            warnings=["Downtime_Risk"],
            dependencies=[dep],
            chunk_id="chunk-005",
            confidence=0.88,
        )
        restored = ExtractedEntities.from_dict(original.to_dict())
        assert restored.actions == original.actions
        assert restored.states == original.states
        assert restored.commands == original.commands
        assert restored.chunk_id == original.chunk_id

    def test_to_dict_excludes_raw_response(self):
        """to_dict() omits raw_response for compact output."""
        entities = ExtractedEntities(raw_response="long string")
        d = entities.to_dict()
        assert "raw_response" not in d

    def test_to_dict_full_includes_raw_response(self):
        """to_dict_full() includes raw_response."""
        entities = ExtractedEntities(raw_response="long string")
        d = entities.to_dict_full()
        assert d["raw_response"] == "long string"


class TestDependency:
    """Tests for Dependency dataclass. (v0.2.2a)"""

    def test_dependency_init(self):
        """Dependency created with action and requires."""
        dep = Dependency(action="Restart", requires="Config_Saved")
        assert dep.action == "Restart"
        assert dep.requires == "Config_Saved"
        assert dep.condition is None

    def test_dependency_roundtrip(self):
        """Serialize/deserialize roundtrip preserves data."""
        dep = Dependency(
            action="Deploy", requires="Tests_Pass",
            condition="on staging", target="Verify"
        )
        restored = Dependency.from_dict(dep.to_dict())
        assert restored == dep

    def test_dependency_from_dict_missing_action_raises(self):
        """Missing 'action' key raises KeyError."""
        with pytest.raises(KeyError):
            Dependency.from_dict({"requires": "State"})


class TestValidators:
    """Tests for naming convention validators. (v0.2.2a)"""

    @pytest.mark.parametrize("name,expected", [
        ("Restart_Server", True),
        ("Config_Saved", True),
        ("Deploy", True),
        ("A", True),
        ("restart_server", False),  # lowercase start
        ("ConfigValid", False),     # missing underscore
        ("", False),                # empty
        ("123_Bad", False),         # starts with digit
    ])
    def test_validate_identifier(self, name, expected):
        """Identifier validation matches Haiku Protocol style guide."""
        assert validate_identifier(name) == expected

    @pytest.mark.parametrize("cmd,expected", [
        ("systemctl restart", True),
        ("docker build -t app .", True),
        ("UPPERCASE_CMD", False),
        ("", False),
    ])
    def test_validate_command(self, cmd, expected):
        """Command validation matches lowercase shell convention."""
        assert validate_command(cmd) == expected
```

---

## Logging Requirements

| Level | When | Example Message |
|-------|------|-----------------|
| **INFO** | Module imported | `"extractor module loaded"` |
| **DEBUG** | Entities serialized | `"ExtractedEntities serialized: %d total entities"` |
| **DEBUG** | Entities deserialized | `"ExtractedEntities deserialized: chunk_id=%s"` |
| **WARNING** | Invalid identifier format | `"Invalid identifier format: %r (expected PascalCase_With_Underscores)"` |

---

## Acceptance Criteria

- [ ] `src/extractor.py` created with module docstring referencing v0.2.2a
- [ ] `EntityType` enum with 5 values matching grammar operators
- [ ] `Dependency` dataclass with `action`, `requires`, optional `condition`/`target`
- [ ] `ExtractedEntities` dataclass with 8 fields and full type hints
- [ ] `total_entities` property returns sum across all entity types
- [ ] `is_empty` property returns True when no entities extracted
- [ ] `to_dict()` excludes `raw_response` for compact output
- [ ] `to_dict_full()` includes `raw_response` for debugging
- [ ] `from_dict()` class method reconstructs from dictionary
- [ ] `validate_identifier()` validates PascalCase_With_Underscores format
- [ ] `validate_command()` validates lowercase shell syntax
- [ ] Logger initialized with `logging.getLogger(__name__)`
- [ ] ≥31 tests across all categories pass
- [ ] No `print()` statements in source code

---

## Limitations & Constraints

1. **No LLM Integration Yet:** This sub-part only defines output structures. LLM calling is v0.2.2c.
2. **No Prompt Templates:** Prompt design is v0.2.2b.
3. **Validation Is Advisory:** `validate_identifier()` returns bool but does not enforce — the extractor may produce non-standard names from LLM output, and normalization is the caller's responsibility.
4. **Confidence Score Unpopulated:** The `confidence` field is defined but set to `0.0` by default. Population logic is deferred to v0.2.2c.

---

## Dependencies

**Must be completed before v0.2.2a:**
- v0.2.1a — Chunk Data Model (establishes the `Chunk` that feeds into extraction)
- v0.1.3c — Source Module Stubs (establishes `src/` package structure)

---

## Outputs to Next Sub-Parts

**For v0.2.2b — Prompt Engineering:**
- Entity type names from `EntityType` enum inform prompt design
- `Dependency` model structure dictates JSON output schema for LLM prompt

**For v0.2.2c — EntityExtractor Core:**
- `ExtractedEntities` is the return type of `extract()`
- `Dependency.from_dict()` is used to parse LLM dependency arrays

**For v0.2.3 — CNL Synthesis:**
- `ExtractedEntities.to_dict()` provides the input format for synthesizer

---

## Decision Log

| Decision | Rationale | Status |
|----------|-----------|--------|
| Add `chunk_id` to ExtractedEntities | Links extraction output back to source chunk for traceability | ✅ Approved |
| Add `confidence` field | Enables downstream filtering of low-confidence extractions | ✅ Approved |
| Separate `to_dict()` and `to_dict_full()` | Raw LLM response can be huge; compact output should omit it | ✅ Approved |
| Use `Dependency` dataclass over plain dict | Provides type safety, serialization, and validation | ✅ Approved |
| `validate_identifier()` returns bool, does not raise | Advisory validation allows the pipeline to proceed with warnings | ✅ Approved |
| `EntityType` enum values are lowercase strings | Matches JSON output convention; enum provides type safety in Python | ✅ Approved |
