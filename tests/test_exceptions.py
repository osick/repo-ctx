"""Tests for the exception hierarchy.

Tests the custom exception classes defined in repo_ctx.exceptions.
Following TDD Chicago School - write tests first, then implement.
"""

import pytest


class TestExceptionHierarchy:
    """Test the exception class hierarchy."""

    def test_base_exception_exists(self):
        """RepoCtxError should be the base exception class."""
        from repo_ctx.exceptions import RepoCtxError

        assert issubclass(RepoCtxError, Exception)

    def test_base_exception_with_message(self):
        """RepoCtxError should accept a message."""
        from repo_ctx.exceptions import RepoCtxError

        error = RepoCtxError("Test error message")
        assert str(error) == "Test error message"

    def test_base_exception_with_details(self):
        """RepoCtxError should accept optional details dict."""
        from repo_ctx.exceptions import RepoCtxError

        error = RepoCtxError("Test error", details={"key": "value"})
        assert error.details == {"key": "value"}

    def test_base_exception_default_details(self):
        """RepoCtxError should have empty details by default."""
        from repo_ctx.exceptions import RepoCtxError

        error = RepoCtxError("Test error")
        assert error.details == {}


class TestConfigurationError:
    """Test ConfigurationError exception."""

    def test_configuration_error_inherits_from_base(self):
        """ConfigurationError should inherit from RepoCtxError."""
        from repo_ctx.exceptions import ConfigurationError, RepoCtxError

        assert issubclass(ConfigurationError, RepoCtxError)

    def test_configuration_error_with_config_key(self):
        """ConfigurationError should accept a config_key parameter."""
        from repo_ctx.exceptions import ConfigurationError

        error = ConfigurationError("Invalid config", config_key="database.host")
        assert error.config_key == "database.host"
        assert "Invalid config" in str(error)


class TestProviderErrors:
    """Test provider-related exceptions."""

    def test_provider_error_inherits_from_base(self):
        """ProviderError should inherit from RepoCtxError."""
        from repo_ctx.exceptions import ProviderError, RepoCtxError

        assert issubclass(ProviderError, RepoCtxError)

    def test_provider_error_with_provider_name(self):
        """ProviderError should accept provider name."""
        from repo_ctx.exceptions import ProviderError

        error = ProviderError("Connection failed", provider="github")
        assert error.provider == "github"

    def test_authentication_error_inherits_from_provider(self):
        """AuthenticationError should inherit from ProviderError."""
        from repo_ctx.exceptions import AuthenticationError, ProviderError

        assert issubclass(AuthenticationError, ProviderError)

    def test_authentication_error_creation(self):
        """AuthenticationError should be creatable with message and provider."""
        from repo_ctx.exceptions import AuthenticationError

        error = AuthenticationError("Token expired", provider="gitlab")
        assert error.provider == "gitlab"
        assert "Token expired" in str(error)

    def test_rate_limit_error_inherits_from_provider(self):
        """RateLimitError should inherit from ProviderError."""
        from repo_ctx.exceptions import RateLimitError, ProviderError

        assert issubclass(RateLimitError, ProviderError)

    def test_rate_limit_error_with_retry_after(self):
        """RateLimitError should accept retry_after seconds."""
        from repo_ctx.exceptions import RateLimitError

        error = RateLimitError("Rate limited", provider="github", retry_after=60)
        assert error.retry_after == 60

    def test_repository_not_found_error(self):
        """RepositoryNotFoundError should inherit from ProviderError."""
        from repo_ctx.exceptions import RepositoryNotFoundError, ProviderError

        assert issubclass(RepositoryNotFoundError, ProviderError)

    def test_repository_not_found_with_repo(self):
        """RepositoryNotFoundError should accept repository identifier."""
        from repo_ctx.exceptions import RepositoryNotFoundError

        error = RepositoryNotFoundError(
            "Repository not found", provider="github", repository="owner/repo"
        )
        assert error.repository == "owner/repo"


class TestStorageErrors:
    """Test storage-related exceptions."""

    def test_storage_error_inherits_from_base(self):
        """StorageError should inherit from RepoCtxError."""
        from repo_ctx.exceptions import StorageError, RepoCtxError

        assert issubclass(StorageError, RepoCtxError)

    def test_storage_error_with_storage_type(self):
        """StorageError should accept storage_type parameter."""
        from repo_ctx.exceptions import StorageError

        error = StorageError("Connection failed", storage_type="sqlite")
        assert error.storage_type == "sqlite"

    def test_connection_error_inherits_from_storage(self):
        """ConnectionError should inherit from StorageError."""
        from repo_ctx.exceptions import StorageConnectionError, StorageError

        assert issubclass(StorageConnectionError, StorageError)

    def test_integrity_error_inherits_from_storage(self):
        """IntegrityError should inherit from StorageError."""
        from repo_ctx.exceptions import IntegrityError, StorageError

        assert issubclass(IntegrityError, StorageError)

    def test_not_found_error_inherits_from_storage(self):
        """NotFoundError should inherit from StorageError."""
        from repo_ctx.exceptions import NotFoundError, StorageError

        assert issubclass(NotFoundError, StorageError)

    def test_not_found_error_with_resource(self):
        """NotFoundError should accept resource identifier."""
        from repo_ctx.exceptions import NotFoundError

        error = NotFoundError(
            "Library not found", storage_type="sqlite", resource_type="library", resource_id="123"
        )
        assert error.resource_type == "library"
        assert error.resource_id == "123"


class TestAnalysisErrors:
    """Test analysis-related exceptions."""

    def test_analysis_error_inherits_from_base(self):
        """AnalysisError should inherit from RepoCtxError."""
        from repo_ctx.exceptions import AnalysisError, RepoCtxError

        assert issubclass(AnalysisError, RepoCtxError)

    def test_analysis_error_with_file_path(self):
        """AnalysisError should accept file_path parameter."""
        from repo_ctx.exceptions import AnalysisError

        error = AnalysisError("Parse failed", file_path="src/main.py")
        assert error.file_path == "src/main.py"

    def test_parsing_error_inherits_from_analysis(self):
        """ParsingError should inherit from AnalysisError."""
        from repo_ctx.exceptions import ParsingError, AnalysisError

        assert issubclass(ParsingError, AnalysisError)

    def test_language_not_supported_error(self):
        """LanguageNotSupportedError should inherit from AnalysisError."""
        from repo_ctx.exceptions import LanguageNotSupportedError, AnalysisError

        assert issubclass(LanguageNotSupportedError, AnalysisError)

    def test_language_not_supported_with_language(self):
        """LanguageNotSupportedError should accept language parameter."""
        from repo_ctx.exceptions import LanguageNotSupportedError

        error = LanguageNotSupportedError("Language not supported", language="cobol")
        assert error.language == "cobol"

    def test_joern_error_inherits_from_analysis(self):
        """JoernError should inherit from AnalysisError."""
        from repo_ctx.exceptions import JoernError, AnalysisError

        assert issubclass(JoernError, AnalysisError)


class TestGenAIErrors:
    """Test GenAI-related exceptions."""

    def test_genai_error_inherits_from_base(self):
        """GenAIError should inherit from RepoCtxError."""
        from repo_ctx.exceptions import GenAIError, RepoCtxError

        assert issubclass(GenAIError, RepoCtxError)

    def test_genai_error_with_model(self):
        """GenAIError should accept model parameter."""
        from repo_ctx.exceptions import GenAIError

        error = GenAIError("Model failed", model="claude-3-sonnet")
        assert error.model == "claude-3-sonnet"

    def test_model_not_available_error(self):
        """ModelNotAvailableError should inherit from GenAIError."""
        from repo_ctx.exceptions import ModelNotAvailableError, GenAIError

        assert issubclass(ModelNotAvailableError, GenAIError)

    def test_token_limit_exceeded_error(self):
        """TokenLimitExceededError should inherit from GenAIError."""
        from repo_ctx.exceptions import TokenLimitExceededError, GenAIError

        assert issubclass(TokenLimitExceededError, GenAIError)

    def test_token_limit_exceeded_with_counts(self):
        """TokenLimitExceededError should accept token counts."""
        from repo_ctx.exceptions import TokenLimitExceededError

        error = TokenLimitExceededError(
            "Token limit exceeded", model="gpt-5-mini", tokens_used=10000, tokens_limit=8000
        )
        assert error.tokens_used == 10000
        assert error.tokens_limit == 8000

    def test_classification_failed_error(self):
        """ClassificationFailedError should inherit from GenAIError."""
        from repo_ctx.exceptions import ClassificationFailedError, GenAIError

        assert issubclass(ClassificationFailedError, GenAIError)


class TestValidationError:
    """Test ValidationError exception."""

    def test_validation_error_inherits_from_base(self):
        """ValidationError should inherit from RepoCtxError."""
        from repo_ctx.exceptions import ValidationError, RepoCtxError

        assert issubclass(ValidationError, RepoCtxError)

    def test_validation_error_with_field(self):
        """ValidationError should accept field and value parameters."""
        from repo_ctx.exceptions import ValidationError

        error = ValidationError(
            "Invalid value", field="repository", value="", expected="non-empty string"
        )
        assert error.field == "repository"
        assert error.value == ""
        assert error.expected == "non-empty string"


class TestExceptionToDict:
    """Test exception serialization to dict for API responses."""

    def test_base_exception_to_dict(self):
        """RepoCtxError should be convertible to dict."""
        from repo_ctx.exceptions import RepoCtxError

        error = RepoCtxError("Test error", details={"context": "test"})
        error_dict = error.to_dict()

        assert error_dict["error"] == "RepoCtxError"
        assert error_dict["message"] == "Test error"
        assert error_dict["details"] == {"context": "test"}

    def test_provider_error_to_dict_includes_provider(self):
        """ProviderError.to_dict() should include provider name."""
        from repo_ctx.exceptions import ProviderError

        error = ProviderError("Failed", provider="github")
        error_dict = error.to_dict()

        assert error_dict["provider"] == "github"

    def test_rate_limit_error_to_dict_includes_retry_after(self):
        """RateLimitError.to_dict() should include retry_after."""
        from repo_ctx.exceptions import RateLimitError

        error = RateLimitError("Rate limited", provider="github", retry_after=60)
        error_dict = error.to_dict()

        assert error_dict["retry_after"] == 60

    def test_not_found_error_to_dict_includes_resource(self):
        """NotFoundError.to_dict() should include resource info."""
        from repo_ctx.exceptions import NotFoundError

        error = NotFoundError(
            "Not found", storage_type="sqlite", resource_type="library", resource_id="123"
        )
        error_dict = error.to_dict()

        assert error_dict["resource_type"] == "library"
        assert error_dict["resource_id"] == "123"
