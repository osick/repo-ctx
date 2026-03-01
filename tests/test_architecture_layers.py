"""Tests for architecture layer detection and rules."""
import pytest
import tempfile
import os
from repo_ctx.analysis.architecture import (
    DSMBuilder,
    CycleDetector,
)
from repo_ctx.analysis.architecture_rules import (
    LayerDetector,
    LayerInfo,
    ArchitectureRules,
    ArchitectureViolation,
    RuleParser,
)
from repo_ctx.analysis.dependency_graph import GraphNode, GraphEdge, DependencyGraphResult, GraphType


class TestLayerDetector:
    """Tests for automatic layer detection."""

    def test_empty_graph_no_layers(self):
        """Empty graph has no layers."""
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={},
            edges=[]
        )
        detector = LayerDetector()
        layers = detector.detect(result)

        assert len(layers) == 0

    def test_single_node_one_layer(self):
        """Single node is its own layer."""
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "A": GraphNode(id="A", label="A", node_type="class")
            },
            edges=[]
        )
        detector = LayerDetector()
        layers = detector.detect(result)

        assert len(layers) == 1
        assert "A" in layers[0].nodes

    def test_linear_chain_multiple_layers(self):
        """Linear dependency chain A -> B -> C creates 3 layers."""
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "A": GraphNode(id="A", label="A", node_type="class"),
                "B": GraphNode(id="B", label="B", node_type="class"),
                "C": GraphNode(id="C", label="C", node_type="class"),
            },
            edges=[
                GraphEdge(source="A", target="B", relation="imports"),
                GraphEdge(source="B", target="C", relation="imports"),
            ]
        )
        detector = LayerDetector()
        layers = detector.detect(result)

        # Should have 3 layers: C (bottom), B (middle), A (top)
        assert len(layers) == 3
        # Bottom layer (providers) should contain C
        assert "C" in layers[0].nodes
        # Top layer (consumers) should contain A
        assert "A" in layers[-1].nodes

    def test_diamond_dependency(self):
        """Diamond pattern: A -> B, A -> C, B -> D, C -> D."""
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "A": GraphNode(id="A", label="A", node_type="class"),
                "B": GraphNode(id="B", label="B", node_type="class"),
                "C": GraphNode(id="C", label="C", node_type="class"),
                "D": GraphNode(id="D", label="D", node_type="class"),
            },
            edges=[
                GraphEdge(source="A", target="B", relation="imports"),
                GraphEdge(source="A", target="C", relation="imports"),
                GraphEdge(source="B", target="D", relation="imports"),
                GraphEdge(source="C", target="D", relation="imports"),
            ]
        )
        detector = LayerDetector()
        layers = detector.detect(result)

        # D at bottom, B and C in middle, A at top
        assert len(layers) >= 2
        assert "D" in layers[0].nodes
        assert "A" in layers[-1].nodes

    def test_cycle_collapses_to_single_layer(self):
        """Nodes in a cycle should be in the same layer."""
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "A": GraphNode(id="A", label="A", node_type="class"),
                "B": GraphNode(id="B", label="B", node_type="class"),
                "C": GraphNode(id="C", label="C", node_type="class"),
            },
            edges=[
                GraphEdge(source="A", target="B", relation="imports"),
                GraphEdge(source="B", target="C", relation="imports"),
                GraphEdge(source="C", target="A", relation="imports"),
            ]
        )
        detector = LayerDetector()
        layers = detector.detect(result)

        # All nodes should be in the same layer due to cycle
        assert len(layers) == 1
        assert set(layers[0].nodes) == {"A", "B", "C"}

    def test_layer_names_assigned(self):
        """Layers get default names (Layer 0, Layer 1, etc.)."""
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "A": GraphNode(id="A", label="A", node_type="class"),
                "B": GraphNode(id="B", label="B", node_type="class"),
            },
            edges=[
                GraphEdge(source="A", target="B", relation="imports"),
            ]
        )
        detector = LayerDetector()
        layers = detector.detect(result)

        assert all(layer.name for layer in layers)

    def test_layer_level_ordering(self):
        """Layers should be ordered by level (0 = bottom)."""
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "A": GraphNode(id="A", label="A", node_type="class"),
                "B": GraphNode(id="B", label="B", node_type="class"),
                "C": GraphNode(id="C", label="C", node_type="class"),
            },
            edges=[
                GraphEdge(source="A", target="B", relation="imports"),
                GraphEdge(source="B", target="C", relation="imports"),
            ]
        )
        detector = LayerDetector()
        layers = detector.detect(result)

        for i, layer in enumerate(layers):
            assert layer.level == i


class TestArchitectureRules:
    """Tests for architecture rule enforcement."""

    def test_no_rules_no_violations(self):
        """No rules means no violations."""
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "A": GraphNode(id="A", label="A", node_type="class"),
                "B": GraphNode(id="B", label="B", node_type="class"),
            },
            edges=[
                GraphEdge(source="A", target="B", relation="imports"),
            ]
        )
        rules = ArchitectureRules()
        violations = rules.check(result)

        assert len(violations) == 0

    def test_layer_rule_violation(self):
        """Detect violation when lower layer depends on upper layer."""
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "ui.View": GraphNode(id="ui.View", label="View", node_type="class"),
                "data.Repository": GraphNode(id="data.Repository", label="Repository", node_type="class"),
            },
            edges=[
                # Data layer depending on UI layer - violation!
                GraphEdge(source="data.Repository", target="ui.View", relation="imports"),
            ]
        )

        rules = ArchitectureRules()
        rules.add_layer_rule("ui", above="data")  # UI above Data

        violations = rules.check(result)

        assert len(violations) == 1
        assert violations[0].rule_name == "layer_order"
        assert "data" in violations[0].source.lower() or "repository" in violations[0].source.lower()

    def test_forbidden_dependency_rule(self):
        """Detect forbidden dependencies."""
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "Controller": GraphNode(id="Controller", label="Controller", node_type="class"),
                "Database": GraphNode(id="Database", label="Database", node_type="class"),
            },
            edges=[
                GraphEdge(source="Controller", target="Database", relation="imports"),
            ]
        )

        rules = ArchitectureRules()
        rules.add_forbidden_rule("Controller", "Database")

        violations = rules.check(result)

        assert len(violations) == 1
        assert violations[0].rule_name == "forbidden"

    def test_allowed_dependency_rule(self):
        """No violation when dependency is explicitly allowed."""
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "Service": GraphNode(id="Service", label="Service", node_type="class"),
                "Repository": GraphNode(id="Repository", label="Repository", node_type="class"),
            },
            edges=[
                GraphEdge(source="Service", target="Repository", relation="imports"),
            ]
        )

        rules = ArchitectureRules()
        rules.add_allowed_rule("Service", "Repository")

        violations = rules.check(result)

        assert len(violations) == 0

    def test_pattern_matching_rules(self):
        """Rules can use patterns (wildcards)."""
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "com.app.ui.LoginView": GraphNode(id="com.app.ui.LoginView", label="LoginView", node_type="class"),
                "com.app.data.UserDao": GraphNode(id="com.app.data.UserDao", label="UserDao", node_type="class"),
            },
            edges=[
                GraphEdge(source="com.app.data.UserDao", target="com.app.ui.LoginView", relation="imports"),
            ]
        )

        rules = ArchitectureRules()
        rules.add_layer_rule("*.ui.*", above="*.data.*")

        violations = rules.check(result)

        assert len(violations) == 1

    def test_multiple_violations(self):
        """Multiple violations detected."""
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "A": GraphNode(id="A", label="A", node_type="class"),
                "B": GraphNode(id="B", label="B", node_type="class"),
                "C": GraphNode(id="C", label="C", node_type="class"),
            },
            edges=[
                GraphEdge(source="A", target="B", relation="imports"),
                GraphEdge(source="A", target="C", relation="imports"),
            ]
        )

        rules = ArchitectureRules()
        rules.add_forbidden_rule("A", "B")
        rules.add_forbidden_rule("A", "C")

        violations = rules.check(result)

        assert len(violations) == 2

    def test_violation_includes_location(self):
        """Violations include source location when available."""
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "A": GraphNode(id="A", label="A", node_type="class", metadata={"file": "src/a.py", "line_start": 10}),
                "B": GraphNode(id="B", label="B", node_type="class"),
            },
            edges=[
                GraphEdge(source="A", target="B", relation="imports", metadata={"line": 15}),
            ]
        )

        rules = ArchitectureRules()
        rules.add_forbidden_rule("A", "B")

        violations = rules.check(result)

        assert len(violations) == 1
        assert violations[0].file_path == "src/a.py"


class TestRuleParser:
    """Tests for architecture rule file parsing."""

    def test_parse_empty_rules(self):
        """Parse empty rules file."""
        yaml_content = ""
        parser = RuleParser()
        rules = parser.parse_yaml(yaml_content)

        assert rules is not None
        assert len(rules.layer_rules) == 0
        assert len(rules.forbidden_rules) == 0

    def test_parse_layer_rules(self):
        """Parse layer rules from YAML."""
        yaml_content = """
layers:
  - name: presentation
    above: business
  - name: business
    above: data
"""
        parser = RuleParser()
        rules = parser.parse_yaml(yaml_content)

        assert len(rules.layer_rules) == 2

    def test_parse_forbidden_rules(self):
        """Parse forbidden dependency rules."""
        yaml_content = """
forbidden:
  - from: "*.controller.*"
    to: "*.repository.*"
    reason: "Controllers should not access repositories directly"
"""
        parser = RuleParser()
        rules = parser.parse_yaml(yaml_content)

        assert len(rules.forbidden_rules) == 1

    def test_parse_allowed_rules(self):
        """Parse allowed dependency rules."""
        yaml_content = """
allowed:
  - from: "*.service.*"
    to: "*.repository.*"
"""
        parser = RuleParser()
        rules = parser.parse_yaml(yaml_content)

        assert len(rules.allowed_rules) == 1

    def test_parse_complete_rules_file(self):
        """Parse complete architecture rules file."""
        yaml_content = """
name: "Clean Architecture"
description: "Layered architecture with strict boundaries"

layers:
  - name: ui
    patterns: ["*.ui.*", "*.view.*", "*.controller.*"]
    above: domain
  - name: domain
    patterns: ["*.domain.*", "*.service.*", "*.usecase.*"]
    above: data
  - name: data
    patterns: ["*.data.*", "*.repository.*", "*.dao.*"]

forbidden:
  - from: "*.data.*"
    to: "*.ui.*"
    reason: "Data layer must not depend on UI"

allowed:
  - from: "*.ui.*"
    to: "*.domain.*"
"""
        parser = RuleParser()
        rules = parser.parse_yaml(yaml_content)

        assert rules.name == "Clean Architecture"
        assert len(rules.layer_rules) == 2
        assert len(rules.forbidden_rules) == 1
        assert len(rules.allowed_rules) == 1

    def test_parse_from_file(self):
        """Parse rules from file."""
        yaml_content = """
layers:
  - name: api
    above: core
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()

            try:
                parser = RuleParser()
                rules = parser.parse_file(f.name)
                assert len(rules.layer_rules) == 1
            finally:
                os.unlink(f.name)


class TestLayerInfo:
    """Tests for LayerInfo dataclass."""

    def test_layer_info_creation(self):
        """Create LayerInfo with all fields."""
        layer = LayerInfo(
            name="presentation",
            level=2,
            nodes=["View", "Controller"],
            patterns=["*.ui.*"]
        )

        assert layer.name == "presentation"
        assert layer.level == 2
        assert len(layer.nodes) == 2
        assert len(layer.patterns) == 1

    def test_layer_info_to_dict(self):
        """LayerInfo serializes to dict."""
        layer = LayerInfo(
            name="data",
            level=0,
            nodes=["Repository"],
            patterns=["*.data.*"]
        )

        d = layer.to_dict()

        assert d["name"] == "data"
        assert d["level"] == 0
        assert "Repository" in d["nodes"]


class TestArchitectureViolation:
    """Tests for ArchitectureViolation dataclass."""

    def test_violation_creation(self):
        """Create violation with required fields."""
        violation = ArchitectureViolation(
            rule_name="layer_order",
            source="DataAccess",
            target="ViewController",
            message="Data layer cannot depend on UI layer"
        )

        assert violation.rule_name == "layer_order"
        assert violation.source == "DataAccess"
        assert violation.target == "ViewController"

    def test_violation_with_location(self):
        """Violation with file location."""
        violation = ArchitectureViolation(
            rule_name="forbidden",
            source="A",
            target="B",
            message="Forbidden dependency",
            file_path="src/a.py",
            line=42
        )

        assert violation.file_path == "src/a.py"
        assert violation.line == 42

    def test_violation_to_dict(self):
        """Violation serializes to dict."""
        violation = ArchitectureViolation(
            rule_name="forbidden",
            source="A",
            target="B",
            message="Test",
            file_path="test.py",
            line=10
        )

        d = violation.to_dict()

        assert d["rule_name"] == "forbidden"
        assert d["file_path"] == "test.py"
        assert d["line"] == 10
