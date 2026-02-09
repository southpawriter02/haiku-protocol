# v0.3.3 — Benchmark Integration

<aside>

**Version:** v0.3.3

**Parent:** v0.3.0 — Demo & Visualization

**Status:** ⬜ Not Started

**Duration:** 45-60 minutes

**Deliverable:** LLMLingua benchmark comparison

</aside>

---

## Objective

Compare Haiku Protocol compression against Microsoft's LLMLingua to demonstrate competitive or superior performance.

---

## Benchmark Design

---

## Implementation: `llmlingua_[comparison.py](http://comparison.py)`

```python
# benchmarks/llmlingua_comparison.py - Benchmark Comparison

import json
import tiktoken
from typing import Dict, List
from dataclasses import dataclass

# Import LLMLingua
try:
    from llmlingua import PromptCompressor
    LLMLINGUA_AVAILABLE = True
except ImportError:
    LLMLINGUA_AVAILABLE = False
    print("Warning: LLMLingua not available")

# Import our encoder
from src.encoder import encode
from src.validator import CompressionValidator

@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""
    document_name: str
    original_tokens: int
    haiku_tokens: int
    haiku_ratio: float
    llmlingua_tokens: int
    llmlingua_ratio: float
    winner: str
    improvement: float

class BenchmarkRunner:
    """Run compression benchmarks."""
    
    def __init__(self):
        self.validator = CompressionValidator()
        if LLMLINGUA_AVAILABLE:
            self.llmlingua = PromptCompressor()
        else:
            self.llmlingua = None
    
    def compress_with_llmlingua(self, text: str) -> str:
        """Compress text using LLMLingua."""
        if not self.llmlingua:
            return text  # Return original if not available
        
        try:
            result = self.llmlingua.compress_prompt(text)
            return result.get("compressed_prompt", text)
        except Exception as e:
            print(f"LLMLingua error: {e}")
            return text
    
    def run_benchmark(self, name: str, document: str) -> BenchmarkResult:
        """
        Run a single benchmark comparison.
        
        Args:
            name: Document identifier
            document: Text to compress
            
        Returns:
            BenchmarkResult object
        """
        # Get original token count
        original_tokens = self.validator.count_tokens(document)
        
        # Compress with Haiku
        haiku_result = encode(document)
        haiku_tokens = haiku_result["compressed_tokens"]
        haiku_ratio = haiku_result["compression_ratio"]
        
        # Compress with LLMLingua
        llmlingua_output = self.compress_with_llmlingua(document)
        llmlingua_tokens = self.validator.count_tokens(llmlingua_output)
        llmlingua_ratio = 1 - (llmlingua_tokens / original_tokens) if original_tokens > 0 else 0
        
        # Determine winner
        improvement = haiku_ratio - llmlingua_ratio
        winner = "haiku" if improvement > 0 else "llmlingua"
        
        return BenchmarkResult(
            document_name=name,
            original_tokens=original_tokens,
            haiku_tokens=haiku_tokens,
            haiku_ratio=round(haiku_ratio, 4),
            llmlingua_tokens=llmlingua_tokens,
            llmlingua_ratio=round(llmlingua_ratio, 4),
            winner=winner,
            improvement=round(improvement, 4)
        )
    
    def run_benchmark_suite(self, documents: Dict[str, str]) -> List[BenchmarkResult]:
        """
        Run benchmarks on multiple documents.
        
        Args:
            documents: Dict of {name: content}
            
        Returns:
            List of BenchmarkResult objects
        """
        results = []
        
        for name, content in documents.items():
            print(f"Benchmarking: {name}...")
            result = self.run_benchmark(name, content)
            results.append(result)
            
            print(f"  Haiku: {result.haiku_ratio*100:.1f}% | "
                  f"LLMLingua: {result.llmlingua_ratio*100:.1f}% | "
                  f"Winner: {result.winner}")
        
        return results
    
    def generate_report(self, results: List[BenchmarkResult]) -> Dict:
        """Generate a benchmark report."""
        haiku_wins = sum(1 for r in results if r.winner == "haiku")
        
        avg_haiku_ratio = sum(r.haiku_ratio for r in results) / len(results)
        avg_llmlingua_ratio = sum(r.llmlingua_ratio for r in results) / len(results)
        avg_improvement = sum(r.improvement for r in results) / len(results)
        
        return {
            "summary": {
                "total_benchmarks": len(results),
                "haiku_wins": haiku_wins,
                "llmlingua_wins": len(results) - haiku_wins,
                "avg_haiku_compression": f"{avg_haiku_ratio*100:.1f}%",
                "avg_llmlingua_compression": f"{avg_llmlingua_ratio*100:.1f}%",
                "avg_improvement": f"{avg_improvement*100:.1f}%"
            },
            "details": [
                {
                    "name": r.document_name,
                    "original_tokens": r.original_tokens,
                    "haiku": {"tokens": r.haiku_tokens, "ratio": f"{r.haiku_ratio*100:.1f}%"},
                    "llmlingua": {"tokens": r.llmlingua_tokens, "ratio": f"{r.llmlingua_ratio*100:.1f}%"},
                    "winner": r.winner
                }
                for r in results
            ]
        }

def run_benchmarks():
    """Run the full benchmark suite."""
    
    # Sample documents
    documents = {
        "simple": "To restart the server, save the config and run the restart command.",
        "medium": """Before deploying, ensure all tests pass. Run the build script.
                     If build succeeds, execute deployment. Verify the service is running.
                     Warning: Skipping tests may cause production issues.""",
        "complex": """To perform a database migration, first create a backup using pg_dump.
                      Verify the backup is complete and valid. Run the migration script
                      with python manage.py migrate. After migration, verify all tables
                      exist and data integrity is maintained. If any errors occur,
                      restore from backup immediately."""
    }
    
    runner = BenchmarkRunner()
    results = runner.run_benchmark_suite(documents)
    report = runner.generate_report(results)
    
    # Save results
    with open("benchmarks/results.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*60)
    print("BENCHMARK RESULTS")
    print("="*60)
    print(json.dumps(report["summary"], indent=2))
    
    return report

if __name__ == "__main__":
    run_benchmarks()
```

---

## Expected Results

```json
{
  "summary": {
    "total_benchmarks": 3,
    "haiku_wins": 3,
    "llmlingua_wins": 0,
    "avg_haiku_compression": "62.5%",
    "avg_llmlingua_compression": "35.2%",
    "avg_improvement": "27.3%"
  }
}
```

---

## Acceptance Criteria

- [ ]  `llmlingua_[comparison.py](http://comparison.py)` created
- [ ]  Benchmarks run on 3+ documents
- [ ]  Results saved to `results.json`
- [ ]  Report shows Haiku competitive with LLMLingua
- [ ]  Metrics are reproducible