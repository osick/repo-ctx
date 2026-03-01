"""
Tests for DocGen LLM module.
"""

import sys
import pytest
from unittest.mock import patch, MagicMock
from docgen.llm import (
    LLMConfig,
    LLMProvider,
    create_llm,
    get_available_providers,
    get_model_aliases,
    detect_provider_from_model,
    MODEL_ALIASES,
    DEFAULT_MODELS,
)


class TestLLMConfig:
    """Tests for LLMConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = LLMConfig()

        assert config.provider == "anthropic"
        assert config.model == "claude-sonnet-4-20250514"  # Default for anthropic
        assert config.temperature == 0.7
        assert config.max_tokens == 4096

    def test_custom_config(self):
        """Test custom configuration values."""
        config = LLMConfig(
            provider="openai",
            model="gpt-5",
            temperature=0.5,
            max_tokens=8000,
        )

        assert config.provider == "openai"
        assert config.model == "gpt-5"
        assert config.temperature == 0.5
        assert config.max_tokens == 8000

    def test_model_alias_resolution(self):
        """Test that model aliases are resolved."""
        config = LLMConfig(model="sonnet")
        assert config.model == "claude-sonnet-4-20250514"

        config = LLMConfig(provider="openai", model="chatgpt-5")
        assert config.model == "gpt-5"

    def test_provider_normalization(self):
        """Test that provider is normalized to lowercase."""
        config = LLMConfig(provider="ANTHROPIC")
        assert config.provider == "anthropic"

    def test_azure_config(self):
        """Test Azure-specific configuration."""
        config = LLMConfig(
            provider="azure",
            model="gpt-5",
            azure_endpoint="https://my-resource.openai.azure.com",
            azure_deployment="my-deployment",
        )

        assert config.azure_endpoint == "https://my-resource.openai.azure.com"
        assert config.azure_deployment == "my-deployment"
        assert config.azure_api_version == "2024-02-15-preview"

    def test_to_dict(self):
        """Test configuration serialization."""
        config = LLMConfig(provider="google", model="gemini-3")
        data = config.to_dict()

        assert data["provider"] == "google"
        assert data["model"] == "gemini-3"
        assert "temperature" in data
        assert "max_tokens" in data


class TestLLMProvider:
    """Tests for LLMProvider enum."""

    def test_provider_values(self):
        """Test provider enum values."""
        assert LLMProvider.ANTHROPIC.value == "anthropic"
        assert LLMProvider.OPENAI.value == "openai"
        assert LLMProvider.AZURE.value == "azure"
        assert LLMProvider.GOOGLE.value == "google"

    def test_all_providers(self):
        """Test that all expected providers exist."""
        providers = [p.value for p in LLMProvider]
        assert "anthropic" in providers
        assert "openai" in providers
        assert "azure" in providers
        assert "google" in providers


class TestModelAliases:
    """Tests for model alias mappings."""

    def test_anthropic_aliases(self):
        """Test Anthropic model aliases."""
        assert "claude-sonnet-4" in MODEL_ALIASES
        assert "sonnet" in MODEL_ALIASES
        assert "opus" in MODEL_ALIASES

    def test_openai_aliases(self):
        """Test OpenAI model aliases."""
        assert "gpt-5-mini" in MODEL_ALIASES
        assert "gpt-5" in MODEL_ALIASES
        assert "chatgpt-5" in MODEL_ALIASES
        assert MODEL_ALIASES["chatgpt-5"] == "gpt-5"

    def test_google_aliases(self):
        """Test Google model aliases."""
        assert "gemini" in MODEL_ALIASES
        assert "gemini-3" in MODEL_ALIASES


class TestDefaultModels:
    """Tests for default model mappings."""

    def test_defaults_exist(self):
        """Test that defaults exist for all providers."""
        for provider in LLMProvider:
            assert provider in DEFAULT_MODELS


class TestDetectProviderFromModel:
    """Tests for detect_provider_from_model function."""

    def test_detect_anthropic(self):
        """Test detecting Anthropic from model name."""
        assert detect_provider_from_model("claude-sonnet-4") == "anthropic"
        assert detect_provider_from_model("claude-opus-4") == "anthropic"
        assert detect_provider_from_model("sonnet-4") == "anthropic"

    def test_detect_openai(self):
        """Test detecting OpenAI from model name."""
        assert detect_provider_from_model("gpt-5-mini") == "openai"
        assert detect_provider_from_model("gpt-5") == "openai"
        assert detect_provider_from_model("o1-preview") == "openai"

    def test_detect_google(self):
        """Test detecting Google from model name."""
        assert detect_provider_from_model("gemini-2.0-flash") == "google"
        assert detect_provider_from_model("gemini-3") == "google"

    def test_unknown_model(self):
        """Test unknown model returns None."""
        assert detect_provider_from_model("unknown-model-xyz") is None


class TestGetAvailableProviders:
    """Tests for get_available_providers function."""

    def test_returns_all_providers(self):
        """Test that all providers are returned."""
        providers = get_available_providers()
        assert "anthropic" in providers
        assert "openai" in providers
        assert "azure" in providers
        assert "google" in providers


class TestGetModelAliases:
    """Tests for get_model_aliases function."""

    def test_returns_copy(self):
        """Test that a copy is returned, not the original."""
        aliases = get_model_aliases()
        original_len = len(aliases)
        aliases["test"] = "test"
        assert len(get_model_aliases()) == original_len


class TestCreateLLM:
    """Tests for create_llm factory function."""

    def test_invalid_provider(self):
        """Test that invalid provider raises ValueError."""
        config = LLMConfig.__new__(LLMConfig)
        config.provider = "invalid_provider"
        config.model = "test"

        with pytest.raises(ValueError, match="Unsupported provider"):
            create_llm(config)

    def test_anthropic_factory_called(self):
        """Test Anthropic factory is called correctly."""
        import docgen.llm

        mock_factory = MagicMock(return_value=MagicMock())
        original = docgen.llm._PROVIDER_FACTORIES[LLMProvider.ANTHROPIC]
        docgen.llm._PROVIDER_FACTORIES[LLMProvider.ANTHROPIC] = mock_factory

        try:
            config = LLMConfig(provider="anthropic", api_key="test-key")
            create_llm(config)
            mock_factory.assert_called_once_with(config)
        finally:
            docgen.llm._PROVIDER_FACTORIES[LLMProvider.ANTHROPIC] = original

    def test_openai_factory_called(self):
        """Test OpenAI factory is called correctly."""
        import docgen.llm

        mock_factory = MagicMock(return_value=MagicMock())
        original = docgen.llm._PROVIDER_FACTORIES[LLMProvider.OPENAI]
        docgen.llm._PROVIDER_FACTORIES[LLMProvider.OPENAI] = mock_factory

        try:
            config = LLMConfig(provider="openai", api_key="test-key")
            create_llm(config)
            mock_factory.assert_called_once_with(config)
        finally:
            docgen.llm._PROVIDER_FACTORIES[LLMProvider.OPENAI] = original

    def test_azure_factory_called(self):
        """Test Azure factory is called correctly."""
        import docgen.llm

        mock_factory = MagicMock(return_value=MagicMock())
        original = docgen.llm._PROVIDER_FACTORIES[LLMProvider.AZURE]
        docgen.llm._PROVIDER_FACTORIES[LLMProvider.AZURE] = mock_factory

        try:
            config = LLMConfig(
                provider="azure",
                api_key="test-key",
                azure_endpoint="https://test.openai.azure.com",
            )
            create_llm(config)
            mock_factory.assert_called_once_with(config)
        finally:
            docgen.llm._PROVIDER_FACTORIES[LLMProvider.AZURE] = original

    def test_google_factory_called(self):
        """Test Google factory is called correctly."""
        import docgen.llm

        mock_factory = MagicMock(return_value=MagicMock())
        original = docgen.llm._PROVIDER_FACTORIES[LLMProvider.GOOGLE]
        docgen.llm._PROVIDER_FACTORIES[LLMProvider.GOOGLE] = mock_factory

        try:
            config = LLMConfig(provider="google", api_key="test-key")
            create_llm(config)
            mock_factory.assert_called_once_with(config)
        finally:
            docgen.llm._PROVIDER_FACTORIES[LLMProvider.GOOGLE] = original


class TestAnthropicLLM:
    """Tests for Anthropic LLM creation."""

    def test_creates_with_api_key(self):
        """Test creating with API key in config."""
        # Mock the ChatAnthropic import
        mock_chat = MagicMock()
        mock_module = MagicMock()
        mock_module.ChatAnthropic = mock_chat

        with patch.dict(sys.modules, {"langchain_anthropic": mock_module}):
            from docgen.llm import _create_anthropic_llm

            config = LLMConfig(provider="anthropic", model="claude-sonnet-4", api_key="test-key")
            _create_anthropic_llm(config)

            mock_chat.assert_called_once()
            call_kwargs = mock_chat.call_args[1]
            assert call_kwargs["api_key"] == "test-key"
            assert call_kwargs["model"] == "claude-sonnet-4-20250514"

    @patch.dict("os.environ", {}, clear=True)
    def test_raises_without_key(self):
        """Test that missing API key raises ValueError."""
        # Mock the import to avoid ImportError
        mock_module = MagicMock()
        with patch.dict(sys.modules, {"langchain_anthropic": mock_module}):
            from docgen.llm import _create_anthropic_llm

            config = LLMConfig(provider="anthropic", api_key=None)

            with pytest.raises(ValueError, match="Anthropic API key required"):
                _create_anthropic_llm(config)


class TestOpenAILLM:
    """Tests for OpenAI LLM creation."""

    def test_creates_with_api_key(self):
        """Test creating with API key in config."""
        mock_chat = MagicMock()
        mock_module = MagicMock()
        mock_module.ChatOpenAI = mock_chat

        with patch.dict(sys.modules, {"langchain_openai": mock_module}):
            from docgen.llm import _create_openai_llm

            config = LLMConfig(provider="openai", model="gpt-5", api_key="test-key")
            _create_openai_llm(config)

            mock_chat.assert_called_once()
            call_kwargs = mock_chat.call_args[1]
            assert call_kwargs["api_key"] == "test-key"

    @patch.dict("os.environ", {}, clear=True)
    def test_raises_without_key(self):
        """Test that missing API key raises ValueError."""
        mock_module = MagicMock()
        with patch.dict(sys.modules, {"langchain_openai": mock_module}):
            from docgen.llm import _create_openai_llm

            config = LLMConfig(provider="openai", api_key=None)

            with pytest.raises(ValueError, match="OpenAI API key required"):
                _create_openai_llm(config)


class TestAzureLLM:
    """Tests for Azure OpenAI LLM creation."""

    def test_creates_with_config(self):
        """Test creating with config values."""
        mock_chat = MagicMock()
        mock_module = MagicMock()
        mock_module.AzureChatOpenAI = mock_chat

        with patch.dict(sys.modules, {"langchain_openai": mock_module}):
            from docgen.llm import _create_azure_llm

            config = LLMConfig(
                provider="azure",
                model="gpt-5",
                api_key="test-key",
                azure_endpoint="https://test.openai.azure.com",
                azure_deployment="my-deployment",
            )
            _create_azure_llm(config)

            mock_chat.assert_called_once()
            call_kwargs = mock_chat.call_args[1]
            assert call_kwargs["api_key"] == "test-key"
            assert call_kwargs["azure_endpoint"] == "https://test.openai.azure.com"

    @patch.dict("os.environ", {}, clear=True)
    def test_raises_without_key(self):
        """Test that missing API key raises ValueError."""
        mock_module = MagicMock()
        with patch.dict(sys.modules, {"langchain_openai": mock_module}):
            from docgen.llm import _create_azure_llm

            config = LLMConfig(provider="azure", api_key=None)

            with pytest.raises(ValueError, match="Azure OpenAI API key required"):
                _create_azure_llm(config)

    @patch.dict("os.environ", {}, clear=True)
    def test_raises_without_endpoint(self):
        """Test that missing endpoint raises ValueError."""
        mock_module = MagicMock()
        with patch.dict(sys.modules, {"langchain_openai": mock_module}):
            from docgen.llm import _create_azure_llm

            config = LLMConfig(provider="azure", api_key="test-key", azure_endpoint=None)

            with pytest.raises(ValueError, match="Azure OpenAI endpoint required"):
                _create_azure_llm(config)


class TestGoogleLLM:
    """Tests for Google Gemini LLM creation."""

    def test_creates_with_api_key(self):
        """Test creating with API key in config."""
        mock_chat = MagicMock()
        mock_module = MagicMock()
        mock_module.ChatGoogleGenerativeAI = mock_chat

        with patch.dict(sys.modules, {"langchain_google_genai": mock_module}):
            from docgen.llm import _create_google_llm

            config = LLMConfig(provider="google", model="gemini-3", api_key="test-key")
            _create_google_llm(config)

            mock_chat.assert_called_once()
            call_kwargs = mock_chat.call_args[1]
            assert call_kwargs["google_api_key"] == "test-key"

    @patch.dict("os.environ", {}, clear=True)
    def test_raises_without_key(self):
        """Test that missing API key raises ValueError."""
        mock_module = MagicMock()
        with patch.dict(sys.modules, {"langchain_google_genai": mock_module}):
            from docgen.llm import _create_google_llm

            config = LLMConfig(provider="google", api_key=None)

            with pytest.raises(ValueError, match="Google API key required"):
                _create_google_llm(config)


class TestImportErrors:
    """Tests for handling missing provider packages."""

    def test_anthropic_import_error(self):
        """Test proper error when langchain-anthropic is not installed."""
        # Remove the module from sys.modules to simulate not installed
        with patch.dict(sys.modules, {"langchain_anthropic": None}):
            # Force reimport
            import importlib
            import docgen.llm
            importlib.reload(docgen.llm)

            config = LLMConfig(provider="anthropic", api_key="test")

            with pytest.raises(ImportError, match="langchain-anthropic is required"):
                docgen.llm._create_anthropic_llm(config)

    def test_openai_import_error(self):
        """Test proper error when langchain-openai is not installed."""
        with patch.dict(sys.modules, {"langchain_openai": None}):
            import importlib
            import docgen.llm
            importlib.reload(docgen.llm)

            config = LLMConfig(provider="openai", api_key="test")

            with pytest.raises(ImportError, match="langchain-openai is required"):
                docgen.llm._create_openai_llm(config)

    def test_google_import_error(self):
        """Test proper error when langchain-google-genai is not installed."""
        with patch.dict(sys.modules, {"langchain_google_genai": None}):
            import importlib
            import docgen.llm
            importlib.reload(docgen.llm)

            config = LLMConfig(provider="google", api_key="test")

            with pytest.raises(ImportError, match="langchain-google-genai is required"):
                docgen.llm._create_google_llm(config)
