"""llms.txt generator for repository context.

Generates compact repository summaries following the llms.txt standard.
See: https://llmstxt.org/

Target: <2000 tokens for quick context loading.
"""

import re
from typing import Optional

from .parser import Parser
from .models import Document


class LlmsTxtGenerator:
    """Generate llms.txt format summaries for repositories."""

    # Target token limit for llms.txt
    MAX_TOKENS = 2000

    def __init__(self):
        self.parser = Parser()

    def generate(
        self,
        documents: list,
        library_id: str,
        description: Optional[str] = None,
        include_api: bool = True,
        include_quickstart: bool = True
    ) -> str:
        """
        Generate llms.txt format summary for a repository.

        Args:
            documents: List of Document objects from the repository
            library_id: Repository identifier (e.g., /owner/repo)
            description: Optional project description override
            include_api: Include API overview section
            include_quickstart: Include getting started section

        Returns:
            Markdown-formatted llms.txt content
        """
        output = []

        # Extract project name from library_id
        project_name = library_id.split("/")[-1] if "/" in library_id else library_id

        # Find README and extract description
        readme = self._find_readme(documents)
        if not description and readme:
            description = self._extract_description(readme.content)

        # Header section
        output.append(f"# {project_name}")
        output.append("")
        if description:
            output.append(f"> {description}")
            output.append("")

        # Key files section
        key_files = self._identify_key_files(documents)
        if key_files:
            output.append("## Key Files")
            output.append("")
            for path, desc in key_files:
                output.append(f"- `{path}`: {desc}")
            output.append("")

        # Getting Started section
        if include_quickstart and readme:
            quickstart = self._extract_quickstart(readme.content)
            if quickstart:
                output.append("## Getting Started")
                output.append("")
                output.append(quickstart)
                output.append("")

        # API Overview section
        if include_api:
            api_overview = self._extract_api_overview(documents)
            if api_overview:
                output.append("## API Overview")
                output.append("")
                output.append(api_overview)
                output.append("")

        # Documentation links
        doc_links = self._generate_doc_links(documents)
        if doc_links:
            output.append("## Documentation")
            output.append("")
            for title, path in doc_links:
                output.append(f"- [{title}]({path})")
            output.append("")

        # Ensure we're under token limit
        result = "\n".join(output)
        tokens = self.parser.count_tokens(result)

        if tokens > self.MAX_TOKENS:
            result = self._truncate_to_limit(result)

        return result

    def _find_readme(self, documents: list) -> Optional[Document]:
        """Find the main README file."""
        readme_patterns = [
            "README.md", "readme.md", "README.rst", "readme.rst",
            "README.txt", "readme.txt", "README", "readme"
        ]

        for pattern in readme_patterns:
            for doc in documents:
                if doc.file_path.lower().endswith(pattern.lower()):
                    # Prefer root-level README
                    if "/" not in doc.file_path or doc.file_path.count("/") == 0:
                        return doc

        # Fall back to any README
        for doc in documents:
            if "readme" in doc.file_path.lower():
                return doc

        return None

    def _extract_description(self, content: str) -> str:
        """Extract project description from README content."""
        lines = content.strip().split("\n")

        # Skip title
        start_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("#"):
                start_idx = i + 1
                break

        # Find first paragraph
        description_lines = []
        in_paragraph = False

        for line in lines[start_idx:]:
            stripped = line.strip()

            # Skip badges, images, empty lines before paragraph
            if not in_paragraph:
                if not stripped or stripped.startswith("!") or stripped.startswith("[!"):
                    continue
                if stripped.startswith("#"):
                    break

            in_paragraph = True

            # End at next heading or empty line after paragraph
            if stripped.startswith("#"):
                break
            if not stripped and description_lines:
                break

            if stripped:
                description_lines.append(stripped)

        description = " ".join(description_lines)

        # Truncate to reasonable length
        if len(description) > 200:
            description = description[:197] + "..."

        return description

    def _identify_key_files(self, documents: list) -> list:
        """Identify key files and generate brief descriptions."""
        key_files = []
        seen_types = set()

        # Priority order for file types
        priority_patterns = [
            ("README", "Project overview and documentation"),
            ("CONTRIBUTING", "Contribution guidelines"),
            ("CHANGELOG", "Version history and changes"),
            ("LICENSE", "License information"),
            ("API", "API documentation"),
            ("INSTALL", "Installation instructions"),
            ("QUICKSTART", "Getting started guide"),
            ("docs/index", "Documentation index"),
            ("src/index", "Main entry point"),
            ("src/main", "Main module"),
            ("__init__", "Package initialization"),
        ]

        for pattern, default_desc in priority_patterns:
            for doc in documents:
                if pattern.lower() in doc.file_path.lower():
                    file_type = pattern.upper()
                    if file_type not in seen_types:
                        seen_types.add(file_type)
                        # Try to get a better description from the file
                        desc = self._get_file_brief(doc) or default_desc
                        key_files.append((doc.file_path, desc))
                        break

            if len(key_files) >= 6:  # Limit to top 6
                break

        return key_files

    def _get_file_brief(self, doc: Document) -> Optional[str]:
        """Get a brief description of a file from its first heading or line."""
        content = doc.content.strip()
        if not content:
            return None

        # Try to get title
        title_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            if len(title) <= 60:
                return title

        # First non-empty line that's not a badge
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped and not stripped.startswith("!") and not stripped.startswith("#"):
                if len(stripped) <= 60:
                    return stripped
                return stripped[:57] + "..."

        return None

    def _extract_quickstart(self, content: str) -> str:
        """Extract quickstart/installation section from README."""
        # Look for installation/quickstart sections
        patterns = [
            r'##?\s*(?:Quick\s*Start|Getting\s*Started|Installation|Setup)\s*\n+(.*?)(?=\n##|\Z)',
            r'##?\s*(?:Usage|Basic\s*Usage)\s*\n+(.*?)(?=\n##|\Z)',
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                section = match.group(1).strip()
                # Truncate to reasonable size
                if len(section) > 500:
                    # Try to cut at a natural point
                    section = section[:500]
                    last_newline = section.rfind("\n")
                    if last_newline > 300:
                        section = section[:last_newline]
                    section += "\n..."
                return section

        # If no section found, try to find first code block
        code_match = re.search(r'```\w*\n(.+?)```', content, re.DOTALL)
        if code_match:
            code = code_match.group(0)
            if len(code) <= 300:
                return code

        return ""

    def _extract_api_overview(self, documents: list) -> str:
        """Extract API overview from documentation."""
        api_docs = []

        # Look for API-related docs
        for doc in documents:
            path_lower = doc.file_path.lower()
            if any(term in path_lower for term in ["api", "reference", "module"]):
                api_docs.append(doc)

        if not api_docs:
            return ""

        # Get main functions/classes from API docs
        overview_items = []

        for doc in api_docs[:3]:  # Limit to top 3 API docs
            # Extract function/class definitions
            code_blocks = re.findall(r'```python\n(.*?)```', doc.content, re.DOTALL)
            for block in code_blocks[:2]:  # Limit code examples
                # Look for function/class definitions
                defs = re.findall(r'^(?:def|class)\s+(\w+)', block, re.MULTILINE)
                for name in defs[:5]:
                    if name not in overview_items and not name.startswith("_"):
                        overview_items.append(name)

        if overview_items:
            return "Key exports: " + ", ".join(f"`{item}`" for item in overview_items[:8])

        return ""

    def _generate_doc_links(self, documents: list) -> list:
        """Generate documentation links section."""
        doc_links = []
        seen_titles = set()

        # Prioritize certain doc types
        priority_docs = []
        other_docs = []

        for doc in documents:
            path_lower = doc.file_path.lower()

            # Skip non-documentation files
            if not any(ext in path_lower for ext in [".md", ".rst", ".txt"]):
                continue

            # Skip test files
            if "test" in path_lower or "spec" in path_lower:
                continue

            title = self.parser.extract_title(doc.content, doc.file_path)

            # Prioritize certain docs
            if any(term in path_lower for term in ["guide", "tutorial", "api", "reference", "usage"]):
                priority_docs.append((title, doc.file_path))
            else:
                other_docs.append((title, doc.file_path))

        # Combine with priority first
        for title, path in priority_docs + other_docs:
            if title not in seen_titles and len(doc_links) < 8:
                seen_titles.add(title)
                doc_links.append((title, path))

        return doc_links

    def _truncate_to_limit(self, content: str) -> str:
        """Truncate content to stay under token limit."""
        # Remove sections from the end until we fit
        sections = content.split("\n## ")

        while self.parser.count_tokens("\n## ".join(sections)) > self.MAX_TOKENS and len(sections) > 2:
            sections.pop()

        result = "\n## ".join(sections)

        # Final check
        if self.parser.count_tokens(result) > self.MAX_TOKENS:
            # Hard truncate
            result = result[:self.MAX_TOKENS * 4]  # Rough estimate
            result += "\n\n*[Truncated for token limit]*"

        return result
