"""Tests for structural complexity metrics (XS)."""
import pytest
import tempfile
import os
import json
from datetime import datetime, timedelta
from repo_ctx.analysis.dependency_graph import GraphNode, GraphEdge, DependencyGraphResult, GraphType


class TestXSMetricsCalculation:
    """Tests for XS (eXcess Structural complexity) calculation."""

    def test_empty_graph_zero_xs(self):
        """Empty graph has zero XS."""
        from repo_ctx.analysis.structural_metrics import XSCalculator

        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={},
            edges=[]
        )
        calculator = XSCalculator()
        metrics = calculator.calculate(result)

        assert metrics.xs_score == 0.0

    def test_simple_graph_low_xs(self):
        """Simple linear graph has low XS."""
        from repo_ctx.analysis.structural_metrics import XSCalculator

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
        calculator = XSCalculator()
        metrics = calculator.calculate(result)

        # Simple graph should have low XS
        assert metrics.xs_score >= 0
        assert metrics.xs_score < 10  # Low threshold

    def test_cyclic_graph_higher_xs(self):
        """Graph with cycles has higher XS."""
        from repo_ctx.analysis.structural_metrics import XSCalculator

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
                GraphEdge(source="C", target="A", relation="imports"),  # Cycle!
            ]
        )
        calculator = XSCalculator()
        metrics = calculator.calculate(result)

        # Cyclic graph should have higher XS
        assert metrics.xs_score > 0
        assert metrics.cycle_count == 1
        assert metrics.cycle_contribution > 0

    def test_xs_components(self):
        """XS score is composed of multiple components."""
        from repo_ctx.analysis.structural_metrics import XSCalculator

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
        calculator = XSCalculator()
        metrics = calculator.calculate(result)

        # Verify components are calculated
        assert hasattr(metrics, 'cycle_contribution')
        assert hasattr(metrics, 'coupling_contribution')
        assert hasattr(metrics, 'size_contribution')

    def test_high_coupling_increases_xs(self):
        """High coupling (many edges per node) increases XS."""
        from repo_ctx.analysis.structural_metrics import XSCalculator

        # Create a densely connected graph (high coupling)
        # 5 nodes each connected to all others = 20 edges / 5 nodes = 4.0 avg coupling
        nodes = {}
        edges = []
        node_names = ["A", "B", "C", "D", "E"]
        for name in node_names:
            nodes[name] = GraphNode(id=name, label=name, node_type="class")

        # Fully connected (each node connects to all others)
        for source in node_names:
            for target in node_names:
                if source != target:
                    edges.append(GraphEdge(source=source, target=target, relation="imports"))

        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes=nodes,
            edges=edges
        )
        calculator = XSCalculator()
        metrics = calculator.calculate(result)

        # High coupling (4.0 avg) exceeds threshold (3.0), should contribute to XS
        assert metrics.avg_coupling > 3.0  # Exceeds threshold
        assert metrics.coupling_contribution > 0

    def test_xs_grade_assignment(self):
        """XS score is assigned a grade (A-F)."""
        from repo_ctx.analysis.structural_metrics import XSCalculator

        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "A": GraphNode(id="A", label="A", node_type="class"),
            },
            edges=[]
        )
        calculator = XSCalculator()
        metrics = calculator.calculate(result)

        # Should have a grade
        assert metrics.grade in ["A", "B", "C", "D", "F"]

    def test_xs_with_violations(self):
        """Architecture violations increase XS."""
        from repo_ctx.analysis.structural_metrics import XSCalculator, XSInput
        from repo_ctx.analysis.architecture_rules import ArchitectureViolation

        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "data.Repo": GraphNode(id="data.Repo", label="Repo", node_type="class"),
                "ui.View": GraphNode(id="ui.View", label="View", node_type="class"),
            },
            edges=[
                GraphEdge(source="data.Repo", target="ui.View", relation="imports"),
            ]
        )

        violations = [
            ArchitectureViolation(
                rule_name="layer_order",
                source="data.Repo",
                target="ui.View",
                message="Data layer cannot depend on UI"
            )
        ]

        calculator = XSCalculator()
        xs_input = XSInput(graph=result, violations=violations)
        metrics = calculator.calculate_from_input(xs_input)

        assert metrics.violation_count == 1
        assert metrics.violation_contribution > 0

    def test_xs_to_dict(self):
        """XS metrics serializes to dictionary."""
        from repo_ctx.analysis.structural_metrics import XSCalculator

        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes={
                "A": GraphNode(id="A", label="A", node_type="class"),
            },
            edges=[]
        )
        calculator = XSCalculator()
        metrics = calculator.calculate(result)

        d = metrics.to_dict()

        assert "xs_score" in d
        assert "grade" in d
        assert "components" in d


class TestMetricsComparison:
    """Tests for comparing metrics over time."""

    def test_compare_two_snapshots(self):
        """Compare metrics between two snapshots."""
        from repo_ctx.analysis.structural_metrics import XSMetrics, MetricsComparison

        old = XSMetrics(
            xs_score=50.0,
            grade="C",
            node_count=10,
            edge_count=15,
            cycle_count=2,
            violation_count=3,
            cycle_contribution=20.0,
            coupling_contribution=15.0,
            size_contribution=10.0,
            violation_contribution=5.0,
            avg_coupling=1.5
        )

        new = XSMetrics(
            xs_score=35.0,
            grade="B",
            node_count=12,
            edge_count=14,
            cycle_count=1,
            violation_count=2,
            cycle_contribution=10.0,
            coupling_contribution=12.0,
            size_contribution=10.0,
            violation_contribution=3.0,
            avg_coupling=1.2
        )

        comparison = MetricsComparison.compare(old, new)

        assert comparison.xs_delta == -15.0  # Improved
        assert comparison.improved is True
        assert comparison.cycle_delta == -1
        assert comparison.violation_delta == -1

    def test_degradation_detected(self):
        """Detect when metrics degrade."""
        from repo_ctx.analysis.structural_metrics import XSMetrics, MetricsComparison

        old = XSMetrics(
            xs_score=30.0,
            grade="B",
            node_count=10,
            edge_count=10,
            cycle_count=0,
            violation_count=0,
            cycle_contribution=0.0,
            coupling_contribution=10.0,
            size_contribution=10.0,
            violation_contribution=0.0,
            avg_coupling=1.0
        )

        new = XSMetrics(
            xs_score=60.0,
            grade="C",
            node_count=15,
            edge_count=25,
            cycle_count=3,
            violation_count=5,
            cycle_contribution=25.0,
            coupling_contribution=15.0,
            size_contribution=12.0,
            violation_contribution=8.0,
            avg_coupling=1.7
        )

        comparison = MetricsComparison.compare(old, new)

        assert comparison.xs_delta == 30.0  # Degraded
        assert comparison.improved is False
        assert comparison.degraded is True

    def test_comparison_to_dict(self):
        """Comparison serializes to dictionary."""
        from repo_ctx.analysis.structural_metrics import XSMetrics, MetricsComparison

        old = XSMetrics(
            xs_score=50.0, grade="C", node_count=10, edge_count=15,
            cycle_count=2, violation_count=3, cycle_contribution=20.0,
            coupling_contribution=15.0, size_contribution=10.0,
            violation_contribution=5.0, avg_coupling=1.5
        )
        new = XSMetrics(
            xs_score=40.0, grade="B", node_count=10, edge_count=12,
            cycle_count=1, violation_count=2, cycle_contribution=10.0,
            coupling_contribution=15.0, size_contribution=10.0,
            violation_contribution=5.0, avg_coupling=1.2
        )

        comparison = MetricsComparison.compare(old, new)
        d = comparison.to_dict()

        assert "xs_delta" in d
        assert "improved" in d
        assert "degraded" in d


class TestMetricsGrading:
    """Tests for XS grade assignment."""

    def test_grade_a_for_excellent(self):
        """Grade A for excellent (low XS)."""
        from repo_ctx.analysis.structural_metrics import XSGrader

        grader = XSGrader()
        assert grader.grade(0) == "A"
        assert grader.grade(10) == "A"

    def test_grade_b_for_good(self):
        """Grade B for good XS."""
        from repo_ctx.analysis.structural_metrics import XSGrader

        grader = XSGrader()
        assert grader.grade(25) == "B"

    def test_grade_c_for_moderate(self):
        """Grade C for moderate XS."""
        from repo_ctx.analysis.structural_metrics import XSGrader

        grader = XSGrader()
        assert grader.grade(50) == "C"

    def test_grade_d_for_poor(self):
        """Grade D for poor XS."""
        from repo_ctx.analysis.structural_metrics import XSGrader

        grader = XSGrader()
        assert grader.grade(75) == "D"

    def test_grade_f_for_critical(self):
        """Grade F for critical XS."""
        from repo_ctx.analysis.structural_metrics import XSGrader

        grader = XSGrader()
        assert grader.grade(100) == "F"
        assert grader.grade(200) == "F"


class TestHotspotDetection:
    """Tests for detecting complexity hotspots."""

    def test_detect_hub_node(self):
        """Detect nodes with high coupling (hubs)."""
        from repo_ctx.analysis.structural_metrics import HotspotDetector

        # Hub node with many connections
        nodes = {"Hub": GraphNode(id="Hub", label="Hub", node_type="class")}
        edges = []
        for i in range(10):
            node_id = f"Node{i}"
            nodes[node_id] = GraphNode(id=node_id, label=node_id, node_type="class")
            edges.append(GraphEdge(source="Hub", target=node_id, relation="imports"))

        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes=nodes,
            edges=edges
        )

        detector = HotspotDetector()
        hotspots = detector.detect(result)

        # Hub should be detected as hotspot
        hub_hotspots = [h for h in hotspots if h.node_id == "Hub"]
        assert len(hub_hotspots) > 0
        assert hub_hotspots[0].reason == "high_coupling"

    def test_detect_cycle_participant(self):
        """Detect nodes participating in cycles."""
        from repo_ctx.analysis.structural_metrics import HotspotDetector

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

        detector = HotspotDetector()
        hotspots = detector.detect(result)

        # All cycle participants should be hotspots
        cycle_hotspots = [h for h in hotspots if h.reason == "cycle_participant"]
        assert len(cycle_hotspots) >= 1

    def test_hotspot_to_dict(self):
        """Hotspot serializes to dictionary."""
        from repo_ctx.analysis.structural_metrics import Hotspot

        hotspot = Hotspot(
            node_id="Hub",
            node_label="Hub",
            reason="high_coupling",
            severity=8.5,
            details={"connections": 10}
        )

        d = hotspot.to_dict()

        assert d["node_id"] == "Hub"
        assert d["reason"] == "high_coupling"
        assert d["severity"] == 8.5


class TestAnalyzeStructure:
    """Tests for the main analyze_structure function."""

    def test_analyze_returns_complete_report(self):
        """analyze_structure returns complete metrics report."""
        from repo_ctx.analysis.structural_metrics import analyze_structure

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

        report = analyze_structure(result)

        assert "metrics" in report
        assert "hotspots" in report
        assert "summary" in report
        assert report["metrics"]["xs_score"] >= 0

    def test_analyze_with_violations(self):
        """analyze_structure with violations."""
        from repo_ctx.analysis.structural_metrics import analyze_structure
        from repo_ctx.analysis.architecture_rules import ArchitectureViolation

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

        violations = [
            ArchitectureViolation(
                rule_name="forbidden",
                source="A",
                target="B",
                message="Forbidden"
            )
        ]

        report = analyze_structure(result, violations=violations)

        assert report["metrics"]["violation_count"] == 1
