"""Factory for creating provider instances."""
from typing import Optional, Dict
from .base import GitProvider
from .exceptions import ProviderConfigError


class ProviderFactory:
    """Factory for creating provider instances."""

    # Registry of provider classes
    _providers: Dict[str, type] = {}

    @classmethod
    def register(cls, name: str, provider_class: type):
        """
        Register a provider class.

        Args:
            name: Provider name (gitlab, github, local, etc.)
            provider_class: Provider class implementing GitProvider
        """
        cls._providers[name] = provider_class

    @classmethod
    def create(
        cls,
        provider_type: str,
        **kwargs
    ) -> GitProvider:
        """
        Create provider instance.

        Args:
            provider_type: Provider type (gitlab, github, local, etc.)
            **kwargs: Provider-specific configuration

        Returns:
            Provider instance

        Raises:
            ProviderConfigError: Provider type not registered or invalid config

        Examples:
            factory.create("gitlab", url="...", token="...")
            factory.create("github", url="...", token="...")
            factory.create("local")
        """
        if provider_type not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ProviderConfigError(
                f"Unknown provider type: {provider_type}. "
                f"Available providers: {available}"
            )

        provider_class = cls._providers[provider_type]

        try:
            return provider_class(**kwargs)
        except TypeError as e:
            raise ProviderConfigError(
                f"Invalid configuration for provider {provider_type}: {e}"
            )

    @classmethod
    def create_gitlab(cls, url: str, token: str) -> GitProvider:
        """
        Create GitLab provider instance.

        Args:
            url: GitLab instance URL
            token: Personal access token

        Returns:
            GitLab provider instance
        """
        return cls.create("gitlab", url=url, token=token)

    @classmethod
    def create_github(
        cls,
        url: str = "https://api.github.com",
        token: Optional[str] = None
    ) -> GitProvider:
        """
        Create GitHub provider instance.

        Args:
            url: GitHub API URL (default: public GitHub)
            token: Personal access token (optional for public repos)

        Returns:
            GitHub provider instance
        """
        return cls.create("github", url=url, token=token)

    @classmethod
    def create_local(cls) -> GitProvider:
        """
        Create local Git provider instance.

        Returns:
            Local provider instance
        """
        return cls.create("local")

    @classmethod
    def from_config(cls, config, provider_type: str) -> GitProvider:
        """
        Create provider from configuration object.

        Args:
            config: Config object with provider settings
            provider_type: Provider type to create

        Returns:
            Provider instance

        Raises:
            ProviderConfigError: Invalid provider type or missing config

        Note:
            Config object should have providers attribute with
            gitlab, github, local sub-objects containing url/token
        """
        if provider_type == "gitlab":
            if not hasattr(config, 'gitlab_url') or not hasattr(config, 'gitlab_token'):
                raise ProviderConfigError(
                    "GitLab provider requires gitlab_url and gitlab_token in config"
                )
            return cls.create_gitlab(
                url=config.gitlab_url,
                token=config.gitlab_token
            )

        elif provider_type == "github":
            # GitHub token is optional for public repos
            url = getattr(config, 'github_url', "https://api.github.com")
            token = getattr(config, 'github_token', None)
            return cls.create_github(url=url, token=token)

        elif provider_type == "local":
            return cls.create_local()

        else:
            raise ProviderConfigError(f"Unknown provider type: {provider_type}")

    @classmethod
    def list_providers(cls) -> list[str]:
        """
        List all registered provider types.

        Returns:
            List of provider names
        """
        return list(cls._providers.keys())

    @classmethod
    def is_registered(cls, provider_type: str) -> bool:
        """
        Check if provider type is registered.

        Args:
            provider_type: Provider type to check

        Returns:
            True if registered, False otherwise
        """
        return provider_type in cls._providers
