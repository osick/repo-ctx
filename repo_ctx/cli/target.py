"""Target detection utilities for CLI commands.

Determines whether a target string refers to:
- Local filesystem path
- Indexed repository (repo-id format: /owner/repo)
- Remote repository (owner/repo format, may need indexing)
"""

import os
from pathlib import Path
from enum import Enum
from dataclasses import dataclass


class TargetType(Enum):
    """Type of target resource."""
    LOCAL_PATH = "local"      # ./src, /abs/path, ~/home
    INDEXED_REPO = "indexed"  # /owner/repo (leading / = indexed)
    REMOTE_REPO = "remote"    # owner/repo (no leading /)


@dataclass
class Target:
    """Parsed target information."""
    type: TargetType
    value: str
    # For repos
    owner: str = ""
    repo: str = ""

    @property
    def repo_id(self) -> str:
        """Get repo ID in /owner/repo format."""
        if self.type in (TargetType.INDEXED_REPO, TargetType.REMOTE_REPO):
            return f"/{self.owner}/{self.repo}"
        return ""

    @property
    def is_local(self) -> bool:
        return self.type == TargetType.LOCAL_PATH

    @property
    def is_repo(self) -> bool:
        return self.type in (TargetType.INDEXED_REPO, TargetType.REMOTE_REPO)


def detect_target(target: str) -> Target:
    """
    Detect the type of target from a string.

    Convention:
    - /owner/repo     → Indexed repository (leading / distinguishes from path)
    - ./path, ~/path  → Local path (explicit relative/home)
    - /absolute/path  → Local path if it exists or looks like path (has extension or multiple segments)
    - owner/repo      → Remote repository (will need indexing)

    Args:
        target: Target string from command line

    Returns:
        Target object with detected type and parsed components
    """
    # Expand user home directory
    expanded = os.path.expanduser(target)

    # Check for explicit local path indicators
    if target.startswith("./") or target.startswith("../") or target.startswith("~/"):
        return Target(
            type=TargetType.LOCAL_PATH,
            value=expanded
        )

    # Check if it's an absolute path that exists
    if target.startswith("/"):
        # Could be /owner/repo (repo-id) or /absolute/path (local)
        path = Path(expanded)

        # If path exists on filesystem, it's a local path
        if path.exists():
            return Target(
                type=TargetType.LOCAL_PATH,
                value=expanded
            )

        # Check if it looks like a repo-id: /owner/repo (exactly 2 parts after /)
        parts = target[1:].split("/")  # Remove leading /
        if len(parts) == 2 and _looks_like_repo_name(parts[0]) and _looks_like_repo_name(parts[1]):
            return Target(
                type=TargetType.INDEXED_REPO,
                value=target,
                owner=parts[0],
                repo=parts[1]
            )

        # Otherwise treat as local path (might not exist yet)
        return Target(
            type=TargetType.LOCAL_PATH,
            value=expanded
        )

    # No leading / - could be relative path or owner/repo
    parts = target.split("/")

    # If it's a single word or has file extension, likely local
    if len(parts) == 1 or _has_file_extension(target):
        return Target(
            type=TargetType.LOCAL_PATH,
            value=expanded
        )

    # Check if it exists as a local path
    if Path(expanded).exists():
        return Target(
            type=TargetType.LOCAL_PATH,
            value=expanded
        )

    # Exactly 2 parts like owner/repo - treat as remote repo
    if len(parts) == 2 and _looks_like_repo_name(parts[0]) and _looks_like_repo_name(parts[1]):
        return Target(
            type=TargetType.REMOTE_REPO,
            value=target,
            owner=parts[0],
            repo=parts[1]
        )

    # Multiple parts - could be group/subgroup/repo or nested path
    # If any part has dots or extensions, treat as path
    if any("." in part for part in parts):
        return Target(
            type=TargetType.LOCAL_PATH,
            value=expanded
        )

    # Default: treat as remote repo (GitLab group/subgroup/project style)
    return Target(
        type=TargetType.REMOTE_REPO,
        value=target,
        owner="/".join(parts[:-1]),
        repo=parts[-1]
    )


def _looks_like_repo_name(s: str) -> bool:
    """Check if string looks like a valid repo/owner name."""
    if not s:
        return False
    # Repo names: alphanumeric, hyphens, underscores
    # Should not have file extensions or special chars
    return (
        s[0].isalnum() and
        all(c.isalnum() or c in "-_" for c in s) and
        "." not in s
    )


def _has_file_extension(s: str) -> bool:
    """Check if string ends with a file extension."""
    common_extensions = {
        ".py", ".js", ".ts", ".java", ".kt", ".go", ".rb", ".php",
        ".c", ".h", ".cpp", ".hpp", ".cs", ".swift", ".st",
        ".json", ".yaml", ".yml", ".toml", ".xml", ".md", ".txt"
    }
    return any(s.endswith(ext) for ext in common_extensions)
