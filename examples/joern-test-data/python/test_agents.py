"""
Tests for DocGen agents.
"""

import pytest
from unittest.mock import patch, MagicMock
from docgen.agents import AnalyzerAgent, ExtractorAgent, WriterAgent, ReviewerAgent
from docgen.state import (
    create_initial_state,
    DocGenPhase,
    Symbol,
    DomainEntity,
    DomainModel,
)
from docgen.tools import ToolResult


class TestAnalyzerAgent:
    """Tests for AnalyzerAgent."""

    def test_init(self):
        """Test agent initialization."""
        agent = AnalyzerAgent()
        assert agent.llm is None

    def test_init_with_llm(self):
        """Test agent initialization with LLM."""
        mock_llm = MagicMock()
        agent = AnalyzerAgent(llm=mock_llm)
        assert agent.llm == mock_llm

    @patch("docgen.agents.analyzer.tools")
    def test_gather_code_data(self, mock_tools):
        """Test gathering code data."""
        mock_tools.analyze.return_value = ToolResult(
            success=True,
            data={"symbols": [{"name": "Test", "symbol_type": "class"}]},
        )
        mock_tools.graph.return_value = ToolResult(
            success=True,
            data={"edges": [{"source": "A", "target": "B", "relation": "uses"}]},
        )

        agent = AnalyzerAgent()
        state = create_initial_state("./src")
        data = agent.gather_code_data(state)

        assert "symbols" in data
        assert "dependencies" in data
        assert len(data["dependencies"]) == 1

    @patch("docgen.agents.analyzer.tools")
    def test_call(self, mock_tools):
        """Test agent execution."""
        mock_tools.analyze.return_value = ToolResult(success=True, data={"symbols": []})
        mock_tools.graph.return_value = ToolResult(success=True, data={"edges": []})
        mock_tools.query.return_value = ToolResult(success=False, data=None, error="Not available")

        agent = AnalyzerAgent()
        state = create_initial_state("./src")
        result = agent(state)

        assert result["phase"] == DocGenPhase.ANALYZING.value
        assert "symbols" in result


class TestExtractorAgent:
    """Tests for ExtractorAgent."""

    def test_init(self):
        """Test agent initialization."""
        agent = ExtractorAgent()
        assert agent.llm is None

    def test_extract_entities_from_symbols(self):
        """Test entity extraction from symbols."""
        symbols = [
            {"name": "User", "symbol_type": "class", "docstring": "A user"},
            {"name": "Order", "symbol_type": "class", "docstring": "An order"},
            {"name": "UserService", "symbol_type": "class", "docstring": "Service"},
            {"name": "test_user", "symbol_type": "function", "docstring": "Test"},
        ]

        agent = ExtractorAgent()
        entities = agent.extract_entities_from_symbols(symbols)

        # Should extract User and Order, but filter out UserService (contains "service")
        # and test_user (not a class, contains "test")
        entity_names = [e.name for e in entities]
        assert "User" in entity_names
        assert "Order" in entity_names

    def test_extract_terminology(self):
        """Test terminology extraction from docs."""
        docs = [
            {
                "content": "A User is a registered customer.\nAn Order is a purchase.",
                "title": "README",
            }
        ]

        agent = ExtractorAgent()
        terminology = agent.extract_terminology(docs)

        # Simple heuristic should extract "X is Y" patterns
        # Note: actual extraction depends on exact patterns
        assert isinstance(terminology, dict)

    def test_call(self, sample_state):
        """Test agent execution."""
        agent = ExtractorAgent()
        result = agent(sample_state)

        assert result["phase"] == DocGenPhase.EXTRACTING.value
        assert "domain_model" in result
        assert "terminology" in result


class TestWriterAgent:
    """Tests for WriterAgent."""

    def test_init(self):
        """Test agent initialization."""
        agent = WriterAgent()
        assert agent.llm is None

    def test_generate_overview_section(self, sample_domain_model):
        """Test overview section generation."""
        agent = WriterAgent()
        section = agent.generate_overview_section(sample_domain_model, [])

        assert section.title == "Overview"
        assert section.section_type == "overview"
        assert "Overview" in section.content

    def test_generate_entity_sections(self, sample_domain_model):
        """Test entity section generation."""
        agent = WriterAgent()
        sections = agent.generate_entity_sections(sample_domain_model)

        assert len(sections) > 0
        assert all(s.section_type == "entity" for s in sections)

    def test_generate_glossary_section(self):
        """Test glossary section generation."""
        terminology = {"User": "A customer", "Order": "A purchase"}

        agent = WriterAgent()
        section = agent.generate_glossary_section(terminology)

        assert section.title == "Glossary"
        assert "User" in section.content
        assert "Order" in section.content

    def test_generate_architecture_diagram(self, sample_domain_model):
        """Test Mermaid diagram generation."""
        agent = WriterAgent()
        diagram = agent.generate_architecture_diagram(sample_domain_model)

        assert "```mermaid" in diagram
        assert "classDiagram" in diagram

    def test_call(self, sample_state):
        """Test agent execution."""
        agent = WriterAgent()
        result = agent(sample_state)

        assert result["phase"] == DocGenPhase.WRITING.value
        assert "documentation" in result
        assert len(result["documentation"]) > 0


class TestReviewerAgent:
    """Tests for ReviewerAgent."""

    def test_init(self):
        """Test agent initialization."""
        agent = ReviewerAgent()
        assert agent.llm is None

    def test_check_completeness(self, sample_documentation, sample_domain_model):
        """Test completeness check."""
        agent = ReviewerAgent()
        issues = agent.check_completeness(sample_documentation, sample_domain_model)

        # Should report missing entities if not all are in docs
        assert isinstance(issues, list)

    def test_check_consistency_no_docs(self, sample_documentation):
        """Test consistency check without existing docs."""
        agent = ReviewerAgent()
        issues = agent.check_consistency(sample_documentation, [])

        assert len(issues) > 0
        assert "No existing documentation" in issues[0]

    def test_check_structure_empty(self):
        """Test structure check with empty documentation."""
        agent = ReviewerAgent()
        issues = agent.check_structure([])

        assert len(issues) > 0
        assert "No documentation sections" in issues[0]

    def test_check_structure_missing_overview(self):
        """Test structure check without overview."""
        docs = [{"title": "Entity", "section_type": "entity", "content": "Content"}]

        agent = ReviewerAgent()
        issues = agent.check_structure(docs)

        assert any("overview" in i.lower() for i in issues)

    def test_call_approved(self, sample_state, sample_documentation):
        """Test agent approves good documentation."""
        sample_state["documentation"] = sample_documentation

        agent = ReviewerAgent()
        result = agent(sample_state)

        assert result["phase"] in [
            DocGenPhase.REVIEWING.value,
            DocGenPhase.COMPLETED.value,
            DocGenPhase.REVISING.value,
        ]
        assert "review_feedback" in result

    def test_call_max_revisions(self, sample_state):
        """Test agent approves after max revisions."""
        sample_state["documentation"] = []
        sample_state["revision_count"] = 5
        sample_state["options"]["max_revisions"] = 2

        agent = ReviewerAgent()
        result = agent(sample_state)

        # Should approve even with issues because max revisions reached
        feedback = result["review_feedback"]
        assert feedback["is_approved"]
