"""Tests for docgen.formatters module."""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from docgen.formatters import (
    MarkdownFormatter,
    JSONFormatter,
    DomainModelFormatter,
    MermaidFormatter,
    get_formatter,
    format_output,
    save_output,
)
from docgen.state import DocGenState, create_initial_state, DocGenPhase


@pytest.fixture
def sample_state() -> DocGenState:
    """Create a sample state for testing."""
    state = create_initial_state("/test/project")
    state["phase"] = DocGenPhase.COMPLETED.value
    state["symbols"] = [
        {"name": "User", "symbol_type": "class", "docstring": "User entity"},
        {"name": "Order", "symbol_type": "class", "docstring": "Order entity"},
    ]
    state["dependencies"] = [
        {"source": "Order", "target": "User", "dependency_type": "uses"}
    ]
    state["domain_model"] = {
        "entities": [
            {
                "name": "User",
                "description": "A user in the system",
                "attributes": ["id", "name", "email"],
                "relationships": ["has many Orders"],
            },
            {
                "name": "Order",
                "description": "A customer order",
                "attributes": ["id", "total", "status"],
                "relationships": ["belongs to User"],
            },
        ],
        "processes": [],
        "glossary": {"User": "A person using the system"},
    }
    state["terminology"] = {
        "User": "A person using the system",
        "Order": "A purchase transaction",
        "_internal": "Should be hidden",
    }
    state["documentation"] = [
        {
            "title": "Overview",
            "content": "## Overview\n\nThis is the overview section.",
            "section_type": "overview",
            "order": 0,
            "diagrams": [],
        },
        {
            "title": "User",
            "content": "## User\n\nUser entity documentation.",
            "section_type": "entity",
            "order": 1,
            "diagrams": [],
        },
        {
            "title": "Architecture",
            "content": "## Architecture\n\n```mermaid\nclassDiagram\n    class User\n    class Order\n```",
            "section_type": "architecture",
            "order": 50,
            "diagrams": ["```mermaid\nclassDiagram\n    class User\n    class Order\n```"],
        },
    ]
    state["review_feedback"] = {"is_approved": True, "issues": [], "suggestions": []}
    state["revision_count"] = 1
    state["is_complete"] = True
    return state


class TestMarkdownFormatter:
    """Tests for MarkdownFormatter."""

    def test_get_extension(self):
        formatter = MarkdownFormatter()
        assert formatter.get_extension() == ".md"

    def test_format_includes_header(self, sample_state):
        formatter = MarkdownFormatter()
        result = formatter.format(sample_state)

        assert "# Domain Documentation:" in result
        assert "project" in result

    def test_format_includes_documentation_sections(self, sample_state):
        formatter = MarkdownFormatter()
        result = formatter.format(sample_state)

        assert "## Overview" in result
        assert "## User" in result

    def test_format_includes_metadata(self, sample_state):
        formatter = MarkdownFormatter()
        result = formatter.format(sample_state)

        assert "## Generation Metadata" in result
        assert "**Target**:" in result
        assert "**Phase**:" in result
        assert "completed" in result

    def test_format_empty_state(self):
        state = create_initial_state("/test/empty")
        formatter = MarkdownFormatter()
        result = formatter.format(state)

        assert "# Domain Documentation:" in result

    def test_format_section(self, sample_state):
        formatter = MarkdownFormatter()
        section = sample_state["documentation"][0]
        result = formatter.format_section(section)

        assert "## Overview" in result


class TestJSONFormatter:
    """Tests for JSONFormatter."""

    def test_get_extension(self):
        formatter = JSONFormatter()
        assert formatter.get_extension() == ".json"

    def test_format_returns_valid_json(self, sample_state):
        formatter = JSONFormatter()
        result = formatter.format(sample_state)

        # Should be valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_format_includes_metadata(self, sample_state):
        formatter = JSONFormatter()
        result = formatter.format(sample_state)
        parsed = json.loads(result)

        assert "metadata" in parsed
        assert parsed["metadata"]["target_path"] == "/test/project"
        assert parsed["metadata"]["phase"] == "completed"

    def test_format_includes_domain_model(self, sample_state):
        formatter = JSONFormatter()
        result = formatter.format(sample_state)
        parsed = json.loads(result)

        assert "domain_model" in parsed
        assert len(parsed["domain_model"]["entities"]) == 2

    def test_format_filters_internal_terminology(self, sample_state):
        formatter = JSONFormatter()
        result = formatter.format(sample_state)
        parsed = json.loads(result)

        assert "_internal" not in parsed["terminology"]
        assert "User" in parsed["terminology"]

    def test_format_with_indent(self, sample_state):
        formatter = JSONFormatter(indent=4)
        result = formatter.format(sample_state)

        # With indent=4, lines should have indentation
        assert "    " in result

    def test_format_with_raw_state(self, sample_state):
        formatter = JSONFormatter(include_raw_state=True)
        result = formatter.format(sample_state)
        parsed = json.loads(result)

        assert "raw_state" in parsed


class TestDomainModelFormatter:
    """Tests for DomainModelFormatter."""

    def test_get_extension(self):
        formatter = DomainModelFormatter()
        assert formatter.get_extension() == ".json"

    def test_format_returns_valid_json(self, sample_state):
        formatter = DomainModelFormatter()
        result = formatter.format(sample_state)

        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_format_includes_only_domain_model(self, sample_state):
        formatter = DomainModelFormatter()
        result = formatter.format(sample_state)
        parsed = json.loads(result)

        assert "domain_model" in parsed
        assert "terminology" in parsed
        # Should not include other state fields
        assert "documentation" not in parsed
        assert "symbols" not in parsed

    def test_format_filters_internal_terminology(self, sample_state):
        formatter = DomainModelFormatter()
        result = formatter.format(sample_state)
        parsed = json.loads(result)

        assert "_internal" not in parsed["terminology"]


class TestMermaidFormatter:
    """Tests for MermaidFormatter."""

    def test_get_extension(self):
        formatter = MermaidFormatter()
        assert formatter.get_extension() == ".mermaid"

    def test_format_extracts_diagrams(self, sample_state):
        formatter = MermaidFormatter()
        result = formatter.format(sample_state)

        assert "mermaid" in result
        assert "classDiagram" in result

    def test_format_no_diagrams(self):
        state = create_initial_state("/test/empty")
        state["documentation"] = [
            {"title": "Test", "content": "No diagrams", "section_type": "test", "order": 0, "diagrams": []}
        ]

        formatter = MermaidFormatter()
        result = formatter.format(state)

        assert "No diagrams generated" in result


class TestGetFormatter:
    """Tests for get_formatter function."""

    def test_get_markdown_formatter(self):
        formatter = get_formatter("markdown")
        assert isinstance(formatter, MarkdownFormatter)

    def test_get_md_formatter(self):
        formatter = get_formatter("md")
        assert isinstance(formatter, MarkdownFormatter)

    def test_get_json_formatter(self):
        formatter = get_formatter("json")
        assert isinstance(formatter, JSONFormatter)

    def test_get_domain_formatter(self):
        formatter = get_formatter("domain")
        assert isinstance(formatter, DomainModelFormatter)

    def test_get_mermaid_formatter(self):
        formatter = get_formatter("mermaid")
        assert isinstance(formatter, MermaidFormatter)

    def test_get_unknown_formatter_raises(self):
        with pytest.raises(ValueError) as exc_info:
            get_formatter("unknown")

        assert "Unknown format" in str(exc_info.value)

    def test_case_insensitive(self):
        formatter = get_formatter("MARKDOWN")
        assert isinstance(formatter, MarkdownFormatter)

    def test_passes_kwargs_to_formatter(self):
        formatter = get_formatter("json", indent=4, include_raw_state=True)
        assert formatter.indent == 4
        assert formatter.include_raw_state is True


class TestFormatOutput:
    """Tests for format_output function."""

    def test_format_output_markdown(self, sample_state):
        result = format_output(sample_state, "markdown")
        assert "# Domain Documentation:" in result

    def test_format_output_json(self, sample_state):
        result = format_output(sample_state, "json")
        parsed = json.loads(result)
        assert "metadata" in parsed

    def test_format_output_default_markdown(self, sample_state):
        result = format_output(sample_state)
        assert "# Domain Documentation:" in result


class TestSaveOutput:
    """Tests for save_output function."""

    def test_save_to_file(self, sample_state):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.md"
            result = save_output(sample_state, str(output_path))

            assert result.exists()
            content = result.read_text()
            assert "# Domain Documentation:" in content

    def test_save_to_directory(self, sample_state):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = save_output(sample_state, tmpdir)

            assert result.exists()
            assert result.suffix == ".md"
            assert "project-docs" in result.name

    def test_save_auto_detects_format_from_extension(self, sample_state):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.json"
            result = save_output(sample_state, str(output_path))

            content = result.read_text()
            parsed = json.loads(content)
            assert "metadata" in parsed

    def test_save_creates_parent_directories(self, sample_state):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "nested" / "dir" / "output.md"
            result = save_output(sample_state, str(output_path))

            assert result.exists()
            assert result.parent.exists()
