"""Data models."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class OutputMode(Enum):
    """Output mode for documentation retrieval.

    - SUMMARY: Titles, descriptions, and key methods only (~500-2000 tokens)
              Optimized for LLM context efficiency
    - STANDARD: Current behavior with quality-based truncation
               Good balance of detail and size
    - FULL: Everything including tests and low-quality docs
            Complete documentation dump
    """
    SUMMARY = "summary"
    STANDARD = "standard"
    FULL = "full"

    @classmethod
    def from_string(cls, value: str) -> "OutputMode":
        """Create OutputMode from string value."""
        if not value:
            return cls.STANDARD
        normalized = value.lower().strip()
        for mode in cls:
            if mode.value == normalized:
                return mode
        raise ValueError(f"Invalid output mode: {value}. Valid modes: {[m.value for m in cls]}")


@dataclass
class Library:
    group_name: str
    project_name: str
    description: str
    default_version: str
    provider: str = "github"  # Provider type: github, gitlab, local
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
