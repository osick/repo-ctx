"""Enrichment service for enhancing code and documentation metadata.

This module provides LLM-enhanced enrichment of code and documentation,
generating improved descriptions, tags, search text, and semantic metadata.
"""

import hashlib
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from repo_ctx.services.base import BaseService, ServiceContext
from repo_ctx.services.llm import (
    LLMService,
    CodeSummary,
    CODE_CATEGORIES,
)
from repo_ctx.services.chunking import ChunkingService, Chunk

logger = logging.getLogger("repo_ctx.services.enrichment")


@dataclass
class EnrichedMetadata:
    """Enriched metadata for code or documentation.

    Attributes:
        title: Short title for the content.
        description: Detailed description.
        tags: List of relevant tags.
        categories: Classification categories.
        concepts: Key programming concepts.
        keywords: Search keywords.
        quality_score: Quality score 0-1.
        search_text: Optimized text for search/embedding.
        related_topics: Related topics for linking.
        metadata: Additional metadata.
    """

    title: str
    description: str
    tags: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    quality_score: float = 0.0
    search_text: str = ""
    related_topics: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EnrichedDocument:
    """Enriched document with enhanced metadata.

    Attributes:
        id: Document identifier.
        file_path: Source file path.
        content: Document content.
        language: Programming language.
        enriched_metadata: Enhanced metadata.
        chunks: Chunked content.
        symbols: Extracted symbols.
        dependencies: Dependencies.
    """

    id: str
    file_path: str
    content: str
    language: str
    enriched_metadata: EnrichedMetadata
    chunks: list[Chunk] = field(default_factory=list)
    symbols: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


@dataclass
class EnrichedSymbol:
    """Enriched symbol with enhanced metadata.

    Attributes:
        name: Symbol name.
        qualified_name: Fully qualified name.
        symbol_type: Type (function, class, etc.).
        description: Enhanced description.
        signature: Symbol signature.
        documentation: Extracted/generated docs.
        tags: Relevant tags.
        search_text: Optimized search text.
        usage_hints: Usage suggestions.
        metadata: Additional metadata.
    """

    name: str
    qualified_name: str
    symbol_type: str
    description: str
    signature: Optional[str] = None
    documentation: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    search_text: str = ""
    usage_hints: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class EnrichmentService(BaseService):
    """Service for enriching code and documentation with LLM-enhanced metadata.

    Uses LLMService for intelligent enrichment and ChunkingService for
    content segmentation. Provides fallback heuristics when LLM unavailable.
    """

    # Common programming concepts for tagging
    PROGRAMMING_CONCEPTS = [
        "asynchronous",
        "concurrency",
        "threading",
        "caching",
        "validation",
        "serialization",
        "authentication",
        "authorization",
        "logging",
        "error-handling",
        "testing",
        "mocking",
        "dependency-injection",
        "orm",
        "database",
        "api",
        "rest",
        "graphql",
        "websocket",
        "streaming",
        "pagination",
        "filtering",
        "sorting",
        "encryption",
        "hashing",
        "compression",
        "file-handling",
        "networking",
        "parsing",
        "templating",
        "configuration",
    ]

    # Common design patterns
    DESIGN_PATTERNS = [
        "singleton",
        "factory",
        "builder",
        "prototype",
        "adapter",
        "decorator",
        "facade",
        "proxy",
        "observer",
        "strategy",
        "command",
        "iterator",
        "state",
        "template-method",
        "visitor",
        "mediator",
        "memento",
        "chain-of-responsibility",
        "repository",
        "unit-of-work",
        "specification",
    ]

    def __init__(
        self,
        context: ServiceContext,
        llm_service: Optional[LLMService] = None,
        chunking_service: Optional[ChunkingService] = None,
        use_llm: bool = True,
        enable_caching: bool = True,
    ) -> None:
        """Initialize the enrichment service.

        Args:
            context: ServiceContext with storage backends.
            llm_service: LLM service for AI-powered enrichment.
            chunking_service: Service for content chunking.
            use_llm: Whether to use LLM for enrichment.
            enable_caching: Whether to cache enrichment results.
        """
        super().__init__(context)
        self.llm_service = llm_service
        self.chunking_service = chunking_service or ChunkingService()
        self.use_llm = use_llm
        self.enable_caching = enable_caching
        self._cache: dict[str, EnrichedMetadata] = {}

    def _content_hash(self, content: str) -> str:
        """Generate hash for content caching."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def enrich_code(
        self,
        code: str,
        language: str,
        file_path: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> EnrichedMetadata:
        """Enrich code with enhanced metadata.

        Args:
            code: Source code to enrich.
            language: Programming language.
            file_path: Optional file path.
            context: Optional additional context.

        Returns:
            EnrichedMetadata with enhanced information.
        """
        if not code.strip():
            return EnrichedMetadata(title="", description="")

        # Check cache
        cache_key = self._content_hash(code)
        if self.enable_caching and cache_key in self._cache:
            return self._cache[cache_key]

        # Use LLM if available
        if self.use_llm and self.llm_service:
            enriched = await self._enrich_with_llm(code, language, file_path, context)
        else:
            enriched = self._enrich_with_heuristics(code, language, file_path)

        # Cache result
        if self.enable_caching:
            self._cache[cache_key] = enriched

        return enriched

    async def _enrich_with_llm(
        self,
        code: str,
        language: str,
        file_path: Optional[str],
        context: Optional[dict[str, Any]],
    ) -> EnrichedMetadata:
        """Enrich code using LLM service.

        Args:
            code: Source code.
            language: Programming language.
            file_path: File path.
            context: Additional context.

        Returns:
            EnrichedMetadata from LLM analysis.
        """
        try:
            # Get summary from LLM
            summary = await self.llm_service.summarize_code(
                code, language, file_path, str(context) if context else None
            )

            # Get classification
            classification = await self.llm_service.classify_code(code, language)

            # Generate search-optimized text
            search_text = self._generate_search_text(
                code=code,
                summary=summary.summary,
                components=summary.key_components,
                tags=classification.tags,
            )

            # Extract title
            title = self._extract_title(code, file_path, summary)

            # Calculate quality score
            quality_score = self._calculate_quality_score(code, language)

            return EnrichedMetadata(
                title=title,
                description=summary.summary,
                tags=classification.tags,
                categories=classification.categories,
                concepts=self._extract_concepts(code),
                keywords=summary.key_components + classification.tags,
                quality_score=quality_score,
                search_text=search_text,
                related_topics=self._find_related_topics(code, classification.categories),
                metadata={
                    "llm_enriched": True,
                    "dependencies": summary.dependencies,
                    "confidence": classification.confidence,
                },
            )

        except Exception as e:
            logger.warning(f"LLM enrichment failed, using heuristics: {e}")
            return self._enrich_with_heuristics(code, language, file_path)

    def _enrich_with_heuristics(
        self,
        code: str,
        language: str,
        file_path: Optional[str],
    ) -> EnrichedMetadata:
        """Enrich code using heuristic analysis.

        Args:
            code: Source code.
            language: Programming language.
            file_path: File path.

        Returns:
            EnrichedMetadata from heuristic analysis.
        """
        # Extract basic information
        title = self._extract_title_heuristic(code, file_path)
        description = self._extract_description_heuristic(code)
        tags = self._extract_tags_heuristic(code, language)
        categories = self._classify_heuristic(code)
        concepts = self._extract_concepts(code)
        keywords = self._extract_keywords_heuristic(code)
        quality_score = self._calculate_quality_score(code, language)

        # Generate search text
        search_text = self._generate_search_text(
            code=code,
            summary=description,
            components=keywords,
            tags=tags,
        )

        return EnrichedMetadata(
            title=title,
            description=description,
            tags=tags,
            categories=categories,
            concepts=concepts,
            keywords=keywords,
            quality_score=quality_score,
            search_text=search_text,
            related_topics=self._find_related_topics(code, categories),
            metadata={"heuristic_enriched": True},
        )

    def _extract_title(
        self,
        code: str,
        file_path: Optional[str],
        summary: CodeSummary,
    ) -> str:
        """Extract a title from code and summary."""
        # Try to get from first class or function
        class_match = re.search(r'class\s+(\w+)', code)
        if class_match:
            return class_match.group(1)

        func_match = re.search(r'def\s+(\w+)', code)
        if func_match:
            return func_match.group(1)

        # Use file path
        if file_path:
            return file_path.split("/")[-1].replace("_", " ").replace(".py", "").title()

        # Use first line of summary
        if summary.summary:
            return summary.summary.split(".")[0][:50]

        return "Code Module"

    def _extract_title_heuristic(
        self, code: str, file_path: Optional[str]
    ) -> str:
        """Extract title using heuristics."""
        # Check for module docstring
        docstring_match = re.search(r'^"""(.+?)"""', code, re.DOTALL)
        if docstring_match:
            first_line = docstring_match.group(1).strip().split("\n")[0]
            return first_line[:60]

        # Check for main class
        class_match = re.search(r'class\s+(\w+)', code)
        if class_match:
            return class_match.group(1)

        # Use file name
        if file_path:
            name = file_path.split("/")[-1]
            name = re.sub(r'\.\w+$', '', name)  # Remove extension
            return name.replace("_", " ").title()

        return "Code Module"

    def _extract_description_heuristic(self, code: str) -> str:
        """Extract description using heuristics."""
        # Try module docstring
        docstring_match = re.search(r'^"""([\s\S]*?)"""', code)
        if docstring_match:
            return docstring_match.group(1).strip()

        # Count elements
        class_count = len(re.findall(r'\bclass\s+\w+', code))
        func_count = len(re.findall(r'\bdef\s+\w+', code))

        parts = []
        if class_count > 0:
            parts.append(f"Contains {class_count} class(es)")
        if func_count > 0:
            parts.append(f"Contains {func_count} function(s)")

        return "; ".join(parts) if parts else "Code module"

    def _extract_tags_heuristic(self, code: str, language: str) -> list[str]:
        """Extract tags using heuristics."""
        tags = [language]
        code_lower = code.lower()

        # Check for patterns
        patterns = {
            "async": ["async ", "await ", "asyncio"],
            "api": ["api", "endpoint", "@route", "@app"],
            "database": ["sql", "query", "orm", "model"],
            "testing": ["test_", "pytest", "unittest", "mock"],
            "web": ["http", "request", "response", "flask", "fastapi", "django"],
            "cli": ["argparse", "click", "typer"],
            "data": ["pandas", "numpy", "dataframe"],
            "ml": ["sklearn", "tensorflow", "pytorch", "model"],
        }

        for tag, keywords in patterns.items():
            if any(kw in code_lower for kw in keywords):
                tags.append(tag)

        return list(set(tags))

    def _classify_heuristic(self, code: str) -> list[str]:
        """Classify code using heuristics."""
        categories = []
        code_lower = code.lower()

        for category in CODE_CATEGORIES:
            if category in code_lower:
                categories.append(category)

        # Pattern-based classification
        if re.search(r'class\s+\w+Service', code):
            categories.append("service")
        if re.search(r'class\s+\w+Repository', code):
            categories.append("repository")
        if re.search(r'class\s+\w+Controller', code):
            categories.append("controller")
        if re.search(r'@app\.route|@router\.\w+', code):
            categories.append("api_endpoint")

        return list(set(categories)) or ["utility"]

    def _extract_concepts(self, code: str) -> list[str]:
        """Extract programming concepts from code."""
        concepts = []
        code_lower = code.lower()

        # Check for concepts
        concept_patterns = {
            "asynchronous": ["async ", "await ", "asyncio"],
            "concurrency": ["thread", "multiprocessing", "concurrent"],
            "caching": ["cache", "lru_cache", "memoize"],
            "validation": ["validate", "validator", "schema"],
            "serialization": ["json", "serialize", "marshal"],
            "authentication": ["auth", "login", "token", "jwt"],
            "error-handling": ["try:", "except", "raise "],
            "logging": ["logging", "logger", "log."],
            "testing": ["test_", "assert", "mock"],
            "dependency-injection": ["inject", "container", "provider"],
            "orm": ["sqlalchemy", "django.db", "orm"],
            "api": ["api", "endpoint", "rest"],
        }

        for concept, patterns in concept_patterns.items():
            if any(p in code_lower for p in patterns):
                concepts.append(concept)

        return concepts

    def _extract_keywords_heuristic(self, code: str) -> list[str]:
        """Extract keywords from code."""
        keywords = []

        # Extract class names
        keywords.extend(re.findall(r'class\s+(\w+)', code))

        # Extract function names
        keywords.extend(re.findall(r'def\s+(\w+)', code))

        # Extract imports
        imports = re.findall(r'(?:from\s+(\S+)|import\s+(\S+))', code)
        for imp in imports:
            dep = imp[0] or imp[1]
            if dep:
                keywords.append(dep.split('.')[0])

        # Clean and deduplicate
        keywords = [k for k in keywords if len(k) > 2 and k not in ['self', 'cls']]
        return list(set(keywords))[:20]

    def _calculate_quality_score(self, code: str, language: str) -> float:
        """Calculate quality score based on heuristics."""
        score = 0.5  # Base score

        # Check for docstrings
        if '"""' in code or "'''" in code:
            score += 0.1

        # Check for type hints
        if "->" in code or ": str" in code or ": int" in code:
            score += 0.1

        # Check for error handling
        if "try:" in code and "except" in code:
            score += 0.05

        # Check for logging
        if "logging" in code or "logger" in code:
            score += 0.05

        # Penalize very long functions (heuristic)
        lines = code.split("\n")
        if len(lines) > 200:
            score -= 0.1

        # Penalize no comments
        comment_lines = len([line for line in lines if line.strip().startswith("#")])
        if comment_lines < len(lines) * 0.05:
            score -= 0.05

        return max(0.0, min(1.0, score))

    def _generate_search_text(
        self,
        code: str,
        summary: str,
        components: list[str],
        tags: list[str],
    ) -> str:
        """Generate optimized text for search/embedding.

        Args:
            code: Source code.
            summary: Code summary.
            components: Key components.
            tags: Tags.

        Returns:
            Search-optimized text.
        """
        parts = [summary]

        # Add component names
        if components:
            parts.append("Components: " + ", ".join(components))

        # Add tags
        if tags:
            parts.append("Tags: " + ", ".join(tags))

        # Add extracted docstrings
        docstrings = re.findall(r'"""([\s\S]*?)"""', code)
        for doc in docstrings[:3]:  # Limit to first 3
            clean_doc = doc.strip()
            if clean_doc and len(clean_doc) < 500:
                parts.append(clean_doc)

        return " ".join(parts)

    def _find_related_topics(
        self, code: str, categories: list[str]
    ) -> list[str]:
        """Find related topics based on code analysis."""
        related = []
        code_lower = code.lower()

        # Check design patterns
        for pattern in self.DESIGN_PATTERNS:
            if pattern.replace("-", "_") in code_lower or pattern in code_lower:
                related.append(f"pattern:{pattern}")

        # Check concepts
        for concept in self.PROGRAMMING_CONCEPTS:
            if concept.replace("-", "_") in code_lower or concept in code_lower:
                related.append(f"concept:{concept}")

        return related[:10]

    async def enrich_symbol(
        self,
        name: str,
        qualified_name: str,
        symbol_type: str,
        signature: Optional[str] = None,
        documentation: Optional[str] = None,
        code: Optional[str] = None,
        language: str = "python",
    ) -> EnrichedSymbol:
        """Enrich a code symbol with enhanced metadata.

        Args:
            name: Symbol name.
            qualified_name: Fully qualified name.
            symbol_type: Type (function, class, etc.).
            signature: Symbol signature.
            documentation: Existing documentation.
            code: Symbol source code.
            language: Programming language.

        Returns:
            EnrichedSymbol with enhanced information.
        """
        # Generate description
        description = self._generate_symbol_description(
            name, symbol_type, signature, documentation
        )

        # Extract tags
        tags = self._extract_symbol_tags(name, symbol_type, code)

        # Generate search text
        search_text = self._generate_symbol_search_text(
            name, qualified_name, symbol_type, description, tags
        )

        # Generate usage hints
        usage_hints = self._generate_usage_hints(name, symbol_type, signature)

        return EnrichedSymbol(
            name=name,
            qualified_name=qualified_name,
            symbol_type=symbol_type,
            description=description,
            signature=signature,
            documentation=documentation,
            tags=tags,
            search_text=search_text,
            usage_hints=usage_hints,
        )

    def _generate_symbol_description(
        self,
        name: str,
        symbol_type: str,
        signature: Optional[str],
        documentation: Optional[str],
    ) -> str:
        """Generate description for a symbol."""
        if documentation:
            # Use first sentence of documentation
            first_line = documentation.strip().split("\n")[0]
            if len(first_line) > 10:
                return first_line

        # Generate from name patterns
        patterns = {
            r"^get_?(.+)": "Retrieves {0}",
            r"^set_?(.+)": "Sets {0}",
            r"^is_?(.+)": "Checks if {0}",
            r"^has_?(.+)": "Checks if has {0}",
            r"^can_?(.+)": "Checks if can {0}",
            r"^create_?(.+)": "Creates {0}",
            r"^delete_?(.+)": "Deletes {0}",
            r"^remove_?(.+)": "Removes {0}",
            r"^update_?(.+)": "Updates {0}",
            r"^find_?(.+)": "Finds {0}",
            r"^search_?(.+)": "Searches for {0}",
            r"^validate_?(.+)": "Validates {0}",
            r"^parse_?(.+)": "Parses {0}",
            r"^process_?(.+)": "Processes {0}",
            r"^handle_?(.+)": "Handles {0}",
            r"^on_?(.+)": "Handler for {0} event",
            r"^to_?(.+)": "Converts to {0}",
            r"^from_?(.+)": "Creates from {0}",
            r"^load_?(.+)": "Loads {0}",
            r"^save_?(.+)": "Saves {0}",
        }

        for pattern, template in patterns.items():
            match = re.match(pattern, name, re.IGNORECASE)
            if match:
                captured = match.group(1).replace("_", " ")
                return template.format(captured)

        # Default description
        nice_name = name.replace("_", " ")
        return f"{symbol_type.capitalize()} {nice_name}"

    def _extract_symbol_tags(
        self,
        name: str,
        symbol_type: str,
        code: Optional[str],
    ) -> list[str]:
        """Extract tags for a symbol."""
        tags = [symbol_type]

        # Name-based tags
        if name.startswith("_"):
            tags.append("private")
        if name.startswith("__") and name.endswith("__"):
            tags.append("magic")
        if name.startswith("test_"):
            tags.append("test")

        # Code-based tags
        if code:
            if "async " in code:
                tags.append("async")
            if "@property" in code:
                tags.append("property")
            if "@staticmethod" in code:
                tags.append("static")
            if "@classmethod" in code:
                tags.append("classmethod")

        return list(set(tags))

    def _generate_symbol_search_text(
        self,
        name: str,
        qualified_name: str,
        symbol_type: str,
        description: str,
        tags: list[str],
    ) -> str:
        """Generate search text for a symbol."""
        parts = [
            name,
            qualified_name,
            symbol_type,
            description,
        ]
        if tags:
            parts.append("Tags: " + " ".join(tags))

        return " ".join(parts)

    def _generate_usage_hints(
        self,
        name: str,
        symbol_type: str,
        signature: Optional[str],
    ) -> list[str]:
        """Generate usage hints for a symbol."""
        hints = []

        if symbol_type == "function":
            if signature:
                hints.append(f"Call: {signature}")
            else:
                hints.append(f"Call: {name}()")

        elif symbol_type == "class":
            hints.append(f"Instantiate: {name}()")
            hints.append(f"Inherit: class MyClass({name}):")

        elif symbol_type == "method":
            if signature:
                hints.append(f"Call: instance.{signature}")
            else:
                hints.append(f"Call: instance.{name}()")

        return hints

    async def enrich_document(
        self,
        content: str,
        file_path: str,
        language: str,
        chunk_for_embedding: bool = True,
    ) -> EnrichedDocument:
        """Enrich a complete document with metadata and chunks.

        Args:
            content: Document content.
            file_path: File path.
            language: Programming language.
            chunk_for_embedding: Whether to chunk for embedding.

        Returns:
            EnrichedDocument with full enrichment.
        """
        # Generate document ID
        doc_id = hashlib.sha256(f"{file_path}:{content[:100]}".encode()).hexdigest()[:16]

        # Enrich content
        enriched_metadata = await self.enrich_code(content, language, file_path)

        # Chunk if requested
        chunks = []
        if chunk_for_embedding:
            chunks = self.chunking_service.chunk_for_embedding(
                content, file_path, max_tokens=500
            )

        # Extract dependencies
        dependencies = self._extract_dependencies(content)

        return EnrichedDocument(
            id=doc_id,
            file_path=file_path,
            content=content,
            language=language,
            enriched_metadata=enriched_metadata,
            chunks=chunks,
            dependencies=dependencies,
        )

    def _extract_dependencies(self, code: str) -> list[str]:
        """Extract dependencies from code."""
        deps = []

        # Python imports
        imports = re.findall(r'(?:from\s+(\S+)|import\s+(\S+))', code)
        for imp in imports:
            dep = imp[0] or imp[1]
            if dep and not dep.startswith('.'):
                deps.append(dep.split('.')[0])

        # JavaScript/TypeScript imports
        js_imports = re.findall(r'(?:import\s+.*?\s+from\s+["\']([^"\']+)["\'])', code)
        deps.extend(js_imports)

        # Go imports
        go_imports = re.findall(r'"([^"]+)"', code)
        deps.extend([i.split("/")[-1] for i in go_imports if "/" in i])

        return list(set(deps))

    async def batch_enrich(
        self,
        items: list[dict[str, Any]],
        item_type: str = "code",
    ) -> list[EnrichedMetadata]:
        """Enrich multiple items in batch.

        Args:
            items: List of items with 'content', 'language', 'file_path'.
            item_type: Type of items ('code' or 'symbol').

        Returns:
            List of EnrichedMetadata objects.
        """
        results = []

        for item in items:
            if item_type == "code":
                enriched = await self.enrich_code(
                    code=item.get("content", ""),
                    language=item.get("language", "python"),
                    file_path=item.get("file_path"),
                )
            else:
                symbol = await self.enrich_symbol(
                    name=item.get("name", ""),
                    qualified_name=item.get("qualified_name", ""),
                    symbol_type=item.get("symbol_type", "function"),
                    signature=item.get("signature"),
                    documentation=item.get("documentation"),
                    code=item.get("code"),
                    language=item.get("language", "python"),
                )
                enriched = EnrichedMetadata(
                    title=symbol.name,
                    description=symbol.description,
                    tags=symbol.tags,
                    search_text=symbol.search_text,
                )

            results.append(enriched)

        return results

    def clear_cache(self) -> None:
        """Clear the enrichment cache."""
        self._cache.clear()
