# repo-ctx MCP Tools Reference

Complete reference for all MCP tools provided by the repo-ctx server.

---

## Overview

repo-ctx provides **5 MCP tools** for repository documentation indexing and retrieval:

1. **gitlab-search-libraries** - Search for indexed repositories
2. **gitlab-fuzzy-search** - Fuzzy/typo-tolerant search
3. **gitlab-index-repository** - Index a single repository
4. **gitlab-index-group** - Index all repositories in a group/organization
5. **gitlab-get-docs** - Retrieve documentation content

**Note:** Despite the "gitlab-" prefix, all tools support **GitLab, GitHub, and local Git repositories**.

---

## 1. gitlab-search-libraries

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
const results = await use_mcp_tool("repo-ctx", "gitlab-search-libraries", {
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

## 2. gitlab-fuzzy-search

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
const results = await use_mcp_tool("repo-ctx", "gitlab-fuzzy-search", {
  query: "fasapi",  // Typo: missing 't'
  limit: 5
});

// Search by partial name
const results2 = await use_mcp_tool("repo-ctx", "gitlab-fuzzy-search", {
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

To get documentation, use gitlab-get-docs with one of the Library IDs above.
```

---

## 3. gitlab-index-repository

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
await use_mcp_tool("repo-ctx", "gitlab-index-repository", {
  repository: "/home/user/projects/my-app"
});

// Auto-detect provider (Local - relative path)
await use_mcp_tool("repo-ctx", "gitlab-index-repository", {
  repository: "~/projects/my-app"
});

// Auto-detect provider (GitHub - 2 parts)
await use_mcp_tool("repo-ctx", "gitlab-index-repository", {
  repository: "fastapi/fastapi"
});

// Auto-detect provider (GitLab - 3 parts)
await use_mcp_tool("repo-ctx", "gitlab-index-repository", {
  repository: "mygroup/subgroup/project"
});

// Explicitly use local
await use_mcp_tool("repo-ctx", "gitlab-index-repository", {
  repository: "/path/to/repo",
  provider: "local"
});

// Explicitly use GitHub
await use_mcp_tool("repo-ctx", "gitlab-index-repository", {
  repository: "microsoft/vscode",
  provider: "github"
});

// Explicitly use GitLab
await use_mcp_tool("repo-ctx", "gitlab-index-repository", {
  repository: "mygroup/myproject",
  provider: "gitlab"
});
```

### Example Output

```
Successfully indexed fastapi/fastapi using github provider.
You can now search for it using gitlab-fuzzy-search or gitlab-get-docs.
```

### What Gets Indexed

- **Default branch** (main/master)
- **Last 5 tags** (e.g., v1.0.0, v0.9.0, etc.)
- **Documentation files**: .md, .rst, .txt files
- **Configurable** via `.repo-ctx.json` or `git_context.json` in repo

---

## 4. gitlab-index-group

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
await use_mcp_tool("repo-ctx", "gitlab-index-group", {
  group: "microsoft",
  provider: "github"
});

// Index GitLab group with subgroups
await use_mcp_tool("repo-ctx", "gitlab-index-group", {
  group: "mycompany",
  includeSubgroups: true,
  provider: "gitlab"
});

// Index GitLab group without subgroups
await use_mcp_tool("repo-ctx", "gitlab-index-group", {
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

## 5. gitlab-get-docs

**Purpose:** Retrieve documentation content for an indexed repository.

**When to use:** After indexing, when you want to read the actual documentation content.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `libraryId` | string | ✅ Yes | - | Library ID in format `/group/project` or `/group/project/version` |
| `topic` | string | ❌ No | - | Filter by topic (matches file path) |
| `page` | integer | ❌ No | 1 | Page number for pagination |

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
await use_mcp_tool("repo-ctx", "gitlab-get-docs", {
  libraryId: "/fastapi/fastapi"
});

// Get specific version
await use_mcp_tool("repo-ctx", "gitlab-get-docs", {
  libraryId: "/fastapi/fastapi/v0.109.0"
});

// Filter by topic (file path)
await use_mcp_tool("repo-ctx", "gitlab-get-docs", {
  libraryId: "/mygroup/myproject",
  topic: "api"  // Matches files with 'api' in path
});

// Pagination (10 docs per page)
await use_mcp_tool("repo-ctx", "gitlab-get-docs", {
  libraryId: "/mygroup/myproject",
  page: 2
});

// Combine filters
await use_mcp_tool("repo-ctx", "gitlab-get-docs", {
  libraryId: "/mygroup/myproject/v1.0.0",
  topic: "tutorial",
  page: 1
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
await use_mcp_tool("repo-ctx", "gitlab-index-repository", {
  repository: "fastapi/fastapi",
  provider: "github"
});

// Or index entire organization
await use_mcp_tool("repo-ctx", "gitlab-index-group", {
  group: "mycompany",
  provider: "gitlab"
});
```

### 2. Search for Documentation

```javascript
// Fuzzy search to find repositories
const results = await use_mcp_tool("repo-ctx", "gitlab-fuzzy-search", {
  query: "authentication",
  limit: 5
});

// Results show library IDs like /mygroup/auth-service
```

### 3. Retrieve Documentation

```javascript
// Get documentation for found repository
const docs = await use_mcp_tool("repo-ctx", "gitlab-get-docs", {
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
- Solution: Index the repository first using gitlab-index-repository

**"Version not found"**
- Solution: Check available versions with gitlab-search-libraries

**"Path is not a Git repository"**
- Solution: Ensure the path contains a `.git` directory
- Initialize Git: `git init` (if starting a new repo)

---

## Tips & Best Practices

### 1. Search Before Indexing

Use `gitlab-fuzzy-search` to check if a repository is already indexed:

```javascript
const results = await use_mcp_tool("repo-ctx", "gitlab-fuzzy-search", {
  query: "fastapi"
});
// If found, no need to index again
```

### 2. Index in Batches

When indexing many repositories, use `gitlab-index-group` instead of multiple `gitlab-index-repository` calls:

```javascript
// ✅ Better
await use_mcp_tool("repo-ctx", "gitlab-index-group", {
  group: "mycompany",
  provider: "gitlab"
});

// ❌ Slower
await use_mcp_tool("repo-ctx", "gitlab-index-repository", {
  repository: "mycompany/repo1"
});
await use_mcp_tool("repo-ctx", "gitlab-index-repository", {
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
await use_mcp_tool("repo-ctx", "gitlab-get-docs", {
  libraryId: "/mygroup/myproject",
  topic: "api"
});
```

### 5. Explicit Provider for Ambiguous Paths

Use explicit provider when path format is ambiguous:

```javascript
// Without provider, 2 parts = GitHub
await use_mcp_tool("repo-ctx", "gitlab-index-repository", {
  repository: "group/project"  // → GitHub (wrong!)
});

// With explicit provider
await use_mcp_tool("repo-ctx", "gitlab-index-repository", {
  repository: "group/project",
  provider: "gitlab"  // ✅ Correct
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
  const docs = await use_mcp_tool("repo-ctx", "gitlab-get-docs", {
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

## Tool Name Note

All tools have the `gitlab-` prefix for **historical reasons** (repo-ctx was initially GitLab-focused). However, all tools now support **GitLab, GitHub, and local Git repositories**. The prefix may be updated in a future version with backward-compatible aliases.

---

## Quick Reference

| Tool | Purpose | Key Parameters | Provider Support |
|------|---------|----------------|------------------|
| `gitlab-search-libraries` | Exact name search | `libraryName` | All (searches all indexed repos) |
| `gitlab-fuzzy-search` | Fuzzy/typo-tolerant search | `query`, `limit` | All (searches all indexed repos) |
| `gitlab-index-repository` | Index single repo | `repository`, `provider` | GitLab, GitHub, Local |
| `gitlab-index-group` | Index group/org | `group`, `includeSubgroups`, `provider` | GitLab, GitHub (not Local) |
| `gitlab-get-docs` | Get documentation | `libraryId`, `topic`, `page` | All (retrieves any indexed repo) |

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
