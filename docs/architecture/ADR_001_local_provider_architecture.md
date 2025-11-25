# ADR 001: Local Filesystem Provider Architecture

**Status:** Proposed
**Date:** 2025-11-25
**Decision Makers:** Development Team
**Tags:** architecture, providers, local-filesystem

---

## Context

The repo-ctx MCP server currently supports GitLab and GitHub providers for indexing remote repositories. Users have requested support for indexing local Git repositories to enable:

1. **Offline development** - Index documentation without network access
2. **Pre-push testing** - Test documentation indexing before pushing to remote
3. **Private repositories** - Index repos not yet on remote platforms
4. **Performance** - Faster indexing without API latency (5-10x faster)

**User Priority:** HIGHEST - "the most important of all" data sources

---

## Decision

We will implement a **LocalGitProvider** that uses GitPython to read local Git repositories directly from the filesystem.

### Key Design Decisions

#### 1. **Use GitPython Library**

**Chosen:** GitPython
**Alternatives Considered:**
- `pygit2` (libgit2 bindings - faster but requires compiled dependencies)
- Direct `git` CLI subprocess calls (simpler but less reliable)

**Rationale:**
- Pure Python implementation (no compiled dependencies)
- Mature, well-maintained library (10+ years, 4K+ stars)
- Async-compatible via `asyncio.to_thread()`
- Comprehensive Git operations support
- Easier to debug and maintain

**Trade-offs:**
- Slightly slower than pygit2 (~20-30% in benchmarks)
- But still 5-10x faster than remote API calls
- Performance acceptable for local indexing use case

#### 2. **Path Detection and Auto-Discovery**

**Format Support:**
- Absolute paths: `/home/user/projects/myapp`
- Relative paths: `./myapp`, `../other-project`
- Home-relative paths: `~/projects/myapp`

**Auto-Detection Logic:**
```python
def detect_provider(path: str) -> str:
    if path.startswith(('/', './', '~/')):
        return 'local'
    elif '/' in path and path.count('/') == 1:
        return 'github'  # owner/repo
    elif '/' in path and path.count('/') >= 2:
        return 'gitlab'  # group/subgroup/project
```

**Rationale:**
- Intuitive path-based provider selection
- No explicit `--provider local` needed for obvious paths
- Falls back to auto-detection for ambiguous cases

#### 3. **Repository Identification**

**Strategy:** Use Git remote URL if available, fallback to path hash

```python
library_id = f"/local/{path_hash_or_remote}"
```

**Examples:**
- With remote: `/local/github.com/owner/repo`
- Without remote: `/local/abc123def` (hash of absolute path)

**Rationale:**
- Stable identifier even if path changes
- Links to remote repo if eventually pushed
- Compatible with existing library_id schema

#### 4. **Branch and Tag Indexing**

**Default Behavior:**
- Index current branch (HEAD)
- Index last 5 tags (same as remote providers)

**New Feature:** Selective branch indexing
```bash
repo-ctx --index ~/myapp --branches main,develop
```

**Rationale:**
- Consistent with existing provider behavior
- Users often only care about main development branches
- Saves indexing time for repos with many branches

#### 5. **File Access Strategy**

**For Historical Versions (branches/tags):**
- Use `git show ref:path` via GitPython
- Read from Git object database (.git/objects)

**For Working Directory:**
- Optional: Read uncommitted changes directly from filesystem
- Default: Only index committed changes

**Rationale:**
- Consistent with Git's versioning model
- Avoids indexing work-in-progress
- Users can explicitly request working directory indexing

#### 6. **Storage Schema Extension**

**Add Provider Column:**
```sql
ALTER TABLE libraries ADD COLUMN provider TEXT DEFAULT 'gitlab';
UPDATE libraries SET provider =
    CASE
        WHEN id LIKE '/local/%' THEN 'local'
        WHEN id LIKE '/%' AND id NOT LIKE '/local/%' THEN
            (SELECT CASE WHEN INSTR(SUBSTR(id, 2), '/') = 1 THEN 'github' ELSE 'gitlab' END)
        ELSE 'gitlab'
    END;
```

**Rationale:**
- Enables filtering repositories by provider
- Required for `list-repositories --provider local`
- Backward compatible (defaults to 'gitlab')

---

## Implementation Plan

### Phase 1A: Core LocalGitProvider (2-3 days)

**Tasks:**
1. Create `repo_ctx/providers/local.py` with `LocalGitProvider` class
2. Implement GitProvider interface methods:
   - `get_project()` - Extract name from directory or git config
   - `get_default_branch()` - Get current branch or HEAD
   - `get_file_tree()` - Use `git ls-tree -r` recursively
   - `read_file()` - Use `git show ref:path`
   - `read_config()` - Read `.repo-ctx.json` or `git_context.json`
   - `get_tags()` - Get tags sorted by date
3. Add GitPython dependency to `pyproject.toml`
4. Update provider detector to recognize filesystem paths
5. Update CLI to handle filesystem paths

**Test Coverage:**
- Unit tests for path resolution (absolute, relative, home)
- Unit tests for Git operations (branches, tags, files)
- Integration tests with temporary Git repos
- Test handling of repos with/without remotes
- Test submodule handling

### Phase 1B: List Repositories Feature (1 day)

**Tasks:**
1. Add `provider` column to libraries table (migration script)
2. Implement `list_repositories()` in `core.py`
3. Add CLI command `list-repositories`
4. Add MCP tool `list-repositories`
5. Support filtering by provider
6. Support multiple output formats (table, json, simple)

**Test Coverage:**
- Test listing all repositories
- Test filtering by provider
- Test output format variations
- Test empty repository list

### Phase 1C: Selective Branch Indexing (1-2 days)

**Tasks:**
1. Add `branches` parameter to `index_repository()` method
2. Add `include_tags` parameter
3. Update CLI with `--branches` flag
4. Update MCP tools with `branches` parameter
5. Modify indexing logic to respect branch selection

**Test Coverage:**
- Test indexing specific branches
- Test default behavior (default branch + tags)
- Test `--no-tags` flag
- Test non-existent branch handling

### Phase 1D: Branch-Specific Search (1 day)

**Tasks:**
1. Add `branches` parameter to `fuzzy_search()` method
2. Update SQL queries to filter by version
3. Update CLI search commands with `--branch` flag
4. Update MCP search tools

**Test Coverage:**
- Test searching in specific branch
- Test searching across multiple branches
- Test default behavior (all branches)

### Phase 1E: AsciiDoc Support (1 day)

**Tasks:**
1. Add `.adoc`, `.asciidoc` to `DOC_EXTENSIONS` in parser
2. Implement `parse_asciidoc()` method (simple text extraction MVP)
3. Optional: Add advanced parsers (asciidoc library, pandoc)
4. Update parser to route .adoc files to correct handler

**Test Coverage:**
- Test .adoc file detection
- Test simple AsciiDoc parsing
- Test header conversion
- Test directive handling

---

## Consequences

### Positive

1. **Offline Capability** - Users can index and search repos without network
2. **Performance** - 5-10x faster than remote providers
3. **Developer Workflow** - Test documentation before pushing
4. **Privacy** - Index private repos without remote access
5. **Consistent Architecture** - LocalGitProvider follows same interface as remote providers

### Negative

1. **Git Dependency** - Requires valid Git repository (not just files)
2. **Path Stability** - Repo identification may break if repo moved without git remote
3. **Uncommitted Changes** - By default, won't index work-in-progress (feature, not bug)

### Neutral

1. **GitPython Dependency** - Adds ~3MB to installation size
2. **Storage Growth** - Provider column adds minimal overhead (~10 bytes/repo)

---

## Alternatives Considered

### Alternative 1: File-based Indexing (No Git Requirement)

**Approach:** Index any directory, not just Git repos

**Pros:**
- Works with any filesystem
- No Git dependency
- Simpler implementation

**Cons:**
- No version control awareness
- No branch/tag support
- Can't track changes over time
- Doesn't fit "repository context" model

**Decision:** Rejected - Git awareness is core to the product

### Alternative 2: Direct .git Object Reading

**Approach:** Read Git objects directly without GitPython

**Pros:**
- No external dependencies
- Maximum performance

**Cons:**
- Complex Git internals (pack files, deltas, etc.)
- Difficult to maintain
- Error-prone for edge cases
- Reinventing the wheel

**Decision:** Rejected - Not worth the maintenance burden

### Alternative 3: Git CLI Subprocess Calls

**Approach:** Shell out to `git` commands

**Pros:**
- No library dependency
- Works if `git` is installed
- Simple implementation

**Cons:**
- Subprocess overhead
- Platform-specific issues (Windows)
- Error handling complexity
- Less reliable than library

**Decision:** Rejected - GitPython provides better reliability

---

## Performance Expectations

### Indexing Speed Targets

- **Small repo** (100 files): < 2 seconds
- **Medium repo** (1000 files): < 20 seconds
- **Large repo** (10K files): < 3 minutes

### Comparison to Remote Providers

- **GitHub API**: ~30-60 seconds for 1000 files (rate limits, network latency)
- **GitLab API**: ~40-80 seconds for 1000 files (rate limits, network latency)
- **Local Git**: ~20 seconds for 1000 files (no network, no rate limits)

**Expected Speedup:** 5-10x faster than remote providers

---

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| GitPython performance issues | Medium | Low | Benchmark early, fallback to pygit2 if needed |
| Large repos (>100K files) | Medium | Medium | Implement batching, parallel processing |
| Git repository corruption | High | Very Low | Validate repo before indexing, clear error messages |
| Path changes break repo links | Low | Medium | Document best practice: always set git remote |
| Submodule handling complexity | Medium | Low | MVP: skip submodules, add feature later |

---

## References

- [GitPython Documentation](https://gitpython.readthedocs.io/)
- [Git Internals](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain)
- [Focused Requirements Document](/tmp/focused_requirements.md)
- [User Priorities](../gitlab-context/.vibe/development-plan-default.md#user-feedback-received-)

---

## Review and Approval

- [ ] Technical Review
- [ ] User Acceptance
- [ ] Security Review (if applicable)

**Approved By:** _Pending_
**Approval Date:** _Pending_

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-11-25 | 0.1 | Initial ADR created | Claude |
