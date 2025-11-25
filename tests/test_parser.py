"""Tests for documentation parser."""
import pytest
from repo_ctx.parser import Parser
from repo_ctx.models import Document


class TestParserShouldIncludeFile:
    """Test file inclusion logic based on configuration."""

    def setup_method(self):
        """Set up parser instance for each test."""
        self.parser = Parser()

    def test_should_include_markdown_file(self):
        """Test that markdown files are included by default."""
        assert self.parser.should_include_file("README.md") is True
        assert self.parser.should_include_file("docs/guide.md") is True

    def test_should_include_rst_file(self):
        """Test that RST files are included."""
        assert self.parser.should_include_file("README.rst") is True
        assert self.parser.should_include_file("docs/api.rst") is True

    def test_should_include_txt_file(self):
        """Test that text files are included."""
        assert self.parser.should_include_file("LICENSE.txt") is True
        assert self.parser.should_include_file("notes.txt") is True

    def test_should_include_markdown_extension(self):
        """Test .markdown extension is included."""
        assert self.parser.should_include_file("guide.markdown") is True

    def test_should_exclude_python_file(self):
        """Test that Python files are excluded by default."""
        assert self.parser.should_include_file("script.py") is False

    def test_should_exclude_javascript_file(self):
        """Test that JS files are excluded."""
        assert self.parser.should_include_file("app.js") is False

    def test_should_exclude_no_extension(self):
        """Test that files without extension are excluded."""
        assert self.parser.should_include_file("Makefile") is False

    def test_should_include_with_folders_config(self):
        """Test inclusion based on folders configuration."""
        config = {"folders": ["docs", "guides"]}

        assert self.parser.should_include_file("docs/README.md", config) is True
        assert self.parser.should_include_file("guides/tutorial.md", config) is True
        assert self.parser.should_include_file("other/file.md", config) is False

    def test_should_include_folders_with_leading_slash(self):
        """Test folder matching with leading slash in path."""
        config = {"folders": ["docs"]}

        assert self.parser.should_include_file("/docs/README.md", config) is True
        assert self.parser.should_include_file("docs/README.md", config) is True

    def test_should_exclude_folder(self):
        """Test exclusion based on excludeFolders."""
        config = {"excludeFolders": ["node_modules", "dist"]}

        assert self.parser.should_include_file("node_modules/package.md", config) is False
        assert self.parser.should_include_file("dist/output.md", config) is False
        assert self.parser.should_include_file("src/file.md", config) is True

    def test_should_exclude_folder_with_slash_variations(self):
        """Test folder exclusion with various path formats."""
        config = {"excludeFolders": ["build"]}

        assert self.parser.should_include_file("build/README.md", config) is False
        assert self.parser.should_include_file("/build/README.md", config) is False
        assert self.parser.should_include_file("src/build/output.md", config) is False

    def test_should_exclude_file_by_name(self):
        """Test exclusion based on excludeFiles."""
        config = {"excludeFiles": ["CHANGELOG.md", "LICENSE.txt"]}

        assert self.parser.should_include_file("CHANGELOG.md", config) is False
        assert self.parser.should_include_file("docs/CHANGELOG.md", config) is False
        assert self.parser.should_include_file("LICENSE.txt", config) is False
        assert self.parser.should_include_file("README.md", config) is True

    def test_folders_and_exclude_folders_combined(self):
        """Test combined folders and excludeFolders logic."""
        config = {
            "folders": ["docs"],
            "excludeFolders": ["docs/draft"]
        }

        assert self.parser.should_include_file("docs/README.md", config) is True
        assert self.parser.should_include_file("docs/draft/wip.md", config) is False

    def test_all_filters_combined(self):
        """Test complex filtering with all config options."""
        config = {
            "folders": ["docs", "guides"],
            "excludeFolders": ["docs/internal"],
            "excludeFiles": ["DRAFT.md"]
        }

        assert self.parser.should_include_file("docs/API.md", config) is True
        assert self.parser.should_include_file("docs/internal/secret.md", config) is False
        assert self.parser.should_include_file("docs/DRAFT.md", config) is False
        assert self.parser.should_include_file("guides/tutorial.md", config) is True
        assert self.parser.should_include_file("other/README.md", config) is False

    def test_should_include_no_config(self):
        """Test file inclusion with no configuration."""
        assert self.parser.should_include_file("README.md", None) is True
        assert self.parser.should_include_file("docs/guide.md", None) is True

    def test_should_include_empty_config(self):
        """Test file inclusion with empty configuration dict."""
        assert self.parser.should_include_file("README.md", {}) is True


class TestParserParseMarkdown:
    """Test markdown parsing."""

    def setup_method(self):
        """Set up parser instance for each test."""
        self.parser = Parser()

    def test_parse_markdown_returns_content(self):
        """Test that parse_markdown returns content as-is (MVP behavior)."""
        content = "# Hello World\n\nThis is a test."
        result = self.parser.parse_markdown(content)
        assert result == content

    def test_parse_markdown_empty_content(self):
        """Test parsing empty markdown."""
        assert self.parser.parse_markdown("") == ""

    def test_parse_markdown_with_code_blocks(self):
        """Test parsing markdown with code blocks."""
        content = """# Test
```python
def hello():
    print("world")
```
"""
        result = self.parser.parse_markdown(content)
        assert result == content


class TestParserExtractSnippets:
    """Test code snippet extraction from markdown."""

    def setup_method(self):
        """Set up parser instance for each test."""
        self.parser = Parser()

    def test_extract_snippets_python(self):
        """Test extracting Python code snippets."""
        content = """
# Example

```python
def hello():
    return "world"
```
"""
        snippets = self.parser.extract_snippets(content)
        assert len(snippets) == 1
        assert snippets[0]["language"] == "python"
        assert "def hello():" in snippets[0]["code"]

    def test_extract_snippets_multiple(self):
        """Test extracting multiple code snippets."""
        content = """
```python
print("hello")
```

Some text here.

```javascript
console.log("world");
```
"""
        snippets = self.parser.extract_snippets(content)
        assert len(snippets) == 2
        assert snippets[0]["language"] == "python"
        assert snippets[1]["language"] == "javascript"

    def test_extract_snippets_no_language(self):
        """Test extracting code snippet without language specified."""
        content = """
```
generic code
```
"""
        snippets = self.parser.extract_snippets(content)
        assert len(snippets) == 1
        assert snippets[0]["language"] == "text"
        assert snippets[0]["code"] == "generic code"

    def test_extract_snippets_empty_content(self):
        """Test extracting snippets from empty content."""
        snippets = self.parser.extract_snippets("")
        assert snippets == []

    def test_extract_snippets_no_code_blocks(self):
        """Test extracting snippets from content without code blocks."""
        content = "# Just a heading\n\nAnd some text."
        snippets = self.parser.extract_snippets(content)
        assert snippets == []

    def test_extract_snippets_bash(self):
        """Test extracting bash code snippet."""
        content = """
```bash
echo "Hello World"
ls -la
```
"""
        snippets = self.parser.extract_snippets(content)
        assert len(snippets) == 1
        assert snippets[0]["language"] == "bash"
        assert "echo" in snippets[0]["code"]

    def test_extract_snippets_strips_whitespace(self):
        """Test that extracted code is stripped of surrounding whitespace."""
        content = """
```python


def test():
    pass


```
"""
        snippets = self.parser.extract_snippets(content)
        assert snippets[0]["code"].startswith("def test():")
        assert not snippets[0]["code"].startswith("\n")


class TestParserCountTokens:
    """Test token counting estimation."""

    def setup_method(self):
        """Set up parser instance for each test."""
        self.parser = Parser()

    def test_count_tokens_empty(self):
        """Test token count for empty string."""
        assert self.parser.count_tokens("") == 0

    def test_count_tokens_short_text(self):
        """Test token count for short text."""
        # "Hello" = 5 chars / 4 = 1.25 → 1 token
        assert self.parser.count_tokens("Hello") == 1

    def test_count_tokens_exact_division(self):
        """Test token count with exact division by 4."""
        # 20 characters / 4 = 5 tokens
        text = "a" * 20
        assert self.parser.count_tokens(text) == 5

    def test_count_tokens_paragraph(self):
        """Test token count for a paragraph."""
        text = "This is a test paragraph with multiple words and sentences."
        # 60 characters / 4 = 15.0 → 15 tokens (integer division gives 14)
        assert self.parser.count_tokens(text) == 14

    def test_count_tokens_markdown(self):
        """Test token count for markdown content."""
        text = """# Title

This is some content.

- Item 1
- Item 2
"""
        expected = len(text) // 4
        assert self.parser.count_tokens(text) == expected


class TestParserFormatForLLM:
    """Test formatting documents for LLM consumption."""

    def setup_method(self):
        """Set up parser instance for each test."""
        self.parser = Parser()

    def test_format_for_llm_single_document(self):
        """Test formatting a single document with enhanced structure."""
        doc = Document(
            version_id=1,
            file_path="README.md",
            content="# Hello World\n\nThis is a test library that demonstrates formatting. It provides examples of how to use the API.\n\n```python\nimport example\nexample.hello()\n```"
        )

        result = self.parser.format_for_llm([doc], "/group/project")

        # New format: # {file_path} - {title}
        assert "# README.md - Hello World" in result
        assert "demonstrates formatting" in result
        assert "## Code Examples" in result
        assert "```python" in result

    def test_format_for_llm_multiple_documents(self):
        """Test formatting multiple documents with enhanced structure."""
        docs = [
            Document(version_id=1, file_path="doc1.md",
                    content="# API Guide\n\nUse the API for data access. Connect using your API key.\n\n```python\napi.connect(key)\n```"),
            Document(version_id=1, file_path="doc2.md",
                    content="# Configuration\n\nConfigure the system using environment variables. Set API_KEY and API_URL.\n\n```bash\nexport API_KEY=xxx\n```"),
        ]

        result = self.parser.format_for_llm(docs, "/group/project")

        assert "# doc1.md - API Guide" in result
        assert "# doc2.md - Configuration" in result
        assert "API for data access" in result
        assert "environment variables" in result
        assert "---" in result  # Separator between docs

    def test_format_for_llm_includes_separators(self):
        """Test that formatted output includes separators with enhanced structure."""
        doc = Document(version_id=1, file_path="test.md",
                      content="# Testing\n\nTest documentation with sufficient content to pass quality filters and demonstrate the separator feature.\n\n```python\ntest()\n```")

        result = self.parser.format_for_llm([doc], "/group/project")

        # Should contain separator (enhanced format uses ---)
        assert "---" in result

    def test_format_for_llm_empty_list(self):
        """Test formatting empty document list."""
        result = self.parser.format_for_llm([], "/group/project")
        assert result == ""

    def test_format_for_llm_preserves_content(self):
        """Test that code blocks are preserved in enhanced structure."""
        doc = Document(
            version_id=1,
            file_path="test.md",
            content="# Formatting Test\n\nThis document demonstrates various formatting options. Use code blocks for examples.\n\n## Example\n```python\ncode = 'example'\nprint(code)\n```"
        )

        result = self.parser.format_for_llm([doc], "/group/project")

        # Enhanced format extracts and structures code blocks
        assert "```python" in result
        assert "code" in result
        assert "## Code Examples" in result


class TestParserInitialization:
    """Test Parser initialization."""

    def test_parser_creates_markdown_it(self):
        """Test that Parser initializes MarkdownIt instance."""
        parser = Parser()
        assert parser.md is not None
        assert hasattr(parser.md, 'parse')  # MarkdownIt has parse method
