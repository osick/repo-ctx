"""Tests for the enrichment service.

These tests verify:
- Metadata enrichment for code and documentation
- Symbol enrichment
- Document enrichment with chunking
- Heuristic-based fallbacks
- Caching functionality
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from repo_ctx.services.enrichment import (
    EnrichmentService,
    EnrichedMetadata,
    EnrichedDocument,
    EnrichedSymbol,
)
from repo_ctx.services.chunking import ChunkingService


class MockServiceContext:
    """Mock service context for testing."""

    def __init__(self):
        self.content_storage = MagicMock()
        self.vector_storage = None
        self.graph_storage = None


class TestEnrichedMetadataDataclass:
    """Tests for EnrichedMetadata dataclass."""

    def test_create_enriched_metadata(self):
        """Test creating enriched metadata."""
        metadata = EnrichedMetadata(
            title="Test Title",
            description="Test description",
            tags=["python", "async"],
            categories=["service"],
        )

        assert metadata.title == "Test Title"
        assert metadata.description == "Test description"
        assert "python" in metadata.tags
        assert "service" in metadata.categories

    def test_enriched_metadata_defaults(self):
        """Test default values in enriched metadata."""
        metadata = EnrichedMetadata(title="Title", description="Desc")

        assert metadata.tags == []
        assert metadata.categories == []
        assert metadata.concepts == []
        assert metadata.keywords == []
        assert metadata.quality_score == 0.0
        assert metadata.search_text == ""
        assert metadata.related_topics == []
        assert metadata.metadata == {}


class TestEnrichedSymbolDataclass:
    """Tests for EnrichedSymbol dataclass."""

    def test_create_enriched_symbol(self):
        """Test creating enriched symbol."""
        symbol = EnrichedSymbol(
            name="my_function",
            qualified_name="module.my_function",
            symbol_type="function",
            description="A test function",
        )

        assert symbol.name == "my_function"
        assert symbol.qualified_name == "module.my_function"
        assert symbol.symbol_type == "function"
        assert symbol.description == "A test function"

    def test_enriched_symbol_defaults(self):
        """Test default values in enriched symbol."""
        symbol = EnrichedSymbol(
            name="test",
            qualified_name="test",
            symbol_type="function",
            description="",
        )

        assert symbol.signature is None
        assert symbol.documentation is None
        assert symbol.tags == []
        assert symbol.search_text == ""
        assert symbol.usage_hints == []


class TestEnrichedDocumentDataclass:
    """Tests for EnrichedDocument dataclass."""

    def test_create_enriched_document(self):
        """Test creating enriched document."""
        metadata = EnrichedMetadata(title="Test", description="Desc")
        doc = EnrichedDocument(
            id="doc-123",
            file_path="test.py",
            content="def foo(): pass",
            language="python",
            enriched_metadata=metadata,
        )

        assert doc.id == "doc-123"
        assert doc.file_path == "test.py"
        assert doc.language == "python"
        assert doc.enriched_metadata.title == "Test"

    def test_enriched_document_defaults(self):
        """Test default values in enriched document."""
        metadata = EnrichedMetadata(title="Test", description="Desc")
        doc = EnrichedDocument(
            id="doc-123",
            file_path="test.py",
            content="",
            language="python",
            enriched_metadata=metadata,
        )

        assert doc.chunks == []
        assert doc.symbols == []
        assert doc.dependencies == []


class TestEnrichmentServiceCreation:
    """Tests for EnrichmentService creation."""

    def test_create_service(self):
        """Test creating enrichment service."""
        context = MockServiceContext()
        service = EnrichmentService(context)

        assert service is not None
        assert service.use_llm is True
        assert service.enable_caching is True

    def test_create_service_with_options(self):
        """Test creating service with custom options."""
        context = MockServiceContext()
        service = EnrichmentService(
            context,
            use_llm=False,
            enable_caching=False,
        )

        assert service.use_llm is False
        assert service.enable_caching is False

    def test_create_service_with_chunking_service(self):
        """Test creating service with custom chunking service."""
        context = MockServiceContext()
        chunking = ChunkingService(default_strategy="fixed_size")
        service = EnrichmentService(context, chunking_service=chunking)

        assert service.chunking_service is chunking


class TestEnrichCodeHeuristics:
    """Tests for code enrichment with heuristics."""

    @pytest.fixture
    def service(self):
        """Create enrichment service without LLM."""
        context = MockServiceContext()
        return EnrichmentService(context, use_llm=False)

    @pytest.mark.asyncio
    async def test_enrich_empty_code(self, service):
        """Test enriching empty code."""
        result = await service.enrich_code("", "python")

        assert result.title == ""
        assert result.description == ""

    @pytest.mark.asyncio
    async def test_enrich_simple_function(self, service):
        """Test enriching simple function."""
        code = '''def hello_world():
    """Say hello."""
    print("Hello, World!")
'''
        result = await service.enrich_code(code, "python", "hello.py")

        assert result.title != ""
        assert result.description != ""
        assert "python" in result.tags

    @pytest.mark.asyncio
    async def test_enrich_class(self, service):
        """Test enriching class code."""
        code = '''class UserService:
    """Service for user management."""

    def get_user(self, user_id):
        pass

    def create_user(self, data):
        pass
'''
        result = await service.enrich_code(code, "python", "user_service.py")

        assert "UserService" in result.title or "User" in result.title
        assert result.quality_score > 0

    @pytest.mark.asyncio
    async def test_enrich_async_code(self, service):
        """Test enriching async code."""
        code = '''async def fetch_data():
    await some_async_call()
    return data
'''
        result = await service.enrich_code(code, "python")

        assert "async" in result.tags or "asynchronous" in result.concepts

    @pytest.mark.asyncio
    async def test_enrich_with_imports(self, service):
        """Test enriching code with imports."""
        code = '''import os
from typing import List
import requests

def make_request():
    return requests.get("http://example.com")
'''
        result = await service.enrich_code(code, "python")

        # Should extract dependencies
        assert "heuristic_enriched" in result.metadata

    @pytest.mark.asyncio
    async def test_enrich_test_code(self, service):
        """Test enriching test code."""
        code = '''import pytest

def test_something():
    assert True

def test_another_thing():
    assert 1 + 1 == 2
'''
        result = await service.enrich_code(code, "python", "test_example.py")

        assert "testing" in result.tags or "test" in result.categories

    @pytest.mark.asyncio
    async def test_enrich_generates_search_text(self, service):
        """Test that enrichment generates search text."""
        code = '''class DataProcessor:
    """Process data efficiently."""

    def process(self, data):
        return data.upper()
'''
        result = await service.enrich_code(code, "python")

        assert result.search_text != ""
        assert len(result.search_text) > 10

    @pytest.mark.asyncio
    async def test_enrich_calculates_quality_score(self, service):
        """Test that enrichment calculates quality score."""
        # High quality code with docstrings and type hints
        good_code = '''def greet(name: str) -> str:
    """Greet a person by name.

    Args:
        name: The person's name.

    Returns:
        A greeting message.
    """
    try:
        return f"Hello, {name}!"
    except Exception as e:
        logging.error(e)
        raise
'''
        result = await service.enrich_code(good_code, "python")

        assert result.quality_score >= 0.5

    @pytest.mark.asyncio
    async def test_enrich_caching(self, service):
        """Test that enrichment caching works."""
        code = "def foo(): pass"

        # First call
        result1 = await service.enrich_code(code, "python")

        # Second call should use cache
        result2 = await service.enrich_code(code, "python")

        assert result1.title == result2.title
        assert result1.description == result2.description

    @pytest.mark.asyncio
    async def test_clear_cache(self, service):
        """Test clearing the cache."""
        code = "def foo(): pass"
        await service.enrich_code(code, "python")

        service.clear_cache()

        assert len(service._cache) == 0


class TestEnrichSymbol:
    """Tests for symbol enrichment."""

    @pytest.fixture
    def service(self):
        """Create enrichment service without LLM."""
        context = MockServiceContext()
        return EnrichmentService(context, use_llm=False)

    @pytest.mark.asyncio
    async def test_enrich_function_symbol(self, service):
        """Test enriching function symbol."""
        result = await service.enrich_symbol(
            name="get_user",
            qualified_name="user_service.get_user",
            symbol_type="function",
        )

        assert result.name == "get_user"
        assert result.qualified_name == "user_service.get_user"
        assert "Retrieves" in result.description  # Pattern-based description

    @pytest.mark.asyncio
    async def test_enrich_symbol_with_documentation(self, service):
        """Test enriching symbol with existing documentation."""
        result = await service.enrich_symbol(
            name="process_data",
            qualified_name="processor.process_data",
            symbol_type="function",
            documentation="Process the input data and return results.",
        )

        # Should use existing documentation
        assert "Process" in result.description

    @pytest.mark.asyncio
    async def test_enrich_symbol_with_signature(self, service):
        """Test enriching symbol with signature."""
        result = await service.enrich_symbol(
            name="create_user",
            qualified_name="service.create_user",
            symbol_type="function",
            signature="create_user(name: str, email: str) -> User",
        )

        assert result.signature == "create_user(name: str, email: str) -> User"
        assert "usage_hints" in dir(result)

    @pytest.mark.asyncio
    async def test_enrich_class_symbol(self, service):
        """Test enriching class symbol."""
        result = await service.enrich_symbol(
            name="UserRepository",
            qualified_name="repositories.UserRepository",
            symbol_type="class",
        )

        assert result.symbol_type == "class"
        assert "class" in result.tags

    @pytest.mark.asyncio
    async def test_enrich_private_symbol(self, service):
        """Test enriching private symbol."""
        result = await service.enrich_symbol(
            name="_internal_helper",
            qualified_name="module._internal_helper",
            symbol_type="function",
        )

        assert "private" in result.tags

    @pytest.mark.asyncio
    async def test_enrich_magic_method(self, service):
        """Test enriching magic method."""
        result = await service.enrich_symbol(
            name="__init__",
            qualified_name="MyClass.__init__",
            symbol_type="method",
        )

        assert "magic" in result.tags

    @pytest.mark.asyncio
    async def test_enrich_async_symbol(self, service):
        """Test enriching async symbol."""
        result = await service.enrich_symbol(
            name="async_fetch",
            qualified_name="client.async_fetch",
            symbol_type="function",
            code="async def async_fetch(): await something()",
        )

        assert "async" in result.tags

    @pytest.mark.asyncio
    async def test_enrich_symbol_generates_search_text(self, service):
        """Test that symbol enrichment generates search text."""
        result = await service.enrich_symbol(
            name="calculate_total",
            qualified_name="calculator.calculate_total",
            symbol_type="function",
        )

        assert result.search_text != ""
        assert "calculate_total" in result.search_text

    @pytest.mark.asyncio
    async def test_enrich_symbol_usage_hints_function(self, service):
        """Test usage hints for functions."""
        result = await service.enrich_symbol(
            name="process",
            qualified_name="module.process",
            symbol_type="function",
            signature="process(data)",
        )

        assert len(result.usage_hints) > 0
        assert any("process(data)" in hint for hint in result.usage_hints)

    @pytest.mark.asyncio
    async def test_enrich_symbol_usage_hints_class(self, service):
        """Test usage hints for classes."""
        result = await service.enrich_symbol(
            name="MyClass",
            qualified_name="module.MyClass",
            symbol_type="class",
        )

        assert len(result.usage_hints) > 0
        assert any("Instantiate" in hint for hint in result.usage_hints)


class TestEnrichDocument:
    """Tests for document enrichment."""

    @pytest.fixture
    def service(self):
        """Create enrichment service without LLM."""
        context = MockServiceContext()
        return EnrichmentService(context, use_llm=False)

    @pytest.mark.asyncio
    async def test_enrich_document(self, service):
        """Test enriching a complete document."""
        content = '''"""User management module."""

import os
from typing import List

class UserManager:
    def get_user(self, user_id):
        pass

    def create_user(self, data):
        pass
'''
        result = await service.enrich_document(
            content=content,
            file_path="user_manager.py",
            language="python",
        )

        assert result.id is not None
        assert result.file_path == "user_manager.py"
        assert result.language == "python"
        assert result.enriched_metadata.title != ""

    @pytest.mark.asyncio
    async def test_enrich_document_with_chunks(self, service):
        """Test that document enrichment includes chunks."""
        content = "\n".join([f"def func_{i}(): pass" for i in range(20)])

        result = await service.enrich_document(
            content=content,
            file_path="functions.py",
            language="python",
            chunk_for_embedding=True,
        )

        # Should have chunks
        assert len(result.chunks) > 0

    @pytest.mark.asyncio
    async def test_enrich_document_without_chunks(self, service):
        """Test document enrichment without chunking."""
        content = "def foo(): pass"

        result = await service.enrich_document(
            content=content,
            file_path="simple.py",
            language="python",
            chunk_for_embedding=False,
        )

        assert result.chunks == []

    @pytest.mark.asyncio
    async def test_enrich_document_extracts_dependencies(self, service):
        """Test that document enrichment extracts dependencies."""
        content = '''import os
import json
from typing import Optional
from mypackage import something
'''
        result = await service.enrich_document(
            content=content,
            file_path="imports.py",
            language="python",
        )

        assert len(result.dependencies) > 0
        assert "os" in result.dependencies or "json" in result.dependencies


class TestBatchEnrich:
    """Tests for batch enrichment."""

    @pytest.fixture
    def service(self):
        """Create enrichment service without LLM."""
        context = MockServiceContext()
        return EnrichmentService(context, use_llm=False)

    @pytest.mark.asyncio
    async def test_batch_enrich_code(self, service):
        """Test batch enriching multiple code items."""
        items = [
            {"content": "def foo(): pass", "language": "python", "file_path": "a.py"},
            {"content": "class Bar: pass", "language": "python", "file_path": "b.py"},
        ]

        results = await service.batch_enrich(items, item_type="code")

        assert len(results) == 2
        assert all(isinstance(r, EnrichedMetadata) for r in results)

    @pytest.mark.asyncio
    async def test_batch_enrich_symbols(self, service):
        """Test batch enriching multiple symbols."""
        items = [
            {"name": "func1", "qualified_name": "m.func1", "symbol_type": "function"},
            {"name": "Class1", "qualified_name": "m.Class1", "symbol_type": "class"},
        ]

        results = await service.batch_enrich(items, item_type="symbol")

        assert len(results) == 2
        assert all(isinstance(r, EnrichedMetadata) for r in results)


class TestEnrichmentPatternDetection:
    """Tests for pattern detection in enrichment."""

    @pytest.fixture
    def service(self):
        """Create enrichment service without LLM."""
        context = MockServiceContext()
        return EnrichmentService(context, use_llm=False)

    @pytest.mark.asyncio
    async def test_detect_api_pattern(self, service):
        """Test detecting API patterns."""
        code = '''from fastapi import FastAPI

app = FastAPI()

@app.get("/users")
async def get_users():
    return []
'''
        result = await service.enrich_code(code, "python")

        assert "api" in result.tags or "api_endpoint" in result.categories

    @pytest.mark.asyncio
    async def test_detect_database_pattern(self, service):
        """Test detecting database patterns."""
        code = '''from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
'''
        result = await service.enrich_code(code, "python")

        assert "database" in result.tags or "orm" in result.concepts

    @pytest.mark.asyncio
    async def test_detect_async_pattern(self, service):
        """Test detecting async patterns."""
        code = '''import asyncio

async def main():
    await asyncio.sleep(1)
    tasks = [task1(), task2()]
    await asyncio.gather(*tasks)
'''
        result = await service.enrich_code(code, "python")

        assert "async" in result.tags or "asynchronous" in result.concepts

    @pytest.mark.asyncio
    async def test_detect_cli_pattern(self, service):
        """Test detecting CLI patterns."""
        code = '''import click

@click.command()
@click.option("--name", help="Your name")
def hello(name):
    click.echo(f"Hello {name}")
'''
        result = await service.enrich_code(code, "python")

        assert "cli" in result.tags


class TestSymbolDescriptionGeneration:
    """Tests for symbol description generation."""

    @pytest.fixture
    def service(self):
        """Create enrichment service without LLM."""
        context = MockServiceContext()
        return EnrichmentService(context, use_llm=False)

    @pytest.mark.asyncio
    async def test_get_pattern_description(self, service):
        """Test get_ pattern generates correct description."""
        result = await service.enrich_symbol(
            name="get_user_by_id",
            qualified_name="service.get_user_by_id",
            symbol_type="function",
        )

        assert "Retrieves" in result.description

    @pytest.mark.asyncio
    async def test_set_pattern_description(self, service):
        """Test set_ pattern generates correct description."""
        result = await service.enrich_symbol(
            name="set_config",
            qualified_name="config.set_config",
            symbol_type="function",
        )

        assert "Sets" in result.description

    @pytest.mark.asyncio
    async def test_is_pattern_description(self, service):
        """Test is_ pattern generates correct description."""
        result = await service.enrich_symbol(
            name="is_valid",
            qualified_name="validator.is_valid",
            symbol_type="function",
        )

        assert "Checks" in result.description

    @pytest.mark.asyncio
    async def test_create_pattern_description(self, service):
        """Test create_ pattern generates correct description."""
        result = await service.enrich_symbol(
            name="create_user",
            qualified_name="factory.create_user",
            symbol_type="function",
        )

        assert "Creates" in result.description

    @pytest.mark.asyncio
    async def test_validate_pattern_description(self, service):
        """Test validate_ pattern generates correct description."""
        result = await service.enrich_symbol(
            name="validate_input",
            qualified_name="validator.validate_input",
            symbol_type="function",
        )

        assert "Validates" in result.description

    @pytest.mark.asyncio
    async def test_handle_pattern_description(self, service):
        """Test handle_ pattern generates correct description."""
        result = await service.enrich_symbol(
            name="handle_request",
            qualified_name="handler.handle_request",
            symbol_type="function",
        )

        assert "Handles" in result.description


class TestQualityScoreCalculation:
    """Tests for quality score calculation."""

    @pytest.fixture
    def service(self):
        """Create enrichment service without LLM."""
        context = MockServiceContext()
        return EnrichmentService(context, use_llm=False)

    @pytest.mark.asyncio
    async def test_docstring_increases_score(self, service):
        """Test that docstrings increase quality score."""
        code_without = "def foo(): pass"
        code_with = '""\"Module docstring.\"\"\"\ndef foo(): pass'

        result_without = await service.enrich_code(code_without, "python")
        result_with = await service.enrich_code(code_with, "python")

        assert result_with.quality_score >= result_without.quality_score

    @pytest.mark.asyncio
    async def test_type_hints_increase_score(self, service):
        """Test that type hints increase quality score."""
        code_without = "def foo(x): return x"
        code_with = "def foo(x: int) -> int: return x"

        result_without = await service.enrich_code(code_without, "python")
        result_with = await service.enrich_code(code_with, "python")

        assert result_with.quality_score >= result_without.quality_score

    @pytest.mark.asyncio
    async def test_error_handling_increases_score(self, service):
        """Test that error handling increases quality score."""
        code_without = "def foo(): do_something()"
        code_with = '''def foo():
    try:
        do_something()
    except ValueError:
        handle_error()
'''
        result_without = await service.enrich_code(code_without, "python")
        result_with = await service.enrich_code(code_with, "python")

        assert result_with.quality_score >= result_without.quality_score

    @pytest.mark.asyncio
    async def test_score_bounded(self, service):
        """Test that quality score is bounded between 0 and 1."""
        codes = [
            "",
            "x = 1",
            "def foo(): pass",
            '"""Doc."""\ndef foo(x: int) -> int: return x',
        ]

        for code in codes:
            result = await service.enrich_code(code, "python")
            assert 0.0 <= result.quality_score <= 1.0


class TestRelatedTopics:
    """Tests for related topics extraction."""

    @pytest.fixture
    def service(self):
        """Create enrichment service without LLM."""
        context = MockServiceContext()
        return EnrichmentService(context, use_llm=False)

    @pytest.mark.asyncio
    async def test_detect_singleton_pattern(self, service):
        """Test detecting singleton pattern."""
        code = '''class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
'''
        result = await service.enrich_code(code, "python")

        pattern_topics = [t for t in result.related_topics if "pattern:" in t]
        assert any("singleton" in t for t in pattern_topics)

    @pytest.mark.asyncio
    async def test_detect_factory_pattern(self, service):
        """Test detecting factory pattern."""
        code = '''class ShapeFactory:
    def create_shape(self, shape_type):
        if shape_type == "circle":
            return Circle()
        elif shape_type == "square":
            return Square()
'''
        result = await service.enrich_code(code, "python")

        pattern_topics = [t for t in result.related_topics if "pattern:" in t]
        assert any("factory" in t for t in pattern_topics)


class TestEdgeCases:
    """Tests for edge cases in enrichment."""

    @pytest.fixture
    def service(self):
        """Create enrichment service without LLM."""
        context = MockServiceContext()
        return EnrichmentService(context, use_llm=False)

    @pytest.mark.asyncio
    async def test_unicode_content(self, service):
        """Test enriching code with unicode."""
        code = '''def greet(name):
    """Greet in multiple languages: 안녕하세요, 你好, مرحبا"""
    return f"Hello, {name}!"
'''
        result = await service.enrich_code(code, "python")

        assert result.title != ""

    @pytest.mark.asyncio
    async def test_very_long_code(self, service):
        """Test enriching very long code."""
        code = "\n".join([f"def func_{i}(): pass" for i in range(500)])

        result = await service.enrich_code(code, "python")

        assert result.title != ""
        # Should penalize very long files
        assert result.quality_score < 0.8

    @pytest.mark.asyncio
    async def test_minified_code(self, service):
        """Test enriching minified-like code."""
        code = "a=1;b=2;c=lambda x:x+1;d=c(a)+c(b)"

        result = await service.enrich_code(code, "python")

        # Should still produce result
        assert result is not None

    @pytest.mark.asyncio
    async def test_empty_symbol_name(self, service):
        """Test enriching symbol with empty name."""
        result = await service.enrich_symbol(
            name="",
            qualified_name="",
            symbol_type="function",
        )

        assert result.name == ""
        assert result.description != ""
