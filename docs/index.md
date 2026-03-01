# repo-ctx

A Git repository documentation indexer and code analyzer for AI assistants and developers.

repo-ctx indexes documentation and analyzes code from Git repositories (GitHub, GitLab, local), making them searchable and accessible via **MCP Server**, **CLI**, or **Python API**.

## Quick Start

### As MCP Server (AI Assistants)

```json
{
  "mcpServers": {
    "repo-ctx": {
      "command": "uvx",
      "args": ["repo-ctx"]
    }
  }
}
```

### As CLI

```bash
pip install repo-ctx

# Index a repository
repo-ctx index fastapi/fastapi

# Search
repo-ctx search "authentication"

# Analyze code
repo-ctx analyze ./src --lang python
```

### As Python Library

```python
from repo_ctx.client import RepoCtxClient

client = RepoCtxClient()
await client.init()
results = await client.search("fastapi")
```

## Key Features

| Feature | Description |
|---------|-------------|
| **Multi-provider** | GitHub, GitLab, and local Git repositories |
| **18 MCP tools** | `ctx-*` tools for indexing, search, analysis, architecture |
| **Code analysis** | Symbol extraction for 12 languages via Joern CPG or tree-sitter |
| **Architecture analysis** | DSM, cycle detection, layer detection, XS metrics |
| **Documentation indexing** | Full-text search across indexed repositories |

## Documentation

| Guide | Audience |
|-------|----------|
| [User Guide](user_guide.md) | End users — installation, configuration, usage |
| [Configuration](configuration.md) | All configuration options |
| [MCP Tools Reference](mcp_tools_reference.md) | MCP tool parameters and examples |
| [Architecture Analysis](architecture_analysis_guide.md) | DSM, cycles, layers, metrics |
| [Multi-Provider Guide](multi-provider-guide.md) | GitHub, GitLab, local provider setup |
| [Developer Guide](dev_guide.md) | Contributors — architecture, adding features |
| [API Reference](library/api-reference.md) | Python library API |
