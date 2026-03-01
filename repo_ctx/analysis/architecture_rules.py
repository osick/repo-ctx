"""Architecture layer detection and rule enforcement.

Provides Structure101-style architecture analysis including:
- Automatic layer detection from dependency patterns
- Architecture rule definition (YAML-based DSL)
- Rule enforcement and violation detection
"""
import fnmatch
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any
from collections import defaultdict

from .dependency_graph import DependencyGraphResult
from .architecture import CycleDetector


@dataclass
class LayerInfo:
    """Information about a detected or defined layer."""
    name: str
    level: int  # 0 = bottom (providers), higher = consumers
    nodes: List[str]
    patterns: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "level": self.level,
            "nodes": self.nodes,
            "patterns": self.patterns,
            "node_count": len(self.nodes)
        }


@dataclass
class ArchitectureViolation:
    """A detected architecture rule violation."""
    rule_name: str
    source: str
    target: str
    message: str
    file_path: Optional[str] = None
    line: Optional[int] = None
    severity: str = "error"  # error, warning, info

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_name": self.rule_name,
            "source": self.source,
            "target": self.target,
            "message": self.message,
            "file_path": self.file_path,
            "line": self.line,
            "severity": self.severity
        }


@dataclass
class LayerRule:
    """A rule defining layer ordering."""
    upper_layer: str  # Pattern or name
    lower_layer: str  # Pattern or name
    reason: Optional[str] = None


@dataclass
class DependencyRule:
    """A rule about allowed/forbidden dependencies."""
    from_pattern: str
    to_pattern: str
    reason: Optional[str] = None


class LayerDetector:
    """Automatically detect layers from dependency structure."""

    def __init__(self):
        """Initialize layer detector."""
        self._cycle_detector = CycleDetector()

    def detect(self, graph: DependencyGraphResult) -> List[LayerInfo]:
        """Detect layers from dependency graph.

        Uses topological sorting with cycle collapsing to identify
        natural layers in the code.

        Args:
            graph: Dependency graph to analyze

        Returns:
            List of LayerInfo objects ordered from bottom to top
        """
        if not graph.nodes:
            return []

        # Build adjacency lists
        # adj[a] = nodes that 'a' depends on (a -> b means a depends on b)
        adj: Dict[str, Set[str]] = defaultdict(set)
        # rev_adj[b] = nodes that depend on 'b'
        rev_adj: Dict[str, Set[str]] = defaultdict(set)

        for edge in graph.edges:
            if edge.source in graph.nodes and edge.target in graph.nodes:
                adj[edge.source].add(edge.target)
                rev_adj[edge.target].add(edge.source)

        # Detect cycles and collapse them into single "super-nodes"
        cycles = self._cycle_detector.detect(graph)
        cycle_members: Dict[str, int] = {}  # node -> cycle_id
        for i, cycle in enumerate(cycles):
            for node in cycle.nodes:
                cycle_members[node] = i

        # Group nodes by cycle (or self if not in cycle)
        super_nodes: Dict[int, Set[str]] = defaultdict(set)
        node_to_super: Dict[str, int] = {}
        super_id = len(cycles)  # Start after cycle IDs

        for node in graph.nodes:
            if node in cycle_members:
                cid = cycle_members[node]
                super_nodes[cid].add(node)
                node_to_super[node] = cid
            else:
                super_nodes[super_id] = {node}
                node_to_super[node] = super_id
                super_id += 1

        # Build super-node adjacency
        super_adj: Dict[int, Set[int]] = defaultdict(set)
        for source, targets in adj.items():
            source_super = node_to_super.get(source)
            if source_super is None:
                continue
            for target in targets:
                target_super = node_to_super.get(target)
                if target_super is not None and source_super != target_super:
                    super_adj[source_super].add(target_super)

        # Calculate layer levels using reverse BFS
        # Nodes with no outgoing dependencies are level 0
        levels: Dict[int, int] = {}

        def get_level(super_id: int, visited: Set[int]) -> int:
            if super_id in levels:
                return levels[super_id]
            if super_id in visited:
                return 0  # Cycle in super-graph (shouldn't happen)

            visited.add(super_id)

            # Level = 1 + max level of dependencies
            max_dep_level = -1
            for dep_super in super_adj.get(super_id, set()):
                dep_level = get_level(dep_super, visited)
                max_dep_level = max(max_dep_level, dep_level)

            levels[super_id] = max_dep_level + 1
            return levels[super_id]

        # Calculate levels for all super-nodes
        for sid in super_nodes:
            get_level(sid, set())

        # Group super-nodes by level
        level_groups: Dict[int, List[int]] = defaultdict(list)
        for sid, level in levels.items():
            level_groups[level].append(sid)

        # Create LayerInfo objects
        layers = []
        for level in sorted(level_groups.keys()):
            # Collect all original nodes in this level
            nodes_in_level = []
            for sid in level_groups[level]:
                nodes_in_level.extend(super_nodes[sid])

            layer = LayerInfo(
                name=f"Layer {level}",
                level=level,
                nodes=sorted(nodes_in_level)
            )
            layers.append(layer)

        return layers


class ArchitectureRules:
    """Architecture rule definition and enforcement."""

    def __init__(self, name: str = "", description: str = ""):
        """Initialize architecture rules.

        Args:
            name: Name of the architecture (e.g., "Clean Architecture")
            description: Description of the architecture
        """
        self.name = name
        self.description = description
        self.layer_rules: List[LayerRule] = []
        self.forbidden_rules: List[DependencyRule] = []
        self.allowed_rules: List[DependencyRule] = []
        self._layer_patterns: Dict[str, List[str]] = {}  # layer_name -> patterns

    def add_layer_rule(
        self,
        upper: str,
        above: str,
        reason: Optional[str] = None
    ) -> None:
        """Add a layer ordering rule.

        Args:
            upper: Upper layer name or pattern
            above: Lower layer name or pattern
            reason: Reason for the rule
        """
        self.layer_rules.append(LayerRule(
            upper_layer=upper,
            lower_layer=above,
            reason=reason
        ))

    def add_forbidden_rule(
        self,
        from_pattern: str,
        to_pattern: str,
        reason: Optional[str] = None
    ) -> None:
        """Add a forbidden dependency rule.

        Args:
            from_pattern: Source pattern (fnmatch)
            to_pattern: Target pattern (fnmatch)
            reason: Reason for the rule
        """
        self.forbidden_rules.append(DependencyRule(
            from_pattern=from_pattern,
            to_pattern=to_pattern,
            reason=reason
        ))

    def add_allowed_rule(
        self,
        from_pattern: str,
        to_pattern: str,
        reason: Optional[str] = None
    ) -> None:
        """Add an allowed dependency rule.

        Args:
            from_pattern: Source pattern (fnmatch)
            to_pattern: Target pattern (fnmatch)
            reason: Reason for the rule
        """
        self.allowed_rules.append(DependencyRule(
            from_pattern=from_pattern,
            to_pattern=to_pattern,
            reason=reason
        ))

    def set_layer_patterns(self, layer_name: str, patterns: List[str]) -> None:
        """Set patterns that define which nodes belong to a layer.

        Args:
            layer_name: Name of the layer
            patterns: List of fnmatch patterns
        """
        self._layer_patterns[layer_name] = patterns

    def check(self, graph: DependencyGraphResult) -> List[ArchitectureViolation]:
        """Check graph against all rules.

        Args:
            graph: Dependency graph to check

        Returns:
            List of violations found
        """
        violations = []

        # Check forbidden rules
        for rule in self.forbidden_rules:
            violations.extend(self._check_forbidden_rule(rule, graph))

        # Check layer rules
        for rule in self.layer_rules:
            violations.extend(self._check_layer_rule(rule, graph))

        return violations

    def _check_forbidden_rule(
        self,
        rule: DependencyRule,
        graph: DependencyGraphResult
    ) -> List[ArchitectureViolation]:
        """Check a forbidden dependency rule."""
        violations = []

        for edge in graph.edges:
            source_matches = self._matches_pattern(edge.source, rule.from_pattern, graph)
            target_matches = self._matches_pattern(edge.target, rule.to_pattern, graph)

            if source_matches and target_matches:
                # Check if this is explicitly allowed
                if self._is_allowed(edge.source, edge.target, graph):
                    continue

                # Get location info
                file_path = None
                line = None
                if edge.source in graph.nodes:
                    node = graph.nodes[edge.source]
                    file_path = node.metadata.get("file")
                line = edge.metadata.get("line")

                violations.append(ArchitectureViolation(
                    rule_name="forbidden",
                    source=edge.source,
                    target=edge.target,
                    message=rule.reason or f"Forbidden dependency: {edge.source} -> {edge.target}",
                    file_path=file_path,
                    line=line
                ))

        return violations

    def _check_layer_rule(
        self,
        rule: LayerRule,
        graph: DependencyGraphResult
    ) -> List[ArchitectureViolation]:
        """Check a layer ordering rule.

        Upper layer can depend on lower layer, but not vice versa.
        """
        violations = []

        for edge in graph.edges:
            source_is_lower = self._matches_pattern(edge.source, rule.lower_layer, graph)
            target_is_upper = self._matches_pattern(edge.target, rule.upper_layer, graph)

            if source_is_lower and target_is_upper:
                # Lower layer is depending on upper layer - violation!
                file_path = None
                line = None
                if edge.source in graph.nodes:
                    node = graph.nodes[edge.source]
                    file_path = node.metadata.get("file")
                line = edge.metadata.get("line")

                violations.append(ArchitectureViolation(
                    rule_name="layer_order",
                    source=edge.source,
                    target=edge.target,
                    message=rule.reason or f"Layer violation: {rule.lower_layer} cannot depend on {rule.upper_layer}",
                    file_path=file_path,
                    line=line
                ))

        return violations

    def _matches_pattern(
        self,
        node_id: str,
        pattern: str,
        graph: DependencyGraphResult
    ) -> bool:
        """Check if a node matches a pattern.

        Supports:
        - Exact match
        - fnmatch wildcards (*, ?)
        - Prefix match (e.g., "ui" matches "ui.View")
        - Layer names (if patterns defined)
        """
        # Check layer patterns first
        if pattern in self._layer_patterns:
            for layer_pattern in self._layer_patterns[pattern]:
                if fnmatch.fnmatch(node_id, layer_pattern):
                    return True
                # Also check node label
                if node_id in graph.nodes:
                    label = graph.nodes[node_id].label
                    if fnmatch.fnmatch(label, layer_pattern):
                        return True
            return False

        # Direct pattern match
        if fnmatch.fnmatch(node_id, pattern):
            return True

        # Check label
        if node_id in graph.nodes:
            label = graph.nodes[node_id].label
            if fnmatch.fnmatch(label, pattern):
                return True

        # Prefix match for simple patterns (no wildcards)
        # e.g., "ui" matches "ui.View" or "ui/View"
        if '*' not in pattern and '?' not in pattern:
            if node_id.startswith(pattern + '.') or node_id.startswith(pattern + '/'):
                return True

        return False

    def _is_allowed(
        self,
        source: str,
        target: str,
        graph: DependencyGraphResult
    ) -> bool:
        """Check if a dependency is explicitly allowed."""
        for rule in self.allowed_rules:
            source_matches = self._matches_pattern(source, rule.from_pattern, graph)
            target_matches = self._matches_pattern(target, rule.to_pattern, graph)
            if source_matches and target_matches:
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "layer_rules": [
                {"upper": r.upper_layer, "above": r.lower_layer, "reason": r.reason}
                for r in self.layer_rules
            ],
            "forbidden_rules": [
                {"from": r.from_pattern, "to": r.to_pattern, "reason": r.reason}
                for r in self.forbidden_rules
            ],
            "allowed_rules": [
                {"from": r.from_pattern, "to": r.to_pattern, "reason": r.reason}
                for r in self.allowed_rules
            ]
        }


class RuleParser:
    """Parse architecture rules from YAML."""

    def parse_yaml(self, yaml_content: str) -> ArchitectureRules:
        """Parse rules from YAML string.

        Args:
            yaml_content: YAML content

        Returns:
            ArchitectureRules object
        """
        import yaml

        if not yaml_content.strip():
            return ArchitectureRules()

        data = yaml.safe_load(yaml_content)
        if not data:
            return ArchitectureRules()

        rules = ArchitectureRules(
            name=data.get("name", ""),
            description=data.get("description", "")
        )

        # Parse layer rules
        for layer_def in data.get("layers", []):
            name = layer_def.get("name")
            above = layer_def.get("above")
            patterns = layer_def.get("patterns", [])

            if patterns:
                rules.set_layer_patterns(name, patterns)

            if above:
                rules.add_layer_rule(name, above, layer_def.get("reason"))

        # Parse forbidden rules
        for forbidden in data.get("forbidden", []):
            rules.add_forbidden_rule(
                forbidden.get("from", "*"),
                forbidden.get("to", "*"),
                forbidden.get("reason")
            )

        # Parse allowed rules
        for allowed in data.get("allowed", []):
            rules.add_allowed_rule(
                allowed.get("from", "*"),
                allowed.get("to", "*"),
                allowed.get("reason")
            )

        return rules

    def parse_file(self, file_path: str) -> ArchitectureRules:
        """Parse rules from a YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            ArchitectureRules object
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return self.parse_yaml(f.read())


def analyze_with_rules(
    graph: DependencyGraphResult,
    rules: Optional[ArchitectureRules] = None,
    rules_file: Optional[str] = None
) -> Dict[str, Any]:
    """Analyze architecture with optional rules.

    Args:
        graph: Dependency graph to analyze
        rules: Architecture rules object
        rules_file: Path to rules YAML file

    Returns:
        Dictionary with layers, violations, and summary
    """
    # Detect layers
    detector = LayerDetector()
    layers = detector.detect(graph)

    # Load rules if file provided
    if rules_file and not rules:
        parser = RuleParser()
        rules = parser.parse_file(rules_file)

    # Check rules
    violations = []
    if rules:
        violations = rules.check(graph)

    return {
        "layers": [layer.to_dict() for layer in layers],
        "violations": [v.to_dict() for v in violations],
        "summary": {
            "layer_count": len(layers),
            "violation_count": len(violations),
            "rules_name": rules.name if rules else None
        }
    }
