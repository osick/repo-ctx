"""Data models."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Library:
    group_name: str
    project_name: str
    description: str
    default_version: str
    id: Optional[int] = None
    last_indexed: Optional[datetime] = None


@dataclass
class Version:
    library_id: int
    version_tag: str
    commit_sha: str
    id: Optional[int] = None


@dataclass
class Document:
    version_id: int
    file_path: str
    content: str
    content_type: str = "markdown"
    tokens: int = 0
    id: Optional[int] = None


@dataclass
class SearchResult:
    library_id: str  # /group/project
    name: str
    description: str
    versions: list[str]
    score: float = 0.0


@dataclass
class FuzzySearchResult:
    library_id: str  # /group/project
    name: str
    group: str
    description: str
    score: float
    match_type: str
    matched_field: str
