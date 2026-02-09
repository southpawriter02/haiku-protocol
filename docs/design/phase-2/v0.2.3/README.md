# v0.2.3 — CNL Synthesis Engine

<aside>

**Version:** v0.2.3

**Parent:** v0.2.0 — Encoder Development

**Status:** ⬜ Not Started

**Duration:** 60–90 minutes (across 4 sub-parts)

**Deliverable:** `synthesizer.py` — CNL string generation engine

</aside>

---

## Objective

Build the module that transforms extracted entities into compressed CNL (Controlled Natural Language) strings. This is where the **Haiku Protocol magic** happens. The synthesizer is a **rule-based** transformation (no LLM calls) that applies the grammar rules from v0.0.2b to produce deterministic, parseable CNL output.

---

## Sub-Parts

| Version | Name | Duration | Deliverable |
|---------|------|----------|-------------|
| [v0.2.3a](cnl_statement_model.md) | CNL Statement Data Model | 15–25 min | `CNLStatement`, `SynthesisConfig`, `OperatorType` enum, validators, 25+ tests |
| [v0.2.3b](identifier_formatting_and_synthesis_rules.md) | Identifier Formatting & Synthesis Rules | 20–30 min | Formatting functions, dependency graph, statement ordering, 28+ tests |
| [v0.2.3c](synthesis_engine.md) | CNL Synthesis Engine Core | 20–30 min | `CNLSynthesizer` class, flat/flow modes, `synthesize_cnl()` convenience function, 30+ tests |
| [v0.2.3d](integration_testing.md) | Integration Testing & Pipeline Handoff | 15–25 min | Golden synthesis samples, grammar compliance validation, pipeline handoff tests, 23+ tests |

**Total: 106+ tests across all sub-parts**

---

## Synthesis Rules

---

## Synthesis Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    CNL SYNTHESIS FLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   INPUT: Extracted Entities                                     │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │ actions: ["Restart_Server"]                               │ │
│   │ states: ["Config_Saved"]                                  │ │
│   │ commands: ["systemctl restart"]                           │ │
│   │ dependencies: [{action: "Restart", requires: "Config"}]   │ │
│   └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│   SYNTHESIS ENGINE                                              │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │ 1. Build dependency graph                                 │ │
│   │ 2. Order statements by dependency                         │ │
│   │ 3. Apply CNL grammar rules                                │ │
│   │ 4. Join with appropriate operators                        │ │
│   └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│   OUTPUT: CNL String                                            │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │ "Action:Restart_Server REQUIRES State:Config_Saved        │ │
│   │  -> EXEC:systemctl_restart; WARN:Skip_Save->Data_Loss"    │ │
│   └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation: [`synthesizer.py`](http://synthesizer.py)

```python
# src/synthesizer.py - CNL Synthesis Engine

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class CNLStatement:
    """A single CNL statement."""
    operator: str  # Action, State, EXEC, WARN, etc.
    value: str
    modifier: Optional[str] = None  # REQUIRES, ->, etc.
    target: Optional[str] = None

class CNLSynthesizer:
    """Synthesize CNL strings from extracted entities."""
    
    def __init__(self):
        self.statements = []
    
    def _format_identifier(self, text: str) -> str:
        """Convert text to CNL identifier format."""
        # Remove special characters, replace spaces with underscores
        import re
        cleaned = re.sub(r'[^\w\s]', '', text)
        return '_'.join(word.capitalize() for word in cleaned.split())
    
    def _format_command(self, cmd: str) -> str:
        """Format a command for CNL."""
        # Replace spaces with underscores for single-token commands
        return cmd.replace(' ', '_')
    
    def synthesize(self, entities: Dict) -> str:
        """
        Synthesize a CNL string from extracted entities.
        
        Args:
            entities: Dictionary with actions, states, commands, etc.
            
        Returns:
            CNL string
        """
        parts = []
        
        # Process actions with dependencies
        actions = entities.get("actions", [])
        states = entities.get("states", [])
        commands = entities.get("commands", [])
        warnings = entities.get("warnings", [])
        dependencies = entities.get("dependencies", [])
        
        # Build action statements
        for action in actions:
            action_id = self._format_identifier(action)
            stmt = f"Action:{action_id}"
            
            # Find dependencies for this action
            for dep in dependencies:
                if dep.get("action", "").lower() in action.lower():
                    req = dep.get("requires", "")
                    if req:
                        req_id = self._format_identifier(req)
                        stmt += f" REQUIRES State:{req_id}"
            
            parts.append(stmt)
        
        # Add standalone states (not in dependencies)
        dep_states = set()
        for dep in dependencies:
            if "requires" in dep:
                dep_states.add(dep["requires"].lower())
        
        for state in states:
            if state.lower() not in dep_states:
                state_id = self._format_identifier(state)
                parts.append(f"State:{state_id}")
        
        # Add commands
        for cmd in commands:
            cmd_formatted = self._format_command(cmd)
            parts.append(f"EXEC:{cmd_formatted}")
        
        # Add warnings
        for warning in warnings:
            # Try to parse condition->outcome format
            if "->" in warning or "→" in warning:
                warning = warning.replace("→", "->")
                parts.append(f"WARN:{self._format_identifier(warning)}")
            else:
                parts.append(f"WARN:{self._format_identifier(warning)}")
        
        # Join parts with appropriate operators
        if len(parts) == 0:
            return ""
        elif len(parts) == 1:
            return parts[0]
        else:
            # Use -> for sequential actions, ; for parallel
            return "; ".join(parts)
    
    def synthesize_with_flow(self, entities: Dict) -> str:
        """
        Synthesize CNL with explicit flow operators.
        
        This version uses -> for sequences within a procedure.
        """
        actions = entities.get("actions", [])
        states = entities.get("states", [])
        commands = entities.get("commands", [])
        dependencies = entities.get("dependencies", [])
        warnings = entities.get("warnings", [])
        
        # Build the main action chain
        main_parts = []
        
        # Start with primary action and its requirements
        if actions:
            primary_action = self._format_identifier(actions[0])
            action_stmt = f"Action:{primary_action}"
            
            # Add requirements
            reqs = []
            for state in states:
                reqs.append(f"State:{self._format_identifier(state)}")
            
            if reqs:
                action_stmt += f" REQUIRES {', '.join(reqs)}"
            
            main_parts.append(action_stmt)
        
        # Add command execution
        if commands:
            cmd_parts = [f"EXEC:{self._format_command(c)}" for c in commands]
            main_parts.extend(cmd_parts)
        
        # Build the flow string
        flow = " -> ".join(main_parts) if main_parts else ""
        
        # Add warnings as separate statements
        if warnings:
            warn_parts = [f"WARN:{self._format_identifier(w)}" for w in warnings]
            if flow:
                flow += "; " + "; ".join(warn_parts)
            else:
                flow = "; ".join(warn_parts)
        
        return flow

# Convenience function
def synthesize_cnl(entities: Dict, use_flow: bool = True) -> str:
    """
    Synthesize CNL from entities.
    
    Args:
        entities: Dictionary of extracted entities
        use_flow: Use flow operators (->)
        
    Returns:
        CNL string
    """
    synthesizer = CNLSynthesizer()
    if use_flow:
        return synthesizer.synthesize_with_flow(entities)
    return synthesizer.synthesize(entities)

if __name__ == "__main__":
    # Test the synthesizer
    sample_entities = {
        "actions": ["Restart_Server"],
        "states": ["Config_Saved"],
        "commands": ["systemctl restart app-server"],
        "warnings": ["Skip save leads to data loss"],
        "dependencies": [
            {"action": "Restart", "requires": "Config_Saved"}
        ]
    }
    
    result = synthesize_cnl(sample_entities)
    print(f"CNL Output: {result}")
```

---

## Test Cases

---

## Acceptance Criteria

- [ ]  [`synthesizer.py`](http://synthesizer.py) created in `src/` directory
- [ ]  `CNLSynthesizer` class implemented
- [ ]  Identifiers formatted correctly (PascalCase_With_Underscores)
- [ ]  Dependencies linked with `REQUIRES`
- [ ]  Commands wrapped with `EXEC:`
- [ ]  All test cases pass