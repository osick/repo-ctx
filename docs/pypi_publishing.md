# Publishing to PyPI

Quick reference for publishing repo-ctx and repo-ctx-agent to pypi.org.

## One-time Setup

```bash
pip install build twine
```

Create API tokens at https://pypi.org/manage/account/token/ (one per project recommended).

Configure `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN
```

Or pass the token per upload:

```bash
twine upload dist/* -u __token__ -p pypi-YOUR-API-TOKEN
```

## repo-ctx (Automated via GitHub Actions)

Publishing is automated. When you bump the version in `pyproject.toml` and push to `main`, the GitHub Action workflow handles everything:

1. Detects the version change
2. Builds the package
3. Publishes to PyPI
4. Creates a git tag (`v0.9.0`)
5. Creates a GitHub Release with changelog

### Release Steps

```bash
# 1. Bump version in pyproject.toml
#    version = "0.9.0"

# 2. Commit and push
git add pyproject.toml
git commit -m "release: v0.9.0"
git push origin main

# 3. Monitor at: https://github.com/repo-ctx/repo-ctx/actions
```

The workflow skips if the tag already exists (safe to push other pyproject.toml changes).

### Manual Trigger

You can also trigger the workflow manually from the Actions tab (`workflow_dispatch`).

## repo-ctx-agent (Manual)

```bash
cd /home/os/development/repo_ctx_agent

# 1. Bump version in pyproject.toml

# 2. Clean, build, upload
rm -rf dist/ build/ *.egg-info
python -m build
twine check dist/*
twine upload dist/*

# 3. Verify
pip install repo-ctx-agent==0.1.1
```

## Test PyPI (dry run)

```bash
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ repo-ctx
```

## Checklist

- [ ] Version bumped in pyproject.toml
- [ ] All tests pass
- [ ] For repo-ctx: push to main (automated)
- [ ] For repo-ctx-agent: `python -m build && twine upload dist/*`
- [ ] Verify install: `pip install <package>==<version>`
