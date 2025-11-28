"""Tests for CodeAnalysisReport generator."""
import pytest
from repo_ctx.analysis.report_generator import CodeAnalysisReport
from repo_ctx.analysis.models import Symbol, SymbolType


class TestCodeAnalysisReportStatistics:
    """Test statistics generation."""

    def test_empty_symbols(self):
        """Test report with no symbols."""
        report = CodeAnalysisReport([])
        markdown = report.generate_markdown()

        assert "## Code Analysis Summary" in markdown
        assert "**Total symbols:** 0" in markdown

    def test_symbol_count(self):
        """Test symbol counting."""
        symbols = [
            Symbol(name="MyClass", symbol_type=SymbolType.CLASS, file_path="test.py", line_start=1, language="python"),
            Symbol(name="func1", symbol_type=SymbolType.FUNCTION, file_path="test.py", line_start=10, language="python"),
            Symbol(name="func2", symbol_type=SymbolType.FUNCTION, file_path="test.py", line_start=20, language="python"),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        assert "**Total symbols:** 3" in markdown
        assert "| class | 1 |" in markdown
        assert "| function | 2 |" in markdown

    def test_multiple_languages(self):
        """Test report with multiple languages."""
        symbols = [
            Symbol(name="Class1", symbol_type=SymbolType.CLASS, file_path="test.py", line_start=1, language="python"),
            Symbol(name="Class2", symbol_type=SymbolType.CLASS, file_path="Test.java", line_start=1, language="java"),
            Symbol(name="func", symbol_type=SymbolType.FUNCTION, file_path="test.js", line_start=1, language="javascript"),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        assert "**By language:**" in markdown
        assert "python" in markdown.lower()
        assert "java" in markdown.lower()


class TestCodeAnalysisReportMermaid:
    """Test mermaid diagram generation."""

    def test_class_hierarchy_generated(self):
        """Test that class hierarchy mermaid is generated."""
        symbols = [
            Symbol(
                name="Animal",
                symbol_type=SymbolType.CLASS,
                file_path="test.py",
                line_start=1,
                language="python",
                visibility="public",
                metadata={}
            ),
            Symbol(
                name="Dog",
                symbol_type=SymbolType.CLASS,
                file_path="test.py",
                line_start=10,
                language="python",
                visibility="public",
                metadata={"bases": ["Animal"]}
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown(include_mermaid=True)

        assert "```mermaid" in markdown
        assert "classDiagram" in markdown
        assert "Animal <|-- Dog" in markdown

    def test_no_mermaid_when_disabled(self):
        """Test that mermaid is not included when disabled."""
        symbols = [
            Symbol(
                name="Dog",
                symbol_type=SymbolType.CLASS,
                file_path="test.py",
                line_start=1,
                language="python",
                metadata={"bases": ["Animal"]}
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown(include_mermaid=False)

        assert "```mermaid" not in markdown

    def test_interface_annotation(self):
        """Test interface is marked in mermaid when there are relationships."""
        symbols = [
            Symbol(
                name="IUser",
                symbol_type=SymbolType.INTERFACE,
                file_path="test.ts",
                line_start=1,
                language="typescript",
                visibility="public",
                metadata={}
            ),
            Symbol(
                name="UserImpl",
                symbol_type=SymbolType.CLASS,
                file_path="test.ts",
                line_start=10,
                language="typescript",
                visibility="public",
                metadata={"implements": ["IUser"]}
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown(include_mermaid=True)

        assert "```mermaid" in markdown
        assert "<<interface>>" in markdown

    def test_enum_annotation(self):
        """Test enum is marked in mermaid when there are relationships."""
        symbols = [
            Symbol(
                name="Color",
                symbol_type=SymbolType.ENUM,
                file_path="test.py",
                line_start=1,
                language="python",
                visibility="public",
                metadata={}
            ),
            Symbol(
                name="Theme",
                symbol_type=SymbolType.CLASS,
                file_path="test.py",
                line_start=10,
                language="python",
                visibility="public",
                metadata={"bases": ["Color"]}
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown(include_mermaid=True)

        assert "```mermaid" in markdown
        assert "<<enumeration>>" in markdown


class TestCodeAnalysisReportAPI:
    """Test public API section generation."""

    def test_public_classes_listed(self):
        """Test that public classes are listed."""
        symbols = [
            Symbol(
                name="UserService",
                symbol_type=SymbolType.CLASS,
                file_path="test.py",
                line_start=1,
                language="python",
                visibility="public",
                signature="class UserService",
                documentation="Handles user operations."
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        assert "### Public API" in markdown
        assert "**Classes:**" in markdown
        assert "UserService" in markdown
        assert "Handles user operations" in markdown

    def test_public_functions_listed(self):
        """Test that public functions are listed."""
        symbols = [
            Symbol(
                name="process_data",
                symbol_type=SymbolType.FUNCTION,
                file_path="test.py",
                line_start=1,
                language="python",
                visibility="public",
                signature="def process_data(data: dict) -> bool"
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        assert "**Functions:**" in markdown
        assert "process_data" in markdown

    def test_private_not_listed_in_api(self):
        """Test that private symbols are not in public API section."""
        symbols = [
            Symbol(
                name="_private_func",
                symbol_type=SymbolType.FUNCTION,
                file_path="test.py",
                line_start=1,
                language="python",
                visibility="private"
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        # Should not appear in Public API section
        # (but might appear in statistics)
        api_section = markdown.split("### Public API")[1] if "### Public API" in markdown else ""
        assert "_private_func" not in api_section

    def test_interfaces_listed(self):
        """Test that interfaces are listed."""
        symbols = [
            Symbol(
                name="IRepository",
                symbol_type=SymbolType.INTERFACE,
                file_path="test.ts",
                line_start=1,
                language="typescript",
                visibility="public"
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        assert "**Interfaces:**" in markdown
        assert "IRepository" in markdown


class TestCodeAnalysisReportDependencies:
    """Test dependencies section generation."""

    def test_imports_listed(self):
        """Test that imports are listed."""
        symbols = []
        dependencies = [
            {"type": "import", "source": "test.py", "target": "os", "is_external": True},
            {"type": "import", "source": "test.py", "target": "json", "is_external": True},
        ]
        report = CodeAnalysisReport(symbols, dependencies)
        markdown = report.generate_markdown()

        assert "### Dependencies" in markdown
        assert "**External imports:**" in markdown
        assert "`os`" in markdown
        assert "`json`" in markdown

    def test_no_dependencies_section_when_empty(self):
        """Test no dependencies section when there are none."""
        symbols = [
            Symbol(name="Test", symbol_type=SymbolType.CLASS, file_path="test.py", line_start=1, language="python"),
        ]
        report = CodeAnalysisReport(symbols, [])
        markdown = report.generate_markdown()

        # Dependencies section should be minimal or empty
        deps_section = markdown.split("### Dependencies")[1] if "### Dependencies" in markdown else ""
        assert "External imports" not in deps_section or len(deps_section.strip()) < 50


class TestCodeAnalysisReportJSON:
    """Test JSON report generation."""

    def test_json_structure(self):
        """Test that JSON has correct structure."""
        symbols = [
            Symbol(
                name="MyClass",
                symbol_type=SymbolType.CLASS,
                file_path="test.py",
                line_start=1,
                language="python",
                visibility="public",
                signature="class MyClass"
            ),
        ]
        report = CodeAnalysisReport(symbols)
        json_data = report.generate_json()

        assert "statistics" in json_data
        assert "public_api" in json_data
        assert "class_hierarchy" in json_data
        assert "dependencies" in json_data

    def test_json_statistics(self):
        """Test JSON statistics."""
        symbols = [
            Symbol(name="A", symbol_type=SymbolType.CLASS, file_path="a.py", line_start=1, language="python"),
            Symbol(name="B", symbol_type=SymbolType.CLASS, file_path="b.py", line_start=1, language="python"),
            Symbol(name="func", symbol_type=SymbolType.FUNCTION, file_path="c.py", line_start=1, language="python"),
        ]
        report = CodeAnalysisReport(symbols)
        json_data = report.generate_json()

        stats = json_data["statistics"]
        assert stats["total_symbols"] == 3
        assert stats["by_type"]["class"] == 2
        assert stats["by_type"]["function"] == 1

    def test_json_public_api(self):
        """Test JSON public API."""
        symbols = [
            Symbol(
                name="Service",
                symbol_type=SymbolType.CLASS,
                file_path="service.py",
                line_start=1,
                language="python",
                visibility="public",
                signature="class Service"
            ),
        ]
        report = CodeAnalysisReport(symbols)
        json_data = report.generate_json()

        public_api = json_data["public_api"]
        assert len(public_api["classes"]) == 1
        assert public_api["classes"][0]["name"] == "Service"

    def test_json_class_hierarchy(self):
        """Test JSON class hierarchy."""
        symbols = [
            Symbol(
                name="Base",
                symbol_type=SymbolType.CLASS,
                file_path="base.py",
                line_start=1,
                language="python",
                metadata={}
            ),
            Symbol(
                name="Child",
                symbol_type=SymbolType.CLASS,
                file_path="child.py",
                line_start=1,
                language="python",
                metadata={"bases": ["Base"]}
            ),
        ]
        report = CodeAnalysisReport(symbols)
        json_data = report.generate_json()

        hierarchy = json_data["class_hierarchy"]
        assert len(hierarchy) == 1
        assert hierarchy[0]["class"] == "Child"
        assert "Base" in hierarchy[0]["inherits"]


class TestCodeAnalysisReportIntegration:
    """Integration tests with CodeAnalyzer."""

    def test_with_code_analyzer(self):
        """Test report generation from CodeAnalyzer results."""
        from repo_ctx.analysis import CodeAnalyzer

        analyzer = CodeAnalyzer()
        code = """
class BaseService:
    def save(self):
        pass

class UserService(BaseService):
    def get_user(self, id):
        return {"id": id}

    def list_users(self):
        return []

def helper_function():
    pass
"""
        symbols = analyzer.analyze_file(code, "service.py")
        deps = analyzer.extract_dependencies(code, "service.py", symbols)

        report = CodeAnalysisReport(symbols, deps)
        markdown = report.generate_markdown()

        # Check structure
        assert "## Code Analysis Summary" in markdown
        assert "### Symbol Statistics" in markdown
        assert "### Public API" in markdown

        # Check content
        assert "BaseService" in markdown
        assert "UserService" in markdown
        assert "helper_function" in markdown

        # Check mermaid
        assert "```mermaid" in markdown
        assert "BaseService <|-- UserService" in markdown
