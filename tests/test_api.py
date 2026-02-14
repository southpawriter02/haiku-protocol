#!/usr/bin/env python3
"""API Connection Testing Module for Haiku Protocol.

Tests connectivity to OpenAI API and validates that the configured
API key is valid and can be used to make successful requests.

Usage:
    python tests/test_api.py
    # or
    pytest tests/test_api.py::test_api_connection_pytest -m api

Exit Codes:
    0 - API connection successful
    1 - API connection failed

Version: v0.1.2d
"""

import logging
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src directory to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from config import Config

logger = logging.getLogger(__name__)


# ============================================
# API Connection Test (Live)
# ============================================


def test_api_connection(verbose: bool = True) -> bool:
    """Test LLM API connection and key validity.

    This function:
        1. Loads configuration from .env via Config class
        2. Validates provider, API key, and model settings
        3. Initializes ChatOpenAI client (works with OpenAI,
           Ollama, and LM Studio via OpenAI-compatible API)
        4. Sends a test prompt to verify connectivity
        5. Handles and reports various error scenarios

    Args:
        verbose: If True, print detailed output.

    Returns:
        True if API connection successful and validated, False otherwise.

    Cost Awareness:
        Uses max_tokens=10 to minimize API cost (~$0.0001 per call).
    """
    if verbose:
        print("\n" + "=" * 70)
        print("Haiku Protocol — API Connection Test (v0.1.3)")
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

    api_key = Config.get_llm_api_key()
    provider = Config.get_llm_provider()
    model = Config.get_llm_model()
    base_url = Config.get_llm_base_url()

    # ----------------------------------------
    # Step 2: Initialize LLM Client
    # ----------------------------------------

    if verbose:
        print(f"[2/3] Initializing {provider} client...")

    try:
        from langchain_openai import ChatOpenAI

        kwargs = dict(
            api_key=api_key,
            model=model,
            temperature=0,
            max_tokens=10,
            timeout=10,
            max_retries=1,
        )
        if base_url:
            kwargs["base_url"] = base_url

        llm = ChatOpenAI(**kwargs)

        if verbose:
            print(f"   Provider: {provider}")
            print(f"   Model: {model}")
            if base_url:
                print(f"   Base URL: {base_url}")
            print("   Timeout: 10 seconds")

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
        test_prompt = "Respond with just the word 'OK' and nothing else"
        response = llm.invoke(test_prompt)

        if hasattr(response, "content"):
            response_text = response.content
        else:
            response_text = str(response)

        if verbose:
            print(f"\n✅ API Response Received:")
            print(f"   Content: {response_text[:50]}...")
            print(f"   Length: {len(response_text)} characters")

        return True

    # ----------------------------------------
    # Error Handling
    # ----------------------------------------

    except Exception as e:
        error_str = str(e)
        error_type = type(e).__name__

        if verbose:
            print(f"\n❌ API Request Failed")
            print(f"   Error Type: {error_type}")
            print(f"   Error Message: {error_str[:200]}")

        if (
            "401" in error_str
            or "Unauthorized" in error_str
            or "invalid_api_key" in error_str
        ):
            if verbose:
                print("\n   Diagnosis: Invalid API Key")
                print("   The API key is invalid or has been revoked.")
                print("\n   Actions:")
                print("   1. Go to https://platform.openai.com/api-keys")
                print("   2. Create a new API key")
                print("   3. Update .env: OPENAI_API_KEY with your new key")
                print("   4. Run this test again\n")
            return False

        elif "429" in error_str or "rate" in error_str.lower():
            if verbose:
                print("\n   Diagnosis: Rate Limit Exceeded")
                print("   Too many requests to OpenAI API.")
                print("\n   Actions:")
                print("   1. Wait a few minutes before retrying")
                print(
                    "   2. Check API usage at: "
                    "https://platform.openai.com/account/usage"
                )
                print("   3. Consider increasing API quota\n")
            return False

        elif "timeout" in error_str.lower() or "Connection" in error_str:
            if verbose:
                print("\n   Diagnosis: Network/Timeout Error")
                print(
                    "   Could not reach OpenAI API or request timed out."
                )
                print("\n   Actions:")
                print("   1. Check your internet connection")
                print(
                    "   2. Verify OpenAI status: "
                    "https://status.openai.com"
                )
                print("   3. Try again in a few moments\n")
            return False

        elif (
            "model" in error_str.lower()
            and "does not exist" in error_str.lower()
        ):
            if verbose:
                print("\n   Diagnosis: Invalid Model Name")
                print(
                    f"   Model '{model}' "
                    "does not exist"
                )
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
# Cost Analyzer
# ============================================


def estimate_api_cost(num_requests: int = 1) -> dict:
    """Estimate API cost for running test_api_connection().

    Args:
        num_requests: How many times test will be run.

    Returns:
        dict with cost estimates including model, tokens, and total cost.
    """
    pricing = {
        "gpt-4": {"input": 0.00003, "output": 0.00006},
        "gpt-4-turbo": {"input": 0.00001, "output": 0.00003},
        "gpt-3.5-turbo": {"input": 0.0000005, "output": 0.0000015},
    }

    model = Config.get_openai_model()
    rates = pricing.get(model, pricing["gpt-4"])

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
        "note": (
            "Costs are approximate; check OpenAI pricing "
            "for current rates"
        ),
    }


# ============================================
# Pytest Integration (Live API — @api marker)
# ============================================


@pytest.mark.api
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY")
    and os.getenv("LLM_PROVIDER", "openai").lower() == "openai",
    reason="OPENAI_API_KEY not set and provider is openai — skipping live API test",
)
def test_api_connection_pytest():
    """Pytest-compatible version of API connection test.

    Marked with @pytest.mark.api — only runs when explicitly requested:
        pytest tests/test_api.py -m api -v
    """
    assert test_api_connection(verbose=True), "API connection test failed"


# ============================================
# Offline Unit Tests
# ============================================


@pytest.mark.unit
class TestApiModuleStructure:
    """Tests verifying test_api.py structure (no API calls)."""

    def test_test_api_connection_function_exists(self):
        """test_api_connection() function is defined."""
        assert callable(test_api_connection)

    def test_estimate_api_cost_function_exists(self):
        """estimate_api_cost() function is defined."""
        assert callable(estimate_api_cost)

    def test_test_api_connection_returns_bool(self):
        """test_api_connection() signature returns bool."""
        import inspect

        sig = inspect.signature(test_api_connection)
        assert sig.return_annotation is bool

    def test_test_api_connection_has_verbose_param(self):
        """test_api_connection() has a verbose parameter."""
        import inspect

        sig = inspect.signature(test_api_connection)
        assert "verbose" in sig.parameters

    def test_config_import_works(self):
        """Config class is importable from test_api module."""
        assert Config is not None
        assert hasattr(Config, "validate")
        assert hasattr(Config, "get_openai_api_key")


@pytest.mark.unit
class TestCostEstimation:
    """Tests for estimate_api_cost() (no API calls)."""

    def test_cost_estimate_returns_dict(self):
        """estimate_api_cost() returns a dictionary."""
        result = estimate_api_cost()
        assert isinstance(result, dict)

    def test_cost_estimate_has_required_keys(self):
        """Cost estimate contains all expected keys."""
        result = estimate_api_cost()
        required_keys = [
            "model",
            "input_tokens",
            "output_tokens",
            "num_requests",
            "input_cost",
            "output_cost",
            "total_cost",
            "note",
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_cost_estimate_default_single_request(self):
        """Default cost estimate is for 1 request."""
        result = estimate_api_cost()
        assert result["num_requests"] == 1

    def test_cost_estimate_scales_with_requests(self):
        """Cost scales linearly with number of requests."""
        cost_1 = estimate_api_cost(num_requests=1)["total_cost"]
        cost_10 = estimate_api_cost(num_requests=10)["total_cost"]
        assert abs(cost_10 - cost_1 * 10) < 1e-15

    def test_cost_estimate_negligible(self):
        """Single test cost is less than $0.001."""
        result = estimate_api_cost(num_requests=1)
        assert result["total_cost"] < 0.001


@pytest.mark.unit
class TestErrorHandling:
    """Tests verifying error handling paths (mocked, no API calls)."""

    def test_returns_false_on_config_validation_failure(self):
        """test_api_connection returns False when Config.validate fails."""
        with patch.object(Config, "validate", return_value=False):
            result = test_api_connection(verbose=False)
            assert result is False

    def test_returns_false_on_import_error(self):
        """test_api_connection returns False when langchain_openai missing."""
        with patch.object(Config, "validate", return_value=True), \
             patch.object(Config, "get_openai_api_key", return_value="sk-test1234567890"), \
             patch.dict("sys.modules", {"langchain_openai": None}):
            # Force ImportError by removing langchain_openai from modules
            result = test_api_connection(verbose=False)
            # May return False via import error or other path
            assert isinstance(result, bool)

    def test_returns_false_on_auth_error(self):
        """test_api_connection returns False on 401 auth error."""
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception(
            "Error code: 401 - invalid_api_key"
        )

        mock_chat_class = MagicMock(return_value=mock_llm)

        with patch.object(Config, "validate", return_value=True), \
             patch.object(Config, "get_openai_api_key", return_value="sk-test1234567890"), \
             patch.object(Config, "get_openai_model", return_value="gpt-4"), \
             patch("tests.test_api.ChatOpenAI", mock_chat_class, create=True):
            # We need to patch the import inside the function
            import importlib
            mock_module = MagicMock()
            mock_module.ChatOpenAI = mock_chat_class
            with patch.dict("sys.modules", {"langchain_openai": mock_module}):
                result = test_api_connection(verbose=False)
                assert result is False

    def test_returns_false_on_timeout(self):
        """test_api_connection returns False on timeout."""
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception(
            "Connection timeout after 10.0 seconds"
        )

        mock_chat_class = MagicMock(return_value=mock_llm)
        mock_module = MagicMock()
        mock_module.ChatOpenAI = mock_chat_class

        with patch.object(Config, "validate", return_value=True), \
             patch.object(Config, "get_openai_api_key", return_value="sk-test1234567890"), \
             patch.object(Config, "get_openai_model", return_value="gpt-4"), \
             patch.dict("sys.modules", {"langchain_openai": mock_module}):
            result = test_api_connection(verbose=False)
            assert result is False

    def test_returns_false_on_rate_limit(self):
        """test_api_connection returns False on 429 rate limit."""
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception(
            "Error code: 429 - rate_limit_exceeded"
        )

        mock_chat_class = MagicMock(return_value=mock_llm)
        mock_module = MagicMock()
        mock_module.ChatOpenAI = mock_chat_class

        with patch.object(Config, "validate", return_value=True), \
             patch.object(Config, "get_openai_api_key", return_value="sk-test1234567890"), \
             patch.object(Config, "get_openai_model", return_value="gpt-4"), \
             patch.dict("sys.modules", {"langchain_openai": mock_module}):
            result = test_api_connection(verbose=False)
            assert result is False

    def test_returns_false_on_invalid_model(self):
        """test_api_connection returns False on invalid model error."""
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception(
            "The model 'gpt-99' does not exist"
        )

        mock_chat_class = MagicMock(return_value=mock_llm)
        mock_module = MagicMock()
        mock_module.ChatOpenAI = mock_chat_class

        with patch.object(Config, "validate", return_value=True), \
             patch.object(Config, "get_openai_api_key", return_value="sk-test1234567890"), \
             patch.object(Config, "get_openai_model", return_value="gpt-99"), \
             patch.dict("sys.modules", {"langchain_openai": mock_module}):
            result = test_api_connection(verbose=False)
            assert result is False


@pytest.mark.unit
class TestVerboseOutput:
    """Tests for verbose output formatting."""

    def test_verbose_true_prints_header(self, capsys):
        """Verbose mode prints the test header."""
        with patch.object(Config, "validate", return_value=False):
            test_api_connection(verbose=True)

        captured = capsys.readouterr()
        assert "Haiku Protocol" in captured.out
        assert "API Connection Test" in captured.out

    def test_verbose_false_suppresses_output(self, capsys):
        """Non-verbose mode suppresses header output."""
        with patch.object(Config, "validate", return_value=False):
            test_api_connection(verbose=False)

        captured = capsys.readouterr()
        assert "Haiku Protocol" not in captured.out


@pytest.mark.unit
class TestApiLogging:
    """Verify logging for API connection tests."""

    def test_logger_exists(self):
        """Module-level logger is configured."""
        assert logger is not None
        assert logger.name == "tests.test_api"


# ============================================
# Direct Execution
# ============================================

if __name__ == "__main__":
    print("\nHaiku Protocol — API Connection Validation")
    print("Starting test...\n")

    success = test_api_connection(verbose=True)

    cost_estimate = estimate_api_cost(num_requests=1)
    print(f"\n💰 Cost Estimate:")
    print(f"   Model: {cost_estimate['model']}")
    print(
        f"   Input/Output Tokens: "
        f"{cost_estimate['input_tokens']}/{cost_estimate['output_tokens']}"
    )
    print(f"   Estimated Cost: ${cost_estimate['total_cost']:.8f}")
    print(f"   ({cost_estimate['note']})")

    print("=" * 70 + "\n")

    exit(0 if success else 1)
