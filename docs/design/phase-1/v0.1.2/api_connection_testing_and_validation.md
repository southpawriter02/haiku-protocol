# v0.1.2d — API Connection Testing & Validation

<aside>

**Version:** 0.1.2d

**Parent:** v0.1.2 — API Configuration & Secrets

**Status:** ⬜ Not Started

**Duration:** 5–10 minutes

**Deliverable:** `tests/test_api.py` with test_api_connection() function that validates OpenAI API key and connectivity

</aside>

---

## Objective

Create `tests/test_api.py` with a test_api_connection() function that uses the Config class (from v0.1.2c) to load the OPENAI_API_KEY and attempts a test API call to OpenAI using ChatOpenAI from langchain_openai. Implement error handling for invalid keys, network timeouts, and rate limiting. Use max_tokens=10 to minimize API costs. Verify that the API connection works before proceeding to development.

---

## API Testing Architecture

### Validation Flow

```
┌────────────────────────────────────────────────────────────┐
│            API Connection Test Workflow                    │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Step 1: Load Configuration                               │
│  ┌────────────────────────────────────────────────────┐   │
│  │ from src.config import Config                      │   │
│  │ Config.validate()  # Verify API key exists        │   │
│  └────────────────────────────────────────────────────┘   │
│                          │                                 │
│                          ▼                                 │
│  Step 2: Initialize ChatOpenAI Client                      │
│  ┌────────────────────────────────────────────────────┐   │
│  │ llm = ChatOpenAI(                                  │   │
│  │   api_key=Config.OPENAI_API_KEY,                 │   │
│  │   model=Config.OPENAI_MODEL,                      │   │
│  │   max_tokens=10  # Minimize cost                 │   │
│  │ )                                                  │   │
│  └────────────────────────────────────────────────────┘   │
│                          │                                 │
│                          ▼                                 │
│  Step 3: Send Test Request                                │
│  ┌────────────────────────────────────────────────────┐   │
│  │ response = llm.invoke("Say 'API OK'")              │   │
│  └────────────────────────────────────────────────────┘   │
│                          │                                 │
│        ┌─────────────────┼─────────────────┐              │
│        ▼                 ▼                 ▼              │
│   ✅ Success      ⚠️  Warning       ❌ Error            │
│   (Response OK)  (Timeout, etc)   (Bad Key, etc)       │
│        │                 │                 │              │
│        └─────────────────┼─────────────────┘              │
│                          ▼                                 │
│  Step 4: Report Results                                   │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Print summary with status                          │   │
│  │ Return True/False                                  │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Error Handling Decision Tree

```
┌──────────────────────────────────────────────────┐
│  Exception during API call?                      │
├──────────────────────────────────────────────────┤
│                     │                             │
│        ┌────────────┼────────────┐               │
│        │            │            │               │
│        ▼            ▼            ▼               │
│    AuthError   TimeoutError  NetworkError      │
│        │            │            │               │
│        ▼            ▼            ▼               │
│    ❌ INVALID  ⚠️  TIMEOUT   ❌ NETWORK       │
│    API KEY    RETRY LATER    CHECK INTERNET   │
│                                                 │
│    StatusCode: 401           StatusCode: 429   │
│    Msg: "invalid_api_key"    Msg: "rate limit" │
│                                                 │
└──────────────────────────────────────────────────┘
```

---

## Source Code: tests/test_api.py

```python
#!/usr/bin/env python3
"""
API Connection Testing Module for Haiku Protocol

Tests connectivity to OpenAI API and validates that the configured
API key is valid and can be used to make successful requests.

Usage:
    python tests/test_api.py
    # or
    pytest tests/test_api.py::test_api_connection

Exit Codes:
    0 - API connection successful
    1 - API connection failed
"""

import os
import sys
from pathlib import Path

# Add src directory to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import Config


# ============================================
# API Connection Test
# ============================================

def test_api_connection(verbose: bool = True) -> bool:
    """
    Test OpenAI API connection and key validity.

    This function:
    1. Loads configuration from .env via Config class
    2. Validates that OPENAI_API_KEY is present and valid
    3. Initializes ChatOpenAI client with the API key
    4. Sends a test prompt to verify connectivity
    5. Handles and reports various error scenarios

    Args:
        verbose (bool): If True, print detailed output; else print minimal

    Returns:
        bool: True if API connection successful and validated, False otherwise

    Raises:
        Nothing - all exceptions caught and reported

    Error Scenarios Handled:
        - Missing API key (empty or not set)
        - Invalid API key format (doesn't start with 'sk-')
        - Invalid API key (correct format but unauthorized)
        - Network timeout (OpenAI API slow or unreachable)
        - Rate limiting (too many requests)
        - Rate limit exceeded (429 error)
        - Internal server errors (5xx errors)

    Cost Awareness:
        - Uses max_tokens=10 to minimize API cost (~$0.0001 per call)
        - Consider running only once per development session
    """

    if verbose:
        print("\n" + "=" * 70)
        print("Haiku Protocol — API Connection Test (v0.1.2d)")
        print("=" * 70)

    # ----------------------------------------
    # Step 1: Validate Configuration
    # ----------------------------------------

    if verbose:
        print("\n[1/3] Validating configuration...")

    if not Config.validate():
        if verbose:
            print("\n❌ Configuration validation failed")
            print("   Please check .env file and run again\n")
        return False

    api_key = Config.get_openai_api_key()

    # ----------------------------------------
    # Step 2: Initialize LLM Client
    # ----------------------------------------

    if verbose:
        print("[2/3] Initializing OpenAI client...")

    try:
        # Import here to avoid dependency errors if langchain not installed
        from langchain_openai import ChatOpenAI

        # Create LLM instance with config values
        llm = ChatOpenAI(
            api_key=api_key,
            model=Config.get_openai_model(),
            temperature=0,  # Deterministic (no randomness)
            max_tokens=10,  # Minimize cost
            timeout=10,  # 10 second timeout
            max_retries=1  # No retries for test (fail fast)
        )

        if verbose:
            print(f"   Model: {Config.get_openai_model()}")
            print(f"   Timeout: 10 seconds")

    except ImportError as e:
        if verbose:
            print(f"\n❌ Import Error: {e}")
            print("   Is langchain-openai installed?")
            print("   Run: pip install langchain-openai\n")
        return False

    except Exception as e:
        if verbose:
            print(f"\n❌ Client Initialization Error: {e}\n")
        return False

    # ----------------------------------------
    # Step 3: Send Test Request
    # ----------------------------------------

    if verbose:
        print("[3/3] Sending test request to API...")

    try:
        # Simple test prompt
        test_prompt = "Respond with just the word 'OK' and nothing else"

        response = llm.invoke(test_prompt)

        # Extract response text
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)

        if verbose:
            print(f"\n✅ API Response Received:")
            print(f"   Content: {response_text[:50]}...")
            print(f"   Length: {len(response_text)} characters")

        return True

    # ----------------------------------------
    # Error Handling: Authentication Issues
    # ----------------------------------------

    except Exception as e:
        error_str = str(e)
        error_type = type(e).__name__

        if verbose:
            print(f"\n❌ API Request Failed")
            print(f"   Error Type: {error_type}")
            print(f"   Error Message: {error_str[:200]}")

        # Categorize error for better troubleshooting
        if "401" in error_str or "Unauthorized" in error_str or "invalid_api_key" in error_str:
            if verbose:
                print("\n   Diagnosis: Invalid API Key")
                print("   The API key is invalid or has been revoked.")
                print("\n   Actions:")
                print("   1. Go to https://platform.openai.com/api-keys")
                print("   2. Create a new API key")
                print("   3. Update .env: OPENAI_API_KEY=sk-your-new-key")
                print("   4. Run this test again\n")
            return False

        elif "429" in error_str or "rate" in error_str.lower():
            if verbose:
                print("\n   Diagnosis: Rate Limit Exceeded")
                print("   Too many requests to OpenAI API.")
                print("\n   Actions:")
                print("   1. Wait a few minutes before retrying")
                print("   2. Check API usage at: https://platform.openai.com/account/usage")
                print("   3. Consider increasing API quota\n")
            return False

        elif "timeout" in error_str.lower() or "Connection" in error_str:
            if verbose:
                print("\n   Diagnosis: Network/Timeout Error")
                print("   Could not reach OpenAI API or request timed out.")
                print("\n   Actions:")
                print("   1. Check your internet connection")
                print("   2. Verify OpenAI status: https://status.openai.com")
                print("   3. Try again in a few moments\n")
            return False

        elif "model" in error_str.lower() and "does not exist" in error_str.lower():
            if verbose:
                print("\n   Diagnosis: Invalid Model Name")
                print(f"   Model '{Config.get_openai_model()}' does not exist")
                print("\n   Valid models:")
                print("   - gpt-4")
                print("   - gpt-4-turbo")
                print("   - gpt-3.5-turbo")
                print("\n   Actions:")
                print("   1. Update .env: OPENAI_MODEL=gpt-4")
                print("   2. Run this test again\n")
            return False

        else:
            if verbose:
                print(f"\n   Unknown Error: {error_type}")
                print("   See error message above for details.\n")
            return False


# ============================================
# Cost Analyzer (Optional)
# ============================================

def estimate_api_cost(num_requests: int = 1) -> dict:
    """
    Estimate API cost for running test_api_connection().

    The test uses:
    - Model: gpt-4 or configured model
    - Input: ~10 tokens
    - Output: max_tokens=10
    - Temperature: 0 (minimal variation)

    Args:
        num_requests (int): How many times test will be run

    Returns:
        dict with cost estimates

    Note:
        Actual cost depends on:
        - Current OpenAI API pricing (changes over time)
        - Exact model used
        - Input/output token counts
        - Any discounts or credits applied
    """

    # As of 2024, approximate pricing (check current rates)
    pricing = {
        "gpt-4": {
            "input": 0.00003,  # per 1K tokens
            "output": 0.00006  # per 1K tokens
        },
        "gpt-4-turbo": {
            "input": 0.00001,  # per 1K tokens
            "output": 0.00003  # per 1K tokens
        },
        "gpt-3.5-turbo": {
            "input": 0.0000005,  # per 1K tokens
            "output": 0.0000015  # per 1K tokens
        }
    }

    model = Config.get_openai_model()
    rates = pricing.get(model, pricing["gpt-4"])  # Default to gpt-4 rates

    # Typical test uses ~10 input + 10 output tokens
    input_tokens = 10
    output_tokens = 10

    input_cost = (input_tokens / 1000) * rates["input"] * num_requests
    output_cost = (output_tokens / 1000) * rates["output"] * num_requests
    total_cost = input_cost + output_cost

    return {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "num_requests": num_requests,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
        "note": "Costs are approximate; check OpenAI pricing for current rates"
    }


# ============================================
# Pytest Integration (for pytest runner)
# ============================================

def test_api_connection_pytest():
    """
    Pytest-compatible version of API connection test.

    Can be run with:
        pytest tests/test_api.py::test_api_connection_pytest

    Or run all tests:
        pytest tests/
    """
    assert test_api_connection(verbose=True), "API connection test failed"


# ============================================
# Direct Execution
# ============================================

if __name__ == "__main__":
    """
    Run API connection test when executed directly.

    Usage:
        python tests/test_api.py

    Output:
        - Configuration validation results
        - API client initialization
        - Test request and response
        - Overall success/failure status
        - Estimated API cost
    """

    print("\nHaiku Protocol — API Connection Validation")
    print("Starting test...\n")

    # Run the test
    success = test_api_connection(verbose=True)

    # Print cost estimate (informational)
    cost_estimate = estimate_api_cost(num_requests=1)
    print(f"\n💰 Cost Estimate:")
    print(f"   Model: {cost_estimate['model']}")
    print(f"   Input/Output Tokens: {cost_estimate['input_tokens']}/{cost_estimate['output_tokens']}")
    print(f"   Estimated Cost: ${cost_estimate['total_cost']:.8f}")
    print(f"   ({cost_estimate['note']})")

    print("=" * 70 + "\n")

    # Exit with appropriate code
    exit(0 if success else 1)
```

---

## Testing Strategy

### Test Coverage

```python
# test_api.py includes testing for:

✅ Configuration loaded correctly
✅ API key format valid
✅ ChatOpenAI client initialized
✅ API request succeeds
✅ Response received and parsed
✅ Error: Invalid API key (401)
✅ Error: Rate limited (429)
✅ Error: Network timeout
✅ Error: Invalid model name
✅ Error: Missing dependencies
✅ Cost estimation
```

### Running the Test

```bash
# Option 1: Direct execution
python tests/test_api.py

# Option 2: Pytest (if installed)
pytest tests/test_api.py

# Option 3: Pytest with verbose output
pytest tests/test_api.py -v -s

# Option 4: Run specific test function
pytest tests/test_api.py::test_api_connection_pytest -v
```

---

## Expected Output: Success Case

```
======================================================================
Haiku Protocol — API Connection Test (v0.1.2d)
======================================================================

[1/3] Validating configuration...
✅ Configuration validated successfully
   API Model: gpt-4
   API Key: sk-proj-...def0
   Debug Mode: False

[2/3] Initializing OpenAI client...
   Model: gpt-4
   Timeout: 10 seconds

[3/3] Sending test request to API...

✅ API Response Received:
   Content: OK...
   Length: 2 characters

======================================================================

💰 Cost Estimate:
   Model: gpt-4
   Input/Output Tokens: 10/10
   Estimated Cost: $0.00000060
   (Costs are approximate; check OpenAI pricing for current rates)

======================================================================
```

---

## Expected Output: Error Cases

### Case 1: Invalid API Key (401)

```
❌ API Request Failed
   Error Type: AuthenticationError
   Error Message: Error code: 401 - invalid_api_key

   Diagnosis: Invalid API Key
   The API key is invalid or has been revoked.

   Actions:
   1. Go to https://platform.openai.com/api-keys
   2. Create a new API key
   3. Update .env: OPENAI_API_KEY=sk-your-new-key
   4. Run this test again
```

---

### Case 2: Rate Limited (429)

```
❌ API Request Failed
   Error Type: RateLimitError
   Error Message: Error code: 429 - rate_limit_exceeded

   Diagnosis: Rate Limit Exceeded
   Too many requests to OpenAI API.

   Actions:
   1. Wait a few minutes before retrying
   2. Check API usage at: https://platform.openai.com/account/usage
   3. Consider increasing API quota
```

---

### Case 3: Network Timeout

```
❌ API Request Failed
   Error Type: APIConnectionError
   Error Message: Connection timeout after 10.0 seconds

   Diagnosis: Network/Timeout Error
   Could not reach OpenAI API or request timed out.

   Actions:
   1. Check your internet connection
   2. Verify OpenAI status: https://status.openai.com
   3. Try again in a few moments
```

---

## Cost Awareness & Optimization

### Minimizing API Costs

```python
# The test_api_connection function minimizes costs by:

1. max_tokens=10
   ├─ Limits response to 10 tokens max
   ├─ Reduces output cost by ~95%
   └─ Still sufficient to verify API works

2. temperature=0
   ├─ Deterministic output (no randomness)
   ├─ Minimal token variation
   └─ Consistent cost

3. max_retries=1
   ├─ Single attempt only (no retries)
   ├─ Prevents repeated failed requests
   └─ Fail fast

4. timeout=10
   ├─ 10 second timeout
   ├─ Prevents hanging indefinitely
   └─ Fast failure detection

# Typical cost per run: ~$0.0000006 (less than 1 millionth of a dollar)
```

### Cost Examples

```
Running test 1x:     ~$0.0000006  (negligible)
Running test 10x:    ~$0.000006   (negligible)
Running test 100x:   ~$0.00006    (negligible)
Running test 1000x:  ~$0.0006     (still tiny)

For comparison:
- Typical gpt-4 usage: ~$0.03 per request
- This test: ~0.0002% the cost of typical usage
```

---

## Integration with Development Workflow

### When to Run the Test

```
Workflow Step:          When to Run Test:
─────────────────────────────────────────────
Setup (v0.1.2):         ✅ After .env created (v0.1.2a)
Development:            ✅ Once per development session
Before deployment:      ✅ Verify API key still works
Debugging API issues:   ✅ Rule out configuration problems
CI/CD pipeline:         ⚠️  Run but handle gracefully
                           (secrets not available in CI)
```

---

## Pytest Configuration

### Optional: pytest.ini for test discovery

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

### Optional: conftest.py for test setup

```python
# tests/conftest.py - Pytest configuration

import os
import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent

@pytest.fixture
def config():
    """Load configuration for tests."""
    from src.config import Config
    return Config
```

---

## Acceptance Criteria

- [ ] `tests/test_api.py` file created
- [ ] `test_api_connection()` function implemented
- [ ] Function imports Config class from src/config.py
- [ ] Function calls Config.validate() before API call
- [ ] Function initializes ChatOpenAI with api_key from Config
- [ ] Function sets max_tokens=10 to minimize cost
- [ ] Function sets temperature=0 for deterministic output
- [ ] Function sends test prompt via llm.invoke()
- [ ] Function catches and handles authentication errors (401)
- [ ] Function catches and handles rate limit errors (429)
- [ ] Function catches and handles timeout errors
- [ ] Function catches and handles invalid model errors
- [ ] Function catches and handles import errors (missing langchain-openai)
- [ ] Function returns True on success, False on failure
- [ ] Function prints informative error messages for each error type
- [ ] Pytest integration: test_api_connection_pytest() exists
- [ ] Script can be run directly: `python tests/test_api.py`
- [ ] Script exit code is 0 on success, 1 on failure
- [ ] Cost estimate function works without running test
- [ ] `tests/` directory exists (created in v0.1.3)

---

## Limitations & Constraints

- Test requires valid internet connection and reachability to OpenAI API
- Test consumes API quota (even if minimal); check your usage limits
- Rate limiting may prevent running test multiple times quickly
- API key must be valid and have sufficient credits/quota
- Test cannot run in offline environments
- Timeouts are hard-coded (10 seconds); may be too short in slow networks
- Error messages are based on exception text (may vary with API/library changes)
- Cost estimates are approximate and based on 2024 pricing (verify current rates)
- Pre-emptive retry disabled (max_retries=1) to fail fast; may need adjustment for flaky networks
- Does not test all model types (only tests configured model)

---

## Dependencies

**Must exist before this sub-part runs:**
- `src/config.py` module (v0.1.2c)
- `.env` file with valid OPENAI_API_KEY (v0.1.2a)
- `.gitignore` configured (v0.1.2b) - for security
- `tests/` directory exists (v0.1.3 or created here)
- langchain-openai package installed (v0.1.1b)
- langchain package installed (v0.1.1b)
- Python 3.10+ (v0.1.1a)

**Python imports required:**
- `src.config.Config` (from v0.1.2c)
- `langchain_openai.ChatOpenAI` (v0.1.1b)
- `pathlib.Path` (standard library)
- `sys` (standard library)

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'langchain_openai'"

**Solution:** Install langchain-openai package (should be done in v0.1.1b):

```bash
pip install langchain-openai

# Verify
python -c "from langchain_openai import ChatOpenAI; print('✅ installed')"
```

---

### Issue: "ModuleNotFoundError: No module named 'src.config'"

**Solution:** Ensure src/config.py exists and Python path is correct:

```bash
# Verify src/config.py exists
ls -la src/config.py

# Run test from project root:
cd /path/to/haiku-protocol
python tests/test_api.py

# If still failing, check sys.path addition in test_api.py (already there)
```

---

### Issue: "OPENAI_API_KEY is empty" message

**Solution:** Verify .env file has the API key:

```bash
# Check .env exists and has the key
cat .env | grep OPENAI_API_KEY

# Should output something like:
# OPENAI_API_KEY=sk-proj-...

# If empty:
# 1. Get a key from: https://platform.openai.com/api-keys
# 2. Update .env file
# 3. Run test again
```

---

### Issue: "Error code: 401 - invalid_api_key"

**Solution:** API key is invalid or revoked. Regenerate it:

```bash
# 1. Go to: https://platform.openai.com/api-keys
# 2. Delete the old key (it may be compromised)
# 3. Create a new API key
# 4. Copy the full key (shown only once!)
# 5. Update .env file:
nano .env
# Change OPENAI_API_KEY=sk-proj-your-new-key-here
# Save and exit

# 6. Run test again
python tests/test_api.py
```

---

### Issue: "Error code: 429 - rate_limit_exceeded"

**Solution:** Too many API requests. Wait and retry:

```bash
# 1. Wait 5-10 minutes before retrying (rate limits reset)
# 2. Check your API usage: https://platform.openai.com/account/usage
# 3. Verify you have sufficient quota/credits
# 4. Consider upgrading your plan for higher limits

# Then retry:
python tests/test_api.py
```

---

### Issue: "Connection timeout after 10.0 seconds"

**Solution:** Network issue or API is slow/down:

```bash
# 1. Check internet connection:
ping google.com

# 2. Check if OpenAI API is down:
# Go to: https://status.openai.com

# 3. Increase timeout temporarily (in test_api.py):
# Change: timeout=10
# To: timeout=30
# Then retry

# 4. Try from different network (if possible)

# Then retry:
python tests/test_api.py
```

---

### Issue: "SyntaxError" when running test

**Solution:** Python version may be too old:

```bash
# Check Python version
python --version

# Should be 3.10 or later
# If older, upgrade Python or use python3.10/python3.11/etc

# Then retry with correct version:
python3.10 tests/test_api.py
```

---

## User Story

> As a **developer setting up Haiku Protocol**, I want to **verify that my OpenAI API key is valid and working** so that **I can be confident that the application will be able to connect to the API before proceeding with development**.

---

## Inputs from Previous Sub-Parts

This sub-part receives inputs from v0.1.2a, v0.1.2b, and v0.1.2c:

**From v0.1.2a (Environment File Creation & Structure):**
- **`.env` file** with valid OPENAI_API_KEY
- **Expected format**: OPENAI_API_KEY=sk-proj-[actual-key]
- **Guarantee**: File exists and is readable

**From v0.1.2b (Git Security & Secret Protection):**
- **Security confirmation**: .env is excluded from git via .gitignore
- **Assurance**: Safe to use API key in test code (won't be committed)
- **Pre-commit hooks** (optional) will prevent accidental exposure

**From v0.1.2c (Configuration Module Implementation):**
- **Config class** that loads OPENAI_API_KEY from .env
- **Config.validate()** method to verify configuration is valid
- **Config.OPENAI_MODEL** to specify which model to test
- **Guarantee**: Config module is imported and working

This sub-part uses all three to:
1. Import Config and call Config.validate()
2. Get OPENAI_API_KEY from Config class (loaded from .env by python-dotenv)
3. Initialize ChatOpenAI with the API key
4. Send test request to verify connectivity
5. Report clear error messages if anything fails

---

## Outputs to Next Sub-Part

This sub-part produces:

**File 1: `tests/test_api.py` module**
```python
from tests.test_api import test_api_connection

# Can be called as:
success = test_api_connection(verbose=True)

# Or run directly:
# python tests/test_api.py
```

**Exports:**
- `test_api_connection(verbose=bool)` → bool
- `estimate_api_cost(num_requests=int)` → dict
- `test_api_connection_pytest()` (pytest integration)

**Outputs:**
- ✅ Verification that API key is valid
- ✅ Confirmation that OpenAI API is reachable
- ✅ Cost estimate for test execution
- ✅ Error diagnostics and remediation steps

**What happens next (v0.1.3):**

v0.1.3 (Project Scaffolding) does NOT receive output from v0.1.2d directly, but benefits from the validation:
- **Assurance**: Configuration is working
- **Baseline**: API is accessible (ready for actual use)
- **Testing**: test_api.py can be extended with more comprehensive tests
- **Template**: Pattern for writing tests in `tests/` directory

---

## Decision Log

(Placeholder: Record decisions made during test implementation)
- Decision on max_tokens: **Set to 10** to minimize cost while ensuring response
- Decision on temperature: **Set to 0** for deterministic testing
- Decision on max_retries: **Set to 1** to fail fast (ideal for validation test)
- Decision on timeout: **Set to 10 seconds** for reasonable wait time
- Decision on error handling: **Catch all exceptions** with specific diagnostics
- Decision on cost estimation: **Approximate 2024 pricing**, included for reference
- Decision on pytest integration: **Optional fixture** for CI/CD flexibility
- Decision on verbose output: **Default to True** for clarity during setup (can be disabled)

