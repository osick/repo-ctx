"""Tests for CLI service layer integration.

This module tests the integration between CLI commands and the service layer,
ensuring CLI uses services by default with legacy fallback.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from argparse import Namespace

from repo_ctx.config import Config


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_config():
    """Create a mock config."""
    config = MagicMock(spec=Config)
    config.storage_path = ":memory:"
    config.storage = None
    config.gitlab_url = None
    config.gitlab_token = None
    config.github_url = None
    config.github_token = None
    return config


@pytest.fixture
def mock_legacy_context():
    """Create a mock legacy context."""
    context = AsyncMock()
    context.init = AsyncMock()
    context.storage = AsyncMock()
    context.search_libraries = AsyncMock(return_value=[])
    context.fuzzy_search_libraries = AsyncMock(return_value=[])
    context.index_repository = AsyncMock()
    context.index_group = AsyncMock(return_value={"indexed": [], "failed": []})
    context.get_documentation = AsyncMock(return_value={"content": []})
    context.list_all_libraries = AsyncMock(return_value=[])
    context._get_repository_url = MagicMock(return_value="https://github.com/test/repo")
    return context


# =============================================================================
# CLIContext Tests
# =============================================================================


class TestCLIContextCreation:
    """Tests for CLIContext creation."""

    def test_create_with_config(self, mock_config):
        """Test creating CLIContext with config."""
        with patch('repo_ctx.cli.context.GitLabContext') as mock_gitlab:
            mock_gitlab.return_value = MagicMock()

            from repo_ctx.cli.context import CLIContext

            ctx = CLIContext(mock_config)
            assert ctx is not None

    def test_create_with_legacy_mode(self, mock_config, mock_legacy_context):
        """Test creating CLIContext in legacy mode."""
        from repo_ctx.cli.context import CLIContext

        ctx = CLIContext(mock_config, legacy_mode=True, legacy_context=mock_legacy_context)
        assert ctx.use_legacy is True

    def test_create_with_services_mode(self, mock_config, mock_legacy_context):
        """Test creating CLIContext in services mode (default)."""
        from repo_ctx.cli.context import CLIContext

        ctx = CLIContext(mock_config, legacy_mode=False, legacy_context=mock_legacy_context)
        assert ctx.use_legacy is False


class TestCLIContextInit:
    """Tests for CLIContext initialization."""

    @pytest.mark.asyncio
    async def test_init_services_mode(self, mock_config, mock_legacy_context):
        """Test init in services mode initializes both."""
        from repo_ctx.cli.context import CLIContext

        ctx = CLIContext(mock_config, legacy_mode=False, legacy_context=mock_legacy_context)
        await ctx.init()

        mock_legacy_context.init.assert_called_once()
        assert ctx.services is not None

    @pytest.mark.asyncio
    async def test_init_legacy_mode(self, mock_config, mock_legacy_context):
        """Test init in legacy mode only initializes legacy."""
        from repo_ctx.cli.context import CLIContext

        ctx = CLIContext(mock_config, legacy_mode=True, legacy_context=mock_legacy_context)
        await ctx.init()

        mock_legacy_context.init.assert_called_once()


class TestCLIContextIndexing:
    """Tests for CLIContext indexing operations."""

    @pytest.mark.asyncio
    async def test_index_repository_services_mode(self, mock_config, mock_legacy_context):
        """Test index_repository uses service layer in services mode."""
        from repo_ctx.cli.context import CLIContext

        ctx = CLIContext(mock_config, legacy_mode=False, legacy_context=mock_legacy_context)
        await ctx.init()

        # Mock the indexing service
        ctx._indexing.index_repository = AsyncMock(return_value={"status": "completed"})

        result = await ctx.index_repository("owner", "repo", provider_type="github")

        ctx._indexing.index_repository.assert_called_once()

    @pytest.mark.asyncio
    async def test_index_repository_legacy_mode(self, mock_config, mock_legacy_context):
        """Test index_repository uses legacy in legacy mode."""
        from repo_ctx.cli.context import CLIContext

        ctx = CLIContext(mock_config, legacy_mode=True, legacy_context=mock_legacy_context)
        await ctx.init()

        await ctx.index_repository("owner", "repo", provider_type="github")

        mock_legacy_context.index_repository.assert_called_once()


class TestCLIContextSearch:
    """Tests for CLIContext search operations."""

    @pytest.mark.asyncio
    async def test_fuzzy_search_services_mode(self, mock_config, mock_legacy_context):
        """Test fuzzy_search uses service layer."""
        from repo_ctx.cli.context import CLIContext

        ctx = CLIContext(mock_config, legacy_mode=False, legacy_context=mock_legacy_context)
        await ctx.init()

        # Services mode still uses legacy for search (not yet migrated)
        await ctx.fuzzy_search_libraries("test", limit=10)

        mock_legacy_context.fuzzy_search_libraries.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_all_libraries_services_mode(self, mock_config, mock_legacy_context):
        """Test list_all_libraries uses repository service in services mode."""
        from repo_ctx.cli.context import CLIContext

        ctx = CLIContext(mock_config, legacy_mode=False, legacy_context=mock_legacy_context)
        await ctx.init()

        # Mock the repository service
        ctx._repository.list_repositories = AsyncMock(return_value=[])

        await ctx.list_all_libraries()

        ctx._repository.list_repositories.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_all_libraries_legacy_mode(self, mock_config, mock_legacy_context):
        """Test list_all_libraries uses legacy in legacy mode."""
        from repo_ctx.cli.context import CLIContext

        ctx = CLIContext(mock_config, legacy_mode=True, legacy_context=mock_legacy_context)
        await ctx.init()

        await ctx.list_all_libraries()

        mock_legacy_context.list_all_libraries.assert_called_once()


class TestCLIContextAnalysis:
    """Tests for CLIContext analysis operations."""

    @pytest.mark.asyncio
    async def test_analyze_code_services_mode(self, mock_config, mock_legacy_context):
        """Test analyze_code uses analysis service."""
        from repo_ctx.cli.context import CLIContext

        ctx = CLIContext(mock_config, legacy_mode=False, legacy_context=mock_legacy_context)
        await ctx.init()

        code = "def hello(): pass"
        result = ctx.analyze_code(code, "test.py")

        assert "symbols" in result
        assert "dependencies" in result

    @pytest.mark.asyncio
    async def test_get_supported_languages(self, mock_config, mock_legacy_context):
        """Test get_supported_languages uses analysis service."""
        from repo_ctx.cli.context import CLIContext

        ctx = CLIContext(mock_config, legacy_mode=False, legacy_context=mock_legacy_context)
        await ctx.init()

        languages = ctx.get_supported_languages()

        assert isinstance(languages, list)
        assert "python" in languages


# =============================================================================
# CLI Parser Tests
# =============================================================================


class TestCLIParserLegacyFlag:
    """Tests for --legacy flag in CLI parser."""

    def test_parser_has_legacy_flag(self):
        """Test parser includes --legacy flag."""
        from repo_ctx.cli import create_parser

        parser = create_parser()
        args = parser.parse_args(["--legacy", "list"])

        assert hasattr(args, 'legacy')
        assert args.legacy is True

    def test_parser_default_no_legacy(self):
        """Test parser defaults to no legacy flag."""
        from repo_ctx.cli import create_parser

        parser = create_parser()
        args = parser.parse_args(["list"])

        assert hasattr(args, 'legacy')
        assert args.legacy is False


# =============================================================================
# CLI Command Tests
# =============================================================================


class TestCLICommands:
    """Tests for CLI command execution with services."""

    @pytest.mark.asyncio
    async def test_cmd_list_uses_context(self):
        """Test list command uses CLIContext."""
        from repo_ctx.cli.flat_commands import cmd_list

        args = Namespace(
            config=None,
            provider="auto",
            output="json",
            legacy=False,
        )

        with patch('repo_ctx.cli.flat_commands.CLIContext') as mock_ctx_class:
            mock_ctx = AsyncMock()
            mock_ctx.init = AsyncMock()
            mock_ctx.list_all_libraries = AsyncMock(return_value=[])
            mock_ctx_class.return_value = mock_ctx

            with patch('repo_ctx.cli.flat_commands.Config') as mock_config:
                mock_config.load.return_value = MagicMock()

                # Capture stdout
                import io
                import sys
                captured = io.StringIO()
                sys.stdout = captured

                try:
                    await cmd_list(args)
                finally:
                    sys.stdout = sys.__stdout__

                mock_ctx.list_all_libraries.assert_called_once()

    @pytest.mark.asyncio
    async def test_cmd_analyze_uses_services(self):
        """Test analyze command uses analysis service."""
        import tempfile
        import os

        # Create a temp file to analyze
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def hello(): pass\n")
            temp_path = f.name

        try:
            args = Namespace(
                config=None,
                provider="auto",
                output="json",
                legacy=False,
                target=temp_path,
                lang=None,
                type=None,
                private=True,
                refresh=False,
                dialect=None,
            )

            with patch('repo_ctx.cli.flat_commands.CLIContext') as mock_ctx_class:
                mock_ctx = AsyncMock()
                mock_ctx.init = AsyncMock()
                mock_ctx.use_legacy = False
                mock_ctx.analyze_code = MagicMock(return_value={
                    "symbols": [{"name": "hello", "symbol_type": "function"}],
                    "dependencies": [],
                    "language": "python",
                    "file_path": temp_path,
                })
                mock_ctx_class.return_value = mock_ctx

                with patch('repo_ctx.cli.flat_commands.Config') as mock_config:
                    mock_config.load.return_value = MagicMock()

                    from repo_ctx.cli.flat_commands import cmd_analyze

                    # Capture stdout
                    import io
                    import sys
                    captured = io.StringIO()
                    sys.stdout = captured

                    try:
                        await cmd_analyze(args)
                    finally:
                        sys.stdout = sys.__stdout__

        finally:
            os.unlink(temp_path)
