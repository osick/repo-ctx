# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Your Application                      │
│  (CLI, Bot, Web Service, Custom Integration)             │
└─────────────────────────┬───────────────────────────────┘
                          │
                          │ Import as Library
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  repo_ctx.core                           │
│              GitLabContext (Main API)                    │
├─────────────────────────────────────────────────────────┤
│  - search_libraries()                                    │
│  - fuzzy_search_libraries()                              │
│  - get_documentation()                                   │
│  - index_repository()                                    │
│  - index_group()                                         │
└──────┬────────────────┬──────────────────┬──────────────┘
       │                │                  │
       ▼                ▼                  ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  GitLab API  │ │   Storage    │ │   Parser     │
│   Client     │ │   (SQLite)   │ │  (Markdown)  │
└──────┬───────┘ └──────┬───────┘ └──────────────┘
       │                │
       ▼                ▼
┌──────────────┐ ┌──────────────┐
│   GitLab     │ │  SQLite DB   │
│   Server     │ │  context.db  │
└──────────────┘ └──────────────┘
```

## Core Components

### 1. Configuration Layer (`config.py`)

**Purpose:** Unified configuration management with multiple sources

**Features:**
- Environment variables (`GITLAB_URL`, `GITLAB_TOKEN`)
- YAML files with variable substitution
- Priority-based loading (CLI args > file > env > defaults)
- Auto-discovery of config files

**Usage:**
```python
config = Config.load()  # Auto-discovery
config = Config.from_env()  # Explicit source
config = Config.from_yaml("config.yaml")  # File-based
```

### 2. Storage Layer (`storage.py`)

**Purpose:** SQLite-based persistence and search

**Database Schema:**
```sql
CREATE TABLE libraries (
    id INTEGER PRIMARY KEY,
    group_name TEXT,
    project_name TEXT,
    description TEXT,
    default_version TEXT,
    last_indexed TIMESTAMP,
    UNIQUE(group_name, project_name)
);

CREATE TABLE versions (
    id INTEGER PRIMARY KEY,
    library_id INTEGER,
    version_tag TEXT,
    commit_sha TEXT,
    FOREIGN KEY (library_id) REFERENCES libraries(id)
);

CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    version_id INTEGER,
    file_path TEXT,
    content TEXT,
    content_type TEXT,
    tokens INTEGER,
    FOREIGN KEY (version_id) REFERENCES versions(id)
);
```

**Features:**
- Async operations (aiosqlite)
- Fuzzy search with Levenshtein distance
- Pagination support
- Topic filtering

### 3. GitLab Client (`gitlab_client.py`)

**Purpose:** Wrapper around python-gitlab library

**Responsibilities:**
- Fetch project information
- Read file trees
- Get commit SHAs
- Read repository configuration (`git_context.json`)

### 4. Parser (`parser.py`)

**Purpose:** Markdown processing and filtering

**Features:**
- File inclusion logic based on config
- Code snippet extraction
- Token counting (rough estimation)
- LLM-friendly formatting

**Configuration Example:**
```json
{
    "projectTitle": "My Project",
    "description": "Project documentation",
    "folders": ["docs", "guides"],
    "excludeFolders": ["node_modules", "dist"],
    "excludeFiles": ["CHANGELOG.md"]
}
```

### 5. Core Business Logic (`core.py`)

**Purpose:** Orchestrate all components

**Main Class: `GitLabContext`**

**Workflow for indexing:**
```
1. Get project from GitLab API
2. Read git_context.json (if exists)
3. Save library to database
4. Get file tree for branch/tag
5. Filter files based on config
6. Read and parse markdown files
7. Save documents to database
```

**Workflow for search:**
```
1. Query SQLite database
2. Apply fuzzy matching (Levenshtein)
3. Rank results by score
4. Return sorted results
```

## Data Models (`models.py`)

All models are Python dataclasses for type safety:

- **Library**: Repository metadata
- **Version**: Git reference (branch/tag) with commit SHA
- **Document**: Indexed file content
- **SearchResult**: Search result with versions
- **FuzzySearchResult**: Enhanced search with match metadata

## Async Design

All I/O operations are async for better performance:

```python
# Sequential (slow)
await index_repo("group1", "proj1")
await index_repo("group2", "proj2")

# Parallel (fast)
await asyncio.gather(
    index_repo("group1", "proj1"),
    index_repo("group2", "proj2")
)
```

## Search Algorithm

### Fuzzy Search Scoring

```
Exact match:        score = 1.0
Starts with:        score = 0.9
Contains:           score = 0.8
Description match:  score = 0.6
Group match:        score = 0.5
Levenshtein ≤3:     score = max(0.4, 1.0 - distance/length)
```

### Levenshtein Distance

Used for typo tolerance:
- "projekt" → "project" (distance: 1)
- "fastap" → "fastapi" (distance: 1)
- Limited to distance ≤ 3 for performance

## Performance Considerations

### Database Indexing

```sql
CREATE INDEX idx_libraries_search
    ON libraries(group_name, project_name);

CREATE INDEX idx_documents_version
    ON documents(version_id);
```

### Caching Opportunities

Currently not implemented, but could add:
- In-memory LRU cache for frequently accessed docs
- Redis layer for distributed deployments
- Cached search results

### Batch Operations

The `index_group()` method processes repositories sequentially.
Could be optimized with parallel processing:

```python
# Future optimization
await asyncio.gather(*[
    index_repository(group, proj)
    for proj in projects
])
```

## Extension Points

### 1. Add New Git Providers

Create a `GitProvider` interface:

```python
class GitProvider(ABC):
    @abstractmethod
    async def get_project(self, path: str): ...

    @abstractmethod
    async def read_file(self, project, path, ref): ...
```

Implement for GitHub, Gitea, etc.

### 2. Custom Storage Backends

Replace SQLite with:
- PostgreSQL for larger deployments
- ElasticSearch for advanced search
- Vector database for semantic search

### 3. Enhanced Parsing

Current parser is basic. Could add:
- Better Markdown-to-text conversion
- Code example extraction and syntax highlighting
- Automatic summarization

### 4. Search Improvements

- Semantic search with embeddings
- Query expansion and synonyms
- Search analytics and learning

## Security Considerations

### Token Storage

GitLab tokens are sensitive:
- Never commit tokens to version control
- Use environment variables or encrypted config
- Minimum required scope: `read_api`

### SQL Injection

Prevented by using parameterized queries:
```python
# Safe
await db.execute(
    "SELECT * FROM libraries WHERE name = ?",
    (user_input,)
)

# Unsafe (not used)
await db.execute(f"SELECT * FROM libraries WHERE name = '{user_input}'")
```

### File System

Storage path should be validated:
- Check parent directories exist
- Use absolute paths
- Set proper file permissions

## Testing Architecture

### Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── test_models.py        # Dataclass tests
├── test_storage.py       # Database tests (in-memory)
├── test_config.py        # Config loading tests
├── test_parser.py        # Markdown parsing tests
└── fixtures/             # Sample data
```

### Mocking Strategy

- **GitLab API**: Mock `python-gitlab` responses
- **File System**: Use `tmp_path` fixture
- **Database**: Use temporary files or `:memory:`
- **Environment**: Use `unittest.mock.patch.dict`

## Deployment Patterns

### As a Library

```python
# Direct import
from repo_ctx import GitLabContext, Config
```

### As a CLI Tool

```bash
uvx repo-ctx --index group/project
```

### As an MCP Server

```bash
uvx repo-ctx  # Starts MCP server
```

### As a Web Service

```python
# Future: REST API
from fastapi import FastAPI
from repo_ctx import GitLabContext

app = FastAPI()
context = GitLabContext(Config.from_env())

@app.get("/search")
async def search(q: str):
    return await context.search_libraries(q)
```

## Dependencies

### Core Dependencies

- `mcp>=1.0.0` - MCP protocol
- `python-gitlab>=4.0.0` - GitLab API client
- `markdown-it-py>=3.0.0` - Markdown parsing
- `aiosqlite>=0.19.0` - Async SQLite
- `pyyaml>=6.0` - YAML config parsing
- `pydantic>=2.0.0` - Data validation

### Optional Dependencies (Future)

```toml
[project.optional-dependencies]
github = ["PyGithub>=2.0.0"]
search = ["elasticsearch>=8.0.0"]
web = ["fastapi>=0.100.0", "uvicorn>=0.20.0"]
```

## Future Architecture Evolution

### Phase 1: Current State
- GitLab-only
- SQLite storage
- Basic search
- MCP + CLI interfaces

### Phase 2: Multi-Platform
- Abstract Git providers
- GitHub support
- Gitea support

### Phase 3: Advanced Search
- ElasticSearch integration
- Semantic search with embeddings
- Better ranking

### Phase 4: Scale
- Distributed indexing
- Caching layer (Redis)
- REST API
- Web UI

For more details, see [EXTENSIONS_ROADMAP.md](../EXTENSIONS_ROADMAP.md).
