"""
Tests for DocGen state module.
"""

import pytest
from docgen.state import (
    DocGenState,
    DocGenPhase,
    DocGenOptions,
    Symbol,
    Dependency,
    Document,
    DomainEntity,
    DomainModel,
    DocSection,
    ReviewFeedback,
    create_initial_state,
)


class TestSymbol:
    """Tests for Symbol dataclass."""

    def test_symbol_creation(self):
        """Test creating a Symbol."""
        symbol = Symbol(
            name="MyClass",
            symbol_type="class",
            signature="class MyClass",
            docstring="A test class",
            file_path="src/test.py",
            line_number=10,
        )

        assert symbol.name == "MyClass"
        assert symbol.symbol_type == "class"
        assert symbol.visibility == "public"

    def test_symbol_to_dict(self):
        """Test Symbol serialization."""
        symbol = Symbol(name="func", symbol_type="function")
        data = symbol.to_dict()

        assert data["name"] == "func"
        assert data["symbol_type"] == "function"
        assert "visibility" in data


class TestDependency:
    """Tests for Dependency dataclass."""

    def test_dependency_creation(self):
        """Test creating a Dependency."""
        dep = Dependency(
            source="ClassA",
            target="ClassB",
            dependency_type="imports",
        )

        assert dep.source == "ClassA"
        assert dep.target == "ClassB"
        assert dep.dependency_type == "imports"

    def test_dependency_to_dict(self):
        """Test Dependency serialization."""
        dep = Dependency(source="A", target="B", dependency_type="uses")
        data = dep.to_dict()

        assert data["source"] == "A"
        assert data["target"] == "B"


class TestDocument:
    """Tests for Document dataclass."""

    def test_document_creation(self):
        """Test creating a Document."""
        doc = Document(
            title="README",
            content="# Hello",
            path="README.md",
            doc_type="readme",
        )

        assert doc.title == "README"
        assert doc.content == "# Hello"
        assert doc.doc_type == "readme"


class TestDomainEntity:
    """Tests for DomainEntity dataclass."""

    def test_entity_creation(self):
        """Test creating a DomainEntity."""
        entity = DomainEntity(
            name="User",
            description="A system user",
            related_symbols=["User", "UserService"],
            attributes=["id", "name", "email"],
            relationships=["has many Orders"],
        )

        assert entity.name == "User"
        assert len(entity.related_symbols) == 2
        assert len(entity.attributes) == 3

    def test_entity_defaults(self):
        """Test DomainEntity default values."""
        entity = DomainEntity(name="Test", description="Test entity")

        assert entity.related_symbols == []
        assert entity.attributes == []
        assert entity.relationships == []


class TestDomainModel:
    """Tests for DomainModel dataclass."""

    def test_domain_model_creation(self):
        """Test creating a DomainModel."""
        model = DomainModel(
            entities=[
                DomainEntity(name="User", description="A user"),
            ],
            processes=[{"name": "Login", "steps": ["Enter credentials"]}],
            glossary={"User": "A registered person"},
        )

        assert len(model.entities) == 1
        assert len(model.processes) == 1
        assert "User" in model.glossary

    def test_domain_model_to_dict(self):
        """Test DomainModel serialization."""
        model = DomainModel()
        data = model.to_dict()

        assert "entities" in data
        assert "processes" in data
        assert "glossary" in data


class TestDocSection:
    """Tests for DocSection dataclass."""

    def test_section_creation(self):
        """Test creating a DocSection."""
        section = DocSection(
            title="Overview",
            content="## Overview\n\nContent here.",
            section_type="overview",
            order=0,
        )

        assert section.title == "Overview"
        assert section.section_type == "overview"
        assert section.order == 0

    def test_section_with_diagrams(self):
        """Test DocSection with diagrams."""
        section = DocSection(
            title="Architecture",
            content="## Architecture",
            section_type="architecture",
            diagrams=["```mermaid\ngraph TD\nA-->B\n```"],
        )

        assert len(section.diagrams) == 1


class TestReviewFeedback:
    """Tests for ReviewFeedback dataclass."""

    def test_feedback_approved(self):
        """Test approved review feedback."""
        feedback = ReviewFeedback(is_approved=True)

        assert feedback.is_approved
        assert feedback.issues == []

    def test_feedback_with_issues(self):
        """Test review feedback with issues."""
        feedback = ReviewFeedback(
            is_approved=False,
            issues=["Missing entity documentation"],
            suggestions=["Add more detail to User section"],
            sections_to_revise=["User"],
        )

        assert not feedback.is_approved
        assert len(feedback.issues) == 1
        assert len(feedback.sections_to_revise) == 1


class TestDocGenOptions:
    """Tests for DocGenOptions dataclass."""

    def test_default_options(self):
        """Test default option values."""
        options = DocGenOptions()

        assert options.model == "claude-sonnet-4"
        assert options.output_format == "markdown"
        assert options.include_diagrams is True
        assert options.max_revisions == 2

    def test_custom_options(self):
        """Test custom option values."""
        options = DocGenOptions(
            model="claude-opus-4",
            max_revisions=5,
            from_index=True,
        )

        assert options.model == "claude-opus-4"
        assert options.max_revisions == 5
        assert options.from_index is True


class TestCreateInitialState:
    """Tests for create_initial_state function."""

    def test_create_state_minimal(self):
        """Test creating state with minimal params."""
        state = create_initial_state(target_path="./src")

        assert state["target_path"] == "./src"
        assert state["output_path"] is None
        assert state["phase"] == DocGenPhase.INITIALIZING.value
        assert state["symbols"] == []
        assert state["is_complete"] is False

    def test_create_state_with_options(self):
        """Test creating state with custom options."""
        options = DocGenOptions(model="claude-opus-4", max_revisions=3)
        state = create_initial_state(
            target_path="/owner/repo",
            output_path="./docs",
            options=options,
        )

        assert state["target_path"] == "/owner/repo"
        assert state["output_path"] == "./docs"
        assert state["options"]["model"] == "claude-opus-4"
        assert state["options"]["max_revisions"] == 3


class TestDocGenPhase:
    """Tests for DocGenPhase enum."""

    def test_phase_values(self):
        """Test phase enum values."""
        assert DocGenPhase.INITIALIZING.value == "initializing"
        assert DocGenPhase.ANALYZING.value == "analyzing"
        assert DocGenPhase.EXTRACTING.value == "extracting"
        assert DocGenPhase.WRITING.value == "writing"
        assert DocGenPhase.REVIEWING.value == "reviewing"
        assert DocGenPhase.COMPLETED.value == "completed"
