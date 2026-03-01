# Configuration Guide

This guide covers all configuration options for repo-ctx across its three interfaces: CLI, MCP Server, and REST API.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration Sources](#configuration-sources)
3. [Environment Variables](#environment-variables)
4. [Configuration File](#configuration-file)
5. [CLI Configuration](#cli-configuration)
6. [MCP Server Configuration](#mcp-server-configuration)
7. [API Server Configuration](#api-server-configuration)
8. [Storage Configuration](#storage-configuration)
9. [GenAI/LLM Configuration](#genaillm-configuration)
10. [Advanced Configuration](#advanced-configuration)

---

## Quick Start

### Zero Configuration (Local + Public GitHub)

repo-ctx works out of the box for:
- Local Git repositories
- Public GitHub repositories (with rate limits)

```bash
# No configuration needed
repo-ctx index ./my-local-project
repo-ctx index facebook/react
```

### Minimal Configuration (Private Repos)

```bash
# GitHub private repos
export GITHUB_TOKEN="ghp_your_token"

# GitLab access
export GITLAB_URL="https://gitlab.company.com"
export GITLAB_TOKEN="glpat-your_token"
```

---

## Configuration Sources

repo-ctx loads configuration from multiple sources with the following priority (highest first):

1. **CLI arguments** - Direct command-line options
2. **Environment variables** - `GITHUB_TOKEN`, `GITLAB_URL`, etc.
3. **Config file (explicit)** - Specified via `--config` flag
4. **Config file (auto-discovered)** - Found in standard locations:
   - `./config.yaml` (current directory)
   - `~/.config/repo-ctx/config.yaml`
   - `~/.repo-ctx/config.yaml`

---

## Environment Variables

### Git Providers

| Variable | Description | Default |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub personal access token | None (public repos only) |
| `GITHUB_URL` | GitHub API URL | `https://api.github.com` |
| `GITLAB_TOKEN` | GitLab personal access token | None (required for GitLab) |
| `GITLAB_URL` | GitLab server URL | None (required for GitLab) |

Alternative prefix `GIT_CONTEXT_*` is also supported:
- `GIT_CONTEXT_GITHUB_TOKEN`
- `GIT_CONTEXT_GITLAB_URL`

### Storage

| Variable | Description | Default |
|----------|-------------|---------|
| `STORAGE_PATH` | SQLite database path | `~/.repo-ctx/context.db` |
| `GIT_CONTEXT_STORAGE_PATH` | Alternative name | Same as above |

### Vector Database (Qdrant)

| Variable | Description | Default |
|----------|-------------|---------|
| `QDRANT_URL` | Qdrant server URL | `:memory:` (in-memory) |
| `QDRANT_API_KEY` | Qdrant Cloud API key | None |
| `QDRANT_COLLECTION_PREFIX` | Collection name prefix | `repo_ctx` |

### Graph Database (Neo4j)

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `NEO4J_USERNAME` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | None |
| `NEO4J_DATABASE` | Database name | `neo4j` |
| `NEO4J_IN_MEMORY` | Use NetworkX backend | `true` |

### GenAI/LLM

| Variable | Description | Default |
|----------|-------------|---------|
| `GENAI_ENABLED` | Enable LLM features | `false` |
| `GENAI_MODEL` | LLM model name | `gpt-5-mini` |
| `GENAI_EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `GENAI_API_KEY` | LLM provider API key | None |
| `GENAI_BASE_URL` | Custom API base URL | None |

### API Server

| Variable | Description | Default |
|----------|-------------|---------|
| `REPO_CTX_API_KEY` | API authentication key | None (no auth) |
| `REPO_CTX_REQUIRE_AUTH` | Require auth for all requests | `false` |

---

## Configuration File

### YAML Format

Create `~/.config/repo-ctx/config.yaml`:

```yaml
# Git Providers
github:
  url: "https://api.github.com"  # Optional
  token: "${GITHUB_TOKEN}"       # Uses env var

gitlab:
  url: "https://gitlab.company.com"
  token: "${GITLAB_TOKEN}"

# Storage
storage:
  path: "~/.repo-ctx/context.db"

  # Vector database (optional)
  qdrant:
    url: ":memory:"              # In-memory, or "http://localhost:6333"
    api_key: "${QDRANT_API_KEY}" # For Qdrant Cloud
    collection_prefix: "repo_ctx"

  # Graph database (optional)
  neo4j:
    uri: "bolt://localhost:7687"
    username: "neo4j"
    password: "${NEO4J_PASSWORD}"
    database: "neo4j"
    in_memory: true              # Use NetworkX instead of Neo4j

# GenAI/LLM (optional)
genai:
  enabled: true
  model: "gpt-5-mini"           # Or "claude-3-haiku-20240307", "ollama/llama3"
  embedding_model: "text-embedding-3-small"
  api_key: "${OPENAI_API_KEY}"
  base_url: null                 # Custom API endpoint
```

### Environment Variable Substitution

The config file supports `${VAR_NAME}` syntax for environment variables:

```yaml
gitlab:
  token: "${GITLAB_TOKEN}"  # Replaced with actual value at load time
```

---

## CLI Configuration

### Global Options

```bash
repo-ctx [global-options] <command> [command-options]
```

| Option | Description |
|--------|-------------|
| `-c, --config PATH` | Config file path |
| `-p, --provider {auto,github,gitlab,local}` | Override provider detection |
| `-o, --output {text,json,yaml}` | Output format |
| `-v, --verbose` | Verbose output |
| `--version, -V` | Show version |

### Examples

```bash
# Use specific config file
repo-ctx -c ~/my-config.yaml index owner/repo

# Force provider
repo-ctx -p github index owner/repo
repo-ctx -p local index ./my-project

# JSON output for scripting
repo-ctx -o json list
repo-ctx -o json search "fastapi" | jq '.results[].name'

# Verbose mode
repo-ctx -v analyze ./src
```

### Interactive Mode

```bash
repo-ctx -i
# or
repo-ctx --interactive
```

Launches an interactive command palette with:
- Command auto-completion
- Fuzzy search for repositories
- Rich formatted output

### MCP Server Mode

```bash
repo-ctx -m
# or
repo-ctx --mcp
```

Starts the MCP server for AI assistant integration.

---

## MCP Server Configuration

### Starting the Server

```bash
# Default (uses environment/config file)
repo-ctx --mcp

# With explicit config
repo-ctx --mcp --config ~/my-config.yaml
```

### Claude Desktop Integration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or equivalent:

```json
{
  "mcpServers": {
    "repo-ctx": {
      "command": "uvx",
      "args": ["repo-ctx", "--mcp"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token",
        "GITLAB_URL": "https://gitlab.company.com",
        "GITLAB_TOKEN": "glpat-your_token"
      }
    }
  }
}
```

### With Custom Config File

```json
{
  "mcpServers": {
    "repo-ctx": {
      "command": "uvx",
      "args": ["repo-ctx", "--mcp", "--config", "/path/to/config.yaml"]
    }
  }
}
```

### Available MCP Tools

The MCP server exposes these tool categories:

| Category | Tools | Description |
|----------|-------|-------------|
| Repository | `ctx-index`, `ctx-list`, `ctx-search`, `ctx-docs` | Index, search, retrieve docs |
| Code Analysis | `ctx-analyze`, `ctx-symbol`, `ctx-symbols`, `ctx-graph` | Symbols, dependencies |
| Architecture | `ctx-dsm`, `ctx-cycles`, `ctx-layers`, `ctx-architecture`, `ctx-metrics` | Structure analysis |
| Export | `ctx-llmstxt`, `ctx-dump` | Compact summaries, full export |
| CPG (Joern) | `ctx-query`, `ctx-export`, `ctx-status` | Advanced code analysis |

---

## API Server Configuration

### Starting the Server

```bash
# Development server
uvicorn repo_ctx.api:app --reload --port 8000

# Production server
uvicorn repo_ctx.api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Authentication

By default, the API allows unauthenticated access from localhost.

**Enable API Key Authentication:**

```bash
# Generate a key
export REPO_CTX_API_KEY=$(openssl rand -hex 32)

# Require auth for all requests (including localhost)
export REPO_CTX_REQUIRE_AUTH=true
```

**Using the API Key:**

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/repositories
```

### Rate Limiting

Default rate limits (configurable in code):
- 100 requests per 60-second window
- Applied per client IP
- Disabled for localhost by default

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /api/v1/info` | Server info and capabilities |
| `GET /api/v1/repositories` | List indexed repositories |
| `POST /api/v1/index` | Index a repository |
| `GET /api/v1/search` | Search repositories |
| `GET /api/v1/docs/{group}/{project}` | Get documentation |
| `POST /api/v1/analyze` | Analyze code |

Full OpenAPI documentation available at `/docs` when server is running.

---

## Storage Configuration

### SQLite (Content Database)

The main content database stores:
- Repository metadata
- Document content
- Symbol information

```bash
# Default location
~/.repo-ctx/context.db

# Custom location
export STORAGE_PATH=/path/to/database.db
```

### Qdrant (Vector Database)

For semantic search capabilities:

```bash
# In-memory (default, data lost on restart)
export QDRANT_URL=":memory:"

# Local Qdrant server
export QDRANT_URL="http://localhost:6333"

# Qdrant Cloud
export QDRANT_URL="https://xyz.qdrant.io:6333"
export QDRANT_API_KEY="your-cloud-api-key"
```

### Neo4j (Graph Database)

For advanced dependency analysis:

```bash
# In-memory NetworkX backend (default)
export NEO4J_IN_MEMORY=true

# Local Neo4j server
export NEO4J_IN_MEMORY=false
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_PASSWORD="your-password"
```

---

## GenAI/LLM Configuration

repo-ctx uses [litellm](https://docs.litellm.ai/) for multi-provider LLM support.

### Enable LLM Features

```bash
export GENAI_ENABLED=true
export GENAI_API_KEY="your-api-key"
```

### Supported Providers

```bash
# OpenAI (default)
export GENAI_MODEL="gpt-5-mini"
export GENAI_API_KEY="sk-..."

# Anthropic
export GENAI_MODEL="claude-3-haiku-20240307"
export GENAI_API_KEY="sk-ant-..."

# Azure OpenAI
export GENAI_MODEL="azure/gpt-4"
export AZURE_API_KEY="..."
export AZURE_API_BASE="https://your-resource.openai.azure.com"

# Local Ollama
export GENAI_MODEL="ollama/llama3"
export GENAI_BASE_URL="http://localhost:11434"

# AWS Bedrock
export GENAI_MODEL="bedrock/anthropic.claude-3-sonnet"
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
```

### LLM Features

When enabled, LLM provides:
- Code summarization
- Documentation enhancement
- Symbol classification
- Quality suggestions

Without LLM, these features fall back to heuristic-based analysis.

---

## Advanced Configuration

### Multiple Environments

Create environment-specific config files:

```bash
# Development
repo-ctx -c config.dev.yaml index owner/repo

# Production
repo-ctx -c config.prod.yaml index owner/repo
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

RUN pip install repo-ctx

ENV GITHUB_TOKEN=""
ENV STORAGE_PATH="/data/context.db"

VOLUME /data

CMD ["repo-ctx", "--mcp"]
```

```bash
docker run -e GITHUB_TOKEN=ghp_xxx -v repo-ctx-data:/data repo-ctx
```

### Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: repo-ctx-config
data:
  config.yaml: |
    github:
      token: "${GITHUB_TOKEN}"
    storage:
      path: "/data/context.db"
```

### Logging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Or in Python
import logging
logging.getLogger("repo_ctx").setLevel(logging.DEBUG)
```

---

## Troubleshooting

### Common Issues

**"No provider configured"**
```bash
# Solution: Set at least one provider
export GITHUB_TOKEN="ghp_xxx"
# or
export GITLAB_URL="..." && export GITLAB_TOKEN="..."
```

**"Rate limit exceeded" (GitHub)**
```bash
# Solution: Use authenticated requests
export GITHUB_TOKEN="ghp_xxx"
```

**"Joern not found"**
```bash
# Solution: Install Joern and add to PATH
export PATH="$HOME/bin/joern:$PATH"
repo-ctx status  # Verify installation
```

### Verify Configuration

```bash
# Show current configuration and capabilities
repo-ctx status

# Test specific provider
repo-ctx -p github list
repo-ctx -p gitlab list
repo-ctx -p local index ./
```

---

## See Also

- [User Guide](user_guide.md) - Usage examples
- [API Reference](library/api-reference.md) - Python library
- [Developer Guide](dev_guide.md) - Contributing
