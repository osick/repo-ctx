# Quick Release Guide

## Prerequisites (One-time Setup)

1. Set up PyPI token in GitHub:
   - Go to https://pypi.org/manage/account/token/
   - Create token for project `repo-ctx`
   - Add to GitHub: Settings > Secrets > Actions > `PYPI_API_TOKEN`

2. Create PyPI environment:
   - Go to Settings > Environments
   - Create environment named `pypi`

## Release Steps

### 1. Update Version

Edit `pyproject.toml`:
```toml
[project]
version = "0.1.2"  # Increment version
```

### 2. Commit and Tag

```bash
# Commit version bump
git add pyproject.toml
git commit -m "Bump version to 0.1.2"

# Create tag
git tag v0.1.2

# Push
git push origin main
git push origin v0.1.2
```

### 3. Automated Process

GitHub Actions will automatically:
- Build package
- Publish to PyPI
- Create GitHub release with changelog
- Label referenced issues

### 4. Verify

Check:
- PyPI: https://pypi.org/project/repo-ctx/
- GitHub Release: https://github.com/osick/repo-ctx/releases
- Installation: `uvx repo-ctx --help`

## Version Numbering

Follow Semantic Versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

Examples:
- `0.1.0` -> `0.1.1` (bug fix)
- `0.1.1` -> `0.2.0` (new feature)
- `0.2.0` -> `1.0.0` (breaking change)

## Linking Issues

Reference issues in commits:
```bash
git commit -m "Add fuzzy search (#45)"
git commit -m "Fix authentication bug (#123)"
```

These issues will be automatically labeled `released-vX.Y.Z`.

## Pre-Release Checklist

- [ ] All tests passing locally
- [ ] Version updated in `pyproject.toml`
- [ ] Breaking changes documented
- [ ] New features tested

## Rollback

If a release has issues:

1. Create a new patch version with fix
2. Release normally
3. Don't delete tags (breaks PyPI)

## Manual Release (Emergency)

If automation fails:

```bash
# Build
uv build

# Publish
python3 -m twine upload dist/*

# Create release
gh release create v0.1.2 dist/* --generate-notes
```

## Troubleshooting

**Workflow not triggered:**
- Ensure tag starts with `v` (e.g., `v0.1.2`)
- Check Actions tab for errors

**PyPI upload fails:**
- Verify `PYPI_API_TOKEN` is set
- Check token hasn't expired
- Ensure version doesn't already exist

**Release notes empty:**
- Make commits between releases
- Use descriptive commit messages
