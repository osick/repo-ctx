"""Tests for LLM service for code analysis.

These tests verify:
- LLM-based code documentation generation
- Code summarization
- Code explanation
- Code classification
- Code quality suggestions
- Docstring generation
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from repo_ctx.services.llm import (
    LLMService,
    LLMResponse,
    CodeSummary,
    CodeExplanation,
    CodeClassification,
    QualitySuggestion,
    GeneratedDocstring,
)


class TestLLMServiceInitialization:
    """Tests for LLM service initialization."""

    def test_llm_service_creation(self):
        """Test creating an LLM service."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=MagicMock())
        service = LLMService(context)

        assert service is not None
        assert service.model == "gpt-5-mini"  # Default model

    def test_llm_service_custom_model(self):
        """Test creating an LLM service with custom model."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=MagicMock())
        service = LLMService(context, model="claude-3-5-sonnet")

        assert service.model == "claude-3-5-sonnet"

    def test_llm_service_with_api_key(self):
        """Test LLM service with API key."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=MagicMock())
        service = LLMService(context, api_key="test-key")

        assert service.api_key == "test-key"

    def test_llm_service_disabled_by_default(self):
        """Test that LLM service can be disabled."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=MagicMock())
        service = LLMService(context, enabled=False)

        assert service.enabled is False


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""

    def test_llm_response_creation(self):
        """Test creating an LLMResponse."""
        response = LLMResponse(
            content="Test response",
            model="gpt-5-mini",
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )

        assert response.content == "Test response"
        assert response.model == "gpt-5-mini"
        assert response.total_tokens == 30

    def test_llm_response_with_metadata(self):
        """Test LLMResponse with metadata."""
        response = LLMResponse(
            content="Test",
            model="gpt-5-mini",
            metadata={"source": "test"},
        )

        assert response.metadata["source"] == "test"


class TestCodeSummarization:
    """Tests for code summarization functionality."""

    @pytest.fixture
    def service(self):
        """Create test service."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=MagicMock())
        return LLMService(context, enabled=True)

    @pytest.mark.asyncio
    async def test_summarize_code_returns_summary(self, service):
        """Test that summarize_code returns a CodeSummary."""
        code = """
def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
"""
        result = await service.summarize_code(code, language="python")

        assert isinstance(result, CodeSummary)
        assert result.summary is not None
        assert len(result.summary) > 0

    @pytest.mark.asyncio
    async def test_summarize_code_empty_code(self, service):
        """Test summarization with empty code."""
        result = await service.summarize_code("", language="python")

        assert result.summary == ""
        assert result.language == "python"

    @pytest.mark.asyncio
    async def test_summarize_code_with_context(self, service):
        """Test summarization with context."""
        code = "def helper(): pass"
        context = "This is part of a data processing pipeline."

        result = await service.summarize_code(
            code, language="python", context=context
        )

        assert isinstance(result, CodeSummary)

    @pytest.mark.asyncio
    async def test_summarize_file(self, service):
        """Test summarizing a complete file."""
        code = """
class UserService:
    def __init__(self, db):
        self.db = db

    def get_user(self, user_id):
        return self.db.query(User).get(user_id)

    def create_user(self, data):
        user = User(**data)
        self.db.add(user)
        return user
"""
        result = await service.summarize_code(
            code, language="python", file_path="services/user.py"
        )

        assert isinstance(result, CodeSummary)
        assert result.file_path == "services/user.py"


class TestCodeExplanation:
    """Tests for code explanation functionality."""

    @pytest.fixture
    def service(self):
        """Create test service."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=MagicMock())
        return LLMService(context, enabled=True)

    @pytest.mark.asyncio
    async def test_explain_code_basic(self, service):
        """Test basic code explanation."""
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        result = await service.explain_code(code, language="python")

        assert isinstance(result, CodeExplanation)
        assert result.explanation is not None
        assert len(result.explanation) > 0

    @pytest.mark.asyncio
    async def test_explain_code_with_detail_level(self, service):
        """Test explanation with different detail levels."""
        code = "x = lambda a, b: a + b"

        result_brief = await service.explain_code(
            code, language="python", detail_level="brief"
        )
        result_detailed = await service.explain_code(
            code, language="python", detail_level="detailed"
        )

        assert isinstance(result_brief, CodeExplanation)
        assert isinstance(result_detailed, CodeExplanation)
        assert result_brief.detail_level == "brief"
        assert result_detailed.detail_level == "detailed"

    @pytest.mark.asyncio
    async def test_explain_code_for_beginner(self, service):
        """Test explanation for beginner audience."""
        code = "result = [x**2 for x in range(10)]"

        result = await service.explain_code(
            code, language="python", audience="beginner"
        )

        assert isinstance(result, CodeExplanation)
        assert result.audience == "beginner"

    @pytest.mark.asyncio
    async def test_explain_code_empty(self, service):
        """Test explanation with empty code."""
        result = await service.explain_code("", language="python")

        assert result.explanation == ""


class TestCodeClassification:
    """Tests for code classification functionality."""

    @pytest.fixture
    def service(self):
        """Create test service."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=MagicMock())
        return LLMService(context, enabled=True)

    @pytest.mark.asyncio
    async def test_classify_code_basic(self, service):
        """Test basic code classification."""
        code = """
class UserRepository:
    def __init__(self, session):
        self.session = session

    def find_by_id(self, id):
        return self.session.query(User).get(id)
"""
        result = await service.classify_code(code, language="python")

        assert isinstance(result, CodeClassification)
        assert result.primary_category is not None
        assert result.confidence >= 0 and result.confidence <= 1

    @pytest.mark.asyncio
    async def test_classify_code_returns_categories(self, service):
        """Test that classification returns multiple categories."""
        code = """
def validate_email(email):
    import re
    pattern = r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$'
    return bool(re.match(pattern, email))
"""
        result = await service.classify_code(code, language="python")

        assert isinstance(result.categories, list)
        assert len(result.categories) > 0

    @pytest.mark.asyncio
    async def test_classify_code_empty(self, service):
        """Test classification with empty code."""
        result = await service.classify_code("", language="python")

        assert result.primary_category == "unknown"
        assert result.confidence == 0.0


class TestQualitySuggestions:
    """Tests for code quality suggestions functionality."""

    @pytest.fixture
    def service(self):
        """Create test service."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=MagicMock())
        return LLMService(context, enabled=True)

    @pytest.mark.asyncio
    async def test_suggest_improvements_basic(self, service):
        """Test basic quality suggestions."""
        code = """
def f(x):
    y = []
    for i in x:
        if i > 0:
            y.append(i * 2)
    return y
"""
        result = await service.suggest_improvements(code, language="python")

        assert isinstance(result, list)
        assert all(isinstance(s, QualitySuggestion) for s in result)

    @pytest.mark.asyncio
    async def test_suggest_improvements_categories(self, service):
        """Test suggestions include different categories."""
        code = """
def process_data(d):
    r = {}
    for k in d:
        r[k] = d[k] * 2
    return r
"""
        result = await service.suggest_improvements(code, language="python")

        # Verify structure
        for suggestion in result:
            assert suggestion.category in [
                "readability", "performance", "maintainability",
                "security", "naming", "documentation", "best_practices"
            ]
            assert suggestion.severity in ["low", "medium", "high"]

    @pytest.mark.asyncio
    async def test_suggest_improvements_empty(self, service):
        """Test suggestions with empty code."""
        result = await service.suggest_improvements("", language="python")

        assert result == []


class TestDocstringGeneration:
    """Tests for docstring generation functionality."""

    @pytest.fixture
    def service(self):
        """Create test service."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=MagicMock())
        return LLMService(context, enabled=True)

    @pytest.mark.asyncio
    async def test_generate_docstring_function(self, service):
        """Test generating docstring for a function."""
        code = """
def calculate_distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
"""
        result = await service.generate_docstring(
            code, language="python", style="google"
        )

        assert isinstance(result, GeneratedDocstring)
        assert result.docstring is not None
        assert result.style == "google"

    @pytest.mark.asyncio
    async def test_generate_docstring_class(self, service):
        """Test generating docstring for a class."""
        code = """
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
"""
        result = await service.generate_docstring(
            code, language="python", style="numpy"
        )

        assert isinstance(result, GeneratedDocstring)
        assert result.style == "numpy"

    @pytest.mark.asyncio
    async def test_generate_docstring_different_styles(self, service):
        """Test generating docstrings in different styles."""
        code = "def add(a, b): return a + b"

        google_result = await service.generate_docstring(
            code, language="python", style="google"
        )
        numpy_result = await service.generate_docstring(
            code, language="python", style="numpy"
        )
        sphinx_result = await service.generate_docstring(
            code, language="python", style="sphinx"
        )

        assert google_result.style == "google"
        assert numpy_result.style == "numpy"
        assert sphinx_result.style == "sphinx"

    @pytest.mark.asyncio
    async def test_generate_docstring_empty(self, service):
        """Test docstring generation with empty code."""
        result = await service.generate_docstring("", language="python")

        assert result.docstring == ""


class TestLLMServiceWithMockedAPI:
    """Tests using mocked LLM API calls."""

    @pytest.fixture
    def mock_litellm(self):
        """Mock litellm for testing."""
        with patch("repo_ctx.services.llm.litellm") as mock:
            mock.acompletion = AsyncMock(
                return_value=MagicMock(
                    choices=[
                        MagicMock(
                            message=MagicMock(content="Test response")
                        )
                    ],
                    usage=MagicMock(
                        prompt_tokens=10,
                        completion_tokens=20,
                        total_tokens=30,
                    ),
                    model="gpt-5-mini",
                )
            )
            yield mock

    @pytest.fixture
    def service(self):
        """Create test service."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=MagicMock())
        return LLMService(context, enabled=True)

    @pytest.mark.asyncio
    async def test_complete_calls_litellm(self, service, mock_litellm):
        """Test that complete calls litellm."""
        await service._complete("Test prompt")

        mock_litellm.acompletion.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_returns_response(self, service, mock_litellm):
        """Test that complete returns LLMResponse."""
        result = await service._complete("Test prompt")

        assert isinstance(result, LLMResponse)
        assert result.content == "Test response"
        assert result.model == "gpt-5-mini"


class TestLLMServiceDisabled:
    """Tests for disabled LLM service."""

    @pytest.fixture
    def service(self):
        """Create disabled service."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=MagicMock())
        return LLMService(context, enabled=False)

    @pytest.mark.asyncio
    async def test_summarize_when_disabled(self, service):
        """Test summarize returns placeholder when disabled."""
        result = await service.summarize_code("def f(): pass", "python")

        assert isinstance(result, CodeSummary)
        assert "disabled" in result.summary.lower() or result.summary == ""

    @pytest.mark.asyncio
    async def test_explain_when_disabled(self, service):
        """Test explain returns placeholder when disabled."""
        result = await service.explain_code("def f(): pass", "python")

        assert isinstance(result, CodeExplanation)
        assert "disabled" in result.explanation.lower() or result.explanation == ""

    @pytest.mark.asyncio
    async def test_classify_when_disabled(self, service):
        """Test classify returns unknown when disabled."""
        result = await service.classify_code("def f(): pass", "python")

        assert result.primary_category == "unknown"


class TestLLMServiceFallback:
    """Tests for LLM service fallback behavior."""

    @pytest.fixture
    def service(self):
        """Create test service."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=MagicMock())
        return LLMService(context, enabled=True, use_fallback=True)

    @pytest.mark.asyncio
    async def test_fallback_summarization(self, service):
        """Test fallback summarization without API."""
        code = """
def calculate_average(numbers):
    '''Calculate the average of a list of numbers.'''
    return sum(numbers) / len(numbers)
"""
        result = await service.summarize_code(code, "python")

        # Fallback should extract from docstring
        assert isinstance(result, CodeSummary)
        assert len(result.summary) > 0

    @pytest.mark.asyncio
    async def test_fallback_classification(self, service):
        """Test fallback classification using heuristics."""
        code = """
class UserController:
    def get(self, request):
        return Response(data)
"""
        result = await service.classify_code(code, "python")

        assert isinstance(result, CodeClassification)
        assert result.primary_category != "unknown"


class TestAnalyzeRepository:
    """Tests for repository-wide analysis."""

    @pytest.fixture
    def service(self):
        """Create test service."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=MagicMock())
        return LLMService(context, enabled=True)

    @pytest.mark.asyncio
    async def test_analyze_symbols(self, service):
        """Test analyzing multiple symbols."""
        symbols = [
            {"name": "get_user", "qualified_name": "services.user.get_user", "symbol_type": "function"},
            {"name": "UserService", "qualified_name": "services.user.UserService", "symbol_type": "class"},
        ]

        result = await service.analyze_symbols(symbols)

        assert isinstance(result, dict)
        assert "summaries" in result

    @pytest.mark.asyncio
    async def test_generate_module_summary(self, service):
        """Test generating module summary."""
        module_code = """
'''User authentication module.'''

from .base import BaseAuth

class OAuth2Auth(BaseAuth):
    def authenticate(self, token):
        pass

    def refresh(self, refresh_token):
        pass
"""
        result = await service.generate_module_summary(
            module_code, "python", "auth/oauth.py"
        )

        assert isinstance(result, CodeSummary)
        assert result.file_path == "auth/oauth.py"
