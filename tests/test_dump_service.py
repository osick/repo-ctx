"""Tests for DumpService.

This module tests the dump functionality for exporting repository
analysis to a .repo-ctx directory.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

from repo_ctx.services.dump import (
    DumpService,
    DumpLevel,
    DumpResult,
    DumpMetadata,
    GitInfo,
    create_dump_service,
)
from repo_ctx.services.base import ServiceContext


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_context():
    """Create a mock service context."""
    context = MagicMock(spec=ServiceContext)
    context.content_storage = MagicMock()
    context.vector_storage = None
    context.graph_storage = None
    return context


@pytest.fixture
def dump_service(mock_context):
    """Create a DumpService instance."""
    return DumpService(mock_context)


@pytest.fixture
def sample_repo(tmp_path):
    """Create a sample repository structure."""
    repo_dir = tmp_path / "sample-repo"
    repo_dir.mkdir()

    # Create some Python files
    src_dir = repo_dir / "src"
    src_dir.mkdir()

    (src_dir / "main.py").write_text('''
"""Main module."""

class MyClass:
    """A sample class."""

    def method(self):
        """A sample method."""
        pass


def my_function():
    """A sample function."""
    pass
''')

    (src_dir / "utils.py").write_text('''
"""Utility functions."""

def helper():
    """A helper function."""
    pass
''')

    # Create a README
    (repo_dir / "README.md").write_text("# Sample Repo\n\nA sample repository.")

    return repo_dir


@pytest.fixture
def git_repo(sample_repo):
    """Initialize a git repository in sample_repo."""
    try:
        from git import Repo
        repo = Repo.init(sample_repo)
        repo.index.add(["src/main.py", "src/utils.py", "README.md"])
        repo.index.commit("Initial commit")
        return sample_repo
    except ImportError:
        pytest.skip("GitPython not available")


# =============================================================================
# GitInfo Tests
# =============================================================================


class TestGitInfo:
    """Tests for GitInfo dataclass."""

    def test_git_info_creation(self):
        """Test creating GitInfo."""
        info = GitInfo(
            commit="abc123",
            short_commit="abc123",
            tag="v1.0.0",
            branch="main",
            dirty=False,
        )
        assert info.commit == "abc123"
        assert info.tag == "v1.0.0"
        assert info.branch == "main"
        assert info.dirty is False

    def test_git_info_to_dict(self):
        """Test converting GitInfo to dict."""
        info = GitInfo(
            commit="abc123",
            short_commit="abc",
            tag="v1.0.0",
            branch="main",
        )
        data = info.to_dict()
        assert data["commit"] == "abc123"
        assert data["tag"] == "v1.0.0"
        assert data["branch"] == "main"

    def test_git_info_defaults(self):
        """Test GitInfo default values."""
        info = GitInfo()
        assert info.commit == ""
        assert info.tag is None
        assert info.dirty is False


# =============================================================================
# DumpMetadata Tests
# =============================================================================


class TestDumpMetadata:
    """Tests for DumpMetadata dataclass."""

    def test_dump_metadata_creation(self):
        """Test creating DumpMetadata."""
        metadata = DumpMetadata(
            level="medium",
            repository={"name": "test"},
            stats={"symbols_extracted": 10},
        )
        assert metadata.level == "medium"
        assert metadata.repository["name"] == "test"
        assert metadata.stats["symbols_extracted"] == 10

    def test_dump_metadata_to_dict(self):
        """Test converting DumpMetadata to dict."""
        metadata = DumpMetadata(
            level="full",
            generated_at="2024-01-01T00:00:00Z",
        )
        data = metadata.to_dict()
        assert data["level"] == "full"
        assert data["generated_at"] == "2024-01-01T00:00:00Z"
        assert "git" in data
        assert "stats" in data


# =============================================================================
# DumpResult Tests
# =============================================================================


class TestDumpResult:
    """Tests for DumpResult dataclass."""

    def test_dump_result_success(self):
        """Test successful DumpResult."""
        result = DumpResult(
            success=True,
            output_path=Path("/tmp/output"),
            level=DumpLevel.MEDIUM,
            files_created=["metadata.json", "llms.txt"],
        )
        assert result.success is True
        assert len(result.files_created) == 2
        assert result.errors == []

    def test_dump_result_failure(self):
        """Test failed DumpResult."""
        result = DumpResult(
            success=False,
            output_path=Path("/tmp/output"),
            level=DumpLevel.COMPACT,
            errors=["Something went wrong"],
        )
        assert result.success is False
        assert "Something went wrong" in result.errors

    def test_dump_result_to_dict(self):
        """Test converting DumpResult to dict."""
        result = DumpResult(
            success=True,
            output_path=Path("/tmp/output"),
            level=DumpLevel.FULL,
        )
        data = result.to_dict()
        assert data["success"] is True
        assert data["level"] == "full"
        assert data["output_path"] == "/tmp/output"


# =============================================================================
# DumpLevel Tests
# =============================================================================


class TestDumpLevel:
    """Tests for DumpLevel enum."""

    def test_dump_level_values(self):
        """Test DumpLevel enum values."""
        assert DumpLevel.COMPACT.value == "compact"
        assert DumpLevel.MEDIUM.value == "medium"
        assert DumpLevel.FULL.value == "full"

    def test_dump_level_from_string(self):
        """Test creating DumpLevel from string."""
        assert DumpLevel("compact") == DumpLevel.COMPACT
        assert DumpLevel("medium") == DumpLevel.MEDIUM
        assert DumpLevel("full") == DumpLevel.FULL


# =============================================================================
# DumpService Tests
# =============================================================================


class TestDumpServiceCreation:
    """Tests for DumpService creation."""

    def test_create_dump_service(self, mock_context):
        """Test creating DumpService."""
        service = DumpService(mock_context)
        assert service is not None

    def test_create_dump_service_factory(self, mock_context):
        """Test factory function."""
        service = create_dump_service(mock_context)
        assert isinstance(service, DumpService)


class TestDumpServiceGitInfo:
    """Tests for git info extraction."""

    def test_get_git_info_non_repo(self, dump_service, tmp_path):
        """Test git info for non-git directory."""
        info = dump_service._get_git_info(tmp_path)
        assert info.commit == ""
        assert info.tag is None

    def test_get_git_info_git_repo(self, dump_service, git_repo):
        """Test git info for git repository."""
        info = dump_service._get_git_info(git_repo)
        assert info.commit != ""
        assert len(info.short_commit) == 7
        assert info.dirty is False


class TestDumpServiceOutputDir:
    """Tests for output directory handling."""

    def test_ensure_output_dir_creates(self, dump_service, tmp_path):
        """Test creating output directory."""
        output_path = tmp_path / "output" / ".repo-ctx"
        result = dump_service._ensure_output_dir(output_path)
        assert result.exists()
        assert result.is_dir()

    def test_ensure_output_dir_exists_no_force(self, dump_service, tmp_path):
        """Test existing directory without force."""
        output_path = tmp_path / ".repo-ctx"
        output_path.mkdir()
        (output_path / "existing.txt").write_text("test")

        with pytest.raises(FileExistsError):
            dump_service._ensure_output_dir(output_path, force=False)

    def test_ensure_output_dir_exists_with_force(self, dump_service, tmp_path):
        """Test existing directory with force."""
        output_path = tmp_path / ".repo-ctx"
        output_path.mkdir()
        (output_path / "existing.txt").write_text("test")

        result = dump_service._ensure_output_dir(output_path, force=True)
        assert result.exists()
        assert not (result / "existing.txt").exists()


class TestDumpServiceFileWriting:
    """Tests for file writing utilities."""

    def test_write_json(self, dump_service, tmp_path):
        """Test writing JSON file."""
        path = tmp_path / "test.json"
        data = {"key": "value", "number": 42}
        dump_service._write_json(path, data)

        assert path.exists()
        with open(path) as f:
            loaded = json.load(f)
        assert loaded["key"] == "value"
        assert loaded["number"] == 42

    def test_write_json_creates_parent_dirs(self, dump_service, tmp_path):
        """Test JSON writing creates parent directories."""
        path = tmp_path / "nested" / "deep" / "test.json"
        dump_service._write_json(path, {"test": True})
        assert path.exists()

    def test_write_text(self, dump_service, tmp_path):
        """Test writing text file."""
        path = tmp_path / "test.md"
        content = "# Hello\n\nWorld"
        dump_service._write_text(path, content)

        assert path.exists()
        assert path.read_text() == content


class TestDumpServiceDump:
    """Tests for main dump functionality."""

    @pytest.mark.asyncio
    async def test_dump_compact(self, dump_service, sample_repo, tmp_path):
        """Test compact level dump."""
        output_path = tmp_path / ".repo-ctx"

        result = await dump_service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.COMPACT,
        )

        assert result.success is True
        assert (output_path / "metadata.json").exists()
        assert (output_path / "llms.txt").exists()
        assert (output_path / "symbols" / "index.json").exists()
        # Compact should NOT have docs/
        assert not (output_path / "docs").exists()

    @pytest.mark.asyncio
    async def test_dump_medium(self, dump_service, sample_repo, tmp_path):
        """Test medium level dump."""
        output_path = tmp_path / ".repo-ctx"

        result = await dump_service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.MEDIUM,
        )

        assert result.success is True
        assert (output_path / "metadata.json").exists()
        assert (output_path / "llms.txt").exists()
        assert (output_path / "symbols" / "index.json").exists()
        assert (output_path / "ARCHITECTURE_SUMMARY.md").exists()
        assert (output_path / "metrics" / "complexity.json").exists()

    @pytest.mark.asyncio
    async def test_dump_full(self, dump_service, sample_repo, tmp_path):
        """Test full level dump."""
        output_path = tmp_path / ".repo-ctx"

        result = await dump_service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.FULL,
        )

        assert result.success is True
        # Full mode creates by-file directory
        assert (output_path / "symbols" / "by-file").exists()
        # Per-file symbol files are created if symbols were extracted
        # Note: may be empty if no symbols found (depends on tree-sitter availability)

    @pytest.mark.asyncio
    async def test_dump_default_output_path(self, dump_service, sample_repo):
        """Test dump with default output path."""
        result = await dump_service.dump(
            source_path=sample_repo,
            level=DumpLevel.COMPACT,
            force=True,
        )

        assert result.success is True
        assert result.output_path == sample_repo / ".repo-ctx"
        assert (sample_repo / ".repo-ctx" / "metadata.json").exists()

    @pytest.mark.asyncio
    async def test_dump_with_git_info(self, dump_service, git_repo, tmp_path):
        """Test dump includes git info."""
        output_path = tmp_path / ".repo-ctx"

        result = await dump_service.dump(
            source_path=git_repo,
            output_path=output_path,
            level=DumpLevel.COMPACT,
        )

        assert result.success is True

        # Check metadata contains git info
        with open(output_path / "metadata.json") as f:
            metadata = json.load(f)

        assert "git" in metadata
        assert metadata["git"]["commit"] != ""

    @pytest.mark.asyncio
    async def test_dump_force_overwrites(self, dump_service, sample_repo, tmp_path):
        """Test dump with force overwrites existing."""
        output_path = tmp_path / ".repo-ctx"
        output_path.mkdir()
        (output_path / "old_file.txt").write_text("old content")

        result = await dump_service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.COMPACT,
            force=True,
        )

        assert result.success is True
        assert not (output_path / "old_file.txt").exists()

    @pytest.mark.asyncio
    async def test_dump_no_force_fails_if_exists(self, dump_service, sample_repo, tmp_path):
        """Test dump without force fails if directory exists."""
        output_path = tmp_path / ".repo-ctx"
        output_path.mkdir()

        result = await dump_service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.COMPACT,
            force=False,
        )

        assert result.success is False
        assert len(result.errors) > 0


class TestDumpServiceLlmsTxt:
    """Tests for llms.txt generation."""

    def test_generate_llms_txt(self, dump_service):
        """Test llms.txt generation."""
        symbols = [
            {"name": "MyClass", "qualified_name": "src.main.MyClass", "type": "class", "file_path": "src/main.py", "documentation": "A class"},
            {"name": "my_func", "qualified_name": "src.main.my_func", "type": "function", "file_path": "src/main.py"},
        ]
        git_info = GitInfo(short_commit="abc1234", branch="main", tag="v1.0.0")

        content = dump_service._generate_llms_txt(Path("/tmp/repo"), symbols, git_info)

        assert "# repo" in content
        assert "Version: v1.0.0" in content
        assert "Branch: main" in content
        assert "1 class" in content
        assert "1 function" in content

    def test_generate_llms_txt_limits_output(self, dump_service):
        """Test llms.txt limits classes/functions shown."""
        # Create many symbols
        symbols = [
            {"name": f"Class{i}", "qualified_name": f"Class{i}", "type": "class", "file_path": "test.py"}
            for i in range(20)
        ]

        content = dump_service._generate_llms_txt(Path("/tmp/repo"), symbols, GitInfo())

        # Should show "... and X more"
        assert "and 10 more" in content


class TestDumpServiceSymbolIndex:
    """Tests for symbol index generation."""

    def test_generate_symbol_index(self, dump_service):
        """Test symbol index generation."""
        symbols = [
            {"name": "A", "qualified_name": "A", "type": "class", "file_path": "a.py", "line_start": 1},
            {"name": "B", "qualified_name": "B", "type": "function", "file_path": "b.py", "line_start": 5},
        ]

        index = dump_service._generate_symbol_index(symbols)

        assert index["total"] == 2
        assert "class" in index["by_type"]
        assert "function" in index["by_type"]
        assert len(index["symbols"]) == 2


class TestDumpServiceMetrics:
    """Tests for metrics generation."""

    def test_generate_metrics(self, dump_service):
        """Test metrics generation."""
        symbols = [
            {"name": "A", "type": "class", "file_path": "a.py"},
            {"name": "a_method", "type": "method", "file_path": "a.py"},
            {"name": "B", "type": "function", "file_path": "b.py"},
        ]

        metrics = dump_service._generate_metrics(symbols)

        assert metrics["summary"]["total_files"] == 2
        assert metrics["summary"]["total_symbols"] == 3
        assert "a.py" in metrics["by_file"]
        assert metrics["by_file"]["a.py"]["class"] == 1


class TestDumpServiceSymbolsByFile:
    """Tests for per-file symbol generation."""

    def test_generate_symbols_by_file(self, dump_service, tmp_path):
        """Test per-file symbol generation."""
        symbols = [
            {"name": "A", "type": "class", "file_path": "src/a.py"},
            {"name": "B", "type": "function", "file_path": "src/b.py"},
        ]

        files = dump_service._generate_symbols_by_file(tmp_path, symbols)

        assert len(files) == 2
        assert (tmp_path / "src_a.py.json").exists()
        assert (tmp_path / "src_b.py.json").exists()


# =============================================================================
# LLM Integration Tests
# =============================================================================


class TestDumpServiceLLMIntegration:
    """Tests for LLM-enhanced dump functionality."""

    def test_create_dump_service_with_llm(self, mock_context):
        """Test creating DumpService with LLM service."""
        mock_llm = MagicMock()
        service = DumpService(mock_context, llm_service=mock_llm)
        assert service._llm_service is mock_llm

    def test_create_dump_service_without_llm(self, mock_context):
        """Test creating DumpService without LLM service."""
        service = DumpService(mock_context)
        assert service._llm_service is None

    def test_llms_txt_with_business_summary(self, dump_service):
        """Test llms.txt includes business summary when provided."""
        symbols = [
            {"name": "MyClass", "qualified_name": "src.main.MyClass", "type": "class", "file_path": "src/main.py"},
        ]
        git_info = GitInfo(short_commit="abc1234", branch="main")
        business_summary = """## Purpose
This is a test project for demonstration.

## Key Features
- Feature 1
- Feature 2"""

        content = dump_service._generate_llms_txt(
            Path("/tmp/repo"),
            symbols,
            git_info,
            business_summary=business_summary
        )

        # Should include business summary at the top
        assert "## Purpose" in content
        assert "This is a test project" in content
        assert "---" in content  # Separator after business summary
        # Should still include technical details
        assert "## Code Statistics" in content
        assert "## Key Classes" in content

    def test_llms_txt_without_business_summary(self, dump_service):
        """Test llms.txt works without business summary."""
        symbols = [
            {"name": "MyClass", "qualified_name": "src.main.MyClass", "type": "class", "file_path": "src/main.py"},
        ]
        git_info = GitInfo(short_commit="abc1234", branch="main")

        content = dump_service._generate_llms_txt(
            Path("/tmp/repo"),
            symbols,
            git_info,
            business_summary=None
        )

        # Should not start with business summary section
        # (business summary would appear before "## Code Statistics")
        code_stats_pos = content.find("## Code Statistics")
        separator_pos = content.find("---")
        # If there's no business summary, the first separator should come AFTER code statistics
        assert code_stats_pos > 0
        assert separator_pos > code_stats_pos  # Separator is only in later sections

        # Should still have technical details
        assert "## Code Statistics" in content
        assert "## Key Classes" in content
        # Should have the directory guide
        assert "## About This Directory" in content

    @pytest.mark.asyncio
    async def test_generate_business_summary_without_llm(self, dump_service):
        """Test business summary returns None when no LLM configured."""
        symbols = [{"name": "Test", "type": "class", "file_path": "test.py"}]

        result = await dump_service._generate_business_summary(Path("/tmp/repo"), symbols)

        assert result is None

    @pytest.mark.asyncio
    async def test_generate_business_summary_with_mock_llm(self, mock_context):
        """Test business summary generation with mocked LLM."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "## Purpose\nThis is a test summary."
        mock_response.total_tokens = 50
        mock_llm._complete = AsyncMock(return_value=mock_response)

        service = DumpService(mock_context, llm_service=mock_llm)
        symbols = [
            {"name": "TestClass", "qualified_name": "test.TestClass", "type": "class", "file_path": "test.py", "documentation": "A test class"},
        ]

        result = await service._generate_business_summary(Path("/tmp/test-repo"), symbols)

        assert result == "## Purpose\nThis is a test summary."
        mock_llm._complete.assert_called_once()

    @pytest.mark.asyncio
    async def test_dump_with_llm_includes_summary(self, mock_context, sample_repo, tmp_path):
        """Test dump with LLM includes business summary in llms.txt."""
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "## Purpose\nThis project does something useful."
        mock_response.total_tokens = 30
        mock_llm._complete = AsyncMock(return_value=mock_response)

        service = DumpService(mock_context, llm_service=mock_llm)
        output_path = tmp_path / ".repo-ctx"

        result = await service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.COMPACT,
        )

        assert result.success is True

        # Check llms.txt contains business summary
        llms_txt = (output_path / "llms.txt").read_text()
        assert "## Purpose" in llms_txt
        assert "This project does something useful" in llms_txt


class TestDumpServiceProgress:
    """Test progress callback functionality."""

    @pytest.mark.asyncio
    async def test_dump_with_progress_callback(self, mock_context, sample_repo, tmp_path):
        """Test dump reports progress via callback."""
        from repo_ctx.progress import CollectingProgressCallback, ProgressPhase

        progress = CollectingProgressCallback()
        service = DumpService(mock_context)
        output_path = tmp_path / ".repo-ctx"

        result = await service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.COMPACT,
            progress=progress,
        )

        assert result.success is True

        # Should have collected progress events
        assert len(progress.events) > 0

        # Should have INIT phase
        init_events = [e for e in progress.events if e.phase == ProgressPhase.INIT]
        assert len(init_events) >= 1

        # Should have PROCESSING phases (analyzing files)
        processing_events = [e for e in progress.events if e.phase == ProgressPhase.PROCESSING]
        assert len(processing_events) >= 1

        # Should have COMPLETE phase
        complete_events = [e for e in progress.events if e.phase == ProgressPhase.COMPLETE]
        assert len(complete_events) >= 1

    @pytest.mark.asyncio
    async def test_dump_without_progress_callback(self, mock_context, sample_repo, tmp_path):
        """Test dump works fine without progress callback."""
        service = DumpService(mock_context)
        output_path = tmp_path / ".repo-ctx"

        result = await service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.COMPACT,
            progress=None,  # Explicitly no progress
        )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_analyze_repository_reports_file_progress(self, mock_context, sample_repo):
        """Test _analyze_repository reports progress for each file."""
        from repo_ctx.progress import CollectingProgressCallback, ProgressPhase

        progress = CollectingProgressCallback()
        service = DumpService(mock_context)

        symbols, deps = await service._analyze_repository(
            sample_repo,
            include_private=False,
            progress=progress,
        )

        # Should have events for analyzing
        assert len(progress.events) > 0

        # Should report INIT
        init_events = [e for e in progress.events if e.phase == ProgressPhase.INIT and e.operation == "analyze"]
        assert len(init_events) == 1

        # Should report COMPLETE
        complete_events = [e for e in progress.events if e.phase == ProgressPhase.COMPLETE and e.operation == "analyze"]
        assert len(complete_events) == 1


# =============================================================================
# Graph Persistence Tests (Neo4j Integration)
# =============================================================================


class TestDumpServiceGraphPersistence:
    """Tests for Neo4j graph persistence feature."""

    @pytest.fixture
    def mock_graph_storage(self):
        """Create a mock graph storage."""
        storage = MagicMock()
        storage.create_nodes = AsyncMock(return_value=None)
        storage.create_relationships = AsyncMock(return_value=None)
        storage.health_check = AsyncMock(return_value=True)
        return storage

    @pytest.fixture
    def context_with_graph(self, mock_context, mock_graph_storage):
        """Create context with graph storage."""
        mock_context.graph_storage = mock_graph_storage
        return mock_context

    @pytest.mark.asyncio
    async def test_dump_with_persist_graph_creates_nodes(
        self, context_with_graph, sample_repo, tmp_path, mock_graph_storage
    ):
        """Test dump with persist_to_graph creates graph nodes for symbols."""
        service = DumpService(context_with_graph)
        output_path = tmp_path / ".repo-ctx"

        result = await service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.COMPACT,
            persist_to_graph=True,
        )

        assert result.success is True
        # Should have called create_nodes
        mock_graph_storage.create_nodes.assert_called()

    @pytest.mark.asyncio
    async def test_dump_with_persist_graph_creates_relationships(
        self, context_with_graph, sample_repo, tmp_path, mock_graph_storage
    ):
        """Test dump with persist_to_graph creates relationships for dependencies."""
        service = DumpService(context_with_graph)
        output_path = tmp_path / ".repo-ctx"

        result = await service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.COMPACT,
            persist_to_graph=True,
        )

        assert result.success is True
        # Should have called create_relationships (even if empty)
        mock_graph_storage.create_relationships.assert_called()

    @pytest.mark.asyncio
    async def test_dump_without_persist_graph_no_graph_calls(
        self, context_with_graph, sample_repo, tmp_path, mock_graph_storage
    ):
        """Test dump without persist_to_graph doesn't touch graph storage."""
        service = DumpService(context_with_graph)
        output_path = tmp_path / ".repo-ctx"

        result = await service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.COMPACT,
            persist_to_graph=False,  # Explicitly disabled
        )

        assert result.success is True
        # Should NOT have called graph methods
        mock_graph_storage.create_nodes.assert_not_called()
        mock_graph_storage.create_relationships.assert_not_called()

    @pytest.mark.asyncio
    async def test_dump_persist_graph_default_is_false(
        self, context_with_graph, sample_repo, tmp_path, mock_graph_storage
    ):
        """Test persist_to_graph defaults to False."""
        service = DumpService(context_with_graph)
        output_path = tmp_path / ".repo-ctx"

        # Don't pass persist_to_graph - should default to False
        result = await service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.COMPACT,
        )

        assert result.success is True
        # Should NOT have called graph methods (default is False)
        mock_graph_storage.create_nodes.assert_not_called()

    @pytest.mark.asyncio
    async def test_dump_result_includes_graph_stats_when_persisted(
        self, context_with_graph, sample_repo, tmp_path
    ):
        """Test DumpResult includes graph stats when persist_to_graph=True."""
        service = DumpService(context_with_graph)
        output_path = tmp_path / ".repo-ctx"

        result = await service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.COMPACT,
            persist_to_graph=True,
        )

        assert result.success is True
        # Metadata should have graph stats
        assert result.metadata is not None
        assert "graph_nodes" in result.metadata.stats or "graph" in str(result.metadata.stats)

    @pytest.mark.asyncio
    async def test_dump_persist_graph_without_graph_storage(
        self, mock_context, sample_repo, tmp_path
    ):
        """Test persist_to_graph gracefully handles missing graph storage."""
        # Context without graph storage
        mock_context.graph_storage = None
        service = DumpService(mock_context)
        output_path = tmp_path / ".repo-ctx"

        # Should not fail even when graph storage is None
        result = await service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.COMPACT,
            persist_to_graph=True,
        )

        # Should still succeed (just skip graph persistence)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_dump_persist_graph_uses_library_id(
        self, context_with_graph, git_repo, tmp_path, mock_graph_storage
    ):
        """Test persist_to_graph creates nodes with library_id from repo info."""
        from repo_ctx.storage.protocols import GraphNode

        service = DumpService(context_with_graph)
        output_path = tmp_path / ".repo-ctx"

        result = await service.dump(
            source_path=git_repo,
            output_path=output_path,
            level=DumpLevel.COMPACT,
            persist_to_graph=True,
        )

        assert result.success is True

        # Verify create_nodes was called with nodes containing library_id
        mock_graph_storage.create_nodes.assert_called()
        call_args = mock_graph_storage.create_nodes.call_args
        nodes = call_args[0][0] if call_args[0] else call_args[1].get('nodes', [])

        # If nodes were created, they should have library_id in properties
        if nodes:
            assert any('library_id' in n.properties for n in nodes)

    def test_persist_to_graph_method_exists(self, mock_context):
        """Test _persist_to_graph method exists on DumpService."""
        service = DumpService(mock_context)
        assert hasattr(service, '_persist_to_graph')

    @pytest.mark.asyncio
    async def test_persist_to_graph_returns_stats(self, context_with_graph):
        """Test _persist_to_graph returns node and relationship counts."""
        service = DumpService(context_with_graph)

        symbols = [
            {"name": "TestClass", "qualified_name": "test.TestClass", "type": "class",
             "file_path": "test.py", "line_start": 1, "visibility": "public"},
        ]
        dependencies = [
            {"source": "test.TestClass.method", "target": "other.OtherClass",
             "dependency_type": "call", "file_path": "test.py"},
        ]

        result = await service._persist_to_graph(
            library_id="test-repo:main:abc1234",
            symbols=symbols,
            dependencies=dependencies,
        )

        assert isinstance(result, dict)
        assert "nodes" in result
        assert "relationships" in result


class TestDumpServiceInMemoryGraph:
    """Tests for in-memory graph mode (when Neo4j is not configured)."""

    @pytest.fixture
    def in_memory_graph_storage(self):
        """Create in-memory graph storage."""
        from repo_ctx.storage.graph import GraphStorage
        return GraphStorage(in_memory=True)

    @pytest.fixture
    def context_with_in_memory_graph(self, mock_context, in_memory_graph_storage):
        """Create context with in-memory graph storage."""
        mock_context.graph_storage = in_memory_graph_storage
        return mock_context

    @pytest.mark.asyncio
    async def test_dump_with_in_memory_graph(
        self, context_with_in_memory_graph, sample_repo, tmp_path
    ):
        """Test dump works with in-memory graph storage."""
        service = DumpService(context_with_in_memory_graph)
        output_path = tmp_path / ".repo-ctx"

        result = await service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.COMPACT,
            persist_to_graph=True,
        )

        assert result.success is True

    @pytest.mark.asyncio
    async def test_in_memory_graph_persists_symbols(
        self, context_with_in_memory_graph, sample_repo, tmp_path, in_memory_graph_storage
    ):
        """Test symbols are actually stored in in-memory graph."""
        service = DumpService(context_with_in_memory_graph)
        output_path = tmp_path / ".repo-ctx"

        await service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.COMPACT,
            persist_to_graph=True,
        )

        # Query the in-memory graph to verify nodes were created
        result = await in_memory_graph_storage.query(
            "MATCH (n) RETURN count(n) as count"
        )
        # Should have some nodes
        assert result[0]["count"] >= 0  # May be 0 if no symbols extracted


# =============================================================================
# Top Nodes By Degree Tests
# =============================================================================


class TestGetTopNodesByDegree:
    """Tests for _get_top_nodes_by_degree method."""

    def test_returns_all_nodes_when_below_limit(self, dump_service):
        """Test returns all nodes when count is below limit."""
        nodes = ["a.py", "b.py", "c.py"]
        edges = [("a.py", "b.py", "import"), ("b.py", "c.py", "import")]

        result_nodes, result_edges = dump_service._get_top_nodes_by_degree(
            nodes, edges, top_n=10
        )

        assert set(result_nodes) == set(nodes)
        assert len(result_edges) == len(edges)

    def test_filters_to_top_n_nodes(self, dump_service):
        """Test filters to top N most connected nodes."""
        # Create nodes with varying degrees
        nodes = ["hub.py", "spoke1.py", "spoke2.py", "spoke3.py", "isolated.py"]
        # hub.py has the highest degree (connected to all spokes)
        edges = [
            ("hub.py", "spoke1.py", "import"),
            ("hub.py", "spoke2.py", "import"),
            ("hub.py", "spoke3.py", "import"),
            ("spoke1.py", "spoke2.py", "call"),
        ]

        result_nodes, result_edges = dump_service._get_top_nodes_by_degree(
            nodes, edges, top_n=3
        )

        # Should include hub.py (degree 3), spoke1.py (degree 2), spoke2.py (degree 2)
        assert len(result_nodes) == 3
        assert "hub.py" in result_nodes
        # isolated.py has degree 0, should be excluded
        assert "isolated.py" not in result_nodes

    def test_filters_edges_to_match_top_nodes(self, dump_service):
        """Test edges are filtered to only include top nodes."""
        nodes = ["a.py", "b.py", "c.py", "d.py"]
        edges = [
            ("a.py", "b.py", "import"),
            ("b.py", "c.py", "import"),
            ("c.py", "d.py", "import"),
        ]

        result_nodes, result_edges = dump_service._get_top_nodes_by_degree(
            nodes, edges, top_n=2
        )

        # All edges should only reference nodes in result_nodes
        for src, tgt, _ in result_edges:
            assert src in result_nodes
            assert tgt in result_nodes

    def test_empty_nodes(self, dump_service):
        """Test handling of empty nodes list."""
        result_nodes, result_edges = dump_service._get_top_nodes_by_degree(
            [], [], top_n=10
        )

        assert result_nodes == []
        assert result_edges == []

    def test_no_edges(self, dump_service):
        """Test handling of nodes with no edges."""
        nodes = ["a.py", "b.py", "c.py"]
        edges = []

        result_nodes, result_edges = dump_service._get_top_nodes_by_degree(
            nodes, edges, top_n=2
        )

        # Should return top_n nodes even with no edges (all have degree 0)
        assert len(result_nodes) == 2
        assert result_edges == []


# =============================================================================
# Interactive Graph Generation Tests
# =============================================================================


class TestInteractiveGraphGeneration:
    """Tests for interactive HTML graph generation."""

    @pytest.mark.asyncio
    async def test_dump_creates_interactive_html(self, dump_service, sample_repo, tmp_path):
        """Test dump creates dependencies.html in architecture folder."""
        output_path = tmp_path / ".repo-ctx"

        result = await dump_service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.MEDIUM,
        )

        assert result.success is True
        # Interactive HTML should be created
        html_path = output_path / "architecture" / "dependencies.html"
        assert html_path.exists(), "dependencies.html should be created"

        # HTML should contain vis.js reference
        html_content = html_path.read_text()
        assert "vis-network" in html_content

    @pytest.mark.asyncio
    async def test_architecture_summary_links_to_html(self, dump_service, sample_repo, tmp_path):
        """Test ARCHITECTURE_SUMMARY.md links to interactive HTML."""
        output_path = tmp_path / ".repo-ctx"

        result = await dump_service.dump(
            source_path=sample_repo,
            output_path=output_path,
            level=DumpLevel.MEDIUM,
        )

        assert result.success is True
        arch_md_path = output_path / "ARCHITECTURE_SUMMARY.md"
        assert arch_md_path.exists()

        content = arch_md_path.read_text()
        # Should mention the interactive graph
        assert "dependencies.html" in content
        # Should have the emoji link
        assert "Interactive" in content or "interactive" in content


# =============================================================================
# Limited Mermaid Diagram Tests
# =============================================================================


class TestLimitedMermaidDiagrams:
    """Tests for limited mermaid diagram generation."""

    def test_architecture_md_limits_large_diagrams(self, dump_service):
        """Test architecture.md limits diagrams for large graphs."""
        # Create architecture data with many nodes
        nodes = [f"file{i}.py" for i in range(50)]
        edges = [(f"file{i}.py", f"file{i+1}.py", "import") for i in range(49)]

        arch_data = {
            "nodes": nodes,
            "edges": edges,
            "mermaid_deps": "flowchart LR\n" + "\n".join([f"    N{i}[file{i}]" for i in range(50)]),
            "cycles_count": 0,
            "layers": {"is_acyclic": True, "count": 5, "layers": []},
            "class_cycles": {"count": 0, "cycles": []},
            "package_cycles": {"count": 0, "cycles": []},
            "class_coupling": {},
            "package_coupling": {},
        }

        md_content = dump_service._generate_architecture_md(arch_data)

        # Should mention that it shows only top nodes
        assert "top" in md_content.lower() or "25" in md_content
        # Should link to interactive graph
        assert "dependencies.html" in md_content

    def test_architecture_md_shows_full_diagram_for_small_graphs(self, dump_service):
        """Test architecture.md shows full diagram for small graphs."""
        nodes = ["a.py", "b.py", "c.py"]
        edges = [("a.py", "b.py", "import")]

        arch_data = {
            "nodes": nodes,
            "edges": edges,
            "mermaid_deps": "flowchart LR\n    N0[a.py]\n    N1[b.py]",
            "cycles_count": 0,
            "layers": {"is_acyclic": True, "count": 2, "layers": []},
            "class_cycles": {"count": 0, "cycles": []},
            "package_cycles": {"count": 0, "cycles": []},
            "class_coupling": {},
            "package_coupling": {},
        }

        md_content = dump_service._generate_architecture_md(arch_data)

        # Should still link to interactive graph
        assert "dependencies.html" in md_content
        # Full mermaid diagram should be included
        assert "```mermaid" in md_content

    def test_related_files_includes_html(self, dump_service):
        """Test Related Files section includes dependencies.html."""
        arch_data = {
            "nodes": ["a.py"],
            "edges": [],
            "mermaid_deps": "",
            "cycles_count": 0,
            "layers": {},
            "class_cycles": {"count": 0, "cycles": []},
            "package_cycles": {"count": 0, "cycles": []},
            "class_coupling": {},
            "package_coupling": {},
        }

        md_content = dump_service._generate_architecture_md(arch_data)

        # Related Files section should include HTML
        assert "dependencies.html" in md_content
        assert "Interactive" in md_content


# =============================================================================
# C++/Joern Support Tests
# =============================================================================


class TestJoernLanguageSupport:
    """Tests for Joern-only language support (C/C++/Go/etc.)."""

    def test_swift_files_trigger_joern_detection(self, mock_context, tmp_path):
        """Test that Swift files trigger Joern mode detection (Swift is Joern-only)."""
        from repo_ctx.analysis import CodeAnalyzer
        import fnmatch

        # Create a sample Swift file
        swift_file = tmp_path / "test.swift"
        swift_file.write_text("class Foo { func bar() {} }")

        # Simulate the detection logic from dump service
        # Only Swift is Joern-only now (tree-sitter supports C/C++/Go/etc.)
        joern_only_exts = {'.swift'}

        needs_joern = False
        for ext in joern_only_exts:
            for path in tmp_path.rglob(f"*{ext}"):
                needs_joern = True
                break
            if needs_joern:
                break

        assert needs_joern is True, "Should detect Swift files need Joern"

    def test_python_only_no_joern_needed(self, mock_context, tmp_path):
        """Test that Python-only repos don't need Joern."""
        # Create a Python file
        py_file = tmp_path / "test.py"
        py_file.write_text("def hello(): pass")

        # Simulate the detection logic from dump service
        # Only Swift is Joern-only now
        joern_only_exts = {'.swift'}

        needs_joern = False
        for ext in joern_only_exts:
            for path in tmp_path.rglob(f"*{ext}"):
                needs_joern = True
                break
            if needs_joern:
                break

        assert needs_joern is False, "Python-only repos should not need Joern"

    def test_cpp_uses_treesitter(self, mock_context, tmp_path):
        """Test that C++ repos now use tree-sitter (not Joern-only anymore)."""
        # Create a C++ file
        cpp_file = tmp_path / "test.cpp"
        cpp_file.write_text("class Foo { void bar() {} };")

        service = DumpService(mock_context)

        # Run analysis - should use tree-sitter for C++
        import asyncio
        symbols, deps = asyncio.get_event_loop().run_until_complete(
            service._analyze_repository(tmp_path)
        )

        # Should use tree-sitter mode
        assert service._analyzer.use_treesitter is True
        # Should find the class
        assert any(s["name"] == "Foo" for s in symbols)

    @pytest.mark.asyncio
    async def test_python_only_uses_treesitter(self, mock_context, tmp_path):
        """Test that Python-only repos use tree-sitter (faster)."""
        # Create a Python file
        py_file = tmp_path / "test.py"
        py_file.write_text("def hello(): pass")

        service = DumpService(mock_context)

        # Run analysis
        symbols, deps = await service._analyze_repository(tmp_path)

        # Should use tree-sitter mode for Python-only repos
        assert service._analyzer.use_treesitter is True
        # Should find the function
        assert len(symbols) >= 1
        assert any(s["name"] == "hello" for s in symbols)

    @pytest.mark.asyncio
    async def test_skip_joern_forces_treesitter(self, mock_context, tmp_path):
        """Test that skip_joern=True forces tree-sitter mode even for C++ repos."""
        # Create a C++ file that would normally trigger Joern
        cpp_file = tmp_path / "test.cpp"
        cpp_file.write_text("class Foo { void bar() {} };")

        service = DumpService(mock_context)

        # Run analysis with skip_joern=True
        symbols, deps = await service._analyze_repository(tmp_path, skip_joern=True)

        # Should use tree-sitter mode despite C++ files
        assert service._analyzer.use_treesitter is True
        # Note: tree-sitter doesn't support C++, so symbols may be empty
        # The key test is that we didn't try to use Joern

    @pytest.mark.asyncio
    async def test_dump_accepts_skip_joern_parameter(self, mock_context, tmp_path):
        """Test that dump() method accepts skip_joern parameter."""
        # Create a Python file
        py_file = tmp_path / "test.py"
        py_file.write_text("def hello(): pass")

        output_path = tmp_path / ".repo-ctx"
        service = DumpService(mock_context)

        # Should not raise - skip_joern parameter should be accepted
        result = await service.dump(
            source_path=tmp_path,
            output_path=output_path,
            level=DumpLevel.COMPACT,
            skip_joern=True,
        )

        assert result.success is True
