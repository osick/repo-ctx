# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

repo-ctx is a Git repository documentation indexer with three interfaces:
- **MCP Server** - Primary use case for LLM integration
- **CLI** - Standalone searching and indexing
- **Python Library** - Custom integrations

Supports GitLab, GitHub, and local Git repositories with auto-detection.

## Common Commands

```bash
# Install dependencies
uv pip install -e .

# Run tests with coverage
pytest tests/ -v --cov=repo_ctx

# Run single test file
pytest tests/test_config.py -v

# Lint code
ruff check repo_ctx/

# Format code
ruff format repo_ctx/

# Run as CLI
uv run repo-ctx --index group/project --provider gitlab
uv run repo-ctx --index owner/repo --provider github
uv run repo-ctx --index /path/to/repo --provider local

# Start MCP server
uv run repo-ctx

# Search
uv run repo-ctx search "query"

# Analyze code
uv run repo-ctx analyze ./src --language python
```

## Architecture

### Core Components

```
repo_ctx/
├── core.py           # Main API: RepositoryContext, GitLabContext
├── config.py         # Configuration management (env, YAML, CLI args)
├── storage.py        # SQLite persistence (aiosqlite)
├── mcp_server.py     # MCP protocol implementation
├── parser.py         # Markdown processing and filtering
├── models.py         # Dataclasses: Library, Document, SearchResult
├── providers/        # Git provider abstraction
│   ├── base.py       # Abstract GitProvider interface
│   ├── factory.py    # Provider factory
│   ├── local.py      # Local filesystem provider
│   ├── github.py     # GitHub API provider
│   └── gitlab.py     # GitLab API provider
├── analysis/         # Code analysis (tree-sitter based)
│   ├── code_analyzer.py    # Main analyzer orchestrating extractors
│   ├── python_extractor.py # Python symbol extraction
│   ├── javascript_extractor.py # JS/TS symbol extraction
│   ├── java_extractor.py   # Java symbol extraction
│   ├── kotlin_extractor.py # Kotlin symbol extraction
│   └── dependency_graph.py # Dependency graph generation
└── cli/              # CLI commands
    ├── commands.py   # CLI command implementations
    └── interactive.py # Interactive mode
```

### Provider Abstraction

All Git operations go through the `GitProvider` interface (`providers/base.py`). The factory (`providers/factory.py`) creates appropriate provider based on type or auto-detection from path format.

### Data Flow

1. **Indexing**: Provider → Parser → Storage (SQLite)
2. **Search**: Query → Storage → FuzzyMatch → Results
3. **Analysis**: Files → TreeSitter → Extractors → Symbols

### Database

SQLite with tables: `libraries`, `versions`, `documents`, `symbols`, `dependencies`. Uses async operations via aiosqlite.

## Adding Features

### New MCP Tool

1. Add tool definition in `mcp_server.py` `list_tools()`
2. Implement handler in `call_tool()`
3. Add core logic in `core.py`
4. Write tests in `tests/test_mcp_tools.py`

### New Provider

1. Create `providers/newprovider.py` implementing `GitProvider`
2. Register in `providers/factory.py`
3. Add config support in `config.py`
4. Write tests in `tests/test_providers_newprovider.py`

### New Language Extractor

1. Create `analysis/language_extractor.py` implementing extraction
2. Register in `analysis/code_analyzer.py`
3. Add tree-sitter dependency to `pyproject.toml`
4. Write tests in `tests/test_analysis_language.py`

## Testing

Tests use pytest with async support. Key fixtures in `tests/conftest.py`:
- Mock providers and storage use in-memory SQLite
- Use `tmp_path` for filesystem tests
- Mock external APIs (GitLab, GitHub)

Run specific test categories:
```bash
pytest tests/test_analysis_*.py -v   # Analysis tests
pytest tests/test_providers_*.py -v  # Provider tests
pytest tests/test_mcp_*.py -v        # MCP tool tests
```

## Key Dependencies

- `mcp` - MCP protocol
- `python-gitlab`, `PyGithub`, `GitPython` - Git providers
- `tree-sitter-*` - Code analysis
- `aiosqlite` - Async database
- `networkx` - Dependency graphs
