# Validator Core Implementation (v0.2.4b)

> **Aside: Metadata Block**
>
> - **Version:** v0.2.4b
> - **Parent Module:** v0.2.4 — Validation & Metrics (Fourth and Final Stage of Encoder Pipeline)
> - **Status:** ⬜ Not Started
> - **Estimated Duration:** 15–20 minutes
> - **Deliverable:** CompressionValidator class with `count_tokens()`, `calculate_metrics()`, `validate_compression()`, `compare_with_baseline()`, and convenience functions in `src/validator.py`
> - **Key Dependencies:** tiktoken, ValidationConfig, CompressionMetrics, ValidationResult data classes
> - **Target Audience:** Core implementation engineers, integration team, validation QA

---

## Objective

Implement the **CompressionValidator** class—the quantitative heart of the Haiku Protocol encoder pipeline. This module measures compression quality through tokenization and validates that encoder output meets configurable thresholds.

The validator provides the empirical evidence for the project's core thesis: *that the Haiku Protocol achieves meaningful compression ratios on procedural documentation while preserving semantic content.*

**Success is defined by:**
1. Accurate token counting using industry-standard tiktoken (GPT-4 cl100k_base encoding)
2. Reliable compression metrics calculation (ratio, savings, percentages)
3. Configurable threshold-based validation
4. Baseline comparison capability for competitive analysis
5. Full test coverage with ≥26 test cases across 8 categories
6. Zero side effects—pure calculation, no I/O or external calls

---

## User Stories

### US-001: As a Pipeline Engineer, I need to measure compression quality accurately

**Scenario:** After the synthesizer generates a CNL output from a Markdown document, I need to quantify how much compression was achieved. The measurement must use OpenAI's standard token counting (cl100k_base) so metrics are comparable to API pricing and model context limits.

**Acceptance:**
- Input: original markdown text + compressed CNL text
- Output: CompressionMetrics with token counts, compression ratio, and savings percentages
- Precision: ratio to 4 decimals, percentages to nearest integer
- No external API calls—tokenization is local and deterministic

---

### US-002: As a Quality Assurance Lead, I need to enforce compression thresholds and compare against baselines

**Scenario:** Our quality bar is 30% minimum compression ratio. I need to validate that each pipeline output meets this threshold, and I also need to compare Haiku Protocol output against baseline compression methods (e.g., LLMLingua) to demonstrate competitive advantage.

**Acceptance:**
- Validation API accepts metrics + optional custom threshold
- Returns structured result with pass/fail, message, and metrics
- Baseline comparison takes pre-compressed text from both methods
- Report shows which approach wins (haiku, baseline, or tie)
- No dependency on external compression tools—validator accepts pre-computed text

---

## Architecture / Design

### Design Principles

1. **Separation of Concerns:** Measurement (metrics) is separate from policy (validation)
2. **Pure Functions:** No state mutation, no file I/O, no API calls—only calculation
3. **Fail-Fast on Configuration:** Unsupported tokenizer model raises ValueError immediately
4. **Edge Case Safety:** Empty strings, whitespace-only text, None inputs handled gracefully
5. **Precision & Consistency:** All ratios normalized to 4 decimal places for reporting

### Class Hierarchy

```
CompressionValidator (Core Implementation)
├── __init__(config: ValidationConfig)
├── count_tokens(text: str) → int
├── calculate_metrics(original: str, compressed: str) → CompressionMetrics
├── validate_compression(metrics: CompressionMetrics, min_ratio: Optional[float]) → ValidationResult
└── compare_with_baseline(original: str, haiku: str, baseline: str) → dict

Data Classes (Imported from config/metrics modules)
├── ValidationConfig(model, min_compression_ratio, ratio_precision, percent_precision)
├── CompressionMetrics(original_tokens, compressed_tokens, compression_ratio, token_savings, savings_percent, original_chars, compressed_chars)
└── ValidationResult(passed, compression_ratio, threshold, message, metrics)

Module Functions (Convenience)
├── calculate_compression(original: str, compressed: str, model: str) → dict
└── count_tokens(text: str, model: str) → int
```

### Full Implementation Example

```python
"""
validator.py: CompressionValidator Core Implementation (v0.2.4b)

This module validates compression quality and calculates metrics for the
Haiku Protocol encoder pipeline. It is the fourth and final stage,
measuring token-level compression achieved by the synthesizer.

The validator provides the quantitative evidence that the Haiku Protocol
achieves meaningful compression ratios on procedural documentation.
"""

import logging
from typing import Optional
import tiktoken

from config import ValidationConfig
from metrics import CompressionMetrics, ValidationResult

logger = logging.getLogger(__name__)


class CompressionValidator:
    """Validate compression quality and calculate metrics.

    The validator is the fourth and final stage of the Haiku Protocol
    encoder pipeline. It measures compression quality through token
    counting and validates that output meets configurable thresholds.

    This module provides the quantitative evidence for the project's
    thesis: that the Haiku Protocol achieves meaningful compression
    ratios on procedural documentation.

    Attributes:
        config: ValidationConfig controlling validation behavior.
        tokenizer: tiktoken.Encoding instance for token counting.

    Usage:
        >>> validator = CompressionValidator()
        >>> metrics = validator.calculate_metrics(original_text, cnl_text)
        >>> print(metrics)
        CompressionMetrics(ratio=0.56, savings=56%, tokens: 100→44)
        >>> result = validator.validate_compression(metrics)
        >>> print(result.passed)
        True
    """

    def __init__(self, config: Optional[ValidationConfig] = None) -> None:
        """Initialize validator with tokenizer and configuration.

        Args:
            config: Validation configuration. If None, uses defaults
                (gpt-4 model, 0.3 min ratio).

        Raises:
            ValueError: If the configured model is not supported by tiktoken.
        """
        self.config = config or ValidationConfig()
        try:
            self.tokenizer = tiktoken.encoding_for_model(self.config.model)
        except KeyError:
            logger.error("Unsupported model for tiktoken: %s", self.config.model)
            raise ValueError(f"Unsupported model: {self.config.model}")
        logger.info("CompressionValidator initialized: model=%s", self.config.model)

    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string using tiktoken.

        Uses the tokenizer configured in ValidationConfig (default:
        cl100k_base for GPT-4). Handles edge cases: empty string
        returns 0, None raises TypeError.

        Args:
            text: Text string to tokenize.

        Returns:
            Integer token count.

        Raises:
            TypeError: If text is not a string.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")
        if not text.strip():
            return 0
        tokens = self.tokenizer.encode(text)
        logger.debug("Token count: %d tokens for %d chars", len(tokens), len(text))
        return len(tokens)

    def calculate_metrics(
        self,
        original: str,
        compressed: str,
    ) -> CompressionMetrics:
        """Calculate compression metrics comparing original to compressed text.

        Measures the token-level compression achieved by the Haiku Protocol
        encoder. This is the core metric that demonstrates the thesis.

        Args:
            original: Original document text (Markdown).
            compressed: Compressed CNL string from synthesizer.

        Returns:
            CompressionMetrics with all fields populated.
        """
        original_tokens = self.count_tokens(original)
        compressed_tokens = self.count_tokens(compressed)

        # Handle edge case: empty original
        if original_tokens == 0:
            logger.warning("Zero tokens in original text: ratio set to 0.0")
            ratio = 0.0
        else:
            ratio = 1 - (compressed_tokens / original_tokens)

        savings = original_tokens - compressed_tokens
        ratio_rounded = round(ratio, self.config.ratio_precision)
        percent = f"{round(ratio * 100, self.config.percent_precision):.0f}%"

        metrics = CompressionMetrics(
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=ratio_rounded,
            token_savings=savings,
            savings_percent=percent,
            original_chars=len(original),
            compressed_chars=len(compressed),
        )

        logger.info(
            "Metrics calculated: ratio=%.4f, savings=%s, tokens: %d -> %d",
            ratio_rounded, percent, original_tokens, compressed_tokens,
        )
        return metrics

    def validate_compression(
        self,
        metrics: CompressionMetrics,
        min_ratio: Optional[float] = None,
    ) -> ValidationResult:
        """Validate that compression meets minimum threshold.

        Checks whether the compression ratio meets the configured
        minimum (default 0.3 = 30%). Returns a structured result
        with pass/fail status and human-readable message.

        Args:
            metrics: CompressionMetrics from calculate_metrics().
            min_ratio: Override threshold. If None, uses config default.

        Returns:
            ValidationResult with pass/fail, ratio, threshold, message.
        """
        threshold = min_ratio if min_ratio is not None else self.config.min_compression_ratio
        passed = metrics.compression_ratio >= threshold

        message = (
            f"{'PASS' if passed else 'FAIL'}: "
            f"{metrics.savings_percent} compression "
            f"(threshold: {threshold * 100:.0f}%)"
        )

        result = ValidationResult(
            passed=passed,
            compression_ratio=metrics.compression_ratio,
            threshold=threshold,
            message=message,
            metrics=metrics,
        )

        if not passed:
            logger.warning(
                "Validation FAILED: ratio=%.4f < threshold=%.2f",
                metrics.compression_ratio, threshold,
            )
        else:
            logger.info("Validation PASSED: ratio=%.4f >= threshold=%.2f",
                       metrics.compression_ratio, threshold)

        return result

    def compare_with_baseline(
        self,
        original: str,
        haiku: str,
        baseline: str,
    ) -> dict:
        """Compare Haiku compression against a baseline method.

        Calculates metrics for both the Haiku Protocol output and a
        baseline-compressed version (e.g., from LLMLingua) against
        the same original text, then reports which achieved better
        compression.

        Args:
            original: Original document text.
            haiku: Haiku Protocol compressed text.
            baseline: Baseline-compressed text (e.g., LLMLingua output).

        Returns:
            Dictionary with haiku metrics, baseline metrics, improvement
            (positive = haiku wins), and winner label.
        """
        haiku_metrics = self.calculate_metrics(original, haiku)
        baseline_metrics = self.calculate_metrics(original, baseline)

        improvement = haiku_metrics.compression_ratio - baseline_metrics.compression_ratio

        comparison = {
            "haiku": haiku_metrics.to_dict(),
            "baseline": baseline_metrics.to_dict(),
            "improvement": round(improvement, self.config.ratio_precision),
            "winner": "haiku" if improvement > 0 else (
                "tie" if improvement == 0 else "baseline"
            ),
        }

        logger.info(
            "Baseline comparison: haiku=%.4f, baseline=%.4f, winner=%s",
            haiku_metrics.compression_ratio,
            baseline_metrics.compression_ratio,
            comparison["winner"],
        )
        return comparison


def calculate_compression(
    original: str,
    compressed: str,
    model: str = "gpt-4",
) -> dict:
    """Calculate compression metrics in a single call.

    Convenience function that creates a CompressionValidator and
    computes metrics. Use this for one-off calculations.

    Args:
        original: Original document text.
        compressed: Compressed CNL text.
        model: Tokenizer model name. Default "gpt-4".

    Returns:
        Metrics dictionary from CompressionMetrics.to_dict().
    """
    config = ValidationConfig(model=model)
    validator = CompressionValidator(config=config)
    metrics = validator.calculate_metrics(original, compressed)
    return metrics.to_dict()


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens in text using tiktoken.

    Convenience function for standalone token counting without
    instantiating the full validator.

    Args:
        text: Text to tokenize.
        model: Model name for encoding. Default "gpt-4".

    Returns:
        Integer token count.
    """
    config = ValidationConfig(model=model)
    validator = CompressionValidator(config=config)
    return validator.count_tokens(text)
```

### Validation Pipeline Diagram

```
┌────────────────────────────────────────────────────────────────┐
│              VALIDATION PIPELINE (v0.2.4b)                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  INPUT: Original Markdown + Compressed CNL                     │
│                          │                                     │
│                          ▼                                     │
│  STEP 1: Token Counting (tiktoken/cl100k_base)                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ original_tokens = count_tokens(original)    → e.g., 100  │  │
│  │ compressed_tokens = count_tokens(compressed) → e.g., 44  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│  STEP 2: Metrics Calculation                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ compression_ratio = 1 - (44 / 100) = 0.56               │  │
│  │ token_savings = 100 - 44 = 56                            │  │
│  │ savings_percent = "56%"                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│  STEP 3: Threshold Validation                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 0.56 >= 0.30 (threshold) → PASS                         │  │
│  │ message: "PASS: 56% compression (threshold: 30%)"       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          ▼                                     │
│  OUTPUT: ValidationResult                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ passed: True                                             │  │
│  │ compression_ratio: 0.56                                  │  │
│  │ threshold: 0.3                                           │  │
│  │ message: "PASS: 56% compression (threshold: 30%)"       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
src/
├── validator.py                    # CompressionValidator implementation
│   ├── CompressionValidator class
│   ├── calculate_compression() function
│   ├── count_tokens() function
│   └── __name__ = __name__ for logger
│
├── config.py                       # ValidationConfig data class (imported)
│   └── ValidationConfig(model, min_compression_ratio, ratio_precision, percent_precision)
│
└── metrics.py                      # Data classes (imported)
    ├── CompressionMetrics
    └── ValidationResult

tests/
├── test_validator.py               # Full test suite (26+ tests)
│   ├── TokenCountingTests (4)
│   ├── MetricsCalculationTests (5)
│   ├── ThresholdValidationTests (4)
│   ├── BaselineComparisonTests (3)
│   ├── ConvenienceFunctionTests (3)
│   ├── EdgeCaseTests (4)
│   ├── ConfigTests (2)
│   └── LoggingTests (1)
│
docs/
└── design/
    └── phase-2/
        └── v0.2.4/
            └── validator_core.md   # This specification
```

---

## Implementation Workflow

```
┌──────────────────────────────────────────────────────────────┐
│          VALIDATOR CORE IMPLEMENTATION WORKFLOW                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  PHASE 1: FOUNDATION (Steps 1–4)                            │
│  ┌──────────────────────────────────────────────────────────┐
│  │ 1. Create src/validator.py skeleton                      │
│  │    - Add imports: tiktoken, logging, typing              │
│  │    - Add logger = logging.getLogger(__name__)            │
│  │    - Create empty CompressionValidator class             │
│  └──────────────────────────────────────────────────────────┘
│                          │                                  │
│                          ▼                                  │
│  PHASE 2: CORE METHODS (Steps 5–8)                         │
│  ┌──────────────────────────────────────────────────────────┐
│  │ 2. Implement __init__(config)                            │
│  │    - Initialize tiktoken encoder (fail if unsupported)  │
│  │    - Log initialization                                  │
│  │                                                          │
│  │ 3. Implement count_tokens(text)                          │
│  │    - Type check (raise TypeError if not str)             │
│  │    - Handle empty/whitespace strings (return 0)          │
│  │    - Tokenize and log count                              │
│  │                                                          │
│  │ 4. Implement calculate_metrics(original, compressed)     │
│  │    - Count tokens for both texts                         │
│  │    - Calculate ratio, savings, percentage                │
│  │    - Create CompressionMetrics object                    │
│  │    - Log metrics                                         │
│  │                                                          │
│  │ 5. Implement validate_compression(metrics, min_ratio)    │
│  │    - Compare ratio against threshold                     │
│  │    - Create ValidationResult                             │
│  │    - Log pass/fail with reason                           │
│  └──────────────────────────────────────────────────────────┘
│                          │                                  │
│                          ▼                                  │
│  PHASE 3: ADVANCED METHODS & FUNCTIONS (Steps 9–11)        │
│  ┌──────────────────────────────────────────────────────────┐
│  │ 6. Implement compare_with_baseline(original, haiku, base)│
│  │    - Calculate metrics for haiku output                  │
│  │    - Calculate metrics for baseline output               │
│  │    - Compare ratios, determine winner                    │
│  │    - Return comparison dict                              │
│  │                                                          │
│  │ 7. Implement calculate_compression() convenience         │
│  │    - Create config, validator, calculate, return dict    │
│  │                                                          │
│  │ 8. Implement count_tokens() convenience                  │
│  │    - Create config, validator, count, return int         │
│  └──────────────────────────────────────────────────────────┘
│                          │                                  │
│                          ▼                                  │
│  PHASE 4: TESTING (Steps 12–14)                            │
│  ┌──────────────────────────────────────────────────────────┐
│  │ 9. Create tests/test_validator.py with 26+ tests         │
│  │    - Token counting tests (4)                            │
│  │    - Metrics calculation tests (5)                       │
│  │    - Threshold validation tests (4)                      │
│  │    - Baseline comparison tests (3)                       │
│  │    - Convenience function tests (3)                      │
│  │    - Edge case tests (4)                                 │
│  │    - Config tests (2)                                    │
│  │    - Logging tests (1)                                   │
│  │                                                          │
│  │ 10. Run full test suite: pytest tests/test_validator.py  │
│  │     - All 26+ tests must pass                            │
│  │     - 100% coverage of public API                        │
│  │     - Edge cases handled                                 │
│  │                                                          │
│  │ 11. Verify no print() statements                         │
│  │     - All output via logger                              │
│  │     - No side effects                                    │
│  └──────────────────────────────────────────────────────────┘
│                          │                                  │
│                          ▼                                  │
│  OUTPUT: Validated CompressionValidator Implementation      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Unit Testing Requirements

### Test Coverage by Category

| Category | Test Count | Description |
|----------|-----------|-------------|
| **Token Counting** | 4 | count_tokens() accuracy and edge cases |
| **Metrics Calculation** | 5 | calculate_metrics() with various inputs |
| **Threshold Validation** | 4 | validate_compression() pass/fail logic |
| **Baseline Comparison** | 3 | compare_with_baseline() winner determination |
| **Convenience Functions** | 3 | Module-level convenience functions |
| **Edge Cases** | 4 | Whitespace, long text, Unicode, negative savings |
| **Configuration** | 2 | Config initialization and custom parameters |
| **Logging** | 1 | Logger setup verification |
| **TOTAL** | **26** | Full pipeline coverage |

### Test Naming Convention

```
test_<category>_<scenario>_<expected_outcome>

Examples:
- test_token_counting_short_text_returns_count
- test_token_counting_empty_string_returns_zero
- test_token_counting_none_input_raises_type_error
- test_metrics_calculation_normal_compression_returns_metrics
- test_metrics_calculation_zero_original_tokens_sets_ratio_zero
- test_threshold_validation_passes_above_threshold
- test_threshold_validation_fails_below_threshold
- test_baseline_comparison_haiku_wins_when_ratio_higher
- test_convenience_calculate_compression_returns_dict
- test_edge_case_whitespace_only_text_returns_zero_tokens
- test_config_custom_model_supported
- test_logging_validator_initialization_logs_info
```

### Example Test Code

```python
"""tests/test_validator.py: CompressionValidator Test Suite"""

import pytest
from unittest.mock import patch, MagicMock
import logging

from validator import CompressionValidator, calculate_compression, count_tokens
from config import ValidationConfig
from metrics import CompressionMetrics, ValidationResult


class TestTokenCounting:
    """Token counting with count_tokens() method."""

    def test_token_counting_short_text_returns_count(self):
        """Short text tokenizes to expected count."""
        validator = CompressionValidator()
        text = "The quick brown fox jumps over the lazy dog"
        count = validator.count_tokens(text)
        assert isinstance(count, int)
        assert count > 0

    def test_token_counting_empty_string_returns_zero(self):
        """Empty string returns 0 tokens."""
        validator = CompressionValidator()
        assert validator.count_tokens("") == 0

    def test_token_counting_whitespace_only_returns_zero(self):
        """Whitespace-only string returns 0 tokens."""
        validator = CompressionValidator()
        assert validator.count_tokens("   \n\t  ") == 0

    def test_token_counting_none_input_raises_type_error(self):
        """None input raises TypeError."""
        validator = CompressionValidator()
        with pytest.raises(TypeError):
            validator.count_tokens(None)


class TestMetricsCalculation:
    """Metrics calculation with calculate_metrics() method."""

    def test_metrics_calculation_normal_compression_returns_all_fields(self):
        """Normal compression returns CompressionMetrics with all fields."""
        validator = CompressionValidator()
        original = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        compressed = "Lorem ipsum dolor sit."
        metrics = validator.calculate_metrics(original, compressed)

        assert isinstance(metrics, CompressionMetrics)
        assert metrics.original_tokens > 0
        assert metrics.compressed_tokens > 0
        assert 0 <= metrics.compression_ratio <= 1
        assert metrics.token_savings >= 0
        assert "%" in metrics.savings_percent

    def test_metrics_calculation_zero_original_tokens_sets_ratio_zero(self):
        """Zero-token original text sets ratio to 0.0."""
        validator = CompressionValidator()
        metrics = validator.calculate_metrics("", "compressed text")
        assert metrics.compression_ratio == 0.0
        assert metrics.original_tokens == 0

    def test_metrics_calculation_empty_compressed_maximizes_savings(self):
        """Empty compressed text maximizes token savings."""
        validator = CompressionValidator()
        original = "This is a longer text with multiple words and sentences."
        metrics = validator.calculate_metrics(original, "")
        assert metrics.compressed_tokens == 0
        assert metrics.token_savings == metrics.original_tokens
        assert metrics.compression_ratio == 1.0

    def test_metrics_calculation_same_text_zero_ratio(self):
        """Identical original and compressed text gives 0 ratio."""
        validator = CompressionValidator()
        text = "The same text"
        metrics = validator.calculate_metrics(text, text)
        assert metrics.compression_ratio == 0.0
        assert metrics.token_savings == 0

    def test_metrics_calculation_high_compression_high_ratio(self):
        """High compression (10:1) gives ratio > 0.9."""
        validator = CompressionValidator()
        original = "word " * 100  # Long repetitive text
        compressed = "word"
        metrics = validator.calculate_metrics(original, compressed)
        assert metrics.compression_ratio > 0.9


class TestThresholdValidation:
    """Threshold validation with validate_compression() method."""

    def test_threshold_validation_passes_above_threshold(self):
        """Ratio above threshold passes validation."""
        config = ValidationConfig(min_compression_ratio=0.3)
        validator = CompressionValidator(config=config)
        metrics = CompressionMetrics(
            original_tokens=100, compressed_tokens=40,
            compression_ratio=0.6, token_savings=60,
            savings_percent="60%", original_chars=500, compressed_chars=200
        )
        result = validator.validate_compression(metrics)
        assert result.passed is True
        assert "PASS" in result.message

    def test_threshold_validation_fails_below_threshold(self):
        """Ratio below threshold fails validation."""
        config = ValidationConfig(min_compression_ratio=0.5)
        validator = CompressionValidator(config=config)
        metrics = CompressionMetrics(
            original_tokens=100, compressed_tokens=60,
            compression_ratio=0.4, token_savings=40,
            savings_percent="40%", original_chars=500, compressed_chars=300
        )
        result = validator.validate_compression(metrics)
        assert result.passed is False
        assert "FAIL" in result.message

    def test_threshold_validation_exact_threshold_edge_passes(self):
        """Ratio exactly at threshold passes."""
        config = ValidationConfig(min_compression_ratio=0.5)
        validator = CompressionValidator(config=config)
        metrics = CompressionMetrics(
            original_tokens=100, compressed_tokens=50,
            compression_ratio=0.5, token_savings=50,
            savings_percent="50%", original_chars=500, compressed_chars=250
        )
        result = validator.validate_compression(metrics)
        assert result.passed is True

    def test_threshold_validation_custom_override_applied(self):
        """Custom threshold parameter overrides config."""
        config = ValidationConfig(min_compression_ratio=0.5)
        validator = CompressionValidator(config=config)
        metrics = CompressionMetrics(
            original_tokens=100, compressed_tokens=40,
            compression_ratio=0.6, token_savings=60,
            savings_percent="60%", original_chars=500, compressed_chars=200
        )
        # Override with stricter threshold
        result = validator.validate_compression(metrics, min_ratio=0.7)
        assert result.passed is False
        assert result.threshold == 0.7


class TestBaselineComparison:
    """Baseline comparison with compare_with_baseline() method."""

    def test_baseline_comparison_haiku_wins(self):
        """Haiku output with better ratio marked as winner."""
        validator = CompressionValidator()
        original = "The quick brown fox jumps over the lazy dog" * 5
        haiku = "Quick fox jumps dog"
        baseline = "The quick brown fox jumps over the lazy dog" * 2

        comparison = validator.compare_with_baseline(original, haiku, baseline)
        assert comparison["winner"] == "haiku"
        assert comparison["improvement"] > 0

    def test_baseline_comparison_baseline_wins(self):
        """Baseline output with better ratio marked as winner."""
        validator = CompressionValidator()
        original = "The quick brown fox jumps over the lazy dog" * 5
        haiku = "The quick brown fox jumps over the lazy dog" * 4
        baseline = "Quick fox jumps"

        comparison = validator.compare_with_baseline(original, haiku, baseline)
        assert comparison["winner"] == "baseline"
        assert comparison["improvement"] < 0

    def test_baseline_comparison_tie(self):
        """Equal compression ratios marked as tie."""
        validator = CompressionValidator()
        original = "text " * 100
        compressed = "text" * 50

        comparison = validator.compare_with_baseline(original, compressed, compressed)
        assert comparison["winner"] == "tie"
        assert comparison["improvement"] == 0


class TestConvenienceFunctions:
    """Module-level convenience function tests."""

    def test_convenience_calculate_compression_returns_dict(self):
        """calculate_compression() returns dict from metrics."""
        original = "Long text that should be compressed significantly"
        compressed = "compressed"
        result = calculate_compression(original, compressed)

        assert isinstance(result, dict)
        assert "compression_ratio" in result
        assert "token_savings" in result

    def test_convenience_count_tokens_returns_int(self):
        """count_tokens() returns integer."""
        text = "The quick brown fox"
        result = count_tokens(text)

        assert isinstance(result, int)
        assert result > 0

    def test_convenience_custom_model_parameter(self):
        """Convenience functions accept custom model parameter."""
        original = "Text to compress"
        compressed = "compress"

        result = calculate_compression(original, compressed, model="gpt-4")
        assert isinstance(result, dict)

        count = count_tokens("test", model="gpt-4")
        assert isinstance(count, int)


class TestEdgeCases:
    """Edge case handling across methods."""

    def test_edge_case_unicode_text_tokenizes_correctly(self):
        """Unicode text (e.g., emoji, non-Latin) tokenizes without error."""
        validator = CompressionValidator()
        text = "Hello 世界 🌍 Привет"
        count = validator.count_tokens(text)
        assert isinstance(count, int)
        assert count > 0

    def test_edge_case_very_long_text_completes_within_timeout(self):
        """Very long text (10k+ tokens) processes without timeout."""
        validator = CompressionValidator()
        long_text = "word " * 2000  # Approx 2000 tokens
        count = validator.count_tokens(long_text)
        assert count > 1000  # Should be significant

    def test_edge_case_compressed_longer_than_original_negative_savings(self):
        """Compressed text longer than original gives negative savings."""
        validator = CompressionValidator()
        original = "short"
        compressed = "This is a much longer version of the short text above"
        metrics = validator.calculate_metrics(original, compressed)

        assert metrics.token_savings < 0
        assert metrics.compression_ratio < 0

    def test_edge_case_repeated_whitespace_handled(self):
        """Multiple spaces, tabs, newlines handled correctly."""
        validator = CompressionValidator()
        text1 = "word1   word2\t\tword3\n\nword4"
        text2 = "word1 word2 word3 word4"
        count1 = validator.count_tokens(text1)
        count2 = validator.count_tokens(text2)
        # Both should tokenize (exact counts may differ)
        assert count1 > 0
        assert count2 > 0


class TestConfiguration:
    """Configuration initialization and behavior."""

    def test_config_default_model_gpt4_supported(self):
        """Default configuration uses gpt-4 model."""
        validator = CompressionValidator()
        assert validator.config.model == "gpt-4"
        assert validator.tokenizer is not None

    def test_config_custom_model_initialization(self):
        """Custom model passed to config initializes successfully."""
        config = ValidationConfig(model="gpt-4")
        validator = CompressionValidator(config=config)
        assert validator.config.model == "gpt-4"


class TestLogging:
    """Logging behavior verification."""

    def test_logging_validator_initialization_logs_info(self, caplog):
        """Validator initialization logs INFO message."""
        with caplog.at_level(logging.INFO):
            validator = CompressionValidator()

        assert "CompressionValidator initialized" in caplog.text
        assert "gpt-4" in caplog.text
```

---

## Logging Requirements

| Level | When | Message Format | Example |
|-------|------|---|---|
| **INFO** | Validator initialized | `CompressionValidator initialized: model=%s` | `CompressionValidator initialized: model=gpt-4` |
| **INFO** | Metrics calculated | `Metrics calculated: ratio=%.4f, savings=%s, tokens: %d -> %d` | `Metrics calculated: ratio=0.5600, savings=56%, tokens: 100 -> 44` |
| **INFO** | Validation passed | `Validation PASSED: ratio=%.4f >= threshold=%.2f` | `Validation PASSED: ratio=0.5600 >= threshold=0.30` |
| **INFO** | Baseline compared | `Baseline comparison: haiku=%.4f, baseline=%.4f, winner=%s` | `Baseline comparison: haiku=0.5600, baseline=0.4200, winner=haiku` |
| **DEBUG** | Token count | `Token count: %d tokens for %d chars` | `Token count: 44 tokens for 250 chars` |
| **WARNING** | Validation failed | `Validation FAILED: ratio=%.4f < threshold=%.2f` | `Validation FAILED: ratio=0.2500 < threshold=0.30` |
| **WARNING** | Zero-token input | `Zero tokens in original text: ratio set to 0.0` | `Zero tokens in original text: ratio set to 0.0` |
| **ERROR** | Invalid model | `Unsupported model for tiktoken: %s` | `Unsupported model for tiktoken: invalid-model-x` |

**Logging Best Practices:**
- Logger initialized: `logger = logging.getLogger(__name__)`
- No print() statements anywhere
- All user-facing output via logger
- DEBUG level for detailed metrics (token counts)
- INFO for milestone completion (validation, comparison)
- WARNING for policy violations (thresholds not met)
- ERROR for configuration failures (unsupported models)

---

## Acceptance Criteria

- [ ] **AC-001:** CompressionValidator initializes successfully with default ValidationConfig
- [ ] **AC-002:** CompressionValidator initializes with custom ValidationConfig
- [ ] **AC-003:** Unsupported tokenizer model raises ValueError with descriptive message
- [ ] **AC-004:** `count_tokens()` returns accurate token count for English text (GPT-4 encoding)
- [ ] **AC-005:** `count_tokens()` returns 0 for empty strings
- [ ] **AC-006:** `count_tokens()` returns 0 for whitespace-only strings
- [ ] **AC-007:** `count_tokens()` raises TypeError for non-string input (e.g., None, int)
- [ ] **AC-008:** `calculate_metrics()` returns CompressionMetrics with all 7 fields populated
- [ ] **AC-009:** `calculate_metrics()` handles zero-token original (ratio=0.0)
- [ ] **AC-010:** `validate_compression()` returns ValidationResult with pass=True when ratio >= threshold
- [ ] **AC-011:** `validate_compression()` returns ValidationResult with pass=False when ratio < threshold
- [ ] **AC-012:** `validate_compression()` uses config threshold by default
- [ ] **AC-013:** `validate_compression()` accepts optional min_ratio override parameter
- [ ] **AC-014:** `compare_with_baseline()` returns dict with haiku, baseline, improvement, and winner keys
- [ ] **AC-015:** `compare_with_baseline()` correctly identifies haiku as winner when ratio higher
- [ ] **AC-016:** `compare_with_baseline()` correctly identifies baseline as winner when ratio higher
- [ ] **AC-017:** `compare_with_baseline()` identifies tie when ratios equal
- [ ] **AC-018:** `calculate_compression()` convenience function works without explicit config
- [ ] **AC-019:** `count_tokens()` convenience function works without explicit config
- [ ] **AC-020:** All 26+ unit tests pass with pytest
- [ ] **AC-021:** No print() statements in implementation (all logging via logger)
- [ ] **AC-022:** All public methods have complete Google-style docstrings
- [ ] **AC-023:** Logger initialized with `__name__` at module level
- [ ] **AC-024:** Edge cases handled: Unicode, very long text, negative savings
- [ ] **AC-025:** Precision: compression_ratio to 4 decimals, percentages to nearest integer
- [ ] **AC-026:** No side effects—pure calculation functions, no I/O or API calls

---

## Limitations & Constraints

### Design Constraints

1. **Tokenizer Consistency:** Always uses tiktoken cl100k_base for GPT-4. No fallback to alternative tokenizers. Unsupported models raise ValueError immediately (fail-fast).

2. **No External Dependencies:** Validator does NOT invoke external APIs (no calls to OpenAI, LLMLingua, or other services). Baseline comparison accepts pre-compressed text from upstream modules.

3. **Text Storage:** Original and compressed text passed to methods are NOT stored internally. Validator works with metrics objects, not raw text, after calculation phase.

4. **Precision Limits:** Floating-point arithmetic may introduce rounding at edge cases. Ratio normalized to 4 decimal places for consistency.

5. **Empty String Handling:** Empty or whitespace-only strings return 0 tokens and 0.0 compression ratio (by design—no content to compress).

6. **No Parallelization:** Single-threaded design. Token counting is CPU-bound but not parallelized (complexity not justified for typical document sizes).

### Architectural Constraints

1. **Pure Functions:** No state mutation outside constructor. All methods are deterministic—same input always produces same output.

2. **Configuration Immutability:** ValidationConfig passed to __init__ is not copied or cached separately; mutations by caller are caller's responsibility.

3. **No Caching:** Token counts not cached between calls. Each call to count_tokens() involves full tiktoken encoding.

4. **No Retry Logic:** Failed tiktoken initialization (unsupported model) fails immediately; no retry or degradation.

### Runtime Constraints

1. **Memory:** Token lists for large texts (10k+ tokens) held in memory during encoding. Not a concern for typical procedural docs (< 500k chars).

2. **Latency:** Token encoding is fast (~1ms per 1000 tokens on modern hardware). No timeout controls implemented; caller responsible for timeout management if needed.

3. **Exception Handling:** Only explicit exceptions (TypeError, ValueError). Unexpected tiktoken errors propagate as-is.

---

## Dependencies

### Required External Packages

| Package | Version | Purpose | Usage |
|---------|---------|---------|-------|
| `tiktoken` | `>=0.7.0` | Token encoding (OpenAI) | `tiktoken.encoding_for_model()`, `encode()` |
| `logging` | stdlib | Application logging | `logging.getLogger(__name__)` |
| `typing` | stdlib | Type hints | `Optional`, `Dict`, return types |

### Internal Dependencies

| Module | Import | Purpose |
|--------|--------|---------|
| `config.py` | `ValidationConfig` | Validation configuration data class |
| `metrics.py` | `CompressionMetrics` | Compression metrics data class |
| `metrics.py` | `ValidationResult` | Validation result data class |

### Data Class Requirements

**ValidationConfig** must provide:
- `model: str` (default "gpt-4")
- `min_compression_ratio: float` (default 0.3)
- `ratio_precision: int` (default 4)
- `percent_precision: int` (default 0)

**CompressionMetrics** must provide:
- `original_tokens: int`
- `compressed_tokens: int`
- `compression_ratio: float`
- `token_savings: int`
- `savings_percent: str`
- `original_chars: int`
- `compressed_chars: int`
- `to_dict() -> dict` method

**ValidationResult** must provide:
- `passed: bool`
- `compression_ratio: float`
- `threshold: float`
- `message: str`
- `metrics: CompressionMetrics`

---

## Outputs to Next Sub-Part

The CompressionValidator implementation (v0.2.4b) provides the following artifacts to be consumed by Phase 2 integration (v0.2.5 or Phase 3 documentation):

### Exported API

1. **CompressionValidator class**
   - Full-featured validator with all public methods
   - Configurable via ValidationConfig
   - Integrated logging

2. **Convenience functions**
   - `calculate_compression(original, compressed, model)` → dict
   - `count_tokens(text, model)` → int

3. **Type signatures**
   - All methods include return type hints
   - All parameters include type hints
   - Full docstring specifications

### Quality Guarantees

- ✓ 26+ unit tests passing
- ✓ 100% coverage of public API
- ✓ Edge cases handled (empty, long, Unicode, negative savings)
- ✓ All logging requirements met
- ✓ No side effects (pure functions)
- ✓ No external API calls

### Integration Points

**For v0.2.5 (Pipeline Integration):**
- Import CompressionValidator
- Initialize with config from pipeline (or defaults)
- Call calculate_metrics(original_md, cnl_text)
- Call validate_compression(metrics) to enforce thresholds

**For v0.2.6 (Metrics Reporting & Dashboard):**
- Consume CompressionMetrics and ValidationResult objects
- Display compression_ratio, token_savings, savings_percent
- Show pass/fail status from ValidationResult.passed

**For Baseline Analysis (Phase 2 or later):**
- Call compare_with_baseline(original, haiku_output, baseline_output)
- Use winner field to determine competitive advantage
- Plot improvement trends over multiple documents

---

## Decision Log

### Decision 1: Tokenizer Strategy (Approved)

**Issue:** How should token counting work? Manual implementation vs. external library?

**Options Considered:**
- A. Implement custom token counter (fast, lightweight, inaccurate)
- B. Use tiktoken (accurate, industry-standard, adds dependency)

**Decision:** **Option B — Use tiktoken**

**Rationale:**
- tiktoken is the official OpenAI tokenizer; results directly comparable to API usage
- Already industry-standard in LLM communities
- Dependency weight justified by accuracy and compatibility
- Fast enough for typical document sizes (< 100 ms for 10k tokens)

**Trade-offs:**
- Adds external dependency (mitigated by popularity and stability)
- No fallback tokenizer if tiktoken unavailable (feature, not bug—fail-fast)

---

### Decision 2: Compression Ratio Formula (Approved)

**Issue:** How should compression_ratio be calculated?

**Options Considered:**
- A. `compressed / original` (intuitive as "remaining" ratio, but inverted semantics)
- B. `1 - (compressed / original)` (intuitive as "improvement" ratio)
- C. `(original - compressed) / original` (equivalent to B, more verbose)

**Decision:** **Option B — `1 - (compressed / original)`**

**Rationale:**
- Higher ratio = better compression (0.56 = "56% better than original")
- Intuitive for thresholds (e.g., "need 30% improvement")
- Aligned with common compression terminology
- Enables straightforward comparison (haiku_ratio > baseline_ratio = haiku wins)

**Trade-offs:**
- Must handle division by zero when original_tokens = 0
- Inverted from some libraries, but correct for user communication

---

### Decision 3: Metrics vs. Validation Separation (Approved)

**Issue:** Should metrics calculation and validation be combined or separate?

**Options Considered:**
- A. Combined: `validate_compression(original, compressed)` → ValidationResult with embedded metrics
- B. Separate: `calculate_metrics()` → CompressionMetrics, then `validate_compression(metrics)` → ValidationResult

**Decision:** **Option B — Separate concerns**

**Rationale:**
- Metrics are measurement facts (immutable, universally true)
- Validation is policy decision (configurable threshold, business logic)
- Separation enables reuse: metrics useful without validation
- Cleaner API: metrics for analysis, validation for pass/fail decisions
- Example: dashboard might report metrics without enforcing thresholds

**Trade-offs:**
- Requires two function calls for full pipeline
- Slight additional complexity in usage (mitigated by convenience functions)

---

### Decision 4: Baseline Comparison Scope (Approved)

**Issue:** Should validator compute baseline compression, or accept pre-computed baseline text?

**Options Considered:**
- A. Validator invokes baseline compression method (e.g., LLMLingua API)
- B. Validator accepts pre-compressed baseline text from caller
- C. Validator factory pattern with pluggable compressors

**Decision:** **Option B — Accept pre-computed baseline**

**Rationale:**
- Validator's job is measurement, not compression
- Baseline computation (LLMLingua, summarization, etc.) is Phase 3 concern
- Keeps validator independent of external compression libraries
- Enables fair comparison with any baseline method
- Simpler, more testable: no external API dependencies

**Trade-offs:**
- Caller responsible for generating baseline output
- Mitigated by clear documentation and Phase 3 baseline module

---

### Decision 5: Token Counting as Method + Function (Approved)

**Issue:** Should token counting be only a class method, or also a module function?

**Options Considered:**
- A. Class method only: `validator.count_tokens(text)`
- B. Module function only: `count_tokens(text)` at module level
- C. Both (method for pipeline, function for convenience)

**Decision:** **Option C — Both**

**Rationale:**
- Class method useful in pipeline context (reuse same validator, config)
- Module function useful for one-off token counting (no config needed)
- Common pattern in libraries (e.g., json.loads vs. JSONDecoder.loads)
- Zero code duplication (function delegates to class)

**Trade-offs:**
- Slight API surface area (mitigated by clear documentation)

---

### Decision 6: Error Handling Strategy (Approved)

**Issue:** How strict should error handling be?

**Options Considered:**
- A. Permissive: Try multiple fallbacks, silent defaults (e.g., try gpt-4, fall back to gpt-3.5)
- B. Strict: Fail immediately on unsupported config (ValueError for bad model)
- C. Middle ground: Log warnings, use safe defaults

**Decision:** **Option B — Strict (fail-fast)**

**Rationale:**
- Unsupported model is a configuration error, not a runtime issue
- Silent fallbacks hide bugs; explicit errors aid debugging
- Failing at initialization ensures early detection
- Metrics from fallback tokenizer could be meaningless (mislead consumers)

**Trade-offs:**
- Less forgiving to misconfiguration
- Mitigated by clear error messages and defaults

---

## Appendix: Implementation Checklist

```
PHASE 1: FOUNDATION
------------------
[ ] Create src/validator.py file
[ ] Add standard imports (tiktoken, logging, typing)
[ ] Add module-level logger: logger = logging.getLogger(__name__)
[ ] Create empty CompressionValidator class with docstring

PHASE 2: CORE METHODS
---------------------
[ ] Implement __init__(config: Optional[ValidationConfig])
    [ ] Initialize self.config
    [ ] Initialize self.tokenizer from tiktoken
    [ ] Add error handling for unsupported models
    [ ] Log initialization with model name

[ ] Implement count_tokens(text: str) -> int
    [ ] Type check (isinstance, raise TypeError)
    [ ] Handle empty/whitespace (return 0)
    [ ] Call tiktoken.encode()
    [ ] Log token count
    [ ] Return count

[ ] Implement calculate_metrics(original: str, compressed: str) -> CompressionMetrics
    [ ] Call count_tokens for both texts
    [ ] Calculate ratio = 1 - (compressed_tokens / original_tokens)
    [ ] Handle zero original (ratio = 0.0, log warning)
    [ ] Calculate savings = original_tokens - compressed_tokens
    [ ] Round ratio to config.ratio_precision (4 decimals)
    [ ] Format percent to config.percent_precision
    [ ] Create CompressionMetrics object with all fields
    [ ] Log metrics calculated
    [ ] Return metrics

[ ] Implement validate_compression(metrics: CompressionMetrics, min_ratio: Optional[float]) -> ValidationResult
    [ ] Determine threshold (min_ratio or config default)
    [ ] Check: passed = metrics.compression_ratio >= threshold
    [ ] Format message "PASS/FAIL: X% compression (threshold: Y%)"
    [ ] Create ValidationResult object
    [ ] Log PASSED or FAILED with reason
    [ ] Return result

PHASE 3: ADVANCED METHODS & FUNCTIONS
--------------------------------------
[ ] Implement compare_with_baseline(original: str, haiku: str, baseline: str) -> dict
    [ ] Call calculate_metrics(original, haiku)
    [ ] Call calculate_metrics(original, baseline)
    [ ] Calculate improvement = haiku.ratio - baseline.ratio
    [ ] Determine winner (haiku > 0, baseline < 0, tie == 0)
    [ ] Create comparison dict with haiku, baseline, improvement, winner
    [ ] Log baseline comparison with winner
    [ ] Return comparison

[ ] Implement calculate_compression() convenience function
    [ ] Create ValidationConfig with model parameter
    [ ] Create CompressionValidator(config)
    [ ] Call validator.calculate_metrics(original, compressed)
    [ ] Return metrics.to_dict()

[ ] Implement count_tokens() convenience function
    [ ] Create ValidationConfig with model parameter
    [ ] Create CompressionValidator(config)
    [ ] Call validator.count_tokens(text)
    [ ] Return count

PHASE 4: TESTING
----------------
[ ] Create tests/test_validator.py
[ ] Implement TestTokenCounting (4 tests)
    [ ] test_token_counting_short_text_returns_count
    [ ] test_token_counting_empty_string_returns_zero
    [ ] test_token_counting_whitespace_only_returns_zero
    [ ] test_token_counting_none_input_raises_type_error

[ ] Implement TestMetricsCalculation (5 tests)
    [ ] test_metrics_calculation_normal_compression_returns_all_fields
    [ ] test_metrics_calculation_zero_original_tokens_sets_ratio_zero
    [ ] test_metrics_calculation_empty_compressed_maximizes_savings
    [ ] test_metrics_calculation_same_text_zero_ratio
    [ ] test_metrics_calculation_high_compression_high_ratio

[ ] Implement TestThresholdValidation (4 tests)
    [ ] test_threshold_validation_passes_above_threshold
    [ ] test_threshold_validation_fails_below_threshold
    [ ] test_threshold_validation_exact_threshold_edge_passes
    [ ] test_threshold_validation_custom_override_applied

[ ] Implement TestBaselineComparison (3 tests)
    [ ] test_baseline_comparison_haiku_wins
    [ ] test_baseline_comparison_baseline_wins
    [ ] test_baseline_comparison_tie

[ ] Implement TestConvenienceFunctions (3 tests)
    [ ] test_convenience_calculate_compression_returns_dict
    [ ] test_convenience_count_tokens_returns_int
    [ ] test_convenience_custom_model_parameter

[ ] Implement TestEdgeCases (4 tests)
    [ ] test_edge_case_unicode_text_tokenizes_correctly
    [ ] test_edge_case_very_long_text_completes_within_timeout
    [ ] test_edge_case_compressed_longer_than_original_negative_savings
    [ ] test_edge_case_repeated_whitespace_handled

[ ] Implement TestConfiguration (2 tests)
    [ ] test_config_default_model_gpt4_supported
    [ ] test_config_custom_model_initialization

[ ] Implement TestLogging (1 test)
    [ ] test_logging_validator_initialization_logs_info

[ ] Run: pytest tests/test_validator.py -v
    [ ] All 26 tests pass
    [ ] No test failures
    [ ] Coverage >= 95%

[ ] Verify no print() statements
    [ ] grep -n "print(" src/validator.py → 0 results
    [ ] All output via logger

[ ] Verify docstrings
    [ ] All public methods have Google-style docstrings
    [ ] All parameters documented
    [ ] All return types documented

DELIVERABLE VERIFICATION
-------------------------
[ ] src/validator.py exists and contains complete implementation
[ ] tests/test_validator.py exists with 26+ passing tests
[ ] All 26+ acceptance criteria met
[ ] Logger initialized with __name__
[ ] No side effects or external I/O
[ ] Edge cases handled gracefully
[ ] Documentation matches implementation
```

---

**Document Version:** v0.2.4b
**Last Updated:** [Implementation Date]
**Status:** ⬜ Not Started
**Next: v0.2.5 or Phase 2 Integration**
