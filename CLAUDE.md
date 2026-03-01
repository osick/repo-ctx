# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

repo-ctx is a Git repository documentation indexer and code analyzer with three interfaces:
- **MCP Server** - Primary use case for LLM integration
- **CLI** - Standalone searching and indexing
- **Python Library** - Custom integrations

Supports GitLab, GitHub, and local Git repositories with auto-detection.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    CLI      │     │ MCP Server  │     │ Python API  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       └───────────────────┼───────────────────┘
                           ▼
               ┌───────────────────────┐
               │   RepoCtxClient       │
               │   (Unified Interface) │
               └───────────┬───────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Services   │    │    Core     │    │  Analysis   │
│ (Chunking,  │    │ (Providers, │    │ (Joern, TS, │
│ Enrichment) │    │  Storage)   │    │  Graphs)    │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `client/` | Unified RepoCtxClient for all interfaces |
| `services/` | Business logic (chunking, enrichment, search) |
| `analysis/` | Code analysis (Joern, tree-sitter, architecture) |
| `providers/` | Git provider abstraction (GitHub, GitLab, local) |
| `cli/` | CLI commands |
| `mcp/` | MCP server context |

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

## Project Structure

```
repo_ctx/
├── core.py           # Main API: RepositoryContext, GitLabContext
├── config.py         # Configuration management (env, YAML, CLI args)
├── storage.py        # SQLite persistence (aiosqlite)
├── mcp_server.py     # MCP server entry point (thin shell)
├── mcp_tools_ctx.py  # All ctx-* tool definitions and handlers
├── parser.py         # Markdown processing and filtering
├── models.py         # Dataclasses: Library, Document, SearchResult
│
├── client/           # Unified client
│   ├── client.py     # RepoCtxClient - dual mode (direct/HTTP)
│   └── models.py     # Client data models
│
├── services/         # Service layer
│   ├── chunking.py   # Content chunking strategies
│   ├── enrichment.py # LLM-enhanced metadata
│   ├── embedding.py  # LLM embedding service (litellm, multi-provider)
│   ├── combined_search.py # Semantic + full-text search
│   ├── llm.py        # LLM service
│   └── ...           # Other services
│
├── providers/        # Git provider abstraction
│   ├── base.py       # Abstract GitProvider interface
│   ├── factory.py    # Provider factory
│   ├── local.py      # Local filesystem provider
│   ├── github.py     # GitHub API provider
│   └── gitlab.py     # GitLab API provider
│
├── analysis/         # Code analysis (tree-sitter based)
│   ├── code_analyzer.py    # Main analyzer orchestrating extractors
│   ├── file_enhancer.py    # LLM file documentation (parallel, retry)
│   ├── codebase_summarizer.py # Business/technical summaries
│   ├── interactive_graph.py # vis.js interactive HTML graphs
│   ├── prompts.py          # LLM prompt templates
│   ├── architecture.py     # DSM, cycle detection, layer detection
│   ├── structural_metrics.py # XS complexity scoring
│   ├── python_extractor.py # Python symbol extraction
│   ├── javascript_extractor.py # JS/TS symbol extraction
│   ├── java_extractor.py   # Java symbol extraction
│   ├── kotlin_extractor.py # Kotlin symbol extraction
│   └── dependency_graph.py # Dependency graph generation
│
├── api/              # FastAPI REST API server
│   ├── app.py        # FastAPI application with lifespan, middleware
│   ├── auth.py       # Authentication configuration
│   ├── middleware.py  # Logging, security headers, rate limiting
│   └── routes/       # Endpoint modules (health, indexing, search, analysis, etc.)
│
├── storage/          # Persistence layer
│   ├── vector.py     # Qdrant vector storage (semantic search)
│   └── protocols.py  # Storage protocols (VectorStorageProtocol)
│
├── joern/            # Joern CPG integration (optional)
│   └── adapter.py    # JoernAdapter
│
└── cli/              # CLI commands
    ├── context.py    # CLIContext (wraps RepoCtxClient)
    ├── flat_commands.py  # CLI command implementations
    └── interactive.py # Interactive mode
```

### Data Flow

1. **Indexing**: Provider -> Parser -> Storage (SQLite)
2. **Search**: Query -> Storage -> FuzzyMatch -> Results
3. **Analysis**: Files -> TreeSitter/Joern -> Extractors -> Symbols
4. **Content**: Content -> Chunking -> Enrichment -> Enhanced Content

## Adding Features

### New Service

1. Create `services/newservice.py` extending `BaseService`
2. Add factory function in `services/__init__.py`
3. Export in `__all__`
4. Write tests in `tests/test_newservice.py`

### New MCP Tool

1. Add tool definition in `mcp_tools_ctx.py` `get_ctx_tools()` — use `ctx-<name>` naming
2. Add handler in `mcp_tools_ctx.py` `handle_ctx_tool()`
3. Register name in `tool_names.py` `CTX_TOOLS`
4. Write tests in `tests/test_mcp_tools_ctx.py`

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
pytest tests/test_client.py -v        # Unified client tests
pytest tests/test_chunking.py -v      # Chunking service tests
pytest tests/test_enrichment.py -v    # Enrichment service tests
pytest tests/test_file_enhancer.py -v # File enhancement (parallel, retry)
pytest tests/test_codebase_summarizer.py -v  # Codebase summaries
pytest tests/test_interactive_graph.py -v    # Interactive HTML graph
pytest tests/test_analysis_*.py -v    # Analysis tests
pytest tests/test_providers_*.py -v   # Provider tests
pytest tests/test_mcp_*.py -v         # MCP tool tests
```

Coverage target: >80%

## Key Dependencies

- `mcp` - MCP protocol
- `python-gitlab`, `PyGithub`, `GitPython` - Git providers
- `tree-sitter-*` - Code analysis (Python, JS/TS, Java, Kotlin, C, C++, Go, Rust, Ruby, PHP, C#, Bash)
- `aiosqlite` - Async database
- `networkx` - Dependency graphs
- `fastapi`, `uvicorn` - REST API server
- `qdrant-client` - Vector storage for semantic search
- `litellm` - Multi-LLM and embedding support
- Joern (external, optional) - Full CPG analysis

## Documentation

| Stakeholder | Document |
|-------------|----------|
| End Users | [docs/user_guide.md](docs/user_guide.md) |
| Library Users | [docs/library/api-reference.md](docs/library/api-reference.md) |
| Contributors | [docs/dev_guide.md](docs/dev_guide.md) |
| Architecture | [docs/architecture_analysis_guide.md](docs/architecture_analysis_guide.md) |
