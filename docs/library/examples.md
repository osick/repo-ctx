# Usage Examples

## Example 1: Index Multiple Repositories

```python
import asyncio
from repo_ctx.config import Config
from repo_ctx.core import GitLabContext


async def index_all_team_repos():
    """Index all repositories for a team."""
    config = Config.from_env()
    context = GitLabContext(config)
    await context.init()

    repositories = [
        ("backend", "api-server"),
        ("backend", "worker-service"),
        ("frontend", "web-app"),
        ("frontend", "mobile-app"),
    ]

    for group, project in repositories:
        print(f"Indexing {group}/{project}...")
        try:
            await context.index_repository(group, project)
            print(f"  ✓ Success")
        except Exception as e:
            print(f"  ✗ Failed: {e}")


asyncio.run(index_all_team_repos())
```

## Example 2: Search and Display Results

```python
import asyncio
from repo_ctx.config import Config
from repo_ctx.core import GitLabContext


async def search_and_display(query: str):
    """Search for libraries and display formatted results."""
    config = Config.from_env()
    context = GitLabContext(config)
    await context.init()

    print(f"Searching for '{query}'...\n")

    # Fuzzy search
    results = await context.fuzzy_search_libraries(query, limit=10)

    if not results:
        print("No results found.")
        return

    print(f"Found {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        match_indicator = {
            "exact": "🎯",
            "starts_with": "▶️",
            "contains": "📝",
            "fuzzy": "🔍"
        }.get(result.match_type, "")

        print(f"{i}. {match_indicator} {result.name}")
        print(f"   Group: {result.group}")
        print(f"   Score: {result.score:.2f} ({result.match_type})")
        if result.description:
            print(f"   {result.description}")
        print()


# Usage
asyncio.run(search_and_display("fastapi"))
```

## Example 3: Export Documentation to Markdown

```python
import asyncio
from pathlib import Path
from repo_ctx.config import Config
from repo_ctx.core import GitLabContext


async def export_docs_to_file(library_id: str, output_file: str):
    """Export library documentation to a markdown file."""
    config = Config.from_env()
    context = GitLabContext(config)
    await context.init()

    print(f"Retrieving documentation for {library_id}...")

    all_content = []
    page = 1

    while True:
        docs = await context.get_documentation(library_id, page=page)
        content = docs["content"][0]["text"]

        if not content:
            break

        all_content.append(content)
        doc_count = docs["metadata"]["documents_count"]

        if doc_count < 10:  # page_size is 10
            break

        page += 1

    # Write to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(f"# Documentation: {library_id}\n\n")
        f.write("\n\n".join(all_content))

    print(f"✓ Exported to {output_file}")


# Usage
asyncio.run(export_docs_to_file(
    "/mygroup/awesome-project",
    "./exports/awesome-project-docs.md"
))
```

## Example 4: Batch Indexing with Progress

```python
import asyncio
from repo_ctx.config import Config
from repo_ctx.core import GitLabContext


async def batch_index_with_progress(group: str):
    """Index a group with progress reporting."""
    config = Config.from_env()
    context = GitLabContext(config)
    await context.init()

    print(f"Indexing group: {group}")
    print("-" * 50)

    results = await context.index_group(group, include_subgroups=True)

    print(f"\nSummary:")
    print(f"  Total:   {results['total']}")
    print(f"  Success: {len(results['indexed'])}")
    print(f"  Failed:  {len(results['failed'])}")

    if results['indexed']:
        print(f"\n✓ Successfully indexed:")
        for path in results['indexed']:
            print(f"  - {path}")

    if results['failed']:
        print(f"\n✗ Failed to index:")
        for failure in results['failed']:
            print(f"  - {failure['path']}: {failure['error']}")


asyncio.run(batch_index_with_progress("engineering"))
```

## Example 5: Custom Integration - Documentation Bot

```python
import asyncio
from repo_ctx.config import Config
from repo_ctx.core import GitLabContext


class DocumentationBot:
    """Bot that answers questions using indexed documentation."""

    def __init__(self):
        self.config = Config.from_env()
        self.context = GitLabContext(self.config)

    async def initialize(self):
        """Initialize the bot."""
        await self.context.init()

    async def find_docs(self, query: str) -> list[dict]:
        """Find relevant documentation for a query."""
        # Search for matching libraries
        libraries = await self.context.fuzzy_search_libraries(query, limit=3)

        results = []
        for lib in libraries:
            # Get documentation
            docs = await self.context.get_documentation(lib.library_id)
            results.append({
                "library": lib.name,
                "group": lib.group,
                "score": lib.score,
                "content": docs["content"][0]["text"][:500]  # Preview
            })

        return results

    async def answer_question(self, question: str):
        """Answer a question using documentation."""
        print(f"Question: {question}\n")

        # Find relevant docs
        docs = await self.find_docs(question)

        if not docs:
            print("No relevant documentation found.")
            return

        print(f"Found documentation in {len(docs)} libraries:\n")

        for doc in docs:
            print(f"📚 {doc['library']} (score: {doc['score']:.2f})")
            print(f"Preview: {doc['content']}...\n")


# Usage
async def main():
    bot = DocumentationBot()
    await bot.initialize()
    await bot.answer_question("How do I configure authentication?")


asyncio.run(main())
```

## Example 6: Working with Specific Versions

```python
import asyncio
from repo_ctx.config import Config
from repo_ctx.core import GitLabContext


async def compare_versions(library: str, version1: str, version2: str):
    """Compare documentation between two versions."""
    config = Config.from_env()
    context = GitLabContext(config)
    await context.init()

    # Get docs for version 1
    docs_v1 = await context.get_documentation(f"/{library}/{version1}")
    count_v1 = docs_v1["metadata"]["documents_count"]

    # Get docs for version 2
    docs_v2 = await context.get_documentation(f"/{library}/{version2}")
    count_v2 = docs_v2["metadata"]["documents_count"]

    print(f"Library: {library}")
    print(f"\n{version1}:")
    print(f"  Documents: {count_v1}")

    print(f"\n{version2}:")
    print(f"  Documents: {count_v2}")

    print(f"\nDifference: {count_v2 - count_v1:+d} documents")


# Usage
asyncio.run(compare_versions(
    "mygroup/project",
    "v1.0.0",
    "v2.0.0"
))
```

## Example 7: Filtering by Topic

```python
import asyncio
from repo_ctx.config import Config
from repo_ctx.core import GitLabContext


async def get_api_docs(library_id: str):
    """Get only API-related documentation."""
    config = Config.from_env()
    context = GitLabContext(config)
    await context.init()

    # Filter by topic
    docs = await context.get_documentation(library_id, topic="api")

    print(f"API Documentation for {library_id}:")
    print("=" * 50)
    print(docs["content"][0]["text"])


asyncio.run(get_api_docs("/backend/api-server"))
```

## Example 8: Using as a Context Manager

```python
import asyncio
from contextlib import asynccontextmanager
from repo_ctx.config import Config
from repo_ctx.core import GitLabContext


@asynccontextmanager
async def get_context():
    """Context manager for GitLabContext."""
    config = Config.from_env()
    context = GitLabContext(config)
    await context.init()
    try:
        yield context
    finally:
        # Cleanup if needed
        pass


async def main():
    async with get_context() as context:
        results = await context.search_libraries("fastapi")
        for result in results:
            print(result.name)


asyncio.run(main())
```

## Testing Examples

### Unit Testing with repo-ctx

```python
import pytest
import pytest_asyncio
from repo_ctx.config import Config
from repo_ctx.core import GitLabContext


@pytest_asyncio.fixture
async def context():
    """Test fixture for GitLabContext."""
    config = Config(
        gitlab_url="https://test.gitlab.com",
        gitlab_token="test-token",
        storage_path=":memory:"
    )
    context = GitLabContext(config)
    await context.init()
    return context


@pytest.mark.asyncio
async def test_search(context):
    """Test searching for libraries."""
    # This would require mocking GitLab API
    results = await context.search_libraries("test")
    assert isinstance(results, list)
```

## More Examples

For more examples, see:
- [repo-ctx CLI source code](../../repo_ctx/__main__.py) - Real-world CLI usage
- [MCP Server implementation](../../repo_ctx/mcp_server.py) - Integration example
- [Test suite](../../tests/) - Comprehensive test examples
