"""
Language definitions for Joern CPG analysis.

This module contains the mapping of programming languages to their
Joern frontend configurations.
"""

import os

# Supported languages via Joern
JOERN_LANGUAGES = {
    "c": {
        "extensions": [".c", ".h"],
        "frontend": "c2cpg",
        "maturity": "very_high",
    },
    "cpp": {
        "extensions": [".cpp", ".cc", ".cxx", ".hpp", ".hxx", ".h"],
        "frontend": "c2cpg",
        "maturity": "very_high",
    },
    "java": {
        "extensions": [".java"],
        "frontend": "javasrc2cpg",
        "maturity": "high",
    },
    "javascript": {
        "extensions": [".js", ".jsx", ".mjs"],
        "frontend": "jssrc2cpg",
        "maturity": "high",
    },
    "typescript": {
        "extensions": [".ts", ".tsx"],
        "frontend": "jssrc2cpg",
        "maturity": "high",
    },
    "python": {
        "extensions": [".py"],
        "frontend": "pysrc2cpg",
        "maturity": "high",
    },
    "kotlin": {
        "extensions": [".kt", ".kts"],
        "frontend": "kotlin2cpg",
        "maturity": "medium",
        "requires_directory": True,  # kotlin2cpg only accepts directories
    },
    "go": {
        "extensions": [".go"],
        "frontend": "gosrc2cpg",
        "maturity": "medium",
    },
    "php": {
        "extensions": [".php"],
        "frontend": "php2cpg",
        "maturity": "medium",
    },
    "ruby": {
        "extensions": [".rb"],
        "frontend": "rubysrc2cpg",
        "maturity": "medium",
    },
    "swift": {
        "extensions": [".swift"],
        "frontend": "swiftsrc2cpg",
        "maturity": "medium",
    },
    "csharp": {
        "extensions": [".cs"],
        "frontend": "csharpsrc2cpg",
        "maturity": "medium",
    },
}


def get_language_for_file(file_path: str) -> str | None:
    """
    Detect programming language from file extension.

    Args:
        file_path: Path to the source file

    Returns:
        Language identifier or None if not supported
    """
    ext = os.path.splitext(file_path)[1].lower()
    for lang, info in JOERN_LANGUAGES.items():
        if ext in info["extensions"]:
            return lang
    return None


def get_supported_extensions() -> list[str]:
    """Get all file extensions supported by Joern."""
    extensions = []
    for info in JOERN_LANGUAGES.values():
        extensions.extend(info["extensions"])
    return sorted(set(extensions))


def get_joern_frontend(language: str) -> str | None:
    """Get the Joern frontend name for a language."""
    info = JOERN_LANGUAGES.get(language)
    return info["frontend"] if info else None


def get_language_maturity(language: str) -> str | None:
    """Get the maturity level for a language."""
    info = JOERN_LANGUAGES.get(language)
    return info["maturity"] if info else None


def requires_directory(language: str) -> bool:
    """Check if a language frontend requires a directory as input.

    Some Joern frontends (like kotlin2cpg) only accept directories,
    not single files.
    """
    info = JOERN_LANGUAGES.get(language)
    return info.get("requires_directory", False) if info else False
