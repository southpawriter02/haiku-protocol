# Running LLMLingua Baseline on Your MacBook (v0.0.3c)

These instructions guide you through running `llmlingua_baseline.py` natively on your M2 Max MacBook with 64 GB unified memory. Your hardware will use the MPS (Metal Performance Shaders) backend for GPU-accelerated inference.

**Estimated time:** 2–5 minutes total (including model download on first run)

---

## Prerequisites Check

Before running, verify these files exist in your project root:

```bash
cd ~/path/to/haiku-protocol   # adjust to your actual project path

# These must exist (from v0.0.3a and v0.0.3b)
ls benchmarks/samples/simple.md benchmarks/samples/medium.md benchmarks/samples/complex.md
ls benchmarks/raw_metrics.json
```

If any file is missing, the script will exit with a clear error telling you which prerequisite to run first.

---

## Step 1: Install Dependencies

The script requires `llmlingua` and `torch` (PyTorch). If you're using a virtual environment, activate it first. If not, install globally:

```bash
# Option A: If you have a venv
python3 -m venv .venv
source .venv/bin/activate

# Option B: Direct install (either way, run these)
pip install llmlingua torch tiktoken
```

**What gets installed:**
- `llmlingua` — The prompt compression library (small package)
- `torch` — PyTorch, which llmlingua depends on (~2 GB download, but you may already have it)
- `tiktoken` — OpenAI's tokenizer for consistent token counting

**Verify installation:**

```bash
python3 -c "import llmlingua; print('llmlingua:', llmlingua.__version__)"
python3 -c "import torch; print('torch:', torch.__version__); print('MPS available:', torch.backends.mps.is_available())"
```

You should see `MPS available: True` — this confirms your M2 Max's GPU will be used.

---

## Step 2: Run the Baseline Script

```bash
cd ~/path/to/haiku-protocol   # make sure you're in the project root
python3 benchmarks/llmlingua_baseline.py
```

**What happens:**
1. The script detects your MPS GPU and prints device info
2. It downloads the `microsoft/phi-2` model from Hugging Face (~5.4 GB, **first run only** — it's cached for subsequent runs at `~/.cache/huggingface/`)
3. It compresses all 3 sample documents (Simple, Medium, Complex) at 50% compression rate
4. It prints a formatted results table and saves JSON output

**Expected output (something like):**

```
=================================================================
LLMLINGUA BASELINE RESULTS (v0.0.3c)
=================================================================

Device: mps
GPU: Apple Metal Performance Shaders
LLMLingua version: 0.2.x
Configuration: rate=50%, algorithm=v1

-----------------------------------------------------------------
Tier        Original  Compressed    Ratio   Time(s)  Status
-----------------------------------------------------------------
Simple          101          ~51    50.xx%    ~2.xxs  OK
Medium          443         ~213    48.xx%    ~3.xxs  OK
Complex        1589         ~731    46.xx%    ~7.xxs  OK

-----------------------------------------------------------------
COMPARISON: LLMLingua vs. Haiku Protocol Targets
-----------------------------------------------------------------
Tier        LLMLingua  Haiku Target          Status
-----------------------------------------------------------------
Simple        50.xx%        35-40%  Baseline set
Medium        48.xx%        40-50%  Baseline set
Complex       46.xx%        45-55%  Baseline set

=================================================================
Output saved to: /path/to/benchmarks/llmlingua_baseline.json
=================================================================
```

---

## Step 3: Verify the Output

```bash
# Check the output file exists and is valid JSON
python3 -m json.tool benchmarks/llmlingua_baseline.json > /dev/null && echo "Valid JSON"

# Quick peek at the results
python3 -c "
import json
with open('benchmarks/llmlingua_baseline.json') as f:
    data = json.load(f)
print('Version:', data['version'])
print('LLMLingua:', data['llmlingua_version'])
print('Device:', data['hardware']['device_used'])
print('Documents:', len(data['documents']))
for doc in data['documents']:
    m = doc['metrics']
    print(f\"  {doc['tier']}: {m['original_tokens']} -> {m['compressed_tokens']} tokens ({m['compression_ratio']:.2%})\")
"
```

---

## Step 4: What I Need Back

Once the script completes successfully, I need the contents of the output JSON file. You can either:

**Option A (easiest):** Just paste the raw JSON output:
```bash
cat benchmarks/llmlingua_baseline.json
```
Copy the output and paste it here.

**Option B:** If the file is already in the project folder I'm connected to, just tell me it's done and I'll read it directly.

---

## Troubleshooting

**Issue: `ModuleNotFoundError: No module named 'llmlingua'`**
→ Run `pip install llmlingua`

**Issue: MPS shows as unavailable**
→ Ensure you're running Python 3.10+ with a recent PyTorch version: `pip install --upgrade torch`

**Issue: Model download hangs or fails**
→ The `microsoft/phi-2` model downloads from Hugging Face. Check your internet connection. If behind a proxy, set `HF_ENDPOINT` or `HTTPS_PROXY` environment variables.

**Issue: `torch.backends.mps` not found**
→ Your PyTorch version may be too old for MPS. Run: `pip install torch>=2.0`

**Issue: Script takes >10 minutes**
→ Something may be wrong with MPS initialization. Try forcing CPU: Edit `COMPRESSION_CONFIG` or temporarily modify the device logic. But on your M2 Max with 64GB, this shouldn't happen.

**Issue: Compression ratios are >0.8 (barely compressed)**
→ Check that sample documents contain actual procedural text (not just headers or blank lines). Verify with `wc -w benchmarks/samples/*.md`.
