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

    def format_for_llm(self, documents: list, library_id: str) -> str:
        """
        Format documents for LLM consumption with enhanced structure.

        Uses Context7-inspired format: brief, structured, code-focused.

        Args:
            documents: List of Document objects
            library_id: Library identifier

        Returns:
            Formatted markdown optimized for LLM parsing
        """
        output = []

        for doc in documents:
            # Skip excluded files
            if self.should_exclude_file(doc.file_path):
                continue

            # Skip very short files (likely empty or stub)
            if len(doc.content.strip()) < 100:
                continue

            # Extract structured content
            title = self.extract_title(doc.content, doc.file_path)
            description = self.extract_description(doc.content)
            snippets = self.extract_snippets_with_context(doc.content)

            # Skip if no useful content (no description and no code)
            if not description and not snippets:
                continue

            # Format document
            output.append(f"# {doc.file_path} - {title}\n\n")

            # Add description if available
            if description:
                output.append(f"{description}\n\n")

            # Add code examples if available
            if snippets:
                output.append("## Code Examples\n\n")

                for snippet in snippets:
                    output.append(f"### {snippet['context']}\n")
                    output.append(f"```{snippet['language']}\n")
                    output.append(snippet['code'])
                    output.append("\n```\n\n")

            # Separator between documents
            output.append("---\n\n")

        return "".join(output)
