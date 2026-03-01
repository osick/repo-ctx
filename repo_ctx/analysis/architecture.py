"""Architecture analysis: DSM generation and cycle detection.

Provides Structure101-style architecture analysis including:
- Dependency Structure Matrix (DSM) generation
- Cycle detection using Tarjan's algorithm
- Breakup suggestions for resolving cycles
- Layer detection and partitioning
"""
import json
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple, Any
from collections import defaultdict

from .dependency_graph import DependencyGraphResult, GraphNode, GraphEdge


@dataclass
class BreakupSuggestion:
    """Suggestion for breaking a dependency cycle."""
    edge_to_remove: GraphEdge
    reason: str
    impact: float  # Lower is better (minimal disruption)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "edge": {
                "source": self.edge_to_remove.source,
                "target": self.edge_to_remove.target,
                "relation": self.edge_to_remove.relation
            },
            "reason": self.reason,
            "impact": self.impact
        }


@dataclass
class CycleInfo:
    """Information about a detected dependency cycle."""
    nodes: List[str]
    edges: List[GraphEdge]
    impact_score: float  # Higher means more problematic
    breakup_suggestions: List[BreakupSuggestion] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "nodes": self.nodes,
            "edges": [
                {"source": e.source, "target": e.target, "relation": e.relation}
                for e in self.edges
            ],
            "impact_score": self.impact_score,
            "breakup_suggestions": [s.to_dict() for s in self.breakup_suggestions]
        }


@dataclass
class DSMResult:
    """Result of DSM generation."""
    matrix: List[List[int]]  # Adjacency matrix (row depends on column)
    labels: List[str]  # Node IDs in matrix order
    label_names: List[str]  # Human-readable names
    cycles: List[CycleInfo]
    size: int

    def is_layered(self) -> bool:
        """Check if matrix is triangular (no cycles above diagonal)."""
        if not self.matrix:
            return True

        # In a properly layered DSM, all dependencies should be
        # below the diagonal (row > col for dependencies)
        for i, row in enumerate(self.matrix):
            for j, val in enumerate(row):
                if val > 0 and i < j:  # Dependency above diagonal
                    return False
        return True

    def to_text(self, max_label_width: int = 20) -> str:
        """Generate text representation of DSM.

        Args:
            max_label_width: Maximum width for labels

        Returns:
            ASCII text representation
        """
        if not self.matrix:
            return "Empty DSM (no nodes)"

        # Truncate labels
        labels = [
            (name[:max_label_width-2] + ".." if len(name) > max_label_width else name)
            for name in self.label_names
        ]

        # Calculate column width
        col_width = max(3, max(len(l) for l in labels) if labels else 3)

        lines = []

        # Header
        header = " " * (col_width + 2)
        for i, label in enumerate(labels):
            header += f"{i:>3} "
        lines.append(header)

        # Separator
        lines.append("-" * len(header))

        # Matrix rows
        for i, (label, row) in enumerate(zip(labels, self.matrix)):
            row_str = f"{label:>{col_width}} |"
            for j, val in enumerate(row):
                if i == j:
                    row_str += "  . "  # Diagonal
                elif val > 0:
                    if any(c for c in self.cycles if self.labels[i] in c.nodes and self.labels[j] in c.nodes):
                        row_str += f" \033[91m{val:>2}\033[0m "  # Red for cycle
                    elif i < j:
                        row_str += f" \033[93m{val:>2}\033[0m "  # Yellow for above diagonal
                    else:
                        row_str += f" {val:>2} "  # Normal
                else:
                    row_str += "    "
            lines.append(row_str)

        # Summary
        lines.append("")
        lines.append(f"Size: {self.size} nodes")
        lines.append(f"Layered: {'Yes' if self.is_layered() else 'No'}")
        lines.append(f"Cycles: {len(self.cycles)}")

        if self.cycles:
            lines.append("")
            lines.append("Detected cycles:")
            for i, cycle in enumerate(self.cycles, 1):
                nodes_str = " -> ".join(cycle.nodes[:5])
                if len(cycle.nodes) > 5:
                    nodes_str += f" -> ... ({len(cycle.nodes)} nodes)"
                lines.append(f"  {i}. {nodes_str} (impact: {cycle.impact_score:.1f})")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "matrix": self.matrix,
            "labels": self.labels,
            "label_names": self.label_names,
            "size": self.size,
            "is_layered": self.is_layered(),
            "cycles": [c.to_dict() for c in self.cycles]
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


class CycleDetector:
    """Detect cycles in dependency graph using Tarjan's algorithm."""

    def __init__(self):
        """Initialize cycle detector."""
        self._index = 0
        self._stack: List[str] = []
        self._on_stack: Set[str] = set()
        self._indices: Dict[str, int] = {}
        self._lowlinks: Dict[str, int] = {}
        self._sccs: List[List[str]] = []

    def detect(self, graph: DependencyGraphResult) -> List[CycleInfo]:
        """Detect all cycles in the graph.

        Uses Tarjan's strongly connected components algorithm.

        Args:
            graph: Dependency graph to analyze

        Returns:
            List of CycleInfo objects for each detected cycle
        """
        # Reset state
        self._index = 0
        self._stack = []
        self._on_stack = set()
        self._indices = {}
        self._lowlinks = {}
        self._sccs = []

        # Build adjacency list
        adj: Dict[str, List[str]] = defaultdict(list)
        for edge in graph.edges:
            if edge.source in graph.nodes and edge.target in graph.nodes:
                adj[edge.source].append(edge.target)

        # Run Tarjan's algorithm
        for node_id in graph.nodes:
            if node_id not in self._indices:
                self._strongconnect(node_id, adj)

        # Filter SCCs to only those with cycles (size > 1 or self-loop)
        cycles = []
        for scc in self._sccs:
            if len(scc) > 1:
                # Multi-node cycle
                cycle_info = self._create_cycle_info(scc, graph, adj)
                cycles.append(cycle_info)
            elif len(scc) == 1:
                # Check for self-loop
                node = scc[0]
                if node in adj[node]:
                    cycle_info = self._create_cycle_info(scc, graph, adj)
                    cycles.append(cycle_info)

        # Sort by impact (highest first)
        cycles.sort(key=lambda c: c.impact_score, reverse=True)

        return cycles

    def _strongconnect(self, node: str, adj: Dict[str, List[str]]) -> None:
        """Tarjan's strongconnect function."""
        self._indices[node] = self._index
        self._lowlinks[node] = self._index
        self._index += 1
        self._stack.append(node)
        self._on_stack.add(node)

        for successor in adj[node]:
            if successor not in self._indices:
                self._strongconnect(successor, adj)
                self._lowlinks[node] = min(self._lowlinks[node], self._lowlinks[successor])
            elif successor in self._on_stack:
                self._lowlinks[node] = min(self._lowlinks[node], self._indices[successor])

        # If node is root of SCC
        if self._lowlinks[node] == self._indices[node]:
            scc = []
            while True:
                w = self._stack.pop()
                self._on_stack.remove(w)
                scc.append(w)
                if w == node:
                    break
            self._sccs.append(scc)

    def _create_cycle_info(
        self,
        nodes: List[str],
        graph: DependencyGraphResult,
        adj: Dict[str, List[str]]
    ) -> CycleInfo:
        """Create CycleInfo for a strongly connected component."""
        node_set = set(nodes)

        # Find edges within the cycle
        cycle_edges = []
        for edge in graph.edges:
            if edge.source in node_set and edge.target in node_set:
                cycle_edges.append(edge)

        # Calculate impact score
        # Based on: number of nodes, number of edges, centrality
        impact_score = len(nodes) * 2.0 + len(cycle_edges) * 1.0

        # Generate breakup suggestions
        suggestions = self._generate_breakup_suggestions(nodes, cycle_edges, graph)

        return CycleInfo(
            nodes=nodes,
            edges=cycle_edges,
            impact_score=impact_score,
            breakup_suggestions=suggestions
        )

    def _generate_breakup_suggestions(
        self,
        nodes: List[str],
        edges: List[GraphEdge],
        graph: DependencyGraphResult
    ) -> List[BreakupSuggestion]:
        """Generate suggestions for breaking the cycle.

        Prioritizes edges that:
        1. Have lowest fan-in (fewer dependents on target)
        2. Connect to external-like nodes
        3. Are not inheritance relationships
        """
        suggestions = []
        node_set = set(nodes)

        # Calculate fan-in for each node
        fan_in: Dict[str, int] = defaultdict(int)
        for edge in graph.edges:
            fan_in[edge.target] += 1

        for edge in edges:
            # Calculate impact of removing this edge
            impact = fan_in[edge.target]

            # Penalize removing inheritance edges
            if edge.relation in ("inherits", "implements"):
                impact += 10

            # Prefer removing import/uses edges
            if edge.relation in ("imports", "uses"):
                impact -= 1

            # Create reason
            source_name = graph.nodes[edge.source].label if edge.source in graph.nodes else edge.source
            target_name = graph.nodes[edge.target].label if edge.target in graph.nodes else edge.target

            reason = f"Remove {edge.relation} from {source_name} to {target_name}"
            if edge.relation in ("inherits", "implements"):
                reason += " (consider composition over inheritance)"
            else:
                reason += " (consider dependency injection or interface extraction)"

            suggestions.append(BreakupSuggestion(
                edge_to_remove=edge,
                reason=reason,
                impact=impact
            ))

        # Sort by impact (lowest first = best suggestions)
        suggestions.sort(key=lambda s: s.impact)

        return suggestions


class DSMBuilder:
    """Build Dependency Structure Matrix from dependency graph."""

    def __init__(self):
        """Initialize DSM builder."""
        self._cycle_detector = CycleDetector()

    def build(self, graph: DependencyGraphResult) -> DSMResult:
        """Build DSM from dependency graph.

        Args:
            graph: Dependency graph to analyze

        Returns:
            DSMResult with matrix, labels, and cycle information
        """
        if not graph.nodes:
            return DSMResult(
                matrix=[],
                labels=[],
                label_names=[],
                cycles=[],
                size=0
            )

        # Detect cycles first
        cycles = self._cycle_detector.detect(graph)

        # Build adjacency information
        adj: Dict[str, Set[str]] = defaultdict(set)
        for edge in graph.edges:
            if edge.source in graph.nodes and edge.target in graph.nodes:
                adj[edge.source].add(edge.target)

        # Topological sort with cycle handling (partition algorithm)
        ordered_nodes = self._partition_nodes(graph, adj, cycles)

        # Create node index mapping
        node_to_idx = {node: i for i, node in enumerate(ordered_nodes)}

        # Build matrix
        size = len(ordered_nodes)
        matrix = [[0] * size for _ in range(size)]

        for source, targets in adj.items():
            if source in node_to_idx:
                i = node_to_idx[source]
                for target in targets:
                    if target in node_to_idx:
                        j = node_to_idx[target]
                        matrix[i][j] += 1

        # Get human-readable labels
        label_names = [
            graph.nodes[node_id].label if node_id in graph.nodes else node_id
            for node_id in ordered_nodes
        ]

        return DSMResult(
            matrix=matrix,
            labels=ordered_nodes,
            label_names=label_names,
            cycles=cycles,
            size=size
        )

    def _partition_nodes(
        self,
        graph: DependencyGraphResult,
        adj: Dict[str, Set[str]],
        cycles: List[CycleInfo]
    ) -> List[str]:
        """Order nodes to minimize above-diagonal dependencies.

        Uses a modified topological sort that handles cycles by
        grouping strongly connected components together.

        Args:
            graph: The dependency graph
            adj: Adjacency list (source -> targets)
            cycles: Detected cycles

        Returns:
            Ordered list of node IDs
        """
        if not graph.nodes:
            return []

        # Build reverse adjacency (who depends on me)
        rev_adj: Dict[str, Set[str]] = defaultdict(set)
        for source, targets in adj.items():
            for target in targets:
                rev_adj[target].add(source)

        # Group nodes in cycles
        cycle_nodes: Set[str] = set()
        for cycle in cycles:
            cycle_nodes.update(cycle.nodes)

        # Calculate "layer" for each node
        # Providers (depended upon) should come first (lower layer number)
        layers: Dict[str, int] = {}

        def get_layer(node: str, visited: Set[str]) -> int:
            if node in layers:
                return layers[node]
            if node in visited:
                return 0  # Cycle, assign same layer

            visited.add(node)

            # Layer = 1 + max layer of nodes I depend on
            max_dep_layer = -1
            for target in adj.get(node, set()):
                if target in graph.nodes:
                    dep_layer = get_layer(target, visited)
                    max_dep_layer = max(max_dep_layer, dep_layer)

            layers[node] = max_dep_layer + 1
            return layers[node]

        # Calculate layers for all nodes
        for node in graph.nodes:
            get_layer(node, set())

        # Sort by layer (providers first), then alphabetically for stability
        ordered = sorted(
            graph.nodes.keys(),
            key=lambda n: (layers.get(n, 0), n)
        )

        return ordered


def analyze_architecture(graph: DependencyGraphResult) -> Dict[str, Any]:
    """Analyze architecture of a dependency graph.

    Convenience function combining DSM and cycle analysis.

    Args:
        graph: Dependency graph to analyze

    Returns:
        Dictionary with DSM, cycles, and summary
    """
    builder = DSMBuilder()
    dsm = builder.build(graph)

    return {
        "dsm": dsm.to_dict(),
        "summary": {
            "total_nodes": dsm.size,
            "is_layered": dsm.is_layered(),
            "cycle_count": len(dsm.cycles),
            "total_cycle_nodes": sum(len(c.nodes) for c in dsm.cycles),
            "max_cycle_impact": max((c.impact_score for c in dsm.cycles), default=0)
        },
        "cycles": [c.to_dict() for c in dsm.cycles]
    }
