# Testing Guide: Hands-On Walkthrough

This guide walks you through testing all main capabilities of repo-ctx using three real repositories of different sizes. Follow this step-by-step to verify your installation and learn the features.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Test Repositories](#test-repositories)
3. [Small Repository: httpie/cli](#small-repository-httpiecli)
4. [Medium Repository: pallets/flask](#medium-repository-palletsflask)
5. [Large Repository: microsoft/typescript](#large-repository-microsofttypescript)
6. [Local Repository Testing](#local-repository-testing)
7. [Verification Checklist](#verification-checklist)

---

## Prerequisites

### Installation

```bash
# Install repo-ctx
pip install repo-ctx

# Or use without installing
uvx repo-ctx --version
```

### Optional: Joern Installation

For full code analysis capabilities (12 languages vs 5):

```bash
# Install Java 19+
sudo apt install openjdk-21-jdk  # Ubuntu/Debian
# or
brew install openjdk@21          # macOS

# Install Joern
curl -L "https://github.com/joernio/joern/releases/latest/download/joern-install.sh" | bash
export PATH="$HOME/bin/joern:$PATH"
```

### Configuration (Optional)

For higher rate limits on GitHub:

```bash
export GITHUB_TOKEN="ghp_your_token"
```

### Verify Setup

```bash
repo-ctx status
```

Expected output shows:
- Version info
- Joern availability (optional)
- Provider status
- Database location

---

## Test Repositories

| Size | Repository | Files | Languages | Use Case |
|------|------------|-------|-----------|----------|
| Small | `httpie/cli` | ~50 | Python | HTTP client CLI |
| Medium | `pallets/flask` | ~200 | Python | Web framework |
| Large | `microsoft/typescript` | ~3000+ | TypeScript | Programming language |

---

## Small Repository: httpie/cli

**Purpose**: Quick verification of basic features (~2-3 minutes)

### Step 1: Index the Repository

```bash
repo-ctx index httpie/cli
```

Expected output:
```
Indexing httpie/cli...
✓ Indexed 1 version (main branch)
✓ 45 documents processed
✓ 128 symbols extracted
```

### Step 2: List Indexed Repositories

```bash
repo-ctx list
```

Expected output:
```
Indexed Repositories:
  /httpie/cli (github) - 1 version
```

### Step 3: Search for Symbols

```bash
repo-ctx search "request" -s /httpie/cli
```

Expected output shows functions/classes containing "request".

### Step 4: Get Documentation

```bash
repo-ctx docs /httpie/cli
```

Expected output: README content and key documentation.

### Step 5: Analyze Code Structure

```bash
repo-ctx analyze /httpie/cli --output json | head -50
```

Expected output: Symbol list with classes, functions, methods.

### Step 6: Generate Dependency Graph

```bash
repo-ctx graph /httpie/cli --type class --format dot > httpie_deps.dot
```

View with Graphviz:
```bash
dot -Tpng httpie_deps.dot -o httpie_deps.png
```

### Step 7: Search Across Repositories

```bash
repo-ctx search "httpie"
```

Expected output: Fuzzy match results including the indexed repo.

### Verification Checklist (Small)

- [ ] Repository indexed successfully
- [ ] Listed in `repo-ctx list`
- [ ] Symbol search returns results
- [ ] Documentation retrieved
- [ ] Code analysis shows symbols
- [ ] Dependency graph generated

---

## Medium Repository: pallets/flask

**Purpose**: Full feature testing with realistic codebase (~5-10 minutes)

### Step 1: Index with Progress Tracking

```bash
repo-ctx index pallets/flask -v
```

Verbose output shows:
- Version detection
- File processing progress
- Symbol extraction stats

### Step 2: Search for Specific Patterns

```bash
# Search for classes
repo-ctx search "Blueprint" -s /pallets/flask --type class

# Search for functions
repo-ctx search "route" -s /pallets/flask --type function

# Limit results
repo-ctx search "app" -s /pallets/flask --limit 10
```

### Step 3: Get Symbol Details

```bash
# Find a specific symbol
repo-ctx search "Flask" -s /pallets/flask --type class

# Get detailed information (use the qualified name from search)
repo-ctx analyze /pallets/flask --symbol "flask.Flask"
```

### Step 4: Documentation with Filtering

```bash
# Get all documentation
repo-ctx docs /pallets/flask

# Filter by topic
repo-ctx docs /pallets/flask --topic "routing"

# Include code examples
repo-ctx docs /pallets/flask --include examples

# Full output with diagrams
repo-ctx docs /pallets/flask --include all
```

### Step 5: Architecture Analysis

```bash
# Generate class dependency graph
repo-ctx graph /pallets/flask --type class

# Generate module dependency graph
repo-ctx graph /pallets/flask --type module --format json > flask_modules.json

# DSM (Design Structure Matrix)
repo-ctx analyze /pallets/flask --dsm
```

### Step 6: JSON Output for Scripting

```bash
# List as JSON
repo-ctx -o json list

# Search as JSON
repo-ctx -o json search "flask" | jq '.results[] | {name, score}'

# Analyze as JSON
repo-ctx -o json analyze /pallets/flask | jq '.symbols | length'
```

### Step 7: CPGQL Query (Requires Joern)

```bash
# Find all public methods
repo-ctx query /pallets/flask "cpg.method.isPublic.name.l"

# Find all imports
repo-ctx query /pallets/flask "cpg.imports.code.l"
```

### Verification Checklist (Medium)

- [ ] Verbose indexing shows progress
- [ ] Symbol search with type filter works
- [ ] Documentation filtering by topic works
- [ ] Architecture analysis (DSM) runs
- [ ] JSON output parses correctly
- [ ] CPGQL queries execute (if Joern installed)

---

## Large Repository: microsoft/typescript

**Purpose**: Performance testing and advanced features (~15-30 minutes)

### Step 1: Index with Analysis

```bash
# Full indexing with code analysis
repo-ctx index microsoft/typescript -v
```

Note: Large repos take longer. Progress is shown in verbose mode.

### Step 2: Explore Repository Structure

```bash
# Get llms.txt summary (compact context for LLMs)
repo-ctx docs /microsoft/typescript --format llmstxt

# Get structured documentation
repo-ctx docs /microsoft/typescript --output-mode summary
```

### Step 3: Symbol Navigation

```bash
# Find main entry points
repo-ctx search "createProgram" -s /microsoft/typescript

# Search with qualified names
repo-ctx search "ts.createProgram" -s /microsoft/typescript

# Find interfaces
repo-ctx search "CompilerOptions" -s /microsoft/typescript --type interface
```

### Step 4: Dependency Analysis

```bash
# Module-level dependencies
repo-ctx graph /microsoft/typescript --type module --depth 2

# File-level dependencies
repo-ctx graph /microsoft/typescript --type file --format graphml > ts_files.graphml
```

### Step 5: Cycle Detection

```bash
# Detect circular dependencies
repo-ctx analyze /microsoft/typescript --cycles

# Get breakup suggestions
repo-ctx analyze /microsoft/typescript --cycles --suggestions
```

### Step 6: Layered Architecture Analysis

```bash
# Detect architectural layers
repo-ctx analyze /microsoft/typescript --layers

# Check layer violations
repo-ctx analyze /microsoft/typescript --layer-violations
```

### Step 7: Semantic Search (Requires GenAI)

```bash
# Enable GenAI first
export GENAI_ENABLED=true
export GENAI_API_KEY="your-key"

# Semantic search for concepts
repo-ctx search "type inference algorithm" -s /microsoft/typescript --semantic
```

### Step 8: Export CPG (Requires Joern)

```bash
# Export full Code Property Graph
repo-ctx export /microsoft/typescript --format neo4jcsv --output ./typescript-cpg/

# Export specific representation
repo-ctx export /microsoft/typescript --representation cfg --format dot
```

### Verification Checklist (Large)

- [ ] Large repo indexing completes
- [ ] llms.txt generation works
- [ ] Symbol search performs well
- [ ] Dependency graph generation works
- [ ] Cycle detection identifies cycles
- [ ] Layer analysis provides insights
- [ ] Semantic search returns relevant results (if GenAI enabled)
- [ ] CPG export completes (if Joern installed)

---

## Local Repository Testing

### Step 1: Index a Local Project

```bash
# Clone a project or use your own
git clone https://github.com/pallets/click.git /tmp/click

# Index it
repo-ctx index /tmp/click
```

### Step 2: Analyze Without Indexing

```bash
# Direct analysis (no indexing required)
repo-ctx analyze /tmp/click

# Analyze specific directory
repo-ctx analyze /tmp/click/src

# Filter by language
repo-ctx analyze /tmp/click --language python
```

### Step 3: Compare Local vs Indexed

```bash
# Local path (filesystem)
repo-ctx analyze ./my-project

# Indexed path (starts with /)
repo-ctx analyze /owner/repo
```

### Step 4: Watch for Changes

```bash
# Re-index after changes
repo-ctx index /tmp/click --refresh
```

---

## MCP Server Testing

### Step 1: Start MCP Server

```bash
repo-ctx --mcp
```

### Step 2: Test with Claude Desktop

Configure in Claude Desktop settings:

```json
{
  "mcpServers": {
    "repo-ctx": {
      "command": "uvx",
      "args": ["repo-ctx", "--mcp"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxx"
      }
    }
  }
}
```

### Step 3: Test MCP Tools

In Claude, try:
- "Search for repositories about authentication"
- "Index the fastapi/fastapi repository"
- "Show me the documentation for /pallets/flask"
- "Analyze the code structure of /httpie/cli"
- "Generate a dependency graph for /microsoft/typescript"

---

## API Server Testing

### Step 1: Start API Server

```bash
uvicorn repo_ctx.api:app --reload --port 8000
```

### Step 2: Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# List repositories
curl http://localhost:8000/api/v1/repositories

# Search
curl "http://localhost:8000/api/v1/search?query=flask"

# Get documentation
curl http://localhost:8000/api/v1/docs/pallets/flask
```

### Step 3: View API Documentation

Open in browser: http://localhost:8000/docs

---

## Verification Checklist

### Core Features

| Feature | Small | Medium | Large |
|---------|-------|--------|-------|
| Index repository | [ ] | [ ] | [ ] |
| List repositories | [ ] | [ ] | [ ] |
| Search repositories | [ ] | [ ] | [ ] |
| Search symbols | [ ] | [ ] | [ ] |
| Get documentation | [ ] | [ ] | [ ] |
| Analyze code | [ ] | [ ] | [ ] |
| Generate graph | [ ] | [ ] | [ ] |

### Advanced Features

| Feature | Test Status |
|---------|-------------|
| JSON/YAML output | [ ] |
| Verbose mode | [ ] |
| Local repository | [ ] |
| Architecture analysis (DSM) | [ ] |
| Cycle detection | [ ] |
| Layer detection | [ ] |
| CPGQL queries (Joern) | [ ] |
| CPG export (Joern) | [ ] |
| Semantic search (GenAI) | [ ] |
| MCP server | [ ] |
| API server | [ ] |

### Performance Benchmarks

Record your results:

| Repository | Index Time | Symbol Count | Memory Usage |
|------------|------------|--------------|--------------|
| httpie/cli | ___s | ___ | ___MB |
| pallets/flask | ___s | ___ | ___MB |
| microsoft/typescript | ___min | ___ | ___MB |

---

## Troubleshooting

### "Repository not found"

```bash
# Check provider
repo-ctx -p github index owner/repo

# Verify access
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/owner/repo
```

### "Rate limit exceeded"

```bash
# Use authenticated requests
export GITHUB_TOKEN="ghp_xxx"
```

### "Analysis failed"

```bash
# Check Joern installation
joern --version

# Fall back to tree-sitter
repo-ctx analyze ./path --no-joern
```

### "Out of memory"

```bash
# For large repos, increase heap
export JAVA_OPTS="-Xmx8g"
```

---

## Next Steps

After completing this guide:

1. Read the [User Guide](user_guide.md) for more usage patterns
2. Explore the [Configuration Guide](configuration.md) for customization
3. Check the [API Reference](library/api-reference.md) for programmatic usage
4. Review [Architecture Analysis Guide](architecture_analysis_guide.md) for advanced features
