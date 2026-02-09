# v0.2.2b — Extraction Prompt Engineering

<aside>

**Version:** v0.2.2b

**Parent:** v0.2.2 — Entity Extraction

**Status:** ⬜ Not Started

**Duration:** 25–35 minutes

**Deliverable:** Versioned prompt templates, few-shot examples, output schema definition, and prompt validation tests

</aside>

---

## Objective

Design and implement the LLM prompt templates that drive entity extraction. The prompt must reliably guide GPT-4 to output structured JSON containing Actions, States, Commands, Warnings, and Dependencies from technical documentation chunks. This sub-part establishes prompt versioning, few-shot examples, output schema enforcement, and test infrastructure for measuring prompt reliability.

The prompt is the single most critical component of the extraction pipeline — its design directly determines extraction accuracy and the quality of downstream CNL synthesis.

---

## User Stories

> As a pipeline developer, I want versioned prompt templates so that I can A/B test different prompt formulations and track which version produces the best extraction accuracy.

> As an LLM engineer, I want few-shot examples embedded in the prompt so that the model has concrete references for the expected output format and naming conventions.

---

## Prompt Architecture

### Prompt Components

```
┌────────────────────────────────────────────────────────────────┐
│              EXTRACTION PROMPT STRUCTURE                        │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. SYSTEM CONTEXT                                        │  │
│  │    Role assignment + task definition                      │  │
│  │    "You are a semantic entity extractor for the           │  │
│  │     Haiku Protocol..."                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 2. ENTITY TYPE DEFINITIONS                               │  │
│  │    What to extract + naming conventions                   │  │
│  │    ACTION: PascalCase_With_Underscores                    │  │
│  │    STATE:  PascalCase_With_Underscores                    │  │
│  │    COMMAND: exact shell syntax                            │  │
│  │    WARN:  PascalCase cause→effect                         │  │
│  │    DEPENDENCY: action REQUIRES state                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 3. FEW-SHOT EXAMPLES                                     │  │
│  │    2–3 input→output pairs from real documentation        │  │
│  │    Demonstrate expected format and edge cases             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 4. OUTPUT SCHEMA                                         │  │
│  │    JSON structure definition with field descriptions      │  │
│  │    Enforce return format: JSON only, no explanation       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 5. INPUT TEXT                                            │  │
│  │    The chunk content to analyze (injected at runtime)     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Prompt Template Implementation

### Prompt Registry

```python
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class PromptVersion:
    """A versioned extraction prompt template.

    Attributes:
        version: Semantic version string (e.g., "1.0.0").
        name: Human-readable prompt name.
        system_context: System role and task description.
        entity_definitions: Entity type definitions and naming rules.
        few_shot_examples: List of (input, output) example pairs.
        output_schema: Expected JSON output format.
        input_template: Template with {text} placeholder for chunk content.
        notes: Design notes or changelog for this version.
    """
    version: str
    name: str
    system_context: str
    entity_definitions: str
    few_shot_examples: List[Dict[str, str]]
    output_schema: str
    input_template: str
    notes: str = ""

    def render(self, text: str) -> str:
        """Render the full prompt with input text injected.

        Args:
            text: Document chunk content to analyze.

        Returns:
            Complete prompt string ready for LLM invocation.
        """
        ...

    def render_system_message(self) -> str:
        """Render the system message (for chat-based APIs).

        Returns:
            System context + entity definitions + examples + schema.
        """
        ...

    def render_user_message(self, text: str) -> str:
        """Render the user message with input text.

        Args:
            text: Document chunk content.

        Returns:
            User message with text injected.
        """
        ...


class PromptRegistry:
    """Registry of versioned extraction prompts.

    Manages multiple prompt versions and provides the active prompt
    for extraction. Supports A/B testing by allowing runtime selection.

    Attributes:
        prompts: Dictionary mapping version strings to PromptVersion objects.
        active_version: The currently selected prompt version string.
    """

    def __init__(self) -> None:
        self.prompts: Dict[str, PromptVersion] = {}
        self.active_version: str = ""

    def register(self, prompt: PromptVersion) -> None:
        """Register a prompt version.

        Args:
            prompt: PromptVersion to register.

        Raises:
            ValueError: If version string already registered.
        """
        ...

    def get_active(self) -> PromptVersion:
        """Get the currently active prompt version.

        Returns:
            Active PromptVersion.

        Raises:
            RuntimeError: If no active version set.
        """
        ...

    def set_active(self, version: str) -> None:
        """Set the active prompt version.

        Args:
            version: Version string to activate.

        Raises:
            KeyError: If version not registered.
        """
        ...

    def list_versions(self) -> List[str]:
        """List all registered version strings."""
        ...
```

---

### Prompt v1.0.0 — Baseline

```python
EXTRACTION_PROMPT_V1 = PromptVersion(
    version="1.0.0",
    name="Baseline Extraction",
    system_context="""You are a semantic entity extractor for the Haiku Protocol project.
Your task is to analyze technical documentation and extract structured entities
that will be compressed into a Controlled Natural Language (CNL) format.

You must identify:
- Procedural steps the user must take (ACTIONS)
- System conditions or prerequisites (STATES)
- Literal commands the user must run (COMMANDS)
- Risk conditions or consequences (WARNINGS)
- Relationships between actions and states (DEPENDENCIES)""",

    entity_definitions="""ENTITY TYPE DEFINITIONS AND NAMING CONVENTIONS:

1. ACTIONS — User-initiated procedural steps
   Format: PascalCase_With_Underscores (verb + noun)
   Examples: Restart_Server, Deploy_Application, Backup_Database
   Rules: Must start with a verb. Use underscores to separate words.

2. STATES — System conditions, prerequisites, or postconditions
   Format: PascalCase_With_Underscores (adjective/noun + noun)
   Examples: Config_Saved, DB_Online, Service_Running
   Rules: Describe a testable condition. Use underscores.

3. COMMANDS — Literal CLI commands or code snippets
   Format: Exact shell syntax, lowercase
   Examples: systemctl restart app-server, docker build -t myapp .
   Rules: Preserve the exact command as written. Do not summarize.

4. WARNINGS — Risk conditions or failure consequences
   Format: PascalCase_With_Underscores
   Examples: Data_Loss, Service_Downtime, Config_Corruption
   Rules: Describe the negative outcome, not the cause.

5. DEPENDENCIES — Relationships showing what requires what
   Format: {"action": "Action_Name", "requires": "State_Name"}
   Rules: An action REQUIRES a state to be true before execution.""",

    few_shot_examples=[
        {
            "input": """To restart the application server, you must first ensure that
all configuration changes have been saved. This prevents any
loss of settings during the reboot process.

Steps:
1. Navigate to the settings panel and click "Save Configuration"
2. Wait for the confirmation message
3. Run the command: systemctl restart app-server

Warning: If you skip step 1, your recent changes may be lost.""",

            "output": """{
    "actions": ["Save_Configuration", "Restart_Server"],
    "states": ["Config_Saved", "Confirmation_Received"],
    "commands": ["systemctl restart app-server"],
    "warnings": ["Data_Loss"],
    "dependencies": [
        {"action": "Restart_Server", "requires": "Config_Saved"}
    ]
}"""
        },
        {
            "input": """Before deploying to production, verify that all tests pass
and the staging environment is healthy. Run the deployment
script and monitor the logs for errors.

$ docker push registry.io/myapp:latest
$ kubectl apply -f deploy.yaml
$ kubectl rollout status deployment/myapp

If deployment fails, immediately rollback:
$ kubectl rollout undo deployment/myapp""",

            "output": """{
    "actions": ["Verify_Tests", "Deploy_Production", "Monitor_Logs", "Rollback_Deployment"],
    "states": ["Tests_Passing", "Staging_Healthy"],
    "commands": [
        "docker push registry.io/myapp:latest",
        "kubectl apply -f deploy.yaml",
        "kubectl rollout status deployment/myapp",
        "kubectl rollout undo deployment/myapp"
    ],
    "warnings": ["Deployment_Failure"],
    "dependencies": [
        {"action": "Deploy_Production", "requires": "Tests_Passing"},
        {"action": "Deploy_Production", "requires": "Staging_Healthy"}
    ]
}"""
        },
    ],

    output_schema="""{
    "actions": ["Action_Name_1", "Action_Name_2"],
    "states": ["State_Name_1", "State_Name_2"],
    "commands": ["exact command 1", "exact command 2"],
    "warnings": ["Warning_Condition_1"],
    "dependencies": [
        {"action": "Action_Name", "requires": "State_Name"}
    ]
}

RULES:
- Return ONLY valid JSON. No explanation, no markdown, no preamble.
- Use PascalCase_With_Underscores for action, state, and warning names.
- Preserve exact command syntax (lowercase, with flags and arguments).
- Return empty arrays [] if no entities of that type are found.
- Each action name must start with a verb.
- Each state name must describe a testable condition.
- Dependencies link an action to a required state.""",

    input_template="""TEXT TO ANALYZE:
---
{text}
---

Extract all semantic entities from the above text. Return JSON only.""",

    notes="Baseline prompt. Two few-shot examples covering procedural docs and deployment runbooks.",
)
```

---

## Output Schema Validation

```python
import json
from typing import Any


REQUIRED_KEYS = {"actions", "states", "commands", "warnings", "dependencies"}


def validate_extraction_output(raw_json: str) -> tuple[bool, dict, list[str]]:
    """Validate that LLM output conforms to expected schema.

    Args:
        raw_json: Raw JSON string from LLM response.

    Returns:
        Tuple of (is_valid, parsed_dict, list_of_errors).
        If is_valid is False, parsed_dict may be partial/empty.
    """
    errors = []

    # Parse JSON
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        return False, {}, [f"Invalid JSON: {e}"]

    if not isinstance(data, dict):
        return False, {}, ["Response is not a JSON object"]

    # Check required keys
    missing = REQUIRED_KEYS - set(data.keys())
    if missing:
        errors.append(f"Missing keys: {missing}")

    # Validate types
    for key in ["actions", "states", "commands", "warnings"]:
        val = data.get(key)
        if val is not None and not isinstance(val, list):
            errors.append(f"'{key}' must be a list, got {type(val).__name__}")
        elif val is not None:
            for item in val:
                if not isinstance(item, str):
                    errors.append(f"Items in '{key}' must be strings, got {type(item).__name__}")

    # Validate dependencies
    deps = data.get("dependencies")
    if deps is not None:
        if not isinstance(deps, list):
            errors.append(f"'dependencies' must be a list, got {type(deps).__name__}")
        else:
            for i, dep in enumerate(deps):
                if not isinstance(dep, dict):
                    errors.append(f"dependencies[{i}] must be a dict")
                elif "action" not in dep or "requires" not in dep:
                    errors.append(f"dependencies[{i}] missing 'action' or 'requires'")

    is_valid = len(errors) == 0
    return is_valid, data if isinstance(data, dict) else {}, errors
```

---

## Unit Testing Requirements

### Test Categories and Minimums

| Category | Tests | Description |
|----------|-------|-------------|
| **Prompt Rendering** | 5 | `render()` includes all sections, `render_system_message()` complete, `render_user_message()` injects text, few-shot examples included, no placeholder artifacts |
| **Registry** | 5 | Register prompt, get active, set active, list versions, duplicate version raises ValueError |
| **Schema Validation** | 8 | Valid JSON passes, missing keys detected, wrong types flagged, invalid JSON caught, empty object, valid dependencies, malformed dependencies, mixed valid/invalid |
| **Few-Shot Examples** | 3 | Examples are valid JSON, examples follow naming conventions, examples have all required keys |
| **Edge Cases** | 3 | Empty text input, very long text input, text with special characters |
| **Template** | 2 | `{text}` placeholder is present, no other unresolved placeholders |

### Example Test Code

```python
import json
import pytest
from src.extractor import (
    PromptVersion, PromptRegistry, EXTRACTION_PROMPT_V1,
    validate_extraction_output,
)


class TestPromptVersion:
    """Tests for PromptVersion and rendering. (v0.2.2b)"""

    def test_render_includes_input_text(self):
        """Rendered prompt contains the input text."""
        prompt = EXTRACTION_PROMPT_V1
        rendered = prompt.render("Test document content")
        assert "Test document content" in rendered

    def test_render_includes_few_shot_examples(self):
        """Rendered prompt includes few-shot example output."""
        prompt = EXTRACTION_PROMPT_V1
        rendered = prompt.render("anything")
        assert "Restart_Server" in rendered
        assert "systemctl restart app-server" in rendered

    def test_render_includes_entity_definitions(self):
        """Rendered prompt includes entity type definitions."""
        prompt = EXTRACTION_PROMPT_V1
        rendered = prompt.render("anything")
        assert "PascalCase_With_Underscores" in rendered

    def test_render_no_unresolved_placeholders(self):
        """Rendered prompt has no remaining {placeholder} markers."""
        prompt = EXTRACTION_PROMPT_V1
        rendered = prompt.render("Some text")
        # Only check for common placeholder patterns, not JSON braces
        assert "{text}" not in rendered


class TestPromptRegistry:
    """Tests for PromptRegistry. (v0.2.2b)"""

    def test_register_and_retrieve(self):
        """Registered prompt can be retrieved by version."""
        registry = PromptRegistry()
        registry.register(EXTRACTION_PROMPT_V1)
        registry.set_active("1.0.0")
        assert registry.get_active().version == "1.0.0"

    def test_duplicate_version_raises(self):
        """Registering same version twice raises ValueError."""
        registry = PromptRegistry()
        registry.register(EXTRACTION_PROMPT_V1)
        with pytest.raises(ValueError):
            registry.register(EXTRACTION_PROMPT_V1)


class TestSchemaValidation:
    """Tests for extraction output validation. (v0.2.2b)"""

    def test_valid_output_passes(self):
        """Well-formed JSON with all keys passes validation."""
        valid = json.dumps({
            "actions": ["Restart_Server"],
            "states": ["Config_Saved"],
            "commands": ["systemctl restart"],
            "warnings": [],
            "dependencies": [
                {"action": "Restart", "requires": "Config_Saved"}
            ]
        })
        is_valid, data, errors = validate_extraction_output(valid)
        assert is_valid is True
        assert len(errors) == 0

    def test_invalid_json_fails(self):
        """Malformed JSON string fails validation."""
        is_valid, _, errors = validate_extraction_output("not json {")
        assert is_valid is False
        assert any("Invalid JSON" in e for e in errors)

    def test_missing_keys_detected(self):
        """Missing required keys are reported."""
        partial = json.dumps({"actions": [], "states": []})
        is_valid, _, errors = validate_extraction_output(partial)
        assert is_valid is False
        assert any("Missing keys" in e for e in errors)

    def test_few_shot_examples_are_valid_json(self):
        """All few-shot example outputs are valid JSON."""
        for example in EXTRACTION_PROMPT_V1.few_shot_examples:
            data = json.loads(example["output"])
            assert isinstance(data, dict)
            assert "actions" in data

    def test_few_shot_examples_follow_naming(self):
        """Few-shot example entities follow naming conventions."""
        from src.extractor import validate_identifier
        for example in EXTRACTION_PROMPT_V1.few_shot_examples:
            data = json.loads(example["output"])
            for action in data["actions"]:
                assert validate_identifier(action), f"Bad action: {action}"
            for state in data["states"]:
                assert validate_identifier(state), f"Bad state: {state}"
```

---

## Logging Requirements

| Level | When | Example Message |
|-------|------|-----------------|
| **INFO** | Prompt registered | `"Prompt registered: version=%s, name=%s"` |
| **INFO** | Active prompt set | `"Active prompt set to version %s"` |
| **DEBUG** | Prompt rendered | `"Prompt rendered: %d chars, version=%s"` |
| **WARNING** | Schema validation failed | `"Extraction output validation failed: %s"` |
| **DEBUG** | Schema validation passed | `"Extraction output validated: %d entities"` |

---

## Acceptance Criteria

- [ ] `PromptVersion` dataclass defined with all template components
- [ ] `render()` produces complete prompt with text injected
- [ ] `render_system_message()` and `render_user_message()` support chat API format
- [ ] `PromptRegistry` manages multiple versioned prompts
- [ ] `EXTRACTION_PROMPT_V1` baseline prompt defined with 2 few-shot examples
- [ ] Few-shot examples are valid JSON matching the output schema
- [ ] Few-shot examples follow PascalCase_With_Underscores naming convention
- [ ] `validate_extraction_output()` checks JSON validity, required keys, and types
- [ ] Output schema defines all 5 entity types with clear format requirements
- [ ] ≥26 tests across all categories pass
- [ ] Prompt contains no unresolved `{placeholder}` markers after rendering
- [ ] No `print()` statements in source code

---

## Dependencies

**Must be completed before v0.2.2b:**
- v0.2.2a — Entity Data Model (defines entity type names and structures)

---

## Outputs to Next Sub-Part

**For v0.2.2c — EntityExtractor Core:**
- `PromptRegistry` provides the active prompt
- `EXTRACTION_PROMPT_V1.render()` produces the prompt string for LLM calls
- `validate_extraction_output()` validates LLM responses

---

## Decision Log

| Decision | Rationale | Status |
|----------|-----------|--------|
| Version prompts with semantic versioning | Enables A/B testing and regression tracking; prompts are the most-tuned component | ✅ Approved |
| Two few-shot examples (procedural + deployment) | Covers the two most common documentation patterns; more examples increase token cost | ✅ Approved |
| Separate system and user messages | LangChain `ChatOpenAI` uses chat format; system context is reused across calls | ✅ Approved |
| Schema validation as standalone function | Can be used in tests, monitoring, and production error handling | ✅ Approved |
| JSON-only output rule in prompt | Prevents LLM explanatory text from breaking JSON parsing | ✅ Approved |
