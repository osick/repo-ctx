"""Tests for GraphStorage implementation.

These tests verify that GraphStorage correctly implements
GraphStorageProtocol using Neo4j.
"""

import pytest
import pytest_asyncio

from repo_ctx.storage.protocols import (
    GraphStorageProtocol,
    GraphNode,
    GraphRelationship,
    GraphResult,
)


class TestGraphStorageCreation:
    """Tests for GraphStorage class existence and initialization."""

    def test_graph_storage_exists(self):
        """GraphStorage class should exist."""
        from repo_ctx.storage.graph import GraphStorage

        assert GraphStorage is not None

    def test_graph_storage_implements_protocol(self):
        """GraphStorage should implement GraphStorageProtocol."""
        from repo_ctx.storage.graph import GraphStorage

        storage = GraphStorage(in_memory=True)
        assert isinstance(storage, GraphStorageProtocol)

    def test_graph_storage_accepts_uri(self):
        """GraphStorage should accept a connection URI."""
        from repo_ctx.storage.graph import GraphStorage

        # Use in_memory=True to avoid needing neo4j driver
        storage = GraphStorage(in_memory=True, uri="bolt://localhost:7687")
        assert storage.uri == "bolt://localhost:7687"

    def test_graph_storage_accepts_credentials(self):
        """GraphStorage should accept username and password."""
        from repo_ctx.storage.graph import GraphStorage

        storage = GraphStorage(
            in_memory=True,
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password123",
        )
        assert storage.username == "neo4j"
        assert storage.password == "password123"

    def test_graph_storage_default_credentials(self):
        """GraphStorage should have default credentials."""
        from repo_ctx.storage.graph import GraphStorage

        storage = GraphStorage(in_memory=True)
        assert storage.username == "neo4j"
        assert storage.password is None

    def test_graph_storage_accepts_database(self):
        """GraphStorage should accept database name."""
        from repo_ctx.storage.graph import GraphStorage

        storage = GraphStorage(
            in_memory=True,
            uri="bolt://localhost:7687",
            database="mydb",
        )
        assert storage.database == "mydb"

    def test_graph_storage_in_memory_mode(self):
        """GraphStorage should support in-memory mode for testing."""
        from repo_ctx.storage.graph import GraphStorage

        storage = GraphStorage(in_memory=True)
        assert storage.in_memory is True


class TestGraphStorageInMemory:
    """Tests for GraphStorage using in-memory mode."""

    @pytest_asyncio.fixture
    async def storage(self):
        """Create an in-memory GraphStorage instance."""
        from repo_ctx.storage.graph import GraphStorage

        storage = GraphStorage(in_memory=True)
        yield storage
        # Cleanup
        await storage.clear()

    @pytest.mark.asyncio
    async def test_health_check_in_memory(self, storage):
        """health_check should return True for in-memory storage."""
        result = await storage.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_create_nodes(self, storage):
        """create_nodes should store nodes successfully."""
        nodes = [
            GraphNode(
                id="node_1",
                labels=["Symbol", "Function"],
                properties={"name": "my_function", "library_id": "test/repo"},
            ),
            GraphNode(
                id="node_2",
                labels=["Symbol", "Class"],
                properties={"name": "MyClass", "library_id": "test/repo"},
            ),
        ]

        await storage.create_nodes(nodes)

        # Verify nodes were created
        result = await storage.query("MATCH (n) RETURN n.id as id, labels(n) as labels")
        assert len(result) == 2
        ids = {r["id"] for r in result}
        assert "node_1" in ids
        assert "node_2" in ids

    @pytest.mark.asyncio
    async def test_create_nodes_with_properties(self, storage):
        """create_nodes should store node properties."""
        nodes = [
            GraphNode(
                id="func_1",
                labels=["Function"],
                properties={
                    "name": "calculate_total",
                    "language": "python",
                    "visibility": "public",
                    "line_number": 42,
                },
            ),
        ]

        await storage.create_nodes(nodes)

        result = await storage.query(
            "MATCH (n:Function {id: $id}) RETURN n",
            params={"id": "func_1"},
        )
        assert len(result) == 1
        node = result[0]["n"]
        assert node["name"] == "calculate_total"
        assert node["language"] == "python"
        assert node["visibility"] == "public"
        assert node["line_number"] == 42

    @pytest.mark.asyncio
    async def test_create_relationships(self, storage):
        """create_relationships should create edges between nodes."""
        # First create nodes
        nodes = [
            GraphNode(id="caller", labels=["Function"], properties={"name": "main"}),
            GraphNode(id="callee", labels=["Function"], properties={"name": "helper"}),
        ]
        await storage.create_nodes(nodes)

        # Then create relationship
        relationships = [
            GraphRelationship(
                from_id="caller",
                to_id="callee",
                type="CALLS",
                properties={"count": 3},
            ),
        ]
        await storage.create_relationships(relationships)

        # Verify relationship exists
        result = await storage.query(
            "MATCH (a)-[r:CALLS]->(b) RETURN a.id as from, b.id as to, type(r) as type"
        )
        assert len(result) == 1
        assert result[0]["from"] == "caller"
        assert result[0]["to"] == "callee"
        assert result[0]["type"] == "CALLS"

    @pytest.mark.asyncio
    async def test_create_relationships_with_properties(self, storage):
        """create_relationships should store relationship properties."""
        nodes = [
            GraphNode(id="module_a", labels=["Module"], properties={"name": "utils"}),
            GraphNode(id="module_b", labels=["Module"], properties={"name": "core"}),
        ]
        await storage.create_nodes(nodes)

        relationships = [
            GraphRelationship(
                from_id="module_a",
                to_id="module_b",
                type="IMPORTS",
                properties={"alias": "c", "is_relative": False},
            ),
        ]
        await storage.create_relationships(relationships)

        result = await storage.query(
            "MATCH ()-[r:IMPORTS]->() RETURN r.alias as alias, r.is_relative as is_relative"
        )
        assert len(result) == 1
        assert result[0]["alias"] == "c"
        assert result[0]["is_relative"] is False

    @pytest.mark.asyncio
    async def test_query_with_params(self, storage):
        """query should support parameterized Cypher queries."""
        nodes = [
            GraphNode(id="py_func", labels=["Function"], properties={"language": "python"}),
            GraphNode(id="js_func", labels=["Function"], properties={"language": "javascript"}),
        ]
        await storage.create_nodes(nodes)

        result = await storage.query(
            "MATCH (n:Function {language: $lang}) RETURN n.id as id",
            params={"lang": "python"},
        )
        assert len(result) == 1
        assert result[0]["id"] == "py_func"

    @pytest.mark.asyncio
    async def test_get_call_graph_outgoing(self, storage):
        """get_call_graph should return outgoing calls."""
        # Create call hierarchy: main -> helper -> util
        nodes = [
            GraphNode(id="main", labels=["Function"], properties={"name": "main"}),
            GraphNode(id="helper", labels=["Function"], properties={"name": "helper"}),
            GraphNode(id="util", labels=["Function"], properties={"name": "util"}),
        ]
        await storage.create_nodes(nodes)

        relationships = [
            GraphRelationship(from_id="main", to_id="helper", type="CALLS"),
            GraphRelationship(from_id="helper", to_id="util", type="CALLS"),
        ]
        await storage.create_relationships(relationships)

        result = await storage.get_call_graph("main", depth=2, direction="outgoing")

        assert isinstance(result, GraphResult)
        assert len(result.nodes) >= 2  # main, helper (maybe util at depth 2)
        assert len(result.relationships) >= 1

    @pytest.mark.asyncio
    async def test_get_call_graph_incoming(self, storage):
        """get_call_graph should return incoming calls."""
        nodes = [
            GraphNode(id="main", labels=["Function"], properties={"name": "main"}),
            GraphNode(id="helper", labels=["Function"], properties={"name": "helper"}),
        ]
        await storage.create_nodes(nodes)

        relationships = [
            GraphRelationship(from_id="main", to_id="helper", type="CALLS"),
        ]
        await storage.create_relationships(relationships)

        result = await storage.get_call_graph("helper", depth=1, direction="incoming")

        assert isinstance(result, GraphResult)
        # Should find main as caller
        node_ids = {n.id for n in result.nodes}
        assert "helper" in node_ids or "main" in node_ids

    @pytest.mark.asyncio
    async def test_get_call_graph_both_directions(self, storage):
        """get_call_graph should return both incoming and outgoing calls."""
        nodes = [
            GraphNode(id="caller", labels=["Function"], properties={"name": "caller"}),
            GraphNode(id="middle", labels=["Function"], properties={"name": "middle"}),
            GraphNode(id="callee", labels=["Function"], properties={"name": "callee"}),
        ]
        await storage.create_nodes(nodes)

        relationships = [
            GraphRelationship(from_id="caller", to_id="middle", type="CALLS"),
            GraphRelationship(from_id="middle", to_id="callee", type="CALLS"),
        ]
        await storage.create_relationships(relationships)

        result = await storage.get_call_graph("middle", depth=1, direction="both")

        assert isinstance(result, GraphResult)
        assert len(result.nodes) >= 2

    @pytest.mark.asyncio
    async def test_delete_by_library(self, storage):
        """delete_by_library should remove all nodes for a library."""
        nodes = [
            GraphNode(id="lib1_func", labels=["Function"], properties={"library_id": "/lib/one"}),
            GraphNode(id="lib2_func", labels=["Function"], properties={"library_id": "/lib/two"}),
        ]
        await storage.create_nodes(nodes)

        deleted = await storage.delete_by_library("/lib/one")

        assert deleted == 1

        # Verify only lib2 node remains
        result = await storage.query("MATCH (n) RETURN n.id as id")
        ids = {r["id"] for r in result}
        assert "lib1_func" not in ids
        assert "lib2_func" in ids

    @pytest.mark.asyncio
    async def test_delete_by_library_removes_relationships(self, storage):
        """delete_by_library should remove relationships of deleted nodes."""
        nodes = [
            GraphNode(id="node_a", labels=["Function"], properties={"library_id": "/lib/one"}),
            GraphNode(id="node_b", labels=["Function"], properties={"library_id": "/lib/one"}),
            GraphNode(id="node_c", labels=["Function"], properties={"library_id": "/lib/two"}),
        ]
        await storage.create_nodes(nodes)

        relationships = [
            GraphRelationship(from_id="node_a", to_id="node_b", type="CALLS"),
            GraphRelationship(from_id="node_c", to_id="node_a", type="CALLS"),
        ]
        await storage.create_relationships(relationships)

        await storage.delete_by_library("/lib/one")

        # Verify no relationships remain (both involving deleted nodes)
        result = await storage.query("MATCH ()-[r]->() RETURN count(r) as count")
        assert result[0]["count"] == 0


class TestGraphStorageMultipleLabels:
    """Tests for nodes with multiple labels."""

    @pytest_asyncio.fixture
    async def storage(self):
        """Create an in-memory GraphStorage instance."""
        from repo_ctx.storage.graph import GraphStorage

        storage = GraphStorage(in_memory=True)
        yield storage
        await storage.clear()

    @pytest.mark.asyncio
    async def test_node_with_multiple_labels(self, storage):
        """Nodes should support multiple labels."""
        nodes = [
            GraphNode(
                id="my_class",
                labels=["Symbol", "Class", "PublicAPI"],
                properties={"name": "MyClass"},
            ),
        ]
        await storage.create_nodes(nodes)

        result = await storage.query(
            "MATCH (n:Symbol:Class:PublicAPI) RETURN n.id as id"
        )
        assert len(result) == 1
        assert result[0]["id"] == "my_class"


class TestGraphStorageRelationshipTypes:
    """Tests for different relationship types."""

    @pytest_asyncio.fixture
    async def storage(self):
        """Create an in-memory GraphStorage instance."""
        from repo_ctx.storage.graph import GraphStorage

        storage = GraphStorage(in_memory=True)
        yield storage
        await storage.clear()

    @pytest.mark.asyncio
    async def test_calls_relationship(self, storage):
        """CALLS relationship should be created correctly."""
        await self._create_relationship(storage, "CALLS")
        result = await storage.query("MATCH ()-[r:CALLS]->() RETURN count(r) as count")
        assert result[0]["count"] == 1

    @pytest.mark.asyncio
    async def test_imports_relationship(self, storage):
        """IMPORTS relationship should be created correctly."""
        await self._create_relationship(storage, "IMPORTS")
        result = await storage.query("MATCH ()-[r:IMPORTS]->() RETURN count(r) as count")
        assert result[0]["count"] == 1

    @pytest.mark.asyncio
    async def test_extends_relationship(self, storage):
        """EXTENDS relationship should be created correctly."""
        await self._create_relationship(storage, "EXTENDS")
        result = await storage.query("MATCH ()-[r:EXTENDS]->() RETURN count(r) as count")
        assert result[0]["count"] == 1

    @pytest.mark.asyncio
    async def test_implements_relationship(self, storage):
        """IMPLEMENTS relationship should be created correctly."""
        await self._create_relationship(storage, "IMPLEMENTS")
        result = await storage.query("MATCH ()-[r:IMPLEMENTS]->() RETURN count(r) as count")
        assert result[0]["count"] == 1

    @pytest.mark.asyncio
    async def test_contains_relationship(self, storage):
        """CONTAINS relationship should be created correctly."""
        await self._create_relationship(storage, "CONTAINS")
        result = await storage.query("MATCH ()-[r:CONTAINS]->() RETURN count(r) as count")
        assert result[0]["count"] == 1

    async def _create_relationship(self, storage, rel_type: str):
        """Helper to create a relationship of given type."""
        nodes = [
            GraphNode(id="from_node", labels=["Node"], properties={}),
            GraphNode(id="to_node", labels=["Node"], properties={}),
        ]
        await storage.create_nodes(nodes)
        await storage.create_relationships([
            GraphRelationship(from_id="from_node", to_id="to_node", type=rel_type)
        ])


class TestGraphStorageErrorHandling:
    """Tests for error handling in GraphStorage."""

    @pytest_asyncio.fixture
    async def storage(self):
        """Create an in-memory GraphStorage instance."""
        from repo_ctx.storage.graph import GraphStorage

        storage = GraphStorage(in_memory=True)
        yield storage
        await storage.clear()

    @pytest.mark.asyncio
    async def test_invalid_cypher_query(self, storage):
        """Invalid Cypher should raise StorageError."""
        from repo_ctx.exceptions import StorageError

        with pytest.raises(StorageError):
            await storage.query("INVALID CYPHER QUERY")

    @pytest.mark.asyncio
    async def test_relationship_with_missing_node(self, storage):
        """Creating relationship with missing node should handle gracefully."""
        # Only create one node
        nodes = [GraphNode(id="existing", labels=["Node"], properties={})]
        await storage.create_nodes(nodes)

        # Try to create relationship to non-existing node
        relationships = [
            GraphRelationship(from_id="existing", to_id="missing", type="CALLS")
        ]

        # Should not raise, but relationship won't be created
        await storage.create_relationships(relationships)

        result = await storage.query("MATCH ()-[r]->() RETURN count(r) as count")
        assert result[0]["count"] == 0

    @pytest.mark.asyncio
    async def test_get_call_graph_nonexistent_symbol(self, storage):
        """get_call_graph for nonexistent symbol should return empty result."""
        result = await storage.get_call_graph("nonexistent_symbol", depth=1, direction="both")

        assert isinstance(result, GraphResult)
        assert len(result.nodes) == 0
        assert len(result.relationships) == 0


class TestGraphStorageBatchOperations:
    """Tests for batch operations in GraphStorage."""

    @pytest_asyncio.fixture
    async def storage(self):
        """Create an in-memory GraphStorage instance."""
        from repo_ctx.storage.graph import GraphStorage

        storage = GraphStorage(in_memory=True)
        yield storage
        await storage.clear()

    @pytest.mark.asyncio
    async def test_create_many_nodes(self, storage):
        """Should handle creating many nodes efficiently."""
        nodes = [
            GraphNode(
                id=f"node_{i}",
                labels=["Function"],
                properties={"name": f"func_{i}", "library_id": "/test/repo"},
            )
            for i in range(100)
        ]

        await storage.create_nodes(nodes)

        result = await storage.query("MATCH (n:Function) RETURN count(n) as count")
        assert result[0]["count"] == 100

    @pytest.mark.asyncio
    async def test_create_many_relationships(self, storage):
        """Should handle creating many relationships efficiently."""
        # Create nodes first
        nodes = [
            GraphNode(id=f"node_{i}", labels=["Node"], properties={})
            for i in range(50)
        ]
        await storage.create_nodes(nodes)

        # Create chain of relationships
        relationships = [
            GraphRelationship(
                from_id=f"node_{i}",
                to_id=f"node_{i+1}",
                type="CALLS",
            )
            for i in range(49)
        ]
        await storage.create_relationships(relationships)

        result = await storage.query("MATCH ()-[r:CALLS]->() RETURN count(r) as count")
        assert result[0]["count"] == 49


class TestGraphStorageClear:
    """Tests for clearing storage."""

    @pytest.mark.asyncio
    async def test_clear_removes_all_data(self):
        """clear should remove all nodes and relationships."""
        from repo_ctx.storage.graph import GraphStorage

        storage = GraphStorage(in_memory=True)

        # Add data
        nodes = [
            GraphNode(id="node_1", labels=["Node"], properties={}),
            GraphNode(id="node_2", labels=["Node"], properties={}),
        ]
        await storage.create_nodes(nodes)
        await storage.create_relationships([
            GraphRelationship(from_id="node_1", to_id="node_2", type="LINKS")
        ])

        # Clear
        await storage.clear()

        # Verify empty
        result = await storage.query("MATCH (n) RETURN count(n) as count")
        assert result[0]["count"] == 0
