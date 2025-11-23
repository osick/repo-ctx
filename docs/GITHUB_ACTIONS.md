# GitHub Actions Setup

This document explains the automated workflows for repo-ctx.

## Workflows

### 1. Publish to PyPI and GitHub Release (`publish.yml`)

**Trigger:** Push of version tags (e.g., `v0.1.2`, `v1.0.0`)

**What it does:**
1. Builds the Python package using `uv`
2. Publishes to PyPI
3. Creates a GitHub release with:
   - Auto-generated changelog from commits
   - Distribution files (.whl and .tar.gz)
   - Installation instructions
4. Labels referenced issues with `released-vX.Y.Z`

**Jobs:**
- `build` - Builds distribution packages
- `publish-to-pypi` - Publishes to PyPI
- `github-release` - Creates GitHub release
- `label-release` - Labels issues mentioned in commits

### 2. Test (`test.yml`)

**Trigger:** Push to main, Pull Requests

**What it does:**
1. Runs tests on Python 3.11 and 3.12
2. Lints code with ruff
3. Builds and validates package
4. Uploads coverage to Codecov

**Jobs:**
- `test` - Run pytest with coverage
- `lint` - Run ruff linter
- `build` - Build and validate package

### 3. Sync Labels (`labels.yml`)

**Trigger:** Push to main (when labels.yml changes), Manual dispatch

**What it does:**
- Syncs GitHub labels from `.github/labels.yml` to the repository

## Required GitHub Secrets

### PYPI_API_TOKEN

PyPI API token for publishing packages.

**Setup:**
1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
   - Token name: `github-actions-repo-ctx`
   - Scope: Project: `repo-ctx` (after first manual upload)
3. Copy the token (starts with `pypi-`)
4. Add to GitHub:
   - Go to repository Settings > Secrets and variables > Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Paste the token

### GITHUB_TOKEN

Automatically provided by GitHub Actions. No setup required.

## GitHub Environments

### pypi Environment

**Setup:**
1. Go to repository Settings > Environments
2. Create new environment: `pypi`
3. Add protection rules (optional):
   - Required reviewers
   - Wait timer
   - Deployment branches: Only protected branches

## How to Create a Release

### Automatic Release (Recommended)

1. Update version in `pyproject.toml`:
   ```toml
   [project]
   version = "0.1.2"
   ```

2. Commit the change:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.1.2"
   ```

3. Create and push a tag:
   ```bash
   git tag v0.1.2
   git push origin main
   git push origin v0.1.2
   ```

4. The workflow will automatically:
   - Build the package
   - Publish to PyPI
   - Create GitHub release
   - Label issues

### Manual Release

If you need to manually trigger or publish:

```bash
# Build locally
uv build

# Publish to PyPI
python3 -m twine upload dist/*

# Create GitHub release manually via web UI or gh CLI
gh release create v0.1.2 dist/* --generate-notes
```

## Commit Message Conventions

To automatically link issues in releases, reference them in commits:

```bash
git commit -m "Fix authentication bug (#123)"
git commit -m "Add fuzzy search feature (#45)"
```

These issues will be automatically labeled with `released-vX.Y.Z` when released.

## Labels

### Automatic Labels

The `publish.yml` workflow automatically creates version labels:
- `released-v0.1.0`
- `released-v0.1.1`
- etc.

### Label Categories

Defined in `.github/labels.yml`:

**Type:**
- `type:feature` - New feature
- `type:bugfix` - Bug fix
- `type:refactor` - Code refactoring
- `type:test` - Testing improvements
- `type:docs` - Documentation changes
- `type:chore` - Maintenance tasks

**Priority:**
- `priority:critical` - Critical priority
- `priority:high` - High priority
- `priority:medium` - Medium priority
- `priority:low` - Low priority

**Status:**
- `status:in-progress` - Work in progress
- `status:blocked` - Blocked by another issue
- `status:needs-review` - Needs review
- `status:ready` - Ready to be worked on

**Component:**
- `component:mcp-server` - MCP server component
- `component:cli` - CLI component
- `component:core` - Core library
- `component:docs` - Documentation

## Troubleshooting

### Publish workflow fails

**Error: Invalid credentials**
- Check that `PYPI_API_TOKEN` secret is set correctly
- Verify token hasn't expired
- Ensure token has correct scope

**Error: File already exists**
- Version already published to PyPI
- Update version in `pyproject.toml`
- Create new tag

**Error: 403 Forbidden**
- Token doesn't have permission for this project
- Use a token scoped to the `repo-ctx` project
- Or use a global token for first upload

### Test workflow fails

**Tests not found**
- Ensure tests exist in `tests/` directory
- Install pytest: `uv pip install --system pytest`

**Coverage upload fails**
- Non-critical, workflow will continue
- Can ignore or set up Codecov account

## CI/CD Best Practices

1. Always run tests before merging to main
2. Use semantic versioning (MAJOR.MINOR.PATCH)
3. Keep changelog updated in release notes
4. Tag releases from main branch only
5. Don't delete tags that have been released
6. Reference issues in commit messages for tracking
