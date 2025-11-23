# API Reference

Complete reference for using repo-ctx as a Python library.

## Configuration (`repo_ctx.config`)

### `Config`

Pydantic model for configuration management.

**Attributes:**
- `gitlab_url` (str): GitLab server URL
- `gitlab_token` (str): GitLab API token
- `storage_path` (str): Path to SQLite database (default: `./data/context.db`)

**Class Methods:**

#### `Config.from_env() -> Config`

Load configuration from environment variables.

**Environment Variables:**
- `GITLAB_URL` or `GIT_CONTEXT_GITLAB_URL` (required)
- `GITLAB_TOKEN` or `GIT_CONTEXT_GITLAB_TOKEN` (required)
- `STORAGE_PATH` or `GIT_CONTEXT_STORAGE_PATH` (optional)

**Raises:**
- `ValueError`: If required environment variables are not set

**Example:**
```python
import os
os.environ["GITLAB_URL"] = "https://gitlab.example.com"
os.environ["GITLAB_TOKEN"] = "glpat-token"

config = Config.from_env()
```

#### `Config.from_yaml(path: str) -> Config`

Load configuration from YAML file with environment variable substitution.

**Parameters:**
- `path` (str): Path to YAML config file

**YAML Format:**
```yaml
gitlab:
  url: "https://gitlab.example.com"
  token: "${GITLAB_TOKEN}"  # Environment variable substitution

storage:
  path: "~/.repo-ctx/context.db"
```

**Raises:**
- `FileNotFoundError`: If config file doesn't exist
- `ValueError`: If referenced environment variable is not set

**Example:**
```python
config = Config.from_yaml("~/.config/repo-ctx/config.yaml")
```

#### `Config.load(config_path=None, gitlab_url=None, gitlab_token=None, storage_path=None) -> Config`

Load configuration with priority handling.

**Priority (highest to lowest):**
1. Explicit arguments
2. Specified config file
3. Environment variables
4. Standard config file locations

**Parameters:**
- `config_path` (str, optional): Explicit path to config file
- `gitlab_url` (str, optional): Override GitLab URL
- `gitlab_token` (str, optional): Override GitLab token
- `storage_path` (str, optional): Override storage path

**Raises:**
- `ValueError`: If no valid configuration source found

**Example:**
```python
# Load with auto-discovery
config = Config.load()

# Explicit config file
config = Config.load(config_path="/path/to/config.yaml")

# Override specific values
config = Config.load(
    config_path="config.yaml",
    gitlab_token="override-token"
)
```

#### `Config.find_config_file() -> Optional[Path]`

Find config file in standard locations.

**Search Order:**
1. `./config.yaml`
2. `~/.config/repo-ctx/config.yaml`
3. `~/.repo-ctx/config.yaml`

**Returns:**
- `Path`: Path to found config file
- `None`: If no config file found

---

## Core (`repo_ctx.core`)

### `GitLabContext`

Main class for interacting with GitLab repositories and documentation.

#### `__init__(config: Config)`

Initialize GitLab context.

**Parameters:**
- `config` (Config): Configuration instance

**Example:**
```python
config = Config.from_env()
context = GitLabContext(config)
```

#### `async init()`

Initialize storage (create database schema).

**Must be called before any other operations.**

**Example:**
```python
await context.init()
```

#### `async search_libraries(query: str) -> list[SearchResult]`

Search for libraries by name (exact/partial match).

**Parameters:**
- `query` (str): Search query

**Returns:**
- `list[SearchResult]`: List of matching libraries with scores

**Example:**
```python
results = await context.search_libraries("fastapi")
for result in results:
    print(f"{result.name}: {result.description}")
```

#### `async fuzzy_search_libraries(query: str, limit: int = 10) -> list[FuzzySearchResult]`

Fuzzy search with typo tolerance and ranking.

**Parameters:**
- `query` (str): Search query (can be partial or misspelled)
- `limit` (int): Maximum number of results (default: 10)

**Returns:**
- `list[FuzzySearchResult]`: Ranked list of matches

**Match Types:**
- `exact`: Exact match (score: 1.0)
- `starts_with`: Name starts with query (score: 0.9)
- `contains`: Name contains query (score: 0.8)
- `fuzzy`: Levenshtein distance match (score: 0.4-0.7)

**Example:**
```python
# Will find "myproject" even with typos
results = await context.fuzzy_search_libraries("myprojct", limit=5)
```

#### `async get_documentation(library_id: str, topic: Optional[str] = None, page: int = 1) -> dict`

Retrieve documentation for a library.

**Parameters:**
- `library_id` (str): Format `/group/project` or `/group/project/version`
- `topic` (str, optional): Filter by topic (searches file paths and content)
- `page` (int): Page number (default: 1, page_size: 10)

**Returns:**
```python
{
    "content": [
        {"type": "text", "text": "formatted documentation"}
    ],
    "metadata": {
        "library": "group/project",
        "version": "main",
        "page": 1,
        "documents_count": 5
    }
}
```

**Raises:**
- `ValueError`: If library not found or invalid library_id format

**Example:**
```python
# Get default version docs
docs = await context.get_documentation("/mygroup/project")

# Get specific version
docs = await context.get_documentation("/mygroup/project/v1.0.0")

# Filter by topic
docs = await context.get_documentation("/mygroup/project", topic="api")
```

#### `async index_repository(group: str, project: str)`

Index a GitLab repository.

**Parameters:**
- `group` (str): Group path (can include subgroups: `group/subgroup`)
- `project` (str): Project name

**Example:**
```python
await context.index_repository("mygroup", "myproject")
await context.index_repository("group/subgroup", "project")
```

#### `async index_group(group_path: str, include_subgroups: bool = True) -> dict`

Index all projects in a GitLab group.

**Parameters:**
- `group_path` (str): Group path
- `include_subgroups` (bool): Include subgroups (default: True)

**Returns:**
```python
{
    "total": 15,
    "indexed": ["group/proj1", "group/proj2", ...],
    "failed": [
        {"path": "group/proj3", "error": "Permission denied"}
    ]
}
```

**Example:**
```python
results = await context.index_group("engineering", include_subgroups=True)
print(f"Successfully indexed {len(results['indexed'])} projects")
```

---

## Storage (`repo_ctx.storage`)

### `Storage`

SQLite storage layer (usually accessed through GitLabContext).

#### `__init__(db_path: str)`

Initialize storage.

**Parameters:**
- `db_path` (str): Path to SQLite database file (or `:memory:` for in-memory)

#### `async init_db()`

Create database schema.

---

## Models (`repo_ctx.models`)

### Data Classes

#### `Library`
```python
@dataclass
class Library:
    group_name: str
    project_name: str
    description: str
    default_version: str
    id: Optional[int] = None
    last_indexed: Optional[datetime] = None
```

#### `Version`
```python
@dataclass
class Version:
    library_id: int
    version_tag: str
    commit_sha: str
    id: Optional[int] = None
```

#### `Document`
```python
@dataclass
class Document:
    version_id: int
    file_path: str
    content: str
    content_type: str = "markdown"
    tokens: int = 0
    id: Optional[int] = None
```

#### `SearchResult`
```python
@dataclass
class SearchResult:
    library_id: str  # /group/project
    name: str
    description: str
    versions: list[str]
    score: float = 0.0
```

#### `FuzzySearchResult`
```python
@dataclass
class FuzzySearchResult:
    library_id: str
    name: str
    group: str
    description: str
    score: float
    match_type: str  # "exact", "starts_with", "contains", "fuzzy"
    matched_field: str  # "name", "description", "group"
```

---

## Parser (`repo_ctx.parser`)

### `Parser`

Markdown parsing and filtering utilities.

#### `should_include_file(path: str, config: Optional[dict] = None) -> bool`

Check if file should be indexed.

**Parameters:**
- `path` (str): File path
- `config` (dict, optional): Repository config from `git_context.json`

**Config Format:**
```python
{
    "folders": ["docs", "guides"],  # Include only these folders
    "excludeFolders": ["node_modules", "dist"],  # Exclude these
    "excludeFiles": ["CHANGELOG.md"]  # Exclude specific files
}
```

**Returns:**
- `bool`: True if file should be included

---

## Error Handling

All async methods can raise:
- `ValueError`: Invalid parameters or data
- `FileNotFoundError`: Config file not found
- `aiosqlite.Error`: Database errors
- `gitlab.exceptions.GitlabError`: GitLab API errors

**Example:**
```python
try:
    await context.index_repository("invalid", "project")
except ValueError as e:
    print(f"Invalid repository: {e}")
except Exception as e:
    print(f"Indexing failed: {e}")
```
