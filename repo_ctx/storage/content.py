"""Content storage implementation using SQLite.

This module implements ContentStorageProtocol for storing:
- Libraries and versions
- Documents with quality scores and classifications
- Symbols with full metadata
- Chunks for GenAI processing
- Classification cache
"""

import json
import aiosqlite
from pathlib import Path
from typing import Any, Optional

from repo_ctx.models import Library, Version, Document
from repo_ctx.storage.protocols import ContentStorageProtocol


class ContentStorage:
    """SQLite-based content storage implementing ContentStorageProtocol.

    This is the enhanced v2 storage with support for:
    - Quality scores on documents
    - Classification caching
    - Chunks for GenAI processing
    - Full symbol metadata
    """

    def __init__(self, db_path: str):
        """Initialize content storage.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    async def init_db(self) -> None:
        """Initialize the database schema.

        Creates all tables, indexes, and triggers for the v2 schema.
        Safe to call multiple times (idempotent).
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Libraries table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS libraries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_name TEXT NOT NULL,
                    project_name TEXT NOT NULL,
                    description TEXT,
                    default_version TEXT,
                    provider TEXT DEFAULT 'github',
                    last_indexed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    settings JSON,
                    UNIQUE(group_name, project_name)
                )
            """)

            # Versions table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    library_id INTEGER NOT NULL,
                    version_tag TEXT NOT NULL,
                    commit_sha TEXT,
                    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(library_id, version_tag),
                    FOREIGN KEY (library_id) REFERENCES libraries(id) ON DELETE CASCADE
                )
            """)

            # Documents table (enhanced with quality_score and classification)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    content TEXT NOT NULL,
                    content_type TEXT DEFAULT 'markdown',
                    tokens INTEGER DEFAULT 0,
                    quality_score FLOAT DEFAULT 0.5,
                    classification TEXT,
                    metadata JSON,
                    UNIQUE(version_id, file_path),
                    FOREIGN KEY (version_id) REFERENCES versions(id) ON DELETE CASCADE
                )
            """)

            # Symbols table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS symbols (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    library_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    qualified_name TEXT,
                    symbol_type TEXT,
                    file_path TEXT,
                    line_start INTEGER,
                    line_end INTEGER,
                    signature TEXT,
                    visibility TEXT,
                    language TEXT,
                    documentation TEXT,
                    is_exported BOOLEAN,
                    metadata JSON,
                    UNIQUE(library_id, qualified_name),
                    FOREIGN KEY (library_id) REFERENCES libraries(id) ON DELETE CASCADE
                )
            """)

            # Dependencies table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    library_id INTEGER NOT NULL,
                    source_symbol_id INTEGER,
                    source_name TEXT,
                    target_name TEXT,
                    dependency_type TEXT,
                    file_path TEXT,
                    line INTEGER,
                    FOREIGN KEY (library_id) REFERENCES libraries(id) ON DELETE CASCADE,
                    FOREIGN KEY (source_symbol_id) REFERENCES symbols(id) ON DELETE SET NULL
                )
            """)

            # Chunks table (for GenAI processing)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER,
                    symbol_id INTEGER,
                    content TEXT NOT NULL,
                    chunk_type TEXT,
                    start_line INTEGER,
                    end_line INTEGER,
                    tokens INTEGER,
                    embedding_id TEXT,
                    metadata JSON,
                    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
                    FOREIGN KEY (symbol_id) REFERENCES symbols(id) ON DELETE CASCADE
                )
            """)

            # Classifications table (cache for LLM classifications)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS classifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_type TEXT NOT NULL,
                    entity_id INTEGER NOT NULL,
                    classification TEXT NOT NULL,
                    confidence FLOAT,
                    model TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(entity_type, entity_id)
                )
            """)

            # Create indexes
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_libraries_provider ON libraries(provider)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_libraries_search ON libraries(group_name, project_name)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_versions_library ON versions(library_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_documents_version ON documents(version_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_documents_quality ON documents(quality_score DESC)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_symbols_library ON symbols(library_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_symbols_type ON symbols(symbol_type)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_chunks_symbol ON chunks(symbol_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_classifications_entity ON classifications(entity_type, entity_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_dependencies_library ON dependencies(library_id)"
            )

            await db.commit()

    async def health_check(self) -> bool:
        """Check if the storage is healthy and connected.

        Returns:
            True if healthy, False otherwise.
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT 1")
                await cursor.fetchone()
                return True
        except Exception:
            return False

    # =========================================================================
    # Library Operations
    # =========================================================================

    async def save_library(self, library: Library) -> int:
        """Save or update a library.

        Args:
            library: Library to save.

        Returns:
            The library ID.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT OR REPLACE INTO libraries
                   (group_name, project_name, description, default_version, provider)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    library.group_name,
                    library.project_name,
                    library.description,
                    library.default_version,
                    library.provider,
                ),
            )
            await db.commit()
            return cursor.lastrowid

    async def get_library(self, library_id: str) -> Optional[Library]:
        """Get a library by its ID string.

        Args:
            library_id: Library identifier (e.g., "/owner/repo").

        Returns:
            Library if found, None otherwise.
        """
        # Parse library_id format: "/group/project"
        parts = library_id.strip("/").split("/")
        if len(parts) != 2:
            return None
        group, project = parts

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM libraries WHERE group_name = ? AND project_name = ?",
                (group, project),
            )
            row = await cursor.fetchone()
            if not row:
                return None

            return Library(
                id=row["id"],
                group_name=row["group_name"],
                project_name=row["project_name"],
                description=row["description"],
                default_version=row["default_version"],
                provider=row["provider"] if "provider" in row.keys() else "github",
                last_indexed=row["last_indexed"] if "last_indexed" in row.keys() else None,
            )

    async def get_all_libraries(self) -> list[Library]:
        """Get all indexed libraries.

        Returns:
            List of all libraries.
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM libraries ORDER BY last_indexed DESC"
            )
            rows = await cursor.fetchall()

            return [
                Library(
                    id=row["id"],
                    group_name=row["group_name"],
                    project_name=row["project_name"],
                    description=row["description"],
                    default_version=row["default_version"],
                    provider=row["provider"] if "provider" in row.keys() else "github",
                    last_indexed=row["last_indexed"] if "last_indexed" in row.keys() else None,
                )
                for row in rows
            ]

    async def delete_library(self, library_id: str) -> bool:
        """Delete a library and all its data.

        Args:
            library_id: Library identifier.

        Returns:
            True if deleted, False if not found.
        """
        parts = library_id.strip("/").split("/")
        if len(parts) != 2:
            return False
        group, project = parts

        async with aiosqlite.connect(self.db_path) as db:
            # Check if exists
            cursor = await db.execute(
                "SELECT id FROM libraries WHERE group_name = ? AND project_name = ?",
                (group, project),
            )
            row = await cursor.fetchone()
            if not row:
                return False

            # Delete (cascades to related tables)
            await db.execute(
                "DELETE FROM libraries WHERE group_name = ? AND project_name = ?",
                (group, project),
            )
            await db.commit()
            return True

    # =========================================================================
    # Version Operations
    # =========================================================================

    async def save_version(self, version: Version) -> int:
        """Save a version.

        Args:
            version: Version to save.

        Returns:
            The version ID.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT OR REPLACE INTO versions (library_id, version_tag, commit_sha)
                   VALUES (?, ?, ?)""",
                (version.library_id, version.version_tag, version.commit_sha),
            )
            await db.commit()
            return cursor.lastrowid

    async def get_version_id(self, library_id: int, version_tag: str) -> Optional[int]:
        """Get version ID by library and tag.

        Args:
            library_id: Library database ID.
            version_tag: Version tag string.

        Returns:
            Version ID if found.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT id FROM versions WHERE library_id = ? AND version_tag = ?",
                (library_id, version_tag),
            )
            row = await cursor.fetchone()
            return row[0] if row else None

    # =========================================================================
    # Document Operations
    # =========================================================================

    async def save_documents(self, documents: list[Document]) -> None:
        """Save multiple documents.

        Args:
            documents: List of documents to save.
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.executemany(
                """INSERT OR REPLACE INTO documents
                   (version_id, file_path, content, content_type, tokens)
                   VALUES (?, ?, ?, ?, ?)""",
                [
                    (
                        doc.version_id,
                        doc.file_path,
                        doc.content,
                        doc.content_type,
                        doc.tokens,
                    )
                    for doc in documents
                ],
            )
            await db.commit()

    async def get_documents(
        self,
        version_id: int,
        topic: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> list[Document]:
        """Get documents for a version.

        Args:
            version_id: Version ID to get documents for.
            topic: Optional topic filter.
            page: Page number (1-indexed).
            page_size: Number of documents per page.

        Returns:
            List of documents.
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            if topic:
                cursor = await db.execute(
                    """SELECT * FROM documents
                       WHERE version_id = ? AND (file_path LIKE ? OR content LIKE ?)
                       ORDER BY file_path
                       LIMIT ? OFFSET ?""",
                    (version_id, f"%{topic}%", f"%{topic}%", page_size, (page - 1) * page_size),
                )
            else:
                cursor = await db.execute(
                    """SELECT * FROM documents
                       WHERE version_id = ?
                       ORDER BY file_path
                       LIMIT ? OFFSET ?""",
                    (version_id, page_size, (page - 1) * page_size),
                )

            rows = await cursor.fetchall()
            return [
                Document(
                    id=row["id"],
                    version_id=row["version_id"],
                    file_path=row["file_path"],
                    content=row["content"],
                    content_type=row["content_type"],
                    tokens=row["tokens"],
                )
                for row in rows
            ]

    # =========================================================================
    # Symbol Operations
    # =========================================================================

    async def save_symbols(self, symbols: list[Any], repository_id: int) -> None:
        """Save multiple symbols.

        Args:
            symbols: List of Symbol objects.
            repository_id: Repository/library ID.
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.executemany(
                """INSERT OR REPLACE INTO symbols (
                    library_id, name, qualified_name, symbol_type, file_path,
                    line_start, line_end, signature, visibility, language,
                    documentation, is_exported, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    (
                        repository_id,
                        s.name,
                        s.qualified_name,
                        s.symbol_type.value if hasattr(s.symbol_type, "value") else str(s.symbol_type),
                        s.file_path,
                        s.line_start,
                        s.line_end,
                        getattr(s, "signature", None),
                        getattr(s, "visibility", None),
                        getattr(s, "language", None),
                        getattr(s, "documentation", None),
                        getattr(s, "is_exported", None),
                        json.dumps(getattr(s, "metadata", {})) if hasattr(s, "metadata") else "{}",
                    )
                    for s in symbols
                ],
            )
            await db.commit()

    async def search_symbols(
        self,
        repository_id: int,
        query: str,
        symbol_type: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Search symbols by query.

        Args:
            repository_id: Repository/library ID.
            query: Search query.
            symbol_type: Optional filter by type.
            language: Optional filter by language.
            limit: Maximum results.

        Returns:
            List of matching symbols as dictionaries.
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            conditions = ["library_id = ?"]
            params: list[Any] = [repository_id]

            if query:
                conditions.append("(name LIKE ? OR qualified_name LIKE ? OR documentation LIKE ?)")
                params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])

            if symbol_type:
                conditions.append("symbol_type = ?")
                params.append(symbol_type)

            if language:
                conditions.append("language = ?")
                params.append(language)

            params.append(limit)

            sql = f"""
                SELECT * FROM symbols
                WHERE {' AND '.join(conditions)}
                ORDER BY name
                LIMIT ?
            """

            cursor = await db.execute(sql, params)
            rows = await cursor.fetchall()

            return [dict(row) for row in rows]

    async def get_symbol_by_name(
        self, repository_id: int, qualified_name: str
    ) -> Optional[dict[str, Any]]:
        """Get a symbol by its qualified name.

        Args:
            repository_id: Repository/library ID.
            qualified_name: Full qualified name.

        Returns:
            Symbol as dictionary if found.
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM symbols WHERE library_id = ? AND qualified_name = ?",
                (repository_id, qualified_name),
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    # =========================================================================
    # Chunk Operations
    # =========================================================================

    async def save_chunk(
        self,
        document_id: Optional[int] = None,
        symbol_id: Optional[int] = None,
        content: str = "",
        chunk_type: Optional[str] = None,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
        tokens: Optional[int] = None,
        embedding_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> int:
        """Save a content chunk.

        Args:
            document_id: Source document ID (optional).
            symbol_id: Source symbol ID (optional).
            content: Chunk content.
            chunk_type: Type of chunk (code, documentation, mixed).
            start_line: Starting line number.
            end_line: Ending line number.
            tokens: Token count.
            embedding_id: Reference to vector DB embedding.
            metadata: Additional metadata.

        Returns:
            Chunk ID.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO chunks
                   (document_id, symbol_id, content, chunk_type, start_line,
                    end_line, tokens, embedding_id, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    document_id,
                    symbol_id,
                    content,
                    chunk_type,
                    start_line,
                    end_line,
                    tokens,
                    embedding_id,
                    json.dumps(metadata) if metadata else None,
                ),
            )
            await db.commit()
            return cursor.lastrowid

    async def get_chunks_by_document(self, document_id: int) -> list[dict[str, Any]]:
        """Get chunks for a document.

        Args:
            document_id: Document ID.

        Returns:
            List of chunks.
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM chunks WHERE document_id = ? ORDER BY start_line",
                (document_id,),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # =========================================================================
    # Classification Operations
    # =========================================================================

    async def save_classification(
        self,
        entity_type: str,
        entity_id: int,
        classification: str,
        confidence: Optional[float] = None,
        model: Optional[str] = None,
    ) -> None:
        """Save a classification.

        Args:
            entity_type: Type of entity (document, symbol, chunk).
            entity_id: Entity ID.
            classification: Classification label.
            confidence: Confidence score (0.0-1.0).
            model: Model used for classification.
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT OR REPLACE INTO classifications
                   (entity_type, entity_id, classification, confidence, model)
                   VALUES (?, ?, ?, ?, ?)""",
                (entity_type, entity_id, classification, confidence, model),
            )
            await db.commit()

    async def get_classification(
        self, entity_type: str, entity_id: int
    ) -> Optional[dict[str, Any]]:
        """Get classification for an entity.

        Args:
            entity_type: Type of entity.
            entity_id: Entity ID.

        Returns:
            Classification as dictionary if found.
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM classifications WHERE entity_type = ? AND entity_id = ?",
                (entity_type, entity_id),
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
