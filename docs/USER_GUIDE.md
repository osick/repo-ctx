# repo-ctx User Guide

**repo-ctx** is a repository documentation indexer and code analyzer designed to provide context to AI assistants and developers. It indexes documentation from Git repositories (local, GitHub, GitLab) and analyzes source code to extract symbols, dependencies, and structure.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Concepts](#core-concepts)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Use Cases](#use-cases)
6. [CLI Reference](#cli-reference)
7. [MCP Server Integration](#mcp-server-integration)
8. [Python Library API](#python-library-api)
9. [Troubleshooting](#troubleshooting)

---

## Getting Started

### What repo-ctx Does

repo-ctx solves a common problem: AI assistants and developers need quick access to documentation and code structure from multiple repositories. Instead of manually copying documentation or navigating codebases, repo-ctx:

1. **Indexes** repositories once (documentation and code)
2. **Searches** across all indexed repositories with fuzzy matching
3. **Retrieves** relevant documentation and code analysis on demand
4. **Integrates** seamlessly with AI tools via the MCP protocol

### Quick Start (5 minutes)

```bash
# Install
pip install repo-ctx

# Index a local repository (no configuration needed)
repo-ctx repo index /path/to/your/project

# Index a public GitHub repository (no token needed)
repo-ctx repo index fastapi/fastapi

# Search across indexed repositories
repo-ctx repo search "authentication"

# Get documentation
repo-ctx repo docs /fastapi/fastapi

# Analyze code structure
repo-ctx code analyze ./src
```

---

## Core Concepts

### Providers

repo-ctx supports three Git providers:

| Provider | Path Format | Authentication |
|----------|-------------|----------------|
| **Local** | `/path/to/repo`, `./repo`, `~/repo` | None required |
| **GitHub** | `owner/repo` | Optional for public repos |
| **GitLab** | `group/project` or `group/subgroup/project` | Required (URL + token) |

The provider is auto-detected from the path format, or you can specify it explicitly with `--provider`.

### Library IDs

After indexing, repositories are identified by a **Library ID**:

```
/owner/repo           # GitHub or local
/group/project        # GitLab
/group/subgroup/proj  # GitLab with subgroups
```

Use Library IDs to retrieve documentation and search results.

### Versions

Each repository can have multiple indexed versions:
- Default branch (main/master)
- Tags (v1.0.0, v2.0.0, etc.)
- Specific branches

Reference specific versions: `/owner/repo/v1.0.0`

### Symbols

Code analysis extracts **symbols** from source code:

| Symbol Type | Description | Languages |
|-------------|-------------|-----------|
| `class` | Class definitions | All |
| `function` | Standalone functions | All |
| `method` | Class methods | All |
| `interface` | Interface definitions | TypeScript, Java, Kotlin |
| `enum` | Enumeration types | Python, TypeScript, Java, Kotlin |

Supported languages: **Python, JavaScript, TypeScript, Java, Kotlin**

---

## Installation

### From PyPI (Recommended)

```bash
pip install repo-ctx
```

Or use `uvx` for one-time execution:
```bash
uvx repo-ctx --help
```

### From Source

```bash
git clone https://github.com/osick/repo-ctx.git
cd repo-ctx
pip install -e .
```

### Verify Installation

```bash
repo-ctx --version
```

---

## Configuration

### No Configuration Required

For basic usage, no configuration is needed:
- **Local repositories**: Work immediately
- **GitHub public repositories**: Work with rate limits (60 requests/hour)

### Environment Variables

For full functionality, set these environment variables:

```bash
# GitHub (increases rate limit to 5000/hour, enables private repos)
export GITHUB_TOKEN="ghp_your_token_here"

# GitLab (required for GitLab access)
export GITLAB_URL="https://gitlab.company.com"
export GITLAB_TOKEN="glpat-your_token_here"

# Optional: Custom storage location
export STORAGE_PATH="~/.repo-ctx/context.db"
```

### Config File

Create `~/.config/repo-ctx/config.yaml`:

```yaml
github:
  token: "${GITHUB_TOKEN}"

gitlab:
  url: "https://gitlab.company.com"
  token: "${GITLAB_TOKEN}"

storage:
  path: "~/.repo-ctx/context.db"
```

### Configuration Priority

1. Command-line arguments (highest)
2. Environment variables
3. Config file
4. Defaults (lowest)

---

## Use Cases

### Use Case 1: AI Assistant Context

Provide your AI assistant with documentation from your codebase:

```bash
# 1. Index your project
repo-ctx repo index /path/to/myproject

# 2. Configure MCP server (see MCP section below)

# 3. In Claude Code or similar, ask:
#    "Search repo-ctx for authentication documentation"
#    "Get documentation from /myproject about API endpoints"
```

### Use Case 2: Multi-Repository Documentation Search

Search across multiple indexed repositories:

```bash
# Index several repositories
repo-ctx repo index fastapi/fastapi
repo-ctx repo index pallets/flask
repo-ctx repo index django/django

# Search across all
repo-ctx repo search "middleware"

# Get specific documentation
repo-ctx repo docs /fastapi/fastapi --topic middleware
```

### Use Case 3: Code Structure Analysis

Understand unfamiliar codebases:

```bash
# Analyze code structure
repo-ctx code analyze ./src

# Find specific symbols
repo-ctx code find ./src "UserService"

# Get detailed symbol information
repo-ctx code info ./src "UserService.create_user"

# List all symbols in a file
repo-ctx code symbols ./src/services/user.py

# Generate dependency graph
repo-ctx code dep ./src --type class --format dot > class_diagram.dot
```

### Use Case 4: Organization-Wide Indexing

Index all repositories in an organization:

```bash
# GitHub organization
repo-ctx repo index-group microsoft --provider github

# GitLab group with subgroups
repo-ctx repo index-group mycompany --provider gitlab

# List what's indexed
repo-ctx repo list
```

### Use Case 5: Version-Specific Documentation

Access documentation from specific versions:

```bash
# Index specific version
repo-ctx repo index fastapi/fastapi

# Get documentation from a tag
repo-ctx repo docs /fastapi/fastapi/v0.109.0

# Search available versions
repo-ctx repo search fastapi
```

---

## CLI Reference

### Operating Modes

repo-ctx supports three operating modes:

| Mode | Command | Description |
|------|---------|-------------|
| **Interactive** | `repo-ctx` or `repo-ctx -i` | Command palette UI |
| **MCP Server** | `repo-ctx -m` | For AI assistant integration |
| **Batch** | `repo-ctx <command>` | Direct command execution |

### Global Options

```bash
-o, --output {text,json,yaml}  # Output format (default: text)
-p, --provider {auto,github,gitlab,local}  # Provider selection
-c, --config PATH              # Custom config file
-v, --verbose                  # Verbose output
-m, --mcp                      # Start MCP server
-i, --interactive              # Start interactive mode
```

### Repository Commands

#### `repo index` - Index a Repository

```bash
# Local repository
repo-ctx repo index /path/to/repo
repo-ctx repo index ./relative/path
repo-ctx repo index ~/my-project

# GitHub repository
repo-ctx repo index owner/repo
repo-ctx repo index fastapi/fastapi --provider github

# GitLab repository
repo-ctx repo index group/project --provider gitlab
repo-ctx repo index group/subgroup/project --provider gitlab
```

#### `repo index-group` - Index Organization/Group

```bash
# GitHub organization
repo-ctx repo index-group microsoft --provider github

# GitLab group (includes subgroups by default)
repo-ctx repo index-group mycompany --provider gitlab

# GitLab group without subgroups
repo-ctx repo index-group mycompany --provider gitlab --no-subgroups
```

#### `repo search` - Search Repositories

```bash
# Fuzzy search (typo-tolerant)
repo-ctx repo search "fastapi"
repo-ctx repo search "fasapi"  # Still finds "fastapi"

# Limit results
repo-ctx repo search "api" --limit 20

# JSON output
repo-ctx -o json repo search "api"
```

#### `repo find-exact` - Exact Name Search

```bash
# Exact match only
repo-ctx repo find-exact "fastapi"
```

#### `repo list` - List Indexed Repositories

```bash
# List all repositories
repo-ctx repo list

# Filter by provider
repo-ctx repo list --provider github
repo-ctx repo list --provider gitlab
repo-ctx repo list --provider local

# JSON output
repo-ctx -o json repo list
```

#### `repo docs` - Get Documentation

```bash
# Basic documentation retrieval
repo-ctx repo docs /owner/repo

# With topic filter
repo-ctx repo docs /owner/repo --topic api

# With token limit (recommended for AI assistants)
repo-ctx repo docs /owner/repo --max-tokens 8000

# Include code analysis
repo-ctx repo docs /owner/repo --include=code
repo-ctx repo docs /owner/repo --include=code,diagrams,symbols

# Include everything
repo-ctx repo docs /owner/repo --include=all

# Specific version
repo-ctx repo docs /owner/repo/v1.0.0
```

**Include Options:**

| Option | Description |
|--------|-------------|
| `code` | Code structure (classes, functions, modules) |
| `symbols` | Detailed symbol information with signatures |
| `diagrams` | Mermaid diagrams (class hierarchy) |
| `tests` | Include test files in analysis |
| `examples` | Include all code examples from docs |
| `all` | Enable all options |

### Code Analysis Commands

#### `code analyze` - Analyze Code Structure

```bash
# Analyze directory
repo-ctx code analyze ./src

# Filter by language
repo-ctx code analyze ./src --language python

# Filter by symbol type
repo-ctx code analyze ./src --symbol-type class

# Show dependencies
repo-ctx code analyze ./src --deps

# Analyze indexed repository
repo-ctx code analyze /owner/repo --repo

# Output formats
repo-ctx code analyze ./src -o json
repo-ctx code analyze ./src -o yaml
```

#### `code find` - Search for Symbols

```bash
# Search by name pattern
repo-ctx code find ./src "User"
repo-ctx code find ./src "Service" --symbol-type class

# Filter by language
repo-ctx code find ./src "handler" --language python

# Search in indexed repository
repo-ctx code find /owner/repo "User" --repo
```

#### `code info` - Get Symbol Details

```bash
# Get detailed information about a symbol
repo-ctx code info ./src "UserService"
repo-ctx code info ./src "UserService.create_user"

# JSON output for structured data
repo-ctx -o json code info ./src "UserService"
```

#### `code symbols` - List File Symbols

```bash
# List all symbols in a file
repo-ctx code symbols ./src/service.py

# Group by type
repo-ctx code symbols ./src/service.py --group

# JSON output
repo-ctx -o json code symbols ./src/service.py
```

#### `code dep` - Generate Dependency Graph

```bash
# Class dependency graph (default)
repo-ctx code dep ./src

# Different graph types
repo-ctx code dep ./src --graph-type class
repo-ctx code dep ./src --graph-type function
repo-ctx code dep ./src --graph-type file
repo-ctx code dep ./src --graph-type module

# Output formats
repo-ctx code dep ./src --output-format json    # JSON Graph Format
repo-ctx code dep ./src --output-format dot     # GraphViz DOT
repo-ctx code dep ./src --output-format graphml # GraphML XML

# Limit depth
repo-ctx code dep ./src --depth 3

# From indexed repository
repo-ctx code dep /owner/repo --repo
```

### Configuration Commands

#### `config show` - Show Current Configuration

```bash
repo-ctx config show
repo-ctx -o json config show
```

---

## MCP Server Integration

### What is MCP?

MCP (Model Context Protocol) is a standard protocol for AI assistants to access external tools and data. repo-ctx implements an MCP server that exposes its functionality to AI assistants like Claude Code.

### MCP Server Setup

#### Claude Code Configuration

Add to `~/.config/claude/mcp.json`:

```json
{
  "mcpServers": {
    "repo-ctx": {
      "command": "uvx",
      "args": ["repo-ctx", "-m"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}",
        "GITLAB_URL": "${GITLAB_URL}",
        "GITLAB_TOKEN": "${GITLAB_TOKEN}"
      }
    }
  }
}
```

#### Minimal Setup (Local + Public GitHub)

```json
{
  "mcpServers": {
    "repo-ctx": {
      "command": "uvx",
      "args": ["repo-ctx", "-m"]
    }
  }
}
```

#### From Source (Development)

```json
{
  "mcpServers": {
    "repo-ctx": {
      "command": "uv",
      "args": ["--directory", "/path/to/repo-ctx", "run", "repo-ctx", "-m"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

### Available MCP Tools

repo-ctx provides **12 MCP tools**:

#### Repository Management

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `repo-ctx-index` | Index a repository | `repository`, `provider` |
| `repo-ctx-index-group` | Index organization/group | `group`, `provider`, `includeSubgroups` |
| `repo-ctx-list` | List indexed repositories | `provider` (optional filter) |
| `repo-ctx-search` | Fuzzy search repositories | `query`, `limit` |
| `repo-ctx-find-repo` | Exact name search | `libraryName` |
| `repo-ctx-docs` | Get documentation | `libraryId`, `topic`, `maxTokens`, `include` |

#### Code Analysis

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `repo-ctx-analyze` | Analyze code structure | `path`, `repository`, `language`, `symbolType` |
| `repo-ctx-find-symbol` | Search for symbols | `path`, `query`, `symbolType`, `language` |
| `repo-ctx-symbol-detail` | Get symbol details | `path`, `symbolName` |
| `repo-ctx-file-symbols` | List file symbols | `filePath`, `groupByType` |
| `repo-ctx-dependency-graph` | Generate dependency graph | `path`, `graphType`, `outputFormat` |
| `repo-ctx-llmstxt` | Generate llms.txt format | `libraryId` |

### MCP Tool Examples

```javascript
// Index a repository
await mcp.call("repo-ctx-index", {
  repository: "fastapi/fastapi"
});

// Search across repositories
const results = await mcp.call("repo-ctx-search", {
  query: "authentication",
  limit: 10
});

// Get documentation with code analysis
const docs = await mcp.call("repo-ctx-docs", {
  libraryId: "/fastapi/fastapi",
  maxTokens: 10000,
  include: ["code", "diagrams"]
});

// Analyze code
const analysis = await mcp.call("repo-ctx-analyze", {
  path: "./src",
  language: "python",
  symbolType: "class"
});

// Search for symbols
const symbols = await mcp.call("repo-ctx-find-symbol", {
  path: "./src",
  query: "User",
  symbolType: "class"
});

// Generate dependency graph
const graph = await mcp.call("repo-ctx-dependency-graph", {
  path: "./src",
  graphType: "class",
  outputFormat: "json"
});
```

### Parameter Compatibility

Both old (camelCase) and new (snake_case) parameter names are supported:

| New Name | Old Name (deprecated) |
|----------|----------------------|
| `repository` | `libraryId`, `repoId` |
| `symbol_type` | `symbolType` |
| `output_format` | `outputFormat` |
| `language` | `lang` |
| `file_path` | `filePath` |

---

## Python Library API

### Installation

```python
from repo_ctx import (
    RepositoryContext,
    Config,
    CodeAnalyzer,
    Symbol,
    SymbolType,
)
```

### Basic Usage

```python
import asyncio
from repo_ctx import Config, RepositoryContext

async def main():
    # Load configuration
    config = Config.from_env()

    # Create context and initialize
    context = RepositoryContext(config)
    await context.init()

    # Index a repository
    await context.index_repository("fastapi", "fastapi", provider_type="github")

    # Search
    results = await context.fuzzy_search_libraries("fastapi", limit=5)
    for result in results:
        print(f"{result.name} (score: {result.score})")

    # Get documentation
    docs = await context.get_documentation("/fastapi/fastapi")
    print(docs["content"][0]["text"])

asyncio.run(main())
```

### Code Analysis API

```python
from repo_ctx import CodeAnalyzer, SymbolType

analyzer = CodeAnalyzer()

# Analyze a file
code = open("service.py").read()
symbols = analyzer.analyze_file(code, "service.py")

# Analyze multiple files
files = {
    "service.py": open("service.py").read(),
    "models.py": open("models.py").read(),
}
results = analyzer.analyze_files(files)
all_symbols = analyzer.aggregate_symbols(results)

# Filter symbols
classes = analyzer.filter_symbols_by_type(all_symbols, SymbolType.CLASS)
public = analyzer.filter_symbols_by_visibility(all_symbols, "public")

# Search symbols
found = analyzer.find_symbol(all_symbols, "UserService")
matches = analyzer.find_symbols(all_symbols, "user")

# Get statistics
stats = analyzer.get_statistics(all_symbols)
# {'total_symbols': 15, 'by_type': {'class': 3, 'method': 12}, ...}

# Extract dependencies
deps = analyzer.extract_dependencies(code, "service.py")
```

### Symbol Properties

```python
symbol = symbols[0]

symbol.name           # "UserService"
symbol.symbol_type    # SymbolType.CLASS
symbol.file_path      # "service.py"
symbol.line_start     # 10
symbol.line_end       # 50
symbol.signature      # "class UserService"
symbol.visibility     # "public" | "private" | "protected"
symbol.language       # "python"
symbol.qualified_name # "UserService"
symbol.documentation  # "Service for managing users."
symbol.is_exported    # True
symbol.metadata       # {"bases": ["BaseService"]}
```

---

## Troubleshooting

### Common Issues

#### "Provider 'gitlab' not configured"

GitLab requires configuration:

```bash
export GITLAB_URL="https://gitlab.company.com"
export GITLAB_TOKEN="glpat-your_token"
```

#### "Rate limit exceeded" (GitHub)

Unauthenticated GitHub access is limited to 60 requests/hour:

```bash
export GITHUB_TOKEN="ghp_your_token"  # Increases to 5000/hour
```

#### "Repository not found"

- Check repository path format matches provider
- Verify you have access (token has correct permissions)
- For private repos, ensure token is configured
- For local repos, ensure path contains `.git` directory

#### "No results found"

Index the repository first:

```bash
repo-ctx repo index owner/repo
repo-ctx repo list  # Verify it's indexed
```

#### "Symbol not found"

- Check the symbol name and case
- Use fuzzy search: `repo-ctx code find ./src "partial_name"`
- Verify file is a supported language

### Debug Mode

Enable verbose output:

```bash
repo-ctx -v repo index owner/repo
```

### Database Location

Default database location: `~/.repo-ctx/context.db`

To use a different location:

```bash
export STORAGE_PATH="/custom/path/context.db"
```

To reset the database, simply delete it:

```bash
rm ~/.repo-ctx/context.db
```

---

## Further Reading

- [Multi-Provider Guide](multi-provider-guide.md) - Detailed provider configuration
- [MCP Tools Reference](mcp_tools_reference.md) - Complete MCP tool documentation
- [Library API Reference](library/api-reference.md) - Python API documentation
- [Architecture Guide](library/architecture.md) - Internal architecture
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute

---

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/osick/repo-ctx/issues)
- **Documentation**: This guide and related docs in the `docs/` folder
