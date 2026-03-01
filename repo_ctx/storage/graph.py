"""Graph storage implementation using Neo4j.

This module implements GraphStorageProtocol for storing and querying
code relationships and semantic graphs.

For testing, an in-memory mode using NetworkX is provided.
"""

from typing import Any, Optional
import re

from repo_ctx.storage.protocols import (
    GraphNode,
    GraphRelationship,
    GraphResult,
)
from repo_ctx.exceptions import StorageError


class GraphStorage:
    """Neo4j-based graph storage implementing GraphStorageProtocol.

    This storage provides graph database capabilities for storing
    code relationships. It supports:
    - Nodes with multiple labels and properties
    - Typed relationships with properties
    - Cypher query execution
    - Call graph traversal

    For testing, use in_memory=True to use a NetworkX-based backend.
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: Optional[str] = None,
        database: str = "neo4j",
        in_memory: bool = False,
    ):
        """Initialize graph storage.

        Args:
            uri: Neo4j connection URI.
            username: Neo4j username.
            password: Neo4j password.
            database: Database name.
            in_memory: Use in-memory NetworkX backend for testing.
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self.in_memory = in_memory

        if in_memory:
            # Use NetworkX for in-memory testing
            import networkx as nx
            self._graph = nx.DiGraph()
            self._driver = None
        else:
            # Use Neo4j driver for real connections
            try:
                from neo4j import GraphDatabase
                self._driver = GraphDatabase.driver(
                    uri,
                    auth=(username, password) if password else None,
                )
                self._graph = None
            except Exception as e:
                raise StorageError(
                    f"Failed to connect to Neo4j: {e}",
                    storage_type="neo4j",
                )

    async def health_check(self) -> bool:
        """Check if the storage is healthy and connected.

        Returns:
            True if healthy, False otherwise.
        """
        if self.in_memory:
            return True

        try:
            with self._driver.session(database=self.database) as session:
                session.run("RETURN 1")
            return True
        except Exception:
            return False

    async def create_nodes(self, nodes: list[GraphNode]) -> None:
        """Create multiple nodes.

        Args:
            nodes: List of nodes to create.
        """
        if not nodes:
            return

        if self.in_memory:
            for node in nodes:
                # Store node with all its properties
                self._graph.add_node(
                    node.id,
                    labels=node.labels,
                    **node.properties,
                )
        else:
            with self._driver.session(database=self.database) as session:
                for node in nodes:
                    labels_str = ":".join(node.labels) if node.labels else "Node"
                    props = {"id": node.id, **node.properties}
                    props_str = ", ".join(f"{k}: ${k}" for k in props.keys())
                    query = f"MERGE (n:{labels_str} {{{props_str}}})"
                    session.run(query, props)

    async def create_relationships(
        self, relationships: list[GraphRelationship]
    ) -> None:
        """Create multiple relationships.

        Args:
            relationships: List of relationships to create.
        """
        if not relationships:
            return

        if self.in_memory:
            for rel in relationships:
                # Only create if both nodes exist
                if rel.from_id in self._graph and rel.to_id in self._graph:
                    self._graph.add_edge(
                        rel.from_id,
                        rel.to_id,
                        type=rel.type,
                        **rel.properties,
                    )
        else:
            with self._driver.session(database=self.database) as session:
                for rel in relationships:
                    props_items = list(rel.properties.items())
                    props_str = ", ".join(f"{k}: ${k}" for k, _ in props_items)
                    props_clause = f" {{{props_str}}}" if props_str else ""
                    query = f"""
                        MATCH (a {{id: $from_id}})
                        MATCH (b {{id: $to_id}})
                        MERGE (a)-[r:{rel.type}{props_clause}]->(b)
                    """
                    params = {
                        "from_id": rel.from_id,
                        "to_id": rel.to_id,
                        **rel.properties,
                    }
                    session.run(query, params)

    async def query(
        self,
        cypher: str,
        params: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query.

        Args:
            cypher: Cypher query string.
            params: Query parameters.

        Returns:
            List of result records as dictionaries.
        """
        params = params or {}

        if self.in_memory:
            return self._execute_in_memory_query(cypher, params)
        else:
            try:
                with self._driver.session(database=self.database) as session:
                    result = session.run(cypher, params)
                    return [dict(record) for record in result]
            except Exception as e:
                raise StorageError(
                    f"Query failed: {e}",
                    storage_type="neo4j",
                )

    def _execute_in_memory_query(
        self, cypher: str, params: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Execute a Cypher-like query on the in-memory graph.

        This is a simplified parser that handles common query patterns.
        """
        cypher_upper = cypher.upper()

        # Handle MATCH (n) RETURN count(n) as count
        if "COUNT" in cypher_upper and "MATCH (N)" in cypher_upper and ":" not in cypher.split("RETURN")[0]:
            return [{"count": len(self._graph.nodes)}]

        # Handle MATCH (n:Label) RETURN count(n) as count
        label_count_match = re.search(r"MATCH\s*\(n:(\w+)\)\s*RETURN\s*count\(n\)", cypher, re.IGNORECASE)
        if label_count_match:
            required_label = label_count_match.group(1)
            count = sum(
                1 for _, data in self._graph.nodes(data=True)
                if required_label in data.get("labels", [])
            )
            return [{"count": count}]

        # Handle MATCH ()-[r]->() RETURN count(r) as count
        if "COUNT(R)" in cypher_upper:
            return [{"count": len(self._graph.edges)}]

        # Handle specific relationship type count
        rel_type_match = re.search(r"\[r:(\w+)\]", cypher)
        if rel_type_match and "COUNT" in cypher_upper:
            rel_type = rel_type_match.group(1)
            count = sum(
                1 for _, _, d in self._graph.edges(data=True)
                if d.get("type") == rel_type
            )
            return [{"count": count}]

        # Handle MATCH (n) RETURN n.id as id, labels(n) as labels
        if "LABELS(N)" in cypher_upper:
            results = []
            for node_id, data in self._graph.nodes(data=True):
                results.append({
                    "id": node_id,
                    "labels": data.get("labels", []),
                })
            return results

        # Handle MATCH (n) RETURN n.id as id
        if "RETURN N.ID" in cypher_upper and "MATCH (N)" in cypher_upper:
            results = []
            for node_id, data in self._graph.nodes(data=True):
                # Apply label filter if present
                label_match = re.search(r":(\w+)", cypher)
                if label_match:
                    required_label = label_match.group(1)
                    node_labels = data.get("labels", [])
                    if required_label not in node_labels:
                        continue
                results.append({"id": node_id})
            return results

        # Handle MATCH (n:Label {property: $param}) RETURN n
        # Negative lookahead to avoid matching "RETURN n.id" patterns
        node_query_match = re.search(
            r"MATCH\s*\(n(?::[\w:]+)?\s*(?:\{([^}]+)\})?\)\s*RETURN\s*n(?![.\w])",
            cypher,
            re.IGNORECASE,
        )
        if node_query_match:
            results = []
            props_str = node_query_match.group(1)
            required_props = {}

            if props_str:
                for prop in props_str.split(","):
                    prop = prop.strip()
                    if ":" in prop:
                        key, value = prop.split(":", 1)
                        key = key.strip()
                        value = value.strip()
                        # Handle parameter reference
                        if value.startswith("$"):
                            param_name = value[1:]
                            required_props[key] = params.get(param_name)
                        else:
                            required_props[key] = value.strip("'\"")

            for node_id, data in self._graph.nodes(data=True):
                # Check label requirements
                label_matches = re.findall(r":(\w+)", cypher.split("{")[0] if "{" in cypher else cypher)
                if label_matches:
                    node_labels = data.get("labels", [])
                    if not all(label in node_labels for label in label_matches):
                        continue

                # Check property requirements
                match = True
                for key, expected_value in required_props.items():
                    if data.get(key) != expected_value and node_id != expected_value:
                        if key == "id" and node_id == expected_value:
                            continue
                        match = False
                        break

                if match:
                    # Return node as dict
                    node_dict = {"id": node_id, **data}
                    results.append({"n": node_dict})

            return results

        # Handle MATCH (a)-[r:TYPE]->(b) RETURN ...
        rel_query_match = re.search(
            r"MATCH\s*\((\w+)\)-\[r:(\w+)\]->\((\w+)\)",
            cypher,
            re.IGNORECASE,
        )
        if rel_query_match:
            results = []
            rel_type = rel_query_match.group(2)

            for u, v, data in self._graph.edges(data=True):
                if data.get("type") == rel_type:
                    _u_data = self._graph.nodes[u]
                    _v_data = self._graph.nodes[v]
                    result = {
                        "from": u,
                        "to": v,
                        "type": data.get("type"),
                    }
                    # Add relationship properties if requested
                    for key, value in data.items():
                        if key != "type":
                            result[key] = value
                    results.append(result)

            return results

        # Handle relationship property queries
        rel_props_match = re.search(
            r"MATCH\s*\(\)-\[r:(\w+)\]->\(\)\s*RETURN\s+(.+)",
            cypher,
            re.IGNORECASE,
        )
        if rel_props_match:
            rel_type = rel_props_match.group(1)
            return_clause = rel_props_match.group(2)

            results = []
            for u, v, data in self._graph.edges(data=True):
                if data.get("type") == rel_type:
                    result = {}
                    # Parse return clause for properties
                    for part in return_clause.split(","):
                        part = part.strip()
                        if " as " in part.lower():
                            expr, alias = re.split(r"\s+as\s+", part, flags=re.IGNORECASE)
                            prop_match = re.search(r"r\.(\w+)", expr)
                            if prop_match:
                                prop_name = prop_match.group(1)
                                result[alias.strip()] = data.get(prop_name)
                    results.append(result)

            return results

        # Handle MATCH (n:Label {language: $lang}) RETURN n.id as id
        prop_filter_match = re.search(
            r"MATCH\s*\(n:(\w+)\s*\{(\w+):\s*\$(\w+)\}\)",
            cypher,
            re.IGNORECASE,
        )
        if prop_filter_match:
            label = prop_filter_match.group(1)
            prop_name = prop_filter_match.group(2)
            param_name = prop_filter_match.group(3)
            expected_value = params.get(param_name)

            results = []
            for node_id, data in self._graph.nodes(data=True):
                node_labels = data.get("labels", [])
                if label in node_labels and data.get(prop_name) == expected_value:
                    results.append({"id": node_id})

            return results

        # Handle MATCH (n:Symbol:Class:PublicAPI) multi-label query with RETURN n.id as id
        multi_label_match = re.search(r"MATCH\s*\(n((?::\w+)+)\)\s*RETURN\s+n\.id\s+as\s+id", cypher, re.IGNORECASE)
        if multi_label_match:
            labels_str = multi_label_match.group(1)
            required_labels = [lbl for lbl in labels_str.split(":") if lbl]
            results = []
            for node_id, data in self._graph.nodes(data=True):
                node_labels = data.get("labels", [])
                if all(label in node_labels for label in required_labels):
                    results.append({"id": node_id})
            return results

        # Handle MATCH (n:Label {prop: $param}) RETURN n.id as id
        param_filter_return_id = re.search(
            r"MATCH\s*\(n:(\w+)\s*\{(\w+):\s*\$(\w+)\}\)\s*RETURN\s+n\.id\s+as\s+id",
            cypher,
            re.IGNORECASE,
        )
        if param_filter_return_id:
            label = param_filter_return_id.group(1)
            prop_name = param_filter_return_id.group(2)
            param_name = param_filter_return_id.group(3)
            expected_value = params.get(param_name)

            results = []
            for node_id, data in self._graph.nodes(data=True):
                node_labels = data.get("labels", [])
                if label in node_labels and data.get(prop_name) == expected_value:
                    results.append({"id": node_id})

            return results

        # Invalid query
        raise StorageError(
            f"Unsupported in-memory query: {cypher}",
            storage_type="neo4j",
        )

    async def get_call_graph(
        self,
        symbol_name: str,
        depth: int = 2,
        direction: str = "both",
    ) -> GraphResult:
        """Get the call graph for a symbol.

        Args:
            symbol_name: Name or qualified name of the symbol.
            depth: Maximum traversal depth.
            direction: "incoming", "outgoing", or "both".

        Returns:
            Graph result with nodes and relationships.
        """
        if self.in_memory:
            return self._get_call_graph_in_memory(symbol_name, depth, direction)

        # Build Cypher query based on direction
        if direction == "outgoing":
            pattern = f"(start)-[*1..{depth}]->(related)"
        elif direction == "incoming":
            pattern = f"(related)-[*1..{depth}]->(start)"
        else:  # both
            pattern = f"(start)-[*1..{depth}]-(related)"

        query = f"""
            MATCH (start {{name: $name}})
            OPTIONAL MATCH {pattern}
            RETURN start, collect(DISTINCT related) as related_nodes,
                   [(start)-[r]-(related) | r] as relationships
        """

        try:
            results = await self.query(query, {"name": symbol_name})
            if not results or not results[0].get("start"):
                return GraphResult(nodes=[], relationships=[])

            nodes = []
            relationships = []

            # Convert Neo4j nodes to GraphNode
            for record in results:
                if record.get("start"):
                    start_node = record["start"]
                    nodes.append(GraphNode(
                        id=start_node.get("id", str(start_node.id)),
                        labels=list(start_node.labels),
                        properties=dict(start_node),
                    ))

                for rel_node in record.get("related_nodes", []):
                    if rel_node:
                        nodes.append(GraphNode(
                            id=rel_node.get("id", str(rel_node.id)),
                            labels=list(rel_node.labels),
                            properties=dict(rel_node),
                        ))

            return GraphResult(nodes=nodes, relationships=relationships)

        except Exception:
            return GraphResult(nodes=[], relationships=[])

    def _get_call_graph_in_memory(
        self, symbol_name: str, depth: int, direction: str
    ) -> GraphResult:
        """Get call graph from in-memory NetworkX graph."""

        # Find the start node
        start_node = None
        for node_id, data in self._graph.nodes(data=True):
            if node_id == symbol_name or data.get("name") == symbol_name:
                start_node = node_id
                break

        if start_node is None:
            return GraphResult(nodes=[], relationships=[])

        # Collect nodes and relationships
        visited_nodes = set()
        collected_rels = []

        def traverse(node: str, current_depth: int):
            if current_depth > depth or node in visited_nodes:
                return
            visited_nodes.add(node)

            if direction in ("outgoing", "both"):
                for successor in self._graph.successors(node):
                    edge_data = self._graph.edges[node, successor]
                    collected_rels.append((node, successor, edge_data))
                    traverse(successor, current_depth + 1)

            if direction in ("incoming", "both"):
                for predecessor in self._graph.predecessors(node):
                    edge_data = self._graph.edges[predecessor, node]
                    collected_rels.append((predecessor, node, edge_data))
                    traverse(predecessor, current_depth + 1)

        traverse(start_node, 0)

        # Build result
        nodes = []
        for node_id in visited_nodes:
            data = self._graph.nodes[node_id]
            nodes.append(GraphNode(
                id=node_id,
                labels=data.get("labels", []),
                properties={k: v for k, v in data.items() if k != "labels"},
            ))

        relationships = []
        seen_rels = set()
        for from_id, to_id, data in collected_rels:
            rel_key = (from_id, to_id, data.get("type"))
            if rel_key not in seen_rels:
                seen_rels.add(rel_key)
                relationships.append(GraphRelationship(
                    from_id=from_id,
                    to_id=to_id,
                    type=data.get("type", "RELATED"),
                    properties={k: v for k, v in data.items() if k != "type"},
                ))

        return GraphResult(nodes=nodes, relationships=relationships)

    async def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a specific node by ID.

        Args:
            node_id: Node identifier.

        Returns:
            Node if found.
        """
        if self.in_memory:
            if node_id in self._graph:
                data = self._graph.nodes[node_id]
                return GraphNode(
                    id=node_id,
                    labels=data.get("labels", []),
                    properties={k: v for k, v in data.items() if k != "labels"},
                )
            return None
        else:
            query = "MATCH (n {id: $id}) RETURN n, labels(n) as labels"
            results = await self.query(query, {"id": node_id})
            if not results:
                return None
            record = results[0]
            node_data = dict(record["n"])
            return GraphNode(
                id=node_id,
                labels=record.get("labels", []),
                properties=node_data,
            )

    async def find_nodes_by_label(
        self,
        label: str,
        properties: Optional[dict[str, Any]] = None,
        limit: int = 100,
    ) -> list[GraphNode]:
        """Find nodes by label and optional properties.

        Args:
            label: Node label to search.
            properties: Optional property filters.
            limit: Maximum results.

        Returns:
            List of matching nodes.
        """
        properties = properties or {}

        if self.in_memory:
            results = []
            for node_id, data in self._graph.nodes(data=True):
                node_labels = data.get("labels", [])
                if label not in node_labels:
                    continue

                # Check property filters
                match = True
                for key, value in properties.items():
                    if data.get(key) != value:
                        match = False
                        break

                if match:
                    results.append(GraphNode(
                        id=node_id,
                        labels=node_labels,
                        properties={k: v for k, v in data.items() if k != "labels"},
                    ))

                if len(results) >= limit:
                    break

            return results
        else:
            props_str = ""
            if properties:
                props_str = " {" + ", ".join(f"{k}: ${k}" for k in properties.keys()) + "}"
            query = f"MATCH (n:{label}{props_str}) RETURN n, labels(n) as labels LIMIT $limit"
            params = {**properties, "limit": limit}

            results = await self.query(query, params)
            return [
                GraphNode(
                    id=record["n"].get("id"),
                    labels=record.get("labels", []),
                    properties=dict(record["n"]),
                )
                for record in results
            ]

    async def delete_by_library(self, library_id: str) -> int:
        """Delete all nodes and relationships for a library.

        Args:
            library_id: Library identifier.

        Returns:
            Number of deleted nodes.
        """
        if self.in_memory:
            nodes_to_delete = [
                node_id for node_id, data in self._graph.nodes(data=True)
                if data.get("library_id") == library_id
            ]
            for node_id in nodes_to_delete:
                self._graph.remove_node(node_id)
            return len(nodes_to_delete)
        else:
            query = """
                MATCH (n {library_id: $library_id})
                DETACH DELETE n
                RETURN count(n) as count
            """
            try:
                results = await self.query(query, {"library_id": library_id})
                return results[0].get("count", 0) if results else 0
            except Exception:
                return 0

    async def clear(self) -> None:
        """Clear all data from the storage."""
        if self.in_memory:
            self._graph.clear()
        else:
            await self.query("MATCH (n) DETACH DELETE n")
