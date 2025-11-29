# repo-ctx MCP Tools Reference

Complete reference for all MCP tools provided by the repo-ctx server.

---

## Overview

repo-ctx provides **10 MCP tools** for repository documentation indexing, retrieval, and code analysis:

### Repository Management & Documentation (6 tools)

1. **repo-ctx-search** - Search for indexed repositories
2. **repo-ctx-fuzzy-search** - Fuzzy/typo-tolerant search
3. **repo-ctx-index** - Index a single repository
4. **repo-ctx-index-group** - Index all repositories in a group/organization
5. **repo-ctx-list** - List all indexed repositories
6. **repo-ctx-docs** - Retrieve documentation content

### Code Analysis (4 tools)

7. **repo-ctx-analyze** - Analyze code structure and extract symbols
8. **repo-ctx-search-symbol** - Search for symbols by name or pattern
9. **repo-ctx-get-symbol-detail** - Get detailed symbol information
10. **repo-ctx-get-file-symbols** - List all symbols in a specific file

**Note:** All tools support **GitLab, GitHub, and local Git repositories** with auto-detection or explicit provider selection.

**Supported languages for code analysis:** Python, JavaScript, TypeScript, Java, Kotlin

---

## 1. repo-ctx-search

**Purpose:** Search for indexed repositories by exact name match.

**When to use:** When you know the exact repository name and want to see available versions.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `libraryName` | string | ✅ Yes | Library name to search for |

### Returns

List of matching libraries with:
- Library ID (format: `/group/project`)
- Name
- Description
- Available versions

### Example Usage

```javascript
// Search for a specific library
const results = await use_mcp_tool("repo-ctx", "repo-ctx-search", {
  libraryName: "fastapi"
});
```

### Example Output

```
Available Libraries (search results):

- Library ID: /tiangolo/fastapi
  Name: fastapi
  Description: FastAPI framework for building APIs
  Versions: main, v0.109.0, v0.108.0

- Library ID: /mygroup/fastapi-service
  Name: fastapi-service
  Description: Internal FastAPI microservice
  Versions: main, develop, v1.0.0
```

---

## 2. repo-ctx-fuzzy-search

**Purpose:** Fuzzy/typo-tolerant search for repositories with ranking.

**When to use:** When you don't know the exact repository name or want to discover repositories by partial match.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | ✅ Yes | - | Search term (can be partial or contain typos) |
| `limit` | integer | ❌ No | 10 | Maximum number of results to return |

### Returns

Ranked list of matching repositories with:
- Library ID
- Name
- Group/Owner
- Description
- Match type (exact, starts_with, contains, fuzzy)
- Matched field (name, description, etc.)
- Score (higher = better match)

### Example Usage

```javascript
// Fuzzy search with typos
const results = await use_mcp_tool("repo-ctx", "repo-ctx-fuzzy-search", {
  query: "fasapi",  // Typo: missing 't'
  limit: 5
});

// Search by partial name
const results2 = await use_mcp_tool("repo-ctx", "repo-ctx-fuzzy-search", {
  query: "api",
  limit: 10
});
```

### Example Output

```
Fuzzy search results for 'fasapi':

1. /tiangolo/fastapi
   Name: fastapi
   Group: tiangolo
   Description: FastAPI framework for building APIs
   Match: fuzzy in name (score: 0.85)

2. /mygroup/fastapi-service
   Name: fastapi-service
   Group: mygroup
   Description: Internal FastAPI microservice
   Match: contains in name (score: 0.70)

To get documentation, use repo-ctx-docs with one of the Library IDs above.
```

---

## 3. repo-ctx-index

**Purpose:** Index a single repository to make its documentation searchable.

**When to use:** When you want to add a specific repository to your searchable documentation index.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `repository` | string | ✅ Yes | - | Repository path (e.g., 'owner/repo', 'group/project', or '/path/to/local/repo') |
| `provider` | string | ❌ No | "auto" | Provider: 'gitlab', 'github', 'local', or 'auto' for auto-detection |

### Provider Auto-Detection

When `provider` is "auto" or omitted:
- **Absolute/relative paths** (`/path`, `./path`, `~/path`) → Local
- **2 parts** (`owner/repo`) → GitHub
- **3+ parts** (`group/subgroup/project`) → GitLab

### Returns

Success or error message with details about the indexing operation.

### Example Usage

```javascript
// Auto-detect provider (Local - absolute path)
await use_mcp_tool("repo-ctx", "repo-ctx-index", {
  repository: "/home/user/projects/my-app"
});

// Auto-detect provider (Local - relative path)
await use_mcp_tool("repo-ctx", "repo-ctx-index", {
  repository: "~/projects/my-app"
});

// Auto-detect provider (GitHub - 2 parts)
await use_mcp_tool("repo-ctx", "repo-ctx-index", {
  repository: "fastapi/fastapi"
});

// Auto-detect provider (GitLab - 3 parts)
await use_mcp_tool("repo-ctx", "repo-ctx-index", {
  repository: "mygroup/subgroup/project"
});

// Explicitly use local
await use_mcp_tool("repo-ctx", "repo-ctx-index", {
  repository: "/path/to/repo",
  provider: "local"
});

// Explicitly use GitHub
await use_mcp_tool("repo-ctx", "repo-ctx-index", {
  repository: "microsoft/vscode",
  provider: "github"
});

// Explicitly use GitLab
await use_mcp_tool("repo-ctx", "repo-ctx-index", {
  repository: "mygroup/myproject",
  provider: "gitlab"
});
```

### Example Output

```
Successfully indexed fastapi/fastapi using github provider.
You can now search for it using repo-ctx-fuzzy-search or repo-ctx-docs.
```

### What Gets Indexed

- **Default branch** (main/master)
- **Last 5 tags** (e.g., v1.0.0, v0.9.0, etc.)
- **Documentation files**: .md, .rst, .txt files
- **Configurable** via `.repo-ctx.json` or `git_context.json` in repo

---

## 4. repo-ctx-index-group

**Purpose:** Index all repositories in a GitLab group or GitHub organization.

**When to use:** When you want to index multiple repositories from an organization at once.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `group` | string | ✅ Yes | - | Group/organization path |
| `includeSubgroups` | boolean | ❌ No | true | Include nested subgroups (GitLab only) |
| `provider` | string | ❌ No | "auto" | Provider: 'gitlab', 'github', or 'auto' |

### Important Notes

- **Subgroups:** Only supported by GitLab (GitHub has no subgroup concept)
- **Rate limits:** Be mindful of API rate limits when indexing large organizations
- **Time:** Indexing many repos takes time - this is a long-running operation

### Returns

Summary with:
- Total projects found
- Successfully indexed count
- Failed count
- List of indexed repositories
- List of failed repositories (with error messages)

### Example Usage

```javascript
// Index GitHub organization
await use_mcp_tool("repo-ctx", "repo-ctx-index-group", {
  group: "microsoft",
  provider: "github"
});

// Index GitLab group with subgroups
await use_mcp_tool("repo-ctx", "repo-ctx-index-group", {
  group: "mycompany",
  includeSubgroups: true,
  provider: "gitlab"
});

// Index GitLab group without subgroups
await use_mcp_tool("repo-ctx", "repo-ctx-index-group", {
  group: "mygroup",
  includeSubgroups: false,
  provider: "gitlab"
});
```

### Example Output

```
Indexed group 'microsoft' using github provider:

Total projects: 50
Successfully indexed: 47
Failed: 3

Indexed repositories:
  - microsoft/vscode
  - microsoft/TypeScript
  - microsoft/terminal
  - microsoft/playwright
  - microsoft/vscode-python
  - microsoft/monaco-editor
  - microsoft/WindowsTerminal
  - microsoft/PowerToys
  - microsoft/WSL
  - microsoft/calculator
  ... and 37 more

Failed repositories:
  - microsoft/private-repo: Repository not found or is private
  - microsoft/archived-repo: Repository is archived
  - microsoft/empty-repo: No documentation files found
```

---

## 5. repo-ctx-list

**Purpose:** List all indexed repositories with metadata (name, description, versions, last indexed date).

**When to use:** When you want to see what repositories are available in your index, or filter by provider to see only local, GitHub, or GitLab repositories.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `provider` | string | ❌ No | - | Optional filter: 'local', 'github', or 'gitlab' |

### Returns

List of all indexed repositories with:
- Library ID (format: `/group/project`)
- Description
- Default version
- Last indexed timestamp

### Example Usage

```javascript
// List all indexed repositories
await use_mcp_tool("repo-ctx", "repo-ctx-list", {});

// List only local repositories
await use_mcp_tool("repo-ctx", "repo-ctx-list", {
  provider: "local"
});

// List only GitHub repositories
await use_mcp_tool("repo-ctx", "repo-ctx-list", {
  provider: "github"
});

// List only GitLab repositories
await use_mcp_tool("repo-ctx", "repo-ctx-list", {
  provider: "gitlab"
});
```

### Example Output

```
All indexed repositories (4 total):

1. /home/user/projects/my-app
   URL: /home/user/projects/my-app
   Description: My Local Application
   Default version: main
   Last indexed: 2025-11-25 14:30:00

2. /fastapi/fastapi
   URL: https://github.com/fastapi/fastapi
   Description: FastAPI framework for building APIs
   Default version: main
   Last indexed: 2025-11-25 10:15:00

3. /mygroup/subgroup/project
   URL: https://gitlab.company.com/mygroup/subgroup/project
   Description: Internal project documentation
   Default version: main
   Last indexed: 2025-11-24 16:20:00

4. /microsoft/vscode
   URL: https://github.com/microsoft/vscode
   Description: Visual Studio Code
   Default version: main
   Last indexed: 2025-11-23 09:45:00
```

### Provider Filtering

The tool automatically detects the provider for each repository based on its path format:

- **Local:** Repositories with paths starting with `/` or `~`
- **GitHub:** Two-part names like `owner/repo`
- **GitLab:** Three or more parts like `group/subgroup/project`

When you specify a provider filter, only repositories matching that provider will be returned.

---

## 6. repo-ctx-docs

**Purpose:** Retrieve documentation content for an indexed repository.

**When to use:** After indexing, when you want to read the actual documentation content.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `libraryId` | string | ✅ Yes | - | Library ID in format `/group/project` or `/group/project/version` |
| `topic` | string | ❌ No | - | Filter by topic (matches file path) |
| `maxTokens` | integer | ❌ No | - | **Recommended:** Maximum tokens to return (e.g., 8000 for most models, 50000 for long-context models). If specified, `page` is ignored. |
| `page` | integer | ❌ No | 1 | Page number for pagination (ignored if `maxTokens` is specified) |
| `include` | array | ❌ No | - | Additional content to include (see table below) |
| `includeMetadata` | boolean | ❌ No | false | Include quality scores and document metadata |
| `refresh` | boolean | ❌ No | false | Force re-analysis of code (ignore cache) |

### Include Options

The `include` parameter accepts an array of strings to control what additional content is included:

| Option | Description |
|--------|-------------|
| `code` | Code structure: classes, functions, modules (compact view) |
| `symbols` | Detailed symbol info: full docstrings, signatures, parameters |
| `diagrams` | Mermaid diagrams: class hierarchy, call graph, import dependencies |
| `tests` | Include test classes/functions in code analysis (excluded by default) |
| `examples` | Include ALL code examples from docs (override smart filtering of pip/docker commands) |
| `all` | Enable all options above |

### Token-Based vs Page-Based Retrieval

**Token-Based (Recommended):**
- Use `maxTokens` to control output size based on your LLM's context window
- More predictable and efficient than arbitrary page numbers
- Quality filtering applied before token limiting
- Example: `maxTokens: 8000` returns up to 8000 tokens of high-quality documentation

**Page-Based (Legacy):**
- Use `page` for simple pagination (10 documents per page)
- Less control over actual output size
- Use when you need to browse through all documents sequentially

### Library ID Formats

```
/group/project           # Default version (usually main/master)
/owner/repo              # GitHub repo, default version
/group/project/v1.0.0    # Specific version/tag
/group/project/develop   # Specific branch
```

### Returns

Formatted documentation content including:
- Library metadata (name, version)
- Page information
- Document count
- Combined markdown content from all matching documents

### Example Usage

```javascript
// Get all documentation (default version)
await use_mcp_tool("repo-ctx", "repo-ctx-docs", {
  libraryId: "/fastapi/fastapi"
});

// Get specific version
await use_mcp_tool("repo-ctx", "repo-ctx-docs", {
  libraryId: "/fastapi/fastapi/v0.109.0"
});

// Filter by topic (file path)
await use_mcp_tool("repo-ctx", "repo-ctx-docs", {
  libraryId: "/mygroup/myproject",
  topic: "api"  // Matches files with 'api' in path
});

// Pagination (10 docs per page)
await use_mcp_tool("repo-ctx", "repo-ctx-docs", {
  libraryId: "/mygroup/myproject",
  page: 2
});

// Combine filters
await use_mcp_tool("repo-ctx", "repo-ctx-docs", {
  libraryId: "/mygroup/myproject/v1.0.0",
  topic: "tutorial",
  page: 1
});

// Include code structure and diagrams (replaces old includeCodeAnalysis)
await use_mcp_tool("repo-ctx", "repo-ctx-docs", {
  libraryId: "/mygroup/myproject",
  include: ["code", "diagrams"]
});

// Full analysis including tests
await use_mcp_tool("repo-ctx", "repo-ctx-docs", {
  libraryId: "/mygroup/myproject",
  include: ["all"],
  refresh: true  // Force re-analysis
});

// Detailed symbols with diagrams (no tests)
await use_mcp_tool("repo-ctx", "repo-ctx-docs", {
  libraryId: "/mygroup/myproject",
  include: ["symbols", "diagrams"],
  maxTokens: 50000
});
```

### Example Output

```markdown
# Documentation for /fastapi/fastapi (v0.109.0)

## Page 1 of 3 (10 documents)

---

### docs/README.md

# FastAPI

FastAPI is a modern, fast (high-performance) web framework...

---

### docs/tutorial/first-steps.md

# First Steps

Let's create your first FastAPI application...

---

### docs/features.md

# Features

FastAPI provides:
- Automatic API documentation
- Data validation with Pydantic
...

---

More documents available. Use --page 2 to see next page.
```

---

## Typical Workflow

### 1. Index Repositories

```javascript
// Index individual repositories
await use_mcp_tool("repo-ctx", "repo-ctx-index", {
  repository: "fastapi/fastapi",
  provider: "github"
});

// Or index entire organization
await use_mcp_tool("repo-ctx", "repo-ctx-index-group", {
  group: "mycompany",
  provider: "gitlab"
});
```

### 2. Search for Documentation

```javascript
// Fuzzy search to find repositories
const results = await use_mcp_tool("repo-ctx", "repo-ctx-fuzzy-search", {
  query: "authentication",
  limit: 5
});

// Results show library IDs like /mygroup/auth-service
```

### 3. Retrieve Documentation

```javascript
// Get documentation for found repository
const docs = await use_mcp_tool("repo-ctx", "repo-ctx-docs", {
  libraryId: "/mygroup/auth-service"
});
```

---

## Configuration

### MCP Server Setup

**Configuration is optional** for local repositories and GitHub public repos!

**Minimal setup (local repos + GitHub public):**
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

**Full setup (all providers):**
```json
{
  "mcpServers": {
    "repo-ctx": {
      "command": "uvx",
      "args": ["repo-ctx"],
      "env": {
        "GITLAB_URL": "https://gitlab.company.com",
        "GITLAB_TOKEN": "${GITLAB_TOKEN}",
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

**Configuration requirements:**
- **Local repos:** No configuration needed
- **GitHub public repos:** No configuration needed (60 req/hr rate limit)
- **GitHub private repos:** Requires `GITHUB_TOKEN` (5000 req/hr)
- **GitLab:** Requires `GITLAB_URL` and `GITLAB_TOKEN`

---

## Error Messages

### Common Errors and Solutions

**"Provider 'local' not configured"**
- This shouldn't happen - local provider is always available
- Check that the path points to a valid Git repository

**"Provider 'github' not configured"**
- ~~Solution: Add GITHUB_TOKEN to MCP server environment~~
- **New behavior:** GitHub is always available for public repos!
- If you see this error, it's likely a bug - GitHub should work without token

**"Provider 'gitlab' not configured"**
- Solution: Add GITLAB_URL and GITLAB_TOKEN to MCP server environment

**"Repository not found"**
- Solution: Check repository path format and provider
- For local: Ensure path contains `.git` directory
- For GitHub/GitLab: Ensure you have access (token has correct permissions)
- Check repository visibility (public vs private)

**"GitHub authentication failed, falling back to unauthenticated access"**
- Warning (not error): Invalid or expired GitHub token detected
- Automatically falls back to unauthenticated mode for public repos
- To fix: Update your GITHUB_TOKEN with a valid token
- Unauthenticated mode: 60 requests/hour rate limit

**"No results found"**
- Solution: Index the repository first using repo-ctx-index

**"Version not found"**
- Solution: Check available versions with repo-ctx-search

**"Path is not a Git repository"**
- Solution: Ensure the path contains a `.git` directory
- Initialize Git: `git init` (if starting a new repo)

---

## Tips & Best Practices

### 1. Search Before Indexing

Use `repo-ctx-fuzzy-search` to check if a repository is already indexed:

```javascript
const results = await use_mcp_tool("repo-ctx", "repo-ctx-fuzzy-search", {
  query: "fastapi"
});
// If found, no need to index again
```

### 2. Index in Batches

When indexing many repositories, use `repo-ctx-index-group` instead of multiple `repo-ctx-index` calls:

```javascript
// ✅ Better
await use_mcp_tool("repo-ctx", "repo-ctx-index-group", {
  group: "mycompany",
  provider: "gitlab"
});

// ❌ Slower
await use_mcp_tool("repo-ctx", "repo-ctx-index", {
  repository: "mycompany/repo1"
});
await use_mcp_tool("repo-ctx", "repo-ctx-index", {
  repository: "mycompany/repo2"
});
// ... many more calls
```

### 3. Use Specific Versions

For stable documentation, reference specific versions:

```javascript
// ✅ Specific version (won't change)
libraryId: "/fastapi/fastapi/v0.109.0"

// ⚠️ Default version (might change when repo updates)
libraryId: "/fastapi/fastapi"
```

### 4. Filter by Topic

Use topic filtering to get relevant sections:

```javascript
// Get only API documentation
await use_mcp_tool("repo-ctx", "repo-ctx-docs", {
  libraryId: "/mygroup/myproject",
  topic: "api"
});
```

### 5. Explicit Provider for Ambiguous Paths

Use explicit provider when path format is ambiguous:

```javascript
// Without provider, 2 parts = GitHub
await use_mcp_tool("repo-ctx", "repo-ctx-index", {
  repository: "group/project"  // → GitHub (wrong!)
});

// With explicit provider
await use_mcp_tool("repo-ctx", "repo-ctx-index", {
  repository: "group/project",
  provider: "gitlab"  // ✅ Correct
});
```

---

## 7. repo-ctx-analyze

**Purpose:** Analyze source code to extract symbols (functions, classes, methods, interfaces, enums).

**When to use:** When you need to understand the code structure without indexing, or analyze remote repositories directly.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | ✅ Yes | - | Local path or remote repository (e.g., `owner/repo` for GitHub) |
| `language` | string | ❌ No | All | Filter by language: `python`, `javascript`, `typescript`, `java` |
| `symbolType` | string | ❌ No | All | Filter by type: `function`, `class`, `method`, `interface`, `enum` |
| `includePrivate` | boolean | ❌ No | true | Include private/protected symbols |
| `outputFormat` | string | ❌ No | text | Output format: `text` (human-readable with emojis), `json` (structured), `yaml` (structured) |

### Returns

List of extracted symbols with:
- Symbol name and qualified name
- Symbol type (function, class, method, etc.)
- File path and line number
- Visibility (public, private, protected)
- Documentation/comments
- Signature (for functions/methods)
- Metadata (parameters, return type, modifiers, etc.)

### Example Usage

```javascript
// Analyze local directory (human-readable text output)
const analysis = await use_mcp_tool("repo-ctx", "repo-ctx-analyze", {
  path: "./src",
  language: "python",
  symbolType: "class"
});

// Analyze with structured JSON output
const jsonAnalysis = await use_mcp_tool("repo-ctx", "repo-ctx-analyze", {
  path: "./src",
  language: "java",
  outputFormat: "json"
});

// Analyze remote GitHub repository with YAML output
const remoteAnalysis = await use_mcp_tool("repo-ctx", "repo-ctx-analyze", {
  path: "owner/repo",
  language: "java",
  symbolType: "method",
  outputFormat: "yaml"
});
```

### Example Output

```
📊 Code Analysis Results

Files analyzed: 15
Total symbols: 47

Symbols by type:
  class: 12
  method: 35

📄 src/services/UserService.java
  📦 🔓 UserService (class)
     Line 15 | public class UserService
     📖 Service for managing user accounts and authentication

  ⚡ 🔓 createUser (method)
     Line 23 | public User createUser(String name, String email)
     📖 Creates a new user account
```

---

## 8. repo-ctx-search-symbol

**Purpose:** Search for symbols by name or pattern across source files.

**When to use:** When you need to find specific functions, classes, or methods by name.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | ✅ Yes | - | Local path or remote repository to search |
| `query` | string | ✅ Yes | - | Symbol name or pattern to search for |
| `symbolType` | string | ❌ No | All | Filter by type: `function`, `class`, `method`, `interface`, `enum` |
| `language` | string | ❌ No | All | Filter by language: `python`, `javascript`, `typescript`, `java` |
| `outputFormat` | string | ❌ No | text | Output format: `text`, `json`, `yaml` |

### Returns

List of matching symbols with:
- Symbol name and location
- Symbol type
- File path and line number
- Brief preview

### Example Usage

```javascript
// Search for symbols containing "user"
const symbols = await use_mcp_tool("repo-ctx", "repo-ctx-search-symbol", {
  path: "./src",
  query: "user",
  symbolType: "class"
});
```

---

## 9. repo-ctx-get-symbol-detail

**Purpose:** Get detailed information about a specific symbol.

**When to use:** When you need comprehensive details about a specific function, class, or method.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | ✅ Yes | - | Local path or remote repository |
| `symbolName` | string | ✅ Yes | - | Exact symbol name or qualified name |
| `outputFormat` | string | ❌ No | text | Output format: `text`, `json`, `yaml` |

### Returns

Detailed symbol information including:
- Full signature
- Documentation
- Parameters and return types
- Dependencies
- Call relationships (if available)
- Metadata (modifiers, visibility, etc.)

### Example Usage

```javascript
// Get details for a specific symbol
const details = await use_mcp_tool("repo-ctx", "repo-ctx-get-symbol-detail", {
  path: "./src",
  symbolName: "UserService.createUser"
});
```

---

## 10. repo-ctx-get-file-symbols

**Purpose:** List all symbols in a specific file.

**When to use:** When you need to understand the structure of a single source file.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `filePath` | string | ✅ Yes | - | Path to the source file |
| `groupByType` | boolean | ❌ No | false | Group symbols by type (class, function, etc.) |
| `outputFormat` | string | ❌ No | text | Output format: `text`, `json`, `yaml` |

### Returns

List of all symbols in the file, optionally grouped by type:
- Symbol name and type
- Line numbers
- Signatures
- Documentation

### Example Usage

```javascript
// Get all symbols in a file
const fileSymbols = await use_mcp_tool("repo-ctx", "repo-ctx-get-file-symbols", {
  filePath: "./src/services/UserService.java",
  groupByType: true
});
```

---

## Rate Limits

### GitHub
- **Authenticated:** 5,000 requests/hour
- **Unauthenticated:** 60 requests/hour (public repos only)

### GitLab
- **Authenticated:** Varies by instance (typically 600-5000/hour)

**Tip:** Always provide authentication tokens to avoid hitting low rate limits.

---

## Advanced Usage

### Custom Repository Configuration

Add `.repo-ctx.json` or `git_context.json` to your repository:

```json
{
  "description": "Custom description for search results",
  "folders": ["docs/", "tutorials/"],
  "exclude_folders": ["docs/internal/"],
  "exclude_files": ["CONTRIBUTING.md", "CODE_OF_CONDUCT.md"]
}
```

This configuration is automatically detected and used during indexing.

### Pagination Strategy

```javascript
// Get first page
let page = 1;
let hasMore = true;

while (hasMore) {
  const docs = await use_mcp_tool("repo-ctx", "repo-ctx-docs", {
    libraryId: "/mygroup/large-project",
    page: page
  });

  // Process docs...

  // Check if more pages (if < 10 docs returned, likely last page)
  const docCount = extractDocCount(docs);
  hasMore = docCount >= 10;
  page++;
}
```

---

## Tool Naming

All tools use the `repo-ctx-` prefix to indicate they are part of the repo-ctx project and work across **all providers** (GitLab, GitHub, and local Git repositories). The naming emphasizes the multi-provider nature of the tool.

---

## Quick Reference

### Repository Management & Documentation

| Tool | Purpose | Key Parameters | Provider Support |
|------|---------|----------------|------------------|
| `repo-ctx-search` | Exact name search | `libraryName` | All (searches all indexed repos) |
| `repo-ctx-fuzzy-search` | Fuzzy/typo-tolerant search | `query`, `limit` | All (searches all indexed repos) |
| `repo-ctx-index` | Index single repo | `repository`, `provider` | GitLab, GitHub, Local |
| `repo-ctx-index-group` | Index group/org | `group`, `includeSubgroups`, `provider` | GitLab, GitHub (not Local) |
| `repo-ctx-list` | List indexed repos | `provider` (optional) | All (shows all indexed repos, filterable) |
| `repo-ctx-docs` | Get documentation | `libraryId`, `topic`, `page` | All (retrieves any indexed repo) |

### Code Analysis

| Tool | Purpose | Key Parameters | Language Support |
|------|---------|----------------|------------------|
| `repo-ctx-analyze` | Extract symbols from code | `path`, `language`, `symbolType`, `outputFormat` | Python, JS, TS, Java, Kotlin |
| `repo-ctx-search-symbol` | Search for symbols | `path`, `query`, `symbolType`, `outputFormat` | Python, JS, TS, Java, Kotlin |
| `repo-ctx-get-symbol-detail` | Get symbol details | `path`, `symbolName`, `outputFormat` | Python, JS, TS, Java, Kotlin |
| `repo-ctx-get-file-symbols` | List file symbols | `filePath`, `groupByType`, `outputFormat` | Python, JS, TS, Java, Kotlin |

**Provider Configuration:**
- **Local:** No configuration required ✅
- **GitHub public:** No configuration required ✅ (60 req/hr)
- **GitHub private:** Requires `GITHUB_TOKEN` (5000 req/hr)
- **GitLab:** Requires `GITLAB_URL` + `GITLAB_TOKEN`

---

## Further Reading

- [Multi-Provider Guide](../docs/multi-provider-guide.md) - Complete provider configuration guide
- [README](../README.md) - Installation and setup
- [CLI Documentation](../README.md#cli-usage) - Command-line interface
- [Python Library API](../docs/library/api-reference.md) - Use as library

---

**Need help?** See troubleshooting in the [Multi-Provider Guide](../docs/multi-provider-guide.md#troubleshooting).
