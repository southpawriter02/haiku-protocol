#!/usr/bin/env python3
"""
llmlingua_baseline.py - LLMLingua Baseline Execution for Haiku Protocol Benchmarking
=====================================================================================

Runs LLMLingua prompt compression on three curated sample documents using
standardized configuration parameters. Captures compression ratios, execution
times, compressed text previews, and semantic preservation notes. Provides
fallback estimation for GPU-limited or resource-constrained environments.

This script is the primary deliverable for v0.0.3c. It produces
``benchmarks/llmlingua_baseline.json``, which v0.0.3d merges with
``raw_metrics.json`` into the consolidated ``baseline_metrics.json``.

Functions:
    detect_gpu_availability: Check for CUDA, MPS, or CPU-only hardware
    initialize_compressor: Create and configure a PromptCompressor instance
    compress_document: Run LLMLingua compression on a single document string
    count_compressed_tokens: Count tokens in compressed text for ratio calc
    estimate_compression_result: Generate fallback estimated metrics when
        LLMLingua is unavailable or too slow
    build_document_result: Assemble the full result dict for one document
    analyze_llmlingua_results: Read a sample file and run compression pipeline
    build_comparison_table: Generate a summary comparison across all tiers
    run_baseline: Orchestrate the full baseline execution across all documents
    main: CLI entry point

Configuration:
    COMPRESSION_CONFIG: Dict of LLMLingua parameters (50% rate, v1 algorithm)
    ESTIMATED_COMPRESSION_RATIOS: Fallback ratios by tier if LLMLingua unavailable
    SAMPLE_FILES: Ordered list of (filename, tier_label) tuples

Implementation Status:
    - IMPLEMENTATION: Phase 0 (v0.0.3c)

Related:
    - v0.0.3c — LLMLingua Baseline Execution (spec)
    - v0.0.3b — Token Counting & Raw Metrics Collection (prerequisite)
    - v0.0.3a — Sample Document Selection & Curation (prerequisite)
    - v0.0.3d — Metrics Documentation & Reporting (downstream consumer)
"""

import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Configuration Constants ──
# These match the spec's "Configuration Parameters" table exactly.
# Rationale documented in v0.0.3c spec: 50% compression rate is a balanced
# target; LLMLingua v1 is more stable and reproducible than v2 (beta);
# full context preservation ensures fair comparison across document tiers.

COMPRESSION_CONFIG: Dict[str, Any] = {
    "compression_rate": 0.5,
    "target_token": None,
    "use_llmlingua2": False,
    "context_budget": -1,
    "target_context_budget": None,
    "min_compress_ratio": 0.5,
}

# Fallback estimation ratios (from spec: "Mock Results Configuration")
# Used when LLMLingua is unavailable or execution fails.
ESTIMATED_COMPRESSION_RATIOS: Dict[str, float] = {
    "Simple": 0.52,
    "Medium": 0.48,
    "Complex": 0.46,
}

# Haiku Protocol target compression ratios per tier (from spec comparison table)
# These represent the project's aspirational improvement over LLMLingua.
HAIKU_TARGET_RATIOS: Dict[str, str] = {
    "Simple": "35-40%",
    "Medium": "40-50%",
    "Complex": "45-55%",
}

# Sample files and their tier labels, matching v0.0.3a output
SAMPLE_FILES: List[Tuple[str, str]] = [
    ("simple.md", "Simple"),
    ("medium.md", "Medium"),
    ("complex.md", "Complex"),
]


def detect_gpu_availability() -> Tuple[bool, Optional[str]]:
    """
    Detect GPU availability and return hardware status.

    Checks for CUDA (NVIDIA), MPS (Apple Silicon), or CPU-only
    environments in that priority order. The detection result determines
    which PyTorch device the LLMLingua compressor will use.

    Returns:
        Tuple of (has_gpu, device_name) where has_gpu is True if any
        GPU backend is available, and device_name is a human-readable
        string identifying the GPU (or None for CPU-only).

    Example:
        >>> has_gpu, name = detect_gpu_availability()
        >>> has_gpu
        True
        >>> name
        'Apple Metal Performance Shaders'
    """
    logger.info("GPU detection started")

    try:
        import torch
    except ImportError:
        logger.warning("PyTorch not installed; cannot detect GPU")
        return False, None

    # Priority 1: NVIDIA CUDA
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        logger.info("GPU detected: CUDA — %s", device_name)
        return True, device_name

    # Priority 2: Apple Metal Performance Shaders
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        logger.info("GPU detected: Apple Metal Performance Shaders")
        return True, "Apple Metal Performance Shaders"

    # Priority 3: CPU only
    logger.info("GPU detection complete: no GPU found, using CPU")
    return False, None


def initialize_compressor(
    device: str = "cuda",
) -> Optional[Any]:
    """
    Initialize the LLMLingua PromptCompressor with automatic fallback.

    Attempts to create a PromptCompressor using the specified device.
    If the primary device fails (e.g., CUDA not available), automatically
    falls back to CPU. Tries multiple model names in priority order:
    NousResearch/Llama-2-7b-hf (LLMLingua default), then microsoft/phi-2
    (lightweight alternative).

    Args:
        device: PyTorch device string. One of "cuda", "mps", or "cpu".
            Defaults to "cuda"; the caller should pass the appropriate
            device based on ``detect_gpu_availability()`` results.

    Returns:
        A PromptCompressor instance if initialization succeeds, or None
        if all initialization attempts fail.

    Example:
        >>> compressor = initialize_compressor("mps")
        >>> compressor is not None
        True
    """
    logger.info("Compressor initialization started: device=%s", device)

    try:
        from llmlingua import PromptCompressor
    except ImportError:
        logger.error("llmlingua not installed; cannot initialize compressor")
        return None

    # Model candidates in priority order: LLMLingua default, then phi-2
    model_candidates = [
        "NousResearch/Llama-2-7b-hf",
        "microsoft/phi-2",
    ]

    # Attempt initialization on the requested device with each model
    for model_name in model_candidates:
        try:
            start_time = time.time()
            logger.info(
                "Trying model=%s on device=%s", model_name, device
            )
            compressor = PromptCompressor(
                model_name=model_name,
                device_map=device,
            )
            elapsed = time.time() - start_time
            logger.info(
                "Compressor initialized: model=%s, device=%s, time=%.2fs",
                model_name, device, elapsed
            )
            return compressor
        except Exception as exc:
            logger.warning(
                "Failed to initialize %s on %s: %s: %s",
                model_name, device, type(exc).__name__, exc
            )

    # Fallback to CPU if the requested device was not CPU
    if device != "cpu":
        logger.info("Falling back to CPU initialization")
        for model_name in model_candidates:
            try:
                start_time = time.time()
                logger.info(
                    "Trying model=%s on device=cpu (fallback)", model_name
                )
                compressor = PromptCompressor(
                    model_name=model_name,
                    device_map="cpu",
                )
                elapsed = time.time() - start_time
                logger.info(
                    "Compressor initialized: model=%s, device=cpu "
                    "(fallback), time=%.2fs",
                    model_name, elapsed
                )
                return compressor
            except Exception as exc:
                logger.error(
                    "Failed to initialize %s on CPU: %s: %s",
                    model_name, type(exc).__name__, exc
                )

    logger.error("Compressor initialization failed on all devices and models")
    return None


def compress_document(
    compressor: Any,
    text: str,
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compress a single document using LLMLingua and return metrics.

    Passes the document text through the PromptCompressor with the
    given configuration. Captures the compressed text, compression
    ratio, and execution wall-clock time. On failure, returns an
    error result with the exception message.

    Args:
        compressor: An initialized PromptCompressor instance.
        text: The full document text to compress.
        config: Compression configuration dict matching
            ``COMPRESSION_CONFIG`` schema.

    Returns:
        Dictionary with keys:
            - ``success`` (bool): Whether compression completed
            - ``full_compressed_text`` (str): Complete compressed output
            - ``compressed_text_preview`` (str): First 200 chars
            - ``compressed_text_length`` (int): Length of compressed text
            - ``compression_ratio`` (float): Ratio from LLMLingua
            - ``execution_time_seconds`` (float): Wall-clock time
            - ``semantic_preservation_notes`` (str): Description of config
        On failure, keys are: ``success``, ``error``, ``execution_time_seconds``

    Raises:
        ValueError: If text is None or empty, or compressor is None
    """
    if compressor is None:
        raise ValueError("Compressor must not be None")
    if text is None or not text.strip():
        raise ValueError("Text must not be None or empty")

    logger.info(
        "Document compression started: %d chars, rate=%.2f",
        len(text), config.get("compression_rate", 0.5)
    )

    start_time = time.time()

    try:
        # compress_prompt expects context as List[str], not a bare string.
        # We wrap the document in a list, which LLMLingua treats as a
        # single-context compression. The 'instruction' and 'question'
        # params are left as empty strings (no system prompt or query).
        #
        # NOTE: Only pass method-level params here. Constructor-level
        # params (use_llmlingua2, context_budget, target_context_budget,
        # min_compress_ratio) belong on PromptCompressor.__init__(), not
        # on compress_prompt(). Passing them here raises TypeError in
        # LLMLingua 0.2.x. Since we use v1 defaults (use_llmlingua2=False),
        # the constructor defaults are correct without explicit override.
        result = compressor.compress_prompt(
            context=[text],
            instruction="",
            question="",
            rate=config["compression_rate"],
        )
        elapsed = time.time() - start_time

        compressed_text = result.get("compressed_prompt", "")
        compression_ratio = result.get("ratio", 0.0)
        # LLMLingua returns 'ratio' as the key in newer versions,
        # fall back to 'compression_ratio' for older versions
        if compression_ratio == 0.0:
            compression_ratio = result.get("compression_ratio", 0.0)

        logger.info(
            "Document compression complete: ratio=%.4f, time=%.2fs, "
            "output_length=%d",
            compression_ratio, elapsed, len(compressed_text)
        )

        return {
            "success": True,
            "full_compressed_text": compressed_text,
            "compressed_text_preview": compressed_text[:200],
            "compressed_text_length": len(compressed_text),
            "compression_ratio": round(compression_ratio, 4),
            "execution_time_seconds": round(elapsed, 2),
            "semantic_preservation_notes": (
                "Default LLMLingua v1 with %.0f%% compression rate"
                % (config["compression_rate"] * 100)
            ),
        }

    except Exception as exc:
        elapsed = time.time() - start_time
        error_detail = "%s: %s" % (type(exc).__name__, exc)
        logger.error(
            "Document compression failed after %.2fs: %s",
            elapsed, error_detail
        )
        return {
            "success": False,
            "error": error_detail,
            "execution_time_seconds": round(elapsed, 2),
        }


def count_compressed_tokens(text: str) -> int:
    """
    Count tokens in compressed text using the same tokenizer as v0.0.3b.

    Reuses the tokenizer logic from ``baseline_metrics.py`` to ensure
    consistent measurement between raw and compressed token counts.
    Falls back to a rough word-based estimate if the tokenizer cannot
    be initialized.

    Args:
        text: Compressed text string to tokenize

    Returns:
        Token count (int)

    Raises:
        ValueError: If text is None
    """
    if text is None:
        raise ValueError("Cannot tokenize None input")

    # Attempt to reuse baseline_metrics tokenizer for consistency
    try:
        from benchmarks.baseline_metrics import count_tokens
        token_count = count_tokens(text)
        logger.debug("Compressed token count (baseline_metrics): %d", token_count)
        return token_count
    except ImportError:
        logger.debug("baseline_metrics not importable; trying direct tokenizer")

    # Direct tiktoken attempt
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        token_count = len(encoding.encode(text))
        logger.debug("Compressed token count (tiktoken): %d", token_count)
        return token_count
    except Exception:
        logger.debug("tiktoken unavailable; trying regex fallback")

    # Regex fallback (same pattern as baseline_metrics.py)
    try:
        import regex
        pattern = regex.compile(
            r"'(?i:[sdmt]|ll|ve|re)"
            r"|[^\r\n\p{L}\p{N}]?+\p{L}+"
            r"|\p{N}{1,3}"
            r"| ?[^\s\p{L}\p{N}]++[\r\n]*"
            r"|\s*[\r\n]"
            r"|\s+(?!\S)"
            r"|\s+"
        )
        chunks = pattern.findall(text)
        token_count = len(chunks)
        logger.debug("Compressed token count (regex fallback): %d", token_count)
        return token_count
    except ImportError:
        pass

    # Last resort: rough word-based estimate
    # Multiplier of 1.3 accounts for subword tokenization overhead
    token_count = int(len(text.split()) * 1.3)
    logger.warning(
        "Token count using word estimate (no tokenizer available): %d",
        token_count
    )
    return token_count


def estimate_compression_result(
    tier: str,
    original_tokens: int,
) -> Dict[str, Any]:
    """
    Generate estimated compression metrics when LLMLingua is unavailable.

    Uses the ``ESTIMATED_COMPRESSION_RATIOS`` lookup table to produce
    plausible compression results. All estimated results are clearly
    flagged with ``cpu_only_estimated: True`` per the v0.0.3c spec's
    fallback plan.

    Args:
        tier: Document complexity tier ("Simple", "Medium", or "Complex")
        original_tokens: Original token count from raw_metrics.json

    Returns:
        Dictionary with keys: ``cpu_only_estimated``, ``original_tokens``,
        ``compressed_tokens``, ``compression_ratio``,
        ``execution_time_seconds``, ``semantic_preservation_notes``

    Raises:
        ValueError: If tier is not in ESTIMATED_COMPRESSION_RATIOS
    """
    if tier not in ESTIMATED_COMPRESSION_RATIOS:
        raise ValueError(
            "Unknown tier '%s'; expected one of %s"
            % (tier, list(ESTIMATED_COMPRESSION_RATIOS.keys()))
        )

    ratio = ESTIMATED_COMPRESSION_RATIOS[tier]
    compressed_tokens = int(original_tokens * ratio)

    logger.info(
        "Estimated compression for %s: ratio=%.2f, "
        "original=%d, compressed=%d (estimated)",
        tier, ratio, original_tokens, compressed_tokens
    )

    return {
        "cpu_only_estimated": True,
        "original_tokens": original_tokens,
        "compressed_tokens": compressed_tokens,
        "compression_ratio": ratio,
        "execution_time_seconds": 0,
        "semantic_preservation_notes": (
            "LLMLingua not executed (GPU unavailable or library missing). "
            "Compression ratio is estimated based on token density."
        ),
    }


def build_document_result(
    tier: str,
    file_path: Path,
    device: str,
    has_gpu: bool,
    gpu_name: Optional[str],
    metrics: Dict[str, Any],
    compressed_preview: str,
    notes: str,
) -> Dict[str, Any]:
    """
    Assemble the full result dictionary for a single document.

    Combines hardware info, compression metrics, and semantic notes
    into the JSON-ready structure that matches the
    ``llmlingua_baseline.json`` schema from the v0.0.3c spec.

    Args:
        tier: Document complexity tier label
        file_path: Path to the source sample document
        device: PyTorch device string used for compression
        has_gpu: Whether GPU was detected
        gpu_name: Human-readable GPU name (or None)
        metrics: Dict with original_tokens, compressed_tokens,
            compression_ratio, execution_time_seconds
        compressed_preview: First 200 chars of compressed text
        notes: Semantic preservation notes string

    Returns:
        Complete document result dict matching the output JSON schema
    """
    result = {
        "tier": tier,
        "file_path": str(file_path),
        "device_used": device,
        "gpu_available": has_gpu,
        "gpu_name": gpu_name,
        "metrics": {
            "original_tokens": metrics["original_tokens"],
            "compressed_tokens": metrics["compressed_tokens"],
            "compression_ratio": metrics["compression_ratio"],
            "execution_time_seconds": metrics["execution_time_seconds"],
        },
        "compressed_text_preview": compressed_preview,
        "semantic_preservation_notes": notes,
    }

    # Propagate the cpu_only_estimated flag if present
    if metrics.get("cpu_only_estimated"):
        result["cpu_only_estimated"] = True

    logger.debug(
        "Document result built: tier=%s, ratio=%.4f, estimated=%s",
        tier,
        metrics["compression_ratio"],
        metrics.get("cpu_only_estimated", False),
    )
    return result


def analyze_llmlingua_results(
    file_path: Path,
    tier: str,
    compressor: Optional[Any],
    device: str,
    has_gpu: bool,
    gpu_name: Optional[str],
    raw_metrics_token_count: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Read a sample document and run the full compression pipeline.

    Reads the document from disk, uses the authoritative token count
    from raw_metrics.json (v0.0.3b output) for original_tokens, runs
    LLMLingua compression (or estimation if compressor is None),
    counts compressed tokens, and assembles the result dictionary.
    The compressor is initialized once in ``run_baseline()`` and
    shared across all documents for efficiency.

    Args:
        file_path: Path to the sample .md file
        tier: Complexity tier label ("Simple", "Medium", or "Complex")
        compressor: An initialized PromptCompressor, or None to use
            fallback estimation
        device: PyTorch device string used
        has_gpu: Whether GPU was detected
        gpu_name: Human-readable GPU identifier (or None)
        raw_metrics_token_count: Authoritative token count from
            raw_metrics.json (v0.0.3b). If provided, used as
            original_tokens for consistency with upstream metrics.
            If None, falls back to local re-counting.

    Returns:
        Document result dict (from ``build_document_result``) on success,
        or a dict with ``error`` key on failure
    """
    logger.info("Analysis started: %s (tier=%s)", file_path.name, tier)

    # ── Read Document ──
    try:
        text = file_path.read_text(encoding="utf-8")
    except (OSError, IOError) as exc:
        logger.error("Failed to read %s: %s", file_path, exc)
        return {
            "tier": tier,
            "file_path": str(file_path),
            "error": "Failed to read document: %s" % str(exc),
        }

    # ── Determine Original Token Count ──
    # Prefer the authoritative count from raw_metrics.json (v0.0.3b)
    # to ensure consistency across the v0.0.3x pipeline. Only fall
    # back to local re-counting if the upstream value is unavailable.
    if raw_metrics_token_count is not None:
        original_tokens = raw_metrics_token_count
        logger.info(
            "Original token count for %s: %d tokens (from raw_metrics.json)",
            tier, original_tokens
        )
    else:
        original_tokens = count_compressed_tokens(text)
        logger.info(
            "Original token count for %s: %d tokens (locally counted)",
            tier, original_tokens
        )

    # ── Compress or Estimate ──
    if compressor is not None:
        compression_result = compress_document(compressor, text, COMPRESSION_CONFIG)

        if compression_result["success"]:
            full_compressed = compression_result["full_compressed_text"]
            compressed_tokens = count_compressed_tokens(full_compressed)
            preview = compression_result["compressed_text_preview"]
            notes = compression_result["semantic_preservation_notes"]

            metrics = {
                "original_tokens": original_tokens,
                "compressed_tokens": compressed_tokens,
                "compression_ratio": compression_result["compression_ratio"],
                "execution_time_seconds": compression_result[
                    "execution_time_seconds"
                ],
            }

            logger.info(
                "Compression succeeded for %s: "
                "original=%d, compressed=%d, ratio=%.4f",
                tier, original_tokens, compressed_tokens,
                compression_result["compression_ratio"]
            )

            return build_document_result(
                tier, file_path, device, has_gpu, gpu_name,
                metrics, preview, notes
            )
        else:
            # Compression failed; fall through to estimation.
            # Surface the error in both log and JSON output so the
            # caller can diagnose without needing terminal access.
            compression_error = compression_result.get("error", "unknown error")
            logger.warning(
                "Compression failed for %s: %s — using estimation fallback",
                tier, compression_error
            )

    else:
        compression_error = "compressor is None (initialization failed)"
        logger.warning("No compressor available for %s", tier)

    # ── Fallback Estimation ──
    logger.info("Using estimation fallback for %s", tier)
    estimated = estimate_compression_result(tier, original_tokens)

    # Include the compression error reason in the notes so it's
    # visible in the JSON output (not just in terminal logs).
    fallback_notes = estimated["semantic_preservation_notes"]
    if compression_error:
        fallback_notes += " Error: %s" % compression_error

    return build_document_result(
        tier, file_path, device, has_gpu, gpu_name,
        estimated,
        "(estimated — no compressed text available)",
        fallback_notes,
    )


def build_comparison_table(
    documents: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Generate a summary comparison table across all document tiers.

    Creates a list of dicts with tier, original tokens, compressed
    tokens, LLMLingua ratio, and Haiku target ratio for each
    successfully processed document. Used for the comparison table
    in the output JSON and for human-readable summary output.

    Args:
        documents: List of document result dicts from ``run_baseline()``

    Returns:
        List of comparison row dicts, one per document, with keys:
        ``tier``, ``original_tokens``, ``compressed_tokens``,
        ``llmlingua_ratio``, ``target_haiku_ratio``
    """
    logger.info("Building comparison table for %d documents", len(documents))

    table = []
    for doc in documents:
        if "error" in doc:
            logger.debug("Skipping errored document: %s", doc.get("tier"))
            continue

        tier = doc["tier"]
        metrics = doc["metrics"]
        row = {
            "tier": tier,
            "original_tokens": metrics["original_tokens"],
            "compressed_tokens": metrics["compressed_tokens"],
            "llmlingua_ratio": metrics["compression_ratio"],
            "target_haiku_ratio": HAIKU_TARGET_RATIOS.get(tier, "N/A"),
            "estimated": doc.get("cpu_only_estimated", False),
        }
        table.append(row)

        logger.debug(
            "Comparison row: %s — LLMLingua=%.4f, Haiku target=%s%s",
            tier,
            metrics["compression_ratio"],
            HAIKU_TARGET_RATIOS.get(tier, "N/A"),
            " (estimated)" if row["estimated"] else ""
        )

    logger.info("Comparison table built: %d rows", len(table))
    return table


def run_baseline(
    samples_dir: Path,
    raw_metrics_path: Path,
    output_path: Path,
) -> Dict[str, Any]:
    """
    Orchestrate the full LLMLingua baseline execution.

    This is the primary workflow function. It:
    1. Verifies prerequisites (raw_metrics.json and samples directory)
    2. Loads authoritative token counts from raw_metrics.json (v0.0.3b)
    3. Detects GPU availability
    4. Initializes the LLMLingua compressor (or prepares fallback)
    5. Records the LLMLingua library version
    6. Processes each sample document (passing upstream token counts)
    7. Builds the comparison table
    8. Writes results to the output JSON file

    Args:
        samples_dir: Path to ``benchmarks/samples/`` directory
        raw_metrics_path: Path to ``benchmarks/raw_metrics.json``
        output_path: Path to write ``benchmarks/llmlingua_baseline.json``

    Returns:
        The complete results dictionary (also saved to output_path)

    Raises:
        FileNotFoundError: If samples_dir or raw_metrics_path don't exist
        SystemExit: If critical prerequisites are missing
    """
    logger.info("LLMLingua baseline execution started")
    baseline_start = time.time()

    # ── Verify Prerequisites ──
    if not raw_metrics_path.exists():
        logger.error("raw_metrics.json not found: %s", raw_metrics_path)
        raise FileNotFoundError(
            "benchmarks/raw_metrics.json not found. Run v0.0.3b first."
        )

    if not samples_dir.exists():
        logger.error("Samples directory not found: %s", samples_dir)
        raise FileNotFoundError(
            "benchmarks/samples/ not found. Run v0.0.3a first."
        )

    logger.info("Prerequisites verified: raw_metrics and samples exist")

    # ── Load Raw Metrics Token Counts ──
    # Read the authoritative token counts from v0.0.3b's output so
    # original_tokens in this pipeline match the upstream measurements
    # exactly, regardless of which tokenizer fallback is available.
    raw_metrics_tokens: Dict[str, int] = {}
    try:
        with open(raw_metrics_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        for doc_entry in raw_data.get("documents", []):
            tier_name = doc_entry.get("tier")
            token_count = doc_entry.get("metrics", {}).get("token_count")
            if tier_name and token_count is not None:
                raw_metrics_tokens[tier_name] = token_count
        logger.info(
            "Loaded raw_metrics token counts: %s",
            {k: v for k, v in raw_metrics_tokens.items()}
        )
    except (json.JSONDecodeError, KeyError) as exc:
        logger.warning(
            "Could not parse raw_metrics.json token counts: %s "
            "(will fall back to local counting)",
            exc
        )

    # ── Detect GPU ──
    has_gpu, gpu_name = detect_gpu_availability()

    # Determine best device: CUDA > MPS > CPU
    if has_gpu and gpu_name and "Metal" in gpu_name:
        device = "mps"
    elif has_gpu:
        device = "cuda"
    else:
        device = "cpu"

    logger.info("Selected device: %s (gpu=%s, name=%s)", device, has_gpu, gpu_name)

    # ── Initialize Compressor ──
    compressor = initialize_compressor(device)

    if compressor is None:
        logger.warning(
            "LLMLingua compressor unavailable; all results will be estimated"
        )

    # ── Record LLMLingua Version ──
    llmlingua_version = "not_installed"
    try:
        import llmlingua as _llm
        llmlingua_version = getattr(_llm, "__version__", "unknown")
        logger.info("LLMLingua version: %s", llmlingua_version)
    except ImportError:
        logger.warning("LLMLingua not installed; version recorded as not_installed")

    # ── Initialize Results Structure ──
    results = {
        "version": "0.0.3c",
        "llmlingua_version": llmlingua_version,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "configuration": COMPRESSION_CONFIG,
        "hardware": {
            "device_used": device,
            "gpu_available": has_gpu,
            "gpu_name": gpu_name,
        },
        "documents": [],
        "comparison_table": [],
    }

    # ── Process Each Document ──
    for filename, tier in SAMPLE_FILES:
        file_path = samples_dir / filename

        if not file_path.exists():
            logger.warning("Sample file not found: %s (skipping)", file_path)
            continue

        doc_result = analyze_llmlingua_results(
            file_path, tier, compressor, device, has_gpu, gpu_name,
            raw_metrics_token_count=raw_metrics_tokens.get(tier),
        )
        results["documents"].append(doc_result)

        if "error" not in doc_result:
            logger.info(
                "Document processed: %s — ratio=%.4f",
                tier, doc_result["metrics"]["compression_ratio"]
            )
        else:
            logger.error(
                "Document failed: %s — %s", tier, doc_result["error"]
            )

    # ── Build Comparison Table ──
    results["comparison_table"] = build_comparison_table(results["documents"])

    # ── Write Output ──
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    baseline_elapsed = time.time() - baseline_start
    logger.info(
        "LLMLingua baseline execution complete: %d documents, "
        "total_time=%.2fs, output=%s",
        len(results["documents"]), baseline_elapsed, output_path
    )

    return results


def main() -> Dict[str, Any]:
    """
    CLI entry point: run the LLMLingua baseline and print summary.

    Resolves project paths, invokes ``run_baseline()``, and prints
    a human-readable summary of compression results to stdout.

    Returns:
        The results dictionary (also saved to benchmarks/llmlingua_baseline.json)
    """
    # ── Resolve Paths ──
    project_root = Path(__file__).parent.parent
    samples_dir = project_root / "benchmarks" / "samples"
    raw_metrics_path = project_root / "benchmarks" / "raw_metrics.json"
    output_path = project_root / "benchmarks" / "llmlingua_baseline.json"

    logger.info("Project root: %s", project_root)
    logger.info("Samples directory: %s", samples_dir)
    logger.info("Output path: %s", output_path)

    # ── Execute Baseline ──
    results = run_baseline(samples_dir, raw_metrics_path, output_path)

    # ── Print Summary ──
    print("\n" + "=" * 65)
    print("LLMLINGUA BASELINE RESULTS (v0.0.3c)")
    print("=" * 65)

    hw = results.get("hardware", {})
    print("\nDevice: %s" % hw.get("device_used", "unknown"))
    if hw.get("gpu_name"):
        print("GPU: %s" % hw["gpu_name"])
    print("LLMLingua version: %s" % results.get("llmlingua_version", "unknown"))
    print("Configuration: rate=%.0f%%, algorithm=%s" % (
        COMPRESSION_CONFIG["compression_rate"] * 100,
        "v1" if not COMPRESSION_CONFIG["use_llmlingua2"] else "v2",
    ))

    print("\n" + "-" * 65)
    print("%-10s  %10s  %10s  %8s  %8s  %s" % (
        "Tier", "Original", "Compressed", "Ratio", "Time(s)", "Status"
    ))
    print("-" * 65)

    for doc in results["documents"]:
        if "error" in doc:
            print("%-10s  %s" % (doc["tier"], doc["error"]))
            continue

        m = doc["metrics"]
        estimated = " (est)" if doc.get("cpu_only_estimated") else ""
        print("%-10s  %10d  %10d  %7.2f%%  %7.2fs  %s" % (
            doc["tier"],
            m["original_tokens"],
            m["compressed_tokens"],
            m["compression_ratio"] * 100,
            m["execution_time_seconds"],
            "OK%s" % estimated
        ))

    # ── Comparison Table ──
    if results.get("comparison_table"):
        print("\n" + "-" * 65)
        print("COMPARISON: LLMLingua vs. Haiku Protocol Targets")
        print("-" * 65)
        print("%-10s  %12s  %12s  %15s" % (
            "Tier", "LLMLingua", "Haiku Target", "Status"
        ))
        print("-" * 65)
        for row in results["comparison_table"]:
            est_flag = " (est)" if row.get("estimated") else ""
            print("%-10s  %11.2f%%  %12s  %s" % (
                row["tier"],
                row["llmlingua_ratio"] * 100,
                row["target_haiku_ratio"],
                "Baseline set%s" % est_flag
            ))

    print("\n" + "=" * 65)
    print("Output saved to: %s" % output_path)
    print("=" * 65)

    return results


if __name__ == "__main__":
    # ── Logging Setup ──
    logging.basicConfig(
        level=logging.DEBUG,
        format=(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d"
            " | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    main()
