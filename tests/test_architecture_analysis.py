"""Tests for architecture analysis: DSM and cycle detection."""
import pytest
from repo_ctx.analysis.architecture import (
    DSMBuilder,
    CycleDetector,
    DSMResult,
    CycleInfo,
    BreakupSuggestion
)
from repo_ctx.analysis.dependency_graph import GraphNode, GraphEdge, DependencyGraphResult, GraphType


class TestDSMBuilder:
    """Tests for Dependency Structure Matrix generation."""

    def test_empty_graph(self):
        """DSM of empty graph."""
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={},
            edges=[]
        )
        builder = DSMBuilder()
        dsm = builder.build(result)

        assert dsm.size == 0
        assert dsm.matrix == []
        assert dsm.labels == []

    def test_single_node_no_edges(self):
        """DSM with single node, no dependencies."""
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "A": GraphNode(id="A", label="A", node_type="class")
            },
            edges=[]
        )
        builder = DSMBuilder()
        dsm = builder.build(result)

        assert dsm.size == 1
        assert dsm.matrix == [[0]]
        assert dsm.labels == ["A"]

    def test_linear_dependency(self):
        """DSM with linear dependencies: A -> B -> C."""
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
        builder = DSMBuilder()
        dsm = builder.build(result)

        assert dsm.size == 3
        # After topological sort: C, B, A (providers first)
        # Or any valid layered order
        assert dsm.is_layered()  # No cycles = triangular matrix

    def test_cyclic_dependency(self):
        """DSM with cyclic dependency: A -> B -> A."""
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
                GraphEdge(source="B", target="A", relation="imports"),
            ]
        )
        builder = DSMBuilder()
        dsm = builder.build(result)

        assert dsm.size == 2
        assert not dsm.is_layered()  # Has cycle
        assert len(dsm.cycles) == 1

    def test_complex_graph_with_cycles(self):
        """DSM with multiple components and cycles."""
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
                GraphEdge(source="B", target="C", relation="imports"),
                GraphEdge(source="C", target="A", relation="imports"),  # Cycle: A-B-C
                GraphEdge(source="D", target="A", relation="imports"),  # D depends on cycle
            ]
        )
        builder = DSMBuilder()
        dsm = builder.build(result)

        assert dsm.size == 4
        assert not dsm.is_layered()
        assert len(dsm.cycles) >= 1

    def test_dsm_to_text(self):
        """Test text output format."""
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
        builder = DSMBuilder()
        dsm = builder.build(result)
        text = dsm.to_text()

        assert "A" in text
        assert "B" in text
        assert isinstance(text, str)

    def test_dsm_to_json(self):
        """Test JSON output format."""
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
        builder = DSMBuilder()
        dsm = builder.build(result)
        json_data = dsm.to_dict()

        assert "matrix" in json_data
        assert "labels" in json_data
        assert "cycles" in json_data
        assert "is_layered" in json_data


class TestCycleDetector:
    """Tests for cycle detection using Tarjan's algorithm."""

    def test_no_cycles(self):
        """Detect no cycles in acyclic graph."""
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
        detector = CycleDetector()
        cycles = detector.detect(result)

        assert len(cycles) == 0

    def test_simple_cycle(self):
        """Detect simple 2-node cycle."""
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
                GraphEdge(source="B", target="A", relation="imports"),
            ]
        )
        detector = CycleDetector()
        cycles = detector.detect(result)

        assert len(cycles) == 1
        assert set(cycles[0].nodes) == {"A", "B"}

    def test_self_loop(self):
        """Detect self-referencing node."""
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "A": GraphNode(id="A", label="A", node_type="class"),
            },
            edges=[
                GraphEdge(source="A", target="A", relation="imports"),
            ]
        )
        detector = CycleDetector()
        cycles = detector.detect(result)

        assert len(cycles) == 1
        assert cycles[0].nodes == ["A"]

    def test_multiple_cycles(self):
        """Detect multiple independent cycles."""
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
                # Cycle 1: A <-> B
                GraphEdge(source="A", target="B", relation="imports"),
                GraphEdge(source="B", target="A", relation="imports"),
                # Cycle 2: C <-> D
                GraphEdge(source="C", target="D", relation="imports"),
                GraphEdge(source="D", target="C", relation="imports"),
            ]
        )
        detector = CycleDetector()
        cycles = detector.detect(result)

        assert len(cycles) == 2

    def test_nested_cycle(self):
        """Detect nested cycle: A -> B -> C -> A."""
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
        detector = CycleDetector()
        cycles = detector.detect(result)

        assert len(cycles) == 1
        assert len(cycles[0].nodes) == 3
        assert set(cycles[0].nodes) == {"A", "B", "C"}

    def test_cycle_with_breakup_suggestions(self):
        """Get breakup suggestions for cycle."""
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
                GraphEdge(source="B", target="A", relation="imports"),
            ]
        )
        detector = CycleDetector()
        cycles = detector.detect(result)

        assert len(cycles) == 1
        suggestions = cycles[0].breakup_suggestions
        assert len(suggestions) > 0
        assert all(isinstance(s, BreakupSuggestion) for s in suggestions)

    def test_cycle_impact_score(self):
        """Cycles have impact scores based on node count and edge weight."""
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
        detector = CycleDetector()
        cycles = detector.detect(result)

        assert len(cycles) == 1
        assert cycles[0].impact_score > 0


class TestCycleInfo:
    """Tests for CycleInfo dataclass."""

    def test_cycle_info_edges(self):
        """CycleInfo contains edges forming the cycle."""
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
                GraphEdge(source="B", target="A", relation="imports"),
            ]
        )
        detector = CycleDetector()
        cycles = detector.detect(result)

        assert len(cycles[0].edges) == 2


class TestBreakupSuggestion:
    """Tests for cycle breakup suggestions."""

    def test_suggestion_has_edge_to_remove(self):
        """Breakup suggestion specifies edge to remove."""
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
                GraphEdge(source="B", target="A", relation="imports"),
            ]
        )
        detector = CycleDetector()
        cycles = detector.detect(result)
        suggestion = cycles[0].breakup_suggestions[0]

        assert suggestion.edge_to_remove is not None
        assert suggestion.edge_to_remove.source in ["A", "B"]
        assert suggestion.edge_to_remove.target in ["A", "B"]

    def test_suggestion_has_reason(self):
        """Breakup suggestion includes reason/rationale."""
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
                GraphEdge(source="B", target="A", relation="imports"),
            ]
        )
        detector = CycleDetector()
        cycles = detector.detect(result)
        suggestion = cycles[0].breakup_suggestions[0]

        assert suggestion.reason is not None
        assert len(suggestion.reason) > 0

    def test_suggestions_sorted_by_impact(self):
        """Suggestions sorted by minimal impact (best first)."""
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
        detector = CycleDetector()
        cycles = detector.detect(result)
        suggestions = cycles[0].breakup_suggestions

        # Suggestions should be sorted by impact (ascending)
        if len(suggestions) > 1:
            for i in range(len(suggestions) - 1):
                assert suggestions[i].impact <= suggestions[i + 1].impact
