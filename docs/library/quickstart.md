# Library Quickstart Guide

## Installation

```bash
pip install repo-ctx
```

## Basic Usage

### 1. Initialize the Context

```python
import asyncio
from repo_ctx.config import Config
from repo_ctx.core import GitLabContext

# Load configuration from environment variables
config = Config.from_env()

# Or load from a config file
config = Config.from_yaml("~/.config/repo-ctx/config.yaml")

# Or create directly
config = Config(
    gitlab_url="https://gitlab.example.com",
    gitlab_token="glpat-your-token",
    storage_path="./data/context.db"
)

# Create context
context = GitLabContext(config)

# Initialize storage
await context.init()
```

### 2. Index a Repository

```python
# Index a single repository
await context.index_repository("mygroup", "myproject")

# Index an entire group (with subgroups)
results = await context.index_group("mygroup", include_subgroups=True)
print(f"Indexed {len(results['indexed'])} projects")
print(f"Failed: {len(results['failed'])}")
```

### 3. Search for Libraries

```python
# Exact search
results = await context.search_libraries("myproject")
for result in results:
    print(f"{result.name} - {result.description}")
    print(f"Versions: {', '.join(result.versions)}")

# Fuzzy search (typo-tolerant)
results = await context.fuzzy_search_libraries("myprojct", limit=5)
for result in results:
    print(f"{result.name} (score: {result.score}, match: {result.match_type})")
```

### 4. Retrieve Documentation

```python
# Get documentation for a library
docs = await context.get_documentation("/mygroup/myproject")
print(docs["content"][0]["text"])

# Get documentation for specific version
docs = await context.get_documentation("/mygroup/myproject/v1.0.0")

# Filter by topic
docs = await context.get_documentation(
    "/mygroup/myproject",
    topic="api",
    page=1
)

# Access metadata
print(f"Library: {docs['metadata']['library']}")
print(f"Version: {docs['metadata']['version']}")
print(f"Documents: {docs['metadata']['documents_count']}")
```

## Complete Example

```python
import asyncio
from repo_ctx.config import Config
from repo_ctx.core import GitLabContext


async def main():
    # Setup
    config = Config.from_env()
    context = GitLabContext(config)
    await context.init()

    # Index a repository
    print("Indexing repository...")
    await context.index_repository("mygroup", "awesome-project")
    print("✓ Indexing complete")

    # Search
    print("\nSearching for 'awesome'...")
    results = await context.fuzzy_search_libraries("awesome", limit=5)
    for result in results:
        print(f"  - {result.name} (score: {result.score:.2f})")

    # Get documentation
    print("\nRetrieving documentation...")
    docs = await context.get_documentation("/mygroup/awesome-project")
    print(f"Retrieved {docs['metadata']['documents_count']} documents")


if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

- [API Reference](api-reference.md) - Complete API documentation
- [Examples](examples.md) - More usage examples
- [Architecture](architecture.md) - How it works internally
