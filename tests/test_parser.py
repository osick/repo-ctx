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

        # README is high-priority: gets full content with file path header
        assert "# README.md" in result
        assert "# Hello World" in result  # Original title preserved in content
        assert "demonstrates formatting" in result
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

    def test_format_for_llm_filters_low_value_snippets(self):
        """Test that low-value installation commands are filtered."""
        doc = Document(
            version_id=1,
            file_path="guide.md",
            content="# Guide\n\nLearn how to use this library. First install it, then import it.\n\n```bash\npip install mylib\n```\n\n```python\nimport mylib\nmylib.do_something()\n```"
        )

        result = self.parser.format_for_llm([doc], "/group/project")

        # Python code should be kept
        assert "```python" in result
        assert "mylib.do_something()" in result
        # pip install should be filtered out
        assert "pip install" not in result

    def test_format_for_llm_readme_full_content(self):
        """Test that README gets full content treatment."""
        doc = Document(
            version_id=1,
            file_path="README.md",
            content="# My Project\n\nThis is a comprehensive project description.\n\n## Features\n\n- Feature 1\n- Feature 2\n\n## Architecture\n\nThe system uses a modular design."
        )

        result = self.parser.format_for_llm([doc], "/group/project")

        # Should include full content, not just description
        assert "# README.md" in result
        assert "comprehensive project description" in result
        assert "## Features" in result
        assert "Feature 1" in result
        assert "## Architecture" in result
        assert "modular design" in result

    def test_format_for_llm_installation_doc_skipped(self):
        """Test that installation docs are skipped (low priority)."""
        docs = [
            Document(version_id=1, file_path="INSTALL.md",
                    content="# Installation\n\nInstall using pip:\n\n```bash\npip install mylib\n```"),
            Document(version_id=1, file_path="api.md",
                    content="# API Reference\n\nThe main API provides several methods for data processing.\n\n```python\napi.process(data)\n```"),
        ]

        result = self.parser.format_for_llm(docs, "/group/project")

        # Installation doc should be skipped
        assert "INSTALL.md" not in result
        # API doc should be included
        assert "api.md" in result or "API Reference" in result

    def test_document_priority_classification(self):
        """Test document priority classification."""
        parser = Parser()

        assert parser.get_document_priority("README.md") == "high"
        assert parser.get_document_priority("docs/index.md") == "high"
        assert parser.get_document_priority("ARCHITECTURE.md") == "high"
        assert parser.get_document_priority("api/reference.md") == "normal"
        assert parser.get_document_priority("INSTALL.md") == "low"
        assert parser.get_document_priority("CONTRIBUTING.md") == "low"

    def test_is_low_value_snippet(self):
        """Test low-value snippet detection."""
        parser = Parser()

        # Low value snippets
        assert parser.is_low_value_snippet("pip install mylib", "bash") is True
        assert parser.is_low_value_snippet("docker run myimage", "shell") is True
        assert parser.is_low_value_snippet("npm install -g package", "bash") is True
        assert parser.is_low_value_snippet("git clone https://...", "bash") is True

        # Valuable snippets
        assert parser.is_low_value_snippet("import mylib\nmylib.process()", "python") is False
        assert parser.is_low_value_snippet("const api = require('api')", "javascript") is False
        # Multi-line bash scripts are kept
        assert parser.is_low_value_snippet("#!/bin/bash\nfor i in *.txt; do\n  process $i\ndone", "bash") is False


class TestParserInitialization:
    """Test Parser initialization."""

    def test_parser_creates_markdown_it(self):
        """Test that Parser initializes MarkdownIt instance."""
        parser = Parser()
        assert parser.md is not None
        assert hasattr(parser.md, 'parse')  # MarkdownIt has parse method


class TestParserQualityScoring:
    """Test quality scoring for documentation files."""

    def setup_method(self):
        """Set up parser instance for each test."""
        self.parser = Parser()

    def test_calculate_quality_score_readme_high_quality(self):
        """Test that README files with good content get high scores."""
        content = """# Project Name

This is a comprehensive README that explains the project. It provides clear documentation with examples.

## Installation

```bash
npm install project-name
```

## Usage

Here's how to use it:

```python
import project
project.run()
```
"""
        score = self.parser.calculate_quality_score(content, "README.md")
        assert score >= 75  # High quality README should score well

    def test_calculate_quality_score_docs_folder_bonus(self):
        """Test that files in docs/ folder get location bonus."""
        content = """# API Reference

Complete API documentation with examples and explanations for developers.

## Methods

- `method1()` - Does something important
- `method2()` - Does something else

```javascript
api.method1();
```
"""
        score = self.parser.calculate_quality_score(content, "docs/api.md")
        assert score >= 70  # docs/ folder gets bonus

    def test_calculate_quality_score_too_short_penalty(self):
        """Test that very short files get penalized."""
        content = "# Title\n\nVery brief."
        score = self.parser.calculate_quality_score(content, "brief.md")
        assert score <= 50  # Too short, should have low score

    def test_calculate_quality_score_no_code_examples(self):
        """Test that files without code examples score lower."""
        content = """# Documentation

This is a long piece of documentation that explains concepts in detail.
It provides thorough explanations and covers many topics comprehensively.
However, it lacks practical code examples that developers can use.
"""
        score = self.parser.calculate_quality_score(content, "guide.md")
        # Should still be decent but not top tier without code
        assert 40 <= score <= 70

    def test_calculate_quality_score_too_long_penalty(self):
        """Test that extremely long files get slight penalty."""
        # Simulate very long content
        content = "# Title\n\n" + ("This is a paragraph. " * 1000)
        score = self.parser.calculate_quality_score(content, "verbose.md")
        # Long but should still be reasonable if has structure
        assert score >= 30


class TestParserDocumentClassification:
    """Test document type classification."""

    def setup_method(self):
        """Set up parser instance for each test."""
        self.parser = Parser()

    def test_classify_document_tutorial(self):
        """Test classification of tutorial-style documents."""
        content = """# Getting Started Tutorial

This tutorial shows you how to get started step by step.

## Step 1: Installation

First, install the package:

```bash
npm install package
```

## Step 2: Configuration

Next, configure your project...
"""
        doc_type = self.parser.classify_document(content, "getting-started.md")
        assert doc_type == "tutorial"

    def test_classify_document_reference(self):
        """Test classification of API reference documents."""
        content = """# API Reference

## Function: processData

**Parameters:**
- `data` (array): The data to process
- `options` (object): Configuration options

**Returns:** Processed data array

**Example:**

```javascript
processData([1, 2, 3], {mode: 'fast'})
```
"""
        doc_type = self.parser.classify_document(content, "api-reference.md")
        assert doc_type == "reference"

    def test_classify_document_guide(self):
        """Test classification of conceptual guides."""
        content = """# Understanding Architecture

This guide explains the architecture and design concepts behind the system.

## Overview

The system uses a modular architecture that separates concerns effectively.
Understanding these concepts will help you work with the codebase more effectively.

## Key Concepts

- Modularity: Each component handles specific functionality
- Loose coupling: Components interact through well-defined interfaces
"""
        doc_type = self.parser.classify_document(content, "architecture-guide.md")
        assert doc_type == "guide"

    def test_classify_document_overview_readme(self):
        """Test classification of README/overview documents."""
        content = """# MyProject

MyProject is a tool for doing amazing things. This repository contains the source code.

## Features

- Feature 1
- Feature 2
- Feature 3

## Quick Start

See the documentation for details.
"""
        doc_type = self.parser.classify_document(content, "README.md")
        assert doc_type == "overview"

    def test_classify_document_index_as_overview(self):
        """Test that index files are classified as overview."""
        content = """# Documentation Index

Welcome to the documentation. Choose a section below.

- Getting Started
- API Reference
- Guides
"""
        doc_type = self.parser.classify_document(content, "docs/index.md")
        assert doc_type == "overview"


class TestParserMetadataExtraction:
    """Test metadata extraction from documents."""

    def setup_method(self):
        """Set up parser instance for each test."""
        self.parser = Parser()

    def test_extract_metadata_complete(self):
        """Test extracting complete metadata from a well-structured document."""
        content = """# API Documentation

This is a comprehensive API reference with examples. It provides detailed documentation
for all available methods and includes practical code examples for developers.

## Authentication

```python
import api
api.authenticate(token='your-token')
```

## Making Requests

```python
response = api.get('/endpoint')
```
"""
        metadata = self.parser.extract_metadata(content, "docs/api.md")

        assert "quality_score" in metadata
        assert "document_type" in metadata
        assert "reading_time" in metadata
        assert "snippet_count" in metadata
        assert "has_code_examples" in metadata

        assert metadata["quality_score"] >= 60  # Good quality doc
        assert metadata["document_type"] in ["tutorial", "reference", "guide", "overview"]
        assert metadata["snippet_count"] == 2  # Two code blocks
        assert metadata["has_code_examples"] is True

    def test_extract_metadata_reading_time(self):
        """Test reading time calculation (roughly 200 words per minute)."""
        # ~400 words should be ~2 minutes
        content = "# Title\n\n" + (" ".join(["word"] * 400))
        metadata = self.parser.extract_metadata(content, "test.md")

        assert "reading_time" in metadata
        assert 1 <= metadata["reading_time"] <= 3  # ~2 minutes +/- 1

    def test_extract_metadata_no_code(self):
        """Test metadata for document without code examples."""
        content = """# Guide

This is a purely conceptual guide without any code examples.
It explains ideas and concepts in plain language.
"""
        metadata = self.parser.extract_metadata(content, "guide.md")

        assert metadata["snippet_count"] == 0
        assert metadata["has_code_examples"] is False


class TestParserRelevanceScoring:
    """Test query-aware relevance scoring."""

    def setup_method(self):
        """Set up parser instance for each test."""
        self.parser = Parser()

    def test_calculate_relevance_score_title_match(self):
        """Test that matching title gives high relevance score."""
        content = """# Authentication Guide

This guide explains how to authenticate users.
"""
        score = self.parser.calculate_relevance_score(
            content, "docs/auth.md", "authentication"
        )
        # Title match (20pts) + heading match (10pts) + content match (5pts) = 35
        assert score >= 30

    def test_calculate_relevance_score_path_match(self):
        """Test that matching file path contributes to score."""
        content = """# Guide

Some content about user management.
"""
        score = self.parser.calculate_relevance_score(
            content, "docs/authentication/setup.md", "authentication"
        )
        # Path match should contribute (10 points per keyword in path)
        assert score >= 10

    def test_calculate_relevance_score_heading_match(self):
        """Test that matching headings contribute to score."""
        content = """# API Documentation

## Authentication

This section covers authentication.

## Authorization

This section covers authorization.
"""
        score = self.parser.calculate_relevance_score(
            content, "docs/api.md", "authentication"
        )
        # Heading match (10pts) + content match (5pts) = 15
        assert score >= 15

    def test_calculate_relevance_score_content_match(self):
        """Test that matching content contributes to score."""
        content = """# Setup Guide

This guide covers the basic setup process.
You will need to configure authentication tokens.
Authentication is required for all API calls.
"""
        score = self.parser.calculate_relevance_score(
            content, "docs/setup.md", "authentication"
        )
        # Content match (5 points per keyword)
        assert score >= 5

    def test_calculate_relevance_score_no_match(self):
        """Test low score when query doesn't match anything."""
        content = """# Database Setup

This guide covers PostgreSQL configuration.
"""
        score = self.parser.calculate_relevance_score(
            content, "docs/database.md", "authentication"
        )
        # No matches should give low score
        assert score < 20

    def test_calculate_relevance_score_multiple_keywords(self):
        """Test relevance scoring with multiple query keywords."""
        content = """# OAuth Authentication

This guide covers OAuth 2.0 authentication flow.

## Token Management

Learn how to manage access tokens.
"""
        score = self.parser.calculate_relevance_score(
            content, "docs/oauth.md", "oauth authentication tokens"
        )
        # Multiple keyword matches should boost score
        assert score >= 50

    def test_calculate_relevance_score_case_insensitive(self):
        """Test that relevance scoring is case insensitive."""
        content = """# AUTHENTICATION Guide

This covers Authentication setup.
"""
        score = self.parser.calculate_relevance_score(
            content, "docs/auth.md", "authentication"
        )
        # Should match regardless of case
        assert score >= 30

    def test_calculate_relevance_score_empty_query(self):
        """Test handling of empty query."""
        content = "# Test\n\nContent here."
        score = self.parser.calculate_relevance_score(
            content, "test.md", ""
        )
        assert score == 0

    def test_calculate_relevance_score_capped_at_100(self):
        """Test that relevance score is capped at 100."""
        content = """# Authentication OAuth Tokens

## Authentication
## OAuth
## Tokens

Content about authentication, oauth, and tokens.
Authentication authentication authentication.
OAuth oauth oauth. Tokens tokens tokens.
"""
        score = self.parser.calculate_relevance_score(
            content, "authentication/oauth/tokens.md", "authentication oauth tokens"
        )
        # Score should be capped at 100
        assert score <= 100
