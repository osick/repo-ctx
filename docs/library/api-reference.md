# Python API Reference

This reference covers using repo-ctx as a Python library.

For detailed architecture and internals, see [Developer Guide](../dev_guide.md).

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Unified Client (Recommended)](#unified-client-recommended)
4. [Configuration](#configuration)
5. [Repository Context (Legacy)](#repository-context-legacy)
6. [Code Analysis](#code-analysis)
7. [Content Processing](#content-processing)
8. [Service Layer](#service-layer)
9. [Models](#models)
10. [Joern Integration](#joern-integration)
11. [Error Handling](#error-handling)

---

## Installation

```bash
pip install repo-ctx
```

---

## Quick Start

### Modern API (Recommended)

```python
import asyncio
from repo_ctx.client import RepoCtxClient

async def main():
    # Use async context manager
    async with RepoCtxClient() as client:
        # Index a repository
        result = await client.index_repository("fastapi/fastapi", provider="github")
        print(f"Indexed: {result.repository}, documents: {result.documents}")

        # Search libraries
        results = await client.search_libraries("fastapi", fuzzy=True)
        for r in results:
            print(f"  {r.name} (score: {r.score:.2f})")

        # Get documentation
        docs = await client.get_documentation("/fastapi/fastapi", max_tokens=8000)
        print(docs["content"][:500])

asyncio.run(main())
```

### Code Analysis

```python
from repo_ctx.analysis import CodeAnalyzer

analyzer = CodeAnalyzer()
symbols, dependencies = analyzer.analyze_file(code, "service.py")

for symbol in symbols:
    print(f"{symbol.symbol_type.value}: {symbol.name}")
```

---

## Unified Client (Recommended)

The `RepoCtxClient` provides a unified interface for all repo-ctx operations. It supports two modes:

- **Direct mode** (default): Uses service layer directly for best performance
- **HTTP mode**: Uses REST API for remote access

### Creating a Client

```python
from repo_ctx.client import RepoCtxClient, ClientMode

# Direct mode (default) - for CLI/library usage
client = RepoCtxClient()

# With custom config
from repo_ctx import Config
config = Config.load()
client = RepoCtxClient(config=config)

# HTTP mode - for remote API access
client = RepoCtxClient(
    api_url="http://localhost:8000",
    api_key="your-api-key"
)

# Explicit mode selection
client = RepoCtxClient(mode=ClientMode.DIRECT)
```

### Using the Client

```python
# As context manager (recommended)
async with RepoCtxClient() as client:
    libraries = await client.list_libraries()

# Manual lifecycle
client = RepoCtxClient()
await client.connect()
try:
    libraries = await client.list_libraries()
finally:
    await client.close()
```

### Library Operations

```python
async with RepoCtxClient() as client:
    # List all indexed libraries
    libraries = await client.list_libraries()
    libraries = await client.list_libraries(provider="github")

    # Get specific library
    lib = await client.get_library("/fastapi/fastapi")

    # Search libraries (fuzzy by default)
    results = await client.search_libraries("fast", limit=10)
    results = await client.search_libraries("fastapi", fuzzy=False)  # Exact
```

### Indexing Operations

```python
async with RepoCtxClient() as client:
    # Index single repository
    result = await client.index_repository(
        repository="fastapi/fastapi",
        provider="github",      # Optional: auto, github, gitlab, local
        analyze_code=True,      # Default: True
    )
    print(f"Status: {result.status}, Docs: {result.documents}")

    # Index organization/group
    results = await client.index_group(
        group="microsoft",
        provider="github",
        include_subgroups=True,
    )
    for r in results:
        print(f"{r.repository}: {r.status}")
```

### Documentation Operations

```python
async with RepoCtxClient() as client:
    docs = await client.get_documentation(
        library_id="/fastapi/fastapi",
        topic="authentication",         # Filter by topic
        max_tokens=10000,               # Limit for LLM context
        output_mode="standard",         # summary, standard, full
        include=["code", "diagrams"],   # code, symbols, diagrams, tests, examples
    )

    print(docs["content"])
    print(docs["metadata"])
```

### Analysis Operations

```python
async with RepoCtxClient() as client:
    # Analyze code
    result = await client.analyze_code(
        code="def hello(): pass",
        file_path="hello.py",
        language="python",  # Optional: auto-detected
    )
    for sym in result.symbols:
        print(f"{sym.symbol_type.value}: {sym.name}")

    # Search symbols
    symbols = await client.search_symbols("User", symbol_type="class")
```

### Client Data Models

```python
from repo_ctx.client import (
    Library,        # Repository information
    Document,       # Documentation content
    Symbol,         # Code symbol
    SearchResult,   # Search result item
    IndexResult,    # Indexing operation result
    AnalysisResult, # Code analysis result
)

# All models support dict conversion
lib = Library.from_dict({"id": "/owner/repo", "name": "repo", ...})
data = lib.to_dict()
```

---

## Configuration

### Config

```python
from repo_ctx import Config

# From environment variables
config = Config.from_env()

# From YAML file
config = Config.from_yaml("~/.config/repo-ctx/config.yaml")

# Auto-discovery
config = Config.load()

# Direct construction
config = Config(
    github_token="ghp_xxx",
    gitlab_url="https://gitlab.company.com",
    gitlab_token="glpat-xxx",
    storage_path="./data/context.db"
)
```

**Environment Variables:**

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub API token |
| `GITLAB_URL` | GitLab server URL |
| `GITLAB_TOKEN` | GitLab API token |
| `STORAGE_PATH` | SQLite database path |

**Config File Format (YAML):**

```yaml
github:
  token: "${GITHUB_TOKEN}"

gitlab:
  url: "https://gitlab.company.com"
  token: "${GITLAB_TOKEN}"

storage:
  path: "~/.repo-ctx/context.db"
```

---

## Repository Context (Legacy)

> **Note**: For new code, use `RepoCtxClient` instead. `RepositoryContext` is maintained for backwards compatibility.

```python
from repo_ctx import Config, RepositoryContext

config = Config.from_env()
context = RepositoryContext(config)
await context.init()

# Index
await context.index_repository("fastapi", "fastapi", provider_type="github")

# Search
results = await context.fuzzy_search_libraries("fastapi", limit=5)

# Documentation
docs = await context.get_documentation("/fastapi/fastapi")
```

---

## Code Analysis

### CodeAnalyzer

Main analyzer orchestrating Joern and tree-sitter backends.

```python
from repo_ctx.analysis import CodeAnalyzer

# Default: Uses Joern when available
analyzer = CodeAnalyzer()

# Force tree-sitter
analyzer = CodeAnalyzer(use_treesitter=True)

# Custom Joern path
analyzer = CodeAnalyzer(joern_path="/opt/joern")
```

#### analyze_file

```python
symbols, dependencies = analyzer.analyze_file(
    code: str,
    file_path: str
)
# Returns: (list[Symbol], list[str])
```

#### analyze_files

```python
results = analyzer.analyze_files(
    files: dict[str, str]  # {file_path: code}
)
# Returns: dict[str, list[Symbol]]
```

#### Helper Methods

```python
# Aggregate symbols from multiple files
all_symbols = analyzer.aggregate_symbols(results)

# Filter by type
classes = analyzer.filter_symbols_by_type(symbols, SymbolType.CLASS)

# Filter by visibility
public = analyzer.filter_symbols_by_visibility(symbols, "public")

# Find symbol by name
symbol = analyzer.find_symbol(symbols, "UserService")

# Get statistics
stats = analyzer.get_statistics(symbols)
```

### DependencyGraph

```python
from repo_ctx.analysis import DependencyGraph, GraphType

graph_builder = DependencyGraph()

result = graph_builder.build(
    symbols=symbols,
    dependencies=dependencies,
    graph_type=GraphType.CLASS,  # FILE, MODULE, CLASS, FUNCTION, SYMBOL
)

# Export formats
json_output = graph_builder.to_json(result)
dot_output = graph_builder.to_dot(result)
graphml_output = graph_builder.to_graphml(result)
```

---

## Content Processing

### ChunkingService

Split content into optimal chunks for LLM processing.

```python
from repo_ctx.services import ChunkingService

chunking = ChunkingService(default_strategy="semantic")

# Chunk code semantically (respects function/class boundaries)
chunks = chunking.chunk(
    content=code,
    source_file="service.py",
    strategy="semantic",
)

for chunk in chunks:
    print(f"Type: {chunk.chunk_type.value}")
    print(f"Lines: {chunk.start_line}-{chunk.end_line}")
    print(f"Content: {chunk.content[:100]}...")

# Chunk for embeddings (smaller chunks)
chunks = chunking.chunk_for_embedding(content, "doc.md", max_tokens=500)

# Chunk for LLM context (larger chunks)
chunks = chunking.chunk_for_context(content, "doc.md", max_tokens=2000)
```

**Chunking Strategies:**

| Strategy | Best For | Description |
|----------|----------|-------------|
| `semantic` | Code files | Respects functions, classes, methods |
| `markdown` | Documentation | Splits at headings |
| `token_based` | Any text | Respects token limits |
| `fixed_size` | Raw text | Fixed character chunks |

```python
# Direct strategy usage
from repo_ctx.services import SemanticChunking, MarkdownChunking

semantic = SemanticChunking(max_chunk_size=2000)
chunks = semantic.chunk(code, "service.py")

markdown = MarkdownChunking(max_heading_level=2)
chunks = markdown.chunk(docs, "README.md")
```

### EnrichmentService

Enhance content with LLM-powered metadata (with heuristic fallbacks).

```python
from repo_ctx.services import (
    create_service_context,
    EnrichmentService,
    create_llm_service,
)

# Create service context
context = create_service_context()

# With LLM (requires API key)
llm = create_llm_service(context, model="gpt-5-mini", api_key="...")
enrichment = EnrichmentService(context, llm_service=llm)

# Without LLM (uses heuristics)
enrichment = EnrichmentService(context, use_llm=False)
```

#### Enrich Code

```python
metadata = await enrichment.enrich_code(
    code="def authenticate(user, password): ...",
    language="python",
    file_path="auth.py",
)

print(metadata.summary)       # Generated summary
print(metadata.tags)          # ["authentication", "security"]
print(metadata.quality_score) # 0.0-1.0
print(metadata.search_text)   # Optimized for search
```

#### Enrich Symbols

```python
enriched = await enrichment.enrich_symbol(
    name="UserService",
    qualified_name="app.services.UserService",
    symbol_type="class",
    code="class UserService: ...",
    language="python",
)

print(enriched.summary)
print(enriched.tags)
print(enriched.related_concepts)  # ["user management", "service layer"]
```

#### Enrich Documents

```python
enriched = await enrichment.enrich_document(
    content="# Authentication\n\nThis module handles...",
    file_path="docs/auth.md",
    language="markdown",
    chunk_for_embedding=True,
)

print(enriched.summary)
print(enriched.tags)
print(enriched.chunks)  # Pre-chunked for embedding
```

---

## Service Layer

For advanced usage, access the service layer directly.

```python
from repo_ctx.services import (
    create_service_context,
    create_repository_service,
    create_indexing_service,
    create_search_service,
    create_analysis_service,
)

# Create context with storage
context = create_service_context()

# Create services
repo_service = create_repository_service(context)
indexing_service = create_indexing_service(context)
search_service = create_search_service(context)
analysis_service = create_analysis_service(context)

# Use services
repositories = await repo_service.list_repositories()
result = await indexing_service.index_repository("owner/repo")
results = await search_service.search("query")
```

### Available Services

| Service | Purpose |
|---------|---------|
| `RepositoryService` | Manage indexed repositories |
| `IndexingService` | Index repositories |
| `SearchService` | Search repositories and symbols |
| `AnalysisService` | Code analysis operations |
| `ChunkingService` | Content chunking |
| `EnrichmentService` | LLM-enhanced metadata |
| `EmbeddingService` | Vector embeddings (optional) |
| `CombinedSearchService` | Multi-backend search |

---

## Models

### Symbol

```python
from repo_ctx.analysis import Symbol, SymbolType

@dataclass
class Symbol:
    name: str
    qualified_name: str
    symbol_type: SymbolType  # CLASS, FUNCTION, METHOD, INTERFACE, ENUM
    file_path: str
    line_start: int
    line_end: int
    signature: str
    visibility: str          # "public", "private", "protected"
    language: str
    documentation: str
    is_exported: bool
    metadata: dict
```

### Client Models

```python
from repo_ctx.client.models import (
    Library,
    Document,
    Symbol,
    SearchResult,
    IndexResult,
    AnalysisResult,
    SymbolType,
    Visibility,
)

# Library
lib = Library(
    id="/owner/repo",
    name="repo",
    group="owner",
    provider="github",
    description="A repository",
    versions=["v1.0", "v2.0"],
)

# Symbol
sym = Symbol(
    name="UserService",
    qualified_name="app.UserService",
    symbol_type=SymbolType.CLASS,
    file_path="service.py",
    line_start=10,
    line_end=50,
    visibility=Visibility.PUBLIC,
)

# All models support from_dict/to_dict
data = lib.to_dict()
lib2 = Library.from_dict(data)
```

### Chunk

```python
from repo_ctx.services import Chunk, ChunkType

@dataclass
class Chunk:
    content: str
    source_file: str
    start_line: int
    end_line: int
    chunk_type: ChunkType  # CODE, FUNCTION, CLASS, DOCUMENTATION, HEADING, TEXT
    metadata: dict
```

### Enriched Models

```python
from repo_ctx.services import EnrichedMetadata, EnrichedDocument, EnrichedSymbol

@dataclass
class EnrichedMetadata:
    summary: str
    tags: list[str]
    quality_score: float
    search_text: str
    metadata: dict

@dataclass
class EnrichedSymbol:
    name: str
    summary: str
    tags: list[str]
    related_concepts: list[str]
    complexity: str  # "low", "medium", "high"

@dataclass
class EnrichedDocument:
    summary: str
    tags: list[str]
    sections: list[str]
    chunks: list[Chunk]
```

---

## Joern Integration

### JoernAdapter

```python
from repo_ctx.joern import JoernAdapter

adapter = JoernAdapter(joern_path="/opt/joern")

# Check availability
if adapter.is_available():
    version = adapter.get_version()
```

#### analyze_directory

```python
result = adapter.analyze_directory(
    path="./src",
    language="python",
    include_external=False,
)
# Returns: AnalysisResult with symbols, dependencies, errors
```

#### run_query

```python
result = adapter.run_query(
    path="./src",
    query="cpg.method.name.l",
    output_format="text"
)
# Returns: QueryResult with output, parsed_result
```

#### export_graph

```python
result = adapter.export_graph(
    path="./src",
    output_dir="./output",
    representation="cfg",  # ast, cfg, cdg, ddg, pdg, cpg14
    format="dot"           # dot, graphml, neo4jcsv
)
```

---

## Error Handling

```python
from repo_ctx.client import RepoCtxClient

async with RepoCtxClient() as client:
    try:
        result = await client.index_repository("invalid/repo")
    except ValueError as e:
        print(f"Invalid input: {e}")
    except RuntimeError as e:
        print(f"Operation failed: {e}")
```

**Common Exceptions:**

| Exception | Cause |
|-----------|-------|
| `ValueError` | Invalid parameters |
| `RuntimeError` | Client not initialized |
| `FileNotFoundError` | Config or file not found |
| `aiosqlite.Error` | Database errors |
| Provider errors | Network/auth issues |

---

## Further Reading

- [User Guide](../user_guide.md) - Usage examples and best practices
- [Developer Guide](../dev_guide.md) - Architecture and internals
- [Architecture Analysis Guide](../architecture_analysis_guide.md) - DSM, cycles, layers
