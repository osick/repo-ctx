# repo-ctx MCP Tools Reference

Reference for all 18 MCP tools provided by the repo-ctx server. All tools use the `ctx-` prefix. Targets are auto-detected as local paths or indexed repositories based on format.

**Provider support:** GitHub, GitLab, and local Git repositories with auto-detection.
**Supported languages:** Python, JavaScript, TypeScript, Java, Kotlin, Smalltalk, C, C++, Go, Rust, Ruby, PHP, C#, Bash (tree-sitter based).

## Quick Reference

| Category | Tool | Description |
|----------|------|-------------|
| Repository | `ctx-index` | Index a repository or group/organization |
| | `ctx-list` | List all indexed repositories |
| | `ctx-search` | Unified search for repositories or symbols |
| | `ctx-docs` | Retrieve documentation content |
| Analysis | `ctx-analyze` | Analyze code and extract symbols |
| | `ctx-symbol` | Get detailed symbol information |
| | `ctx-symbols` | List all symbols in a file |
| | `ctx-graph` | Generate dependency graphs |
| Architecture | `ctx-dsm` | Generate Design Structure Matrix |
| | `ctx-cycles` | Detect dependency cycles |
| | `ctx-layers` | Detect architectural layers |
| | `ctx-architecture` | Architecture analysis with rule enforcement |
| | `ctx-metrics` | Calculate XS structural complexity metrics |
| Export | `ctx-llmstxt` | Generate compact llms.txt summary |
| | `ctx-dump` | Export repository analysis snapshot |
| CPG (Joern) | `ctx-query` | Run CPGQL query (requires Joern) |
| | `ctx-export` | Export CPG graphs (requires Joern) |
| | `ctx-status` | Show system status and capabilities |

## Tool Details

### ctx-index

Index a repository or organization/group. Provider auto-detection: absolute/relative paths -> local; two-part names (`owner/repo`) -> GitHub; three+ parts -> GitLab.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `repository` | string | Yes | - | Repository path or group name |
| `provider` | string | No | `auto` | `auto`, `github`, `gitlab`, `local` |
| `group` | boolean | No | `false` | Index all repos in a group/org |
| `include_subgroups` | boolean | No | `true` | Include subgroups (GitLab only) |

```javascript
await mcp.call("ctx-index", { repository: "fastapi/fastapi" });
await mcp.call("ctx-index", { repository: "microsoft", group: true, provider: "github" });
await mcp.call("ctx-index", { repository: "/home/user/projects/myapp" });
```

### ctx-list

List all indexed repositories with metadata. Optional `provider` filter: `github`, `gitlab`, `local`.

```javascript
await mcp.call("ctx-list", {});
await mcp.call("ctx-list", { provider: "local" });
```

### ctx-search

Unified search for repositories or symbols. Default mode is fuzzy repository search.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query |
| `mode` | string | No | `repos` | `repos` or `symbols` |
| `target` | string | No | - | Path/repo for symbol search (required when mode=symbols) |
| `exact` | boolean | No | `false` | Exact match (repos only) |
| `limit` | integer | No | `10` | Max results |
| `type` | string | No | - | `class`, `function`, `method`, `interface`, `enum` |
| `lang` | string | No | - | Language filter (symbols only) |

```javascript
await mcp.call("ctx-search", { query: "fastapi" });
await mcp.call("ctx-search", { query: "UserService", mode: "symbols", target: "./src" });
```

### ctx-docs

Retrieve documentation for an indexed repository.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `repository` | string | Yes | - | Repository ID (`/owner/repo` or `/owner/repo/version`) |
| `topic` | string | No | - | Filter by topic |
| `query` | string | No | - | Relevance filter query |
| `max_tokens` | integer | No | - | Maximum tokens to return |
| `mode` | string | No | `standard` | `summary`, `standard`, `full` |
| `format` | string | No | `standard` | `standard` or `llmstxt` |
| `include` | array | No | - | `code`, `symbols`, `diagrams`, `tests`, `examples`, `all` |
| `refresh` | boolean | No | `false` | Force re-analysis of code |

```javascript
await mcp.call("ctx-docs", { repository: "/fastapi/fastapi", max_tokens: 10000, include: ["code", "diagrams"] });
```

### ctx-analyze

Analyze code and extract symbols. Auto-detects local path vs indexed repo.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target` | string | Yes | - | Local path (`./src`) or indexed repo (`/owner/repo`) |
| `lang` | string | No | - | Filter by language |
| `type` | string | No | - | `function`, `class`, `method`, `interface`, `enum` |
| `include_private` | boolean | No | `true` | Include private symbols |
| `refresh` | boolean | No | `false` | Force re-analysis for indexed repos |
| `smalltalk_dialect` | string | No | - | `standard`, `squeak`, `pharo`, `visualworks`, `cincom` |

```javascript
await mcp.call("ctx-analyze", { target: "./src", lang: "python", type: "class" });
```

### ctx-symbol

Get detailed information about a specific symbol including signature, documentation, location, and dependencies.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Symbol name or qualified name (e.g., `MyClass.method`) |
| `target` | string | No | Local path or `/repo-id` (default: `.`) |

```javascript
await mcp.call("ctx-symbol", { name: "UserService.createUser", target: "./src" });
```

### ctx-symbols

List all symbols defined in a specific file.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | string | Yes | - | Path to source file |
| `group_by_type` | boolean | No | `true` | Group symbols by type |

```javascript
await mcp.call("ctx-symbols", { file: "./src/services/user.py" });
```

### ctx-graph

Generate dependency graph showing relationships between code elements.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target` | string | Yes | - | Local path or `/repo-id` |
| `type` | string | No | `class` | `file`, `module`, `class`, `function` |
| `format` | string | No | `json` | `json`, `dot`, `graphml` |
| `depth` | integer | No | - | Maximum traversal depth |

```javascript
await mcp.call("ctx-graph", { target: "./src", type: "module", format: "dot" });
```

### ctx-dsm

Generate a Design Structure Matrix for architecture analysis. A triangular matrix indicates clean layered architecture; cells above the diagonal indicate cycles.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target` | string | Yes | - | Local path or repository ID |
| `type` | string | No | `class` | `file`, `module`, `class`, `function` |
| `format` | string | No | `text` | `text`, `json` |

```javascript
await mcp.call("ctx-dsm", { target: "./src", type: "module" });
```

### ctx-cycles

Detect dependency cycles using Tarjan's algorithm. Returns cycle nodes, edges, impact scores, and breakup suggestions.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target` | string | Yes | - | Local path or repository ID |
| `type` | string | No | `class` | `file`, `module`, `class`, `function` |
| `format` | string | No | `text` | `text`, `json` |

```javascript
await mcp.call("ctx-cycles", { target: "./src", type: "module" });
```

### ctx-layers

Detect architectural layers from dependency structure using topological analysis.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target` | string | Yes | - | Local path or repository ID |
| `type` | string | No | `class` | `file`, `module`, `class`, `function` |
| `format` | string | No | `text` | `text`, `json` |

```javascript
await mcp.call("ctx-layers", { target: "./src", type: "class" });
```

### ctx-architecture

Analyze architecture with layer detection and optional YAML-based rule enforcement. Rules define layer ordering and forbidden dependencies.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target` | string | Yes | - | Local path or repository ID |
| `type` | string | No | `class` | `file`, `module`, `class`, `function` |
| `rules_file` | string | No | - | Path to architecture rules YAML file |
| `rules_yaml` | string | No | - | Inline architecture rules as YAML string |
| `format` | string | No | `text` | `text`, `json` |

```javascript
await mcp.call("ctx-architecture", { target: "./src" });
await mcp.call("ctx-architecture", { target: "./src", rules_file: "./arch-rules.yaml" });
```

### ctx-metrics

Calculate XS (eXcess Structural complexity) metrics. Returns grade (A-F), XS score, component breakdown (cycles, coupling, size, violations), and complexity hotspots.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `target` | string | Yes | - | Local path or repository ID |
| `type` | string | No | `class` | `file`, `module`, `class`, `function` |
| `rules_file` | string | No | - | Path to architecture rules YAML |
| `rules_yaml` | string | No | - | Inline architecture rules YAML |
| `format` | string | No | `text` | `text`, `json` |

```javascript
await mcp.call("ctx-metrics", { target: "./src", type: "module" });
```

### ctx-llmstxt

Generate a compact llms.txt summary for a repository (under 2000 tokens). Returns project overview, key files, quickstart guide, and documentation links.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `repository` | string | Yes | - | Repository ID (`owner/repo` or `group/project`) |
| `include_api` | boolean | No | `true` | Include API overview |
| `include_quickstart` | boolean | No | `true` | Include quickstart guide |

```javascript
await mcp.call("ctx-llmstxt", { repository: "fastapi/fastapi" });
```

### ctx-dump

Export repository analysis to a `.repo-ctx` directory. Creates a static snapshot including metadata, symbols, and architecture analysis.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | Yes | - | Path to local repository |
| `level` | string | No | `medium` | `compact`, `medium`, `full` |
| `output_path` | string | No | - | Custom output directory |
| `force` | boolean | No | `false` | Overwrite existing dump |
| `include_private` | boolean | No | `false` | Include private symbols |
| `use_llm` | boolean | No | `false` | Use LLM for business summary |
| `llm_model` | string | No | - | LLM model to use |

```javascript
await mcp.call("ctx-dump", { path: "./", level: "full", force: true });
```

### ctx-query

Run a CPGQL query on source code. Requires Joern installation.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Path to source directory |
| `query` | string | Yes | CPGQL query string (e.g., `cpg.method.name.l`) |

```javascript
await mcp.call("ctx-query", { path: "./src", query: "cpg.method.name.l" });
```

### ctx-export

Export Code Property Graph to a visualization format. Requires Joern installation.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | Yes | - | Path to source directory |
| `output_dir` | string | Yes | - | Output directory |
| `representation` | string | No | `all` | `all`, `ast`, `cfg`, `cdg`, `ddg`, `pdg`, `cpg14` |
| `format` | string | No | `dot` | `dot`, `graphml`, `graphson`, `neo4jcsv` |

```javascript
await mcp.call("ctx-export", { path: "./src", output_dir: "./cpg-output", representation: "cfg" });
```

### ctx-status

Show system status including Joern availability and supported languages. Optional `component` parameter: `all` (default), `joern`, `languages`.

```javascript
await mcp.call("ctx-status", {});
```

## Typical Workflow

```javascript
// 1. Index
await mcp.call("ctx-index", { repository: "fastapi/fastapi" });
// 2. Search
await mcp.call("ctx-search", { query: "fastapi" });
// 3. Read docs
await mcp.call("ctx-docs", { repository: "/fastapi/fastapi", max_tokens: 10000 });
// 4. Analyze code
await mcp.call("ctx-analyze", { target: "/fastapi/fastapi", lang: "python" });
// 5. Check architecture
await mcp.call("ctx-metrics", { target: "./src" });
await mcp.call("ctx-cycles", { target: "./src", type: "module" });
```

## Configuration

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

**Provider requirements:** Local repos need no config. GitHub public needs no config (60 req/hr). GitHub private requires `GITHUB_TOKEN` (5000 req/hr). GitLab requires `GITLAB_URL` + `GITLAB_TOKEN`.

## Error Messages

| Error | Solution |
|-------|----------|
| "Provider 'gitlab' not configured" | Add `GITLAB_URL` and `GITLAB_TOKEN` to env |
| "Repository not found" | Check path format and provider; verify access permissions |
| "No results found" | Index the repository first with `ctx-index` |
| "Version not found" | Check available versions with `ctx-search` |
| "Path is not a Git repository" | Ensure the path contains a `.git` directory |
| "Joern is not installed" | Install Joern from https://joern.io/ (for ctx-query/ctx-export) |

## Tips

1. **Search before indexing** -- use `ctx-search` to check if a repository is already indexed.
2. **Index in batches** -- use `ctx-index` with `group: true` instead of multiple single-repo calls.
3. **Use specific versions** -- `/owner/repo/v1.0.0` for stable docs vs `/owner/repo` for latest.
4. **Filter by topic** -- `ctx-docs` with `topic` narrows results to relevant sections.
5. **Explicit provider** -- set `provider` when two-part paths could be GitLab or GitHub.
6. **Architecture workflow** -- run `ctx-metrics` for a quick health check, then `ctx-cycles` and `ctx-dsm` to investigate issues.

## Further Reading

- [User Guide](user_guide.md)
- [API Reference](library/api-reference.md)
- [Architecture Analysis Guide](architecture_analysis_guide.md)
