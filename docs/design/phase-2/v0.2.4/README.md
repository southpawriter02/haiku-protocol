# v0.2.4 — Validation & Metrics

<aside>

**Version:** v0.2.4

**Parent:** v0.2.0 — Encoder Development

**Status:** ⬜ Not Started

**Duration:** 30–45 minutes (across 3 sub-parts)

**Deliverable:** `validator.py` — Metrics calculation and validation

</aside>

---

## Objective

Build the validation module that calculates compression metrics and verifies semantic fidelity. The validator is the **fourth and final stage** of the encoder pipeline, providing the quantitative evidence for the Haiku Protocol's compression thesis through token counting and threshold validation.

---

## Sub-Parts

| Version | Name | Duration | Deliverable |
|---------|------|----------|-------------|
| [v0.2.4a](metrics_data_model.md) | Compression Metrics Data Model | 10–15 min | `CompressionMetrics`, `ValidationResult`, `ValidationConfig`, 22+ tests |
| [v0.2.4b](validator_core.md) | CompressionValidator Core Implementation | 15–20 min | Token counting, metrics calculation, threshold validation, baseline comparison, 26+ tests |
| [v0.2.4c](integration_testing.md) | Integration Testing & Pipeline Completion | 10–15 min | Pipeline integration tests, `encoder.py` orchestrator, Phase 2 exit verification, 22+ tests |

**Total: 70+ tests across all sub-parts**

---

## Metrics Calculated

---

## Implementation: [`validator.py`](http://validator.py)

```python
# src/validator.py - Metrics and Validation Module

import tiktoken
from dataclasses import dataclass
from typing import Optional

@dataclass
class CompressionMetrics:
    """Container for compression metrics."""
    original_text: str
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    token_savings: int
    savings_percent: str
    
    def __repr__(self):
        return f"CompressionMetrics(ratio={self.compression_ratio:.2f}, savings={self.savings_percent})"
    
    def to_dict(self) -> dict:
        return {
            "original_tokens": self.original_tokens,
            "compressed_tokens": self.compressed_tokens,
            "compression_ratio": self.compression_ratio,
            "token_savings": self.token_savings,
            "savings_percent": self.savings_percent
        }

class CompressionValidator:
    """Validate compression and calculate metrics."""
    
    def __init__(self, model: str = "gpt-4"):
        """
        Initialize validator with tokenizer.
        
        Args:
            model: Model name for tokenizer (default: gpt-4)
        """
        self.tokenizer = tiktoken.encoding_for_model(model)
        self.model = model
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.tokenizer.encode(text))
    
    def calculate_metrics(self, original: str, compressed: str) -> CompressionMetrics:
        """
        Calculate compression metrics.
        
        Args:
            original: Original document text
            compressed: Compressed CNL text
            
        Returns:
            CompressionMetrics object
        """
        original_tokens = self.count_tokens(original)
        compressed_tokens = self.count_tokens(compressed)
        
        # Avoid division by zero
        if original_tokens == 0:
            ratio = 0.0
        else:
            ratio = 1 - (compressed_tokens / original_tokens)
        
        savings = original_tokens - compressed_tokens
        savings_pct = f"{round(ratio * 100)}%"
        
        return CompressionMetrics(
            original_text=original,
            compressed_text=compressed,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=round(ratio, 4),
            token_savings=savings,
            savings_percent=savings_pct
        )
    
    def validate_compression(self, metrics: CompressionMetrics, 
                            min_ratio: float = 0.3) -> dict:
        """
        Validate that compression meets minimum threshold.
        
        Args:
            metrics: CompressionMetrics object
            min_ratio: Minimum acceptable compression ratio
            
        Returns:
            Validation result dictionary
        """
        passed = metrics.compression_ratio >= min_ratio
        
        return {
            "passed": passed,
            "compression_ratio": metrics.compression_ratio,
            "threshold": min_ratio,
            "message": f"{'✅ PASS' if passed else '❌ FAIL'}: "
                      f"{metrics.savings_percent} compression "
                      f"(threshold: {min_ratio*100}%)"
        }
    
    def compare_with_baseline(self, original: str, haiku: str, 
                             baseline: str) -> dict:
        """
        Compare Haiku compression against a baseline (e.g., LLMLingua).
        
        Args:
            original: Original text
            haiku: Haiku-compressed text
            baseline: Baseline-compressed text
            
        Returns:
            Comparison dictionary
        """
        haiku_metrics = self.calculate_metrics(original, haiku)
        baseline_metrics = self.calculate_metrics(original, baseline)
        
        improvement = haiku_metrics.compression_ratio - baseline_metrics.compression_ratio
        
        return {
            "haiku": haiku_metrics.to_dict(),
            "baseline": baseline_metrics.to_dict(),
            "improvement": round(improvement, 4),
            "winner": "haiku" if improvement > 0 else "baseline"
        }

# Convenience functions
def calculate_compression(original: str, compressed: str, 
                         model: str = "gpt-4") -> dict:
    """
    Calculate compression metrics.
    
    Args:
        original: Original text
        compressed: Compressed text
        model: Tokenizer model
        
    Returns:
        Metrics dictionary
    """
    validator = CompressionValidator(model)
    metrics = validator.calculate_metrics(original, compressed)
    return metrics.to_dict()

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens in text."""
    validator = CompressionValidator(model)
    return validator.count_tokens(text)

if __name__ == "__main__":
    # Test the validator
    original = """
    To restart the application server, you must first ensure that 
    all configuration changes have been saved. This prevents any 
    loss of settings during the reboot process. Navigate to the 
    settings panel and click "Save Configuration." Wait for the 
    confirmation message. Once confirmed, run: systemctl restart app-server
    """
    
    compressed = "Action:Restart_Server REQUIRES State:Config_Saved -> EXEC:systemctl_restart_app-server"
    
    validator = CompressionValidator()
    metrics = validator.calculate_metrics(original, compressed)
    
    print(f"Original: {metrics.original_tokens} tokens")
    print(f"Compressed: {metrics.compressed_tokens} tokens")
    print(f"Compression: {metrics.savings_percent}")
    print(f"Ratio: {metrics.compression_ratio}")
    
    validation = validator.validate_compression(metrics, min_ratio=0.5)
    print(f"\nValidation: {validation['message']}")
```

---

## Test Cases

---

## Acceptance Criteria

- [ ]  [`validator.py`](http://validator.py) created in `src/` directory
- [ ]  `CompressionValidator` class implemented
- [ ]  Token counting works correctly
- [ ]  Metrics calculation handles edge cases
- [ ]  Validation threshold check works
- [ ]  Baseline comparison implemented