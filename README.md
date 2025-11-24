# Repository Context (`repo-ctx`)

A flexible Git repository documentation indexer and search tool with multiple interfaces:
- **MCP Server** for LLM integration (primary use case)
- **CLI** for standalone searching
- **Python library** for custom integrations

Supports **GitLab** and **GitHub** repositories (including Enterprise versions) with auto-detection and explicit provider selection.

## Features

- **Multi-provider support** - Index from GitLab and GitHub simultaneously
- Search repositories by name with fuzzy matching
- Retrieve documentation with topic filtering
- Support for multiple versions (tags/branches)
- Configurable via `git_context.json` in repositories
- SQLite storage for fast local access
- MCP protocol for seamless LLM integration
- Works with Claude Code, Kiro CLI, GitHub Copilot, and other AI tools
- Use as a Python library in your own tools
- Auto-detect provider from repository path format

## Installation

### From PyPI (Recommended)

```bash
uvx repo-ctx
```

### From Source

```bash
cd repo-ctx
uv pip install -e .
```

## Configuration

repo-ctx supports GitLab and GitHub (including Enterprise versions). Configure one or both providers using:

1. **Command-line arguments** (`--gitlab-url`, `--gitlab-token`, `--github-token`)
2. **Specified config file** (`--config /path/to/config.yaml`)
3. **Environment variables** (`GITLAB_URL`, `GITLAB_TOKEN`, `GITHUB_TOKEN`)
4. **Standard config locations**:
   - `~/.config/repo-ctx/config.yaml`
   - `~/.repo-ctx/config.yaml`
   - `./config.yaml` (current directory)

**📚 Complete Guide:** See [Multi-Provider Support Guide](docs/multi-provider-guide.md) for detailed configuration options, examples, and troubleshooting.

### Quick Start: GitLab Only

```bash
export GITLAB_URL="https://gitlab.company.internal"
export GITLAB_TOKEN="glpat-your-token-here"

uvx repo-ctx --index group/project
```

### Quick Start: GitHub Only

```bash
# Public repos (no token needed, subject to 60/hr rate limit)
uvx repo-ctx --index owner/repo

# Private repos or higher rate limits (5000/hr)
export GITHUB_TOKEN="ghp-your-token-here"
uvx repo-ctx --index owner/repo
```

### Quick Start: Both Providers

```bash
export GITLAB_URL="https://gitlab.company.com"
export GITLAB_TOKEN="glpat-xxx"
export GITHUB_TOKEN="ghp-xxx"

# Auto-detect provider from path format
uvx repo-ctx --index owner/repo              # → GitHub (2 parts)
uvx repo-ctx --index group/subgroup/project  # → GitLab (3+ parts)

# Or explicitly specify provider
uvx repo-ctx --index owner/repo --provider github
uvx repo-ctx --index group/project --provider gitlab
```

### Config File (Both Providers)

Create `~/.config/repo-ctx/config.yaml`:

```yaml
gitlab:
  url: "https://gitlab.company.internal"
  token: "${GITLAB_TOKEN}"

github:
  url: "https://api.github.com"  # Optional, defaults to public GitHub
  token: "${GITHUB_TOKEN}"        # Optional for public repos

storage:
  path: "~/.repo-ctx/context.db"
```


## Usage

### As a Python Library

repo-ctx can be imported and used as a library in your own applications:

```python
import asyncio
from repo_ctx.config import Config
from repo_ctx.core import RepositoryContext

async def main():
    # Initialize with both providers
    config = Config.from_env()
    context = RepositoryContext(config)
    await context.init()

    # Index from GitLab
    await context.index_repository("mygroup", "myproject", provider_type="gitlab")

    # Index from GitHub
    await context.index_repository("fastapi", "fastapi", provider_type="github")

    # Search across all indexed repos
    results = await context.fuzzy_search_libraries("fastapi", limit=5)
    for result in results:
        print(f"{result.name} (score: {result.score})")

    # Get documentation (works for any indexed repo)
    docs = await context.get_documentation("/fastapi/fastapi")
    print(docs["content"][0]["text"])

asyncio.run(main())
```

**Note:** `RepositoryContext` is the new multi-provider class. `GitLabContext` is still available as a backward-compatible alias.

**📚 Library Documentation:**
- [Quickstart Guide](docs/library/quickstart.md) - Get started in 5 minutes
- [API Reference](docs/library/api-reference.md) - Complete API documentation
- [Examples](docs/library/examples.md) - Real-world usage examples
- [Architecture](docs/library/architecture.md) - How it works internally

### CLI Usage

#### Search for Repositories

```bash
# Fuzzy search (typo-tolerant)
uv run repo-ctx search "fastapi"

# Limit results
uv run repo-ctx search "python" --limit 5

# Search within specific repo
uv run repo-ctx search "api" --repo mygroup
```

#### List Indexed Repositories

```bash
# Detailed view (shows last indexed date)
uv run repo-ctx list

# Simple view (names only)
uv run repo-ctx list --format simple
```

**Example output:**
```
Indexed Repositories (3):

1. mygroup/fastapi-project
   Description: FastAPI microservice for user authentication
   Default version: main
   Last indexed: 2025-11-23 14:30:00 (2 hours ago)

2. backend/api-server
   Description: Main API server
   Default version: main
   Last indexed: 2025-11-22 09:15:00 (1 day ago)
```

#### Get Documentation

```bash
# Get all documentation
uv run repo-ctx docs mygroup/project

# Filter by topic
uv run repo-ctx docs mygroup/project --topic api

# Get specific version
uv run repo-ctx docs mygroup/project/v1.0.0

# Pagination
uv run repo-ctx docs mygroup/project --page 2
```

#### Index a Repository

**GitLab:**
```bash
export GITLAB_URL="https://gitlab.company.internal"
export GITLAB_TOKEN="your_token"
uvx repo-ctx --index group/project
```

**GitHub:**
```bash
export GITHUB_TOKEN="ghp-your-token"
uvx repo-ctx --index owner/repo

# Or with explicit provider
uvx repo-ctx --index owner/repo --provider github
```

**With command-line arguments:**
```bash
# GitLab
uvx repo-ctx \
  --gitlab-url https://gitlab.company.internal \
  --gitlab-token glpat-your-token \
  --index group/subgroup/repository

# GitHub
uvx repo-ctx \
  --github-token ghp-your-token \
  --index owner/repo \
  --provider github
```

**From source:**
```bash
uv run repo-ctx --index group/subgroup/repository --provider gitlab
uv run repo-ctx --index owner/repo --provider github
```

**📚 More examples:** See [Multi-Provider Guide](docs/multi-provider-guide.md) for GitHub Enterprise, both providers simultaneously, and advanced usage.

### Run as MCP Server

#### With Claude Code / MCP Clients

**Option 1: Using uvx with environment variables (Simplest)**

Add to MCP settings (e.g., `~/.config/claude/mcp.json`):

```json
{
  "mcpServers": {
    "repo-ctx": {
      "command": "uvx",
      "args": ["repo-ctx"],
      "env": {
        "GITLAB_URL": "https://gitlab.company.internal",
        "GITLAB_TOKEN": "${GITLAB_TOKEN}",
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

**Note:** Configure one or both providers. The example above shows both GitLab and GitHub configured.

**Option 2: Using uvx with config file**

```json
{
  "mcpServers": {
    "repo-ctx": {
      "command": "uvx",
      "args": [
        "repo-ctx",
        "--config",
        "/home/user/.config/repo-ctx/config.yaml"
      ]
    }
  }
}
```

**Option 3: From source (for development)**

```json
{
  "mcpServers": {
    "repo-ctx": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/repo-ctx",
        "run",
        "repo-ctx"
      ],
      "env": {
        "GITLAB_URL": "https://gitlab.company.internal",
        "GITLAB_TOKEN": "${GITLAB_TOKEN}"
      }
    }
  }
}
```

#### With Kiro CLI

Add to `~/.config/kiro/mcp.json`:

```json
{
  "mcpServers": {
    "repo-ctx": {
      "command": "uvx",
      "args": ["repo-ctx"],
      "env": {
        "GITLAB_URL": "https://gitlab.company.internal",
        "GITLAB_TOKEN": "${GITLAB_TOKEN}"
      }
    }
  }
}
```

Then use:
```bash
kiro-cli chat
```

Ask questions like:
- "Search for python in GitLab"
- "Fuzzy search for fastmcp"
- "Get GitLab docs for /group1/subgroup1/repo1"
- "Show me documentation about vector search from GitLab repo group/subgroup/repository"

#### With GitHub Copilot (VS Code)

Add to `.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "repo-ctx": {
      "command": "uvx",
      "args": ["repo-ctx"],
      "env": {
        "GITLAB_URL": "https://gitlab.company.internal",
        "GITLAB_TOKEN": "${GITLAB_TOKEN}"
      }
    }
  }
}
```

## Repository Configuration

Add a `git_context.json` file to your repository root to customize indexing:

```json
{
  "projectTitle": "API Documentation",
  "description": "Internal API documentation and guides",
  "folders": ["docs", "guides"],
  "excludeFolders": ["node_modules", "dist"],
  "excludeFiles": ["CHANGELOG.md"]
}
```

## MCP Tools

### gitlab-search-libraries
Search for GitLab libraries/projects by name (exact match).

**Input:** `libraryName` (string)  
**Output:** List of matching libraries with IDs and versions

### gitlab-fuzzy-search
Fuzzy search for GitLab repositories. Returns top matches even with typos or partial names.

**Input:**
- `query` (string): Search term (can be partial or fuzzy)
- `limit` (integer, optional): Max results (default: 10)

**Output:** Ranked list of repositories with match scores

**Example:** Search "blueprint" finds "blueprint-for-skivi", "api-blueprint", etc.

### gitlab-index-repository
Index a GitLab repository to make its documentation searchable.

**Input:** `repository` (string): Format `group/project` or `group/subgroup/project`  
**Output:** Success/error message

**Example:** Index "mygroup/blueprint"

### gitlab-index-group
Index all repositories in a GitLab group (including subgroups).

**Input:**
- `group` (string): Group path (e.g., "groupname")
- `includeSubgroups` (boolean, optional): Include subgroups (default: true)

**Output:** Summary of indexed repositories

**Example:** Index entire "mygroup" group with all subgroups and repos

### gitlab-get-docs
Retrieve documentation for a specific library.

**Input:**
- `libraryId` (string): Format `/group/project` or `/group/project/version`
- `topic` (string, optional): Filter by topic
- `page` (integer, optional): Page number (default: 1)

**Output:** Formatted documentation content

## Architecture

```
┌──────────────┐         ┌─────────────────┐         ┌──────────────┐
│   LLM/AI     │◄───────►│  Git Context    │◄───────►│   GitLab     │
│   Client     │   MCP   │     Server      │   API   │   Server     │
└──────────────┘         └─────────────────┘         └──────────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  SQLite DB      │
                         └─────────────────┘
```

## Troubleshooting

**Configuration not found?**
- Set environment variables: `export GITLAB_URL=... GITLAB_TOKEN=...`
- Or create config file at: `~/.config/repo-ctx/config.yaml`
- Or use CLI args: `--gitlab-url --gitlab-token`
- Run `repo-ctx --help` to see all options

**Server not starting?**
- Check configuration is valid (try `repo-ctx --help`)
- Verify GITLAB_TOKEN is set or provided via config
- Ensure GITLAB_URL is accessible
- For uvx: Make sure environment variables are set in MCP config

**No results when searching?**
- Index the repository first: `uvx repo-ctx --index group/project`
- Check database exists: `ls ~/.repo-ctx/context.db`
- Verify you have access to the GitLab project

**GitLab connection errors?**
- Verify token has `read_api` scope
- Check GitLab URL is accessible
- Ensure token hasn't expired
- Test connection: `curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" $GITLAB_URL/api/v4/user`

## Development

### Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details on:
- Development setup
- Running tests
- Code style guidelines
- Pull request process

### Automated Releases

This project uses GitHub Actions for automated releases:

- **Tests** run on every PR and push to main
- **Publishing** is automated when version tags are pushed
- **GitHub Releases** are created automatically with changelogs
- **Issue labeling** happens automatically for referenced issues

See [docs/GITHUB_ACTIONS.md](docs/GITHUB_ACTIONS.md) for complete CI/CD documentation.

### Quick Release

```bash
# Update version in pyproject.toml, then:
git add pyproject.toml
git commit -m "Bump version to 0.1.2"
git tag v0.1.2
git push origin main && git push origin v0.1.2
```

GitHub Actions will automatically build, test, and publish to PyPI.

See [docs/RELEASE_GUIDE.md](docs/RELEASE_GUIDE.md) for detailed release instructions.

## Requirements

- Python 3.10+
- uv package manager
- GitLab server with API access
- Personal access token with `read_api` scope

