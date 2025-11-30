# repo-ctx

A Git repository documentation indexer and code analyzer for AI assistants and developers.

**[User Guide](docs/USER_GUIDE.md)** | [MCP Tools Reference](docs/mcp_tools_reference.md) | [API Documentation](docs/library/api-reference.md)

---

## What is repo-ctx?

repo-ctx indexes documentation and analyzes code from Git repositories, making them searchable and accessible to AI assistants (via MCP) and developers (via CLI or Python API).

**Key Features:**
- Index repositories from **GitHub**, **GitLab**, or **local** filesystems
- **Fuzzy search** across all indexed documentation
- **Code analysis** for Python, JavaScript, TypeScript, Java, and Kotlin
- **MCP server** for seamless AI assistant integration
- Works with **Claude Code**, **Cursor**, **VS Code Copilot**, and other MCP-compatible tools

---

## Quick Start

```bash
# Install
pip install repo-ctx

# Index a local repository (no configuration needed)
repo-ctx repo index /path/to/your/project

# Index a public GitHub repository
repo-ctx repo index fastapi/fastapi

# Search across indexed repositories
repo-ctx repo search "authentication"

# Get documentation
repo-ctx repo docs /fastapi/fastapi

# Analyze code structure
repo-ctx code analyze ./src
```

For detailed instructions, see the **[User Guide](docs/USER_GUIDE.md)**.

---

## Installation

### From PyPI

```bash
pip install repo-ctx
```

### Using uvx (no install needed)

```bash
uvx repo-ctx --help
```

### From Source

```bash
git clone https://github.com/anthropics/repo-ctx.git
cd repo-ctx
pip install -e .
```

---

## Configuration

**No configuration required** for:
- Local Git repositories
- Public GitHub repositories (rate-limited to 60 req/hour)

**Optional configuration** for:
- GitHub private repos or higher rate limits: set `GITHUB_TOKEN`
- GitLab access: set `GITLAB_URL` and `GITLAB_TOKEN`

```bash
export GITHUB_TOKEN="ghp_your_token"
export GITLAB_URL="https://gitlab.company.com"
export GITLAB_TOKEN="glpat-your_token"
```

See the [User Guide](docs/USER_GUIDE.md#configuration) for complete configuration options.

---

## Usage

### CLI

```bash
# Repository commands
repo-ctx repo index <path>       # Index a repository
repo-ctx repo search <query>     # Search repositories
repo-ctx repo list               # List indexed repositories
repo-ctx repo docs <library_id>  # Get documentation

# Code analysis commands
repo-ctx code analyze <path>     # Analyze code structure
repo-ctx code find <path> <query> # Search for symbols
repo-ctx code info <path> <name> # Get symbol details
repo-ctx code dep <path>         # Generate dependency graph

# Interactive mode
repo-ctx -i

# Output formats: text (default), json, yaml
repo-ctx -o json repo list
```

### MCP Server (for AI Assistants)

Add to your MCP configuration (e.g., `~/.config/claude/mcp.json`):

```json
{
  "mcpServers": {
    "repo-ctx": {
      "command": "uvx",
      "args": ["repo-ctx", "-m"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

See the [MCP Tools Reference](docs/mcp_tools_reference.md) for available tools and examples.

### Python Library

```python
import asyncio
from repo_ctx import Config, RepositoryContext, CodeAnalyzer

async def main():
    config = Config.from_env()
    context = RepositoryContext(config)
    await context.init()

    # Index and search
    await context.index_repository("fastapi", "fastapi", provider_type="github")
    results = await context.fuzzy_search_libraries("fastapi")
    docs = await context.get_documentation("/fastapi/fastapi")

asyncio.run(main())

# Code analysis
analyzer = CodeAnalyzer()
symbols = analyzer.analyze_file(code, "service.py")
```

See the [API Reference](docs/library/api-reference.md) for complete documentation.

---

## MCP Tools Overview

repo-ctx provides **12 MCP tools** for AI assistant integration:

| Category | Tools |
|----------|-------|
| **Repository** | `repo-ctx-index`, `repo-ctx-search`, `repo-ctx-list`, `repo-ctx-docs` |
| **Code Analysis** | `repo-ctx-analyze`, `repo-ctx-find-symbol`, `repo-ctx-dependency-graph` |

```javascript
// Example: Index and search
await mcp.call("repo-ctx-index", { repository: "fastapi/fastapi" });
await mcp.call("repo-ctx-search", { query: "authentication" });
await mcp.call("repo-ctx-docs", { libraryId: "/fastapi/fastapi" });
```

---

## Documentation

| Document | Description |
|----------|-------------|
| **[User Guide](docs/USER_GUIDE.md)** | Complete guide with use cases and examples |
| [MCP Tools Reference](docs/mcp_tools_reference.md) | Detailed MCP tool documentation |
| [Multi-Provider Guide](docs/multi-provider-guide.md) | GitHub, GitLab, local provider setup |
| [API Reference](docs/library/api-reference.md) | Python library documentation |
| [Architecture](docs/library/architecture.md) | Internal design and components |

---

## Supported Languages

Code analysis supports:
- **Python** - Classes, functions, methods, decorators
- **JavaScript** - ES6 classes, functions, arrow functions
- **TypeScript** - Classes, interfaces, types, enums
- **Java** - Classes, interfaces, methods, enums
- **Kotlin** - Classes, objects, functions, data classes

---

## Requirements

- Python 3.10+
- Git (for local repository indexing)

**Optional:**
- GitHub token (for private repos or higher rate limits)
- GitLab URL and token (for GitLab access)

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Development setup
git clone https://github.com/anthropics/repo-ctx.git
cd repo-ctx
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint and format
ruff check repo_ctx/
ruff format repo_ctx/
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
