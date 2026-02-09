# v0.2.2c — EntityExtractor Core Implementation

<aside>

**Version:** v0.2.2c

**Parent:** v0.2.2 — Entity Extraction

**Status:** ⬜ Not Started

**Duration:** 30–45 minutes

**Deliverable:** `EntityExtractor` class with LLM integration, JSON response parsing, retry logic, and confidence scoring

</aside>

---

## Objective

Implement the core `EntityExtractor` class that calls an LLM (GPT-4 via LangChain) with a structured extraction prompt, parses the JSON response, validates the output schema, and returns an `ExtractedEntities` container. This is the central engine of the second pipeline stage — it transforms raw chunk text into structured semantic entities.

The extractor must handle:
- LLM invocation via LangChain `ChatOpenAI`
- JSON parsing with fallback for malformed responses
- Output schema validation with error recovery
- Retry logic for transient LLM failures
- Confidence scoring based on extraction quality signals

---

## User Story

> As an encoder pipeline operator, I want the entity extractor to reliably produce structured JSON from document chunks — even when the LLM returns malformed output — so that the pipeline does not crash and partial results are still usable.

---

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│              ENTITY EXTRACTION FLOW                            │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   INPUT: Chunk.content (str)                                   │
│                          │                                     │
│                          ▼                                     │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ 1. PROMPT RENDERING                                     │  │
│   │    PromptRegistry.get_active().render(text)              │  │
│   └─────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ 2. LLM INVOCATION (with retries)                        │  │
│   │    ChatOpenAI.invoke(messages)                           │  │
│   │    ┌─ Retry on: rate limit, timeout, server error       │  │
│   │    └─ Max retries: configurable (default 3)             │  │
│   └─────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ 3. RESPONSE PARSING                                     │  │
│   │    Try: json.loads(response.content)                     │  │
│   │    Fallback: regex JSON extraction from mixed text       │  │
│   │    Last resort: return empty ExtractedEntities           │  │
│   └─────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ 4. SCHEMA VALIDATION                                    │  │
│   │    validate_extraction_output(raw_json)                  │  │
│   │    Log warnings for missing keys / wrong types           │  │
│   └─────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ 5. ENTITY CONSTRUCTION                                  │  │
│   │    Build ExtractedEntities from validated dict           │  │
│   │    Compute confidence score                              │  │
│   │    Attach chunk_id and raw_response                      │  │
│   └─────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│   OUTPUT: ExtractedEntities                                    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Implementation

### EntityExtractor Class

```python
class EntityExtractor:
    """Extract semantic entities from text using an LLM.

    Wraps LangChain's ChatOpenAI to send structured extraction prompts
    and parse JSON responses into ExtractedEntities containers.

    Attributes:
        llm: LangChain ChatOpenAI instance.
        prompt_registry: Registry of versioned extraction prompts.
        config: Extraction configuration (retries, model, temperature).

    Example:
        >>> extractor = EntityExtractor(model="gpt-4", temperature=0)
        >>> result = extractor.extract("Restart the server after saving config.")
        >>> result.actions
        ['Restart_Server']
    """

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        prompt_version: Optional[str] = None,
    ) -> None:
        """Initialize the entity extractor.

        Args:
            model: OpenAI model identifier (e.g., "gpt-4", "gpt-4-turbo").
            temperature: LLM temperature. 0 for deterministic output.
            max_retries: Maximum retry attempts for transient failures.
            retry_delay: Base delay between retries (exponential backoff).
            prompt_version: Specific prompt version to use. If None, uses
                the registry's active version.

        Raises:
            RuntimeError: If OPENAI_API_KEY is not set in environment.
        """
        ...

    def extract(self, text: str, chunk_id: Optional[str] = None) -> ExtractedEntities:
        """Extract entities from a single text string.

        Args:
            text: Document chunk content to analyze.
            chunk_id: Optional chunk ID for traceability.

        Returns:
            ExtractedEntities with extracted data and confidence score.
            Returns empty ExtractedEntities on unrecoverable failure.

        Raises:
            TypeError: If text is not a string.
        """
        ...

    def _invoke_llm(self, prompt: str) -> str:
        """Call the LLM with retry logic.

        Args:
            prompt: Rendered prompt string.

        Returns:
            Raw response content string.

        Raises:
            ExtractionError: After all retries exhausted.
        """
        ...

    def _parse_response(self, raw_response: str) -> dict:
        """Parse LLM response into a dictionary.

        Attempts JSON parsing with multiple fallback strategies:
        1. Direct json.loads()
        2. Regex extraction of JSON object from mixed text
        3. Regex extraction of JSON from markdown code block
        4. Return empty dict on total failure

        Args:
            raw_response: Raw LLM response string.

        Returns:
            Parsed dictionary (may be empty on failure).
        """
        ...

    def _compute_confidence(
        self, entities: ExtractedEntities, parse_succeeded: bool
    ) -> float:
        """Compute a confidence score for the extraction.

        Confidence is based on:
        - JSON parse success (0.3 weight)
        - Naming convention compliance (0.3 weight)
        - Non-empty extraction (0.2 weight)
        - Dependency validity (0.2 weight)

        Args:
            entities: The extracted entities to score.
            parse_succeeded: Whether JSON parsing succeeded on first try.

        Returns:
            Float between 0.0 and 1.0.
        """
        ...
```

### Custom Exceptions

```python
class ExtractionError(Exception):
    """Raised when entity extraction fails after all retries.

    Attributes:
        message: Error description.
        raw_response: The last LLM response received (if any).
        attempts: Number of attempts made.
    """
    def __init__(self, message: str, raw_response: str = "", attempts: int = 0):
        self.message = message
        self.raw_response = raw_response
        self.attempts = attempts
        super().__init__(message)
```

### Convenience Function

```python
def extract_entities(
    text: str,
    model: str = "gpt-4",
    chunk_id: Optional[str] = None,
) -> dict:
    """Extract entities from text and return as dictionary.

    Convenience wrapper for quick usage without managing
    EntityExtractor lifecycle.

    Args:
        text: Text to analyze.
        model: OpenAI model to use.
        chunk_id: Optional chunk ID for traceability.

    Returns:
        Dictionary of extracted entities (via ExtractedEntities.to_dict()).
    """
    extractor = EntityExtractor(model=model)
    result = extractor.extract(text, chunk_id=chunk_id)
    return result.to_dict()
```

---

## JSON Parsing Fallback Chain

```
┌────────────────────────────────────────────────────────────────┐
│              JSON PARSING FALLBACK CHAIN                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Attempt 1: json.loads(raw_response)                           │
│  ┌─ Success → return dict                                      │
│  └─ Failure → continue                                         │
│                                                                │
│  Attempt 2: Regex extract { ... } from response                │
│  ┌─ Pattern: r'\{.*\}' with re.DOTALL                          │
│  ├─ Success → json.loads(match) → return dict                  │
│  └─ Failure → continue                                         │
│                                                                │
│  Attempt 3: Extract from markdown code block                   │
│  ┌─ Pattern: r'```(?:json)?\s*(\{.*?\})\s*```'                 │
│  ├─ Success → json.loads(match) → return dict                  │
│  └─ Failure → continue                                         │
│                                                                │
│  Attempt 4: Return empty dict + log WARNING                    │
│  └─ return {}                                                  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Confidence Scoring Algorithm

```python
def _compute_confidence(self, entities, parse_succeeded):
    score = 0.0

    # Factor 1: JSON parse success (0.3)
    if parse_succeeded:
        score += 0.3

    # Factor 2: Naming convention compliance (0.3)
    total_identifiers = len(entities.actions) + len(entities.states) + len(entities.warnings)
    if total_identifiers > 0:
        valid_count = sum(
            validate_identifier(name)
            for name in entities.actions + entities.states + entities.warnings
        )
        score += 0.3 * (valid_count / total_identifiers)

    # Factor 3: Non-empty extraction (0.2)
    if not entities.is_empty:
        score += 0.2

    # Factor 4: Dependency validity (0.2)
    if entities.dependencies:
        valid_deps = sum(
            1 for d in entities.dependencies
            if d.action and d.requires
        )
        score += 0.2 * (valid_deps / len(entities.dependencies))
    elif entities.total_entities > 0:
        # No dependencies is okay for simple chunks
        score += 0.1

    return round(min(score, 1.0), 2)
```

---

## Unit Testing Requirements

### Test Categories and Minimums

All LLM calls are mocked using `unittest.mock.patch` or `pytest-mock` to avoid real API calls and costs.

| Category | Tests | Description |
|----------|-------|-------------|
| **Happy Path** | 4 | Successful extraction, entities populated, chunk_id attached, confidence > 0 |
| **JSON Parsing** | 6 | Clean JSON, JSON with preamble text, JSON in code block, malformed JSON fallback, nested braces, empty response |
| **Retry Logic** | 4 | Success on first try, success on retry, all retries fail raises ExtractionError, exponential backoff timing |
| **Confidence** | 5 | Perfect score factors, low score for bad naming, zero for empty, partial for mixed, parse failure penalty |
| **Error Handling** | 4 | Missing API key, non-string input TypeError, ExtractionError properties, empty text returns empty entities |
| **Convenience Fn** | 2 | `extract_entities()` returns dict, custom model param forwarded |
| **Logging** | 2 | Extraction start logged, extraction result logged |

### Example Test Code

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.extractor import (
    EntityExtractor, ExtractedEntities, ExtractionError,
    extract_entities,
)


class TestEntityExtractor:
    """Tests for EntityExtractor core. (v0.2.2c)"""

    @patch("src.extractor.ChatOpenAI")
    def test_extract_returns_entities(self, mock_llm_class):
        """Successful extraction returns populated ExtractedEntities."""
        mock_response = Mock()
        mock_response.content = '{"actions": ["Restart_Server"], "states": ["Config_Saved"], "commands": ["systemctl restart"], "warnings": [], "dependencies": [{"action": "Restart_Server", "requires": "Config_Saved"}]}'
        mock_llm_class.return_value.invoke.return_value = mock_response

        extractor = EntityExtractor()
        result = extractor.extract("Restart the server after saving config.")

        assert isinstance(result, ExtractedEntities)
        assert "Restart_Server" in result.actions
        assert result.confidence > 0

    @patch("src.extractor.ChatOpenAI")
    def test_extract_attaches_chunk_id(self, mock_llm_class):
        """chunk_id is attached to returned entities."""
        mock_response = Mock()
        mock_response.content = '{"actions": [], "states": [], "commands": [], "warnings": [], "dependencies": []}'
        mock_llm_class.return_value.invoke.return_value = mock_response

        extractor = EntityExtractor()
        result = extractor.extract("text", chunk_id="chunk-042")
        assert result.chunk_id == "chunk-042"


class TestJSONParsing:
    """Tests for response parsing fallbacks. (v0.2.2c)"""

    @patch("src.extractor.ChatOpenAI")
    def test_parse_json_with_preamble(self, mock_llm_class):
        """JSON embedded in explanatory text is extracted."""
        mock_response = Mock()
        mock_response.content = 'Here are the entities:\n{"actions": ["Deploy"], "states": [], "commands": [], "warnings": [], "dependencies": []}\nDone!'
        mock_llm_class.return_value.invoke.return_value = mock_response

        extractor = EntityExtractor()
        result = extractor.extract("Deploy the app")
        assert "Deploy" in result.actions

    @patch("src.extractor.ChatOpenAI")
    def test_parse_json_in_code_block(self, mock_llm_class):
        """JSON inside markdown code block is extracted."""
        mock_response = Mock()
        mock_response.content = '```json\n{"actions": ["Test"], "states": [], "commands": [], "warnings": [], "dependencies": []}\n```'
        mock_llm_class.return_value.invoke.return_value = mock_response

        extractor = EntityExtractor()
        result = extractor.extract("Test something")
        assert "Test" in result.actions

    @patch("src.extractor.ChatOpenAI")
    def test_parse_total_failure_returns_empty(self, mock_llm_class):
        """Unparseable response returns empty ExtractedEntities."""
        mock_response = Mock()
        mock_response.content = "I cannot extract entities from this text."
        mock_llm_class.return_value.invoke.return_value = mock_response

        extractor = EntityExtractor()
        result = extractor.extract("Some text")
        assert result.is_empty


class TestConfidenceScoring:
    """Tests for confidence computation. (v0.2.2c)"""

    def test_perfect_confidence(self):
        """Well-formed extraction with valid naming gets high confidence."""
        extractor = EntityExtractor.__new__(EntityExtractor)
        entities = ExtractedEntities(
            actions=["Restart_Server"],
            states=["Config_Saved"],
            dependencies=[
                # Using Dependency if available, else dict
            ],
        )
        score = extractor._compute_confidence(entities, parse_succeeded=True)
        assert score >= 0.7

    def test_empty_extraction_low_confidence(self):
        """Empty extraction gets low confidence."""
        extractor = EntityExtractor.__new__(EntityExtractor)
        entities = ExtractedEntities()
        score = extractor._compute_confidence(entities, parse_succeeded=True)
        assert score <= 0.5
```

---

## Logging Requirements

| Level | When | Example Message |
|-------|------|-----------------|
| **INFO** | Extractor initialized | `"EntityExtractor initialized: model=%s, temperature=%.1f"` |
| **INFO** | Extraction complete | `"Extraction complete: chunk_id=%s, %d entities, confidence=%.2f"` |
| **DEBUG** | LLM invoked | `"LLM invoked: prompt=%d chars, model=%s"` |
| **DEBUG** | JSON parsed | `"JSON parsed successfully on attempt %d"` |
| **WARNING** | JSON parse failed, using fallback | `"JSON parse failed, trying regex extraction: %s"` |
| **WARNING** | Low confidence extraction | `"Low confidence extraction (%.2f): chunk_id=%s"` |
| **ERROR** | All retries exhausted | `"Extraction failed after %d retries: %s"` |
| **ERROR** | API key missing | `"OPENAI_API_KEY not set in environment"` |

---

## Acceptance Criteria

- [ ] `EntityExtractor` class implemented with `__init__`, `extract`, `_invoke_llm`, `_parse_response`, `_compute_confidence`
- [ ] LLM invocation via LangChain `ChatOpenAI` with configurable model and temperature
- [ ] Retry logic with configurable `max_retries` and exponential backoff
- [ ] JSON parsing fallback chain: direct → regex → code block → empty
- [ ] Schema validation applied to parsed output
- [ ] Confidence score computed from parse success, naming compliance, non-emptiness, and dependency validity
- [ ] `chunk_id` and `raw_response` attached to returned `ExtractedEntities`
- [ ] `ExtractionError` raised with context after all retries fail
- [ ] `extract_entities()` convenience function returns dict
- [ ] ≥27 tests pass (all mocked, no real API calls)
- [ ] All logging uses `%s`-style formatting
- [ ] No `print()` statements

---

## Dependencies

**Must be completed before v0.2.2c:**
- v0.2.2a — Entity Data Model (`ExtractedEntities`, `Dependency`)
- v0.2.2b — Extraction Prompt Engineering (`PromptRegistry`, `validate_extraction_output`)

**External dependencies:**
- `langchain-openai` (installed in v0.1.1b)
- `OPENAI_API_KEY` environment variable

---

## Outputs to Next Sub-Part

**For v0.2.2d — Batch Extraction:**
- `EntityExtractor.extract()` processes single chunks
- Batch processing wraps multiple `extract()` calls

**For v0.2.3 — CNL Synthesis:**
- `ExtractedEntities.to_dict()` is the input format for the synthesizer

---

## Decision Log

| Decision | Rationale | Status |
|----------|-----------|--------|
| Exponential backoff for retries | Prevents rate limit hammering; industry standard for API calls | ✅ Approved |
| Three-stage JSON fallback | LLMs sometimes add explanatory text around JSON; regex extraction recovers most failures | ✅ Approved |
| Confidence as weighted sum | Simple, interpretable scoring; weights can be tuned via config in future | ✅ Approved |
| Return empty entities instead of raising on parse failure | Pipeline should degrade gracefully; caller can filter by confidence | ✅ Approved |
| Mock all LLM calls in tests | Avoids API costs, ensures deterministic tests, enables CI without credentials | ✅ Approved |
