"""Pytest configuration and shared fixtures."""
import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_db_path():
    """Create a temporary database path."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def sample_library_data():
    """Sample library data for testing."""
    return {
        "group_name": "testgroup",
        "project_name": "testproject",
        "description": "A test project for testing",
        "default_version": "main"
    }


@pytest.fixture
def sample_markdown_content():
    """Sample markdown content for testing."""
    return """# Test Documentation

This is a test document.

## Code Example

```python
def hello():
    return "Hello, World!"
```

## Features

- Feature 1
- Feature 2
- Feature 3
"""


@pytest.fixture
def sample_git_context_config():
    """Sample git_context.json configuration."""
    return {
        "projectTitle": "Test Project",
        "description": "Test documentation",
        "folders": ["docs", "guides"],
        "excludeFolders": ["node_modules", "dist"],
        "excludeFiles": ["CHANGELOG.md"]
    }
