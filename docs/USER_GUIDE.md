# repo-ctx User Guide

A multi-provider repository documentation indexer and code analyzer supporting GitLab, GitHub, and local Git repositories.

---

## Operating Modes

repo-ctx supports three operating modes:

| Mode | Command | Description |
|------|---------|-------------|
| Interactive | `repo-ctx` or `repo-ctx -i` | Command palette UI |
| MCP Server | `repo-ctx -m` | For AI assistants |
| Batch | `repo-ctx <command>` | Direct command execution |

---

## CLI Commands

### Interactive Mode

```bash
# Start interactive command palette (default)
repo-ctx

# Explicitly start interactive mode
repo-ctx -i
repo-ctx --interactive
```

### Repository Commands

```bash
# Index repositories
repo-ctx repo index owner/repo
repo-ctx repo index /path/to/local/repo
repo-ctx repo index group/project --provider gitlab

# Search repositories
repo-ctx repo search fastapi
repo-ctx repo search fastapi --limit 20

# List indexed repositories
repo-ctx repo list
repo-ctx repo list --provider github

# Get documentation
repo-ctx repo docs /owner/repo
repo-ctx repo docs /owner/repo --topic api --max-tokens 8000
```

### Code Analysis Commands

```bash
# Analyze code structure
repo-ctx code analyze ./src
repo-ctx -o json code analyze ./src
repo-ctx code analyze ./src --lang python --type class
repo-ctx code analyze ./src --deps

# Search for symbols
repo-ctx code find ./src User
repo-ctx -o json code find ./src Service --type class

# Get symbol details
repo-ctx code info ./src UserService
repo-ctx -o json code info ./src UserService

# List file symbols
repo-ctx code symbols ./src/service.py
repo-ctx -o json code symbols ./src/service.py --group
```

### Configuration Commands

```bash
# Show current configuration
repo-ctx config show
repo-ctx -o json config show
```

### Global Options

```bash
-o, --output {text,json,yaml}  # Output format (default: text)
-p, --provider {auto,github,gitlab,local}  # Provider override
-c, --config PATH              # Config file path
-v, --verbose                  # Verbose output
```

---

## MCP Tools (10 tools)

### Repository Management

| Tool | Description |
|------|-------------|
| `repo-ctx-search` | Search indexed repositories by exact name |
| `repo-ctx-fuzzy-search` | Fuzzy/typo-tolerant search |
| `repo-ctx-index` | Index a single repository |
| `repo-ctx-index-group` | Index all repos in a group/org |
| `repo-ctx-list` | List all indexed repositories |
| `repo-ctx-docs` | Retrieve documentation content |

```javascript
// Index a repository
await mcp.call("repo-ctx-index", { repository: "owner/repo" });

// Fuzzy search
await mcp.call("repo-ctx-fuzzy-search", { query: "fastapi", limit: 5 });

// Get documentation
await mcp.call("repo-ctx-docs", { libraryId: "/owner/repo", maxTokens: 8000 });
```

### Code Analysis

| Tool | Description |
|------|-------------|
| `repo-ctx-analyze` | Extract symbols from code |
| `repo-ctx-search-symbol` | Search symbols by name pattern |
| `repo-ctx-get-symbol-detail` | Get detailed symbol info |
| `repo-ctx-get-file-symbols` | List all symbols in a file |

**Supported languages:** Python, JavaScript, TypeScript, Java, Kotlin

```javascript
// Analyze code (JSON output)
await mcp.call("repo-ctx-analyze", {
  path: "./src",
  language: "python",
  outputFormat: "json"
});

// Search for symbols
await mcp.call("repo-ctx-search-symbol", {
  path: "./src",
  query: "User",
  symbolType: "class"
});

// Get symbol details
await mcp.call("repo-ctx-get-symbol-detail", {
  path: "./src",
  symbolName: "UserService",
  outputFormat: "json"
});

// List file symbols
await mcp.call("repo-ctx-get-file-symbols", {
  filePath: "./src/service.py",
  groupByType: true,
  outputFormat: "json"
});
```

---

## Library API

### Installation

```python
from repo_ctx import (
    CodeAnalyzer,
    Symbol,
    SymbolType,
    Config,
    Storage,
    GitLabContext,
)
```

### Code Analysis

```python
from repo_ctx import CodeAnalyzer, SymbolType

analyzer = CodeAnalyzer()

# Analyze a single file
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
matches = analyzer.find_symbols(all_symbols, "user")  # pattern match

# Get statistics
stats = analyzer.get_statistics(all_symbols)
# {'total_symbols': 15, 'by_type': {'class': 3, 'method': 12}, ...}

# Extract dependencies
deps = analyzer.extract_dependencies(code, "service.py")
# [{'type': 'import', 'source': 'service.py', 'target': 'os', ...}]

# Supported languages
languages = analyzer.get_supported_languages()
# ['python', 'javascript', 'typescript', 'java', 'kotlin']
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

### Repository Indexing

```python
import asyncio
from repo_ctx import Config, GitLabContext

async def main():
    config = Config.load()
    context = GitLabContext(config)
    await context.init()

    # Index repository
    await context.index_repository("owner", "repo")

    # Search
    results = await context.search_libraries("fastapi")
    fuzzy = await context.fuzzy_search_libraries("fasapi", limit=5)

    # Get documentation
    docs = await context.get_documentation("/owner/repo", max_tokens=8000)

asyncio.run(main())
```

---

## Configuration

### Environment Variables

```bash
# GitHub (optional for public repos)
export GITHUB_TOKEN=ghp_xxx

# GitLab (required)
export GITLAB_URL=https://gitlab.company.com
export GITLAB_TOKEN=glpat-xxx
```

### MCP Server Config

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

---

## Quick Reference

### CLI Commands

| Category | Command | Description |
|----------|---------|-------------|
| Repo | `repo index <path>` | Index a repository |
| Repo | `repo search <query>` | Search repositories |
| Repo | `repo list` | List indexed repos |
| Repo | `repo docs <id>` | Get documentation |
| Code | `code analyze <path>` | Analyze code structure |
| Code | `code find <path> <query>` | Search symbols |
| Code | `code info <path> <name>` | Get symbol details |
| Code | `code symbols <file>` | List file symbols |
| Config | `config show` | Show configuration |

### MCP Tools

| Category | Tool | Description |
|----------|------|-------------|
| Repo | `repo-ctx-index` | Index repository |
| Repo | `repo-ctx-search` | Exact search |
| Repo | `repo-ctx-fuzzy-search` | Fuzzy search |
| Repo | `repo-ctx-list` | List repositories |
| Repo | `repo-ctx-docs` | Get documentation |
| Code | `repo-ctx-analyze` | Analyze code |
| Code | `repo-ctx-search-symbol` | Search symbols |
| Code | `repo-ctx-get-symbol-detail` | Symbol details |
| Code | `repo-ctx-get-file-symbols` | File symbols |

**Output formats:** `text` (default), `json`, `yaml`

**Languages:** Python, JavaScript, TypeScript, Java, Kotlin
