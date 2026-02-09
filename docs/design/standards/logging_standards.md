# Logging Standards — Haiku Protocol

<aside>

**Scope:** All phases (v0.1.x through v0.4.x)

**Status:** Active

**Applies To:** All Python source in `src/`, `tests/`, and CLI scripts

**Deliverable:** Standardized logging framework, format specification, level guidelines, and operational patterns for the entire project

</aside>

---

## Purpose

This document establishes logging standards for the Haiku Protocol project. Consistent, structured logging enables debugging during development, observability in production, and traceability when investigating compression pipeline behavior.

---

## Logging Philosophy

### Core Principles

1. **Log for the reader, not the writer.** A log message should be understandable by someone who didn't write the code.
2. **Structured over freeform.** Every log entry should carry context (module, function, relevant IDs) — not just a bare string.
3. **Levels are contracts.** Each log level has a specific meaning. Misusing levels erodes trust in logs.
4. **No secrets in logs.** API keys, passwords, and PII must never appear in log output at any level.
5. **Logging is not debugging.** Use a debugger for step-through investigation. Logs capture *what happened* for later review.

---

## Framework

### Standard Library `logging` Module

Haiku Protocol uses Python's built-in `logging` module. No third-party logging libraries (loguru, structlog) are required, keeping the dependency footprint minimal.

### Why `logging` (not print, not loguru)

| Approach | Verdict | Rationale |
|----------|---------|-----------|
| `print()` | Prohibited in `src/` | No levels, no formatting, no routing, mixes with user output |
| `logging` (stdlib) | Required | Built-in, zero dependencies, industry standard, configurable |
| `loguru` | Not used | Unnecessary dependency for this project scale |
| `structlog` | Not used | Overkill for CLI/Streamlit application |

**Exception:** `print()` is acceptable in:
- Streamlit UI code (`app.py`) for user-facing output via `st.write()`
- CLI scripts run directly (`if __name__ == "__main__"` blocks)
- Test output (via `pytest -s` or `capsys`)

---

## Logger Setup

### Per-Module Logger Pattern

Every module in `src/` must create its own logger using `__name__`:

```python
"""encoder.py - Haiku Protocol Compression Pipeline"""

import logging

logger = logging.getLogger(__name__)
```

### Project-Level Configuration

A single configuration point initializes the logging system. Place this in `src/logging_config.py`:

```python
"""
logging_config.py - Centralized Logging Configuration
======================================================

Configures logging for the entire Haiku Protocol application.
Called once at application startup (in app.py or main entry point).

Usage:
    from src.logging_config import setup_logging
    setup_logging()  # Call once at startup
"""

import logging
import os
import sys
from pathlib import Path


def setup_logging(
    level: str = None,
    log_file: str = None,
    log_format: str = None
) -> None:
    """
    Configure project-wide logging.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
               Defaults to LOG_LEVEL env var, then INFO.
        log_file: Optional file path for file logging.
                  Defaults to None (stdout only).
        log_format: Optional custom format string.
                    Defaults to standard format below.
    """
    # Resolve level from argument, env var, or default
    level = level or os.getenv("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Standard format
    if log_format is None:
        log_format = (
            "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | "
            "%(message)s"
        )

    # Date format
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    handlers = []

    # Console handler (always)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    handlers.append(console_handler)

    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        handlers.append(file_handler)

    # Apply configuration
    logging.basicConfig(
        level=numeric_level,
        handlers=handlers,
        force=True  # Override any existing config
    )

    # Silence noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # Log the configuration itself
    root_logger = logging.getLogger()
    root_logger.debug(
        "Logging configured: level=%s, file=%s", level, log_file or "stdout"
    )
```

---

## Log Format

### Standard Format

```
2026-02-05 14:32:01 | INFO     | src.encoder:encode:45 | Compression started for document (2340 tokens)
2026-02-05 14:32:02 | DEBUG    | src.chunker:chunk:78 | Chunking with strategy=semantic, chunk_size=512
2026-02-05 14:32:03 | WARNING  | src.validator:validate:112 | Semantic similarity below threshold (0.68 < 0.70)
2026-02-05 14:32:03 | ERROR    | src.synthesizer:synthesize:95 | CNL generation failed: invalid grammar rule
```

### Format Fields

| Field | Format Code | Example | Purpose |
|-------|-------------|---------|---------|
| Timestamp | `%(asctime)s` | `2026-02-05 14:32:01` | When it happened |
| Level | `%(levelname)-8s` | `INFO    ` | Severity (padded to 8 chars) |
| Module | `%(name)s` | `src.encoder` | Which module logged it |
| Function | `%(funcName)s` | `encode` | Which function logged it |
| Line | `%(lineno)d` | `45` | Source line number |
| Message | `%(message)s` | `Compression started...` | What happened |

---

## Log Levels — Usage Contract

### Level Definitions

```
┌────────────┬────────────────────────────────────────────────────────────┐
│   Level    │ When to Use                                               │
├────────────┼────────────────────────────────────────────────────────────┤
│ CRITICAL   │ Application cannot continue. Data loss or corruption      │
│            │ is imminent. Requires immediate human intervention.        │
│            │                                                            │
│ ERROR      │ An operation failed. The current request/task cannot       │
│            │ complete, but the application can continue running.        │
│            │                                                            │
│ WARNING    │ Something unexpected happened, but the operation           │
│            │ completed. A potential problem that should be reviewed.    │
│            │                                                            │
│ INFO       │ Normal operation milestones. Key events that confirm      │
│            │ the application is working correctly.                      │
│            │                                                            │
│ DEBUG      │ Detailed diagnostic information for developers.           │
│            │ Variable values, intermediate state, decision points.     │
└────────────┴────────────────────────────────────────────────────────────┘
```

### Level Examples — Haiku Protocol Specific

```python
import logging

logger = logging.getLogger(__name__)

# CRITICAL — Application is broken
logger.critical("Configuration file corrupted — cannot start application")
logger.critical("Database connection lost during write — data may be inconsistent")

# ERROR — Operation failed
logger.error("API call failed after 3 retries: %s", error_message)
logger.error("CNL synthesis produced empty output for chunk %d", chunk_id)
logger.error("Validation failed: compression ratio %.2f below minimum 0.10", ratio)

# WARNING — Unexpected but recoverable
logger.warning("API response slower than expected (%.1fs > 5s threshold)", elapsed)
logger.warning("Chunk %d exceeds maximum size (%d > %d tokens)", chunk_id, size, max_size)
logger.warning("Semantic similarity %.2f below target %.2f", actual, target)

# INFO — Key operation milestones
logger.info("Compression started: document=%d tokens, strategy=%s", token_count, strategy)
logger.info("Compression complete: ratio=%.2f%%, time=%.1fs", ratio * 100, elapsed)
logger.info("Loaded %d chunks from document", len(chunks))
logger.info("API connection validated successfully")

# DEBUG — Developer diagnostics
logger.debug("Chunk boundaries: %s", [(c.start_char, c.end_char) for c in chunks])
logger.debug("Entity extraction found %d entities in chunk %d", len(entities), chunk_id)
logger.debug("Config loaded: model=%s, debug=%s", model, debug)
logger.debug("Raw API response: %s", response.content[:200])
```

---

## Log Message Best Practices

### Message Formatting

Use `%s`-style formatting (lazy evaluation), not f-strings:

```python
# Good — lazy evaluation, only formatted if level is active
logger.debug("Processing chunk %d of %d", current, total)
logger.info("Compression ratio: %.2f%%", ratio * 100)
logger.error("API error (status=%d): %s", status_code, message)

# Bad — f-string always evaluated, even if level is filtered
logger.debug(f"Processing chunk {current} of {total}")
logger.info(f"Compression ratio: {ratio * 100:.2f}%")
```

### Message Content Rules

| Do | Don't |
|----|-------|
| Include relevant IDs: `"Chunk %d processed"` | Log bare strings: `"Done"` |
| Include measurements: `"Compressed in %.2fs"` | Log without context: `"Slow"` |
| Use consistent terminology from the codebase | Invent new terms in log messages |
| Log at function boundaries (entry/exit) for DEBUG | Log every line of execution |
| Include error details: `"Failed: %s", str(e)` | Swallow exceptions silently |

### What to Log at Each Level

```
Application Startup:
  INFO  — "Haiku Protocol v0.1.0 starting"
  INFO  — "Configuration loaded: model=gpt-4"
  DEBUG — "Environment: Python 3.11.2, langchain 0.1.14"

Compression Pipeline:
  INFO  — "Compression started: 2340 tokens"
  DEBUG — "Chunking: strategy=semantic, chunk_size=512"
  DEBUG — "Chunk 1: 498 tokens, Chunk 2: 512 tokens, ..."
  DEBUG — "Entities extracted: 14 nouns, 8 verbs, 3 relations"
  DEBUG — "CNL synthesis: 5 statements generated"
  INFO  — "Compression complete: ratio=35%, 2340→819 tokens, 1.2s"

Validation:
  INFO  — "Validation started"
  DEBUG — "Semantic similarity: 0.87"
  DEBUG — "Information retention: 0.92"
  WARNING — "Compression ratio 0.09 below 0.10 minimum"
  INFO  — "Validation passed: confidence=0.89"

Error Scenarios:
  WARNING — "API rate limit approaching (89/100 requests this minute)"
  ERROR — "API call failed: 401 Unauthorized"
  ERROR — "Chunk 3 produced empty CNL output, skipping"
  CRITICAL — ".env file missing and no environment variables set"
```

---

## Security — Never Log Secrets

### Prohibited Content

The following must NEVER appear in log output at any level:

- API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
- Passwords or tokens
- User personal data (names, emails)
- Full file paths containing usernames (use relative paths)

### Masking Pattern

```python
def mask_api_key(key: str) -> str:
    """Mask API key for safe logging. Shows first 6 and last 4 chars."""
    if not key or len(key) < 12:
        return "***"
    return f"{key[:6]}...{key[-4:]}"

# Usage
logger.info("API configured: key=%s, model=%s", mask_api_key(api_key), model)
# Output: API configured: key=sk-pro...ef0a, model=gpt-4
```

---

## Environment-Based Configuration

### Development vs Production

| Setting | Development | Production |
|---------|------------|------------|
| `LOG_LEVEL` | `DEBUG` | `INFO` or `WARNING` |
| Console output | Yes | Yes |
| File output | Optional | Recommended |
| Third-party loggers | `DEBUG` | `WARNING` |
| Log format | Standard (human-readable) | Standard (human-readable) |

### .env Configuration

```bash
# Development
LOG_LEVEL=DEBUG

# Production / Demo
LOG_LEVEL=INFO
```

---

## Module-Specific Logging Patterns

### Encoder (src/encoder.py)

```python
logger = logging.getLogger(__name__)

class HaikuEncoder:
    def encode(self, document: str) -> str:
        logger.info(
            "Compression started: document_length=%d chars",
            len(document)
        )

        chunks = self.chunker.chunk(document)
        logger.debug("Document split into %d chunks", len(chunks))

        # ... processing ...

        logger.info(
            "Compression complete: ratio=%.2f%%, original=%d, compressed=%d, time=%.2fs",
            metrics.compression_ratio * 100,
            metrics.original_tokens,
            metrics.compressed_tokens,
            metrics.processing_time_ms / 1000
        )
        return result
```

### Config (src/config.py)

```python
logger = logging.getLogger(__name__)

class Config:
    @classmethod
    def validate(cls) -> bool:
        logger.debug("Starting configuration validation")

        api_key = cls.get_openai_api_key()
        if not api_key:
            logger.error("OPENAI_API_KEY is required but empty")
            return False

        # Never log the actual key
        logger.debug("API key present: %s", mask_api_key(api_key))
        logger.info("Configuration validated successfully")
        return True
```

### Validator (src/validator.py)

```python
logger = logging.getLogger(__name__)

class HaikuValidator:
    def compute_metrics(self, original: str, compressed: str) -> CompressionMetrics:
        logger.info("Computing compression metrics")

        ratio = (orig_tokens - comp_tokens) / orig_tokens
        logger.debug(
            "Token counts: original=%d, compressed=%d, ratio=%.4f",
            orig_tokens, comp_tokens, ratio
        )

        if ratio < 0.10:
            logger.warning(
                "Compression ratio %.2f%% below minimum threshold 10%%",
                ratio * 100
            )

        return metrics
```

---

## Logging in Tests

### Test Logging Configuration

Tests should use `caplog` fixture to capture and assert log output:

```python
import logging

def test_encoder_logs_start_message(caplog, encoder, sample_short_text):
    """Encoder logs INFO message when compression starts."""
    with caplog.at_level(logging.INFO):
        encoder.encode(sample_short_text)

    assert "Compression started" in caplog.text


def test_validator_warns_on_low_ratio(caplog, validator):
    """Validator logs WARNING when compression ratio is too low."""
    with caplog.at_level(logging.WARNING):
        validator.compute_metrics(original="short", compressed="short text here")

    assert "below minimum threshold" in caplog.text
    assert caplog.records[0].levelname == "WARNING"
```

### Do Not Use `print()` in Tests

```python
# Bad — print output mixes with test runner output
def test_something():
    print("Starting test...")  # No
    result = do_thing()
    print(f"Result: {result}")  # No

# Good — use logging and caplog
def test_something(caplog):
    with caplog.at_level(logging.DEBUG):
        result = do_thing()
    assert "expected message" in caplog.text
```

---

## Use Cases

### Use Case 1: Debugging a Failed Compression

```
# Set LOG_LEVEL=DEBUG in .env, then run:

2026-02-05 14:32:01 | INFO     | src.encoder:encode:45 | Compression started: document_length=2340 chars
2026-02-05 14:32:01 | DEBUG    | src.chunker:chunk:78 | Chunking: strategy=semantic, chunk_size=512
2026-02-05 14:32:01 | DEBUG    | src.chunker:chunk:92 | Chunk 0: 498 tokens (chars 0-1023)
2026-02-05 14:32:01 | DEBUG    | src.chunker:chunk:92 | Chunk 1: 512 tokens (chars 974-2048)
2026-02-05 14:32:02 | DEBUG    | src.extractor:extract:55 | Chunk 0: 14 entities extracted
2026-02-05 14:32:02 | DEBUG    | src.extractor:extract:55 | Chunk 1: 11 entities extracted
2026-02-05 14:32:02 | ERROR    | src.synthesizer:synthesize:95 | CNL generation failed for chunk 1: grammar rule violation
2026-02-05 14:32:02 | ERROR    | src.encoder:encode:72 | Compression aborted: synthesis failed on chunk 1

# Developer can now see exactly which chunk failed and why.
```

### Use Case 2: Monitoring Streamlit Demo Performance

```
# Set LOG_LEVEL=INFO, observe during user demo:

2026-02-05 15:00:01 | INFO     | src.encoder:encode:45 | Compression started: document_length=5200 chars
2026-02-05 15:00:04 | INFO     | src.encoder:encode:89 | Compression complete: ratio=42.3%, 5200→3000 tokens, 3.1s
2026-02-05 15:00:04 | INFO     | src.validator:validate:55 | Validation passed: confidence=0.91

# Quick confirmation that everything worked without DEBUG noise.
```

---

## Workflow: Adding Logging to a Module

```
1. Import logging at top of module
       │
       ▼
2. Create module logger: logger = logging.getLogger(__name__)
       │
       ▼
3. Add INFO logs at method entry/exit (key operations)
       │
       ▼
4. Add DEBUG logs for intermediate state and decisions
       │
       ▼
5. Add WARNING logs for recoverable anomalies
       │
       ▼
6. Add ERROR logs for operation failures
       │
       ▼
7. Verify no secrets are logged (grep for API_KEY, password, etc.)
       │
       ▼
8. Test log output with: LOG_LEVEL=DEBUG pytest -s
```

---

## Dos and Don'ts

### Do

- Use `logging.getLogger(__name__)` in every module
- Use `%s`-style formatting for lazy evaluation
- Log at function entry (INFO) and exit (INFO) for key operations
- Include relevant context (IDs, counts, measurements) in messages
- Mask secrets before logging
- Test log output with `caplog` in pytest
- Configure logging once at application startup via `setup_logging()`

### Don't

- Use `print()` for operational logging in `src/` modules
- Use f-strings in log messages (defeats lazy evaluation)
- Log at DEBUG level in tight loops (performance impact)
- Log full API responses (may contain sensitive data, large payloads)
- Log the same information at multiple levels
- Use `logging.basicConfig()` in individual modules (only in `setup_logging()`)
- Create multiple logger instances in the same module
- Catch and silently swallow exceptions without logging

---

## Acceptance Criteria (for this document)

- [ ] Every `src/` module uses `logging.getLogger(__name__)`
- [ ] No `print()` calls in `src/` modules for operational logging
- [ ] `src/logging_config.py` exists with `setup_logging()` function
- [ ] `LOG_LEVEL` environment variable controls verbosity
- [ ] Log format includes timestamp, level, module, function, line, message
- [ ] API keys and secrets are masked in all log output
- [ ] INFO logs mark key operation milestones (start, complete, fail)
- [ ] DEBUG logs provide diagnostic detail without excessive volume
- [ ] WARNING logs flag recoverable anomalies
- [ ] ERROR logs document operation failures with context
- [ ] Tests verify log output using `caplog` fixture
- [ ] Third-party library loggers are silenced to WARNING level

---

## Related Documents

- [v0.1.3b — Root Configuration Files](../phase-1/v0.1.3/root_configuration_files.md) — `LOG_LEVEL` environment variable definition
- [v0.1.2a — Environment File Creation](../phase-1/v0.1.2/environment_file_creation_and_structure.md) — `.env` structure with DEBUG and LOG_LEVEL
- [v0.1.2c — Configuration Module](../phase-1/v0.1.2/configuration_module_implementation.md) — Config class that reads LOG_LEVEL
- [Testing Standards](testing_standards.md) — `caplog` patterns for testing log output
- [Commenting Standards](commenting_standards.md) — When to comment vs. when to log
