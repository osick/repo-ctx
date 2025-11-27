"""Tests for code analysis storage methods."""
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
        """Test saving a symbol to database."""
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

        symbol_id = await storage.save_symbol(symbol, repository_id=1)
        assert symbol_id is not None
        assert symbol_id > 0

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

        ids = await storage.save_symbols(symbols, repository_id=1)
        assert len(ids) == 2
        assert all(id > 0 for id in ids)

    @pytest.mark.asyncio
    async def test_get_symbols_by_file(self, storage):
        """Test retrieving symbols by file path."""
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

        module1_symbols = await storage.get_symbols_by_file(repository_id=1, file_path="module1.py")
        assert len(module1_symbols) == 1
        assert module1_symbols[0]["name"] == "func1"

    @pytest.mark.asyncio
    async def test_get_symbols_by_type(self, storage):
        """Test retrieving symbols by type."""
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

        functions = await storage.get_symbols_by_type(repository_id=1, symbol_type="function")
        assert len(functions) == 1
        assert functions[0]["name"] == "func1"

        classes = await storage.get_symbols_by_type(repository_id=1, symbol_type="class")
        assert len(classes) == 1
        assert classes[0]["name"] == "MyClass"

    @pytest.mark.asyncio
    async def test_search_symbols(self, storage):
        """Test full-text search of symbols."""
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

        # Search by name
        results = await storage.search_symbols(repository_id=1, query="user")
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

        symbol_id = await storage.save_symbol(symbol, repository_id=1)
        retrieved = await storage.get_symbol_by_id(symbol_id)

        assert retrieved is not None
        assert retrieved["name"] == "test_func"
        assert retrieved["symbol_type"] == "function"


class TestDependencyStorage:
    """Test dependency storage operations."""

    @pytest.mark.asyncio
    async def test_save_dependency(self, storage):
        """Test saving a dependency."""
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

        source_id = await storage.save_symbol(source, repository_id=1)
        target_id = await storage.save_symbol(target, repository_id=1)

        # Save dependency
        dep_id = await storage.save_dependency(
            source_symbol_id=source_id,
            target_symbol_id=target_id,
            dependency_type="call",
            line=5
        )

        assert dep_id is not None
        assert dep_id > 0

    @pytest.mark.asyncio
    async def test_get_dependencies_for_symbol(self, storage):
        """Test getting dependencies for a symbol."""
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

        main_id = await storage.save_symbol(main_func, repository_id=1)
        helper1_id = await storage.save_symbol(helper1, repository_id=1)
        helper2_id = await storage.save_symbol(helper2, repository_id=1)

        # Create dependencies
        await storage.save_dependency(main_id, helper1_id, "call", line=3)
        await storage.save_dependency(main_id, helper2_id, "call", line=4)

        # Get dependencies
        deps = await storage.get_dependencies_for_symbol(main_id)
        assert len(deps) == 2
        target_ids = {dep["target_symbol_id"] for dep in deps}
        assert helper1_id in target_ids
        assert helper2_id in target_ids

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

        target_id = await storage.save_symbol(target_func, repository_id=1)
        caller1_id = await storage.save_symbol(caller1, repository_id=1)
        caller2_id = await storage.save_symbol(caller2, repository_id=1)

        # Create dependencies
        await storage.save_dependency(caller1_id, target_id, "call", line=5)
        await storage.save_dependency(caller2_id, target_id, "call", line=3)

        # Get dependents
        dependents = await storage.get_dependents_for_symbol(target_id)
        assert len(dependents) == 2
        source_ids = {dep["source_symbol_id"] for dep in dependents}
        assert caller1_id in source_ids
        assert caller2_id in source_ids


class TestCallGraphStorage:
    """Test call graph storage operations."""

    @pytest.mark.asyncio
    async def test_save_call_edge(self, storage):
        """Test saving a call graph edge."""
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

        caller_id = await storage.save_symbol(caller, repository_id=1)
        callee_id = await storage.save_symbol(callee, repository_id=1)

        # Save call edge
        await storage.save_call_edge(
            caller_id=caller_id,
            callee_id=callee_id,
            call_locations=[{"line": 5, "file": "main.py"}]
        )

        # Verify
        call_graph = await storage.get_call_graph(repository_id=1)
        assert len(call_graph) >= 1

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

        main_id = await storage.save_symbol(main, repository_id=1)
        func1_id = await storage.save_symbol(func1, repository_id=1)
        func2_id = await storage.save_symbol(func2, repository_id=1)

        # Create call edges
        await storage.save_call_edge(main_id, func1_id, [{"line": 3}])
        await storage.save_call_edge(main_id, func2_id, [{"line": 4}])

        # Get forward calls
        forward = await storage.get_forward_calls(main_id)
        assert len(forward) == 2
        callee_ids = {call["callee_id"] for call in forward}
        assert func1_id in callee_ids
        assert func2_id in callee_ids

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

        target_id = await storage.save_symbol(target, repository_id=1)
        caller1_id = await storage.save_symbol(caller1, repository_id=1)
        caller2_id = await storage.save_symbol(caller2, repository_id=1)

        # Create call edges
        await storage.save_call_edge(caller1_id, target_id, [{"line": 5}])
        await storage.save_call_edge(caller2_id, target_id, [{"line": 15}])

        # Get backward calls
        backward = await storage.get_backward_calls(target_id)
        assert len(backward) == 2
        caller_ids = {call["caller_id"] for call in backward}
        assert caller1_id in caller_ids
        assert caller2_id in caller_ids
