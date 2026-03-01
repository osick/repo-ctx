"""LLM service for code analysis.

This module provides LLM-enhanced code analysis using litellm for multi-provider support.
Supports code summarization, explanation, classification, and documentation generation.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Literal, Optional

from repo_ctx.services.base import BaseService, ServiceContext

logger = logging.getLogger("repo_ctx.services.llm")

# Try to import litellm
try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    litellm = None


@dataclass
class LLMResponse:
    """Response from LLM completion."""

    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeSummary:
    """Summary of code."""

    summary: str
    language: str
    file_path: Optional[str] = None
    key_components: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeExplanation:
    """Explanation of code."""

    explanation: str
    language: str
    detail_level: str = "standard"
    audience: str = "developer"
    concepts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeClassification:
    """Classification of code."""

    primary_category: str
    categories: list[str] = field(default_factory=list)
    confidence: float = 0.0
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class QualitySuggestion:
    """Code quality improvement suggestion."""

    suggestion: str
    category: str  # readability, performance, maintainability, security, naming, documentation, best_practices
    severity: str  # low, medium, high
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    original_code: Optional[str] = None
    suggested_code: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedDocstring:
    """Generated docstring for code."""

    docstring: str
    style: str  # google, numpy, sphinx, jsdoc
    parameters: list[dict[str, str]] = field(default_factory=list)
    returns: Optional[str] = None
    raises: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# Code classification categories
CODE_CATEGORIES = [
    "controller",
    "service",
    "repository",
    "model",
    "utility",
    "configuration",
    "test",
    "middleware",
    "handler",
    "validator",
    "parser",
    "serializer",
    "factory",
    "observer",
    "strategy",
    "adapter",
    "decorator",
    "singleton",
    "api_endpoint",
    "data_access",
    "business_logic",
    "presentation",
    "infrastructure",
]


class LLMService(BaseService):
    """Service for LLM-enhanced code analysis.

    Uses litellm for multi-provider support (OpenAI, Anthropic, Cohere, etc.).
    Provides code summarization, explanation, classification, and documentation.
    """

    # Default prompts for various operations
    SUMMARIZE_PROMPT = """Analyze the following {language} code and provide a concise summary.
Focus on:
1. What the code does (main purpose)
2. Key components (classes, functions, variables)
3. External dependencies

Code:
```{language}
{code}
```

{context}

Respond with a JSON object:
{{
    "summary": "Brief description of what the code does",
    "key_components": ["list", "of", "key", "components"],
    "dependencies": ["list", "of", "external", "dependencies"]
}}"""

    EXPLAIN_PROMPT = """Explain the following {language} code for a {audience} audience.
Provide a {detail_level} explanation covering:
1. What the code does step by step
2. Key programming concepts used
3. How different parts work together

Code:
```{language}
{code}
```

Respond with a JSON object:
{{
    "explanation": "Detailed explanation of the code",
    "concepts": ["list", "of", "programming", "concepts", "used"]
}}"""

    CLASSIFY_PROMPT = """Classify the following {language} code into categories.
Available categories: {categories}

Code:
```{language}
{code}
```

Respond with a JSON object:
{{
    "primary_category": "the main category",
    "categories": ["all", "applicable", "categories"],
    "confidence": 0.95,
    "tags": ["relevant", "tags", "like", "async", "http", "orm"]
}}"""

    IMPROVE_PROMPT = """Analyze the following {language} code and suggest improvements.
Focus on: readability, performance, maintainability, security, naming, documentation, best practices.

Code:
```{language}
{code}
```

Respond with a JSON array of suggestions:
[
    {{
        "suggestion": "Description of the improvement",
        "category": "one of: readability, performance, maintainability, security, naming, documentation, best_practices",
        "severity": "one of: low, medium, high",
        "original_code": "problematic code snippet (if applicable)",
        "suggested_code": "improved code snippet (if applicable)"
    }}
]"""

    DOCSTRING_PROMPT = """Generate a {style} style docstring for the following {language} code.

Code:
```{language}
{code}
```

Respond with a JSON object:
{{
    "docstring": "The complete docstring with proper formatting",
    "parameters": [
        {{"name": "param_name", "type": "param_type", "description": "param description"}}
    ],
    "returns": "Return value description (if applicable)",
    "raises": ["Exception types that may be raised"],
    "examples": ["Usage examples"]
}}"""

    def __init__(
        self,
        context: ServiceContext,
        model: str = "gpt-5-mini",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        enabled: bool = True,
        use_fallback: bool = True,
        max_tokens: int = 2048,
        temperature: float = 0.3,
    ) -> None:
        """Initialize the LLM service.

        Args:
            context: ServiceContext with storage backends.
            model: LLM model name (litellm format).
            api_key: API key for the LLM provider.
            base_url: Optional base URL for the API.
            enabled: Whether LLM features are enabled.
            use_fallback: Whether to use heuristic fallbacks when API unavailable.
            max_tokens: Maximum tokens for responses.
            temperature: Temperature for generation.
        """
        super().__init__(context)
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.enabled = enabled
        self.use_fallback = use_fallback
        self.max_tokens = max_tokens
        self.temperature = temperature

    async def _complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[str] = None,
    ) -> LLMResponse:
        """Make an LLM completion request.

        Args:
            prompt: User prompt.
            system_prompt: Optional system prompt.
            response_format: Optional response format (e.g., "json").

        Returns:
            LLMResponse with the completion.
        """
        if not LITELLM_AVAILABLE:
            logger.warning("litellm not installed - using fallback")
            return LLMResponse(
                content="",
                model=self.model,
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            # Set API key based on model
            if self.api_key:
                if "openai" in self.model.lower() or "gpt" in self.model.lower():
                    litellm.openai_key = self.api_key
                elif "claude" in self.model.lower() or "anthropic" in self.model.lower():
                    litellm.anthropic_key = self.api_key
                elif "cohere" in self.model.lower():
                    litellm.cohere_key = self.api_key

            kwargs = {
                "model": self.model,
                "messages": messages,
                "api_key": self.api_key,
                # Use max_completion_tokens (newer standard) - litellm translates for older models
                "max_completion_tokens": self.max_tokens,
                # Drop unsupported params instead of raising errors
                "drop_params": True,
                # Explicitly drop temperature - many newer models (gpt-5, o-series) only support default
                # See: https://github.com/BerriAI/litellm/issues/13781
                "additional_drop_params": ["temperature"],
            }

            if self.base_url:
                kwargs["api_base"] = self.base_url

            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}

            # First attempt - try with parameters as configured
            try:
                response = await litellm.acompletion(**kwargs)
            except litellm.UnsupportedParamsError as e:
                # Retry without problematic params - fallback for edge cases
                logger.warning(f"Retrying without unsupported params: {e}")
                kwargs.pop("temperature", None)
                kwargs.pop("max_completion_tokens", None)
                kwargs["max_tokens"] = self.max_tokens  # Try legacy param
                response = await litellm.acompletion(**kwargs)

            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
            )

        except Exception as e:
            logger.error(f"Error completing LLM request: {e}")
            return LLMResponse(
                content="",
                model=self.model,
                metadata={"error": str(e)},
            )

    def _parse_json_response(self, content: str, default: Any) -> Any:
        """Parse JSON from LLM response.

        Args:
            content: Response content.
            default: Default value if parsing fails.

        Returns:
            Parsed JSON or default value.
        """
        if not content:
            return default

        try:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            if json_match:
                content = json_match.group(1)

            return json.loads(content)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON response: {content[:100]}...")
            return default

    async def summarize_code(
        self,
        code: str,
        language: str,
        file_path: Optional[str] = None,
        context: Optional[str] = None,
    ) -> CodeSummary:
        """Generate a summary of code.

        Args:
            code: Source code to summarize.
            language: Programming language.
            file_path: Optional file path for context.
            context: Optional additional context.

        Returns:
            CodeSummary with the analysis.
        """
        if not code.strip():
            return CodeSummary(summary="", language=language, file_path=file_path)

        if not self.enabled:
            return CodeSummary(
                summary="LLM service is disabled",
                language=language,
                file_path=file_path,
            )

        # Use fallback if API not available
        if not LITELLM_AVAILABLE and self.use_fallback:
            return self._fallback_summarize(code, language, file_path)

        context_text = f"Additional context: {context}" if context else ""
        prompt = self.SUMMARIZE_PROMPT.format(
            language=language,
            code=code[:8000],  # Limit code length
            context=context_text,
        )

        response = await self._complete(prompt, response_format="json")
        data = self._parse_json_response(
            response.content,
            {"summary": "", "key_components": [], "dependencies": []},
        )

        return CodeSummary(
            summary=data.get("summary", ""),
            language=language,
            file_path=file_path,
            key_components=data.get("key_components", []),
            dependencies=data.get("dependencies", []),
            metadata={"tokens_used": response.total_tokens},
        )

    def _fallback_summarize(
        self, code: str, language: str, file_path: Optional[str]
    ) -> CodeSummary:
        """Generate fallback summary using heuristics.

        Args:
            code: Source code.
            language: Programming language.
            file_path: File path.

        Returns:
            CodeSummary based on heuristics.
        """
        summary_parts = []
        key_components = []
        dependencies = []

        # Extract docstring if present
        docstring_match = re.search(r'["\']""{3}([\s\S]*?)["\']""{3}|["\']{3}([\s\S]*?)["\']{3}', code)
        if docstring_match:
            docstring = docstring_match.group(1) or docstring_match.group(2)
            summary_parts.append(docstring.strip().split("\n")[0])

        # Count classes and functions
        class_count = len(re.findall(r'\bclass\s+(\w+)', code))
        func_count = len(re.findall(r'\bdef\s+(\w+)', code))

        if class_count > 0:
            summary_parts.append(f"Contains {class_count} class(es)")
            # Extract class names
            key_components.extend(re.findall(r'\bclass\s+(\w+)', code))

        if func_count > 0:
            summary_parts.append(f"Contains {func_count} function(s)")
            # Extract function names
            key_components.extend(re.findall(r'\bdef\s+(\w+)', code)[:5])

        # Extract imports
        imports = re.findall(r'(?:from\s+(\S+)|import\s+(\S+))', code)
        for imp in imports:
            dep = imp[0] or imp[1]
            if dep and not dep.startswith('.'):
                dependencies.append(dep.split('.')[0])

        dependencies = list(set(dependencies))[:10]

        summary = "; ".join(summary_parts) if summary_parts else "Code analysis (heuristic)"

        return CodeSummary(
            summary=summary,
            language=language,
            file_path=file_path,
            key_components=key_components[:10],
            dependencies=dependencies,
            metadata={"fallback": True},
        )

    async def explain_code(
        self,
        code: str,
        language: str,
        detail_level: Literal["brief", "standard", "detailed"] = "standard",
        audience: Literal["beginner", "developer", "expert"] = "developer",
    ) -> CodeExplanation:
        """Generate an explanation of code.

        Args:
            code: Source code to explain.
            language: Programming language.
            detail_level: Level of detail in explanation.
            audience: Target audience for the explanation.

        Returns:
            CodeExplanation with the analysis.
        """
        if not code.strip():
            return CodeExplanation(
                explanation="",
                language=language,
                detail_level=detail_level,
                audience=audience,
            )

        if not self.enabled:
            return CodeExplanation(
                explanation="LLM service is disabled",
                language=language,
                detail_level=detail_level,
                audience=audience,
            )

        # Use fallback if API not available
        if not LITELLM_AVAILABLE and self.use_fallback:
            return self._fallback_explain(code, language, detail_level, audience)

        prompt = self.EXPLAIN_PROMPT.format(
            language=language,
            code=code[:8000],
            detail_level=detail_level,
            audience=audience,
        )

        response = await self._complete(prompt, response_format="json")
        data = self._parse_json_response(
            response.content,
            {"explanation": "", "concepts": []},
        )

        return CodeExplanation(
            explanation=data.get("explanation", ""),
            language=language,
            detail_level=detail_level,
            audience=audience,
            concepts=data.get("concepts", []),
            metadata={"tokens_used": response.total_tokens},
        )

    def _fallback_explain(
        self,
        code: str,
        language: str,
        detail_level: str,
        audience: str,
    ) -> CodeExplanation:
        """Generate fallback explanation using heuristics.

        Args:
            code: Source code.
            language: Programming language.
            detail_level: Detail level.
            audience: Target audience.

        Returns:
            CodeExplanation based on heuristics.
        """
        concepts = []
        explanation_parts = []

        # Detect common patterns
        if "class " in code:
            concepts.append("object-oriented programming")
            explanation_parts.append("This code defines one or more classes")

        if "async " in code or "await " in code:
            concepts.append("asynchronous programming")
            explanation_parts.append("Uses async/await for asynchronous operations")

        if "lambda " in code:
            concepts.append("lambda functions")

        if "[" in code and "for " in code and "]" in code:
            concepts.append("list comprehension")

        if "try:" in code or "except" in code:
            concepts.append("exception handling")

        if "@" in code:
            concepts.append("decorators")

        explanation = "; ".join(explanation_parts) if explanation_parts else "Code structure analysis (heuristic)"

        return CodeExplanation(
            explanation=explanation,
            language=language,
            detail_level=detail_level,
            audience=audience,
            concepts=concepts,
            metadata={"fallback": True},
        )

    async def classify_code(
        self,
        code: str,
        language: str,
    ) -> CodeClassification:
        """Classify code into categories.

        Args:
            code: Source code to classify.
            language: Programming language.

        Returns:
            CodeClassification with the analysis.
        """
        if not code.strip():
            return CodeClassification(
                primary_category="unknown",
                categories=[],
                confidence=0.0,
            )

        if not self.enabled:
            return CodeClassification(
                primary_category="unknown",
                categories=[],
                confidence=0.0,
            )

        # Use fallback if API not available
        if not LITELLM_AVAILABLE and self.use_fallback:
            return self._fallback_classify(code, language)

        prompt = self.CLASSIFY_PROMPT.format(
            language=language,
            code=code[:8000],
            categories=", ".join(CODE_CATEGORIES),
        )

        response = await self._complete(prompt, response_format="json")
        data = self._parse_json_response(
            response.content,
            {"primary_category": "unknown", "categories": [], "confidence": 0.0, "tags": []},
        )

        return CodeClassification(
            primary_category=data.get("primary_category", "unknown"),
            categories=data.get("categories", []),
            confidence=data.get("confidence", 0.0),
            tags=data.get("tags", []),
            metadata={"tokens_used": response.total_tokens},
        )

    def _fallback_classify(self, code: str, language: str) -> CodeClassification:
        """Classify code using heuristics.

        Args:
            code: Source code.
            language: Programming language.

        Returns:
            CodeClassification based on heuristics.
        """
        categories = []
        tags = []
        code_lower = code.lower()

        # Pattern-based classification
        patterns = {
            "controller": ["controller", "handler", "route", "@get", "@post", "@put", "@delete"],
            "service": ["service", "manager", "provider"],
            "repository": ["repository", "repo", "dao", "storage"],
            "model": ["model", "entity", "schema", "dataclass", "@dataclass"],
            "test": ["test_", "assert", "pytest", "unittest", "mock"],
            "utility": ["util", "helper", "tool"],
            "configuration": ["config", "settings", "environment"],
            "middleware": ["middleware", "interceptor"],
            "validator": ["validator", "validate", "validation"],
            "parser": ["parser", "parse", "tokenize"],
            "factory": ["factory", "create", "build"],
            "api_endpoint": ["@app.route", "@router", "endpoint", "api"],
        }

        for category, keywords in patterns.items():
            if any(kw in code_lower for kw in keywords):
                categories.append(category)

        # Extract tags
        if "async " in code:
            tags.append("async")
        if "http" in code_lower:
            tags.append("http")
        if "sql" in code_lower or "query" in code_lower:
            tags.append("database")

        primary = categories[0] if categories else "utility"
        confidence = min(0.3 + 0.1 * len(categories), 0.8) if categories else 0.3

        return CodeClassification(
            primary_category=primary,
            categories=categories,
            confidence=confidence,
            tags=tags,
            metadata={"fallback": True},
        )

    async def suggest_improvements(
        self,
        code: str,
        language: str,
    ) -> list[QualitySuggestion]:
        """Generate code improvement suggestions.

        Args:
            code: Source code to analyze.
            language: Programming language.

        Returns:
            List of QualitySuggestion objects.
        """
        if not code.strip():
            return []

        if not self.enabled:
            return []

        # Use fallback if API not available
        if not LITELLM_AVAILABLE and self.use_fallback:
            return self._fallback_suggest(code, language)

        prompt = self.IMPROVE_PROMPT.format(
            language=language,
            code=code[:8000],
        )

        response = await self._complete(prompt, response_format="json")

        # Use fallback if API call failed
        if not response.content and self.use_fallback:
            return self._fallback_suggest(code, language)

        data = self._parse_json_response(response.content, [])

        suggestions = []
        for item in data:
            if isinstance(item, dict):
                suggestions.append(QualitySuggestion(
                    suggestion=item.get("suggestion", ""),
                    category=item.get("category", "best_practices"),
                    severity=item.get("severity", "low"),
                    original_code=item.get("original_code"),
                    suggested_code=item.get("suggested_code"),
                ))

        # Use fallback if no suggestions from API
        if not suggestions and self.use_fallback:
            return self._fallback_suggest(code, language)

        return suggestions

    def _fallback_suggest(self, code: str, language: str) -> list[QualitySuggestion]:
        """Generate fallback suggestions using heuristics.

        Args:
            code: Source code.
            language: Programming language.

        Returns:
            List of suggestions based on heuristics.
        """
        suggestions = []

        # Check for common issues
        if len(code.split("\n")) > 100:
            suggestions.append(QualitySuggestion(
                suggestion="Consider breaking this file into smaller modules",
                category="maintainability",
                severity="medium",
            ))

        # Check for single-letter variable names
        if re.search(r'\b[a-z]\s*=', code):
            suggestions.append(QualitySuggestion(
                suggestion="Use descriptive variable names instead of single letters",
                category="naming",
                severity="low",
            ))

        # Check for missing docstrings
        if "def " in code and '"""' not in code and "'''" not in code:
            suggestions.append(QualitySuggestion(
                suggestion="Add docstrings to functions and classes",
                category="documentation",
                severity="medium",
            ))

        # Check for broad exception handling
        if "except:" in code or "except Exception:" in code:
            suggestions.append(QualitySuggestion(
                suggestion="Avoid broad exception handling; catch specific exceptions",
                category="best_practices",
                severity="medium",
            ))

        return suggestions

    async def generate_docstring(
        self,
        code: str,
        language: str,
        style: Literal["google", "numpy", "sphinx", "jsdoc"] = "google",
    ) -> GeneratedDocstring:
        """Generate a docstring for code.

        Args:
            code: Source code (function or class).
            language: Programming language.
            style: Docstring style to use.

        Returns:
            GeneratedDocstring with the result.
        """
        if not code.strip():
            return GeneratedDocstring(docstring="", style=style)

        if not self.enabled:
            return GeneratedDocstring(
                docstring="",
                style=style,
                metadata={"disabled": True},
            )

        # Use fallback if API not available
        if not LITELLM_AVAILABLE and self.use_fallback:
            return self._fallback_docstring(code, language, style)

        prompt = self.DOCSTRING_PROMPT.format(
            language=language,
            code=code[:4000],
            style=style,
        )

        response = await self._complete(prompt, response_format="json")
        data = self._parse_json_response(
            response.content,
            {"docstring": "", "parameters": [], "returns": None, "raises": [], "examples": []},
        )

        return GeneratedDocstring(
            docstring=data.get("docstring", ""),
            style=style,
            parameters=data.get("parameters", []),
            returns=data.get("returns"),
            raises=data.get("raises", []),
            examples=data.get("examples", []),
            metadata={"tokens_used": response.total_tokens},
        )

    def _fallback_docstring(
        self, code: str, language: str, style: str
    ) -> GeneratedDocstring:
        """Generate fallback docstring using heuristics.

        Args:
            code: Source code.
            language: Programming language.
            style: Docstring style.

        Returns:
            GeneratedDocstring based on heuristics.
        """
        parameters = []
        returns = None

        # Extract function signature for Python
        func_match = re.search(r'def\s+(\w+)\s*\(([^)]*)\)', code)
        if func_match:
            func_name = func_match.group(1)
            params_str = func_match.group(2)

            # Parse parameters
            if params_str.strip():
                for param in params_str.split(","):
                    param = param.strip()
                    if param and param != "self" and param != "cls":
                        param_name = param.split(":")[0].split("=")[0].strip()
                        parameters.append({
                            "name": param_name,
                            "type": "Any",
                            "description": f"The {param_name} parameter",
                        })

            # Check for return
            if "->" in code:
                returns = "The result of the operation"

            # Generate docstring based on style
            if style == "google":
                docstring = f'"""Brief description of {func_name}.\n\n'
                if parameters:
                    docstring += "Args:\n"
                    for p in parameters:
                        docstring += f"    {p['name']}: {p['description']}\n"
                if returns:
                    docstring += f"\nReturns:\n    {returns}\n"
                docstring += '"""'
            else:
                docstring = f'"""{func_name} function."""'

            return GeneratedDocstring(
                docstring=docstring,
                style=style,
                parameters=parameters,
                returns=returns,
                metadata={"fallback": True},
            )

        return GeneratedDocstring(
            docstring='"""TODO: Add documentation."""',
            style=style,
            metadata={"fallback": True},
        )

    async def analyze_symbols(
        self,
        symbols: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Analyze multiple symbols and generate summaries.

        Args:
            symbols: List of symbol dictionaries.

        Returns:
            Dictionary with analysis results.
        """
        summaries = {}

        for symbol in symbols:
            name = symbol.get("name", "")
            symbol_type = symbol.get("symbol_type", "")
            qualified_name = symbol.get("qualified_name", name)

            # Generate brief description based on naming
            description = self._analyze_symbol_name(name, symbol_type)
            summaries[qualified_name] = description

        return {
            "summaries": summaries,
            "total_analyzed": len(symbols),
        }

    def _analyze_symbol_name(self, name: str, symbol_type: str) -> str:
        """Analyze a symbol name and generate description.

        Args:
            name: Symbol name.
            symbol_type: Type of symbol.

        Returns:
            Brief description.
        """
        # Common naming patterns
        patterns = {
            r"^get_?": "Retrieves",
            r"^set_?": "Sets",
            r"^is_?": "Checks if",
            r"^has_?": "Checks if has",
            r"^can_?": "Checks if can",
            r"^create_?": "Creates",
            r"^delete_?": "Deletes",
            r"^update_?": "Updates",
            r"^find_?": "Finds",
            r"^search_?": "Searches for",
            r"^validate_?": "Validates",
            r"^parse_?": "Parses",
            r"^process_?": "Processes",
            r"^handle_?": "Handles",
            r"^on_?": "Event handler for",
        }

        for pattern, prefix in patterns.items():
            if re.match(pattern, name, re.IGNORECASE):
                rest = re.sub(pattern, "", name, flags=re.IGNORECASE)
                rest = re.sub(r"_", " ", rest)
                return f"{prefix} {rest}"

        # Default description
        nice_name = re.sub(r"_", " ", name)
        return f"{symbol_type.capitalize()} {nice_name}"

    async def generate_module_summary(
        self,
        code: str,
        language: str,
        file_path: str,
    ) -> CodeSummary:
        """Generate a summary for a complete module/file.

        Args:
            code: Module source code.
            language: Programming language.
            file_path: Module file path.

        Returns:
            CodeSummary with module analysis.
        """
        return await self.summarize_code(code, language, file_path)
