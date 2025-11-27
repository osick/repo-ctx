# repo-ctx User Guide

A multi-provider repository documentation indexer and code analyzer supporting GitLab, GitHub, and local Git repositories.

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

## CLI Commands

### Repository Management

```bash
# Index repositories
repo-ctx --index owner/repo
repo-ctx --index /path/to/local/repo
repo-ctx --index group/project --provider gitlab

# Search repositories
repo-ctx search fastapi
repo-ctx list
repo-ctx list --provider github

# Get documentation
repo-ctx docs /owner/repo
repo-ctx docs /owner/repo --topic api --max-tokens 8000
```

### Code Analysis

```bash
# Analyze code structure
repo-ctx analyze ./src
repo-ctx analyze ./src --output json
repo-ctx analyze ./src --language python --filter-type class
repo-ctx analyze ./src --show-dependencies
repo-ctx analyze ./src --show-callgraph

# Search for symbols
repo-ctx search-symbol ./src User
repo-ctx search-symbol ./src Service --filter-type class --output json

# Get symbol details
repo-ctx symbol-detail ./src UserService
repo-ctx symbol-detail ./src UserService --output json

# List file symbols
repo-ctx file-symbols ./src/service.py
repo-ctx file-symbols ./src/service.py --output json
```

### Output Formats

All analysis commands support `--output text|json|yaml`:

```bash
repo-ctx analyze ./src --output json
repo-ctx search-symbol ./src User --output yaml
repo-ctx symbol-detail ./src MyClass --output json
repo-ctx file-symbols ./src/app.py --output json
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
      "args": ["repo-ctx"],
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

| Interface | Analyze | Search | Detail | File Symbols |
|-----------|---------|--------|--------|--------------|
| MCP | `repo-ctx-analyze` | `repo-ctx-search-symbol` | `repo-ctx-get-symbol-detail` | `repo-ctx-get-file-symbols` |
| CLI | `analyze` | `search-symbol` | `symbol-detail` | `file-symbols` |
| Library | `analyze_file()` | `find_symbols()` | `find_symbol()` | `analyze_file()` |

**Output formats:** `text` (default), `json`, `yaml`

**Languages:** Python, JavaScript, TypeScript, Java, Kotlin
