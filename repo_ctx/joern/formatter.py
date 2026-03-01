"""
CPG Query Output Formatter for LLM consumption.

This module provides utilities to transform raw CPGQL query output into
structured, self-documenting formats suitable for LLM code analysis.
"""

import re
from dataclasses import dataclass, field
from typing import Any


# Patterns for filtering Joern internal artifacts
INTERNAL_PATTERNS = [
    r"^<operator>\.",       # Operators: <operator>.assignment, etc.
    r"^<meta",              # Meta: <metaClassCallHandler>, <metaClassAdapter>
    r"^<fake",              # Fake: <fakeNew>
    r"^<body>$",            # Body markers
    r"^<module>$",          # Module markers
    r"^<lambda>\d+$",       # Lambda markers
    r"<metaClassAdapter>$", # Meta adapters
    r"<redefinition\d+>$",  # Redefinitions
    r"^ANY$",               # Type placeholders
]

INTERNAL_REGEX = re.compile("|".join(INTERNAL_PATTERNS))

# Patterns indicating query/parse errors
ERROR_PATTERNS = [
    r"Query failed",
    r"joern-parse failed",
    r"java\.lang\.",
    r"AssertionError",
    r"Could not guess language",
    r"Please specify a language",
    r"--language option",
    r"Script execution failed",
    r"Error during compilation",
]

ERROR_REGEX = re.compile("|".join(ERROR_PATTERNS), re.IGNORECASE)


def is_internal_symbol(name: str) -> bool:
    """Check if a symbol name is a Joern internal artifact."""
    if not name:
        return True
    return bool(INTERNAL_REGEX.search(name))


def is_error_output(text: str) -> bool:
    """Check if the output contains error messages instead of valid data."""
    if not text:
        return False
    return bool(ERROR_REGEX.search(text))


def clean_inheritance_string(inherits: str) -> str:
    """Clean up inheritance string by extracting just the class names."""
    if not inherits:
        return ""

    # Split by comma and extract clean class names
    parts = inherits.split(",")
    clean_parts = []

    for part in parts:
        # Skip empty and internal parts
        if not part or is_internal_symbol(part):
            continue

        # Extract the last meaningful name from qualified paths
        # e.g., "sample/py:<module>.py:<module>.Shape" -> "Shape"
        name = part.split(".")[-1] if "." in part else part

        # Skip if name is internal
        if is_internal_symbol(name):
            continue

        # Skip duplicates
        if name not in clean_parts:
            clean_parts.append(name)

    return ", ".join(clean_parts)


def filter_internal_symbols(items: list[str]) -> list[str]:
    """Filter out Joern internal artifacts from a list of names."""
    return [item for item in items if not is_internal_symbol(item)]


@dataclass
class FormattedSection:
    """A section of formatted output."""
    title: str
    description: str
    items: list[dict[str, Any]] = field(default_factory=list)
    columns: list[str] = field(default_factory=list)


@dataclass
class FormattedReport:
    """A complete formatted report for LLM consumption."""
    title: str
    source_path: str
    language: str
    sections: list[FormattedSection] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


class CPGFormatter:
    """
    Formats CPG query results into LLM-friendly structured output.

    The formatter:
    - Filters out Joern internal artifacts
    - Groups results by category
    - Adds context (file, line, class)
    - Includes explanatory headers
    """

    def format_methods_report(
        self,
        raw_output: str,
        source_path: str = "",
        language: str = "",
    ) -> str:
        """
        Format method query output into a readable report.

        Expected input format (pipe-delimited):
        name|fullName|filename|lineStart|lineEnd|signature

        Args:
            raw_output: Raw query output
            source_path: Source directory path
            language: Programming language

        Returns:
            Formatted markdown report
        """
        # Check for error output
        if is_error_output(raw_output):
            return self._render_error_markdown("Methods", language)

        lines = raw_output.strip().split("\n")
        methods = []

        for line in lines:
            line = line.strip()
            if not line or is_internal_symbol(line.split("|")[0] if "|" in line else line):
                continue

            if "|" in line:
                parts = line.split("|")
                if len(parts) >= 6:
                    methods.append({
                        "name": parts[0],
                        "qualified_name": parts[1],
                        "file": parts[2],
                        "line_start": parts[3],
                        "line_end": parts[4],
                        "signature": parts[5],
                    })
            else:
                # Simple name only
                methods.append({"name": line})

        return self._render_methods_markdown(methods, source_path, language)

    def format_types_report(
        self,
        raw_output: str,
        source_path: str = "",
        language: str = "",
    ) -> str:
        """
        Format type/class query output into a readable report.

        Expected input format (pipe-delimited):
        name|fullName|filename|lineNumber|inheritsFrom

        Args:
            raw_output: Raw query output
            source_path: Source directory path
            language: Programming language

        Returns:
            Formatted markdown report
        """
        # Check for error output
        if is_error_output(raw_output):
            return self._render_error_markdown("Types", language)

        lines = raw_output.strip().split("\n")
        types = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "|" in line:
                parts = line.split("|")
                name = parts[0] if len(parts) > 0 else ""

                # Skip internal types
                if is_internal_symbol(name):
                    continue

                if len(parts) >= 4:
                    # Clean up inheritance string
                    inherits = clean_inheritance_string(parts[4]) if len(parts) > 4 else ""

                    types.append({
                        "name": name,
                        "qualified_name": parts[1],
                        "file": parts[2],
                        "line": parts[3],
                        "inherits_from": inherits,
                    })
            else:
                if not is_internal_symbol(line):
                    types.append({"name": line})

        return self._render_types_markdown(types, source_path, language)

    def format_calls_report(
        self,
        raw_output: str,
        source_path: str = "",
        language: str = "",
    ) -> str:
        """
        Format call graph query output into a readable report.

        Expected input format (pipe-delimited):
        caller|callee|lineNumber

        Args:
            raw_output: Raw query output
            source_path: Source directory path
            language: Programming language

        Returns:
            Formatted markdown report
        """
        # Check for error output
        if is_error_output(raw_output):
            return self._render_error_markdown("Calls", language)

        lines = raw_output.strip().split("\n")
        calls = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "|" in line:
                parts = line.split("|")
                caller = parts[0] if len(parts) > 0 else ""
                callee = parts[1] if len(parts) > 1 else ""
                line_num = parts[2] if len(parts) > 2 else ""

                # Skip internal operators and artifacts
                if is_internal_symbol(caller) or is_internal_symbol(callee):
                    continue

                calls.append({
                    "caller": caller,
                    "callee": callee,
                    "line": line_num,
                })
            else:
                if not is_internal_symbol(line):
                    calls.append({"callee": line})

        return self._render_calls_markdown(calls, source_path, language)

    def format_combined_report(
        self,
        methods_output: str,
        types_output: str,
        calls_output: str,
        source_path: str = "",
        language: str = "",
    ) -> str:
        """
        Create a comprehensive code analysis report combining all queries.

        Args:
            methods_output: Raw output from methods query
            types_output: Raw output from types query
            calls_output: Raw output from calls query
            source_path: Source directory path
            language: Programming language

        Returns:
            Formatted markdown report
        """
        parts = []

        # Header
        parts.append("# Code Analysis Report")
        parts.append("")
        if source_path:
            parts.append(f"**Source:** `{source_path}`")
        if language:
            parts.append(f"**Language:** {language}")
        parts.append("")
        parts.append("---")
        parts.append("")

        # Types section
        types_section = self.format_types_report(types_output, source_path, language)
        if types_section:
            parts.append(types_section)
            parts.append("")

        # Methods section
        methods_section = self.format_methods_report(methods_output, source_path, language)
        if methods_section:
            parts.append(methods_section)
            parts.append("")

        # Calls section
        calls_section = self.format_calls_report(calls_output, source_path, language)
        if calls_section:
            parts.append(calls_section)
            parts.append("")

        return "\n".join(parts)

    def _render_error_markdown(self, section_type: str, language: str = "") -> str:
        """Render an error message when CPG analysis fails."""
        lang_note = f" for {language}" if language else ""
        return f"""## {section_type}

*CPG analysis not available{lang_note}.*

Joern may not support this language or the analysis failed.
Use tree-sitter analysis for symbol extraction instead.
"""

    def _render_methods_markdown(
        self,
        methods: list[dict],
        source_path: str,
        language: str,
    ) -> str:
        """Render methods as markdown."""
        if not methods:
            return ""

        lines = [
            "## Methods/Functions",
            "",
            "Functions and methods defined in the codebase.",
            "",
        ]

        # Group by file if we have file info
        by_file: dict[str, list] = {}
        no_file = []

        for method in methods:
            file_path = method.get("file", "")
            if file_path:
                by_file.setdefault(file_path, []).append(method)
            else:
                no_file.append(method)

        if by_file:
            for file_path, file_methods in sorted(by_file.items()):
                lines.append(f"### `{file_path}`")
                lines.append("")
                lines.append("| Method | Lines | Parameters |")
                lines.append("|--------|-------|------------|")
                for m in file_methods:
                    name = m.get("name", "")
                    line_range = ""
                    if m.get("line_start") and m.get("line_end"):
                        line_range = f"{m['line_start']}-{m['line_end']}"
                    elif m.get("line_start"):
                        line_range = str(m["line_start"])
                    params = m.get("signature", "")[:80]  # signature field holds parameters now
                    lines.append(f"| `{name}` | {line_range} | {params} |")
                lines.append("")
        elif no_file:
            lines.append("| Method |")
            lines.append("|--------|")
            for m in no_file:
                lines.append(f"| `{m.get('name', '')}` |")
            lines.append("")

        lines.append(f"**Total methods:** {len(methods)}")
        lines.append("")

        return "\n".join(lines)

    def _render_types_markdown(
        self,
        types: list[dict],
        source_path: str,
        language: str,
    ) -> str:
        """Render types as markdown."""
        if not types:
            return ""

        lines = [
            "## Classes/Types",
            "",
            "Type declarations (classes, interfaces, structs) in the codebase.",
            "",
        ]

        # Separate classes with inheritance from standalone
        with_inheritance = [t for t in types if t.get("inherits_from")]
        standalone = [t for t in types if not t.get("inherits_from")]

        if with_inheritance:
            lines.append("### Inheritance Hierarchy")
            lines.append("")
            lines.append("| Type | Extends | File | Line |")
            lines.append("|------|---------|------|------|")
            for t in with_inheritance:
                name = t.get("name", "")
                inherits = t.get("inherits_from", "")
                file_path = t.get("file", "")
                line = t.get("line", "")
                lines.append(f"| `{name}` | {inherits} | {file_path} | {line} |")
            lines.append("")

        if standalone:
            lines.append("### Standalone Types")
            lines.append("")
            lines.append("| Type | File | Line |")
            lines.append("|------|------|------|")
            for t in standalone:
                name = t.get("name", "")
                file_path = t.get("file", "")
                line = t.get("line", "")
                lines.append(f"| `{name}` | {file_path} | {line} |")
            lines.append("")

        lines.append(f"**Total types:** {len(types)}")
        lines.append("")

        return "\n".join(lines)

    def _render_calls_markdown(
        self,
        calls: list[dict],
        source_path: str,
        language: str,
    ) -> str:
        """Render call graph as markdown."""
        if not calls:
            return ""

        lines = [
            "## Call Graph",
            "",
            "Function calls between methods in the codebase.",
            "Shows which functions call which other functions.",
            "",
        ]

        # Group by caller
        by_caller: dict[str, list] = {}

        for call in calls:
            caller = call.get("caller", "(top-level)")
            callee = call.get("callee", "")
            if caller and callee:
                by_caller.setdefault(caller, []).append(call)

        if by_caller:
            lines.append("| Caller | Calls | Line |")
            lines.append("|--------|-------|------|")
            for caller, caller_calls in sorted(by_caller.items()):
                for c in caller_calls:
                    callee = c.get("callee", "")
                    line = c.get("line", "")
                    lines.append(f"| `{caller}` | `{callee}` | {line} |")
            lines.append("")

        # Count unique callers and callees
        unique_callers = set(c.get("caller", "") for c in calls if c.get("caller"))
        unique_callees = set(c.get("callee", "") for c in calls if c.get("callee"))

        lines.append(f"**Total calls:** {len(calls)}")
        lines.append(f"**Unique callers:** {len(unique_callers)}")
        lines.append(f"**Unique callees:** {len(unique_callees)}")
        lines.append("")

        return "\n".join(lines)


def format_simple_list(
    raw_output: str,
    title: str = "Results",
    description: str = "",
) -> str:
    """
    Format a simple list of names with filtering and deduplication.

    Args:
        raw_output: Raw query output (one item per line)
        title: Section title
        description: Optional description

    Returns:
        Formatted markdown
    """
    lines = raw_output.strip().split("\n")
    items = []

    for line in lines:
        line = line.strip()
        if line and not is_internal_symbol(line):
            items.append(line)

    # Deduplicate while preserving order
    seen = set()
    unique_items = []
    for item in items:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)

    output = [f"## {title}", ""]
    if description:
        output.append(description)
        output.append("")

    if unique_items:
        for item in unique_items:
            output.append(f"- `{item}`")
        output.append("")
        output.append(f"**Total:** {len(unique_items)}")
    else:
        output.append("No items found.")

    output.append("")
    return "\n".join(output)
