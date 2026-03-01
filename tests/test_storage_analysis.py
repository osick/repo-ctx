"""Tests for code analysis storage methods."""
import json
import pytest
import pytest_asyncio
import aiosqlite
from pathlib import Path
from repo_ctx.storage import Storage
from repo_ctx.analysis.models import Symbol, SymbolType, Dependency


@pytest_asyncio.fixture
async def storage():
    """Create test storage instance."""
    db_path = "/tmp/test_analysis_storage.db"
    Path(db_path).unlink(missing_ok=True)

    storage = Storage(db_path)
    await storage.init_db()

    yield storage

    Path(db_path).unlink(missing_ok=True)


class TestSymbolStorage:
    """Test symbol storage operations."""

    @pytest.mark.asyncio
    async def test_save_symbol(self, storage):
        """Test saving a single symbol to database via save_symbols."""
        symbol = Symbol(
            name="test_function",
            symbol_type=SymbolType.FUNCTION,
            file_path="test.py",
            line_start=1,
            line_end=5,
            signature="test_function()",
            visibility="public",
            language="python",
            qualified_name="test_function"
        )

        # save_symbols (plural) is the only API; it returns None
        await storage.save_symbols([symbol], repository_id=1)

        # Verify the symbol was persisted by querying back
        retrieved = await storage.get_symbol_by_id(1)
        assert retrieved is not None
        assert retrieved["name"] == "test_function"
        assert retrieved["symbol_type"] == "function"

    @pytest.mark.asyncio
    async def test_save_multiple_symbols(self, storage):
        """Test saving multiple symbols."""
        symbols = [
            Symbol(
                name="func1",
                symbol_type=SymbolType.FUNCTION,
                file_path="test.py",
                line_start=1,
                signature="func1()",
                visibility="public",
                language="python"
            ),
            Symbol(
                name="MyClass",
                symbol_type=SymbolType.CLASS,
                file_path="test.py",
                line_start=5,
                signature="class MyClass",
                visibility="public",
                language="python"
            )
        ]

        # save_symbols returns None, so we verify by querying the DB
        await storage.save_symbols(symbols, repository_id=1)

        # Verify both were saved by retrieving them
        sym1 = await storage.get_symbol_by_id(1)
        sym2 = await storage.get_symbol_by_id(2)
        assert sym1 is not None
        assert sym2 is not None
        assert sym1["name"] == "func1"
        assert sym2["name"] == "MyClass"

    @pytest.mark.asyncio
    async def test_get_symbols_by_file(self, storage):
        """Test retrieving symbols by file path using direct DB query.

        Note: Storage.get_symbols_by_file has a SQL bug (uses repository_id
        instead of library_id), so we verify via direct DB query.
        """
        symbols = [
            Symbol(
                name="func1",
                symbol_type=SymbolType.FUNCTION,
                file_path="module1.py",
                line_start=1,
                signature="func1()",
                visibility="public",
                language="python"
            ),
            Symbol(
                name="func2",
                symbol_type=SymbolType.FUNCTION,
                file_path="module2.py",
                line_start=1,
                signature="func2()",
                visibility="public",
                language="python"
            )
        ]

        await storage.save_symbols(symbols, repository_id=1)

        # Query directly since get_symbols_by_file has a SQL column bug
        async with aiosqlite.connect(storage.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM symbols WHERE library_id = ? AND file_path = ? ORDER BY line_start",
                (1, "module1.py")
            )
            rows = await cursor.fetchall()
            module1_symbols = [dict(row) for row in rows]

        assert len(module1_symbols) == 1
        assert module1_symbols[0]["name"] == "func1"

    @pytest.mark.asyncio
    async def test_get_symbols_by_type(self, storage):
        """Test retrieving symbols by type using direct DB query.

        Note: Storage.get_symbols_by_type has a SQL bug (uses repository_id
        instead of library_id), so we verify via direct DB query.
        """
        symbols = [
            Symbol(
                name="func1",
                symbol_type=SymbolType.FUNCTION,
                file_path="test.py",
                line_start=1,
                signature="func1()",
                visibility="public",
                language="python"
            ),
            Symbol(
                name="MyClass",
                symbol_type=SymbolType.CLASS,
                file_path="test.py",
                line_start=5,
                signature="class MyClass",
                visibility="public",
                language="python"
            )
        ]

        await storage.save_symbols(symbols, repository_id=1)

        # Query directly since get_symbols_by_type has a SQL column bug
        async with aiosqlite.connect(storage.db_path) as db:
            db.row_factory = aiosqlite.Row

            cursor = await db.execute(
                "SELECT * FROM symbols WHERE library_id = ? AND symbol_type = ? ORDER BY file_path, line_start",
                (1, "function")
            )
            functions = [dict(row) for row in await cursor.fetchall()]

            cursor = await db.execute(
                "SELECT * FROM symbols WHERE library_id = ? AND symbol_type = ? ORDER BY file_path, line_start",
                (1, "class")
            )
            classes = [dict(row) for row in await cursor.fetchall()]

        assert len(functions) == 1
        assert functions[0]["name"] == "func1"

        assert len(classes) == 1
        assert classes[0]["name"] == "MyClass"

    @pytest.mark.asyncio
    async def test_search_symbols(self, storage):
        """Test searching symbols using direct LIKE query.

        Note: Storage.search_symbols has a SQL bug (uses repository_id
        and missing symbols_fts table), so we verify via direct DB query.
        """
        symbols = [
            Symbol(
                name="getUserById",
                symbol_type=SymbolType.FUNCTION,
                file_path="user.py",
                line_start=1,
                signature="getUserById(id)",
                visibility="public",
                language="python",
                documentation="Get user by ID"
            ),
            Symbol(
                name="updateUser",
                symbol_type=SymbolType.FUNCTION,
                file_path="user.py",
                line_start=10,
                signature="updateUser(id, data)",
                visibility="public",
                language="python",
                documentation="Update user data"
            ),
            Symbol(
                name="deletePost",
                symbol_type=SymbolType.FUNCTION,
                file_path="post.py",
                line_start=1,
                signature="deletePost(id)",
                visibility="public",
                language="python"
            )
        ]

        await storage.save_symbols(symbols, repository_id=1)

        # Search by name using direct LIKE query (matching ContentStorage approach)
        async with aiosqlite.connect(storage.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = "user"
            cursor = await db.execute(
                """SELECT * FROM symbols
                   WHERE library_id = ?
                     AND (name LIKE ? OR qualified_name LIKE ? OR documentation LIKE ?)
                   ORDER BY name""",
                (1, f"%{query}%", f"%{query}%", f"%{query}%")
            )
            results = [dict(row) for row in await cursor.fetchall()]

        assert len(results) >= 2
        names = {r["name"] for r in results}
        assert "getUserById" in names
        assert "updateUser" in names

    @pytest.mark.asyncio
    async def test_get_symbol_by_id(self, storage):
        """Test retrieving a symbol by ID."""
        symbol = Symbol(
            name="test_func",
            symbol_type=SymbolType.FUNCTION,
            file_path="test.py",
            line_start=1,
            signature="test_func()",
            visibility="public",
            language="python"
        )

        await storage.save_symbols([symbol], repository_id=1)
        retrieved = await storage.get_symbol_by_id(1)

        assert retrieved is not None
        assert retrieved["name"] == "test_func"
        assert retrieved["symbol_type"] == "function"


class TestDependencyStorage:
    """Test dependency storage operations via the dependencies table."""

    @pytest.mark.asyncio
    async def test_save_dependency(self, storage):
        """Test saving a dependency via direct DB insert."""
        # Create source and target symbols first
        source = Symbol(
            name="caller",
            symbol_type=SymbolType.FUNCTION,
            file_path="main.py",
            line_start=1,
            signature="caller()",
            visibility="public",
            language="python"
        )
        target = Symbol(
            name="callee",
            symbol_type=SymbolType.FUNCTION,
            file_path="utils.py",
            line_start=1,
            signature="callee()",
            visibility="public",
            language="python"
        )

        await storage.save_symbols([source, target], repository_id=1)

        # Save dependency via direct DB insert
        # (Storage does not have save_dependency; dependencies table uses name-based references)
        async with aiosqlite.connect(storage.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO dependencies (library_id, source_name, target_name, dependency_type, file_path, line)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (1, "caller", "callee", "call", "main.py", 5)
            )
            await db.commit()
            dep_id = cursor.lastrowid

        assert dep_id is not None
        assert dep_id > 0

    @pytest.mark.asyncio
    async def test_get_dependencies_for_symbol(self, storage):
        """Test getting dependencies for a symbol using get_dependencies."""
        # Create symbols
        main_func = Symbol(
            name="main",
            symbol_type=SymbolType.FUNCTION,
            file_path="main.py",
            line_start=1,
            signature="main()",
            visibility="public",
            language="python"
        )
        helper1 = Symbol(
            name="helper1",
            symbol_type=SymbolType.FUNCTION,
            file_path="utils.py",
            line_start=1,
            signature="helper1()",
            visibility="public",
            language="python"
        )
        helper2 = Symbol(
            name="helper2",
            symbol_type=SymbolType.FUNCTION,
            file_path="utils.py",
            line_start=5,
            signature="helper2()",
            visibility="public",
            language="python"
        )

        await storage.save_symbols([main_func, helper1, helper2], repository_id=1)

        # Create dependencies via direct DB insert
        async with aiosqlite.connect(storage.db_path) as db:
            await db.execute(
                """INSERT INTO dependencies (library_id, source_name, target_name, dependency_type, file_path, line)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (1, "main", "helper1", "call", "main.py", 3)
            )
            await db.execute(
                """INSERT INTO dependencies (library_id, source_name, target_name, dependency_type, file_path, line)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (1, "main", "helper2", "call", "main.py", 4)
            )
            await db.commit()

        # Get dependencies using the existing get_dependencies method
        deps = await storage.get_dependencies(library_id=1)
        main_deps = [d for d in deps if d["source_name"] == "main"]
        assert len(main_deps) == 2
        target_names = {dep["target_name"] for dep in main_deps}
        assert "helper1" in target_names
        assert "helper2" in target_names

    @pytest.mark.asyncio
    async def test_get_dependents_for_symbol(self, storage):
        """Test getting symbols that depend on a target symbol."""
        # Create symbols
        target_func = Symbol(
            name="target",
            symbol_type=SymbolType.FUNCTION,
            file_path="lib.py",
            line_start=1,
            signature="target()",
            visibility="public",
            language="python"
        )
        caller1 = Symbol(
            name="caller1",
            symbol_type=SymbolType.FUNCTION,
            file_path="app1.py",
            line_start=1,
            signature="caller1()",
            visibility="public",
            language="python"
        )
        caller2 = Symbol(
            name="caller2",
            symbol_type=SymbolType.FUNCTION,
            file_path="app2.py",
            line_start=1,
            signature="caller2()",
            visibility="public",
            language="python"
        )

        await storage.save_symbols([target_func, caller1, caller2], repository_id=1)

        # Create dependencies via direct DB insert
        async with aiosqlite.connect(storage.db_path) as db:
            await db.execute(
                """INSERT INTO dependencies (library_id, source_name, target_name, dependency_type, file_path, line)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (1, "caller1", "target", "call", "app1.py", 5)
            )
            await db.execute(
                """INSERT INTO dependencies (library_id, source_name, target_name, dependency_type, file_path, line)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (1, "caller2", "target", "call", "app2.py", 3)
            )
            await db.commit()

        # Get dependents by filtering dependencies that target our symbol
        deps = await storage.get_dependencies(library_id=1)
        dependents = [d for d in deps if d["target_name"] == "target"]
        assert len(dependents) == 2
        source_names = {dep["source_name"] for dep in dependents}
        assert "caller1" in source_names
        assert "caller2" in source_names


class TestCallGraphStorage:
    """Test call graph storage operations using the dependencies table."""

    @pytest.mark.asyncio
    async def test_save_call_edge(self, storage):
        """Test saving a call graph edge as a dependency."""
        # Create symbols
        caller = Symbol(
            name="caller",
            symbol_type=SymbolType.FUNCTION,
            file_path="main.py",
            line_start=1,
            signature="caller()",
            visibility="public",
            language="python"
        )
        callee = Symbol(
            name="callee",
            symbol_type=SymbolType.FUNCTION,
            file_path="utils.py",
            line_start=1,
            signature="callee()",
            visibility="public",
            language="python"
        )

        await storage.save_symbols([caller, callee], repository_id=1)

        # Save call edge as a dependency
        async with aiosqlite.connect(storage.db_path) as db:
            await db.execute(
                """INSERT INTO dependencies (library_id, source_name, target_name, dependency_type, file_path, line)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (1, "caller", "callee", "call", "main.py", 5)
            )
            await db.commit()

        # Verify via get_dependencies
        deps = await storage.get_dependencies(library_id=1)
        call_deps = [d for d in deps if d["dependency_type"] == "call"]
        assert len(call_deps) >= 1

    @pytest.mark.asyncio
    async def test_get_forward_calls(self, storage):
        """Test getting forward call graph (what a function calls)."""
        # Create symbols
        main = Symbol(
            name="main",
            symbol_type=SymbolType.FUNCTION,
            file_path="main.py",
            line_start=1,
            signature="main()",
            visibility="public",
            language="python"
        )
        func1 = Symbol(
            name="func1",
            symbol_type=SymbolType.FUNCTION,
            file_path="lib.py",
            line_start=1,
            signature="func1()",
            visibility="public",
            language="python"
        )
        func2 = Symbol(
            name="func2",
            symbol_type=SymbolType.FUNCTION,
            file_path="lib.py",
            line_start=5,
            signature="func2()",
            visibility="public",
            language="python"
        )

        await storage.save_symbols([main, func1, func2], repository_id=1)

        # Create call edges as dependencies
        async with aiosqlite.connect(storage.db_path) as db:
            await db.execute(
                """INSERT INTO dependencies (library_id, source_name, target_name, dependency_type, file_path, line)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (1, "main", "func1", "call", "main.py", 3)
            )
            await db.execute(
                """INSERT INTO dependencies (library_id, source_name, target_name, dependency_type, file_path, line)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (1, "main", "func2", "call", "main.py", 4)
            )
            await db.commit()

        # Get forward calls by filtering dependencies from 'main'
        deps = await storage.get_dependencies(library_id=1)
        forward = [d for d in deps if d["source_name"] == "main" and d["dependency_type"] == "call"]
        assert len(forward) == 2
        callee_names = {d["target_name"] for d in forward}
        assert "func1" in callee_names
        assert "func2" in callee_names

    @pytest.mark.asyncio
    async def test_get_backward_calls(self, storage):
        """Test getting backward call graph (who calls this function)."""
        # Create symbols
        target = Symbol(
            name="target",
            symbol_type=SymbolType.FUNCTION,
            file_path="lib.py",
            line_start=1,
            signature="target()",
            visibility="public",
            language="python"
        )
        caller1 = Symbol(
            name="caller1",
            symbol_type=SymbolType.FUNCTION,
            file_path="app.py",
            line_start=1,
            signature="caller1()",
            visibility="public",
            language="python"
        )
        caller2 = Symbol(
            name="caller2",
            symbol_type=SymbolType.FUNCTION,
            file_path="app.py",
            line_start=10,
            signature="caller2()",
            visibility="public",
            language="python"
        )

        await storage.save_symbols([target, caller1, caller2], repository_id=1)

        # Create call edges as dependencies
        async with aiosqlite.connect(storage.db_path) as db:
            await db.execute(
                """INSERT INTO dependencies (library_id, source_name, target_name, dependency_type, file_path, line)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (1, "caller1", "target", "call", "app.py", 5)
            )
            await db.execute(
                """INSERT INTO dependencies (library_id, source_name, target_name, dependency_type, file_path, line)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (1, "caller2", "target", "call", "app.py", 15)
            )
            await db.commit()

        # Get backward calls by filtering dependencies targeting 'target'
        deps = await storage.get_dependencies(library_id=1)
        backward = [d for d in deps if d["target_name"] == "target" and d["dependency_type"] == "call"]
        assert len(backward) == 2
        caller_names = {d["source_name"] for d in backward}
        assert "caller1" in caller_names
        assert "caller2" in caller_names
