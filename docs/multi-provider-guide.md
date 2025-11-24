# Multi-Provider Support Guide

## Overview

`repo-ctx` supports indexing and searching repositories from multiple Git platforms:

- **GitLab** - Self-hosted or GitLab.com
- **GitHub** - GitHub.com or GitHub Enterprise
- **Auto-detection** - Automatically determines provider from repository path format

You can configure one or both providers simultaneously and choose which to use when indexing.

## Configuration

### Environment Variables

Configure providers using environment variables (supports both plain and `GIT_CONTEXT_` prefixed versions):

```bash
# GitLab (optional)
export GITLAB_URL="https://gitlab.company.com"
export GITLAB_TOKEN="glpat-xxx"

# GitHub (optional)
export GITHUB_URL="https://api.github.com"  # Optional, defaults to public GitHub
export GITHUB_TOKEN="ghp_xxx"                # Optional for public repos

# Storage
export STORAGE_PATH="~/.repo-ctx/context.db"
```

**Note:** At least one provider must be configured (GitLab or GitHub).

### Config File

Create `~/.config/repo-ctx/config.yaml`:

```yaml
gitlab:
  url: "https://gitlab.company.com"
  token: "${GITLAB_TOKEN}"

github:
  url: "https://api.github.com"      # Optional, defaults to public GitHub
  token: "${GITHUB_TOKEN}"            # Optional for public repos

storage:
  path: "~/.repo-ctx/context.db"
```

### Configuration Scenarios

#### Scenario 1: GitLab Only (Backward Compatible)

```bash
export GITLAB_URL="https://gitlab.company.com"
export GITLAB_TOKEN="glpat-xxx"
# Works exactly as before - GitLab is the default provider
```

#### Scenario 2: GitHub Only

```bash
export GITHUB_TOKEN="ghp_xxx"
# GitHub becomes the default provider
```

#### Scenario 3: Both Providers

```bash
export GITLAB_URL="https://gitlab.internal.com"
export GITLAB_TOKEN="glpat-xxx"
export GITHUB_TOKEN="ghp_xxx"
# GitLab is default, GitHub available via --provider flag
```

#### Scenario 4: GitHub Public Repos Only

```bash
# No configuration needed for public GitHub repos!
# Can index public repositories without authentication
# (subject to 60 requests/hour rate limit)
```

## CLI Usage

### Provider Selection

Use the `--provider` flag to explicitly choose which provider to use:

```bash
# Auto-detect provider from path format (default)
uv run repo-ctx --index owner/repo

# Explicitly use GitLab
uv run repo-ctx --index group/project --provider gitlab

# Explicitly use GitHub
uv run repo-ctx --index owner/repo --provider github
```

### Auto-Detection Rules

When `--provider` is not specified or set to `auto`, the provider is detected from path format:

- **2 parts** (`owner/repo`) → GitHub
- **3+ parts** (`group/subgroup/project`) → GitLab
- If both providers are configured, GitLab is the default

### Indexing Examples

#### Index from GitHub

```bash
# Public repository (no token needed)
export GITHUB_URL="https://api.github.com"
uv run repo-ctx --index fastapi/fastapi

# Private repository (token required)
export GITHUB_TOKEN="ghp_xxx"
uv run repo-ctx --index myorg/private-repo

# With explicit provider selection
uv run repo-ctx --index fastapi/fastapi --provider github
```

#### Index from GitLab

```bash
export GITLAB_URL="https://gitlab.company.com"
export GITLAB_TOKEN="glpat-xxx"

# Nested groups supported
uv run repo-ctx --index group/subgroup/project

# With explicit provider selection
uv run repo-ctx --index group/project --provider gitlab
```

#### Index from Both Providers

```bash
# Configure both
export GITLAB_URL="https://gitlab.internal.com"
export GITLAB_TOKEN="glpat-xxx"
export GITHUB_TOKEN="ghp_xxx"

# Index from GitLab
uv run repo-ctx --index mygroup/myproject --provider gitlab

# Index from GitHub
uv run repo-ctx --index fastapi/fastapi --provider github

# Auto-detect (2 parts = GitHub, 3+ parts = GitLab)
uv run repo-ctx --index owner/repo              # → GitHub
uv run repo-ctx --index group/subgroup/project  # → GitLab
```

### GitHub Enterprise

```bash
export GITHUB_URL="https://github.company.com/api/v3"
export GITHUB_TOKEN="ghp_enterprise_token"

uv run repo-ctx --index myorg/myrepo
```

### Provider-Specific CLI Arguments

You can also pass provider credentials directly as CLI arguments:

```bash
# GitHub
uv run repo-ctx \
  --github-token ghp_xxx \
  --index owner/repo \
  --provider github

# GitLab
uv run repo-ctx \
  --gitlab-url https://gitlab.company.com \
  --gitlab-token glpat-xxx \
  --index group/project \
  --provider gitlab

# Both (specify which to use with --provider)
uv run repo-ctx \
  --gitlab-url https://gitlab.company.com \
  --gitlab-token glpat-xxx \
  --github-token ghp_xxx \
  --index owner/repo \
  --provider github
```

## MCP Server Usage

### Basic Setup with Both Providers

Add to MCP settings (e.g., `~/.config/claude/mcp.json`):

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

### MCP Tools with Provider Parameter

All indexing tools now support an optional `provider` parameter:

#### gitlab-index-repository

Index a single repository from GitLab or GitHub:

```json
{
  "name": "gitlab-index-repository",
  "arguments": {
    "repository": "owner/repo",
    "provider": "github"  // "gitlab", "github", or "auto" (default)
  }
}
```

**Examples:**

```javascript
// Auto-detect from path format
await use_mcp_tool("repo-ctx", "gitlab-index-repository", {
  repository: "fastapi/fastapi"  // 2 parts → GitHub
});

// Explicit GitHub
await use_mcp_tool("repo-ctx", "gitlab-index-repository", {
  repository: "microsoft/vscode",
  provider: "github"
});

// Explicit GitLab
await use_mcp_tool("repo-ctx", "gitlab-index-repository", {
  repository: "group/subgroup/project",
  provider: "gitlab"
});
```

#### gitlab-index-group

Index all repositories in a GitLab group or GitHub organization:

```json
{
  "name": "gitlab-index-group",
  "arguments": {
    "group": "myorg",
    "includeSubgroups": true,  // Only works with GitLab
    "provider": "github"  // "gitlab", "github", or "auto"
  }
}
```

**Examples:**

```javascript
// Index GitHub organization
await use_mcp_tool("repo-ctx", "gitlab-index-group", {
  group: "microsoft",
  provider: "github"
});

// Index GitLab group with subgroups
await use_mcp_tool("repo-ctx", "gitlab-index-group", {
  group: "mygroup",
  includeSubgroups: true,
  provider: "gitlab"
});
```

### Search and Documentation Tools

Search and documentation retrieval tools work across all indexed repositories regardless of provider:

```javascript
// Search works across GitLab and GitHub repositories
await use_mcp_tool("repo-ctx", "gitlab-fuzzy-search", {
  query: "fastapi",
  limit: 10
});

// Get documentation (works for any indexed repo)
await use_mcp_tool("repo-ctx", "gitlab-get-docs", {
  libraryId: "/fastapi/fastapi"  // GitHub repo
});

await use_mcp_tool("repo-ctx", "gitlab-get-docs", {
  libraryId: "/mygroup/myproject"  // GitLab repo
});
```

## Python Library Usage

### Initialize with Multiple Providers

```python
import asyncio
from repo_ctx.config import Config
from repo_ctx.core import RepositoryContext

async def main():
    # Configure both providers
    config = Config(
        gitlab_url="https://gitlab.company.com",
        gitlab_token="glpat-xxx",
        github_url="https://api.github.com",
        github_token="ghp_xxx",
        storage_path="~/.repo-ctx/context.db"
    )

    # Or load from environment
    # config = Config.from_env()

    ctx = RepositoryContext(config)
    await ctx.init()

    # Index from GitLab
    await ctx.index_repository("mygroup", "myproject", provider_type="gitlab")

    # Index from GitHub
    await ctx.index_repository("fastapi", "fastapi", provider_type="github")

    # Auto-detect provider
    await ctx.index_repository("owner", "repo")  # → GitHub (2 parts)
    await ctx.index_repository("group", "subgroup/project")  # → GitLab (3 parts)

    # Search across all indexed repos
    results = await ctx.fuzzy_search_libraries("fastapi", limit=5)
    for result in results:
        print(f"{result.name} (score: {result.score})")

asyncio.run(main())
```

### Provider-Specific Operations

```python
# Index entire GitHub organization
results = await ctx.index_group(
    "microsoft",
    include_subgroups=False,
    provider_type="github"
)

# Index GitLab group with subgroups
results = await ctx.index_group(
    "mygroup",
    include_subgroups=True,
    provider_type="gitlab"
)

print(f"Indexed: {len(results['indexed'])} repositories")
print(f"Failed: {len(results['failed'])} repositories")
```

### Check Available Providers

```python
# See which providers are configured
print(f"Available providers: {list(ctx.providers.keys())}")
print(f"Default provider: {ctx.default_provider}")

# Get specific provider instance
gitlab_provider = ctx.get_provider("gitlab")
github_provider = ctx.get_provider("github")
```

## Features Comparison

| Feature | GitLab | GitHub | Notes |
|---------|--------|--------|-------|
| **Repository Access** | ✅ | ✅ | Both support public & private |
| **File Tree** | ✅ | ✅ | Recursive tree traversal |
| **File Reading** | ✅ | ✅ | UTF-8 with base64 decoding |
| **Config Files** | ✅ | ✅ | Multiple filename variants |
| **Tags** | ✅ | ✅ | Limit to N most recent |
| **Group/Org Listing** | ✅ | ✅ | List all repos in group/org |
| **Nested Groups** | ✅ | ❌ | GitLab supports subgroups |
| **Enterprise** | ✅ | ✅ | Both support self-hosted |
| **Auth** | Required | Optional* | *Optional for public GitHub repos |
| **Rate Limiting** | 5000/hr | 5000/hr (auth)<br>60/hr (unauth) | Both handled gracefully |

## Error Handling

### Provider-Specific Errors

```python
from repo_ctx.providers import (
    ProviderNotFoundError,
    ProviderAuthError,
    ProviderRateLimitError,
    ProviderError
)

try:
    await ctx.index_repository("owner", "repo", provider_type="github")
except ProviderNotFoundError:
    print("Repository doesn't exist or is private")
except ProviderAuthError:
    print("Invalid credentials or no access")
except ProviderRateLimitError:
    print("Rate limit exceeded")
except ProviderError as e:
    print(f"Provider error: {e}")
```

### Configuration Validation

```python
try:
    config = Config.from_env()
except ValueError as e:
    print(f"Configuration error: {e}")
    # Error message explains which providers need to be configured
```

## Troubleshooting

### "At least one provider must be configured"

**Problem:** Neither GitLab nor GitHub credentials are set.

**Solution:** Configure at least one provider:

```bash
# Option 1: GitHub only
export GITHUB_TOKEN="ghp_xxx"

# Option 2: GitLab only
export GITLAB_URL="https://gitlab.company.com"
export GITLAB_TOKEN="glpat-xxx"

# Option 3: Both
export GITLAB_URL="https://gitlab.company.com"
export GITLAB_TOKEN="glpat-xxx"
export GITHUB_TOKEN="ghp_xxx"
```

### "Provider 'github' not configured"

**Problem:** Trying to use GitHub provider but credentials not set.

**Solution:** Set GitHub credentials:

```bash
export GITHUB_TOKEN="ghp_xxx"
```

### GitHub Rate Limit (60/hour)

**Problem:** Indexing public GitHub repos without authentication hits rate limit.

**Solution:** Provide a GitHub token to increase limit to 5000/hour:

```bash
export GITHUB_TOKEN="ghp_xxx"
```

### Wrong Provider Used

**Problem:** Auto-detection chooses wrong provider.

**Solution:** Use explicit `--provider` flag:

```bash
uv run repo-ctx --index owner/repo --provider github
```

## Migration Guide

### For Existing GitLab-Only Users

**No changes required!** Everything works as before:

```bash
# Existing setup continues to work
export GITLAB_URL="https://gitlab.company.com"
export GITLAB_TOKEN="glpat-xxx"
uv run repo-ctx --index mygroup/myproject
```

### Adding GitHub Support

To add GitHub support to existing GitLab setup:

```bash
# Keep existing GitLab config
export GITLAB_URL="https://gitlab.company.com"
export GITLAB_TOKEN="glpat-xxx"

# Add GitHub config
export GITHUB_TOKEN="ghp_xxx"

# Now you can index from both
uv run repo-ctx --index mygroup/project --provider gitlab
uv run repo-ctx --index owner/repo --provider github
```

## Best Practices

### 1. Use Explicit Provider Selection for Production

While auto-detection works well, use explicit `--provider` in scripts:

```bash
#!/bin/bash
# Production indexing script
uv run repo-ctx --index company/backend --provider gitlab
uv run repo-ctx --index fastapi/fastapi --provider github
```

### 2. Token Security

Store tokens in environment variables or secure secrets management:

```bash
# Load from secure location
export GITLAB_TOKEN=$(cat ~/.secrets/gitlab-token)
export GITHUB_TOKEN=$(cat ~/.secrets/github-token)
```

### 3. Rate Limit Management

For large organizations, index in batches and handle rate limits:

```python
from repo_ctx.providers import ProviderRateLimitError
import asyncio

async def index_with_retry(ctx, group, project, provider):
    for attempt in range(3):
        try:
            await ctx.index_repository(group, project, provider_type=provider)
            return
        except ProviderRateLimitError:
            print(f"Rate limit hit, waiting 60s...")
            await asyncio.sleep(60)
```

### 4. Monitor Provider Availability

Check which providers are available at runtime:

```python
ctx = RepositoryContext(config)
await ctx.init()

if "github" in ctx.providers:
    print("GitHub provider available")
if "gitlab" in ctx.providers:
    print("GitLab provider available")
```

## Next Steps

- [CLI Reference](../README.md#cli-usage) - Complete CLI documentation
- [MCP Server Setup](../README.md#run-as-mcp-server) - MCP server configuration
- [Python Library API](library/api-reference.md) - Full API documentation
- [Architecture Guide](library/architecture.md) - How multi-provider support works internally
