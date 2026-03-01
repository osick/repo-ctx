"""Structural complexity metrics (XS - eXcess Structural complexity).

Provides Structure101-style complexity measurement including:
- XS score calculation (cycles + coupling + violations + size)
- Grade assignment (A-F)
- Hotspot detection
- Metrics comparison over time
- Coupling metrics (Ca, Ce, Instability, Abstractness)
"""
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Set
from collections import defaultdict

from .dependency_graph import DependencyGraphResult, GraphNode, GraphEdge


@dataclass
class Hotspot:
    """A complexity hotspot in the code."""
    node_id: str
    node_label: str
    reason: str  # high_coupling, cycle_participant, violation_source
    severity: float  # 0-10 scale
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "node_id": self.node_id,
            "node_label": self.node_label,
            "reason": self.reason,
            "severity": self.severity,
            "details": self.details
        }


@dataclass
class XSMetrics:
    """eXcess Structural complexity metrics."""
    xs_score: float  # Total XS score (0-100+)
    grade: str  # A-F
    node_count: int
    edge_count: int
    cycle_count: int
    violation_count: int
    cycle_contribution: float
    coupling_contribution: float
    size_contribution: float
    violation_contribution: float
    avg_coupling: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "xs_score": round(self.xs_score, 2),
            "grade": self.grade,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "cycle_count": self.cycle_count,
            "violation_count": self.violation_count,
            "avg_coupling": round(self.avg_coupling, 2),
            "components": {
                "cycle_contribution": round(self.cycle_contribution, 2),
                "coupling_contribution": round(self.coupling_contribution, 2),
                "size_contribution": round(self.size_contribution, 2),
                "violation_contribution": round(self.violation_contribution, 2)
            }
        }


@dataclass
class XSInput:
    """Input for XS calculation with optional violations."""
    graph: DependencyGraphResult
    violations: List[Any] = field(default_factory=list)  # ArchitectureViolation


@dataclass
class MetricsComparison:
    """Comparison between two XS metrics snapshots."""
    xs_delta: float
    grade_old: str
    grade_new: str
    improved: bool
    degraded: bool
    cycle_delta: int
    violation_delta: int
    node_delta: int
    edge_delta: int

    @classmethod
    def compare(cls, old: XSMetrics, new: XSMetrics) -> "MetricsComparison":
        """Compare two metrics snapshots."""
        xs_delta = new.xs_score - old.xs_score
        return cls(
            xs_delta=xs_delta,
            grade_old=old.grade,
            grade_new=new.grade,
            improved=xs_delta < 0,
            degraded=xs_delta > 0,
            cycle_delta=new.cycle_count - old.cycle_count,
            violation_delta=new.violation_count - old.violation_count,
            node_delta=new.node_count - old.node_count,
            edge_delta=new.edge_count - old.edge_count
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "xs_delta": round(self.xs_delta, 2),
            "grade_old": self.grade_old,
            "grade_new": self.grade_new,
            "improved": self.improved,
            "degraded": self.degraded,
            "cycle_delta": self.cycle_delta,
            "violation_delta": self.violation_delta,
            "node_delta": self.node_delta,
            "edge_delta": self.edge_delta
        }


class XSGrader:
    """Assign grades based on XS score."""

    # Grade thresholds (XS score ranges)
    THRESHOLDS = {
        "A": (0, 20),    # Excellent
        "B": (20, 40),   # Good
        "C": (40, 60),   # Moderate
        "D": (60, 80),   # Poor
        "F": (80, float("inf"))  # Critical
    }

    def grade(self, xs_score: float) -> str:
        """Assign grade based on XS score.

        Args:
            xs_score: The XS score to grade

        Returns:
            Grade letter (A-F)
        """
        for grade, (low, high) in self.THRESHOLDS.items():
            if low <= xs_score < high:
                return grade
        return "F"

    def description(self, grade: str) -> str:
        """Get description for a grade."""
        descriptions = {
            "A": "Excellent - Clean architecture with minimal complexity",
            "B": "Good - Well-structured with some areas for improvement",
            "C": "Moderate - Notable structural issues that should be addressed",
            "D": "Poor - Significant structural problems requiring attention",
            "F": "Critical - Major architectural issues, refactoring recommended"
        }
        return descriptions.get(grade, "Unknown")


class XSCalculator:
    """Calculate XS (eXcess Structural complexity) score."""

    # Weight factors for each component
    CYCLE_WEIGHT = 15.0      # Per cycle
    COUPLING_WEIGHT = 2.0    # Per excess coupling
    SIZE_WEIGHT = 0.1        # Per node above threshold
    VIOLATION_WEIGHT = 5.0   # Per violation

    # Thresholds
    COUPLING_THRESHOLD = 3.0   # Avg dependencies per node considered "normal"
    SIZE_THRESHOLD = 50        # Nodes below this don't contribute to size penalty

    def __init__(self):
        """Initialize calculator."""
        self._grader = XSGrader()

    def calculate(self, graph: DependencyGraphResult) -> XSMetrics:
        """Calculate XS metrics for a dependency graph.

        Args:
            graph: Dependency graph to analyze

        Returns:
            XSMetrics with calculated values
        """
        return self.calculate_from_input(XSInput(graph=graph))

    def calculate_from_input(self, xs_input: XSInput) -> XSMetrics:
        """Calculate XS metrics from input with violations.

        Args:
            xs_input: XSInput containing graph and optional violations

        Returns:
            XSMetrics with calculated values
        """
        graph = xs_input.graph
        violations = xs_input.violations

        node_count = len(graph.nodes)
        edge_count = len(graph.edges)

        if node_count == 0:
            return XSMetrics(
                xs_score=0.0,
                grade="A",
                node_count=0,
                edge_count=0,
                cycle_count=0,
                violation_count=0,
                cycle_contribution=0.0,
                coupling_contribution=0.0,
                size_contribution=0.0,
                violation_contribution=0.0,
                avg_coupling=0.0
            )

        # Calculate cycle contribution
        from .architecture import CycleDetector
        cycle_detector = CycleDetector()
        cycles = cycle_detector.detect(graph)
        cycle_count = len(cycles)
        cycle_contribution = cycle_count * self.CYCLE_WEIGHT

        # Calculate coupling contribution
        avg_coupling = edge_count / node_count if node_count > 0 else 0
        excess_coupling = max(0, avg_coupling - self.COUPLING_THRESHOLD)
        coupling_contribution = excess_coupling * node_count * self.COUPLING_WEIGHT

        # Calculate size contribution
        excess_size = max(0, node_count - self.SIZE_THRESHOLD)
        size_contribution = excess_size * self.SIZE_WEIGHT

        # Calculate violation contribution
        violation_count = len(violations)
        violation_contribution = violation_count * self.VIOLATION_WEIGHT

        # Total XS score
        xs_score = (
            cycle_contribution +
            coupling_contribution +
            size_contribution +
            violation_contribution
        )

        # Assign grade
        grade = self._grader.grade(xs_score)

        return XSMetrics(
            xs_score=xs_score,
            grade=grade,
            node_count=node_count,
            edge_count=edge_count,
            cycle_count=cycle_count,
            violation_count=violation_count,
            cycle_contribution=cycle_contribution,
            coupling_contribution=coupling_contribution,
            size_contribution=size_contribution,
            violation_contribution=violation_contribution,
            avg_coupling=avg_coupling
        )


class HotspotDetector:
    """Detect complexity hotspots in code."""

    # Thresholds for hotspot detection
    HIGH_COUPLING_THRESHOLD = 5  # Connections to be considered "hub"
    CYCLE_SEVERITY_MULTIPLIER = 2.0

    def detect(self, graph: DependencyGraphResult) -> List[Hotspot]:
        """Detect hotspots in the dependency graph.

        Args:
            graph: Dependency graph to analyze

        Returns:
            List of detected hotspots sorted by severity
        """
        hotspots = []

        # Calculate node coupling (in + out degree)
        in_degree: Dict[str, int] = defaultdict(int)
        out_degree: Dict[str, int] = defaultdict(int)

        for edge in graph.edges:
            out_degree[edge.source] += 1
            in_degree[edge.target] += 1

        # Detect high coupling hotspots
        for node_id, node in graph.nodes.items():
            total_connections = in_degree[node_id] + out_degree[node_id]
            if total_connections >= self.HIGH_COUPLING_THRESHOLD:
                severity = min(10.0, total_connections / 2.0)
                hotspots.append(Hotspot(
                    node_id=node_id,
                    node_label=node.label,
                    reason="high_coupling",
                    severity=severity,
                    details={
                        "in_degree": in_degree[node_id],
                        "out_degree": out_degree[node_id],
                        "total_connections": total_connections
                    }
                ))

        # Detect cycle participants
        from .architecture import CycleDetector
        cycle_detector = CycleDetector()
        cycles = cycle_detector.detect(graph)

        cycle_nodes: Dict[str, int] = defaultdict(int)  # node -> cycle count
        for cycle in cycles:
            for node_id in cycle.nodes:
                cycle_nodes[node_id] += 1

        for node_id, cycle_count in cycle_nodes.items():
            if node_id in graph.nodes:
                node = graph.nodes[node_id]
                severity = min(10.0, cycle_count * self.CYCLE_SEVERITY_MULTIPLIER + 3.0)
                hotspots.append(Hotspot(
                    node_id=node_id,
                    node_label=node.label,
                    reason="cycle_participant",
                    severity=severity,
                    details={
                        "cycle_count": cycle_count
                    }
                ))

        # Sort by severity (highest first)
        hotspots.sort(key=lambda h: h.severity, reverse=True)

        return hotspots


def analyze_structure(
    graph: DependencyGraphResult,
    violations: Optional[List[Any]] = None
) -> Dict[str, Any]:
    """Analyze structural complexity of a dependency graph.

    Args:
        graph: Dependency graph to analyze
        violations: Optional list of architecture violations

    Returns:
        Dictionary with metrics, hotspots, and summary
    """
    violations = violations or []

    # Calculate XS metrics
    calculator = XSCalculator()
    xs_input = XSInput(graph=graph, violations=violations)
    metrics = calculator.calculate_from_input(xs_input)

    # Detect hotspots
    detector = HotspotDetector()
    hotspots = detector.detect(graph)

    # Get grade description
    grader = XSGrader()
    grade_description = grader.description(metrics.grade)

    return {
        "metrics": metrics.to_dict(),
        "hotspots": [h.to_dict() for h in hotspots[:10]],  # Top 10
        "summary": {
            "grade": metrics.grade,
            "grade_description": grade_description,
            "xs_score": round(metrics.xs_score, 2),
            "total_nodes": metrics.node_count,
            "total_edges": metrics.edge_count,
            "cycles": metrics.cycle_count,
            "violations": metrics.violation_count,
            "hotspot_count": len(hotspots)
        }
    }


# =============================================================================
# Coupling Metrics (Ca, Ce, Instability, Abstractness)
# =============================================================================

@dataclass
class NodeCouplingMetrics:
    """Coupling metrics for a single node (class/package)."""
    node_id: str
    node_label: str
    node_type: str

    # Coupling metrics
    ca: int = 0  # Afferent coupling: incoming dependencies (who depends on me)
    ce: int = 0  # Efferent coupling: outgoing dependencies (who do I depend on)

    # Derived metrics
    instability: float = 0.0  # Ce / (Ca + Ce), 0=stable, 1=unstable

    # Additional info
    is_abstract: bool = False  # Is this an interface/abstract class?
    dependents: List[str] = field(default_factory=list)  # Who depends on me
    dependencies: List[str] = field(default_factory=list)  # Who do I depend on

    # Risk assessment
    risk_level: str = "low"  # low, medium, high, critical
    risk_reason: str = ""

    def calculate_instability(self) -> None:
        """Calculate instability metric."""
        total = self.ca + self.ce
        if total > 0:
            self.instability = self.ce / total
        else:
            self.instability = 0.0

    def assess_risk(self) -> None:
        """Assess refactoring risk based on coupling metrics."""
        # High afferent (many depend on this) + high efferent = risky
        if self.ca >= 10 and self.ce >= 10:
            self.risk_level = "critical"
            self.risk_reason = f"God class: {self.ca} dependents, {self.ce} dependencies"
        elif self.ca >= 15:
            self.risk_level = "high"
            self.risk_reason = f"Core component: {self.ca} dependents, change carefully"
        elif self.ca >= 10 and self.instability > 0.7:
            self.risk_level = "high"
            self.risk_reason = f"Unstable core: {self.ca} dependents but high instability ({self.instability:.2f})"
        elif self.ce >= 15:
            self.risk_level = "medium"
            self.risk_reason = f"High coupling: depends on {self.ce} components"
        elif self.ca >= 5 or self.ce >= 5:
            self.risk_level = "medium"
            self.risk_reason = f"Moderate coupling (Ca={self.ca}, Ce={self.ce})"
        else:
            self.risk_level = "low"
            self.risk_reason = "Well-isolated component"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "node_id": self.node_id,
            "node_label": self.node_label,
            "node_type": self.node_type,
            "ca": self.ca,
            "ce": self.ce,
            "instability": round(self.instability, 3),
            "is_abstract": self.is_abstract,
            "dependents_count": len(self.dependents),
            "dependencies_count": len(self.dependencies),
            "risk_level": self.risk_level,
            "risk_reason": self.risk_reason,
        }


@dataclass
class PackageCouplingMetrics(NodeCouplingMetrics):
    """Coupling metrics for a package, including abstractness."""

    # Package-specific metrics
    abstractness: float = 0.0  # Ratio of abstract types to total types
    distance: float = 0.0  # Distance from main sequence |A + I - 1|

    # Package contents
    class_count: int = 0
    abstract_class_count: int = 0
    interface_count: int = 0

    # Zone classification
    zone: str = "normal"  # normal, zone_of_pain, zone_of_uselessness

    def calculate_abstractness(self) -> None:
        """Calculate abstractness metric."""
        total = self.class_count + self.interface_count
        if total > 0:
            abstract_total = self.abstract_class_count + self.interface_count
            self.abstractness = abstract_total / total
        else:
            self.abstractness = 0.0

    def calculate_distance(self) -> None:
        """Calculate distance from main sequence."""
        self.distance = abs(self.abstractness + self.instability - 1.0)

    def classify_zone(self) -> None:
        """Classify package into zones based on metrics."""
        if self.instability < 0.3 and self.abstractness < 0.3:
            self.zone = "zone_of_pain"  # Rigid, hard to change
        elif self.instability > 0.7 and self.abstractness > 0.7:
            self.zone = "zone_of_uselessness"  # Over-abstracted
        else:
            self.zone = "normal"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base = super().to_dict()
        base.update({
            "abstractness": round(self.abstractness, 3),
            "distance": round(self.distance, 3),
            "class_count": self.class_count,
            "abstract_class_count": self.abstract_class_count,
            "interface_count": self.interface_count,
            "zone": self.zone,
        })
        return base


@dataclass
class CouplingAnalysisResult:
    """Result of coupling analysis."""
    graph_type: str  # "class" or "package"
    node_metrics: List[NodeCouplingMetrics]

    # Aggregate metrics
    avg_ca: float = 0.0
    avg_ce: float = 0.0
    avg_instability: float = 0.0

    # Problem counts
    god_classes: int = 0
    unstable_cores: int = 0
    high_coupling: int = 0

    # Recommendations
    refactoring_targets: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "graph_type": self.graph_type,
            "node_count": len(self.node_metrics),
            "metrics": [m.to_dict() for m in self.node_metrics],
            "aggregates": {
                "avg_ca": round(self.avg_ca, 2),
                "avg_ce": round(self.avg_ce, 2),
                "avg_instability": round(self.avg_instability, 2),
            },
            "problems": {
                "god_classes": self.god_classes,
                "unstable_cores": self.unstable_cores,
                "high_coupling": self.high_coupling,
            },
            "refactoring_targets": self.refactoring_targets,
        }


class CouplingAnalyzer:
    """Analyze coupling metrics for dependency graphs."""

    # Thresholds for identifying problems
    GOD_CLASS_CA_THRESHOLD = 10
    GOD_CLASS_CE_THRESHOLD = 10
    UNSTABLE_CORE_CA_THRESHOLD = 10
    UNSTABLE_CORE_INSTABILITY_THRESHOLD = 0.7
    HIGH_COUPLING_THRESHOLD = 15

    def analyze(self, graph: DependencyGraphResult) -> CouplingAnalysisResult:
        """Analyze coupling metrics for a dependency graph.

        Args:
            graph: Dependency graph (class-level or package-level)

        Returns:
            CouplingAnalysisResult with metrics for each node
        """
        # Calculate incoming and outgoing edges for each node
        incoming: Dict[str, Set[str]] = defaultdict(set)
        outgoing: Dict[str, Set[str]] = defaultdict(set)

        for edge in graph.edges:
            if edge.source in graph.nodes and edge.target in graph.nodes:
                outgoing[edge.source].add(edge.target)
                incoming[edge.target].add(edge.source)

        # Create metrics for each node
        node_metrics: List[NodeCouplingMetrics] = []

        for node_id, node in graph.nodes.items():
            # Skip external nodes
            if node.metadata.get("is_external", False):
                continue

            # Determine if abstract
            is_abstract = (
                node.node_type in ("interface", "abstract_class") or
                node.metadata.get("is_abstract", False)
            )

            metrics = NodeCouplingMetrics(
                node_id=node_id,
                node_label=node.label,
                node_type=node.node_type,
                ca=len(incoming.get(node_id, set())),
                ce=len(outgoing.get(node_id, set())),
                is_abstract=is_abstract,
                dependents=sorted(incoming.get(node_id, set())),
                dependencies=sorted(outgoing.get(node_id, set())),
            )

            metrics.calculate_instability()
            metrics.assess_risk()

            node_metrics.append(metrics)

        # Calculate aggregates
        if node_metrics:
            avg_ca = sum(m.ca for m in node_metrics) / len(node_metrics)
            avg_ce = sum(m.ce for m in node_metrics) / len(node_metrics)
            avg_instability = sum(m.instability for m in node_metrics) / len(node_metrics)
        else:
            avg_ca = avg_ce = avg_instability = 0.0

        # Count problems
        god_classes = sum(
            1 for m in node_metrics
            if m.ca >= self.GOD_CLASS_CA_THRESHOLD and m.ce >= self.GOD_CLASS_CE_THRESHOLD
        )
        unstable_cores = sum(
            1 for m in node_metrics
            if m.ca >= self.UNSTABLE_CORE_CA_THRESHOLD and m.instability > self.UNSTABLE_CORE_INSTABILITY_THRESHOLD
        )
        high_coupling = sum(
            1 for m in node_metrics
            if m.ce >= self.HIGH_COUPLING_THRESHOLD
        )

        # Generate refactoring targets (sorted by risk)
        refactoring_targets = []
        for m in sorted(node_metrics, key=lambda x: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x.risk_level, 4),
            -(x.ca + x.ce)
        )):
            if m.risk_level in ("critical", "high"):
                refactoring_targets.append({
                    "node_id": m.node_id,
                    "node_label": m.node_label,
                    "risk_level": m.risk_level,
                    "risk_reason": m.risk_reason,
                    "ca": m.ca,
                    "ce": m.ce,
                    "instability": round(m.instability, 3),
                    "suggestion": self._get_suggestion(m),
                })

        return CouplingAnalysisResult(
            graph_type=graph.graph_type.value,
            node_metrics=node_metrics,
            avg_ca=avg_ca,
            avg_ce=avg_ce,
            avg_instability=avg_instability,
            god_classes=god_classes,
            unstable_cores=unstable_cores,
            high_coupling=high_coupling,
            refactoring_targets=refactoring_targets[:20],  # Top 20
        )

    def _get_suggestion(self, metrics: NodeCouplingMetrics) -> str:
        """Get refactoring suggestion based on metrics."""
        if metrics.ca >= self.GOD_CLASS_CA_THRESHOLD and metrics.ce >= self.GOD_CLASS_CE_THRESHOLD:
            return "Split by responsibility into smaller classes"
        elif metrics.ca >= self.UNSTABLE_CORE_CA_THRESHOLD and metrics.instability > self.UNSTABLE_CORE_INSTABILITY_THRESHOLD:
            return "Extract interface to stabilize API, reduce dependencies"
        elif metrics.ce >= self.HIGH_COUPLING_THRESHOLD:
            return "Reduce dependencies through dependency injection or facade pattern"
        elif metrics.ca >= 10:
            return "Consider extracting interface if API changes frequently"
        else:
            return "Monitor for coupling growth"

    def analyze_packages(
        self,
        graph: DependencyGraphResult,
        class_graph: Optional[DependencyGraphResult] = None
    ) -> CouplingAnalysisResult:
        """Analyze package-level coupling with abstractness metrics.

        Args:
            graph: Package-level dependency graph
            class_graph: Optional class-level graph for abstractness calculation

        Returns:
            CouplingAnalysisResult with package metrics
        """
        # First do basic coupling analysis
        basic_result = self.analyze(graph)

        # If we have class-level info, enhance with abstractness
        if class_graph:
            package_contents: Dict[str, Dict[str, int]] = defaultdict(
                lambda: {"classes": 0, "abstract": 0, "interfaces": 0}
            )

            for node_id, node in class_graph.nodes.items():
                if node.metadata.get("is_external", False):
                    continue

                # Extract package from node
                file_path = node.metadata.get("file", "")
                package = self._get_package_from_path(file_path)

                if node.node_type == "interface":
                    package_contents[package]["interfaces"] += 1
                elif node.node_type == "class":
                    package_contents[package]["classes"] += 1
                    if node.metadata.get("is_abstract", False):
                        package_contents[package]["abstract"] += 1

            # Upgrade metrics to PackageCouplingMetrics
            upgraded_metrics = []
            for m in basic_result.node_metrics:
                pkg_info = package_contents.get(m.node_id, {})

                pkg_metrics = PackageCouplingMetrics(
                    node_id=m.node_id,
                    node_label=m.node_label,
                    node_type="package",
                    ca=m.ca,
                    ce=m.ce,
                    instability=m.instability,
                    is_abstract=False,
                    dependents=m.dependents,
                    dependencies=m.dependencies,
                    risk_level=m.risk_level,
                    risk_reason=m.risk_reason,
                    class_count=pkg_info.get("classes", 0),
                    abstract_class_count=pkg_info.get("abstract", 0),
                    interface_count=pkg_info.get("interfaces", 0),
                )

                pkg_metrics.calculate_abstractness()
                pkg_metrics.calculate_distance()
                pkg_metrics.classify_zone()

                upgraded_metrics.append(pkg_metrics)

            basic_result.node_metrics = upgraded_metrics

        return basic_result

    def _get_package_from_path(self, file_path: str) -> str:
        """Extract package name from file path."""
        import os
        parts = file_path.replace("\\", "/").split("/")
        # Remove filename, keep directory
        if parts:
            parts = parts[:-1]
        return "/".join(parts) if parts else "."


def analyze_coupling(
    graph: DependencyGraphResult,
    class_graph: Optional[DependencyGraphResult] = None
) -> Dict[str, Any]:
    """Analyze coupling metrics for a dependency graph.

    Convenience function for coupling analysis.

    Args:
        graph: Dependency graph to analyze
        class_graph: Optional class-level graph for package abstractness

    Returns:
        Dictionary with coupling metrics and refactoring recommendations
    """
    analyzer = CouplingAnalyzer()

    if graph.graph_type.value == "module":
        result = analyzer.analyze_packages(graph, class_graph)
    else:
        result = analyzer.analyze(graph)

    return result.to_dict()
