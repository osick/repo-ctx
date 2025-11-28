"""Storage layer using SQLite."""
import aiosqlite
from pathlib import Path
from typing import Optional
from .models import Library, Version, Document, SearchResult, FuzzySearchResult


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


class Storage:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    async def init_db(self):
        """Initialize database schema."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS libraries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_name TEXT NOT NULL,
                    project_name TEXT NOT NULL,
                    description TEXT,
                    default_version TEXT,
                    provider TEXT DEFAULT 'github',
                    last_indexed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(group_name, project_name)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    library_id INTEGER NOT NULL,
                    version_tag TEXT NOT NULL,
                    commit_sha TEXT,
                    UNIQUE(library_id, version_tag),
                    FOREIGN KEY (library_id) REFERENCES libraries(id)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    content TEXT NOT NULL,
                    content_type TEXT DEFAULT 'markdown',
                    tokens INTEGER DEFAULT 0,
                    UNIQUE(version_id, file_path),
                    FOREIGN KEY (version_id) REFERENCES versions(id)
                )
            """)
            await db.execute("CREATE INDEX IF NOT EXISTS idx_libraries_search ON libraries(group_name, project_name)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_documents_version ON documents(version_id)")

            # Run migrations
            await self._run_migrations(db)

            await db.commit()

    async def _run_migrations(self, db):
        """Run all pending migrations."""
        from pathlib import Path
        migrations_dir = Path(__file__).parent / "migrations"

        if not migrations_dir.exists():
            return

        # Run migrations in order
        migration_files = sorted(migrations_dir.glob("*.sql"))
        for migration_path in migration_files:
            try:
                migration_sql = migration_path.read_text()
                await db.executescript(migration_sql)
            except Exception:
                # Migration may have already been applied (e.g., column exists)
                pass
    
    async def save_library(self, library: Library) -> int:
        """Save or update library."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT OR REPLACE INTO libraries (group_name, project_name, description, default_version, provider)
                   VALUES (?, ?, ?, ?, ?)""",
                (library.group_name, library.project_name, library.description, library.default_version, library.provider)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def save_version(self, version: Version) -> int:
        """Save version."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT OR REPLACE INTO versions (library_id, version_tag, commit_sha)
                   VALUES (?, ?, ?)""",
                (version.library_id, version.version_tag, version.commit_sha)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def save_document(self, doc: Document):
        """Save document."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT OR REPLACE INTO documents (version_id, file_path, content, content_type, tokens)
                   VALUES (?, ?, ?, ?, ?)""",
                (doc.version_id, doc.file_path, doc.content, doc.content_type, doc.tokens)
            )
            await db.commit()
    
    async def search(self, query: str) -> list[SearchResult]:
        """Search libraries by name."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """SELECT l.id, l.group_name, l.project_name, l.description,
                          GROUP_CONCAT(v.version_tag) as versions
                   FROM libraries l
                   LEFT JOIN versions v ON l.id = v.library_id
                   WHERE l.group_name LIKE ? OR l.project_name LIKE ? OR l.description LIKE ?
                   GROUP BY l.id""",
                (f"%{query}%", f"%{query}%", f"%{query}%")
            )
            rows = await cursor.fetchall()
            
            results = []
            for row in rows:
                versions = row["versions"].split(",") if row["versions"] else []
                results.append(SearchResult(
                    library_id=f"/{row['group_name']}/{row['project_name']}",
                    name=f"{row['group_name']}/{row['project_name']}",
                    description=row["description"] or "",
                    versions=versions,
                    score=1.0
                ))
            return results
    
    async def get_library(self, group: str, project: str) -> Optional[Library]:
        """Get library by group and project."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM libraries WHERE group_name = ? AND project_name = ?",
                (group, project)
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
                provider=row["provider"] if "provider" in row.keys() else "github"
            )
    
    async def get_version_id(self, library_id: int, version_tag: str) -> Optional[int]:
        """Get version ID."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT id FROM versions WHERE library_id = ? AND version_tag = ?",
                (library_id, version_tag)
            )
            row = await cursor.fetchone()
            return row[0] if row else None
    
    async def get_documents(
        self,
        version_id: int,
        topic: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> list[Document]:
        """
        Get documents for a version.

        Args:
            version_id: Version ID
            topic: Optional topic filter
            page: Page number for pagination
            page_size: Documents per page

        Returns:
            List of documents (page-based pagination only)

        Note:
            Token-based limiting is now handled in core.py after formatting,
            so quality filtering happens before token limiting.
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            if topic:
                cursor = await db.execute(
                    """SELECT * FROM documents
                       WHERE version_id = ? AND (file_path LIKE ? OR content LIKE ?)
                       ORDER BY file_path""",
                    (version_id, f"%{topic}%", f"%{topic}%")
                )
            else:
                cursor = await db.execute(
                    "SELECT * FROM documents WHERE version_id = ? ORDER BY file_path",
                    (version_id,)
                )

            rows = await cursor.fetchall()
            documents = [Document(
                id=row["id"],
                version_id=row["version_id"],
                file_path=row["file_path"],
                content=row["content"],
                content_type=row["content_type"],
                tokens=row["tokens"]
            ) for row in rows]

            # Page-based limiting
            # If page_size is very large (999+), return all (for token-based limiting in core)
            if page_size >= 999:
                return documents

            offset = (page - 1) * page_size
            return documents[offset:offset + page_size]
    
    async def get_all_libraries(self) -> list[Library]:
        """Get all indexed libraries with metadata."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM libraries ORDER BY last_indexed DESC"
            )
            rows = await cursor.fetchall()

            return [Library(
                id=row["id"],
                group_name=row["group_name"],
                project_name=row["project_name"],
                description=row["description"],
                default_version=row["default_version"],
                provider=row["provider"] if "provider" in row.keys() else "github",
                last_indexed=row["last_indexed"]
            ) for row in rows]

    async def fuzzy_search(self, query: str, limit: int = 10) -> list[FuzzySearchResult]:
        """Fuzzy search across libraries."""
        query_lower = query.lower()
        results = []
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM libraries")
            rows = await cursor.fetchall()
            
            for row in rows:
                name = row["project_name"].lower()
                group = row["group_name"].lower()
                desc = (row["description"] or "").lower()
                
                score = 0.0
                match_type = ""
                matched_field = ""
                
                # Exact match
                if query_lower == name:
                    score = 1.0
                    match_type = "exact"
                    matched_field = "name"
                # Starts with
                elif name.startswith(query_lower):
                    score = 0.9
                    match_type = "starts_with"
                    matched_field = "name"
                # Contains in name
                elif query_lower in name:
                    score = 0.8
                    match_type = "contains"
                    matched_field = "name"
                # Description match
                elif query_lower in desc:
                    score = 0.6
                    match_type = "contains"
                    matched_field = "description"
                # Group match
                elif query_lower in group:
                    score = 0.5
                    match_type = "contains"
                    matched_field = "group"
                # Fuzzy match (Levenshtein)
                else:
                    distance = levenshtein_distance(query_lower, name)
                    if distance <= 3 and len(name) > 0:
                        score = max(0.4, 1.0 - (distance / len(name)))
                        match_type = "fuzzy"
                        matched_field = "name"
                
                if score > 0:
                    results.append(FuzzySearchResult(
                        library_id=f"/{row['group_name']}/{row['project_name']}",
                        name=row["project_name"],
                        group=row["group_name"],
                        description=row["description"] or "",
                        score=score,
                        match_type=match_type,
                        matched_field=matched_field
                    ))
        
        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    # Code Analysis Storage Methods

    async def save_symbol(self, symbol, repository_id: int) -> int:
        """
        Save a symbol to the database.

        Args:
            symbol: Symbol object to save
            repository_id: Repository ID

        Returns:
            Symbol ID
        """
        import json

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO symbols (
                    repository_id, file_path, symbol_type, name, qualified_name,
                    line_start, line_end, column_start, signature, visibility,
                    language, documentation, is_exported, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    repository_id,
                    symbol.file_path,
                    symbol.symbol_type.value,
                    symbol.name,
                    symbol.qualified_name,
                    symbol.line_start,
                    symbol.line_end,
                    symbol.column_start,
                    symbol.signature,
                    symbol.visibility,
                    symbol.language,
                    symbol.documentation,
                    symbol.is_exported,
                    json.dumps(symbol.metadata)
                )
            )
            await db.commit()
            return cursor.lastrowid

    async def save_symbols(self, symbols: list, repository_id: int) -> list[int]:
        """
        Save multiple symbols to the database.

        Args:
            symbols: List of Symbol objects
            repository_id: Repository ID

        Returns:
            List of symbol IDs
        """
        ids = []
        for symbol in symbols:
            symbol_id = await self.save_symbol(symbol, repository_id)
            ids.append(symbol_id)
        return ids

    async def get_symbol_by_id(self, symbol_id: int) -> Optional[dict]:
        """Get a symbol by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM symbols WHERE id = ?",
                (symbol_id,)
            )
            row = await cursor.fetchone()
            if not row:
                return None
            return dict(row)

    async def get_symbols_by_file(self, repository_id: int, file_path: str) -> list[dict]:
        """Get all symbols for a specific file."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM symbols WHERE repository_id = ? AND file_path = ? ORDER BY line_start",
                (repository_id, file_path)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_symbols_by_type(self, repository_id: int, symbol_type: str) -> list[dict]:
        """Get all symbols of a specific type."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM symbols WHERE repository_id = ? AND symbol_type = ? ORDER BY file_path, line_start",
                (repository_id, symbol_type)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def search_symbols(self, repository_id: int, query: str) -> list[dict]:
        """Full-text search symbols. If query is empty, returns all symbols for the repository."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            if not query or not query.strip():
                # Return all symbols for the repository
                cursor = await db.execute(
                    "SELECT * FROM symbols WHERE repository_id = ? ORDER BY file_path, line_start",
                    (repository_id,)
                )
            else:
                # Use FTS for search
                cursor = await db.execute(
                    """SELECT s.* FROM symbols s
                       JOIN symbols_fts fts ON s.id = fts.rowid
                       WHERE fts.symbols_fts MATCH ? AND s.repository_id = ?
                       ORDER BY rank""",
                    (query, repository_id)
                )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def save_dependency(
        self,
        source_symbol_id: int,
        target_symbol_id: int,
        dependency_type: str,
        line: Optional[int] = None
    ) -> int:
        """Save a dependency between symbols."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO dependencies (
                    source_symbol_id, target_symbol_id, dependency_type, location_line
                ) VALUES (?, ?, ?, ?)""",
                (source_symbol_id, target_symbol_id, dependency_type, line)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_dependencies_for_symbol(self, symbol_id: int) -> list[dict]:
        """Get all dependencies where this symbol is the source."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM dependencies WHERE source_symbol_id = ?",
                (symbol_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_dependents_for_symbol(self, symbol_id: int) -> list[dict]:
        """Get all dependencies where this symbol is the target."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM dependencies WHERE target_symbol_id = ?",
                (symbol_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def save_call_edge(
        self,
        caller_id: int,
        callee_id: int,
        call_locations: list[dict]
    ):
        """Save a call graph edge."""
        import json

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO call_graph (caller_id, callee_id, call_count, call_locations)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(caller_id, callee_id) DO UPDATE SET
                   call_count = call_count + 1,
                   call_locations = ?""",
                (caller_id, callee_id, len(call_locations), json.dumps(call_locations), json.dumps(call_locations))
            )
            await db.commit()

    async def get_call_graph(self, repository_id: int) -> list[dict]:
        """Get the full call graph for a repository."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """SELECT cg.* FROM call_graph cg
                   JOIN symbols s ON cg.caller_id = s.id
                   WHERE s.repository_id = ?""",
                (repository_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_forward_calls(self, symbol_id: int) -> list[dict]:
        """Get all functions called by this symbol."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM call_graph WHERE caller_id = ?",
                (symbol_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_backward_calls(self, symbol_id: int) -> list[dict]:
        """Get all functions that call this symbol."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM call_graph WHERE callee_id = ?",
                (symbol_id,)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
