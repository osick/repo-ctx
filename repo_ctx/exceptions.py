"""Custom exception hierarchy for repo-ctx.

This module defines a comprehensive exception hierarchy for handling errors
across the repo-ctx application. All exceptions inherit from RepoCtxError
and provide serialization support for API responses.

Exception Hierarchy:
    RepoCtxError (base)
    ├── ConfigurationError        # Invalid configuration
    ├── ProviderError            # Git provider issues
    │   ├── AuthenticationError  # Auth failed
    │   ├── RateLimitError       # API rate limited
    │   └── RepositoryNotFoundError  # Repo doesn't exist
    ├── StorageError             # Database issues
    │   ├── StorageConnectionError  # Cannot connect
    │   ├── IntegrityError       # Data constraint violation
    │   └── NotFoundError        # Record not found
    ├── AnalysisError            # Code analysis issues
    │   ├── ParsingError         # Cannot parse code
    │   ├── LanguageNotSupportedError  # Unknown language
    │   └── JoernError           # Joern CPG failure
    ├── GenAIError               # LLM issues
    │   ├── ModelNotAvailableError  # Model unreachable
    │   ├── TokenLimitExceededError  # Input too large
    │   └── ClassificationFailedError  # Cannot classify
    └── ValidationError          # Invalid input
"""

from typing import Any, Optional


class RepoCtxError(Exception):
    """Base exception for all repo-ctx errors.

    Attributes:
        message: Human-readable error message.
        details: Additional context as a dictionary.
    """

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Human-readable error message.
            details: Optional dictionary with additional context.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API responses.

        Returns:
            Dictionary representation of the error.
        """
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
        }


# =============================================================================
# Configuration Errors
# =============================================================================


class ConfigurationError(RepoCtxError):
    """Exception raised for configuration errors.

    Attributes:
        config_key: The configuration key that caused the error.
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        """Initialize ConfigurationError.

        Args:
            message: Human-readable error message.
            config_key: The configuration key that caused the error.
            details: Optional dictionary with additional context.
        """
        super().__init__(message, details)
        self.config_key = config_key

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary including config_key."""
        result = super().to_dict()
        if self.config_key:
            result["config_key"] = self.config_key
        return result


# =============================================================================
# Provider Errors
# =============================================================================


class ProviderError(RepoCtxError):
    """Base exception for git provider errors.

    Attributes:
        provider: Name of the provider (github, gitlab, local).
    """

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        """Initialize ProviderError.

        Args:
            message: Human-readable error message.
            provider: Name of the git provider.
            details: Optional dictionary with additional context.
        """
        super().__init__(message, details)
        self.provider = provider

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary including provider."""
        result = super().to_dict()
        if self.provider:
            result["provider"] = self.provider
        return result


class AuthenticationError(ProviderError):
    """Exception raised when authentication fails."""

    pass


class RateLimitError(ProviderError):
    """Exception raised when API rate limit is exceeded.

    Attributes:
        retry_after: Seconds until rate limit resets.
    """

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        retry_after: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        """Initialize RateLimitError.

        Args:
            message: Human-readable error message.
            provider: Name of the git provider.
            retry_after: Seconds until rate limit resets.
            details: Optional dictionary with additional context.
        """
        super().__init__(message, provider, details)
        self.retry_after = retry_after

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary including retry_after."""
        result = super().to_dict()
        if self.retry_after is not None:
            result["retry_after"] = self.retry_after
        return result


class RepositoryNotFoundError(ProviderError):
    """Exception raised when a repository is not found.

    Attributes:
        repository: Repository identifier that was not found.
    """

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        repository: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        """Initialize RepositoryNotFoundError.

        Args:
            message: Human-readable error message.
            provider: Name of the git provider.
            repository: Repository identifier.
            details: Optional dictionary with additional context.
        """
        super().__init__(message, provider, details)
        self.repository = repository

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary including repository."""
        result = super().to_dict()
        if self.repository:
            result["repository"] = self.repository
        return result


# =============================================================================
# Storage Errors
# =============================================================================


class StorageError(RepoCtxError):
    """Base exception for storage/database errors.

    Attributes:
        storage_type: Type of storage (sqlite, qdrant, neo4j).
    """

    def __init__(
        self,
        message: str,
        storage_type: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        """Initialize StorageError.

        Args:
            message: Human-readable error message.
            storage_type: Type of storage backend.
            details: Optional dictionary with additional context.
        """
        super().__init__(message, details)
        self.storage_type = storage_type

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary including storage_type."""
        result = super().to_dict()
        if self.storage_type:
            result["storage_type"] = self.storage_type
        return result


class StorageConnectionError(StorageError):
    """Exception raised when connection to storage fails."""

    pass


class IntegrityError(StorageError):
    """Exception raised when data integrity constraints are violated."""

    pass


class NotFoundError(StorageError):
    """Exception raised when a record is not found.

    Attributes:
        resource_type: Type of resource not found (library, document, symbol).
        resource_id: Identifier of the resource.
    """

    def __init__(
        self,
        message: str,
        storage_type: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        """Initialize NotFoundError.

        Args:
            message: Human-readable error message.
            storage_type: Type of storage backend.
            resource_type: Type of resource not found.
            resource_id: Identifier of the resource.
            details: Optional dictionary with additional context.
        """
        super().__init__(message, storage_type, details)
        self.resource_type = resource_type
        self.resource_id = resource_id

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary including resource info."""
        result = super().to_dict()
        if self.resource_type:
            result["resource_type"] = self.resource_type
        if self.resource_id:
            result["resource_id"] = self.resource_id
        return result


# =============================================================================
# Analysis Errors
# =============================================================================


class AnalysisError(RepoCtxError):
    """Base exception for code analysis errors.

    Attributes:
        file_path: Path to the file being analyzed.
    """

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        """Initialize AnalysisError.

        Args:
            message: Human-readable error message.
            file_path: Path to the file being analyzed.
            details: Optional dictionary with additional context.
        """
        super().__init__(message, details)
        self.file_path = file_path

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary including file_path."""
        result = super().to_dict()
        if self.file_path:
            result["file_path"] = self.file_path
        return result


class ParsingError(AnalysisError):
    """Exception raised when code parsing fails."""

    pass


class LanguageNotSupportedError(AnalysisError):
    """Exception raised when a language is not supported.

    Attributes:
        language: The unsupported language.
    """

    def __init__(
        self,
        message: str,
        language: Optional[str] = None,
        file_path: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        """Initialize LanguageNotSupportedError.

        Args:
            message: Human-readable error message.
            language: The unsupported language.
            file_path: Path to the file.
            details: Optional dictionary with additional context.
        """
        super().__init__(message, file_path, details)
        self.language = language

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary including language."""
        result = super().to_dict()
        if self.language:
            result["language"] = self.language
        return result


class JoernError(AnalysisError):
    """Exception raised when Joern CPG analysis fails."""

    pass


# =============================================================================
# GenAI Errors
# =============================================================================


class GenAIError(RepoCtxError):
    """Base exception for GenAI/LLM errors.

    Attributes:
        model: Name of the model that failed.
    """

    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        """Initialize GenAIError.

        Args:
            message: Human-readable error message.
            model: Name of the LLM model.
            details: Optional dictionary with additional context.
        """
        super().__init__(message, details)
        self.model = model

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary including model."""
        result = super().to_dict()
        if self.model:
            result["model"] = self.model
        return result


class ModelNotAvailableError(GenAIError):
    """Exception raised when an LLM model is not available."""

    pass


class TokenLimitExceededError(GenAIError):
    """Exception raised when token limit is exceeded.

    Attributes:
        tokens_used: Number of tokens in the request.
        tokens_limit: Maximum allowed tokens.
    """

    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        tokens_used: Optional[int] = None,
        tokens_limit: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        """Initialize TokenLimitExceededError.

        Args:
            message: Human-readable error message.
            model: Name of the LLM model.
            tokens_used: Number of tokens in the request.
            tokens_limit: Maximum allowed tokens.
            details: Optional dictionary with additional context.
        """
        super().__init__(message, model, details)
        self.tokens_used = tokens_used
        self.tokens_limit = tokens_limit

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary including token counts."""
        result = super().to_dict()
        if self.tokens_used is not None:
            result["tokens_used"] = self.tokens_used
        if self.tokens_limit is not None:
            result["tokens_limit"] = self.tokens_limit
        return result


class ClassificationFailedError(GenAIError):
    """Exception raised when content classification fails."""

    pass


# =============================================================================
# Validation Errors
# =============================================================================


class ValidationError(RepoCtxError):
    """Exception raised for input validation errors.

    Attributes:
        field: Name of the field that failed validation.
        value: The invalid value.
        expected: Description of expected value.
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        expected: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        """Initialize ValidationError.

        Args:
            message: Human-readable error message.
            field: Name of the field that failed validation.
            value: The invalid value.
            expected: Description of expected value.
            details: Optional dictionary with additional context.
        """
        super().__init__(message, details)
        self.field = field
        self.value = value
        self.expected = expected

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary including validation details."""
        result = super().to_dict()
        if self.field:
            result["field"] = self.field
        if self.value is not None:
            result["value"] = self.value
        if self.expected:
            result["expected"] = self.expected
        return result
