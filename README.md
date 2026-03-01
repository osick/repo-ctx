# repo-ctx

[![PyPI](https://img.shields.io/pypi/v/repo-ctx)](https://pypi.org/project/repo-ctx/)
[![Python](https://img.shields.io/pypi/pyversions/repo-ctx)](https://pypi.org/project/repo-ctx/)
[![License](https://img.shields.io/github/license/osick/repo-ctx)](LICENSE)

## ***Give your AI assistant deep understanding of any codebase.***

Your AI assistant can only help with code it can see. repo-ctx gives it searchable access to any Git repository — with real symbol extraction, dependency graphs, and architecture analysis across 12+ languages. Set up in one command.

---

## The Problem

AI coding assistants are powerful — but blind. They only know what's in the current file or what you paste in. When you need help understanding a dependency, navigating an unfamiliar codebase, or analyzing architecture across repositories, you're on your own.

**repo-ctx solves this.** It indexes Git repositories and exposes them to AI assistants through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/), giving tools like Claude Code, Cursor, and VS Code Copilot real, structured access to codebases.

---

## What Makes repo-ctx Different

### 1. Built for AI Assistants

repo-ctx isn't a code browser you query manually. It's an MCP server — your AI assistant calls its tools directly when it needs to understand code.

```
You: "How does the authentication flow work in our API?"

Claude (using repo-ctx):
  → ctx-search "authentication" across 3 indexed repos
  → ctx-analyze auth_service.py → extracts 12 symbols, 4 dependencies
  → ctx-graph ./src/auth → maps the full dependency chain
  → Gives you a complete, accurate answer
```

### 2. Multi-Repo, Multi-Provider

Index everything in one place. GitHub, GitLab, and local repositories — search across all of them.

```bash
repo-ctx index ./my-project              # Local repo
repo-ctx index fastapi/fastapi           # GitHub
repo-ctx index my-company/backend        # GitLab
repo-ctx index --group my-org            # Entire GitHub org
```

Then your AI assistant can search, analyze, and cross-reference all of them simultaneously.

### 3. Deep Code Understanding

Not just text search — real structural analysis:

- **Symbol extraction** — functions, classes, methods, interfaces across Python, Java, JavaScript, TypeScript, Kotlin, Go, Rust, C/C++, Ruby, PHP, C#, Bash
- **Dependency graphs** — who calls what, import chains, coupling analysis
- **Architecture analysis** — Design Structure Matrix, cycle detection, layer identification, complexity metrics
- **Joern CPG** — optional deep analysis with call graphs, data flow tracking, and CPGQL queries

---

## Quick Start

```bash
# Install
pip install repo-ctx

# Index a repository
repo-ctx index fastapi/fastapi

# Search it
repo-ctx search "middleware"

# Analyze code locally
repo-ctx analyze ./src --language python
```

---

## MCP Setup

Add to your MCP configuration (`~/.config/claude/mcp.json` for Claude Code):

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

Works immediately with local and public GitHub repos — no tokens required for those.

For private repos: set `GITHUB_TOKEN` or `GITLAB_TOKEN` + `GITLAB_URL`.

### 18 MCP Tools

| Category | Tools |
|----------|-------|
| **Repository** | `ctx-index`, `ctx-list`, `ctx-search`, `ctx-docs` |
| **Code Analysis** | `ctx-analyze`, `ctx-symbol`, `ctx-symbols`, `ctx-graph` |
| **Architecture** | `ctx-dsm`, `ctx-cycles`, `ctx-layers`, `ctx-architecture`, `ctx-metrics` |
| **Export** | `ctx-llmstxt`, `ctx-dump` |
| **CPG (Joern)** | `ctx-query`, `ctx-export`, `ctx-status` |

Full reference: [MCP Tools Reference](docs/mcp_tools_reference.md)

---

## Also Works As

**CLI** — standalone searching, indexing, and analysis from the terminal.

**Python library** — embed repo-ctx in your own tools and workflows.

```python
from repo_ctx.client import RepoCtxClient

async with RepoCtxClient() as client:
    await client.index_repository("fastapi/fastapi", provider="github")
    results = await client.search("middleware")
```

---

## Documentation

- [User Guide](docs/user_guide.md) — usage, examples, configuration
- [Developer Guide](docs/dev_guide.md) — architecture, contributing
- [MCP Tools Reference](docs/mcp_tools_reference.md) — all 18 tools documented
- [Architecture Analysis Guide](docs/architecture_analysis_guide.md) — DSM, cycles, metrics

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
