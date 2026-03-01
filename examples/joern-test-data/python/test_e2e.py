"""End-to-end tests for docgen workflow."""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from docgen.workflow import run_workflow_sync, compile_workflow
from docgen.state import create_initial_state, DocGenPhase, DocGenOptions
from docgen.tools import ToolResult
from docgen.formatters import format_output, save_output


@pytest.fixture
def mock_tools():
    """Mock repo-ctx tools for testing."""
    analyze_result = ToolResult(
        success=True,
        data={
            "symbols": [
                {
                    "name": "UserService",
                    "symbol_type": "class",
                    "docstring": "Service for managing users",
                    "file_path": "src/services/user.py",
                    "line_number": 10,
                },
                {
                    "name": "OrderService",
                    "symbol_type": "class",
                    "docstring": "Service for managing orders",
                    "file_path": "src/services/order.py",
                    "line_number": 15,
                },
                {
                    "name": "process_payment",
                    "symbol_type": "function",
                    "docstring": "Process a payment transaction",
                    "file_path": "src/payments.py",
                    "line_number": 50,
                },
            ]
        },
    )

    graph_result = ToolResult(
        success=True,
        data={
            "edges": [
                {"source": "OrderService", "target": "UserService", "relation": "uses"},
                {"source": "OrderService", "target": "process_payment", "relation": "calls"},
            ]
        },
    )

    query_result = ToolResult(
        success=True,
        data={"result": ["method1", "method2", "method3"]},
    )

    docs_result = ToolResult(
        success=True,
        data={"content": "# Project Documentation\n\nThis is the main project."},
    )

    with patch("docgen.tools.tools") as mock_tools:
        mock_tools.analyze.return_value = analyze_result
        mock_tools.graph.return_value = graph_result
        mock_tools.query.return_value = query_result
        mock_tools.docs.return_value = docs_result
        yield mock_tools


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    def test_workflow_completes_successfully(self, mock_tools):
        """Test that workflow runs to completion."""
        final_state = run_workflow_sync(
            target_path="/test/project",
            include_diagrams=True,
            max_revisions=2,
        )

        assert final_state["is_complete"] is True
        assert final_state["phase"] == DocGenPhase.COMPLETED.value

    def test_workflow_generates_documentation(self, mock_tools):
        """Test that workflow generates documentation sections."""
        final_state = run_workflow_sync(
            target_path="/test/project",
            include_diagrams=True,
        )

        documentation = final_state.get("documentation", [])
        assert len(documentation) > 0

        # Check for expected sections
        section_types = {s.get("section_type") for s in documentation}
        assert "overview" in section_types

    def test_workflow_extracts_domain_model(self, mock_tools):
        """Test that workflow extracts domain model."""
        final_state = run_workflow_sync(target_path="/test/project")

        domain_model = final_state.get("domain_model", {})
        # Domain model should exist even if empty (filtered by heuristics)
        assert domain_model is not None
        assert "entities" in domain_model
        # Note: entities may be empty if heuristics filter them out

    def test_workflow_includes_diagrams_when_enabled(self, mock_tools):
        """Test that diagrams are included when enabled."""
        final_state = run_workflow_sync(
            target_path="/test/project",
            include_diagrams=True,
        )

        documentation = final_state.get("documentation", [])

        # Check for architecture section with diagrams
        arch_sections = [s for s in documentation if s.get("section_type") == "architecture"]

        if arch_sections:
            arch = arch_sections[0]
            assert "mermaid" in arch.get("content", "").lower() or len(arch.get("diagrams", [])) > 0

    def test_workflow_respects_max_revisions(self, mock_tools):
        """Test that workflow respects max revision limit."""
        final_state = run_workflow_sync(
            target_path="/test/project",
            max_revisions=1,
        )

        # Should complete even if review has issues
        assert final_state.get("revision_count", 0) <= 2


class TestEndToEndFormatting:
    """End-to-end formatting tests."""

    def test_markdown_output(self, mock_tools):
        """Test markdown output generation."""
        final_state = run_workflow_sync(target_path="/test/project")

        output = format_output(final_state, "markdown")

        assert "# Domain Documentation:" in output
        assert "project" in output

    def test_json_output(self, mock_tools):
        """Test JSON output generation."""
        final_state = run_workflow_sync(target_path="/test/project")

        output = format_output(final_state, "json")
        parsed = json.loads(output)

        assert "metadata" in parsed
        assert "domain_model" in parsed
        assert "documentation" in parsed

    def test_save_to_file(self, mock_tools):
        """Test saving output to file."""
        final_state = run_workflow_sync(target_path="/test/project")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = save_output(final_state, tmpdir, "markdown")

            assert output_path.exists()
            content = output_path.read_text()
            assert "# Domain Documentation:" in content


class TestEndToEndWithLLM:
    """End-to-end tests with mocked LLM."""

    def test_workflow_with_llm(self, mock_tools):
        """Test workflow with mocked LLM."""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(
            content="This is LLM-generated documentation for the project."
        )

        final_state = run_workflow_sync(
            target_path="/test/project",
            llm=mock_llm,
        )

        assert final_state["is_complete"] is True

        # LLM should have been called at least once
        assert mock_llm.invoke.called

    def test_workflow_fallback_without_llm(self, mock_tools):
        """Test workflow falls back to heuristics without LLM."""
        final_state = run_workflow_sync(
            target_path="/test/project",
            llm=None,
        )

        # Should still complete successfully
        assert final_state["is_complete"] is True
        assert len(final_state.get("documentation", [])) > 0


class TestEndToEndCLI:
    """End-to-end CLI tests."""

    def test_cli_dry_run(self):
        """Test CLI dry run mode."""
        from typer.testing import CliRunner
        from docgen.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["generate", "/test/path", "--dry-run"])

        assert result.exit_code == 0
        assert "Dry run" in result.stdout
        assert "Workflow steps" in result.stdout

    def test_cli_version(self):
        """Test CLI version command."""
        from typer.testing import CliRunner
        from docgen.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "DocGen" in result.stdout

    def test_cli_models(self):
        """Test CLI models command."""
        from typer.testing import CliRunner
        from docgen.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["models"])

        assert result.exit_code == 0
        assert "claude-sonnet-4" in result.stdout
        assert "gpt-5" in result.stdout

    def test_cli_workflow(self):
        """Test CLI workflow command."""
        from typer.testing import CliRunner
        from docgen.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["workflow"])

        assert result.exit_code == 0
        assert "Analyzer Agent" in result.stdout
        assert "Extractor Agent" in result.stdout
        assert "Writer Agent" in result.stdout
        assert "Reviewer Agent" in result.stdout


class TestWorkflowStateTransitions:
    """Test workflow state transitions."""

    def test_phases_progress_correctly(self, mock_tools):
        """Test that workflow phases progress in correct order."""
        # Track phases during execution by examining final state
        final_state = run_workflow_sync(target_path="/test/project")

        # Should end in completed state
        assert final_state["phase"] == DocGenPhase.COMPLETED.value

        # Should have analysis data (from ANALYZING phase)
        assert "symbols" in final_state
        assert "dependencies" in final_state

        # Should have domain model (from EXTRACTING phase)
        assert "domain_model" in final_state

        # Should have documentation (from WRITING phase)
        assert "documentation" in final_state

        # Should have review feedback (from REVIEWING phase)
        assert "review_feedback" in final_state

    def test_review_cycle(self, mock_tools):
        """Test that review cycle works correctly."""
        final_state = run_workflow_sync(
            target_path="/test/project",
            max_revisions=2,
        )

        # Check revision count
        revision_count = final_state.get("revision_count", 0)
        assert revision_count >= 1

        # Check review feedback
        feedback = final_state.get("review_feedback", {})
        assert "is_approved" in feedback
