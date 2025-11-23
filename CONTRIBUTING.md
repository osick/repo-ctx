# Contributing to repo-ctx

Thank you for your interest in contributing to repo-ctx!

## Development Setup

### Prerequisites

- Python 3.10 or higher
- uv package manager
- GitLab server access (for testing)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/osick/repo-ctx.git
   cd repo-ctx
   ```

2. Install dependencies:
   ```bash
   uv pip install -e .
   uv pip install pytest pytest-cov pytest-asyncio ruff
   ```

3. Configure for testing:
   ```bash
   export GITLAB_URL="https://gitlab.company.internal"
   export GITLAB_TOKEN="your-token"
   ```

## Development Workflow

### Making Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and add tests

3. Run tests:
   ```bash
   pytest tests/ -v --cov=repo_ctx
   ```

4. Lint your code:
   ```bash
   ruff check repo_ctx/
   ```

5. Commit your changes:
   ```bash
   git add .
   git commit -m "Add your feature (#issue-number)"
   ```

6. Push and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

### Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Reference any related issues
4. Wait for review

The test workflow will automatically run on your PR.

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=repo_ctx --cov-report=html

# Run specific test
pytest tests/test_config.py -v
```

### Writing Tests

Place tests in the `tests/` directory:

```python
import pytest
from repo_ctx.config import Config

def test_config_from_env():
    # Test implementation
    pass
```

## Code Style

We use `ruff` for linting:

```bash
# Check code
ruff check repo_ctx/

# Format code
ruff format repo_ctx/
```

## Releasing

Releases are automated via GitHub Actions. See [docs/GITHUB_ACTIONS.md](docs/GITHUB_ACTIONS.md) for details.

### Release Checklist

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md (if exists)
3. Commit: `git commit -m "Bump version to X.Y.Z"`
4. Tag: `git tag vX.Y.Z`
5. Push: `git push origin main && git push origin vX.Y.Z`

GitHub Actions will automatically:
- Build and publish to PyPI
- Create GitHub release
- Generate changelog
- Label referenced issues

## Project Structure

```
repo-ctx/
├── repo_ctx/            # Main package
│   ├── __init__.py
│   ├── __main__.py      # CLI entry point
│   ├── config.py        # Configuration management
│   ├── core.py          # Core functionality
│   ├── mcp_server.py    # MCP server implementation
│   └── storage.py       # Database operations
├── tests/               # Test suite
├── docs/                # Documentation
├── .github/             # GitHub Actions workflows
└── pyproject.toml       # Package metadata
```

## Adding New Features

### MCP Tools

To add a new MCP tool:

1. Define the tool in `mcp_server.py` `list_tools()`:
   ```python
   Tool(
       name="gitlab-your-tool",
       description="What it does",
       inputSchema={...}
   )
   ```

2. Implement in `call_tool()`:
   ```python
   elif name == "gitlab-your-tool":
       result = await context.your_method(arguments)
       return [TextContent(type="text", text=result)]
   ```

3. Add core logic to `core.py`

4. Write tests

### CLI Commands

To add CLI functionality:

1. Add argument to `__main__.py`:
   ```python
   parser.add_argument("--your-command", help="Description")
   ```

2. Handle in `main()` function

3. Test with `uv run repo-ctx --your-command`

## Documentation

Update these files when adding features:

- `README.md` - User-facing features
- `docs/GITHUB_ACTIONS.md` - CI/CD changes
- `docs/EXTENSIONS_ROADMAP.md` - Future plans

## Getting Help

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues and PRs first

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## License

By contributing, you agree that your contributions will be licensed under the Apache-2.0 License.
