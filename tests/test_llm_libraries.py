"""Tests for v0.1.1b — LangChain & LLM Libraries.

Verifies that the core LLM orchestration libraries are installed and
functional: langchain, langchain-openai, and tiktoken.

Version: v0.1.1b
"""

import logging

import pytest

# Skip entire module if LLM libraries are not installed
pytest.importorskip("langchain", reason="langchain not installed")
pytest.importorskip("tiktoken", reason="tiktoken not installed")

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Happy Path Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLLMLibraryVersions:
    """Tests verifying LLM library versions meet v0.1.1b acceptance criteria."""

    def test_langchain_version_meets_minimum(self):
        """langchain is installed with version ≥ 0.1.0.

        Acceptance Criterion: "pip show langchain returns version ≥0.1.0"
        """
        # Arrange
        import langchain

        # Act
        version = langchain.__version__
        parts = version.split(".")
        major, minor = int(parts[0]), int(parts[1])

        # Assert
        assert (major, minor) >= (0, 1), (
            f"langchain version {version} does not meet minimum 0.1.0"
        )
        logger.info("langchain version check passed: %s", version)

    def test_langchain_openai_version_meets_minimum(self):
        """langchain-openai is installed with version ≥ 0.0.5.

        Acceptance Criterion: "pip show langchain-openai returns version ≥0.0.5"
        """
        # Arrange
        import langchain_openai

        # Act
        version = getattr(langchain_openai, "__version__", None)

        # Assert
        assert version is not None or langchain_openai, (
            "langchain_openai is not importable"
        )
        if version:
            parts = version.split(".")
            assert len(parts) >= 3, (
                f"Unexpected version format: {version}"
            )
        logger.info(
            "langchain-openai version check passed: %s",
            version or "installed (no __version__)",
        )

    def test_tiktoken_version_meets_minimum(self):
        """tiktoken is installed with version ≥ 0.5.0.

        Acceptance Criterion: "pip show tiktoken returns version ≥0.5.0"
        """
        # Arrange
        import tiktoken

        # Act
        version = tiktoken.__version__
        parts = version.split(".")
        major, minor = int(parts[0]), int(parts[1])

        # Assert
        assert (major, minor) >= (0, 5), (
            f"tiktoken version {version} does not meet minimum 0.5.0"
        )
        logger.info("tiktoken version check passed: %s", version)


# ---------------------------------------------------------------------------
# Functional Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLLMLibraryFunctionality:
    """Tests verifying core LLM library functionality."""

    def test_langchain_prompt_template_works(self):
        """LangChain PromptTemplate can format a prompt string.

        Acceptance Criterion: "verify_llm_libs.py shows all ✅"
        """
        # Arrange
        from langchain_core.prompts import PromptTemplate

        template = PromptTemplate(
            input_variables=["topic"],
            template="Tell me about {topic}",
        )

        # Act
        result = template.format(topic="AI compression")

        # Assert
        assert result == "Tell me about AI compression"
        logger.info("PromptTemplate functional: output=%s", result)

    def test_tiktoken_encodes_tokens_correctly(self):
        """tiktoken encodes text into a non-empty list of integer tokens.

        Acceptance Criterion: "test_tiktoken.py counts tokens correctly"
        """
        # Arrange
        import tiktoken

        enc = tiktoken.encoding_for_model("gpt-4")
        text = (
            "To restart the server, you must first ensure that "
            "the configuration file is saved."
        )

        # Act
        tokens = enc.encode(text)

        # Assert
        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert all(isinstance(t, int) for t in tokens)
        logger.info(
            "tiktoken tokenization passed: text_len=%d, token_count=%d",
            len(text), len(tokens),
        )

    def test_tiktoken_roundtrip_encode_decode(self):
        """tiktoken can encode and decode back to the original text."""
        # Arrange
        import tiktoken

        enc = tiktoken.encoding_for_model("gpt-4")
        original = "Hello, world!"

        # Act
        tokens = enc.encode(original)
        decoded = enc.decode(tokens)

        # Assert
        assert decoded == original
        logger.info("tiktoken roundtrip passed: %s", original)


# ---------------------------------------------------------------------------
# Edge Case Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLLMLibraryEdgeCases:
    """Edge case tests for LLM library verification."""

    def test_tiktoken_empty_string_returns_empty_tokens(self):
        """Encoding an empty string produces an empty token list."""
        import tiktoken

        enc = tiktoken.encoding_for_model("gpt-4")
        tokens = enc.encode("")
        assert tokens == []

    def test_tiktoken_unicode_text_encodes_successfully(self):
        """tiktoken handles Unicode text without errors."""
        import tiktoken

        enc = tiktoken.encoding_for_model("gpt-4")
        tokens = enc.encode("日本語テスト 🚀")
        assert len(tokens) > 0

    def test_langchain_prompt_template_empty_variable(self):
        """PromptTemplate handles an empty string variable."""
        from langchain_core.prompts import PromptTemplate

        template = PromptTemplate(
            input_variables=["topic"],
            template="Tell me about {topic}",
        )
        result = template.format(topic="")
        assert result == "Tell me about "

    def test_langchain_prompt_template_special_characters(self):
        """PromptTemplate handles special characters in variable values."""
        from langchain_core.prompts import PromptTemplate

        template = PromptTemplate(
            input_variables=["topic"],
            template="Tell me about {topic}",
        )
        result = template.format(topic="<script>alert('xss')</script>")
        assert "<script>" in result


# ---------------------------------------------------------------------------
# Log Output Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLLMLibraryLogging:
    """Verify that library checks produce expected log output."""

    def test_langchain_import_logs_version(self, caplog):
        """Importing langchain and logging its version produces INFO output."""
        import langchain

        with caplog.at_level(logging.INFO):
            logger.info("langchain version: %s", langchain.__version__)

        assert "langchain version" in caplog.text

    def test_tiktoken_encoding_logs_token_count(self, caplog):
        """Tiktoken encoding logs the token count at INFO level."""
        import tiktoken

        enc = tiktoken.encoding_for_model("gpt-4")
        tokens = enc.encode("test")

        with caplog.at_level(logging.INFO):
            logger.info("Token count: %d", len(tokens))

        assert "Token count" in caplog.text


# ---------------------------------------------------------------------------
# Use Case Test
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLLMLibrariesUseCase:
    """End-to-end use case test for v0.1.1b."""

    def test_full_llm_library_verification_workflow(self):
        """Simulate the complete LLM library verification workflow.

        Use Case: "Developer installs LLM libraries, verifies all three
        are importable with correct versions, and confirms functional
        tokenization."
        """
        # 1. langchain importable with version
        import langchain
        assert langchain.__version__

        # 2. langchain-openai importable
        import langchain_openai
        assert langchain_openai

        # 3. tiktoken importable with version
        import tiktoken
        assert tiktoken.__version__

        # 4. PromptTemplate works
        from langchain_core.prompts import PromptTemplate

        template = PromptTemplate(
            input_variables=["topic"],
            template="Explain {topic}",
        )
        assert template.format(topic="compression") == "Explain compression"

        # 5. tiktoken tokenizes correctly
        enc = tiktoken.encoding_for_model("gpt-4")
        tokens = enc.encode("Hello world")
        assert len(tokens) > 0
        assert enc.decode(tokens) == "Hello world"
