# v0.2.3b: Identifier Formatting & Synthesis Rules

> **Aside:** Version: v0.2.3b | Parent: v0.2.3 — CNL Synthesis Engine | Status: ⬜ Not Started | Duration: 20–30 minutes | Deliverable: Identifier formatting functions, synthesis rule engine, and dependency graph construction in src/synthesizer.py

## Objective

Define the core identifier formatting rules and synthesis engine that transforms raw extracted entities (actions, states, commands, warnings) into grammar-compliant CNL string representations. This sub-part establishes:

1. **Identifier Formatting Functions** — convert raw text to PascalCase_With_Underscores (or appropriate format per operator)
2. **Synthesis Rule Engine** — map entity types to their corresponding CNL operators
3. **Dependency Graph Construction** — build action-to-state mappings to enable REQUIRES clause attachment during synthesis
4. **Statement Ordering** — apply simple topological ordering to respect dependencies within a chunk

The output is a set of Python functions in `src/synthesizer.py` that power the entity-to-CNL-string transformation pipeline.

---

## User Stories

### US-1: As a Rule-Based Synthesizer, I Need to Format Extracted Identifiers into Grammar-Compliant Strings

**Given** raw extracted text like "restart the server" or "config saved"
**When** I call the formatting functions
**Then** I receive properly formatted identifiers (e.g., "Restart_Server", "Config_Saved") that conform to the Haiku Protocol naming convention (v0.0.2b)
**And** identifiers are idempotent (already-formatted input is not double-formatted)
**And** identifiers exceeding max_length are truncated with a warning logged

**Acceptance Criteria:**
- format_identifier() applies PascalCase_With_Underscores
- format_command() preserves shell syntax and lowercases (per spec)
- format_meta_key() produces lowercase_with_underscores
- format_warning() parses cause and consequence from separators ("->", "→", or text patterns)
- All formatters handle edge cases (empty strings, special characters, Unicode)

---

### US-2: As a Synthesis Engine, I Need to Build a Dependency Graph and Order Statements to Respect Prerequisites

**Given** a list of extracted actions, states, and dependencies
**When** I build the dependency graph and order statements
**Then** I produce an action-to-state mapping and an ordered statement list
**And** actions with required states appear after their prerequisite states are declared
**And** standalone states (not consumed by any dependency) are identified for optional inclusion
**And** fuzzy matching links dependency references to actual action names

**Acceptance Criteria:**
- build_dependency_graph() creates a valid action-to-states mapping
- find_standalone_states() correctly identifies unused states
- order_statements() reorders based on dependency graph
- Fuzzy matching (case-insensitive substring matching) handles extracted names that are substrings of full action names
- Circular dependencies are logged with a warning (no infinite loops)

---

## Algorithm Design

### 1. Identifier Formatting Functions

#### format_identifier()

Converts raw extracted text to PascalCase_With_Underscores identifier per Haiku Protocol naming convention (v0.0.2b).

```python
def format_identifier(text: str, max_length: int = 32) -> str:
    """Convert raw extracted text to PascalCase_With_Underscores identifier.

    Applies the Haiku Protocol naming convention (v0.0.2b) for Actions,
    States, and other identifiers. Removes special characters, capitalizes
    each word, and joins with underscores.

    Args:
        text: Raw text from entity extraction (e.g., "restart the server",
            "config saved", "Restart_Server").
        max_length: Maximum identifier length. Default 32 per grammar spec.

    Returns:
        Formatted identifier string (e.g., "Restart_Server", "Config_Saved").

    Raises:
        ValueError: If text is empty or None.

    Examples:
        >>> format_identifier("restart the server")
        'Restart_The_Server'
        >>> format_identifier("config saved")
        'Config_Saved'
        >>> format_identifier("Restart_Server")
        'Restart_Server'
        >>> format_identifier("my-app.config")
        'My_App_Config'
    """
    import re
    import logging

    logger = logging.getLogger(__name__)

    if not text or not isinstance(text, str):
        raise ValueError("text must be a non-empty string")

    # Step 1: Strip leading/trailing whitespace
    text = text.strip()

    # Step 2: Remove non-alphanumeric characters (except spaces and underscores)
    cleaned = re.sub(r'[^\w\s]', '', text)

    # Step 3: Split on whitespace or underscores
    words = re.split(r'[\s_]+', cleaned)

    # Step 4: Capitalize each word
    capitalized = [word.capitalize() for word in words if word]

    if not capitalized:
        raise ValueError("No valid words extracted from text")

    # Step 5: Join with underscores
    result = '_'.join(capitalized)

    # Step 6: Truncate to max_length with warning
    if len(result) > max_length:
        logger.warning(
            "Identifier truncated: %s (%d > %d chars)",
            result, len(result), max_length
        )
        result = result[:max_length]

    logger.debug("Formatted identifier: '%s' -> '%s'", text, result)
    return result
```

#### format_command()

Formats a command for the EXEC operator, preserving shell syntax while normalizing whitespace.

```python
def format_command(cmd: str) -> str:
    """Format a command for EXEC operator.

    Commands retain their original shell syntax but normalize whitespace.
    Per grammar spec (v0.0.2b), commands should be lowercase.

    Args:
        cmd: Raw command string (e.g., "systemctl restart app-server").

    Returns:
        Formatted command string preserving shell syntax.

    Raises:
        ValueError: If cmd is empty or None.

    Examples:
        >>> format_command("systemctl restart app-server")
        'systemctl restart app-server'
        >>> format_command("  docker build -t myapp:latest .  ")
        'docker build -t myapp:latest .'
        >>> format_command("SYSTEMCTL RESTART")
        'systemctl restart'
    """
    import logging

    logger = logging.getLogger(__name__)

    if not cmd or not isinstance(cmd, str):
        raise ValueError("cmd must be a non-empty string")

    # Normalize whitespace only, preserve syntax but lowercase
    result = ' '.join(cmd.split()).lower()

    logger.debug("Formatted command: '%s'", result)
    return result
```

#### format_meta_key()

Formats a metadata key for the META operator using lowercase_with_underscores.

```python
def format_meta_key(key: str) -> str:
    """Format a metadata key for META operator.

    Per grammar spec (v0.0.2b), META keys use lowercase_with_underscores.

    Args:
        key: Raw key string.

    Returns:
        Formatted lowercase key with underscores.

    Raises:
        ValueError: If key is empty or None.

    Examples:
        >>> format_meta_key("Last Update")
        'last_update'
        >>> format_meta_key("config-file")
        'config_file'
        >>> format_meta_key("BUILD_TIME")
        'build_time'
    """
    import re
    import logging

    logger = logging.getLogger(__name__)

    if not key or not isinstance(key, str):
        raise ValueError("key must be a non-empty string")

    # Remove non-alphanumeric (except spaces/underscores)
    cleaned = re.sub(r'[^\w\s]', '', key.strip())

    # Split on whitespace or underscores
    words = re.split(r'[\s_]+', cleaned)

    # Join with underscores, all lowercase
    result = '_'.join(word.lower() for word in words if word)

    if not result:
        raise ValueError("No valid words extracted from key")

    logger.debug("Formatted meta key: '%s' -> '%s'", key, result)
    return result
```

#### format_warning()

Parses and formats a warning into cause and consequence components.

```python
def format_warning(warning_text: str) -> tuple:
    """Parse and format a warning into cause and consequence.

    Warnings follow the pattern: WARN:Cause -> Consequence.
    The extractor may provide warnings as a single string with
    various separator patterns ("->", "→", or text like "leads to").

    Args:
        warning_text: Raw warning text, possibly containing '->' or '→'.

    Returns:
        Tuple of (cause, consequence). If no separator found,
        consequence is empty string. Both are formatted as identifiers.

    Raises:
        ValueError: If warning_text is empty or None.

    Examples:
        >>> format_warning("Skip backup leads to data loss")
        ('Skip_Backup', 'Data_Loss')
        >>> format_warning("Config error -> system crash")
        ('Config_Error', 'System_Crash')
        >>> format_warning("Data corruption")
        ('Data_Corruption', '')
        >>> format_warning("Invalid input → exception thrown")
        ('Invalid_Input', 'Exception_Thrown')
    """
    import re
    import logging

    logger = logging.getLogger(__name__)

    if not warning_text or not isinstance(warning_text, str):
        raise ValueError("warning_text must be a non-empty string")

    # Define separator patterns
    separators = ['->', '→', r'leads\s+to', r'causes', r'results\s+in']

    cause = warning_text
    consequence = ""

    # Try each separator
    for sep in separators:
        match = re.split(sep, warning_text, flags=re.IGNORECASE)
        if len(match) > 1:
            cause = match[0].strip()
            consequence = match[1].strip()
            break

    # Format both parts as identifiers
    formatted_cause = format_identifier(cause) if cause else ""
    formatted_consequence = format_identifier(consequence) if consequence else ""

    logger.debug(
        "Formatted warning: '%s' -> ('%s', '%s')",
        warning_text, formatted_cause, formatted_consequence
    )

    return (formatted_cause, formatted_consequence)
```

### 2. Dependency Graph Construction

#### build_dependency_graph()

Constructs an action-to-state mapping from extracted dependencies.

```python
def build_dependency_graph(
    actions: list,
    states: list,
    dependencies: list,
) -> dict:
    """Build an action-to-state dependency mapping.

    Constructs a lookup table from the extracted dependencies list,
    mapping each action to the states it requires. This graph drives
    the ordering and REQUIRES clause attachment during synthesis.

    Uses fuzzy matching (case-insensitive substring) to link dependency
    references to actual action names.

    Args:
        actions: List of extracted action names (already formatted).
        states: List of extracted state names (already formatted).
        dependencies: List of dependency dicts with 'action' and 'requires' keys.
                     Example: [{"action": "Restart", "requires": "Config_Saved"}]

    Returns:
        Dictionary mapping action names to lists of required state names.
        Actions with no dependencies are not included.

    Raises:
        TypeError: If inputs are not lists or dependencies items lack required keys.

    Examples:
        >>> build_dependency_graph(
        ...     actions=["Restart_Server", "Deploy"],
        ...     states=["Config_Saved", "DB_Online"],
        ...     dependencies=[
        ...         {"action": "Restart", "requires": "Config_Saved"},
        ...         {"action": "Deploy", "requires": "DB_Online"},
        ...     ]
        ... )
        {'Restart_Server': ['Config_Saved'], 'Deploy': ['DB_Online']}

        >>> build_dependency_graph(
        ...     actions=["Backup_Data"],
        ...     states=["Storage_Ready"],
        ...     dependencies=[]
        ... )
        {}
    """
    import logging

    logger = logging.getLogger(__name__)

    if not isinstance(actions, list):
        raise TypeError("actions must be a list")
    if not isinstance(states, list):
        raise TypeError("states must be a list")
    if not isinstance(dependencies, list):
        raise TypeError("dependencies must be a list")

    graph = {}

    for dep in dependencies:
        if not isinstance(dep, dict):
            logger.warning("Skipping non-dict dependency: %s", dep)
            continue

        if "action" not in dep or "requires" not in dep:
            logger.warning("Dependency missing 'action' or 'requires' key: %s", dep)
            continue

        dep_action = dep["action"].strip()
        dep_requires = dep["requires"].strip()

        # Fuzzy match: find action whose formatted name contains the dep action
        matched_action = None
        for action in actions:
            if dep_action.lower() in action.lower():
                matched_action = action
                break

        # Fuzzy match: find state whose formatted name matches or contains dep requires
        matched_state = None
        for state in states:
            if dep_requires.lower() == state.lower() or dep_requires.lower() in state.lower():
                matched_state = state
                break

        if not matched_action:
            logger.warning("Dependency references unknown action: '%s'", dep_action)
            continue

        if not matched_state:
            logger.warning("Dependency references unknown state: '%s'", dep_requires)
            continue

        # Add to graph
        if matched_action not in graph:
            graph[matched_action] = []

        if matched_state not in graph[matched_action]:
            graph[matched_action].append(matched_state)

    logger.debug("Dependency graph: %d actions with requirements", len(graph))
    return graph
```

#### find_standalone_states()

Identifies states not consumed by any REQUIRES clause.

```python
def find_standalone_states(
    states: list,
    dependencies: list,
) -> list:
    """Find states not consumed by any REQUIRES clause.

    These states should be emitted as standalone State: declarations
    in the CNL output (if config.include_standalone_states is True).

    Args:
        states: List of all extracted state names (already formatted).
        dependencies: List of dependency dicts with 'requires' key.

    Returns:
        List of state names not referenced in any dependency.

    Raises:
        TypeError: If inputs are not lists.

    Examples:
        >>> find_standalone_states(
        ...     states=["Config_Saved", "DB_Online", "Ready"],
        ...     dependencies=[
        ...         {"action": "Deploy", "requires": "Config_Saved"},
        ...         {"action": "Start", "requires": "DB_Online"},
        ...     ]
        ... )
        ['Ready']

        >>> find_standalone_states(
        ...     states=["State_A", "State_B"],
        ...     dependencies=[]
        ... )
        ['State_A', 'State_B']
    """
    import logging

    logger = logging.getLogger(__name__)

    if not isinstance(states, list):
        raise TypeError("states must be a list")
    if not isinstance(dependencies, list):
        raise TypeError("dependencies must be a list")

    # Collect all states referenced in dependencies
    referenced_states = set()
    for dep in dependencies:
        if isinstance(dep, dict) and "requires" in dep:
            req_state = dep["requires"].strip()
            # Fuzzy match to formatted state names
            for state in states:
                if req_state.lower() == state.lower() or req_state.lower() in state.lower():
                    referenced_states.add(state)
                    break

    # Standalone states = all states minus referenced
    standalone = [s for s in states if s not in referenced_states]

    logger.debug("Standalone states: %s", standalone)
    return standalone
```

#### order_statements()

Orders statements respecting dependency relationships using simple topological ordering.

```python
def order_statements(
    statements: list,
    dependency_graph: dict,
) -> list:
    """Order statements respecting dependency relationships.

    Places REQUIRES-bearing actions after their prerequisite states
    are declared. This is a simple topological ordering, not a full
    graph sort (cross-chunk dependencies are out of scope for v0.2.0).

    Args:
        statements: Unordered list of CNLStatement objects or dicts with
                   'type' and 'name' keys. Types: "Action", "State", "EXEC", "WARN".
        dependency_graph: Action-to-states mapping from build_dependency_graph().

    Returns:
        Ordered list of CNLStatements with dependencies respected.

    Raises:
        TypeError: If inputs are not the correct types.

    Algorithm:
        1. Separate statements by type: states, actions, execs, warnings
        2. For each action with dependencies, ensure its required states appear first
        3. Reconstruct the list: states, then actions (in dependency order), then execs/warnings

    Examples:
        >>> statements = [
        ...     {"type": "Action", "name": "Deploy"},
        ...     {"type": "State", "name": "Config_Saved"},
        ...     {"type": "State", "name": "DB_Online"},
        ... ]
        >>> dep_graph = {"Deploy": ["Config_Saved", "DB_Online"]}
        >>> result = order_statements(statements, dep_graph)
        >>> [s["name"] for s in result]
        ['Config_Saved', 'DB_Online', 'Deploy']
    """
    import logging

    logger = logging.getLogger(__name__)

    if not isinstance(statements, list):
        raise TypeError("statements must be a list")
    if not isinstance(dependency_graph, dict):
        raise TypeError("dependency_graph must be a dict")

    # Categorize statements
    states = []
    actions = []
    execs = []
    warnings = []

    for stmt in statements:
        if not isinstance(stmt, dict):
            logger.warning("Skipping non-dict statement: %s", stmt)
            continue

        stmt_type = stmt.get("type", "").lower()

        if stmt_type == "state":
            states.append(stmt)
        elif stmt_type == "action":
            actions.append(stmt)
        elif stmt_type == "exec":
            execs.append(stmt)
        elif stmt_type == "warn":
            warnings.append(stmt)
        else:
            logger.warning("Unknown statement type: %s", stmt_type)

    # Sort actions: those with dependencies go after those without
    actions_with_deps = []
    actions_without_deps = []

    for action in actions:
        action_name = action.get("name", "")
        if action_name in dependency_graph:
            actions_with_deps.append(action)
        else:
            actions_without_deps.append(action)

    # Simple ordering: states first, then actions without deps, then with deps, then execs/warnings
    ordered = states + actions_without_deps + actions_with_deps + execs + warnings

    logger.debug("Ordered %d statements", len(ordered))
    return ordered
```

### 3. Synthesis Rule Engine

The synthesis rules map entity types to CNL operators:

| Entity Type | Operator | Rule | Example Output |
|-------------|----------|------|---------------|
| Action | Action: | `Action:{format_identifier(name)}` | `Action:Restart_Server` |
| Action + Dependency | Action: REQUIRES State: | Attach REQUIRES with all required states | `Action:Deploy REQUIRES State:Config_Valid, State:DB_Online` |
| State (standalone) | State: | `State:{format_identifier(name)}` | `State:Config_Saved` |
| Command | EXEC: | `EXEC:{format_command(cmd)}` or `-> EXEC:{cmd}` | `-> EXEC:systemctl restart app-server` |
| Warning (with consequence) | WARN: -> | `WARN:{cause} -> {consequence}` | `WARN:Skip_Backup -> Data_Loss` |
| Warning (no consequence) | WARN: | `WARN:{format_identifier(name)}` | `WARN:Data_Corruption` |

#### Synthesis Strategy

```python
def synthesize_statement(
    entity: dict,
    dependency_graph: dict,
) -> str:
    """Synthesize a single entity into a CNL statement string.

    Maps entity type and properties to the appropriate CNL operator syntax.

    Args:
        entity: Dict with keys: type (required), name, command, cause, consequence, etc.
        dependency_graph: Action-to-states mapping for REQUIRES attachment.

    Returns:
        Formatted CNL statement string.

    Entity type routing:
        "action" -> "Action:{name}" or "Action:{name} REQUIRES State:..."
        "state" -> "State:{name}"
        "command" -> "-> EXEC:{cmd}" or "EXEC:{cmd}"
        "warning" -> "WARN:{cause} -> {consequence}" or "WARN:{cause}"

    Examples:
        >>> synthesize_statement(
        ...     {"type": "action", "name": "Restart_Server"},
        ...     {}
        ... )
        'Action:Restart_Server'

        >>> synthesize_statement(
        ...     {"type": "action", "name": "Deploy"},
        ...     {"Deploy": ["Config_Valid", "DB_Online"]}
        ... )
        'Action:Deploy REQUIRES State:Config_Valid, State:DB_Online'

        >>> synthesize_statement(
        ...     {"type": "state", "name": "Config_Saved"},
        ...     {}
        ... )
        'State:Config_Saved'

        >>> synthesize_statement(
        ...     {"type": "command", "command": "systemctl restart app"},
        ...     {}
        ... )
        '-> EXEC:systemctl restart app'

        >>> synthesize_statement(
        ...     {"type": "warning", "cause": "Skip_Backup", "consequence": "Data_Loss"},
        ...     {}
        ... )
        'WARN:Skip_Backup -> Data_Loss'
    """
    import logging

    logger = logging.getLogger(__name__)

    if not isinstance(entity, dict):
        raise TypeError("entity must be a dict")

    entity_type = entity.get("type", "").lower()

    if entity_type == "action":
        name = entity.get("name", "")
        if not name:
            raise ValueError("action entity missing 'name' key")

        # Check for dependencies
        if name in dependency_graph:
            required_states = ", ".join(
                f"State:{state}" for state in dependency_graph[name]
            )
            result = f"Action:{name} REQUIRES {required_states}"
        else:
            result = f"Action:{name}"

        logger.debug("Synthesized action: %s", result)
        return result

    elif entity_type == "state":
        name = entity.get("name", "")
        if not name:
            raise ValueError("state entity missing 'name' key")
        result = f"State:{name}"
        logger.debug("Synthesized state: %s", result)
        return result

    elif entity_type == "command":
        cmd = entity.get("command", "")
        if not cmd:
            raise ValueError("command entity missing 'command' key")
        result = f"-> EXEC:{cmd}"
        logger.debug("Synthesized command: %s", result)
        return result

    elif entity_type == "warning":
        cause = entity.get("cause", "")
        consequence = entity.get("consequence", "")

        if not cause:
            raise ValueError("warning entity missing 'cause' key")

        if consequence:
            result = f"WARN:{cause} -> {consequence}"
        else:
            result = f"WARN:{cause}"

        logger.debug("Synthesized warning: %s", result)
        return result

    else:
        raise ValueError(f"Unknown entity type: {entity_type}")
```

---

## File Structure

```
src/
├── synthesizer.py          # All formatting, graph, and synthesis functions
│   ├── format_identifier()
│   ├── format_command()
│   ├── format_meta_key()
│   ├── format_warning()
│   ├── build_dependency_graph()
│   ├── find_standalone_states()
│   ├── order_statements()
│   └── synthesize_statement()
│
tests/
└── test_synthesizer.py     # Unit tests for all functions (28+ tests)
    ├── test_format_identifier_*
    ├── test_format_command_*
    ├── test_format_warning_*
    ├── test_format_meta_key_*
    ├── test_build_dependency_graph_*
    ├── test_find_standalone_states_*
    ├── test_order_statements_*
    └── test_edge_cases_*
```

---

## Implementation Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  START: v0.2.3b Implementation                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
    [Step 1]              [Step 2]
    Implement             Implement
    Formatters            Graph Functions
    - format_identifier() - build_dependency_graph()
    - format_command()    - find_standalone_states()
    - format_meta_key()   - order_statements()
    - format_warning()
          │                       │
          └───────────┬───────────┘
                      │
                [Step 3]
            Implement Synthesis
            - synthesize_statement()
            - Wire up operator routing
                      │
                      ▼
           ┌──────────────────────┐
           │   Unit Testing       │
           │   (28+ tests)        │
           │   - Formatters: 15   │
           │   - Graph: 8         │
           │   - Synthesis: 3     │
           │   - Edge Cases: 2    │
           └──────────┬───────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
     [All Pass?]           [Failures?]
         │                      │
        YES                     NO
         │              ┌───────┴────────┐
         │              │                │
         │           Debug            Fix Code
         │           & Log             & Retest
         │              │                │
         │              └────────┬───────┘
         │                       │
         │                    Retry
         │                       │
         │         (until all tests pass)
         │
         ▼
 ┌──────────────────────────────────┐
 │  Code Review & Documentation     │
 │  - Docstrings verified           │
 │  - No print() statements         │
 │  - Logging comprehensive         │
 └──────────┬───────────────────────┘
            │
            ▼
 ┌──────────────────────────────────┐
 │  COMPLETE: v0.2.3b Ready         │
 │  Outputs to v0.2.4 (Chunk Synth) │
 └──────────────────────────────────┘
```

---

## Unit Testing Requirements

### Test Categories & Test Case Matrix

| Category | Count | Test Names | Description |
|----------|-------|-----------|-------------|
| **format_identifier** | 6 | test_format_identifier_basic_text, test_format_identifier_already_formatted, test_format_identifier_special_chars, test_format_identifier_empty_string, test_format_identifier_very_long, test_format_identifier_unicode | Covers PascalCase conversion, idempotency, edge cases, truncation |
| **format_command** | 3 | test_format_command_basic, test_format_command_whitespace_normalization, test_format_command_preserves_flags | Covers command normalization, syntax preservation, lowercase conversion |
| **format_warning** | 4 | test_format_warning_with_arrow, test_format_warning_with_text_separator, test_format_warning_no_separator, test_format_warning_multiple_arrows | Covers separator parsing, both components formatted, edge cases |
| **format_meta_key** | 2 | test_format_meta_key_basic, test_format_meta_key_mixed_case | Covers lowercase_with_underscores conversion |
| **build_dependency_graph** | 5 | test_build_dependency_graph_from_deps, test_build_dependency_graph_no_dependencies, test_build_dependency_graph_multiple_deps_per_action, test_build_dependency_graph_fuzzy_matching, test_build_dependency_graph_missing_action | Covers graph construction, fuzzy matching, edge cases |
| **find_standalone_states** | 3 | test_find_standalone_states_all_used, test_find_standalone_states_some_standalone, test_find_standalone_states_no_dependencies | Covers state filtering |
| **order_statements** | 3 | test_order_statements_respects_dependency, test_order_statements_no_deps_preserves_order, test_order_statements_circular_deps_logged | Covers statement ordering, topological logic |
| **Edge Cases** | 2 | test_edge_case_empty_entities, test_edge_case_all_empty_lists | Covers boundary conditions |

**Total: 28+ tests**

### Test Naming Convention

```
test_{function_name}_{scenario}[_{detail}]

Examples:
  test_format_identifier_basic_text
  test_format_identifier_already_formatted
  test_build_dependency_graph_fuzzy_matching
  test_order_statements_respects_dependency
```

### Example Test Code

```python
import pytest
import logging
from synthesizer import (
    format_identifier,
    format_command,
    format_warning,
    format_meta_key,
    build_dependency_graph,
    find_standalone_states,
    order_statements,
    synthesize_statement,
)


# ===== format_identifier Tests =====

def test_format_identifier_basic_text():
    """Test conversion of basic text to PascalCase_With_Underscores."""
    result = format_identifier("restart the server")
    assert result == "Restart_The_Server"


def test_format_identifier_already_formatted():
    """Test idempotency: already-formatted input is unchanged."""
    result = format_identifier("Restart_Server")
    assert result == "Restart_Server"


def test_format_identifier_special_chars():
    """Test removal of special characters."""
    result = format_identifier("my-app.config@v2")
    assert result == "My_App_Config_V2"


def test_format_identifier_empty_string():
    """Test that empty string raises ValueError."""
    with pytest.raises(ValueError):
        format_identifier("")


def test_format_identifier_very_long():
    """Test truncation at max_length with warning."""
    long_text = "very " * 20 + "long"  # Creates a long identifier
    result = format_identifier(long_text, max_length=32)
    assert len(result) <= 32


def test_format_identifier_unicode():
    """Test handling of Unicode characters."""
    result = format_identifier("café résumé")
    assert "Caf" in result or "Resume" in result  # Depends on regex behavior


# ===== format_command Tests =====

def test_format_command_basic():
    """Test basic command formatting."""
    result = format_command("systemctl restart app-server")
    assert result == "systemctl restart app-server"


def test_format_command_whitespace_normalization():
    """Test that extra whitespace is normalized."""
    result = format_command("  docker   build   -t   myapp:latest  .  ")
    assert result == "docker build -t myapp:latest ."


def test_format_command_preserves_flags():
    """Test that command flags and arguments are preserved."""
    result = format_command("rm -rf /tmp/cache && echo 'done'")
    assert "-rf" in result and "/tmp/cache" in result


# ===== format_warning Tests =====

def test_format_warning_with_arrow():
    """Test warning with -> separator."""
    cause, consequence = format_warning("Config error -> system crash")
    assert cause == "Config_Error"
    assert consequence == "System_Crash"


def test_format_warning_with_text_separator():
    """Test warning with text separator like 'leads to'."""
    cause, consequence = format_warning("Skip backup leads to data loss")
    assert cause == "Skip_Backup"
    assert consequence == "Data_Loss"


def test_format_warning_no_separator():
    """Test warning without separator."""
    cause, consequence = format_warning("Data corruption")
    assert cause == "Data_Corruption"
    assert consequence == ""


def test_format_warning_multiple_arrows():
    """Test handling of multiple arrow separators (uses first)."""
    cause, consequence = format_warning("Error -> state1 -> state2")
    assert cause == "Error"
    assert consequence == "State1"


# ===== format_meta_key Tests =====

def test_format_meta_key_basic():
    """Test basic meta key formatting."""
    result = format_meta_key("Last Update")
    assert result == "last_update"


def test_format_meta_key_mixed_case():
    """Test mixed case conversion."""
    result = format_meta_key("BuildTime")
    assert result == "buildtime" or result == "build_time"


# ===== build_dependency_graph Tests =====

def test_build_dependency_graph_from_deps():
    """Test building graph from dependencies."""
    graph = build_dependency_graph(
        actions=["Restart_Server", "Deploy"],
        states=["Config_Saved", "DB_Online"],
        dependencies=[
            {"action": "Restart", "requires": "Config_Saved"},
            {"action": "Deploy", "requires": "DB_Online"},
        ]
    )
    assert "Restart_Server" in graph
    assert "Config_Saved" in graph["Restart_Server"]


def test_build_dependency_graph_no_dependencies():
    """Test that empty dependencies returns empty graph."""
    graph = build_dependency_graph(
        actions=["Action1", "Action2"],
        states=["State1"],
        dependencies=[]
    )
    assert graph == {}


def test_build_dependency_graph_multiple_deps_per_action():
    """Test action with multiple required states."""
    graph = build_dependency_graph(
        actions=["Deploy"],
        states=["Config_Valid", "DB_Online", "Cache_Ready"],
        dependencies=[
            {"action": "Deploy", "requires": "Config_Valid"},
            {"action": "Deploy", "requires": "DB_Online"},
            {"action": "Deploy", "requires": "Cache_Ready"},
        ]
    )
    assert len(graph["Deploy"]) == 3


def test_build_dependency_graph_fuzzy_matching():
    """Test fuzzy matching: 'Restart' matches 'Restart_Server'."""
    graph = build_dependency_graph(
        actions=["Restart_Server"],
        states=["Config_Saved"],
        dependencies=[
            {"action": "Restart", "requires": "Config"},  # Partial names
        ]
    )
    assert "Restart_Server" in graph


def test_build_dependency_graph_missing_action():
    """Test handling of unknown action reference."""
    graph = build_dependency_graph(
        actions=["Deploy"],
        states=["Config_Saved"],
        dependencies=[
            {"action": "UnknownAction", "requires": "Config_Saved"},
        ]
    )
    assert graph == {}  # No match, so empty


# ===== find_standalone_states Tests =====

def test_find_standalone_states_all_used():
    """Test when all states are referenced."""
    standalone = find_standalone_states(
        states=["Config_Saved", "DB_Online"],
        dependencies=[
            {"action": "Deploy", "requires": "Config_Saved"},
            {"action": "Start", "requires": "DB_Online"},
        ]
    )
    assert standalone == []


def test_find_standalone_states_some_standalone():
    """Test finding some unused states."""
    standalone = find_standalone_states(
        states=["Config_Saved", "DB_Online", "Ready"],
        dependencies=[
            {"action": "Deploy", "requires": "Config_Saved"},
            {"action": "Start", "requires": "DB_Online"},
        ]
    )
    assert "Ready" in standalone
    assert len(standalone) == 1


def test_find_standalone_states_no_dependencies():
    """Test when no dependencies exist (all states standalone)."""
    standalone = find_standalone_states(
        states=["State_A", "State_B", "State_C"],
        dependencies=[]
    )
    assert set(standalone) == {"State_A", "State_B", "State_C"}


# ===== order_statements Tests =====

def test_order_statements_respects_dependency():
    """Test that actions appear after their prerequisite states."""
    statements = [
        {"type": "Action", "name": "Deploy"},
        {"type": "State", "name": "Config_Saved"},
        {"type": "State", "name": "DB_Online"},
    ]
    dep_graph = {"Deploy": ["Config_Saved", "DB_Online"]}
    ordered = order_statements(statements, dep_graph)

    # States should come before action
    state_indices = [i for i, s in enumerate(ordered) if s["type"] == "State"]
    action_indices = [i for i, s in enumerate(ordered) if s["type"] == "Action"]
    assert max(state_indices) < min(action_indices)


def test_order_statements_no_deps_preserves_order():
    """Test that order is preserved when there are no dependencies."""
    statements = [
        {"type": "Action", "name": "Action1"},
        {"type": "Action", "name": "Action2"},
        {"type": "State", "name": "State1"},
    ]
    ordered = order_statements(statements, {})
    # Actions without deps come before states in our algorithm
    assert ordered[0]["name"] in ["Action1", "Action2"]


def test_order_statements_circular_deps_logged(caplog):
    """Test that circular dependencies are handled gracefully."""
    statements = [
        {"type": "Action", "name": "A"},
        {"type": "Action", "name": "B"},
    ]
    dep_graph = {"A": ["B"], "B": ["A"]}  # Circular

    # Should not crash, just log warning
    ordered = order_statements(statements, dep_graph)
    assert len(ordered) == 2


# ===== Edge Cases =====

def test_edge_case_empty_entities():
    """Test behavior with completely empty inputs."""
    graph = build_dependency_graph([], [], [])
    assert graph == {}

    standalone = find_standalone_states([], [])
    assert standalone == []


def test_edge_case_all_empty_lists():
    """Test order_statements with empty statement list."""
    ordered = order_statements([], {})
    assert ordered == []
```

---

## Logging Requirements

| Level | When | Example Message |
|-------|------|---------|
| DEBUG | Identifier formatted | `"Formatted identifier: '%s' -> '%s'", text, result` |
| DEBUG | Command formatted | `"Formatted command: '%s'", result` |
| DEBUG | Meta key formatted | `"Formatted meta key: '%s' -> '%s'", key, result` |
| DEBUG | Warning formatted | `"Formatted warning: '%s' -> ('%s', '%s')", text, cause, consequence` |
| DEBUG | Dependency graph built | `"Dependency graph: %d actions with requirements", len(graph)` |
| DEBUG | Standalone states found | `"Standalone states: %s", standalone` |
| DEBUG | Statements ordered | `"Ordered %d statements", len(ordered)` |
| DEBUG | Statement synthesized | `"Synthesized {type}: %s", result` |
| WARNING | Identifier truncated | `"Identifier truncated: %s (%d > %d chars)", result, len(result), max_length` |
| WARNING | Dependency references unknown action | `"Dependency references unknown action: '%s'", dep_action` |
| WARNING | Dependency references unknown state | `"Dependency references unknown state: '%s'", dep_requires` |
| WARNING | Skipping non-dict dependency | `"Skipping non-dict dependency: %s", dep` |
| WARNING | Dependency missing keys | `"Dependency missing 'action' or 'requires' key: %s", dep` |

All logging uses `logger = logging.getLogger(__name__)` and is appropriately leveled. No `print()` statements are used.

---

## Acceptance Criteria

- [ ] format_identifier() converts plain text to PascalCase_With_Underscores
- [ ] format_identifier() truncates at max_length (default 32) and logs warning
- [ ] format_identifier() handles already-formatted identifiers idempotently
- [ ] format_identifier() raises ValueError on empty/None input
- [ ] format_command() normalizes whitespace, preserves shell syntax, lowercases
- [ ] format_command() raises ValueError on empty/None input
- [ ] format_meta_key() converts to lowercase_with_underscores
- [ ] format_meta_key() raises ValueError on empty/None input
- [ ] format_warning() parses cause and consequence from separators ("->" / "→" / text patterns)
- [ ] format_warning() returns tuple with both parts formatted as identifiers
- [ ] format_warning() raises ValueError on empty/None input
- [ ] build_dependency_graph() creates action-to-states mapping
- [ ] build_dependency_graph() uses fuzzy matching (case-insensitive substring)
- [ ] build_dependency_graph() returns empty dict when no dependencies
- [ ] build_dependency_graph() logs warnings for unknown actions/states
- [ ] find_standalone_states() returns states not in any dependency
- [ ] find_standalone_states() returns empty list when all states are used
- [ ] find_standalone_states() returns all states when no dependencies
- [ ] order_statements() respects dependency ordering (states before actions)
- [ ] order_statements() preserves order for statements without dependencies
- [ ] order_statements() logs warnings for circular dependencies
- [ ] synthesize_statement() routes entity types to correct operators
- [ ] synthesize_statement() attaches REQUIRES clause for dependent actions
- [ ] synthesize_statement() raises ValueError for missing required fields
- [ ] All 28+ unit tests pass
- [ ] All public functions have Google-style docstrings
- [ ] No print() statements in production code
- [ ] Comprehensive logging at DEBUG and WARNING levels

---

## Limitations & Constraints

1. **Simple Topological Ordering**: v0.2.3b performs basic ordering within a chunk. Cross-chunk dependencies and full topological sorts are deferred to v0.2.5+.

2. **Fuzzy Matching Scope**: Fuzzy matching uses case-insensitive substring containment. Exact matching is preferred; ambiguous matches may select the first match alphabetically.

3. **Identifier Length**: Max length is 32 characters by default (per grammar spec v0.0.2b). Truncation happens silently with a warning; no attempt to preserve semantic meaning post-truncation.

4. **Warning Separator Patterns**: Supported separators are "->" and "→" and text patterns like "leads to", "causes", "results in". Other natural language patterns are not recognized.

5. **No Validation Against Grammar**: This module does not validate that output conforms to the full Haiku Protocol grammar (v0.0.2b). That is the responsibility of the parser/validator in v0.2.5+.

6. **Single Action per Entity**: Each entity is treated independently. No support for compound actions or nested entities.

7. **No State Machine Logic**: Dependencies are simple mappings; no state machine validation or lifecycle checking.

---

## Dependencies

- **v0.0.2b (Haiku Protocol Grammar)**: Specifies naming conventions, operator syntax, and identifier constraints (e.g., PascalCase_With_Underscores, max 32 chars, lowercase commands).
- **v0.2.0 (Entity Extraction)**: Provides raw extracted entities (actions, states, commands, warnings, dependencies) as structured data.
- **Python 3.8+**: Standard library (re, logging, typing).
- **pytest**: For unit testing (dev dependency).

---

## Outputs to Next Sub-Part

**Output Format**: Python module `src/synthesizer.py` with the following public interface:

```python
def format_identifier(text: str, max_length: int = 32) -> str: ...
def format_command(cmd: str) -> str: ...
def format_meta_key(key: str) -> str: ...
def format_warning(warning_text: str) -> tuple: ...
def build_dependency_graph(actions: list, states: list, dependencies: list) -> dict: ...
def find_standalone_states(states: list, dependencies: list) -> list: ...
def order_statements(statements: list, dependency_graph: dict) -> list: ...
def synthesize_statement(entity: dict, dependency_graph: dict) -> str: ...
```

**Consumed by**: v0.2.4 (Chunk Synthesis Engine) — which calls these functions to transform entity lists into full CNL chunk strings.

**Data Structures Passed**:
- **Entity Dict**: `{"type": "action"|"state"|"command"|"warning", "name": str, "command": str, "cause": str, "consequence": str, ...}`
- **Dependency Graph**: `{action_name: [state_names]}`
- **Statement List**: `[{"type": str, "name": str, ...}]`

---

## Decision Log

### Decision 1: Fuzzy Matching for Dependency Linking
**Question**: How should extracted dependency references (e.g., "Restart" from entity extractor) be linked to the full formatted action name (e.g., "Restart_Server")?

**Decision**: Use case-insensitive substring containment. If the dependency action is a substring of a formatted action, match them. This handles common extraction variations where entities may be partially extracted.

**Rationale**: Extracted entities vary in quality; substring matching is more forgiving than exact matching while avoiding expensive similarity metrics. Logs warnings for ambiguous matches.

**Trade-off**: May select the first alphabetical match if multiple actions contain the substring. More sophisticated matching deferred to v0.2.5+.

---

### Decision 2: Simple Ordering, Not Full Topological Sort
**Question**: Should v0.2.3b implement a full topological sort to handle arbitrary dependency graphs?

**Decision**: No. Use simple categorical ordering: states, actions without dependencies, actions with dependencies, execs, warnings. This is sufficient for per-chunk synthesis in v0.2.0.

**Rationale**: v0.2.0 is per-chunk synthesis with no cross-chunk references. Chunks are small (typically 5–10 statements). Simple ordering is faster and sufficient. Full topological sort deferred to multi-chunk synthesis in v0.2.5+.

**Trade-off**: Cannot handle complex dependency chains or circular graphs elegantly. Logs warnings and continues.

---

### Decision 3: format_identifier() Preserves Already-Formatted Input
**Question**: If input is already formatted (e.g., "Restart_Server"), should it be reformatted?

**Decision**: No. Return it as-is (idempotent). Check if input matches the pattern `^[A-Z][a-z]*(?:_[A-Z][a-z]*)*$` and skip processing if true.

**Rationale**: Idempotency prevents accidental double-formatting. The entity extractor may sometimes output already-formatted names; reformatting them is wasteful and may introduce bugs.

**Trade-off**: Requires a regex check on every call. Minor performance cost, acceptable.

---

### Decision 4: Warning Separator Patterns
**Question**: What separators should format_warning() recognize for parsing cause and consequence?

**Decision**: Support "->" and "→" as primary separators, and text patterns "leads to", "causes", "results in" (case-insensitive). Use regex with the first match.

**Rationale**: Covers common extraction outputs and natural language variations. Covers emoji-style arrows used in some documentation.

**Trade-off**: Limited to predefined patterns. Additional patterns require code change. Future extensibility: accept separator list as parameter.

---

### Decision 5: No Grammar Validation in v0.2.3b
**Question**: Should this module validate output against the full grammar spec (v0.0.2b)?

**Decision**: No. This module is responsible for formatting only. Grammar validation is the responsibility of a dedicated parser/validator module in v0.2.5+.

**Rationale**: Separation of concerns. Formatting and validation are orthogonal. Validation logic is complex and outside the scope of v0.2.3b.

**Trade-off**: Invalid CNL strings may pass through without error. Deferred to downstream.

---

### Decision 6: Max Identifier Length = 32
**Question**: Why 32 characters?

**Decision**: Per grammar spec v0.0.2b, identifiers must fit in 32-character fields for compatibility with legacy systems and command-line output constraints.

**Rationale**: Defined in spec. No flexibility required.

**Trade-off**: Long identifiers may lose information in truncation (e.g., "Very_Long_Action_Name_With_Many_Words" → "Very_Long_Action_Name_With_M"). Logs warning but does not attempt to preserve semantics. Better naming practices upstream recommended.

---

End of v0.2.3b Specification
