# v0.2.4a: Compression Metrics Data Model

## Aside: Metadata Block

| Property | Value |
|----------|-------|
| **Version** | v0.2.4a |
| **Parent** | v0.2.4 — Validation & Metrics |
| **Status** | ⬜ Not Started |
| **Duration** | 10–15 minutes |
| **Deliverable** | `CompressionMetrics` dataclass, `ValidationResult` dataclass, `ValidationConfig` configuration, type definitions, and comprehensive unit tests in `src/validator.py` and `tests/test_validator.py` |

---

## Objective

Define the foundational data structures for the Validation & Metrics module (v0.2.4), the final stage of the Haiku Protocol encoder pipeline. Establish pure, stateless data models for holding compression measurements, validation results, and configuration—enabling consistent, serializable quantification of compression quality across the pipeline.

This sub-part creates the **measurement contract** for v0.2.4: compress input documents to CNL, count tokens before and after, calculate compression ratio, and report whether the compression meets minimum thresholds. CompressionMetrics holds the "what," ValidationResult communicates the "whether," and ValidationConfig controls the "how" (thresholds and tokenizer settings).

---

## User Stories

### Story 1: Pipeline Reports Compression Quality
**As a** pipeline orchestrator
**I want to** receive compression metrics (token counts, ratio, savings) in a standardized structure
**So that** I can log results, make validation decisions, and compare compression across different documents

**Acceptance:**
- Metrics object constructed from original and compressed token counts
- All calculated fields (ratio, savings, percent) derived automatically
- Metrics serializable to JSON for logging/storage
- Ratio calculated as `1 - (compressed / original)`, range 0.0–1.0
- Savings calculated as `original - compressed` (absolute token count)

### Story 2: Validation Gates Compression Output
**As a** pipeline validator
**I want to** check whether compression achieves a configurable minimum ratio threshold
**So that** low-quality compressions are rejected before downstream use

**Acceptance:**
- ValidationResult returned from validation check
- Result indicates pass/fail with human-readable message
- Threshold configurable via ValidationConfig
- Config includes tokenizer model name to ensure consistency
- Precision of ratio and percentage output is configurable

---

## Data Model Design

### CompressionMetrics Dataclass

The primary container for compression quality measurements. Holds the results of comparing original document text against its compressed CNL representation.

```python
from dataclasses import dataclass, field
from typing import Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class CompressionMetrics:
    """Container for compression quality measurements.

    Holds the results of comparing original document text against
    its compressed CNL representation. This is the primary output
    of the validation module and the quantitative evidence for the
    Haiku Protocol's compression thesis.

    Attributes:
        original_tokens (int): Token count of the original document text.
            Counted using tiktoken with cl100k_base encoding (GPT-4).
        compressed_tokens (int): Token count of the compressed CNL string.
        compression_ratio (float): Fraction of tokens saved, calculated as
            1 - (compressed_tokens / original_tokens). Range: 0.0–1.0.
            A ratio of 0.5 means 50% of tokens were removed.
        token_savings (int): Absolute count of tokens saved
            (original_tokens - compressed_tokens).
        savings_percent (str): Human-readable percentage string (e.g., "56%").
        original_chars (int): Character count of original text. Default: 0.
        compressed_chars (int): Character count of compressed text. Default: 0.
    """
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    token_savings: int
    savings_percent: str
    original_chars: int = 0
    compressed_chars: int = 0

    def to_dict(self) -> dict:
        """Convert metrics to JSON-serializable dictionary.

        Returns a dictionary representation excluding raw original/compressed
        text to keep the serialized payload lightweight.

        Returns:
            dict: Keys include original_tokens, compressed_tokens, compression_ratio,
                token_savings, savings_percent, original_chars, compressed_chars.

        Example:
            >>> metrics = CompressionMetrics(
            ...     original_tokens=100,
            ...     compressed_tokens=44,
            ...     compression_ratio=0.56,
            ...     token_savings=56,
            ...     savings_percent="56%",
            ...     original_chars=500,
            ...     compressed_chars=220
            ... )
            >>> metrics.to_dict()
            {
                'original_tokens': 100,
                'compressed_tokens': 44,
                'compression_ratio': 0.56,
                'token_savings': 56,
                'savings_percent': '56%',
                'original_chars': 500,
                'compressed_chars': 220
            }
        """
        logger.debug(
            "CompressionMetrics serialized: original=%d, compressed=%d",
            self.original_tokens,
            self.compressed_tokens
        )
        return {
            'original_tokens': self.original_tokens,
            'compressed_tokens': self.compressed_tokens,
            'compression_ratio': self.compression_ratio,
            'token_savings': self.token_savings,
            'savings_percent': self.savings_percent,
            'original_chars': self.original_chars,
            'compressed_chars': self.compressed_chars,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CompressionMetrics':
        """Deserialize metrics from dictionary.

        Reconstructs a CompressionMetrics instance from a dictionary.
        Handles optional fields (original_chars, compressed_chars) with defaults.

        Args:
            data (dict): Dictionary with required keys: original_tokens,
                compressed_tokens, compression_ratio, token_savings, savings_percent.
                Optional: original_chars, compressed_chars.

        Returns:
            CompressionMetrics: Reconstructed instance.

        Raises:
            KeyError: If required keys are missing from data.
            TypeError: If types are invalid (e.g., string for int field).

        Example:
            >>> data = {
            ...     'original_tokens': 100,
            ...     'compressed_tokens': 44,
            ...     'compression_ratio': 0.56,
            ...     'token_savings': 56,
            ...     'savings_percent': '56%',
            ...     'original_chars': 500,
            ...     'compressed_chars': 220
            ... }
            >>> metrics = CompressionMetrics.from_dict(data)
            >>> metrics.compression_ratio
            0.56
        """
        return cls(
            original_tokens=data['original_tokens'],
            compressed_tokens=data['compressed_tokens'],
            compression_ratio=data['compression_ratio'],
            token_savings=data['token_savings'],
            savings_percent=data['savings_percent'],
            original_chars=data.get('original_chars', 0),
            compressed_chars=data.get('compressed_chars', 0),
        )

    def __repr__(self) -> str:
        """Human-readable representation.

        Provides a compact, at-a-glance summary of compression results.

        Returns:
            str: Format:
                CompressionMetrics(ratio=0.56, savings=56%, tokens: 100→44)

        Example:
            >>> metrics = CompressionMetrics(
            ...     original_tokens=100,
            ...     compressed_tokens=44,
            ...     compression_ratio=0.56,
            ...     token_savings=56,
            ...     savings_percent="56%"
            ... )
            >>> repr(metrics)
            'CompressionMetrics(ratio=0.56, savings=56%, tokens: 100→44)'
        """
        return (
            f"CompressionMetrics(ratio={self.compression_ratio}, "
            f"savings={self.savings_percent}, "
            f"tokens: {self.original_tokens}→{self.compressed_tokens})"
        )

    @property
    def is_compressed(self) -> bool:
        """Check if compression actually occurred.

        Returns:
            bool: True if compression_ratio > 0, False otherwise.
                  Indicates that tokens were removed.

        Example:
            >>> metrics = CompressionMetrics(
            ...     original_tokens=100,
            ...     compressed_tokens=44,
            ...     compression_ratio=0.56,
            ...     token_savings=56,
            ...     savings_percent="56%"
            ... )
            >>> metrics.is_compressed
            True

            >>> metrics_no_compression = CompressionMetrics(
            ...     original_tokens=100,
            ...     compressed_tokens=100,
            ...     compression_ratio=0.0,
            ...     token_savings=0,
            ...     savings_percent="0%"
            ... )
            >>> metrics_no_compression.is_compressed
            False
        """
        return self.compression_ratio > 0

    def meets_threshold(self, min_ratio: float = 0.3) -> bool:
        """Check if compression ratio meets minimum threshold.

        Args:
            min_ratio (float): Minimum acceptable compression ratio.
                Default 0.3 (30% token reduction required).

        Returns:
            bool: True if self.compression_ratio >= min_ratio.

        Example:
            >>> metrics = CompressionMetrics(
            ...     original_tokens=100,
            ...     compressed_tokens=44,
            ...     compression_ratio=0.56,
            ...     token_savings=56,
            ...     savings_percent="56%"
            ... )
            >>> metrics.meets_threshold(0.3)
            True
            >>> metrics.meets_threshold(0.7)
            False
            >>> metrics.meets_threshold(0.56)
            True  # Equality passes
        """
        return self.compression_ratio >= min_ratio
```

### ValidationResult Dataclass

Result of a compression validation check, returned by the validator to communicate whether compression meets quality thresholds.

```python
@dataclass
class ValidationResult:
    """Result of a compression validation check.

    Returned by CompressionValidator.validate_compression() to
    communicate whether the compression output meets quality thresholds.

    Attributes:
        passed (bool): True if compression meets the minimum ratio threshold.
        compression_ratio (float): The actual compression ratio achieved.
        threshold (float): The minimum ratio that was required.
        message (str): Human-readable summary of the validation result.
        metrics (Optional[CompressionMetrics]): The full CompressionMetrics
            used for validation. May be None if validation failed at an
            earlier stage.
    """
    passed: bool
    compression_ratio: float
    threshold: float
    message: str
    metrics: Optional['CompressionMetrics'] = None

    def to_dict(self) -> dict:
        """Convert validation result to JSON-serializable dictionary.

        Returns:
            dict: Keys include passed, compression_ratio, threshold, message,
                and (if metrics is not None) metrics serialized via to_dict().

        Example:
            >>> metrics = CompressionMetrics(
            ...     original_tokens=100,
            ...     compressed_tokens=44,
            ...     compression_ratio=0.56,
            ...     token_savings=56,
            ...     savings_percent="56%"
            ... )
            >>> result = ValidationResult(
            ...     passed=True,
            ...     compression_ratio=0.56,
            ...     threshold=0.3,
            ...     message="Compression passed validation.",
            ...     metrics=metrics
            ... )
            >>> result.to_dict()
            {
                'passed': True,
                'compression_ratio': 0.56,
                'threshold': 0.3,
                'message': 'Compression passed validation.',
                'metrics': {...}
            }
        """
        result_dict = {
            'passed': self.passed,
            'compression_ratio': self.compression_ratio,
            'threshold': self.threshold,
            'message': self.message,
        }
        if self.metrics is not None:
            result_dict['metrics'] = self.metrics.to_dict()
        return result_dict

    def __repr__(self) -> str:
        """Human-readable representation.

        Provides a one-line status summary.

        Returns:
            str: Format:
                ValidationResult(PASS: ratio=0.56, threshold=0.30)
                or
                ValidationResult(FAIL: ratio=0.25, threshold=0.30)

        Example:
            >>> result_pass = ValidationResult(
            ...     passed=True,
            ...     compression_ratio=0.56,
            ...     threshold=0.3,
            ...     message="Compression passed."
            ... )
            >>> repr(result_pass)
            'ValidationResult(PASS: ratio=0.56, threshold=0.30)'

            >>> result_fail = ValidationResult(
            ...     passed=False,
            ...     compression_ratio=0.25,
            ...     threshold=0.3,
            ...     message="Compression failed threshold."
            ... )
            >>> repr(result_fail)
            'ValidationResult(FAIL: ratio=0.25, threshold=0.30)'
        """
        status = "PASS" if self.passed else "FAIL"
        return (
            f"ValidationResult({status}: "
            f"ratio={self.compression_ratio:.2f}, "
            f"threshold={self.threshold:.2f})"
        )
```

### ValidationConfig Dataclass

Configuration for compression validation behavior, ensuring tokenizer consistency and threshold settings.

```python
@dataclass
class ValidationConfig:
    """Configuration for compression validation behavior.

    Controls how the validator measures and evaluates compression results.
    Ensures tokenizer consistency across runs by specifying the model name
    and allows threshold tuning without code changes.

    Attributes:
        model (str): Model name for tiktoken tokenizer. Default "gpt-4".
            Must be a model supported by tiktoken's encoding_for_model().
            Examples: "gpt-4", "gpt-4-32k", "gpt-3.5-turbo".
        min_compression_ratio (float): Minimum acceptable compression ratio.
            Default 0.3 (30%). Pipeline reports FAIL below this threshold.
            Range: 0.0–1.0.
        ratio_precision (int): Decimal places for compression ratio rounding.
            Default 4. Used internally for consistent calculations.
        percent_precision (int): Decimal places for percentage display.
            Default 0 (integer percentages like "56%", not "56.2%").
    """
    model: str = "gpt-4"
    min_compression_ratio: float = 0.3
    ratio_precision: int = 4
    percent_precision: int = 0

    def __post_init__(self):
        """Validate configuration values after initialization.

        Ensures that:
        - min_compression_ratio is in valid range [0.0, 1.0]
        - ratio_precision is non-negative
        - percent_precision is non-negative
        - model string is non-empty

        Raises:
            ValueError: If any validation fails.
        """
        if not (0.0 <= self.min_compression_ratio <= 1.0):
            raise ValueError(
                f"min_compression_ratio must be in [0.0, 1.0], "
                f"got {self.min_compression_ratio}"
            )
        if self.ratio_precision < 0:
            raise ValueError(
                f"ratio_precision must be non-negative, got {self.ratio_precision}"
            )
        if self.percent_precision < 0:
            raise ValueError(
                f"percent_precision must be non-negative, "
                f"got {self.percent_precision}"
            )
        if not self.model or not isinstance(self.model, str):
            raise ValueError(f"model must be a non-empty string, got {self.model}")
```

### Type Definitions

```python
from typing import Dict, List, Tuple, Union

# Type aliases for clarity in validator signatures
CompressedPair = Tuple[str, str]  # (original_text, compressed_text)
MetricsDict = Dict[str, Union[int, float, str]]
ValidationReportDict = Dict[str, Union[bool, float, str, MetricsDict]]

# Logging constants
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

---

## File Structure

```
src/
├── validator.py
│   ├── logger initialization
│   ├── CompressionMetrics dataclass
│   │   ├── __init__ (implicit via @dataclass)
│   │   ├── to_dict()
│   │   ├── from_dict()
│   │   ├── __repr__()
│   │   ├── is_compressed (property)
│   │   └── meets_threshold()
│   ├── ValidationResult dataclass
│   │   ├── __init__ (implicit via @dataclass)
│   │   ├── to_dict()
│   │   └── __repr__()
│   ├── ValidationConfig dataclass
│   │   ├── __init__ (implicit via @dataclass)
│   │   └── __post_init__()
│   └── Type definitions
│
tests/
└── test_validator.py
    ├── Logger Tests (1 test)
    ├── CompressionMetrics Happy Path Tests (4 tests)
    ├── CompressionMetrics Serialization Tests (4 tests)
    ├── CompressionMetrics Computed Properties Tests (3 tests)
    ├── CompressionMetrics Edge Case Tests (4 tests)
    ├── ValidationResult Tests (3 tests)
    ├── ValidationConfig Tests (2 tests)
    ├── Error Path Tests (2 tests)
    └── Integration Tests (0 tests — reserved for v0.2.4b)
```

---

## Implementation Workflow

```
┌────────────────────────────────────────────────────────────────────┐
│                      v0.2.4a Workflow                              │
└────────────────────────────────────────────────────────────────────┘

Step 1: Define Data Structures
┌─────────────────────────────┐
│  CompressionMetrics         │
│  - 7 fields (int, float,str)│
│  - 5 methods                │
│  - Property: is_compressed  │
└──────────┬──────────────────┘
           │
Step 2: Define ValidationResult
┌─────────────────────────────┐
│  ValidationResult           │
│  - 5 fields                 │
│  - 2 methods                │
│  - Contains metrics         │
└──────────┬──────────────────┘
           │
Step 3: Define ValidationConfig
┌─────────────────────────────┐
│  ValidationConfig           │
│  - 4 fields with defaults   │
│  - __post_init__ validation │
└──────────┬──────────────────┘
           │
Step 4: Write Unit Tests (22+ tests)
┌─────────────────────────────┐
│  test_validator.py          │
│  - Happy path (4)           │
│  - Serialization (4)        │
│  - Computed props (3)       │
│  - Edge cases (4)           │
│  - ValidationResult (3)     │
│  - ValidationConfig (2)     │
│  - Error paths (2)          │
│  - Logger (1)               │
└──────────┬──────────────────┘
           │
Step 5: Verify Coverage & Imports
┌─────────────────────────────┐
│  - All tests passing        │
│  - from_dict() round-trips  │
│  - Logger initialized       │
│  - Types importable         │
└─────────────────────────────┘

Timeline: 10–15 minutes
Deliverable: src/validator.py + tests/test_validator.py
```

---

## Unit Testing Requirements

### Test Categories & Specifications

| Category | # Tests | Description | Test Names & Logic |
|----------|---------|-------------|-------------------|
| **Happy Path** | 4 | Basic construction, field access, defaults, repr | `test_compression_metrics_construction`, `test_compression_metrics_field_access`, `test_compression_metrics_defaults`, `test_compression_metrics_repr` |
| **Serialization** | 4 | `to_dict()` keys, `from_dict()` roundtrip, JSON, missing optional fields | `test_metrics_to_dict_keys`, `test_metrics_from_dict_roundtrip`, `test_metrics_json_compatibility`, `test_metrics_from_dict_missing_optional` |
| **Computed Properties** | 3 | `is_compressed` True/False, `meets_threshold()` True/False/edge | `test_is_compressed_true`, `test_is_compressed_false`, `test_meets_threshold_variations` |
| **ValidationResult** | 3 | Construction, `to_dict()`, repr with pass/fail | `test_validation_result_construction`, `test_validation_result_to_dict`, `test_validation_result_repr` |
| **ValidationConfig** | 2 | Default values, custom overrides | `test_validation_config_defaults`, `test_validation_config_custom` |
| **Edge Cases** | 4 | Zero tokens, zero ratio, 100% compression, negative savings | `test_metrics_zero_tokens`, `test_metrics_zero_ratio`, `test_metrics_full_compression`, `test_metrics_negative_savings` |
| **Logging** | 1 | Logger initialized with `__name__` | `test_logger_initialized` |
| **Error Paths** | 2 | `from_dict()` missing required field, invalid types | `test_from_dict_missing_required`, `test_from_dict_invalid_type` |

**Total: 23 tests**

### Test Naming Convention

Tests follow the pattern: `test_<dataclass>_<aspect>`

Examples:
- `test_compression_metrics_construction` — Creates CompressionMetrics successfully
- `test_metrics_to_dict_keys` — Verifies to_dict() returns correct keys
- `test_is_compressed_true` — Tests is_compressed property when ratio > 0
- `test_validation_result_repr` — Checks __repr__() formatting

### Example Test Code

```python
import pytest
from src.validator import (
    CompressionMetrics,
    ValidationResult,
    ValidationConfig,
)
import logging
import json


# ============================================================================
# Logger Tests
# ============================================================================

def test_logger_initialized():
    """Logger should be initialized with __name__."""
    from src import validator
    assert hasattr(validator, 'logger')
    assert validator.logger.name == 'src.validator'


# ============================================================================
# CompressionMetrics Happy Path Tests
# ============================================================================

def test_compression_metrics_construction():
    """CompressionMetrics should construct with required fields."""
    metrics = CompressionMetrics(
        original_tokens=100,
        compressed_tokens=44,
        compression_ratio=0.56,
        token_savings=56,
        savings_percent="56%",
    )
    assert metrics.original_tokens == 100
    assert metrics.compressed_tokens == 44
    assert metrics.compression_ratio == 0.56
    assert metrics.token_savings == 56
    assert metrics.savings_percent == "56%"


def test_compression_metrics_field_access():
    """All fields should be accessible after construction."""
    metrics = CompressionMetrics(
        original_tokens=1000,
        compressed_tokens=300,
        compression_ratio=0.7,
        token_savings=700,
        savings_percent="70%",
        original_chars=5000,
        compressed_chars=1500,
    )
    assert metrics.original_chars == 5000
    assert metrics.compressed_chars == 1500


def test_compression_metrics_defaults():
    """Optional fields (original_chars, compressed_chars) default to 0."""
    metrics = CompressionMetrics(
        original_tokens=100,
        compressed_tokens=44,
        compression_ratio=0.56,
        token_savings=56,
        savings_percent="56%",
    )
    assert metrics.original_chars == 0
    assert metrics.compressed_chars == 0


def test_compression_metrics_repr():
    """__repr__() should return human-readable format."""
    metrics = CompressionMetrics(
        original_tokens=100,
        compressed_tokens=44,
        compression_ratio=0.56,
        token_savings=56,
        savings_percent="56%",
    )
    expected = "CompressionMetrics(ratio=0.56, savings=56%, tokens: 100→44)"
    assert repr(metrics) == expected


# ============================================================================
# CompressionMetrics Serialization Tests
# ============================================================================

def test_metrics_to_dict_keys():
    """to_dict() should return all required keys."""
    metrics = CompressionMetrics(
        original_tokens=100,
        compressed_tokens=44,
        compression_ratio=0.56,
        token_savings=56,
        savings_percent="56%",
        original_chars=500,
        compressed_chars=220,
    )
    result = metrics.to_dict()
    required_keys = {
        'original_tokens', 'compressed_tokens', 'compression_ratio',
        'token_savings', 'savings_percent', 'original_chars', 'compressed_chars'
    }
    assert set(result.keys()) == required_keys


def test_metrics_from_dict_roundtrip():
    """from_dict() should reconstruct metrics from to_dict() output."""
    original = CompressionMetrics(
        original_tokens=100,
        compressed_tokens=44,
        compression_ratio=0.56,
        token_savings=56,
        savings_percent="56%",
        original_chars=500,
        compressed_chars=220,
    )
    serialized = original.to_dict()
    reconstructed = CompressionMetrics.from_dict(serialized)
    assert reconstructed.original_tokens == original.original_tokens
    assert reconstructed.compressed_tokens == original.compressed_tokens
    assert reconstructed.compression_ratio == original.compression_ratio
    assert reconstructed.token_savings == original.token_savings
    assert reconstructed.savings_percent == original.savings_percent
    assert reconstructed.original_chars == original.original_chars
    assert reconstructed.compressed_chars == original.compressed_chars


def test_metrics_json_compatibility():
    """to_dict() output should be JSON-serializable."""
    metrics = CompressionMetrics(
        original_tokens=100,
        compressed_tokens=44,
        compression_ratio=0.56,
        token_savings=56,
        savings_percent="56%",
    )
    result_dict = metrics.to_dict()
    json_str = json.dumps(result_dict)
    parsed = json.loads(json_str)
    assert parsed['compression_ratio'] == 0.56
    assert parsed['savings_percent'] == "56%"


def test_metrics_from_dict_missing_optional():
    """from_dict() should handle missing optional fields with defaults."""
    data = {
        'original_tokens': 100,
        'compressed_tokens': 44,
        'compression_ratio': 0.56,
        'token_savings': 56,
        'savings_percent': "56%",
        # original_chars and compressed_chars omitted
    }
    metrics = CompressionMetrics.from_dict(data)
    assert metrics.original_chars == 0
    assert metrics.compressed_chars == 0


# ============================================================================
# CompressionMetrics Computed Properties Tests
# ============================================================================

def test_is_compressed_true():
    """is_compressed should return True when compression_ratio > 0."""
    metrics = CompressionMetrics(
        original_tokens=100,
        compressed_tokens=44,
        compression_ratio=0.56,
        token_savings=56,
        savings_percent="56%",
    )
    assert metrics.is_compressed is True


def test_is_compressed_false():
    """is_compressed should return False when compression_ratio == 0."""
    metrics = CompressionMetrics(
        original_tokens=100,
        compressed_tokens=100,
        compression_ratio=0.0,
        token_savings=0,
        savings_percent="0%",
    )
    assert metrics.is_compressed is False


def test_meets_threshold_variations():
    """meets_threshold() should handle True, False, and edge cases."""
    metrics = CompressionMetrics(
        original_tokens=100,
        compressed_tokens=44,
        compression_ratio=0.56,
        token_savings=56,
        savings_percent="56%",
    )
    # Above threshold
    assert metrics.meets_threshold(0.3) is True
    # Below threshold
    assert metrics.meets_threshold(0.7) is False
    # At threshold (equality passes)
    assert metrics.meets_threshold(0.56) is True
    # Zero threshold
    assert metrics.meets_threshold(0.0) is True


# ============================================================================
# ValidationResult Tests
# ============================================================================

def test_validation_result_construction():
    """ValidationResult should construct with required fields."""
    metrics = CompressionMetrics(
        original_tokens=100,
        compressed_tokens=44,
        compression_ratio=0.56,
        token_savings=56,
        savings_percent="56%",
    )
    result = ValidationResult(
        passed=True,
        compression_ratio=0.56,
        threshold=0.3,
        message="Compression passed validation.",
        metrics=metrics,
    )
    assert result.passed is True
    assert result.compression_ratio == 0.56
    assert result.threshold == 0.3
    assert result.metrics == metrics


def test_validation_result_to_dict():
    """to_dict() should serialize ValidationResult including metrics."""
    metrics = CompressionMetrics(
        original_tokens=100,
        compressed_tokens=44,
        compression_ratio=0.56,
        token_savings=56,
        savings_percent="56%",
    )
    result = ValidationResult(
        passed=True,
        compression_ratio=0.56,
        threshold=0.3,
        message="Validation passed.",
        metrics=metrics,
    )
    result_dict = result.to_dict()
    assert result_dict['passed'] is True
    assert result_dict['compression_ratio'] == 0.56
    assert result_dict['threshold'] == 0.3
    assert 'metrics' in result_dict
    assert result_dict['metrics']['original_tokens'] == 100


def test_validation_result_repr():
    """__repr__() should show status, ratio, and threshold."""
    result_pass = ValidationResult(
        passed=True,
        compression_ratio=0.56,
        threshold=0.30,
        message="Passed.",
    )
    repr_str = repr(result_pass)
    assert "PASS" in repr_str
    assert "0.56" in repr_str
    assert "0.30" in repr_str

    result_fail = ValidationResult(
        passed=False,
        compression_ratio=0.25,
        threshold=0.30,
        message="Failed.",
    )
    repr_str_fail = repr(result_fail)
    assert "FAIL" in repr_str_fail


# ============================================================================
# ValidationConfig Tests
# ============================================================================

def test_validation_config_defaults():
    """ValidationConfig should use sensible defaults."""
    config = ValidationConfig()
    assert config.model == "gpt-4"
    assert config.min_compression_ratio == 0.3
    assert config.ratio_precision == 4
    assert config.percent_precision == 0


def test_validation_config_custom():
    """ValidationConfig should accept custom values."""
    config = ValidationConfig(
        model="gpt-3.5-turbo",
        min_compression_ratio=0.5,
        ratio_precision=2,
        percent_precision=1,
    )
    assert config.model == "gpt-3.5-turbo"
    assert config.min_compression_ratio == 0.5
    assert config.ratio_precision == 2
    assert config.percent_precision == 1


# ============================================================================
# Edge Case Tests
# ============================================================================

def test_metrics_zero_tokens():
    """Metrics with zero original tokens should not crash."""
    metrics = CompressionMetrics(
        original_tokens=0,
        compressed_tokens=0,
        compression_ratio=0.0,
        token_savings=0,
        savings_percent="0%",
    )
    assert metrics.original_tokens == 0
    assert metrics.is_compressed is False


def test_metrics_zero_ratio():
    """Metrics with zero compression ratio represents no compression."""
    metrics = CompressionMetrics(
        original_tokens=100,
        compressed_tokens=100,
        compression_ratio=0.0,
        token_savings=0,
        savings_percent="0%",
    )
    assert metrics.compression_ratio == 0.0
    assert metrics.meets_threshold(0.0) is True
    assert metrics.meets_threshold(0.01) is False


def test_metrics_full_compression():
    """Metrics with ratio 1.0 represents complete compression."""
    metrics = CompressionMetrics(
        original_tokens=100,
        compressed_tokens=0,
        compression_ratio=1.0,
        token_savings=100,
        savings_percent="100%",
    )
    assert metrics.compression_ratio == 1.0
    assert metrics.meets_threshold(1.0) is True


def test_metrics_negative_savings():
    """Metrics with negative savings represents expansion (edge case)."""
    # This should not normally occur but the dataclass should handle it
    metrics = CompressionMetrics(
        original_tokens=100,
        compressed_tokens=150,
        compression_ratio=-0.5,  # Negative because more tokens were added
        token_savings=-50,
        savings_percent="-50%",
    )
    assert metrics.token_savings == -50
    assert metrics.is_compressed is False


# ============================================================================
# Error Path Tests
# ============================================================================

def test_from_dict_missing_required():
    """from_dict() should raise KeyError if required field is missing."""
    incomplete_data = {
        'original_tokens': 100,
        'compressed_tokens': 44,
        # Missing: compression_ratio, token_savings, savings_percent
    }
    with pytest.raises(KeyError):
        CompressionMetrics.from_dict(incomplete_data)


def test_from_dict_invalid_type():
    """from_dict() with invalid types should raise appropriate errors."""
    invalid_data = {
        'original_tokens': "not an int",  # Should be int
        'compressed_tokens': 44,
        'compression_ratio': 0.56,
        'token_savings': 56,
        'savings_percent': "56%",
    }
    # The behavior depends on how strictly validation is implemented.
    # This test should verify the expected behavior (e.g., TypeError or ValueError).
    with pytest.raises((TypeError, ValueError)):
        CompressionMetrics.from_dict(invalid_data)
```

---

## Logging Requirements

| Level | When | Example | Location |
|-------|------|---------|----------|
| **INFO** | Module loaded | `"validator module loaded"` | Top of `src/validator.py` on import |
| **DEBUG** | Metrics created | `"CompressionMetrics created: ratio=%.4f, savings=%s"` | `CompressionMetrics.__init__` (or post_init if using dataclass factory) |
| **DEBUG** | Metrics serialized | `"CompressionMetrics serialized: original=%d, compressed=%d"` | `CompressionMetrics.to_dict()` |
| **DEBUG** | Validation check | `"Validation: ratio=%.4f, threshold=%.2f, passed=%s"` | `validate_compression()` (v0.2.4b) |
| **WARNING** | Zero token input | `"Zero tokens in original text: ratio set to 0.0"` | Token counting logic (v0.2.4b) |

---

## Acceptance Criteria

- [ ] **AC-1**: CompressionMetrics dataclass defined with 7 fields (original_tokens, compressed_tokens, compression_ratio, token_savings, savings_percent, original_chars, compressed_chars)
- [ ] **AC-2**: CompressionMetrics.to_dict() returns JSON-serializable dictionary excluding raw text
- [ ] **AC-3**: CompressionMetrics.from_dict() reconstructs metrics from dictionary, handling optional fields
- [ ] **AC-4**: CompressionMetrics.__repr__() outputs compact format: `CompressionMetrics(ratio=X, savings=Y%, tokens: A→B)`
- [ ] **AC-5**: CompressionMetrics.is_compressed property returns True iff compression_ratio > 0
- [ ] **AC-6**: CompressionMetrics.meets_threshold(min_ratio) returns True iff compression_ratio >= min_ratio
- [ ] **AC-7**: ValidationResult dataclass defined with 5 fields (passed, compression_ratio, threshold, message, metrics)
- [ ] **AC-8**: ValidationResult.to_dict() serializes including nested metrics
- [ ] **AC-9**: ValidationResult.__repr__() outputs status line: `ValidationResult(PASS/FAIL: ratio=X, threshold=Y)`
- [ ] **AC-10**: ValidationConfig dataclass defined with 4 fields and sensible defaults (model="gpt-4", min_compression_ratio=0.3, ratio_precision=4, percent_precision=0)
- [ ] **AC-11**: ValidationConfig.__post_init__() validates that min_compression_ratio in [0.0, 1.0] and precision fields are non-negative
- [ ] **AC-12**: Unit tests file (`tests/test_validator.py`) contains 23+ passing tests covering all categories
- [ ] **AC-13**: Logger initialized at module level with `__name__`
- [ ] **AC-14**: All dataclasses and type definitions are importable from `src.validator`
- [ ] **AC-15**: Serialization round-trips (to_dict → from_dict) preserve all values
- [ ] **AC-16**: Edge cases (zero tokens, zero ratio, 100% compression, negative savings) handled without errors

---

## Limitations & Constraints

1. **Tokenizer Consistency**: CompressionMetrics assumes tiktoken with cl100k_base (GPT-4 encoding) is used for token counting. Future support for multiple tokenizers is deferred to v0.3.0+.

2. **No Text Storage in Serialization**: CompressionMetrics.to_dict() excludes raw original and compressed text to keep serialized payloads lightweight. Original text remains available upstream in the pipeline.

3. **No Side Effects**: All dataclasses are pure, stateless containers. No API calls, file I/O, or external state modifications.

4. **Edge Case Handling**: Modules gracefully handle empty strings, None values, and whitespace-only input by applying conservative defaults (ratio=0.0, savings=0) rather than crashing.

5. **Precision Limits**: Compression ratio rounded to 4 decimal places by default; percentage display rounded to nearest integer. Floating-point comparison (e.g., in meets_threshold) uses `>=` to avoid strict equality issues.

6. **No Upstream Dependencies**: ValidationResult and ValidationConfig do not make decisions about compression; they only hold data and configuration. Policy decisions (e.g., whether compression is "good enough") are deferred to validator logic in v0.2.4b.

7. **Metrics Always Include Absolute Values**: token_savings and savings_percent are absolute numbers; they may be negative (expansion case) but still represent the quantitative delta.

---

## Dependencies

| Dependency | Version | Usage | Required By |
|------------|---------|-------|-------------|
| **Python** | 3.9+ | Dataclass syntax, typing module | v0.2.4a |
| **tiktoken** | Latest (from requirements.txt) | Token counting in v0.2.4b | Validation logic (not v0.2.4a) |
| **pytest** | Latest (from requirements.txt) | Unit test framework | tests/test_validator.py |
| **v0.1.3c** | — | Source Module Stubs (upstream) | Provides sample document text |

---

## Outputs to Next Sub-Part (v0.2.4b)

**v0.2.4b — CompressionValidator Implementation** receives these interfaces:

1. **CompressionMetrics class**: Importable from `src.validator`
   - Full implementation with all methods
   - Tested and verified serialization

2. **ValidationResult class**: Importable from `src.validator`
   - Full implementation
   - Ready for validator to populate on validation decisions

3. **ValidationConfig class**: Importable from `src.validator`
   - Full implementation with __post_init__ validation
   - Configuration interface for v0.2.4b

4. **Type definitions**: Dict, Tuple, and Union aliases for validator signatures
   - `CompressedPair = Tuple[str, str]`
   - `MetricsDict = Dict[str, Union[int, float, str]]`
   - `ValidationReportDict = Dict[str, Union[bool, float, str, MetricsDict]]`

5. **Logger**: Module logger initialized and available for v0.2.4b to emit DEBUG/WARNING/INFO messages

6. **Serialization interface**: Both CompressionMetrics and ValidationResult tested for JSON round-trip compatibility

---

## Decision Log

| # | Decision | Rationale | Impact |
|---|----------|-----------|--------|
| **D1** | CompressionMetrics excludes raw text from to_dict() | Serialized metrics should be lightweight; original text is available upstream and need not be duplicated in JSON | Reduces payload size; preserves pipeline separation of concerns |
| **D2** | ValidationResult as separate dataclass from metrics | Validation is a **policy decision** (threshold check) distinct from **measurement** (metrics). Decoupling allows CompressionMetrics to be reused in other pipelines | Improves modularity; enables future non-validator uses of metrics |
| **D3** | ValidationConfig includes model name parameter | Ensures tokenizer consistency is configurable without code changes; future support for multi-model pipelines | Enables threshold and tokenizer tuning without modifying validator code |
| **D4** | savings_percent stored as string, not float | Human-readable display value; float compression_ratio is machine-readable equivalent. Avoids redundant formatting logic | Simplifies downstream logging and display; single source of truth (ratio) for calculations |
| **D5** | cl100k_base tokenizer hardcoded in config default | Matches GPT-4 token limits; familiar to users; consistent with Haiku Protocol goals. Multi-model support deferred to v0.3.0+ | Provides stable baseline; allows deferral of tokenizer abstraction |
| **D6** | meets_threshold() uses >= (not >) | Equality case (ratio exactly meets threshold) should pass; edge case handling | Avoids off-by-one issues in validation gates |
| **D7** | is_compressed as property, not method | Follows Python convention for boolean state queries; lighter syntax (metrics.is_compressed vs metrics.is_compressed()) | Improved readability; consistent with Python idioms |
| **D8** | ValidationConfig.__post_init__() validates range | Catch invalid configs early with clear error messages rather than silent failures downstream | Fails fast; prevents invalid configurations from corrupting validation results |

---

## Appendix: Example Usage

```python
# Typical usage flow in v0.2.4b:
from src.validator import CompressionMetrics, ValidationResult, ValidationConfig

# 1. Create configuration
config = ValidationConfig(
    model="gpt-4",
    min_compression_ratio=0.3,
    ratio_precision=4,
    percent_precision=0
)

# 2. Count tokens (v0.2.4b will do this)
original_tokens = 100
compressed_tokens = 44

# 3. Calculate metrics
compression_ratio = 1 - (compressed_tokens / original_tokens)
token_savings = original_tokens - compressed_tokens
savings_percent = f"{round(compression_ratio * 100)}%"

metrics = CompressionMetrics(
    original_tokens=original_tokens,
    compressed_tokens=compressed_tokens,
    compression_ratio=round(compression_ratio, config.ratio_precision),
    token_savings=token_savings,
    savings_percent=savings_percent,
)

# 4. Validate
passed = metrics.meets_threshold(config.min_compression_ratio)
result = ValidationResult(
    passed=passed,
    compression_ratio=metrics.compression_ratio,
    threshold=config.min_compression_ratio,
    message="Compression passed validation." if passed else "Compression failed validation.",
    metrics=metrics
)

# 5. Log or serialize
print(result)  # ValidationResult(PASS: ratio=0.56, threshold=0.30)
result_dict = result.to_dict()
# Result is JSON-serializable for logging/storage
```

---

*End of v0.2.4a Specification*
