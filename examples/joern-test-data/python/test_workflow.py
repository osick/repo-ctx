"""
Tests for DocGen workflow module.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from docgen.workflow import (
    should_revise,
    create_workflow,
    compile_workflow,
    get_workflow_diagram,
)
from docgen.state import create_initial_state, ReviewFeedback


class TestShouldRevise:
    """Tests for the should_revise routing function."""

    def test_should_revise_approved(self):
        """Test routing when documentation is approved."""
        state = create_initial_state("./src")
        state["review_feedback"] = ReviewFeedback(is_approved=True).to_dict()

        result = should_revise(state)
        assert result == "done"

    def test_should_revise_not_approved(self):
        """Test routing when documentation needs revision."""
        state = create_initial_state("./src")
        state["review_feedback"] = ReviewFeedback(
            is_approved=False,
            issues=["Missing content"],
        ).to_dict()

        result = should_revise(state)
        assert result == "revise"

    def test_should_revise_no_feedback(self):
        """Test routing with no feedback (defaults to revise)."""
        state = create_initial_state("./src")

        result = should_revise(state)
        assert result == "revise"


class TestCreateWorkflow:
    """Tests for workflow creation."""

    def test_create_workflow_default_agents(self):
        """Test creating workflow with default agents."""
        graph = create_workflow()

        assert graph is not None
        # Check nodes exist
        assert "analyze" in graph.nodes
        assert "extract" in graph.nodes
        assert "write" in graph.nodes
        assert "review" in graph.nodes

    def test_create_workflow_custom_agents(self):
        """Test creating workflow with custom agents."""
        from docgen.agents import AnalyzerAgent, ExtractorAgent

        custom_analyzer = AnalyzerAgent(llm=MagicMock())
        custom_extractor = ExtractorAgent(llm=MagicMock())

        graph = create_workflow(
            analyzer=custom_analyzer,
            extractor=custom_extractor,
        )

        assert graph is not None


class TestCompileWorkflow:
    """Tests for workflow compilation."""

    def test_compile_workflow(self):
        """Test compiling the workflow."""
        compiled = compile_workflow()

        assert compiled is not None
        # Compiled workflow should have invoke method
        assert hasattr(compiled, "invoke") or hasattr(compiled, "ainvoke")


class TestGetWorkflowDiagram:
    """Tests for workflow diagram generation."""

    def test_get_workflow_diagram(self):
        """Test getting Mermaid diagram."""
        diagram = get_workflow_diagram()

        assert "```mermaid" in diagram
        assert "graph TD" in diagram
        assert "analyze" in diagram.lower()
        assert "extract" in diagram.lower()
        assert "write" in diagram.lower()
        assert "review" in diagram.lower()
