"""Dependency graph builder and exporter.

Generates dependency graphs in JSON Graph Format (JGF), DOT, and GraphML.
See: https://jsongraphformat.info/
"""
import json
from enum import Enum
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from .models import Symbol, SymbolType, Dependency


class GraphType(str, Enum):
    """Graph granularity types."""
    FILE = "file"
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    SYMBOL = "symbol"


class EdgeRelation(str, Enum):
    """Edge relationship types."""
    IMPORTS = "imports"
    INHERITS = "inherits"
    IMPLEMENTS = "implements"
    CONTAINS = "contains"
    CALLS = "calls"
    USES = "uses"
    INSTANTIATES = "instantiates"


@dataclass
class GraphNode:
    """Represents a node in the dependency graph."""
    id: str
    label: str
    node_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """Represents an edge in the dependency graph."""
    source: str
    target: str
    relation: str
    directed: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DependencyGraphResult:
    """Result of dependency graph generation."""
    id: str
    label: str
    graph_type: GraphType
    nodes: Dict[str, GraphNode]
    edges: List[GraphEdge]
    metadata: Dict[str, Any] = field(default_factory=dict)


class DependencyGraph:
    """Builds and exports dependency graphs from code analysis results."""

    def __init__(self, generator_version: str = "0.3.1"):
        """Initialize dependency graph builder.

        Args:
            generator_version: Version of the generator for metadata
        """
        self.generator_version = generator_version

    def build(
        self,
        symbols: List[Symbol],
        dependencies: List[Dict[str, Any]],
        graph_type: GraphType = GraphType.CLASS,
        graph_id: str = "code-graph",
        graph_label: str = "Code Dependency Graph",
        max_depth: Optional[int] = None,
        repository_info: Optional[Dict[str, Any]] = None
    ) -> DependencyGraphResult:
        """Build a dependency graph from symbols and dependencies.

        Args:
            symbols: List of Symbol objects from code analysis
            dependencies: List of dependency dictionaries
            graph_type: Type of graph to generate
            graph_id: Identifier for the graph
            graph_label: Human-readable label
            max_depth: Maximum traversal depth (None for unlimited)
            repository_info: Optional repository metadata

        Returns:
            DependencyGraphResult containing nodes and edges
        """
        nodes: Dict[str, GraphNode] = {}
        edges: List[GraphEdge] = []

        # Build nodes based on graph type
        if graph_type == GraphType.FILE:
            nodes, edges = self._build_file_graph(symbols, dependencies)
        elif graph_type == GraphType.MODULE:
            nodes, edges = self._build_module_graph(symbols, dependencies)
        elif graph_type == GraphType.CLASS:
            nodes, edges = self._build_class_graph(symbols, dependencies)
        elif graph_type == GraphType.FUNCTION:
            nodes, edges = self._build_function_graph(symbols, dependencies)
        else:  # SYMBOL - include all
            nodes, edges = self._build_symbol_graph(symbols, dependencies)

        # Apply depth limit if specified
        if max_depth is not None:
            nodes, edges = self._apply_depth_limit(nodes, edges, max_depth)

        # Calculate statistics
        languages = set()
        for node in nodes.values():
            lang = node.metadata.get("language")
            if lang:
                languages.add(lang)

        metadata = {
            "generator": "repo-ctx",
            "version": self.generator_version,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "graph_type": graph_type.value,
            "statistics": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "languages": sorted(languages)
            }
        }

        if repository_info:
            metadata["repository"] = repository_info

        return DependencyGraphResult(
            id=graph_id,
            label=graph_label,
            graph_type=graph_type,
            nodes=nodes,
            edges=edges,
            metadata=metadata
        )

    def _build_file_graph(
        self,
        symbols: List[Symbol],
        dependencies: List[Dict[str, Any]]
    ) -> tuple[Dict[str, GraphNode], List[GraphEdge]]:
        """Build file-level dependency graph."""
        nodes: Dict[str, GraphNode] = {}
        edges: List[GraphEdge] = []
        seen_edges: Set[tuple] = set()

        # Create file nodes
        files = set()
        for symbol in symbols:
            files.add(symbol.file_path)

        for file_path in files:
            file_symbols = [s for s in symbols if s.file_path == file_path]
            languages = set(s.language for s in file_symbols)

            nodes[file_path] = GraphNode(
                id=file_path,
                label=file_path.split("/")[-1],
                node_type="file",
                metadata={
                    "file": file_path,
                    "language": languages.pop() if len(languages) == 1 else "mixed",
                    "symbol_count": len(file_symbols)
                }
            )

        # Create edges from imports
        for dep in dependencies:
            if dep.get("type") == "import":
                source_file = dep.get("source")
                target = dep.get("target", "")

                # Try to find target file
                target_file = None
                for f in files:
                    if target in f or f.endswith(f"{target}.py"):
                        target_file = f
                        break

                if source_file and target_file and source_file != target_file:
                    edge_key = (source_file, target_file, "imports")
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        edges.append(GraphEdge(
                            source=source_file,
                            target=target_file,
                            relation=EdgeRelation.IMPORTS.value
                        ))

                # Also add external module nodes
                if source_file and not target_file and target:
                    if target not in nodes:
                        nodes[target] = GraphNode(
                            id=target,
                            label=target,
                            node_type="external_module",
                            metadata={"is_external": True}
                        )
                    edge_key = (source_file, target, "imports")
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        edges.append(GraphEdge(
                            source=source_file,
                            target=target,
                            relation=EdgeRelation.IMPORTS.value,
                            metadata={"is_external": True}
                        ))

        return nodes, edges

    def _build_module_graph(
        self,
        symbols: List[Symbol],
        dependencies: List[Dict[str, Any]]
    ) -> tuple[Dict[str, GraphNode], List[GraphEdge]]:
        """Build module-level dependency graph."""
        nodes: Dict[str, GraphNode] = {}
        edges: List[GraphEdge] = []
        seen_edges: Set[tuple] = set()

        # Extract module names from file paths
        modules = {}
        for symbol in symbols:
            file_path = symbol.file_path
            # Convert file path to module name
            module_name = file_path.replace("/", ".").replace("\\", ".")
            if module_name.endswith(".py"):
                module_name = module_name[:-3]
            elif module_name.endswith(".js") or module_name.endswith(".ts"):
                module_name = module_name[:-3]

            if module_name not in modules:
                modules[module_name] = {
                    "files": set(),
                    "symbols": [],
                    "language": symbol.language
                }
            modules[module_name]["files"].add(file_path)
            modules[module_name]["symbols"].append(symbol)

        # Create module nodes
        for module_name, info in modules.items():
            nodes[module_name] = GraphNode(
                id=module_name,
                label=module_name.split(".")[-1],
                node_type="module",
                metadata={
                    "files": list(info["files"]),
                    "language": info["language"],
                    "symbol_count": len(info["symbols"])
                }
            )

        # Create edges from imports
        for dep in dependencies:
            if dep.get("type") == "import":
                source_file = dep.get("source", "")
                target = dep.get("target", "")

                # Convert to module names
                source_module = source_file.replace("/", ".").replace("\\", ".")
                if source_module.endswith(".py"):
                    source_module = source_module[:-3]

                if source_module in modules:
                    # Check if target matches any known module
                    target_module = None
                    for mod_name in modules:
                        if target == mod_name or mod_name.endswith(f".{target}"):
                            target_module = mod_name
                            break

                    if target_module and source_module != target_module:
                        edge_key = (source_module, target_module, "imports")
                        if edge_key not in seen_edges:
                            seen_edges.add(edge_key)
                            edges.append(GraphEdge(
                                source=source_module,
                                target=target_module,
                                relation=EdgeRelation.IMPORTS.value
                            ))
                    elif not target_module and target:
                        # External module
                        if target not in nodes:
                            nodes[target] = GraphNode(
                                id=target,
                                label=target,
                                node_type="external_module",
                                metadata={"is_external": True}
                            )
                        edge_key = (source_module, target, "imports")
                        if edge_key not in seen_edges:
                            seen_edges.add(edge_key)
                            edges.append(GraphEdge(
                                source=source_module,
                                target=target,
                                relation=EdgeRelation.IMPORTS.value,
                                metadata={"is_external": True}
                            ))

        return nodes, edges

    def _build_class_graph(
        self,
        symbols: List[Symbol],
        dependencies: List[Dict[str, Any]]
    ) -> tuple[Dict[str, GraphNode], List[GraphEdge]]:
        """Build class-level dependency graph."""
        nodes: Dict[str, GraphNode] = {}
        edges: List[GraphEdge] = []
        seen_edges: Set[tuple] = set()

        # Filter class and interface symbols
        class_types = {SymbolType.CLASS, SymbolType.INTERFACE, SymbolType.ENUM}
        class_symbols = [s for s in symbols if s.symbol_type in class_types]

        # Create class nodes
        for symbol in class_symbols:
            node_id = f"{symbol.file_path}:{symbol.name}"
            nodes[node_id] = GraphNode(
                id=node_id,
                label=symbol.name,
                node_type=symbol.symbol_type.value,
                metadata={
                    "type": symbol.symbol_type.value,
                    "file": symbol.file_path,
                    "line_start": symbol.line_start,
                    "line_end": symbol.line_end,
                    "language": symbol.language,
                    "visibility": symbol.visibility,
                    "signature": symbol.signature,
                    "documentation": symbol.documentation,
                    "qualified_name": symbol.qualified_name
                }
            )

            # Add inheritance edges from metadata
            bases = symbol.metadata.get("bases", [])
            for base in bases:
                # Try to find the base class node
                base_node_id = None
                for s in class_symbols:
                    if s.name == base:
                        base_node_id = f"{s.file_path}:{s.name}"
                        break

                if base_node_id:
                    edge_key = (node_id, base_node_id, "inherits")
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        edges.append(GraphEdge(
                            source=node_id,
                            target=base_node_id,
                            relation=EdgeRelation.INHERITS.value,
                            metadata={"line": symbol.line_start}
                        ))
                else:
                    # External base class
                    ext_id = f"external:{base}"
                    if ext_id not in nodes:
                        nodes[ext_id] = GraphNode(
                            id=ext_id,
                            label=base,
                            node_type="class",
                            metadata={"is_external": True}
                        )
                    edge_key = (node_id, ext_id, "inherits")
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        edges.append(GraphEdge(
                            source=node_id,
                            target=ext_id,
                            relation=EdgeRelation.INHERITS.value,
                            metadata={"is_external": True}
                        ))

            # Add implements edges for interfaces
            implements = symbol.metadata.get("implements", [])
            for iface in implements:
                iface_node_id = None
                for s in class_symbols:
                    if s.name == iface:
                        iface_node_id = f"{s.file_path}:{s.name}"
                        break

                if iface_node_id:
                    edge_key = (node_id, iface_node_id, "implements")
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        edges.append(GraphEdge(
                            source=node_id,
                            target=iface_node_id,
                            relation=EdgeRelation.IMPLEMENTS.value
                        ))

        # Add containment edges (class contains methods)
        method_symbols = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        for method in method_symbols:
            parent_class = method.metadata.get("parent_class")
            if parent_class:
                parent_node_id = None
                for s in class_symbols:
                    if s.name == parent_class and s.file_path == method.file_path:
                        parent_node_id = f"{s.file_path}:{s.name}"
                        break

                if parent_node_id:
                    method_node_id = f"{method.file_path}:{parent_class}.{method.name}"
                    # Don't add method nodes to keep graph clean
                    # Just note the relationship in parent metadata
                    if parent_node_id in nodes:
                        methods = nodes[parent_node_id].metadata.get("methods", [])
                        methods.append(method.name)
                        nodes[parent_node_id].metadata["methods"] = methods

        return nodes, edges

    def _build_function_graph(
        self,
        symbols: List[Symbol],
        dependencies: List[Dict[str, Any]]
    ) -> tuple[Dict[str, GraphNode], List[GraphEdge]]:
        """Build function call graph."""
        nodes: Dict[str, GraphNode] = {}
        edges: List[GraphEdge] = []
        seen_edges: Set[tuple] = set()

        # Filter function and method symbols
        func_types = {SymbolType.FUNCTION, SymbolType.METHOD}
        func_symbols = [s for s in symbols if s.symbol_type in func_types]

        # Create function nodes
        for symbol in func_symbols:
            parent_class = symbol.metadata.get("parent_class", "")
            if parent_class:
                node_id = f"{symbol.file_path}:{parent_class}.{symbol.name}"
            else:
                node_id = f"{symbol.file_path}:{symbol.name}"

            nodes[node_id] = GraphNode(
                id=node_id,
                label=symbol.name,
                node_type=symbol.symbol_type.value,
                metadata={
                    "type": symbol.symbol_type.value,
                    "file": symbol.file_path,
                    "line_start": symbol.line_start,
                    "line_end": symbol.line_end,
                    "language": symbol.language,
                    "visibility": symbol.visibility,
                    "signature": symbol.signature,
                    "documentation": symbol.documentation,
                    "parent_class": parent_class if parent_class else None
                }
            )

        # Create edges from call dependencies
        for dep in dependencies:
            if dep.get("type") == "call":
                caller = dep.get("caller", "")
                callee = dep.get("callee", "")
                source_file = dep.get("source", "")

                # Find caller node
                caller_node_id = None
                for node_id in nodes:
                    if node_id.endswith(f":{caller}") or node_id.endswith(f".{caller}"):
                        caller_node_id = node_id
                        break

                # Find callee node
                callee_node_id = None
                for node_id in nodes:
                    if node_id.endswith(f":{callee}") or node_id.endswith(f".{callee}"):
                        callee_node_id = node_id
                        break

                if caller_node_id and callee_node_id and caller_node_id != callee_node_id:
                    edge_key = (caller_node_id, callee_node_id, "calls")
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        edges.append(GraphEdge(
                            source=caller_node_id,
                            target=callee_node_id,
                            relation=EdgeRelation.CALLS.value,
                            metadata={"line": dep.get("line")}
                        ))

        return nodes, edges

    def _build_symbol_graph(
        self,
        symbols: List[Symbol],
        dependencies: List[Dict[str, Any]]
    ) -> tuple[Dict[str, GraphNode], List[GraphEdge]]:
        """Build complete symbol graph with all relationships."""
        nodes: Dict[str, GraphNode] = {}
        edges: List[GraphEdge] = []

        # Create nodes for all symbols
        for symbol in symbols:
            parent_class = symbol.metadata.get("parent_class", "")
            if parent_class:
                node_id = f"{symbol.file_path}:{parent_class}.{symbol.name}"
            else:
                node_id = f"{symbol.file_path}:{symbol.name}"

            nodes[node_id] = GraphNode(
                id=node_id,
                label=symbol.name,
                node_type=symbol.symbol_type.value,
                metadata={
                    "type": symbol.symbol_type.value,
                    "file": symbol.file_path,
                    "line_start": symbol.line_start,
                    "line_end": symbol.line_end,
                    "language": symbol.language,
                    "visibility": symbol.visibility,
                    "signature": symbol.signature,
                    "documentation": symbol.documentation,
                    "qualified_name": symbol.qualified_name,
                    "is_exported": symbol.is_exported
                }
            )

        # Combine edges from class and function graphs
        _, class_edges = self._build_class_graph(symbols, dependencies)
        _, func_edges = self._build_function_graph(symbols, dependencies)

        edges.extend(class_edges)
        edges.extend(func_edges)

        # Add containment edges
        seen_edges: Set[tuple] = set((e.source, e.target, e.relation) for e in edges)

        for symbol in symbols:
            if symbol.symbol_type == SymbolType.METHOD:
                parent_class = symbol.metadata.get("parent_class")
                if parent_class:
                    parent_id = f"{symbol.file_path}:{parent_class}"
                    method_id = f"{symbol.file_path}:{parent_class}.{symbol.name}"
                    if parent_id in nodes and method_id in nodes:
                        edge_key = (parent_id, method_id, "contains")
                        if edge_key not in seen_edges:
                            seen_edges.add(edge_key)
                            edges.append(GraphEdge(
                                source=parent_id,
                                target=method_id,
                                relation=EdgeRelation.CONTAINS.value
                            ))

        return nodes, edges

    def _apply_depth_limit(
        self,
        nodes: Dict[str, GraphNode],
        edges: List[GraphEdge],
        max_depth: int
    ) -> tuple[Dict[str, GraphNode], List[GraphEdge]]:
        """Apply depth limit to graph by BFS traversal.

        Keeps nodes reachable within max_depth from any root node.
        Root nodes are those with no incoming edges.
        """
        if max_depth < 1:
            return nodes, edges

        # Find root nodes (no incoming edges)
        targets = set(e.target for e in edges)
        roots = set(nodes.keys()) - targets

        if not roots:
            # If no roots, use all nodes as potential roots
            roots = set(nodes.keys())

        # BFS to find reachable nodes within depth
        reachable: Set[str] = set()
        current_level = roots
        for _ in range(max_depth + 1):
            reachable.update(current_level)
            next_level = set()
            for node_id in current_level:
                for edge in edges:
                    if edge.source == node_id and edge.target in nodes:
                        next_level.add(edge.target)
            current_level = next_level - reachable

        # Filter nodes and edges
        filtered_nodes = {k: v for k, v in nodes.items() if k in reachable}
        filtered_edges = [
            e for e in edges
            if e.source in reachable and e.target in reachable
        ]

        return filtered_nodes, filtered_edges

    def to_json(self, result: DependencyGraphResult) -> str:
        """Export graph to JSON Graph Format (JGF).

        Args:
            result: DependencyGraphResult to export

        Returns:
            JSON string in JGF format
        """
        jgf = {
            "graph": {
                "id": result.id,
                "type": "code-dependency-graph",
                "label": result.label,
                "directed": True,
                "metadata": result.metadata,
                "nodes": {},
                "edges": []
            }
        }

        # Add nodes
        for node_id, node in result.nodes.items():
            jgf["graph"]["nodes"][node_id] = {
                "label": node.label,
                "metadata": node.metadata
            }

        # Add edges
        for edge in result.edges:
            edge_obj = {
                "source": edge.source,
                "target": edge.target,
                "relation": edge.relation,
                "directed": edge.directed
            }
            if edge.metadata:
                edge_obj["metadata"] = edge.metadata
            jgf["graph"]["edges"].append(edge_obj)

        return json.dumps(jgf, indent=2)

    def to_dot(self, result: DependencyGraphResult) -> str:
        """Export graph to DOT format (GraphViz).

        Args:
            result: DependencyGraphResult to export

        Returns:
            DOT format string
        """
        lines = [
            f'digraph "{result.id}" {{',
            '  rankdir=TB;',
            '  node [shape=box, style="rounded,filled", fontname="Helvetica"];',
            '  edge [fontname="Helvetica", fontsize=10];',
            ''
        ]

        # Color mapping for node types
        colors = {
            "class": "#a8d5ba",
            "interface": "#b8d4e8",
            "enum": "#f5d5a8",
            "function": "#d5a8d5",
            "method": "#d5c8e8",
            "file": "#e8e8e8",
            "module": "#c8e8c8",
            "external_module": "#ffcccc"
        }

        # Add nodes
        for node_id, node in result.nodes.items():
            color = colors.get(node.node_type, "#ffffff")
            safe_id = self._dot_escape(node_id)
            label = f"{node.label}\\n({node.node_type})"

            # Add location info for code nodes
            if node.metadata.get("file"):
                file_name = node.metadata["file"].split("/")[-1]
                line = node.metadata.get("line_start", "")
                label += f"\\n{file_name}:{line}"

            lines.append(f'  "{safe_id}" [label="{label}", fillcolor="{color}"];')

        lines.append('')

        # Add edges
        for edge in result.edges:
            safe_source = self._dot_escape(edge.source)
            safe_target = self._dot_escape(edge.target)
            style = ""

            if edge.relation == EdgeRelation.INHERITS.value:
                style = ', style=bold, color="#2e7d32"'
            elif edge.relation == EdgeRelation.IMPLEMENTS.value:
                style = ', style=dashed, color="#1565c0"'
            elif edge.relation == EdgeRelation.CALLS.value:
                style = ', color="#7b1fa2"'
            elif edge.metadata.get("is_external"):
                style = ', style=dotted, color="#999999"'

            lines.append(f'  "{safe_source}" -> "{safe_target}" [label="{edge.relation}"{style}];')

        lines.append('}')
        return '\n'.join(lines)

    def to_graphml(self, result: DependencyGraphResult) -> str:
        """Export graph to GraphML format.

        Args:
            result: DependencyGraphResult to export

        Returns:
            GraphML XML string
        """
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<graphml xmlns="http://graphml.graphdrawing.org/xmlns"',
            '         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
            '         xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns',
            '         http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">',
            '',
            '  <!-- Node attributes -->',
            '  <key id="label" for="node" attr.name="label" attr.type="string"/>',
            '  <key id="type" for="node" attr.name="type" attr.type="string"/>',
            '  <key id="file" for="node" attr.name="file" attr.type="string"/>',
            '  <key id="line_start" for="node" attr.name="line_start" attr.type="int"/>',
            '  <key id="language" for="node" attr.name="language" attr.type="string"/>',
            '  <key id="visibility" for="node" attr.name="visibility" attr.type="string"/>',
            '',
            '  <!-- Edge attributes -->',
            '  <key id="relation" for="edge" attr.name="relation" attr.type="string"/>',
            '',
            f'  <graph id="{self._xml_escape(result.id)}" edgedefault="directed">',
        ]

        # Add nodes
        for node_id, node in result.nodes.items():
            safe_id = self._xml_escape(node_id)
            lines.append(f'    <node id="{safe_id}">')
            lines.append(f'      <data key="label">{self._xml_escape(node.label)}</data>')
            lines.append(f'      <data key="type">{self._xml_escape(node.node_type)}</data>')

            if node.metadata.get("file"):
                lines.append(f'      <data key="file">{self._xml_escape(node.metadata["file"])}</data>')
            if node.metadata.get("line_start"):
                lines.append(f'      <data key="line_start">{node.metadata["line_start"]}</data>')
            if node.metadata.get("language"):
                lines.append(f'      <data key="language">{self._xml_escape(node.metadata["language"])}</data>')
            if node.metadata.get("visibility"):
                lines.append(f'      <data key="visibility">{self._xml_escape(node.metadata["visibility"])}</data>')

            lines.append('    </node>')

        # Add edges
        edge_id = 0
        for edge in result.edges:
            safe_source = self._xml_escape(edge.source)
            safe_target = self._xml_escape(edge.target)
            lines.append(f'    <edge id="e{edge_id}" source="{safe_source}" target="{safe_target}">')
            lines.append(f'      <data key="relation">{self._xml_escape(edge.relation)}</data>')
            lines.append('    </edge>')
            edge_id += 1

        lines.append('  </graph>')
        lines.append('</graphml>')

        return '\n'.join(lines)

    def _dot_escape(self, s: str) -> str:
        """Escape string for DOT format."""
        return s.replace('"', '\\"').replace('\n', '\\n')

    def _xml_escape(self, s: str) -> str:
        """Escape string for XML."""
        return (s.replace('&', '&amp;')
                 .replace('<', '&lt;')
                 .replace('>', '&gt;')
                 .replace('"', '&quot;')
                 .replace("'", '&apos;'))
