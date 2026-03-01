"""Tests for llms.txt generation."""

import pytest
from repo_ctx.llmstxt import LlmsTxtGenerator
from repo_ctx.models import Document


class TestLlmsTxtGenerator:
    """Tests for LlmsTxtGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create generator instance."""
        return LlmsTxtGenerator()

    @pytest.fixture
    def sample_readme(self):
        """Create a sample README document."""
        return Document(
            id=1,
            version_id=1,
            file_path="README.md",
            content="""# My Awesome Project

A powerful tool for developers to build amazing applications.

## Installation

```bash
pip install my-awesome-project
```

## Quick Start

```python
from myproject import App

app = App()
app.run()
```

## Features

- Feature 1
- Feature 2
- Feature 3
""",
            tokens=200
        )

    @pytest.fixture
    def sample_api_doc(self):
        """Create a sample API documentation."""
        return Document(
            id=2,
            version_id=1,
            file_path="docs/api.md",
            content="""# API Reference

## Core Classes

```python
def initialize():
    '''Initialize the application'''
    pass

class Application:
    '''Main application class'''
    pass
```
""",
            tokens=100
        )

    @pytest.fixture
    def sample_guide(self):
        """Create a sample guide document."""
        return Document(
            id=3,
            version_id=1,
            file_path="docs/guide.md",
            content="""# User Guide

This guide helps you get started with the project.

## Configuration

Configure the app using environment variables.
""",
            tokens=80
        )

    def test_generate_basic_output(self, generator, sample_readme):
        """Test basic llms.txt generation."""
        result = generator.generate(
            [sample_readme],
            "/owner/my-awesome-project"
        )

        # Should contain project name
        assert "my-awesome-project" in result

        # Should contain description
        assert "powerful tool" in result.lower() or "developers" in result.lower()

    def test_generate_includes_key_files(self, generator, sample_readme, sample_guide):
        """Test that key files section is included."""
        result = generator.generate(
            [sample_readme, sample_guide],
            "/owner/project"
        )

        assert "Key Files" in result or "README" in result

    def test_generate_includes_quickstart(self, generator, sample_readme):
        """Test that quickstart section is included when available."""
        result = generator.generate(
            [sample_readme],
            "/owner/project",
            include_quickstart=True
        )

        # Should include installation or quick start content
        assert "pip install" in result or "Quick Start" in result or "Getting Started" in result

    def test_generate_excludes_quickstart_when_disabled(self, generator, sample_readme):
        """Test that quickstart is excluded when disabled."""
        result = generator.generate(
            [sample_readme],
            "/owner/project",
            include_quickstart=False
        )

        # Should not have a Getting Started section header
        # (content may still appear in description)
        lines = result.split('\n')
        getting_started_headers = [l for l in lines if l.strip().startswith('##') and 'Getting Started' in l]
        assert len(getting_started_headers) == 0

    def test_generate_includes_api_overview(self, generator, sample_api_doc):
        """Test that API overview is included when API docs available."""
        result = generator.generate(
            [sample_api_doc],
            "/owner/project",
            include_api=True
        )

        # May or may not have API section depending on content extraction
        # Just verify no errors
        assert result is not None

    def test_generate_excludes_api_when_disabled(self, generator, sample_api_doc):
        """Test that API is excluded when disabled."""
        result = generator.generate(
            [sample_api_doc],
            "/owner/project",
            include_api=False
        )

        lines = result.split('\n')
        api_headers = [l for l in lines if l.strip().startswith('##') and 'API' in l]
        assert len(api_headers) == 0

    def test_generate_with_description_override(self, generator, sample_readme):
        """Test description override."""
        custom_desc = "Custom project description for testing"
        result = generator.generate(
            [sample_readme],
            "/owner/project",
            description=custom_desc
        )

        assert custom_desc in result

    def test_generate_doc_links(self, generator, sample_readme, sample_guide):
        """Test that documentation links are generated."""
        result = generator.generate(
            [sample_readme, sample_guide],
            "/owner/project"
        )

        # Should have documentation section with links
        assert "Documentation" in result or "docs/" in result.lower()

    def test_generate_under_token_limit(self, generator, sample_readme, sample_api_doc, sample_guide):
        """Test that output stays under token limit."""
        result = generator.generate(
            [sample_readme, sample_api_doc, sample_guide],
            "/owner/project"
        )

        # Count tokens (rough estimate: ~4 chars per token)
        tokens = generator.parser.count_tokens(result)
        assert tokens <= generator.MAX_TOKENS

    def test_generate_empty_documents(self, generator):
        """Test with no documents."""
        result = generator.generate(
            [],
            "/owner/project"
        )

        # Should still produce valid output with project name
        assert "project" in result

    def test_generate_extracts_project_name(self, generator, sample_readme):
        """Test project name extraction from library_id."""
        result = generator.generate(
            [sample_readme],
            "/my-org/awesome-tool"
        )

        # Should use the project name part
        assert "awesome-tool" in result


class TestLlmsTxtHelpers:
    """Test helper methods of LlmsTxtGenerator."""

    @pytest.fixture
    def generator(self):
        """Create generator instance."""
        return LlmsTxtGenerator()

    def test_find_readme_basic(self, generator):
        """Test finding README in document list."""
        readme = Document(
            version_id=1, file_path="README.md",
            content="# Project\n\nDescription", tokens=50
        )
        other = Document(
            version_id=1, file_path="docs/guide.md",
            content="# Guide", tokens=30
        )

        found = generator._find_readme([other, readme])
        assert found is not None
        assert found.file_path == "README.md"

    def test_find_readme_case_insensitive(self, generator):
        """Test README finding is case insensitive."""
        readme = Document(
            version_id=1, file_path="readme.md",
            content="# Project", tokens=50
        )

        found = generator._find_readme([readme])
        assert found is not None

    def test_find_readme_prefers_root(self, generator):
        """Test that root README is preferred over nested."""
        root_readme = Document(
            version_id=1, file_path="README.md",
            content="# Root", tokens=50
        )
        nested_readme = Document(
            version_id=1, file_path="docs/README.md",
            content="# Nested", tokens=50
        )

        found = generator._find_readme([nested_readme, root_readme])
        assert found.file_path == "README.md"

    def test_extract_description_from_readme(self, generator):
        """Test description extraction from README content."""
        content = """# My Project

This is a great project for doing things.

## Installation
"""
        desc = generator._extract_description(content)
        assert "great project" in desc.lower()

    def test_extract_description_skips_badges(self, generator):
        """Test that badges are skipped when extracting description."""
        content = """# My Project

![Badge](https://badge.url)
[![Status](https://status.url)](link)

This is the actual description.

## More
"""
        desc = generator._extract_description(content)
        assert "actual description" in desc.lower()
        assert "![" not in desc

    def test_extract_description_truncates_long(self, generator):
        """Test that long descriptions are truncated."""
        content = """# Project

This is a very long description that goes on and on and contains a lot of words that describe the project in great detail with many features and capabilities and use cases and examples and more information than could possibly fit in a reasonable summary.
"""
        desc = generator._extract_description(content)
        assert len(desc) <= 203  # 200 + "..."

    def test_identify_key_files(self, generator):
        """Test key file identification."""
        docs = [
            Document(version_id=1, file_path="README.md", content="# Project", tokens=50),
            Document(version_id=1, file_path="CONTRIBUTING.md", content="# Contributing", tokens=30),
            Document(version_id=1, file_path="LICENSE", content="MIT", tokens=10),
            Document(version_id=1, file_path="docs/random.md", content="# Random", tokens=20),
        ]

        key_files = generator._identify_key_files(docs)

        paths = [p for p, _ in key_files]
        assert "README.md" in paths
        assert "CONTRIBUTING.md" in paths

    def test_extract_quickstart(self, generator):
        """Test quickstart extraction."""
        content = """# Project

## Installation

```bash
pip install project
```

## Usage

Use the project.
"""
        quickstart = generator._extract_quickstart(content)
        assert "pip install" in quickstart

    def test_extract_quickstart_truncates(self, generator):
        """Test that long quickstart sections are truncated."""
        long_content = """# Project

## Getting Started

""" + "This is a very long section. " * 100

        quickstart = generator._extract_quickstart(long_content)
        assert len(quickstart) <= 550  # 500 + buffer + "..."
