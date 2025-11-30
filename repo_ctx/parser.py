"""Documentation parser."""
import re
from typing import Optional, List, Dict
from markdown_it import MarkdownIt


class Parser:
    def __init__(self):
        self.md = MarkdownIt()

        # Filler phrases to remove from descriptions
        self.filler_phrases = [
            r"^This document describes?\s+",
            r"^This guide shows?\s+",
            r"^This page explains?\s+",
            r"^This section covers?\s+",
            r"^The following\s+",
            r"^In this (document|guide|page|section),?\s+",
        ]

        # Low-value code snippet patterns (installation commands, etc.)
        self.low_value_code_patterns = [
            # Package managers
            r'^\s*(pip|pip3)\s+install',
            r'^\s*npm\s+(install|i)\s',
            r'^\s*yarn\s+(add|install)',
            r'^\s*pnpm\s+(add|install)',
            r'^\s*brew\s+install',
            r'^\s*apt(-get)?\s+install',
            r'^\s*conda\s+install',
            r'^\s*poetry\s+add',
            # Docker commands
            r'^\s*docker\s+(run|pull|build|compose)',
            r'^\s*docker-compose\s+',
            # Git commands (simple ones)
            r'^\s*git\s+(clone|pull|push)\s',
            # Simple shell commands
            r'^\s*cd\s+',
            r'^\s*mkdir\s+',
            r'^\s*export\s+\w+=',
            # Virtual environment
            r'^\s*(python|python3)\s+-m\s+venv',
            r'^\s*source\s+.*activate',
            r'^\s*\.\s+.*activate',
        ]

        # High-priority document patterns (should include full content)
        self.high_priority_docs = [
            'readme.md', 'readme.rst', 'readme.txt', 'readme',
            'index.md', 'index.rst',
            'overview.md', 'introduction.md', 'getting-started.md',
            'architecture.md', 'design.md',
        ]

        # Low-priority document patterns (minimal content)
        self.low_priority_docs = [
            'install', 'installation', 'setup',
            'contributing', 'code_of_conduct', 'codeofconduct',
            'security', 'support',
        ]
    
    def should_include_file(self, path: str, config: Optional[dict] = None) -> bool:
        """Check if file should be included based on config."""
        # Default: include markdown and text files
        if not any(path.endswith(ext) for ext in ['.md', '.rst', '.txt', '.markdown']):
            return False
        
        if not config:
            return True
        
        # Check exclude patterns
        exclude_folders = config.get("excludeFolders", [])
        for folder in exclude_folders:
            if f"/{folder}/" in path or path.startswith(f"{folder}/"):
                return False
        
        exclude_files = config.get("excludeFiles", [])
        if any(path.endswith(f) for f in exclude_files):
            return False
        
        # Check include patterns
        folders = config.get("folders", [])
        if folders:
            return any(f"/{folder}/" in path or path.startswith(f"{folder}/") for folder in folders)
        
        return True

    def get_document_priority(self, file_path: str) -> str:
        """
        Classify document priority based on file path.

        Returns:
            'high': README, index, architecture docs - include full content
            'normal': API docs, guides - standard processing
            'low': Installation, contributing - minimal content
        """
        filename = file_path.lower().split('/')[-1]
        path_lower = file_path.lower()

        # Check high priority
        for pattern in self.high_priority_docs:
            if filename == pattern or filename.startswith(pattern.replace('.md', '')):
                return 'high'

        # Check low priority
        for pattern in self.low_priority_docs:
            if pattern in filename:
                return 'low'

        # API and reference docs are normal priority
        if '/api/' in path_lower or '/reference/' in path_lower:
            return 'normal'

        return 'normal'

    def is_low_value_snippet(self, code: str, language: str) -> bool:
        """
        Check if a code snippet is low-value (installation commands, etc.).

        Args:
            code: The code content
            language: The language identifier (bash, shell, etc.)

        Returns:
            True if this is a low-value snippet that should be filtered
        """
        # Only filter shell/bash snippets
        if language not in ('bash', 'shell', 'sh', 'console', 'text', ''):
            return False

        # Check each line against low-value patterns
        lines = code.strip().split('\n')

        # If it's a one-liner or two-liner, check if it's a simple command
        if len(lines) <= 2:
            for line in lines:
                line = line.strip()
                # Skip comment lines and empty lines
                if not line or line.startswith('#'):
                    continue
                # Remove common prompt prefixes
                line = re.sub(r'^[\$\>]\s*', '', line)

                for pattern in self.low_value_code_patterns:
                    if re.match(pattern, line, re.IGNORECASE):
                        return True

        return False

    def filter_valuable_snippets(self, snippets: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Filter code snippets to keep only valuable ones.

        Args:
            snippets: List of snippet dicts with 'context', 'language', 'code'

        Returns:
            Filtered list with low-value snippets removed
        """
        return [s for s in snippets if not self.is_low_value_snippet(s['code'], s['language'])]

    def extract_full_content(self, content: str) -> str:
        """
        Extract full content from a document, cleaning up noise.

        Used for high-priority documents like README.

        Args:
            content: Full markdown content

        Returns:
            Cleaned content with badges and noise removed
        """
        lines = content.split('\n')
        cleaned_lines = []
        skip_badges = True  # Skip badge section at top

        for line in lines:
            # Skip badge lines (markdown images at top of file)
            if skip_badges:
                if re.match(r'^\s*(\[!\[|<img|<a href=.*badge)', line):
                    continue
                elif line.strip() == '':
                    continue
                else:
                    skip_badges = False

            # Skip standalone badge lines anywhere
            if re.match(r'^\s*\[!\[.*\]\(.*\)\]\(.*\)\s*$', line):
                continue

            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def parse_markdown(self, content: str) -> str:
        """Parse markdown and return formatted content."""
        # For MVP, just return content as-is
        # Could enhance with better formatting later
        return content
    
    def extract_snippets(self, content: str) -> list[dict]:
        """Extract code snippets from markdown."""
        snippets = []
        # Match code blocks: ```language\ncode\n```
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            language = match.group(1) or "text"
            code = match.group(2).strip()
            snippets.append({
                "language": language,
                "code": code
            })
        
        return snippets
    
    def count_tokens(self, content: str) -> int:
        """Rough token count estimation."""
        # Simple estimation: ~4 chars per token
        return len(content) // 4

    def extract_title(self, content: str, fallback_filename: str = "") -> str:
        """
        Extract title from markdown content.

        Args:
            content: Markdown content
            fallback_filename: Filename to use if no heading found

        Returns:
            Extracted title or filename without extension
        """
        # Look for first H1 or H2
        h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()

        h2_match = re.search(r'^##\s+(.+)$', content, re.MULTILINE)
        if h2_match:
            return h2_match.group(1).strip()

        # Fallback to filename without extension
        if fallback_filename:
            return re.sub(r'\.(md|markdown|rst|txt)$', '', fallback_filename.split('/')[-1])

        return "Documentation"

    def extract_description(self, content: str, max_sentences: int = 3) -> str:
        """
        Extract brief description from content.

        Args:
            content: Markdown content
            max_sentences: Maximum number of sentences to include

        Returns:
            Brief description (2-3 sentences max)
        """
        # Remove code blocks first
        content_no_code = re.sub(r'```.*?```', '', content, flags=re.DOTALL)

        # Find first paragraph after title
        # Skip the title line(s)
        lines = content_no_code.split('\n')
        paragraph_lines = []
        found_title = False

        for line in lines:
            line = line.strip()

            # Skip title markers
            if line.startswith('#'):
                found_title = True
                continue

            # Skip empty lines until we find content
            if not line:
                if paragraph_lines:  # Stop at first empty line after content
                    break
                continue

            # After title, collect paragraph text
            if found_title:
                paragraph_lines.append(line)
            elif not line.startswith('#'):  # Content before any title
                paragraph_lines.append(line)

        if not paragraph_lines:
            return ""

        # Join and split into sentences
        paragraph = ' '.join(paragraph_lines)

        # Remove filler phrases
        for pattern in self.filler_phrases:
            paragraph = re.sub(pattern, '', paragraph, flags=re.IGNORECASE)

        # Split into sentences (simple approach)
        sentences = re.split(r'[.!?]+\s+', paragraph)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Take first N sentences
        description = '. '.join(sentences[:max_sentences])
        if description and not description.endswith('.'):
            description += '.'

        return description

    def extract_snippets_with_context(self, content: str) -> List[Dict[str, str]]:
        """
        Extract code snippets with surrounding context.

        Args:
            content: Markdown content

        Returns:
            List of dicts with 'context', 'language', and 'code'
        """
        snippets = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            # Find code block start
            code_match = re.match(r'^```(\w+)?', line)
            if code_match:
                language = code_match.group(1) or "text"

                # Extract code until closing ```
                code_lines = []
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() == '```':
                        break
                    code_lines.append(lines[j])

                code = '\n'.join(code_lines).strip()

                # Find context: look backwards for heading or descriptive text
                context = "Example usage"
                for k in range(i - 1, max(0, i - 5), -1):
                    prev_line = lines[k].strip()

                    # Check for H3/H4 heading
                    heading_match = re.match(r'^###?\s+(.+)$', prev_line)
                    if heading_match:
                        context = heading_match.group(1).strip()
                        break

                    # Check for descriptive sentence (ends with : or mentions code)
                    if prev_line and (prev_line.endswith(':') or
                                     any(word in prev_line.lower() for word in ['example', 'usage', 'code', 'following'])):
                        context = prev_line.rstrip(':')
                        break

                snippets.append({
                    "context": context,
                    "language": language,
                    "code": code
                })

        return snippets

    def should_exclude_file(self, path: str) -> bool:
        """
        Check if file should be excluded based on quality filtering rules.

        Args:
            path: File path

        Returns:
            True if file should be excluded
        """
        path_lower = path.lower()

        # Exclude changelogs
        changelog_patterns = ['changelog', 'history', 'releases', 'news']
        if any(pattern in path_lower for pattern in changelog_patterns):
            return True

        # Exclude auto-generated files
        autogen_patterns = [
            'package-lock.json', 'yarn.lock', 'go.sum', 'gemfile.lock',
            'poetry.lock', 'pipfile.lock', 'pnpm-lock'
        ]
        if any(pattern in path_lower for pattern in autogen_patterns):
            return True

        # Exclude license files (unless in docs folder)
        if 'license' in path_lower or 'copying' in path_lower:
            if '/docs/' not in path_lower and '/doc/' not in path_lower:
                return True

        return False

    def calculate_quality_score(self, content: str, file_path: str) -> float:
        """
        Calculate quality score for a documentation file (0-100).

        Scoring factors:
        - File location (README, docs/ folder)
        - Content quality (has code, good length, structure)
        - Completeness (title, description, examples)

        Args:
            content: Document content
            file_path: File path

        Returns:
            Quality score from 0 to 100
        """
        score = 0.0
        path_lower = file_path.lower()
        filename = path_lower.split('/')[-1]

        # File location weight (0-30 points)
        if filename in ['readme.md', 'index.md', 'readme.rst']:
            score += 30
        elif '/docs/' in path_lower or '/doc/' in path_lower:
            score += 25
        elif '/' not in file_path:  # Root level
            score += 20
        else:  # Subdirectories
            score += 15

        # Content quality (0-30 points)
        content_length = len(content)

        # Has code examples
        snippets = self.extract_snippets(content)
        if snippets:
            score += 15

        # Has headings/structure
        if re.search(r'^#{1,3}\s+', content, re.MULTILINE):
            score += 10

        # Appropriate length (500-3000 chars ideal for docs)
        if 500 <= content_length <= 3000:
            score += 5
        elif content_length < 200:
            score -= 10  # Too short
        elif content_length > 10000:
            score -= 5   # Very long (might be generated)

        # Document completeness (0-20 points)
        title = self.extract_title(content, file_path)
        if title and title != "Documentation":
            score += 5

        description = self.extract_description(content)
        if description:
            score += 5

        if snippets:
            score += 10

        # File type (0-20 points)
        if file_path.endswith('.md') or file_path.endswith('.markdown'):
            score += 20
        elif file_path.endswith('.rst'):
            score += 15
        elif file_path.endswith('.txt'):
            score += 10

        # Ensure score is in range 0-100
        return max(0.0, min(100.0, score))

    def classify_document(self, content: str, file_path: str) -> str:
        """
        Classify document type based on content patterns.

        Types:
        - 'tutorial': Step-by-step guides with examples
        - 'reference': API docs, technical specifications
        - 'guide': Conceptual explanations
        - 'overview': README, index, high-level introductions

        Args:
            content: Document content
            file_path: File path

        Returns:
            Document type string
        """
        content_lower = content.lower()
        path_lower = file_path.lower()
        filename = path_lower.split('/')[-1]

        # Check filename patterns first
        if filename in ['readme.md', 'readme.rst', 'readme.txt']:
            return "overview"

        if filename in ['index.md', 'index.rst', 'overview.md']:
            return "overview"

        # Tutorial patterns
        tutorial_keywords = [
            'tutorial', 'getting started', 'quick start', 'walkthrough',
            'step 1', 'step 2', 'how to', 'guide to', 'first,', 'then,', 'next,'
        ]
        tutorial_score = sum(1 for kw in tutorial_keywords if kw in content_lower)

        # Reference patterns
        reference_keywords = [
            'api reference', 'api documentation', 'specification',
            'parameters:', 'returns:', 'arguments:', 'function:',
            'method:', 'class:', 'interface:', 'type:'
        ]
        reference_score = sum(1 for kw in reference_keywords if kw in content_lower)

        # Guide patterns
        guide_keywords = [
            'understanding', 'concepts', 'architecture', 'design',
            'overview', 'introduction to', 'explains', 'best practices'
        ]
        guide_score = sum(1 for kw in guide_keywords if kw in content_lower)

        # Determine type based on scores
        scores = {
            'tutorial': tutorial_score,
            'reference': reference_score,
            'guide': guide_score
        }

        # If no clear winner, default to guide
        max_score = max(scores.values())
        if max_score == 0:
            return "guide"

        # Return highest scoring type
        for doc_type, score in scores.items():
            if score == max_score:
                return doc_type

        return "guide"

    def extract_metadata(self, content: str, file_path: str) -> dict:
        """
        Extract comprehensive metadata from document.

        Args:
            content: Document content
            file_path: File path

        Returns:
            Dictionary with metadata fields:
            - quality_score: 0-100 quality score
            - document_type: tutorial/reference/guide/overview
            - reading_time: Estimated minutes to read
            - snippet_count: Number of code examples
            - has_code_examples: Boolean
            - word_count: Approximate word count
        """
        # Calculate quality and classification
        quality_score = self.calculate_quality_score(content, file_path)
        document_type = self.classify_document(content, file_path)

        # Extract snippets
        snippets = self.extract_snippets(content)
        snippet_count = len(snippets)

        # Calculate word count and reading time
        # Remove code blocks for word count
        content_no_code = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        words = content_no_code.split()
        word_count = len(words)

        # Reading time: average 200 words per minute
        reading_time = max(1, round(word_count / 200))

        return {
            "quality_score": round(quality_score, 1),
            "document_type": document_type,
            "reading_time": reading_time,
            "snippet_count": snippet_count,
            "has_code_examples": snippet_count > 0,
            "word_count": word_count
        }

    def format_for_llm(self, documents: list, library_id: str, include_examples: bool = False) -> str:
        """
        Format documents for LLM consumption with priority-based content handling.

        High-priority docs (README, architecture): Full content with badge/noise removal
        Normal docs (API, guides): Structured extraction with filtered code snippets
        Low-priority docs (install, contributing): Skip or minimal content

        Args:
            documents: List of Document objects
            library_id: Library identifier
            include_examples: If True, include all code examples without filtering

        Returns:
            Formatted markdown optimized for LLM parsing
        """
        output = []

        # Sort documents by priority (high first)
        def priority_sort_key(doc):
            p = self.get_document_priority(doc.file_path)
            return {'high': 0, 'normal': 1, 'low': 2}.get(p, 1)

        sorted_docs = sorted(documents, key=priority_sort_key)

        for doc in sorted_docs:
            # Skip excluded files
            if self.should_exclude_file(doc.file_path):
                continue

            # Skip very short files (likely empty or stub)
            if len(doc.content.strip()) < 100:
                continue

            priority = self.get_document_priority(doc.file_path)
            title = self.extract_title(doc.content, doc.file_path)

            if priority == 'high':
                # High priority: Include full content with noise removed
                full_content = self.extract_full_content(doc.content)

                # Filter out low-value code snippets unless include_examples is set
                if not include_examples:
                    def replace_low_value_blocks(match):
                        lang = match.group(1) or ''
                        code = match.group(2)
                        if self.is_low_value_snippet(code, lang):
                            return ''  # Remove low-value snippets
                        return match.group(0)  # Keep valuable ones

                    full_content = re.sub(
                        r'```(\w*)\n(.*?)```',
                        replace_low_value_blocks,
                        full_content,
                        flags=re.DOTALL
                    )

                # Clean up multiple consecutive blank lines
                full_content = re.sub(r'\n{3,}', '\n\n', full_content)

                output.append(f"# {doc.file_path}\n\n")
                output.append(full_content.strip())
                output.append("\n\n---\n\n")

            elif priority == 'normal':
                # Normal priority: Structured extraction with filtered snippets
                description = self.extract_description(doc.content, max_sentences=5)
                snippets = self.extract_snippets_with_context(doc.content)

                # Filter snippets unless include_examples is set
                if include_examples:
                    valuable_snippets = snippets
                else:
                    valuable_snippets = self.filter_valuable_snippets(snippets)

                # Skip if no useful content
                if not description and not valuable_snippets:
                    continue

                output.append(f"# {doc.file_path} - {title}\n\n")

                if description:
                    output.append(f"{description}\n\n")

                if valuable_snippets:
                    output.append("## Code Examples\n\n")
                    for snippet in valuable_snippets[:5]:  # Limit to 5 examples
                        output.append(f"### {snippet['context']}\n")
                        output.append(f"```{snippet['language']}\n")
                        output.append(snippet['code'])
                        output.append("\n```\n\n")

                output.append("---\n\n")

            else:  # low priority
                # Low priority: Skip entirely or include just a brief note
                # For now, skip low-priority docs to save tokens
                continue

        return "".join(output)

    def format_summary_for_llm(self, documents: list, library_id: str) -> str:
        """
        Format documents as a compact summary for LLM consumption.

        Includes only:
        - Document titles
        - Short descriptions (1-2 sentences)
        - List of key sections/headings

        Designed for SUMMARY output mode (~500-2000 tokens).

        Args:
            documents: List of Document objects
            library_id: Library identifier

        Returns:
            Compact summary markdown
        """
        output = [f"# Summary: {library_id}\n\n"]

        # Sort by quality score
        scored_docs = []
        for doc in documents:
            if self.should_exclude_file(doc.file_path):
                continue
            if len(doc.content.strip()) < 100:
                continue
            quality = self.calculate_quality_score(doc.content, doc.file_path)
            scored_docs.append((doc, quality))

        scored_docs.sort(key=lambda x: x[1], reverse=True)

        for doc, quality in scored_docs[:10]:  # Limit to top 10 docs
            title = self.extract_title(doc.content, doc.file_path)
            doc_type = self.classify_document(doc.content, doc.file_path)

            # Get first 1-2 sentences as description
            description = self.extract_description(doc.content, max_sentences=2)

            # Extract main headings (## level)
            headings = re.findall(r'^##\s+(.+?)$', doc.content, re.MULTILINE)
            headings = [h.strip() for h in headings[:5]]  # Limit to 5 headings

            output.append(f"## {title}\n")
            output.append(f"*{doc.file_path}* ({doc_type}, score: {quality:.0f})\n\n")

            if description:
                output.append(f"{description}\n\n")

            if headings:
                output.append("Sections: " + ", ".join(headings) + "\n")

            output.append("\n")

        # Add note about truncation
        total_docs = len([d for d in documents if not self.should_exclude_file(d.file_path)])
        if total_docs > 10:
            output.append(f"\n---\n*Showing top 10 of {total_docs} documents. Use output_mode='standard' for full content.*\n")

        return "".join(output)

    def calculate_relevance_score(self, content: str, file_path: str, query: str) -> float:
        """
        Calculate relevance score for a document given a query (0-100).

        Scoring factors:
        - Keyword matches in title (highest weight)
        - Keyword matches in headings
        - Keyword matches in content
        - Proximity of keywords

        Args:
            content: Document content
            file_path: File path
            query: Search query string

        Returns:
            Relevance score from 0 to 100
        """
        if not query:
            return 0.0

        score = 0.0
        query_lower = query.lower()

        # Extract keywords from query (simple tokenization)
        keywords = set(word.strip() for word in re.split(r'[\s,;:]+', query_lower) if len(word.strip()) > 2)

        if not keywords:
            return 0.0

        title = self.extract_title(content, file_path).lower()
        path_lower = file_path.lower()
        content_lower = content.lower()

        # Title matches (0-40 points)
        title_matches = sum(1 for kw in keywords if kw in title)
        if title_matches:
            score += min(40, title_matches * 20)  # 20 points per keyword match in title

        # File path matches (0-20 points)
        path_matches = sum(1 for kw in keywords if kw in path_lower)
        if path_matches:
            score += min(20, path_matches * 10)  # 10 points per keyword match in path

        # Heading matches (0-20 points)
        headings = ' '.join(re.findall(r'^#{1,3}\s+(.+?)$', content, re.MULTILINE)).lower()
        heading_matches = sum(1 for kw in keywords if kw in headings)
        if heading_matches:
            score += min(20, heading_matches * 10)  # 10 points per keyword match in headings

        # Content matches (0-20 points)
        content_matches = sum(1 for kw in keywords if kw in content_lower)
        if content_matches:
            # More matches = higher score, but capped
            score += min(20, content_matches * 5)  # 5 points per keyword in content

        return min(100.0, score)

    def format_full_for_llm(self, documents: list, library_id: str) -> str:
        """
        Format all documents without filtering for FULL output mode.

        Includes everything:
        - All documents (no priority filtering)
        - All code examples (no snippet filtering)
        - Test files and low-quality docs included

        Args:
            documents: List of Document objects
            library_id: Library identifier

        Returns:
            Complete documentation markdown
        """
        output = []

        for doc in documents:
            # Skip only truly empty files
            if len(doc.content.strip()) < 10:
                continue

            title = self.extract_title(doc.content, doc.file_path)
            full_content = self.extract_full_content(doc.content)

            output.append(f"# {doc.file_path}\n\n")
            output.append(full_content.strip())
            output.append("\n\n---\n\n")

        return "".join(output)
