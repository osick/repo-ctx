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
repo-ctx code analyze /owner/repo --repo        # Analyze indexed repo

# Search for symbols
repo-ctx code find ./src User
repo-ctx -o json code find ./src Service --type class
repo-ctx code find /owner/repo User --repo      # Search in indexed repo

# Get symbol details
repo-ctx code info ./src UserService
repo-ctx -o json code info ./src UserService

# List file symbols
repo-ctx code symbols ./src/service.py
repo-ctx -o json code symbols ./src/service.py --group

# Generate dependency graphs
repo-ctx code dep ./src                          # Default: class diagram
repo-ctx code dep ./src --type function          # Call graph
repo-ctx code dep ./src --type file              # File dependencies
repo-ctx code dep ./src --format dot             # GraphViz format
repo-ctx code dep /owner/repo --repo             # From indexed repo
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

### Include Options (for `repo docs`)

The `--include` flag controls what content is included in documentation output:

```bash
-I, --include OPTIONS  # Comma-separated list of content types
```

| Option | Description |
|--------|-------------|
| `code` | Code structure (classes, functions, methods) |
| `symbols` | Detailed symbol information with signatures |
| `diagrams` | Mermaid diagrams (class hierarchy) |
| `tests` | Include test files in analysis |
| `examples` | Include all code examples from docs |
| `all` | Enable all options |

```bash
# Include code structure only
repo-ctx repo docs /owner/repo --include=code

# Include code with diagrams
repo-ctx repo docs /owner/repo --include=code,diagrams

# Include everything
repo-ctx repo docs /owner/repo --include=all

# Combine with other options
repo-ctx repo docs /owner/repo --include=code,symbols --max-tokens 15000
```

---

## MCP Tools (11 tools)

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

// Get documentation with code analysis
await mcp.call("repo-ctx-docs", {
  libraryId: "/owner/repo",
  maxTokens: 10000,
  include: ["code", "diagrams"]
});
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

---

## Dependency Graph Commands

### CLI

```bash
# Generate class dependency graph (JSON, default)
repo-ctx code dep ./src --type class

# Generate function call graph as DOT (GraphViz)
repo-ctx code dep ./src --type function --format dot

# Generate file dependency graph as GraphML
repo-ctx code dep ./src --type file --format graphml

# Analyze indexed repository
repo-ctx code dep -r /owner/repo --type class

# Limit traversal depth
repo-ctx code dep ./src --type class --depth 3
```

### MCP Tool

| Tool | Description |
|------|-------------|
| `repo-ctx-dependency-graph` | Generate dependency graphs |

```javascript
// Generate class dependency graph
await mcp.call("repo-ctx-dependency-graph", {
  path: "./src",
  graphType: "class",
  outputFormat: "json"
});

// Generate function call graph for indexed repo
await mcp.call("repo-ctx-dependency-graph", {
  repoId: "/owner/repo",
  graphType: "function",
  outputFormat: "dot"
});
```

### Graph Types

| Type | Description |
|------|-------------|
| `file` | File-level import dependencies |
| `module` | Module/package dependencies |
| `class` | Class inheritance and composition |
| `function` | Function/method call graph |
| `symbol` | Complete symbol graph (all relationships) |

### Output Formats

| Format | Description |
|--------|-------------|
| `json` | JSON Graph Format (JGF) - structured, machine-readable |
| `dot` | GraphViz DOT - for visualization with `dot -Tsvg` |
| `graphml` | GraphML XML - for graph analysis tools |

---

## Combined Documentation with Code Analysis

Get documentation AND code analysis together using `--include`:

### CLI

```bash
# Get docs with code analysis summary
repo-ctx repo docs /owner/repo --include=code

# With detailed symbols and diagrams
repo-ctx repo docs /owner/repo --include=code,symbols,diagrams

# Include test files in analysis
repo-ctx repo docs /owner/repo --include=code,tests

# Include everything
repo-ctx repo docs /owner/repo --include=all --max-tokens 15000

# JSON output
repo-ctx -o json repo docs /owner/repo --include=code
```

### MCP Tool

```javascript
// Get documentation with code analysis
await mcp.call("repo-ctx-docs", {
  libraryId: "/owner/repo",
  maxTokens: 10000,
  include: ["code"]
});

// Include code, symbols, and diagrams
await mcp.call("repo-ctx-docs", {
  libraryId: "/owner/repo",
  maxTokens: 15000,
  include: ["code", "symbols", "diagrams"]
});

// Include everything
await mcp.call("repo-ctx-docs", {
  libraryId: "/owner/repo",
  include: ["all"]
});
```

### Include Options

| Option | Description |
|--------|-------------|
| `code` | Code structure (classes, functions, methods) |
| `symbols` | Detailed symbol information with signatures and docs |
| `diagrams` | Mermaid class hierarchy diagrams |
| `tests` | Include test files in code analysis |
| `examples` | Include all code examples from documentation |
| `all` | Enable all of the above options |

The code analysis section includes:
- **Symbol Summary**: Count of classes, functions, methods, interfaces by language
- **Class Hierarchy**: Mermaid diagram showing inheritance relationships (when `diagrams` included)
- **Top-Level API**: Public classes and functions with signatures
- **Detailed Symbols**: Full symbol details with docs (when `symbols` included)
- **Dependency Overview**: Key import relationships

---

## Complete Information Summary

### Available Information Types

| Category | Information | CLI | MCP | Library API |
|----------|-------------|-----|-----|-------------|
| **Documentation** | README, guides, API docs | `repo docs` | `repo-ctx-docs` | `get_documentation()` |
| **Repository Metadata** | Name, description, versions | `repo list` | `repo-ctx-list` | `list_all_libraries()` |
| **Code Symbols** | Classes, functions, methods | `code analyze` | `repo-ctx-analyze` | `analyze_file()` |
| **Symbol Search** | Find by name/pattern | `code find` | `repo-ctx-search-symbol` | `find_symbols()` |
| **Symbol Details** | Signature, docs, location | `code info` | `repo-ctx-get-symbol-detail` | `find_symbol()` |
| **File Symbols** | All symbols in a file | `code symbols` | `repo-ctx-get-file-symbols` | `analyze_file()` |
| **Dependencies** | Import/call relationships | `code dep` | `repo-ctx-dependency-graph` | `extract_dependencies()` |
| **Dependency Graph** | Visual graph (DOT/GraphML) | `code dep --format dot` | `repo-ctx-dependency-graph` | `DependencyGraph.build()` |

### Symbol Types Extracted

| Type | Python | JavaScript | TypeScript | Java | Kotlin |
|------|--------|------------|------------|------|--------|
| Class | ✓ | ✓ | ✓ | ✓ | ✓ |
| Function | ✓ | ✓ | ✓ | ✓ | ✓ |
| Method | ✓ | ✓ | ✓ | ✓ | ✓ |
| Interface | - | - | ✓ | ✓ | ✓ |
| Enum | ✓ | - | ✓ | ✓ | ✓ |

### Dependency/Relationship Types

| Relation | Description | Graph Types |
|----------|-------------|-------------|
| `imports` | Module/file imports | file, module |
| `inherits` | Class inheritance | class, symbol |
| `implements` | Interface implementation | class, symbol |
| `contains` | Containment (class→method) | symbol |
| `calls` | Function/method calls | function, symbol |

### Output Formats by Command

| Command | text | json | yaml | dot | graphml |
|---------|------|------|------|-----|---------|
| `repo docs` | ✓ | ✓ | ✓ | - | - |
| `code analyze` | ✓ | ✓ | ✓ | - | - |
| `code find` | ✓ | ✓ | ✓ | - | - |
| `code info` | ✓ | ✓ | ✓ | - | - |
| `code symbols` | ✓ | ✓ | ✓ | - | - |
| `code dep` | - | ✓ | - | ✓ | ✓ |

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         repo-ctx                                 │
├─────────────────────────────────────────────────────────────────┤
│  Providers          │  Analysis           │  Storage            │
│  ─────────          │  ────────           │  ───────            │
│  • GitHub           │  • PythonExtractor  │  • SQLite DB        │
│  • GitLab           │  • JavaScriptExtr.  │  • FTS5 Search      │
│  • Local Git        │  • JavaExtractor    │  • Symbol Index     │
│                     │  • KotlinExtractor  │  • Doc Index        │
│                     │  • DependencyGraph  │                     │
├─────────────────────────────────────────────────────────────────┤
│  Interfaces                                                      │
│  ──────────                                                      │
│  • CLI (Interactive/Batch)                                       │
│  • MCP Server (11 tools)                                         │
│  • Python Library API                                            │
└─────────────────────────────────────────────────────────────────┘
```

### MCP Tools Summary (11 tools)

| # | Tool | Category | Key Parameters |
|---|------|----------|----------------|
| 1 | `repo-ctx-search` | Repo | `libraryName` |
| 2 | `repo-ctx-fuzzy-search` | Repo | `query`, `limit` |
| 3 | `repo-ctx-index` | Repo | `repository`, `provider` |
| 4 | `repo-ctx-index-group` | Repo | `group`, `includeSubgroups` |
| 5 | `repo-ctx-list` | Repo | `provider` |
| 6 | `repo-ctx-docs` | Repo | `libraryId`, `maxTokens`, `include` |
| 7 | `repo-ctx-analyze` | Code | `path`, `repoId`, `language`, `symbolType` |
| 8 | `repo-ctx-search-symbol` | Code | `path`, `repoId`, `query`, `symbolType` |
| 9 | `repo-ctx-get-symbol-detail` | Code | `path`, `repoId`, `symbolName` |
| 10 | `repo-ctx-get-file-symbols` | Code | `filePath`, `groupByType` |
| 11 | `repo-ctx-dependency-graph` | Code | `path`, `repoId`, `graphType`, `outputFormat` |
