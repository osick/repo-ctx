"""Tests for InteractiveGraphGenerator.

This module tests the interactive HTML graph generation functionality.
"""

import json
import pytest
from pathlib import Path

from repo_ctx.analysis.interactive_graph import InteractiveGraphGenerator


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def generator():
    """Create an InteractiveGraphGenerator instance."""
    return InteractiveGraphGenerator()


@pytest.fixture
def sample_nodes():
    """Create sample node data."""
    return [
        {"id": "main.py", "type": "file"},
        {"id": "utils.py", "type": "file"},
        {"id": "models.py", "type": "file"},
    ]


@pytest.fixture
def sample_edges():
    """Create sample edge data."""
    return [
        ("main.py", "utils.py", "import"),
        ("main.py", "models.py", "import"),
        ("utils.py", "models.py", "call"),
    ]


# =============================================================================
# Basic Generation Tests
# =============================================================================


class TestInteractiveGraphGeneration:
    """Tests for basic graph generation."""

    def test_generate_creates_html_file(self, generator, sample_nodes, sample_edges, tmp_path):
        """Test generate creates an HTML file."""
        output_path = tmp_path / "graph.html"

        result = generator.generate(
            nodes=sample_nodes,
            edges=sample_edges,
            output_path=output_path,
            title="Test Graph",
        )

        assert result == output_path
        assert output_path.exists()
        assert output_path.suffix == ".html"

    def test_generated_html_contains_vis_js(self, generator, sample_nodes, sample_edges, tmp_path):
        """Test generated HTML contains vis.js references."""
        output_path = tmp_path / "graph.html"

        generator.generate(
            nodes=sample_nodes,
            edges=sample_edges,
            output_path=output_path,
        )

        content = output_path.read_text()
        assert "vis-network" in content

    def test_generated_html_contains_graph_data(self, generator, sample_nodes, sample_edges, tmp_path):
        """Test generated HTML contains the graph data as JSON."""
        output_path = tmp_path / "graph.html"

        generator.generate(
            nodes=sample_nodes,
            edges=sample_edges,
            output_path=output_path,
        )

        content = output_path.read_text()
        # Should contain node IDs
        assert "main.py" in content
        assert "utils.py" in content
        assert "models.py" in content

    def test_generated_html_contains_title(self, generator, sample_nodes, sample_edges, tmp_path):
        """Test generated HTML contains the specified title."""
        output_path = tmp_path / "graph.html"
        title = "My Custom Graph Title"

        generator.generate(
            nodes=sample_nodes,
            edges=sample_edges,
            output_path=output_path,
            title=title,
        )

        content = output_path.read_text()
        assert title in content

    def test_generate_creates_parent_directories(self, generator, sample_nodes, sample_edges, tmp_path):
        """Test generate creates parent directories if they don't exist."""
        output_path = tmp_path / "nested" / "deep" / "graph.html"

        generator.generate(
            nodes=sample_nodes,
            edges=sample_edges,
            output_path=output_path,
        )

        assert output_path.exists()


# =============================================================================
# Node Handling Tests
# =============================================================================


class TestNodeHandling:
    """Tests for node processing."""

    def test_handles_string_nodes(self, generator, tmp_path):
        """Test handles nodes as simple strings."""
        nodes = ["file1.py", "file2.py"]
        edges = [("file1.py", "file2.py", "import")]
        output_path = tmp_path / "graph.html"

        generator.generate(nodes=nodes, edges=edges, output_path=output_path)

        content = output_path.read_text()
        assert "file1.py" in content
        assert "file2.py" in content

    def test_handles_dict_nodes(self, generator, tmp_path):
        """Test handles nodes as dictionaries."""
        nodes = [
            {"id": "file1.py", "type": "file", "label": "File 1"},
            {"id": "file2.py", "type": "class", "label": "File 2"},
        ]
        edges = [("file1.py", "file2.py", "import")]
        output_path = tmp_path / "graph.html"

        generator.generate(nodes=nodes, edges=edges, output_path=output_path)

        content = output_path.read_text()
        assert "file1.py" in content
        assert "file2.py" in content

    def test_calculates_node_degrees(self, generator, tmp_path):
        """Test node degrees are calculated correctly."""
        nodes = [
            {"id": "hub.py"},
            {"id": "spoke1.py"},
            {"id": "spoke2.py"},
        ]
        # hub.py has 2 outgoing edges
        edges = [
            ("hub.py", "spoke1.py", "import"),
            ("hub.py", "spoke2.py", "import"),
        ]
        output_path = tmp_path / "graph.html"

        generator.generate(nodes=nodes, edges=edges, output_path=output_path)

        content = output_path.read_text()
        # Parse the graphData from the HTML
        assert "graphData" in content


# =============================================================================
# Edge Handling Tests
# =============================================================================


class TestEdgeHandling:
    """Tests for edge processing."""

    def test_handles_edge_types(self, generator, tmp_path):
        """Test handles different edge types."""
        nodes = [{"id": "a.py"}, {"id": "b.py"}]
        edges = [("a.py", "b.py", "import")]
        output_path = tmp_path / "graph.html"

        generator.generate(nodes=nodes, edges=edges, output_path=output_path)

        content = output_path.read_text()
        assert "import" in content

    def test_handles_empty_edge_type(self, generator, tmp_path):
        """Test handles edges with no type."""
        nodes = [{"id": "a.py"}, {"id": "b.py"}]
        edges = [("a.py", "b.py", None)]
        output_path = tmp_path / "graph.html"

        generator.generate(nodes=nodes, edges=edges, output_path=output_path)

        content = output_path.read_text()
        assert "depends" in content  # Default type


# =============================================================================
# Cycle Handling Tests
# =============================================================================


class TestCycleHandling:
    """Tests for cycle visualization."""

    def test_cycles_are_included_in_config(self, generator, tmp_path):
        """Test cycles are included in the config."""
        nodes = [{"id": "a.py"}, {"id": "b.py"}]
        edges = [("a.py", "b.py", "import"), ("b.py", "a.py", "import")]
        cycles = [{"nodes": ["a.py", "b.py"]}]
        output_path = tmp_path / "graph.html"

        generator.generate(
            nodes=nodes,
            edges=edges,
            output_path=output_path,
            cycles=cycles,
        )

        content = output_path.read_text()
        # Config should contain cycles_count
        assert "cycles_count" in content

    def test_cycle_nodes_are_marked(self, generator, tmp_path):
        """Test nodes in cycles are marked."""
        nodes = [{"id": "a.py"}, {"id": "b.py"}, {"id": "c.py"}]
        edges = [("a.py", "b.py", "import"), ("b.py", "a.py", "import")]
        cycles = [["a.py", "b.py"]]  # List of node lists
        output_path = tmp_path / "graph.html"

        generator.generate(
            nodes=nodes,
            edges=edges,
            output_path=output_path,
            cycles=cycles,
        )

        content = output_path.read_text()
        assert "cycle_nodes" in content


# =============================================================================
# Layer Handling Tests
# =============================================================================


class TestLayerHandling:
    """Tests for layer visualization."""

    def test_layers_are_included_in_config(self, generator, tmp_path):
        """Test layers count is included in the config."""
        nodes = [{"id": "a.py"}, {"id": "b.py"}]
        edges = [("a.py", "b.py", "import")]
        layers = [
            {"level": 0, "nodes": ["a.py"]},
            {"level": 1, "nodes": ["b.py"]},
        ]
        output_path = tmp_path / "graph.html"

        generator.generate(
            nodes=nodes,
            edges=edges,
            output_path=output_path,
            layers=layers,
        )

        content = output_path.read_text()
        assert "layers_count" in content


# =============================================================================
# Architecture Data Integration Tests
# =============================================================================


class TestArchitectureDataIntegration:
    """Tests for generate_from_arch_data method."""

    def test_generate_from_arch_data(self, generator, tmp_path):
        """Test generation from architecture data dict."""
        arch_data = {
            "nodes": ["main.py", "utils.py"],
            "edges": [("main.py", "utils.py", "import")],
            "cycles": {"cycles": []},
            "layers": {"layers": []},
        }
        output_path = tmp_path / "arch_graph.html"

        result = generator.generate_from_arch_data(
            arch_data=arch_data,
            output_path=output_path,
            title="Architecture Graph",
        )

        assert result == output_path
        assert output_path.exists()

        content = output_path.read_text()
        assert "main.py" in content
        assert "Architecture Graph" in content

    def test_generate_from_arch_data_with_cycles(self, generator, tmp_path):
        """Test generation from arch data with cycles."""
        arch_data = {
            "nodes": ["a.py", "b.py"],
            "edges": [("a.py", "b.py", "import"), ("b.py", "a.py", "import")],
            "cycles": {
                "cycles": [{"nodes": ["a.py", "b.py"]}]
            },
            "layers": {"layers": []},
        }
        output_path = tmp_path / "graph.html"

        generator.generate_from_arch_data(arch_data, output_path)

        content = output_path.read_text()
        assert "cycles_count" in content


# =============================================================================
# HTML Content Tests
# =============================================================================


class TestHTMLContent:
    """Tests for HTML content structure."""

    def test_html_has_proper_structure(self, generator, sample_nodes, sample_edges, tmp_path):
        """Test HTML has proper DOCTYPE and structure."""
        output_path = tmp_path / "graph.html"

        generator.generate(
            nodes=sample_nodes,
            edges=sample_edges,
            output_path=output_path,
        )

        content = output_path.read_text()
        assert "<!DOCTYPE html>" in content
        assert "<html>" in content
        assert "</html>" in content
        assert "<head>" in content
        assert "<body>" in content

    def test_html_has_sidebar(self, generator, sample_nodes, sample_edges, tmp_path):
        """Test HTML has sidebar with statistics."""
        output_path = tmp_path / "graph.html"

        generator.generate(
            nodes=sample_nodes,
            edges=sample_edges,
            output_path=output_path,
        )

        content = output_path.read_text()
        assert 'id="sidebar"' in content
        assert 'id="stats"' in content
        assert 'id="legend"' in content

    def test_html_has_controls(self, generator, sample_nodes, sample_edges, tmp_path):
        """Test HTML has filter and layout controls."""
        output_path = tmp_path / "graph.html"

        generator.generate(
            nodes=sample_nodes,
            edges=sample_edges,
            output_path=output_path,
        )

        content = output_path.read_text()
        assert 'id="controls"' in content
        assert 'id="filter-type"' in content
        assert 'id="search"' in content
        assert 'id="layout"' in content

    def test_html_has_graph_container(self, generator, sample_nodes, sample_edges, tmp_path):
        """Test HTML has graph container."""
        output_path = tmp_path / "graph.html"

        generator.generate(
            nodes=sample_nodes,
            edges=sample_edges,
            output_path=output_path,
        )

        content = output_path.read_text()
        assert 'id="graph"' in content


# =============================================================================
# Edge Cases Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_graph(self, generator, tmp_path):
        """Test generation with empty graph."""
        output_path = tmp_path / "empty.html"

        generator.generate(
            nodes=[],
            edges=[],
            output_path=output_path,
        )

        assert output_path.exists()
        content = output_path.read_text()
        assert "graphData" in content

    def test_single_node_no_edges(self, generator, tmp_path):
        """Test generation with single node and no edges."""
        nodes = [{"id": "lonely.py"}]
        output_path = tmp_path / "single.html"

        generator.generate(
            nodes=nodes,
            edges=[],
            output_path=output_path,
        )

        assert output_path.exists()
        content = output_path.read_text()
        assert "lonely.py" in content

    def test_special_characters_in_node_id(self, generator, tmp_path):
        """Test handles special characters in node IDs."""
        nodes = [{"id": "path/to/file.py"}, {"id": "other/file.py"}]
        edges = [("path/to/file.py", "other/file.py", "import")]
        output_path = tmp_path / "special.html"

        generator.generate(
            nodes=nodes,
            edges=edges,
            output_path=output_path,
        )

        assert output_path.exists()
        content = output_path.read_text()
        # Should handle path separators
        assert "file.py" in content
