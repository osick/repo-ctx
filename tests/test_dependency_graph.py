"""Tests for DependencyGraph builder and exporter."""
import json
import pytest
from repo_ctx.analysis.dependency_graph import (
    DependencyGraph,
    DependencyGraphResult,
    GraphType,
    EdgeRelation,
    GraphNode,
    GraphEdge,
)
from repo_ctx.analysis.models import Symbol, SymbolType


class TestGraphEnums:
    """Test GraphType and EdgeRelation enums."""

    def test_graph_type_values(self):
        """Test GraphType enum has correct values."""
        assert GraphType.FILE.value == "file"
        assert GraphType.MODULE.value == "module"
        assert GraphType.CLASS.value == "class"
        assert GraphType.FUNCTION.value == "function"
        assert GraphType.SYMBOL.value == "symbol"

    def test_edge_relation_values(self):
        """Test EdgeRelation enum has correct values."""
        assert EdgeRelation.IMPORTS.value == "imports"
        assert EdgeRelation.INHERITS.value == "inherits"
        assert EdgeRelation.IMPLEMENTS.value == "implements"
        assert EdgeRelation.CONTAINS.value == "contains"
        assert EdgeRelation.CALLS.value == "calls"
        assert EdgeRelation.USES.value == "uses"
        assert EdgeRelation.INSTANTIATES.value == "instantiates"


class TestDataclasses:
    """Test GraphNode, GraphEdge, and DependencyGraphResult dataclasses."""

    def test_graph_node_creation(self):
        """Test creating a GraphNode."""
        node = GraphNode(
            id="test:MyClass",
            label="MyClass",
            node_type="class",
            metadata={"file": "test.py", "line_start": 10}
        )
        assert node.id == "test:MyClass"
        assert node.label == "MyClass"
        assert node.node_type == "class"
        assert node.metadata["file"] == "test.py"

    def test_graph_node_default_metadata(self):
        """Test GraphNode has empty metadata by default."""
        node = GraphNode(id="test", label="Test", node_type="class")
        assert node.metadata == {}

    def test_graph_edge_creation(self):
        """Test creating a GraphEdge."""
        edge = GraphEdge(
            source="file1.py:ClassA",
            target="file2.py:ClassB",
            relation="inherits",
            directed=True,
            metadata={"line": 5}
        )
        assert edge.source == "file1.py:ClassA"
        assert edge.target == "file2.py:ClassB"
        assert edge.relation == "inherits"
        assert edge.directed is True
        assert edge.metadata["line"] == 5

    def test_graph_edge_defaults(self):
        """Test GraphEdge default values."""
        edge = GraphEdge(source="a", target="b", relation="calls")
        assert edge.directed is True
        assert edge.metadata == {}

    def test_dependency_graph_result(self):
        """Test DependencyGraphResult dataclass."""
        nodes = {"n1": GraphNode(id="n1", label="N1", node_type="class")}
        edges = [GraphEdge(source="n1", target="n2", relation="inherits")]
        result = DependencyGraphResult(
            id="test-graph",
            label="Test Graph",
            graph_type=GraphType.CLASS,
            nodes=nodes,
            edges=edges,
            metadata={"generator": "test"}
        )
        assert result.id == "test-graph"
        assert result.label == "Test Graph"
        assert result.graph_type == GraphType.CLASS
        assert len(result.nodes) == 1
        assert len(result.edges) == 1


class TestDependencyGraphBuilder:
    """Test DependencyGraph.build() method."""

    def setup_method(self):
        """Set up graph builder for each test."""
        self.builder = DependencyGraph(generator_version="1.0.0-test")

    def _create_test_symbols(self):
        """Create a set of test symbols for graph building."""
        return [
            Symbol(
                name="ClassA",
                symbol_type=SymbolType.CLASS,
                file_path="src/module1.py",
                line_start=1,
                line_end=20,
                language="python",
                visibility="public",
                metadata={"bases": ["BaseClass"]}
            ),
            Symbol(
                name="ClassB",
                symbol_type=SymbolType.CLASS,
                file_path="src/module1.py",
                line_start=22,
                line_end=40,
                language="python",
                visibility="public",
                metadata={"bases": ["ClassA"]}
            ),
            Symbol(
                name="BaseClass",
                symbol_type=SymbolType.CLASS,
                file_path="src/base.py",
                line_start=1,
                line_end=15,
                language="python",
                visibility="public",
                metadata={}
            ),
            Symbol(
                name="method_a",
                symbol_type=SymbolType.METHOD,
                file_path="src/module1.py",
                line_start=5,
                line_end=10,
                language="python",
                visibility="public",
                metadata={"parent_class": "ClassA"}
            ),
            Symbol(
                name="helper_func",
                symbol_type=SymbolType.FUNCTION,
                file_path="src/utils.py",
                line_start=1,
                line_end=5,
                language="python",
                visibility="public",
                metadata={}
            ),
            Symbol(
                name="UserInterface",
                symbol_type=SymbolType.INTERFACE,
                file_path="src/interfaces.ts",
                line_start=1,
                line_end=10,
                language="typescript",
                visibility="public",
                metadata={}
            ),
        ]

    def _create_test_dependencies(self):
        """Create a set of test dependencies."""
        return [
            {"type": "import", "source": "src/module1.py", "target": "base"},
            {"type": "import", "source": "src/module1.py", "target": "utils"},
            {"type": "import", "source": "src/module1.py", "target": "os"},
            {"type": "call", "source": "src/module1.py", "caller": "method_a", "callee": "helper_func"},
        ]

    def test_build_class_graph(self):
        """Test building a class-level dependency graph."""
        symbols = self._create_test_symbols()
        dependencies = self._create_test_dependencies()

        result = self.builder.build(
            symbols=symbols,
            dependencies=dependencies,
            graph_type=GraphType.CLASS,
            graph_id="test-project",
            graph_label="Test Project Class Graph"
        )

        assert result.id == "test-project"
        assert result.graph_type == GraphType.CLASS
        # Should have class and interface nodes (not functions/methods)
        assert len(result.nodes) >= 3  # ClassA, ClassB, BaseClass, UserInterface

        # Check metadata
        assert result.metadata["generator"] == "repo-ctx"
        assert result.metadata["graph_type"] == "class"
        assert "statistics" in result.metadata
        assert result.metadata["statistics"]["node_count"] == len(result.nodes)

    def test_build_file_graph(self):
        """Test building a file-level dependency graph."""
        symbols = self._create_test_symbols()
        dependencies = self._create_test_dependencies()

        result = self.builder.build(
            symbols=symbols,
            dependencies=dependencies,
            graph_type=GraphType.FILE,
            graph_id="test-project"
        )

        assert result.graph_type == GraphType.FILE
        # Should have file nodes
        file_nodes = [n for n in result.nodes.values() if n.node_type == "file"]
        assert len(file_nodes) >= 3  # module1.py, base.py, utils.py, interfaces.ts

    def test_build_function_graph(self):
        """Test building a function call graph."""
        symbols = self._create_test_symbols()
        dependencies = self._create_test_dependencies()

        result = self.builder.build(
            symbols=symbols,
            dependencies=dependencies,
            graph_type=GraphType.FUNCTION,
            graph_id="test-project"
        )

        assert result.graph_type == GraphType.FUNCTION
        # Should have function and method nodes
        func_nodes = [n for n in result.nodes.values()
                     if n.node_type in ("function", "method")]
        assert len(func_nodes) >= 2  # method_a, helper_func

    def test_build_module_graph(self):
        """Test building a module-level dependency graph."""
        symbols = self._create_test_symbols()
        dependencies = self._create_test_dependencies()

        result = self.builder.build(
            symbols=symbols,
            dependencies=dependencies,
            graph_type=GraphType.MODULE,
            graph_id="test-project"
        )

        assert result.graph_type == GraphType.MODULE
        # Should have module nodes
        assert len(result.nodes) >= 1

    def test_build_symbol_graph(self):
        """Test building a complete symbol graph."""
        symbols = self._create_test_symbols()
        dependencies = self._create_test_dependencies()

        result = self.builder.build(
            symbols=symbols,
            dependencies=dependencies,
            graph_type=GraphType.SYMBOL,
            graph_id="test-project"
        )

        assert result.graph_type == GraphType.SYMBOL
        # Should have all symbols as nodes
        assert len(result.nodes) >= len(symbols)

    def test_build_with_inheritance_edges(self):
        """Test that inheritance edges are created correctly."""
        symbols = self._create_test_symbols()
        dependencies = []

        result = self.builder.build(
            symbols=symbols,
            dependencies=dependencies,
            graph_type=GraphType.CLASS
        )

        # Check inheritance edges
        inherit_edges = [e for e in result.edges if e.relation == "inherits"]
        assert len(inherit_edges) >= 1  # ClassB inherits from ClassA

    def test_build_with_max_depth(self):
        """Test building graph with depth limit."""
        symbols = self._create_test_symbols()
        dependencies = self._create_test_dependencies()

        result = self.builder.build(
            symbols=symbols,
            dependencies=dependencies,
            graph_type=GraphType.CLASS,
            max_depth=1
        )

        # Result should be limited
        assert result.metadata["graph_type"] == "class"

    def test_build_empty_symbols(self):
        """Test building graph with no symbols."""
        result = self.builder.build(
            symbols=[],
            dependencies=[],
            graph_type=GraphType.CLASS
        )

        assert len(result.nodes) == 0
        assert len(result.edges) == 0
        assert result.metadata["statistics"]["node_count"] == 0
        assert result.metadata["statistics"]["edge_count"] == 0

    def test_build_with_repository_info(self):
        """Test building graph with repository metadata."""
        symbols = self._create_test_symbols()
        repo_info = {
            "id": "/owner/repo",
            "provider": "github",
            "group": "owner",
            "project": "repo"
        }

        result = self.builder.build(
            symbols=symbols,
            dependencies=[],
            graph_type=GraphType.CLASS,
            repository_info=repo_info
        )

        assert result.metadata["repository"] == repo_info


class TestDependencyGraphJSONExport:
    """Test DependencyGraph.to_json() method."""

    def setup_method(self):
        """Set up graph builder for each test."""
        self.builder = DependencyGraph()

    def _create_simple_result(self):
        """Create a simple result for testing export."""
        nodes = {
            "src/a.py:ClassA": GraphNode(
                id="src/a.py:ClassA",
                label="ClassA",
                node_type="class",
                metadata={"file": "src/a.py", "line_start": 1, "language": "python"}
            ),
            "src/b.py:ClassB": GraphNode(
                id="src/b.py:ClassB",
                label="ClassB",
                node_type="class",
                metadata={"file": "src/b.py", "line_start": 5, "language": "python"}
            )
        }
        edges = [
            GraphEdge(
                source="src/b.py:ClassB",
                target="src/a.py:ClassA",
                relation="inherits",
                directed=True
            )
        ]
        return DependencyGraphResult(
            id="test-graph",
            label="Test Graph",
            graph_type=GraphType.CLASS,
            nodes=nodes,
            edges=edges,
            metadata={"generator": "repo-ctx", "version": "1.0.0"}
        )

    def test_to_json_valid_format(self):
        """Test that to_json produces valid JSON."""
        result = self._create_simple_result()
        json_str = self.builder.to_json(result)

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed is not None

    def test_to_json_jgf_structure(self):
        """Test that JSON follows JGF structure."""
        result = self._create_simple_result()
        json_str = self.builder.to_json(result)
        parsed = json.loads(json_str)

        # JGF top-level structure
        assert "graph" in parsed
        graph = parsed["graph"]
        assert "id" in graph
        assert "nodes" in graph
        assert "edges" in graph
        assert "directed" in graph
        assert graph["directed"] is True

    def test_to_json_nodes(self):
        """Test that nodes are correctly formatted."""
        result = self._create_simple_result()
        json_str = self.builder.to_json(result)
        parsed = json.loads(json_str)

        nodes = parsed["graph"]["nodes"]
        assert len(nodes) == 2

        # Check node structure
        for node_id, node in nodes.items():
            assert "label" in node
            assert "metadata" in node

    def test_to_json_edges(self):
        """Test that edges are correctly formatted."""
        result = self._create_simple_result()
        json_str = self.builder.to_json(result)
        parsed = json.loads(json_str)

        edges = parsed["graph"]["edges"]
        assert len(edges) == 1

        edge = edges[0]
        assert "source" in edge
        assert "target" in edge
        assert "relation" in edge
        assert "directed" in edge

    def test_to_json_metadata(self):
        """Test that metadata is included."""
        result = self._create_simple_result()
        json_str = self.builder.to_json(result)
        parsed = json.loads(json_str)

        assert "metadata" in parsed["graph"]
        assert parsed["graph"]["metadata"]["generator"] == "repo-ctx"


class TestDependencyGraphDOTExport:
    """Test DependencyGraph.to_dot() method."""

    def setup_method(self):
        """Set up graph builder for each test."""
        self.builder = DependencyGraph()

    def _create_simple_result(self):
        """Create a simple result for testing export."""
        nodes = {
            "src/a.py:ClassA": GraphNode(
                id="src/a.py:ClassA",
                label="ClassA",
                node_type="class",
                metadata={"file": "src/a.py", "line_start": 1}
            ),
            "src/b.py:ClassB": GraphNode(
                id="src/b.py:ClassB",
                label="ClassB",
                node_type="class",
                metadata={"file": "src/b.py", "line_start": 5}
            )
        }
        edges = [
            GraphEdge(
                source="src/b.py:ClassB",
                target="src/a.py:ClassA",
                relation="inherits"
            )
        ]
        return DependencyGraphResult(
            id="test-graph",
            label="Test Graph",
            graph_type=GraphType.CLASS,
            nodes=nodes,
            edges=edges
        )

    def test_to_dot_valid_syntax(self):
        """Test that to_dot produces valid DOT syntax."""
        result = self._create_simple_result()
        dot_str = self.builder.to_dot(result)

        # Should start with digraph
        assert dot_str.startswith('digraph')
        # Should have opening and closing braces
        assert '{' in dot_str
        assert dot_str.rstrip().endswith('}')

    def test_to_dot_contains_nodes(self):
        """Test that DOT output contains node definitions."""
        result = self._create_simple_result()
        dot_str = self.builder.to_dot(result)

        # Should contain node labels
        assert "ClassA" in dot_str
        assert "ClassB" in dot_str

    def test_to_dot_contains_edges(self):
        """Test that DOT output contains edge definitions."""
        result = self._create_simple_result()
        dot_str = self.builder.to_dot(result)

        # Should contain edge arrow
        assert "->" in dot_str
        assert "inherits" in dot_str

    def test_to_dot_node_colors(self):
        """Test that DOT output has colored nodes by type."""
        result = self._create_simple_result()
        dot_str = self.builder.to_dot(result)

        # Should have fillcolor attribute
        assert "fillcolor" in dot_str

    def test_to_dot_escapes_special_chars(self):
        """Test that special characters are escaped."""
        nodes = {
            'file:Class"Quote': GraphNode(
                id='file:Class"Quote',
                label='Class"Quote',
                node_type="class",
                metadata={}
            )
        }
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes=nodes,
            edges=[]
        )

        dot_str = self.builder.to_dot(result)
        # Quotes should be escaped
        assert '\\"' in dot_str


class TestDependencyGraphGraphMLExport:
    """Test DependencyGraph.to_graphml() method."""

    def setup_method(self):
        """Set up graph builder for each test."""
        self.builder = DependencyGraph()

    def _create_simple_result(self):
        """Create a simple result for testing export."""
        nodes = {
            "src/a.py:ClassA": GraphNode(
                id="src/a.py:ClassA",
                label="ClassA",
                node_type="class",
                metadata={"file": "src/a.py", "line_start": 1, "language": "python"}
            )
        }
        edges = []
        return DependencyGraphResult(
            id="test-graph",
            label="Test Graph",
            graph_type=GraphType.CLASS,
            nodes=nodes,
            edges=edges
        )

    def test_to_graphml_valid_xml(self):
        """Test that to_graphml produces valid XML structure."""
        result = self._create_simple_result()
        xml_str = self.builder.to_graphml(result)

        # Should start with XML declaration
        assert xml_str.startswith('<?xml')
        # Should have graphml element
        assert '<graphml' in xml_str
        assert '</graphml>' in xml_str

    def test_to_graphml_contains_nodes(self):
        """Test that GraphML output contains node elements."""
        result = self._create_simple_result()
        xml_str = self.builder.to_graphml(result)

        # Should contain node element
        assert '<node id=' in xml_str
        assert '</node>' in xml_str

    def test_to_graphml_key_definitions(self):
        """Test that GraphML output has key definitions for attributes."""
        result = self._create_simple_result()
        xml_str = self.builder.to_graphml(result)

        # Should have key definitions
        assert '<key id="label"' in xml_str
        assert '<key id="type"' in xml_str

    def test_to_graphml_data_elements(self):
        """Test that GraphML output has data elements for node attributes."""
        result = self._create_simple_result()
        xml_str = self.builder.to_graphml(result)

        # Should have data elements
        assert '<data key="label">' in xml_str
        assert 'ClassA' in xml_str

    def test_to_graphml_escapes_xml(self):
        """Test that XML special characters are escaped."""
        nodes = {
            "file:Class<T>": GraphNode(
                id="file:Class<T>",
                label="Class<T>",
                node_type="class",
                metadata={}
            )
        }
        result = DependencyGraphResult(
            id="test",
            label="Test",
            graph_type=GraphType.CLASS,
            nodes=nodes,
            edges=[]
        )

        xml_str = self.builder.to_graphml(result)
        # < and > should be escaped
        assert '&lt;' in xml_str
        assert '&gt;' in xml_str


class TestDependencyGraphWithCodeAnalyzer:
    """Integration tests for DependencyGraph with CodeAnalyzer."""

    def setup_method(self):
        """Set up analyzer and graph builder for each test."""
        from repo_ctx.analysis import CodeAnalyzer
        self.analyzer = CodeAnalyzer()
        self.graph_builder = DependencyGraph()

    def test_analyze_and_build_python_graph(self):
        """Test analyzing Python code and building a dependency graph."""
        code = """
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof"

class Cat(Animal):
    def speak(self):
        return "Meow"

def get_animal(kind):
    if kind == "dog":
        return Dog()
    return Cat()
"""
        symbols = self.analyzer.analyze_file(code, "animals.py")
        dependencies = self.analyzer.extract_dependencies(code, "animals.py")

        result = self.graph_builder.build(
            symbols=symbols,
            dependencies=dependencies,
            graph_type=GraphType.CLASS,
            graph_id="animals-project"
        )

        # Should have class nodes
        class_names = [n.label for n in result.nodes.values() if n.node_type == "class"]
        assert "Animal" in class_names
        assert "Dog" in class_names
        assert "Cat" in class_names

        # Should have inheritance edges
        inherit_edges = [e for e in result.edges if e.relation == "inherits"]
        assert len(inherit_edges) >= 2  # Dog->Animal, Cat->Animal

    def test_analyze_and_build_javascript_graph(self):
        """Test analyzing JavaScript code and building a dependency graph."""
        code = """
class Component {
    render() {
        return null;
    }
}

class Button extends Component {
    render() {
        return "button";
    }
}

function createComponent(type) {
    return new Button();
}
"""
        symbols = self.analyzer.analyze_file(code, "components.js")
        dependencies = self.analyzer.extract_dependencies(code, "components.js")

        result = self.graph_builder.build(
            symbols=symbols,
            dependencies=dependencies,
            graph_type=GraphType.CLASS,
            graph_id="js-project"
        )

        # Should have class nodes
        class_names = [n.label for n in result.nodes.values() if n.node_type == "class"]
        assert "Component" in class_names
        assert "Button" in class_names

    def test_build_multi_file_graph(self):
        """Test building a graph from multiple files."""
        files = {
            "base.py": """
class BaseModel:
    def save(self):
        pass
""",
            "user.py": """
from base import BaseModel

class User(BaseModel):
    def __init__(self, name):
        self.name = name
""",
            "admin.py": """
from user import User

class Admin(User):
    def has_permission(self):
        return True
"""
        }

        # Analyze all files
        all_symbols = []
        all_dependencies = []
        for file_path, code in files.items():
            symbols = self.analyzer.analyze_file(code, file_path)
            deps = self.analyzer.extract_dependencies(code, file_path)
            all_symbols.extend(symbols)
            all_dependencies.extend(deps)

        result = self.graph_builder.build(
            symbols=all_symbols,
            dependencies=all_dependencies,
            graph_type=GraphType.CLASS,
            graph_id="multi-file-project"
        )

        # Should have class nodes from all files
        class_names = [n.label for n in result.nodes.values() if n.node_type == "class"]
        assert "BaseModel" in class_names
        assert "User" in class_names
        assert "Admin" in class_names

        # Export to all formats should work
        json_output = self.graph_builder.to_json(result)
        assert "BaseModel" in json_output

        dot_output = self.graph_builder.to_dot(result)
        assert "BaseModel" in dot_output

        graphml_output = self.graph_builder.to_graphml(result)
        assert "BaseModel" in graphml_output


class TestCallExtraction:
    """Test function call extraction for dependency graphs."""

    def setup_method(self):
        """Set up analyzer and graph builder for each test."""
        from repo_ctx.analysis import CodeAnalyzer
        self.analyzer = CodeAnalyzer()
        self.graph_builder = DependencyGraph()

    def test_extract_calls_from_python(self):
        """Test extracting function calls from Python code."""
        code = """
def helper():
    return 42

def process():
    result = helper()
    return result

def main():
    process()
    helper()
"""
        symbols = self.analyzer.analyze_file(code, "test.py")
        deps = self.analyzer.extract_dependencies(code, "test.py", symbols)

        # Should have call dependencies
        call_deps = [d for d in deps if d.get("type") == "call"]
        assert len(call_deps) >= 3  # process->helper, main->process, main->helper

        # Check that caller/callee are present
        for dep in call_deps:
            assert "caller" in dep
            assert "callee" in dep

    def test_function_graph_has_call_edges(self):
        """Test that function graph includes call edges."""
        code = """
def func_a():
    func_b()

def func_b():
    func_c()

def func_c():
    pass
"""
        symbols = self.analyzer.analyze_file(code, "test.py")
        deps = self.analyzer.extract_dependencies(code, "test.py", symbols)

        result = self.graph_builder.build(
            symbols=symbols,
            dependencies=deps,
            graph_type=GraphType.FUNCTION,
            graph_id="call-test"
        )

        # Should have edges for the calls
        assert result.metadata["statistics"]["edge_count"] >= 2

        # Verify edge relations
        call_edges = [e for e in result.edges if e.relation == "calls"]
        assert len(call_edges) >= 2

    def test_method_calls_within_class(self):
        """Test extracting method calls within a class."""
        code = """
class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b

    def compute(self, a, b):
        sum_result = self.add(a, b)
        product = self.multiply(a, b)
        return sum_result, product
"""
        symbols = self.analyzer.analyze_file(code, "test.py")
        deps = self.analyzer.extract_dependencies(code, "test.py", symbols)

        # Should have call dependencies from compute to add and multiply
        call_deps = [d for d in deps if d.get("type") == "call"]
        assert len(call_deps) >= 2

        # Verify the caller is compute method
        compute_calls = [d for d in call_deps if "compute" in d.get("caller", "")]
        assert len(compute_calls) >= 2


class TestDepthLimiting:
    """Test depth limiting functionality."""

    def setup_method(self):
        """Set up graph builder for each test."""
        self.builder = DependencyGraph()

    def test_depth_limit_zero(self):
        """Test that depth 0 or negative returns all nodes."""
        nodes = {
            "a": GraphNode(id="a", label="A", node_type="class"),
            "b": GraphNode(id="b", label="B", node_type="class"),
            "c": GraphNode(id="c", label="C", node_type="class"),
        }
        edges = [
            GraphEdge(source="a", target="b", relation="inherits"),
            GraphEdge(source="b", target="c", relation="inherits"),
        ]

        filtered_nodes, filtered_edges = self.builder._apply_depth_limit(nodes, edges, 0)
        # depth 0 should return all nodes (as per implementation)
        assert len(filtered_nodes) == 3

    def test_depth_limit_one(self):
        """Test depth limit of 1."""
        nodes = {
            "root": GraphNode(id="root", label="Root", node_type="class"),
            "child1": GraphNode(id="child1", label="Child1", node_type="class"),
            "grandchild": GraphNode(id="grandchild", label="Grandchild", node_type="class"),
        }
        edges = [
            GraphEdge(source="root", target="child1", relation="contains"),
            GraphEdge(source="child1", target="grandchild", relation="contains"),
        ]

        filtered_nodes, filtered_edges = self.builder._apply_depth_limit(nodes, edges, 1)
        # With depth 1, should include root and child1
        assert "root" in filtered_nodes
        assert "child1" in filtered_nodes

    def test_depth_limit_preserves_edges(self):
        """Test that depth limiting preserves valid edges."""
        nodes = {
            "a": GraphNode(id="a", label="A", node_type="class"),
            "b": GraphNode(id="b", label="B", node_type="class"),
        }
        edges = [
            GraphEdge(source="a", target="b", relation="inherits"),
        ]

        filtered_nodes, filtered_edges = self.builder._apply_depth_limit(nodes, edges, 2)
        # Both nodes should be kept
        assert len(filtered_nodes) == 2
        # Edge should be preserved
        assert len(filtered_edges) == 1
