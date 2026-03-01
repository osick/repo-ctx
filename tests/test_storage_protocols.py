"""Tests for storage protocol definitions.

Tests the abstract storage protocols that define the interfaces
for Content (SQLite), Vector (Qdrant), and Graph (Neo4j) storage.
Following TDD Chicago School - write tests first, then implement.
"""

import pytest
from typing import Protocol, runtime_checkable


class TestStorageProtocolsExist:
    """Test that storage protocol classes exist and are properly defined."""

    def test_content_storage_protocol_exists(self):
        """ContentStorageProtocol should exist and be a Protocol."""
        from repo_ctx.storage.protocols import ContentStorageProtocol

        assert hasattr(ContentStorageProtocol, "__protocol_attrs__") or issubclass(
            ContentStorageProtocol, Protocol
        )

    def test_vector_storage_protocol_exists(self):
        """VectorStorageProtocol should exist and be a Protocol."""
        from repo_ctx.storage.protocols import VectorStorageProtocol

        assert hasattr(VectorStorageProtocol, "__protocol_attrs__") or issubclass(
            VectorStorageProtocol, Protocol
        )

    def test_graph_storage_protocol_exists(self):
        """GraphStorageProtocol should exist and be a Protocol."""
        from repo_ctx.storage.protocols import GraphStorageProtocol

        assert hasattr(GraphStorageProtocol, "__protocol_attrs__") or issubclass(
            GraphStorageProtocol, Protocol
        )


class TestContentStorageProtocolMethods:
    """Test ContentStorageProtocol method signatures."""

    def test_has_init_db_method(self):
        """ContentStorageProtocol should have init_db method."""
        from repo_ctx.storage.protocols import ContentStorageProtocol
        import inspect

        assert hasattr(ContentStorageProtocol, "init_db")
        sig = inspect.signature(ContentStorageProtocol.init_db)
        # Should be async (returns coroutine)
        assert "self" in str(sig)

    def test_has_save_library_method(self):
        """ContentStorageProtocol should have save_library method."""
        from repo_ctx.storage.protocols import ContentStorageProtocol

        assert hasattr(ContentStorageProtocol, "save_library")

    def test_has_get_library_method(self):
        """ContentStorageProtocol should have get_library method."""
        from repo_ctx.storage.protocols import ContentStorageProtocol

        assert hasattr(ContentStorageProtocol, "get_library")

    def test_has_save_documents_method(self):
        """ContentStorageProtocol should have save_documents method."""
        from repo_ctx.storage.protocols import ContentStorageProtocol

        assert hasattr(ContentStorageProtocol, "save_documents")

    def test_has_get_documents_method(self):
        """ContentStorageProtocol should have get_documents method."""
        from repo_ctx.storage.protocols import ContentStorageProtocol

        assert hasattr(ContentStorageProtocol, "get_documents")

    def test_has_save_symbols_method(self):
        """ContentStorageProtocol should have save_symbols method."""
        from repo_ctx.storage.protocols import ContentStorageProtocol

        assert hasattr(ContentStorageProtocol, "save_symbols")

    def test_has_search_symbols_method(self):
        """ContentStorageProtocol should have search_symbols method."""
        from repo_ctx.storage.protocols import ContentStorageProtocol

        assert hasattr(ContentStorageProtocol, "search_symbols")

    def test_has_health_check_method(self):
        """ContentStorageProtocol should have health_check method."""
        from repo_ctx.storage.protocols import ContentStorageProtocol

        assert hasattr(ContentStorageProtocol, "health_check")


class TestVectorStorageProtocolMethods:
    """Test VectorStorageProtocol method signatures."""

    def test_has_upsert_embeddings_method(self):
        """VectorStorageProtocol should have upsert_embeddings method."""
        from repo_ctx.storage.protocols import VectorStorageProtocol

        assert hasattr(VectorStorageProtocol, "upsert_embeddings")

    def test_has_search_similar_method(self):
        """VectorStorageProtocol should have search_similar method."""
        from repo_ctx.storage.protocols import VectorStorageProtocol

        assert hasattr(VectorStorageProtocol, "search_similar")

    def test_has_delete_by_library_method(self):
        """VectorStorageProtocol should have delete_by_library method."""
        from repo_ctx.storage.protocols import VectorStorageProtocol

        assert hasattr(VectorStorageProtocol, "delete_by_library")

    def test_has_health_check_method(self):
        """VectorStorageProtocol should have health_check method."""
        from repo_ctx.storage.protocols import VectorStorageProtocol

        assert hasattr(VectorStorageProtocol, "health_check")

    def test_has_create_collection_method(self):
        """VectorStorageProtocol should have create_collection method."""
        from repo_ctx.storage.protocols import VectorStorageProtocol

        assert hasattr(VectorStorageProtocol, "create_collection")


class TestGraphStorageProtocolMethods:
    """Test GraphStorageProtocol method signatures."""

    def test_has_create_nodes_method(self):
        """GraphStorageProtocol should have create_nodes method."""
        from repo_ctx.storage.protocols import GraphStorageProtocol

        assert hasattr(GraphStorageProtocol, "create_nodes")

    def test_has_create_relationships_method(self):
        """GraphStorageProtocol should have create_relationships method."""
        from repo_ctx.storage.protocols import GraphStorageProtocol

        assert hasattr(GraphStorageProtocol, "create_relationships")

    def test_has_query_method(self):
        """GraphStorageProtocol should have query method."""
        from repo_ctx.storage.protocols import GraphStorageProtocol

        assert hasattr(GraphStorageProtocol, "query")

    def test_has_get_call_graph_method(self):
        """GraphStorageProtocol should have get_call_graph method."""
        from repo_ctx.storage.protocols import GraphStorageProtocol

        assert hasattr(GraphStorageProtocol, "get_call_graph")

    def test_has_delete_by_library_method(self):
        """GraphStorageProtocol should have delete_by_library method."""
        from repo_ctx.storage.protocols import GraphStorageProtocol

        assert hasattr(GraphStorageProtocol, "delete_by_library")

    def test_has_health_check_method(self):
        """GraphStorageProtocol should have health_check method."""
        from repo_ctx.storage.protocols import GraphStorageProtocol

        assert hasattr(GraphStorageProtocol, "health_check")


class TestDataTransferObjects:
    """Test data transfer objects for storage operations."""

    def test_embedding_dto_exists(self):
        """Embedding DTO should exist."""
        from repo_ctx.storage.protocols import Embedding

        embedding = Embedding(
            id="emb_123",
            vector=[0.1, 0.2, 0.3],
            payload={"library_id": "test", "chunk_type": "code"},
        )
        assert embedding.id == "emb_123"
        assert embedding.vector == [0.1, 0.2, 0.3]
        assert embedding.payload["library_id"] == "test"

    def test_similarity_result_dto_exists(self):
        """SimilarityResult DTO should exist."""
        from repo_ctx.storage.protocols import SimilarityResult

        result = SimilarityResult(
            id="emb_123", score=0.95, payload={"file_path": "src/main.py"}
        )
        assert result.id == "emb_123"
        assert result.score == 0.95
        assert result.payload["file_path"] == "src/main.py"

    def test_graph_node_dto_exists(self):
        """GraphNode DTO should exist."""
        from repo_ctx.storage.protocols import GraphNode

        node = GraphNode(
            id="node_123",
            labels=["Symbol", "Function"],
            properties={"name": "main", "qualified_name": "src.main"},
        )
        assert node.id == "node_123"
        assert "Symbol" in node.labels
        assert node.properties["name"] == "main"

    def test_graph_relationship_dto_exists(self):
        """GraphRelationship DTO should exist."""
        from repo_ctx.storage.protocols import GraphRelationship

        rel = GraphRelationship(
            from_id="node_1",
            to_id="node_2",
            type="CALLS",
            properties={"line": 42},
        )
        assert rel.from_id == "node_1"
        assert rel.to_id == "node_2"
        assert rel.type == "CALLS"
        assert rel.properties["line"] == 42

    def test_graph_result_dto_exists(self):
        """GraphResult DTO should exist for query results."""
        from repo_ctx.storage.protocols import GraphResult, GraphNode, GraphRelationship

        node1 = GraphNode(id="n1", labels=["Symbol"], properties={"name": "func1"})
        node2 = GraphNode(id="n2", labels=["Symbol"], properties={"name": "func2"})
        rel = GraphRelationship(from_id="n1", to_id="n2", type="CALLS", properties={})

        result = GraphResult(nodes=[node1, node2], relationships=[rel])
        assert len(result.nodes) == 2
        assert len(result.relationships) == 1


class TestProtocolRuntimeCheckable:
    """Test that protocols are runtime checkable where needed."""

    def test_content_storage_protocol_is_runtime_checkable(self):
        """ContentStorageProtocol should be runtime checkable."""
        from repo_ctx.storage.protocols import ContentStorageProtocol

        # Should have _is_runtime_protocol attribute
        assert getattr(ContentStorageProtocol, "_is_runtime_protocol", False)

    def test_vector_storage_protocol_is_runtime_checkable(self):
        """VectorStorageProtocol should be runtime checkable."""
        from repo_ctx.storage.protocols import VectorStorageProtocol

        assert getattr(VectorStorageProtocol, "_is_runtime_protocol", False)

    def test_graph_storage_protocol_is_runtime_checkable(self):
        """GraphStorageProtocol should be runtime checkable."""
        from repo_ctx.storage.protocols import GraphStorageProtocol

        assert getattr(GraphStorageProtocol, "_is_runtime_protocol", False)


class TestStorageModuleExports:
    """Test that storage module exports all necessary items."""

    def test_protocols_module_exports(self):
        """Protocols module should export all protocols and DTOs."""
        from repo_ctx.storage import protocols

        # Protocols
        assert hasattr(protocols, "ContentStorageProtocol")
        assert hasattr(protocols, "VectorStorageProtocol")
        assert hasattr(protocols, "GraphStorageProtocol")

        # DTOs
        assert hasattr(protocols, "Embedding")
        assert hasattr(protocols, "SimilarityResult")
        assert hasattr(protocols, "GraphNode")
        assert hasattr(protocols, "GraphRelationship")
        assert hasattr(protocols, "GraphResult")

    def test_storage_package_init(self):
        """Storage package __init__ should export key items."""
        from repo_ctx import storage

        assert hasattr(storage, "ContentStorageProtocol")
        assert hasattr(storage, "VectorStorageProtocol")
        assert hasattr(storage, "GraphStorageProtocol")
