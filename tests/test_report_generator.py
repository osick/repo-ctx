"""Tests for CodeAnalysisReport generator."""
import pytest
from repo_ctx.analysis.report_generator import CodeAnalysisReport
from repo_ctx.analysis.models import Symbol, SymbolType


class TestCodeAnalysisReportMarkdown:
    """Test markdown report generation."""

    def test_empty_symbols(self):
        """Test report with no symbols."""
        report = CodeAnalysisReport([])
        markdown = report.generate_markdown()

        assert "## Code Analysis" in markdown

    def test_classes_section_generated(self):
        """Test that classes section is generated with full details."""
        symbols = [
            Symbol(
                name="MyClass",
                symbol_type=SymbolType.CLASS,
                file_path="test.py",
                line_start=1,
                line_end=50,
                language="python",
                visibility="public",
                signature="class MyClass(BaseClass)",
                documentation="A test class for demonstration."
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        assert "### Classes" in markdown
        assert "class MyClass(BaseClass)" in markdown
        assert "Location: line 1-50" in markdown
        assert "A test class for demonstration" in markdown

    def test_classes_grouped_by_file(self):
        """Test that classes are grouped by file."""
        symbols = [
            Symbol(name="Class1", symbol_type=SymbolType.CLASS, file_path="file_a.py", line_start=1, language="python"),
            Symbol(name="Class2", symbol_type=SymbolType.CLASS, file_path="file_b.py", line_start=1, language="python"),
            Symbol(name="Class3", symbol_type=SymbolType.CLASS, file_path="file_a.py", line_start=20, language="python"),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        assert "#### file_a.py" in markdown
        assert "#### file_b.py" in markdown

    def test_class_methods_listed(self):
        """Test that class methods are listed under their class."""
        symbols = [
            Symbol(
                name="MyClass",
                symbol_type=SymbolType.CLASS,
                file_path="test.py",
                line_start=1,
                language="python",
                visibility="public"
            ),
            Symbol(
                name="public_method",
                symbol_type=SymbolType.METHOD,
                file_path="test.py",
                line_start=5,
                language="python",
                visibility="public",
                signature="public_method(self, arg)",
                metadata={"parent_class": "MyClass"}
            ),
            Symbol(
                name="_private_method",
                symbol_type=SymbolType.METHOD,
                file_path="test.py",
                line_start=10,
                language="python",
                visibility="private",
                signature="_private_method(self)",
                metadata={"parent_class": "MyClass"}
            ),
        ]
        report = CodeAnalysisReport(symbols)

        # Default (compact) mode shows method names only
        markdown = report.generate_markdown()
        assert "Methods: public_method" in markdown

        # Detailed mode (include_symbols=True) shows full method list
        markdown_detailed = report.generate_markdown(include_symbols=True)
        assert "Public methods (1):" in markdown_detailed
        assert "public_method(self, arg)" in markdown_detailed
        assert "Private methods (1):" in markdown_detailed
        assert "_private_method(self)" in markdown_detailed

    def test_class_inheritance_shown(self):
        """Test that inheritance info is shown."""
        symbols = [
            Symbol(
                name="ChildClass",
                symbol_type=SymbolType.CLASS,
                file_path="test.py",
                line_start=1,
                language="python",
                metadata={"bases": ["ParentClass", "Mixin"]}
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        assert "Inherits: ParentClass, Mixin" in markdown

    def test_class_implements_shown(self):
        """Test that implements info is shown."""
        symbols = [
            Symbol(
                name="UserService",
                symbol_type=SymbolType.CLASS,
                file_path="test.ts",
                line_start=1,
                language="typescript",
                metadata={"implements": ["IUserService", "IDisposable"]}
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        assert "Implements: IUserService, IDisposable" in markdown

    def test_functions_section_generated(self):
        """Test that functions section is generated."""
        symbols = [
            Symbol(
                name="process_data",
                symbol_type=SymbolType.FUNCTION,
                file_path="test.py",
                line_start=1,
                language="python",
                visibility="public",
                signature="def process_data(data: dict) -> bool",
                documentation="Process incoming data."
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        assert "### Functions" in markdown
        assert "def process_data(data: dict) -> bool" in markdown
        assert "Process incoming data" in markdown

    def test_private_functions_not_in_functions_section(self):
        """Test that private functions are not listed."""
        symbols = [
            Symbol(
                name="_helper",
                symbol_type=SymbolType.FUNCTION,
                file_path="test.py",
                line_start=1,
                language="python",
                visibility="private"
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        # Private functions should not appear in functions section
        assert "_helper" not in markdown or "### Functions" not in markdown

    def test_interfaces_section_generated(self):
        """Test that interfaces section is generated."""
        symbols = [
            Symbol(
                name="IRepository",
                symbol_type=SymbolType.INTERFACE,
                file_path="test.ts",
                line_start=1,
                language="typescript",
                visibility="public",
                signature="interface IRepository<T>",
                documentation="Generic repository interface."
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        assert "### Interfaces" in markdown
        assert "interface IRepository<T>" in markdown
        assert "Generic repository interface" in markdown

    def test_interface_extends_shown(self):
        """Test that interface extends info is shown."""
        symbols = [
            Symbol(
                name="IAdvancedRepo",
                symbol_type=SymbolType.INTERFACE,
                file_path="test.ts",
                line_start=1,
                language="typescript",
                metadata={"extends": ["IRepository", "IDisposable"]}
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        assert "Extends: IRepository, IDisposable" in markdown

    def test_enums_section_generated(self):
        """Test that enums section is generated."""
        symbols = [
            Symbol(
                name="Color",
                symbol_type=SymbolType.ENUM,
                file_path="test.py",
                line_start=1,
                language="python",
                signature="enum Color",
                metadata={"values": ["RED", "GREEN", "BLUE"]}
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        assert "### Enumerations" in markdown
        assert "enum Color" in markdown
        assert "Values: RED, GREEN, BLUE" in markdown


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

    def test_no_mermaid_when_no_relationships(self):
        """Test that mermaid is not generated when there are no inheritance relationships."""
        symbols = [
            Symbol(
                name="ClassA",
                symbol_type=SymbolType.CLASS,
                file_path="test.py",
                line_start=1,
                language="python",
                metadata={}
            ),
            Symbol(
                name="ClassB",
                symbol_type=SymbolType.CLASS,
                file_path="test.py",
                line_start=10,
                language="python",
                metadata={}
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown(include_mermaid=True)

        # No mermaid diagram when there are no relationships
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

    def test_mermaid_shows_public_methods(self):
        """Test that mermaid diagram shows public methods for classes."""
        symbols = [
            Symbol(
                name="Animal",
                symbol_type=SymbolType.CLASS,
                file_path="test.py",
                line_start=1,
                language="python",
                metadata={}
            ),
            Symbol(
                name="speak",
                symbol_type=SymbolType.METHOD,
                file_path="test.py",
                line_start=5,
                language="python",
                visibility="public",
                metadata={"parent_class": "Animal"}
            ),
            Symbol(
                name="Dog",
                symbol_type=SymbolType.CLASS,
                file_path="test.py",
                line_start=10,
                language="python",
                metadata={"bases": ["Animal"]}
            ),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown(include_mermaid=True)

        assert "+speak()" in markdown


class TestCodeAnalysisReportFileStructure:
    """Test file structure section generation."""

    def test_file_structure_table_generated(self):
        """Test that file structure table is generated for multiple files."""
        symbols = [
            Symbol(name="ClassA", symbol_type=SymbolType.CLASS, file_path="file1.py", line_start=1, language="python"),
            Symbol(name="func1", symbol_type=SymbolType.FUNCTION, file_path="file1.py", line_start=10, language="python", visibility="public"),
            Symbol(name="ClassB", symbol_type=SymbolType.CLASS, file_path="file2.py", line_start=1, language="python"),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        assert "### File Structure" in markdown
        assert "| File | Classes | Functions | Methods | Interfaces | Enums |" in markdown
        assert "file1.py" in markdown
        assert "file2.py" in markdown

    def test_no_file_structure_for_single_file(self):
        """Test that file structure table is not generated for single file."""
        symbols = [
            Symbol(name="ClassA", symbol_type=SymbolType.CLASS, file_path="test.py", line_start=1, language="python"),
            Symbol(name="ClassB", symbol_type=SymbolType.CLASS, file_path="test.py", line_start=10, language="python"),
        ]
        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        assert "### File Structure" not in markdown


class TestCodeAnalysisReportDependencies:
    """Test dependencies section generation."""

    def test_imports_listed(self):
        """Test that imports are listed."""
        symbols = []
        dependencies = [
            {"type": "import", "source": "test.py", "target": "os"},
            {"type": "import", "source": "test.py", "target": "json"},
        ]
        report = CodeAnalysisReport(symbols, dependencies)
        markdown = report.generate_markdown()

        assert "### Dependencies" in markdown
        assert "Import Dependencies" in markdown
        assert "`os`" in markdown
        assert "`json`" in markdown

    def test_internal_calls_listed(self):
        """Test that internal function calls are listed."""
        symbols = []
        dependencies = [
            {"type": "call", "caller": "main", "callee": "helper", "is_internal": True},
            {"type": "call", "caller": "main", "callee": "process", "is_internal": True},
        ]
        report = CodeAnalysisReport(symbols, dependencies)
        markdown = report.generate_markdown()

        assert "Internal Function Calls" in markdown
        assert "`helper`" in markdown
        assert "`process`" in markdown

    def test_no_dependencies_section_when_empty(self):
        """Test no dependencies section when there are none."""
        symbols = [
            Symbol(name="Test", symbol_type=SymbolType.CLASS, file_path="test.py", line_start=1, language="python"),
        ]
        report = CodeAnalysisReport(symbols, [])
        markdown = report.generate_markdown()

        assert "### Dependencies" not in markdown

    def test_call_graph_mermaid_generated(self):
        """Test that call graph mermaid diagram is generated."""
        symbols = []
        dependencies = [
            {"type": "call", "caller": "main", "callee": "helper", "is_internal": True},
            {"type": "call", "caller": "main", "callee": "process", "is_internal": True},
            {"type": "call", "caller": "process", "callee": "validate", "is_internal": True},
        ]
        report = CodeAnalysisReport(symbols, dependencies)
        markdown = report.generate_markdown(include_mermaid=True)

        assert "### Call Graph" in markdown
        assert "```mermaid" in markdown
        assert "flowchart TD" in markdown
        assert 'main["main"]' in markdown
        assert 'helper["helper"]' in markdown
        assert "main --> helper" in markdown
        assert "main --> process" in markdown
        assert "process --> validate" in markdown

    def test_call_graph_handles_method_names(self):
        """Test that call graph handles dotted method names correctly."""
        symbols = []
        dependencies = [
            {"type": "call", "caller": "UserService.get_user", "callee": "UserService._validate", "is_internal": True},
        ]
        report = CodeAnalysisReport(symbols, dependencies)
        markdown = report.generate_markdown(include_mermaid=True)

        assert "### Call Graph" in markdown
        assert 'UserService_get_user["UserService.get_user"]' in markdown
        assert 'UserService__validate["UserService._validate"]' in markdown
        assert "UserService_get_user --> UserService__validate" in markdown

    def test_no_call_graph_when_no_internal_calls(self):
        """Test that call graph is not generated when no internal calls."""
        symbols = []
        dependencies = [
            {"type": "import", "source": "test.py", "target": "os"},
        ]
        report = CodeAnalysisReport(symbols, dependencies)
        markdown = report.generate_markdown(include_mermaid=True)

        assert "### Call Graph" not in markdown

    def test_import_graph_mermaid_generated(self):
        """Test that import dependencies mermaid diagram is generated."""
        symbols = []
        dependencies = [
            {"type": "import", "source": "main.py", "target": "os", "is_external": True},
            {"type": "import", "source": "main.py", "target": "json", "is_external": True},
        ]
        report = CodeAnalysisReport(symbols, dependencies)
        markdown = report.generate_markdown(include_mermaid=True)

        assert "### Import Dependencies Graph" in markdown
        assert "```mermaid" in markdown
        assert "flowchart LR" in markdown
        assert 'main_py[["main.py"]]' in markdown
        assert 'ext_os(("os"))' in markdown
        assert 'ext_json(("json"))' in markdown
        assert "main_py -.-> ext_os" in markdown

    def test_import_graph_distinguishes_internal_external(self):
        """Test that import graph shows different styles for internal/external."""
        symbols = []
        dependencies = [
            {"type": "import", "source": "main.py", "target": "os", "is_external": True},
            {"type": "import", "source": "main.py", "target": "utils", "is_external": False},
        ]
        report = CodeAnalysisReport(symbols, dependencies)
        markdown = report.generate_markdown(include_mermaid=True)

        # External uses dashed arrow and circle shape
        assert "-.-> ext_os" in markdown
        # Internal uses solid arrow and rectangle shape
        assert 'int_utils["utils"]' in markdown
        assert "--> int_utils" in markdown

    def test_no_import_graph_when_no_imports(self):
        """Test that import graph is not generated when no imports."""
        symbols = []
        dependencies = [
            {"type": "call", "caller": "main", "callee": "helper", "is_internal": True},
        ]
        report = CodeAnalysisReport(symbols, dependencies)
        markdown = report.generate_markdown(include_mermaid=True)

        assert "### Import Dependencies Graph" not in markdown


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

        assert "classes" in json_data
        assert "interfaces" in json_data
        assert "enums" in json_data
        assert "functions" in json_data
        assert "hierarchy" in json_data
        assert "dependencies" in json_data

    def test_json_classes(self):
        """Test JSON classes data."""
        symbols = [
            Symbol(
                name="UserService",
                symbol_type=SymbolType.CLASS,
                file_path="service.py",
                line_start=1,
                line_end=50,
                language="python",
                visibility="public",
                signature="class UserService",
                documentation="Handles user operations.",
                metadata={"bases": ["BaseService"], "implements": ["IService"]}
            ),
            Symbol(
                name="get_user",
                symbol_type=SymbolType.METHOD,
                file_path="service.py",
                line_start=10,
                language="python",
                visibility="public",
                signature="def get_user(self, id)",
                metadata={"parent_class": "UserService"}
            ),
        ]
        report = CodeAnalysisReport(symbols)
        json_data = report.generate_json()

        classes = json_data["classes"]
        assert len(classes) == 1
        assert classes[0]["name"] == "UserService"
        assert classes[0]["file"] == "service.py"
        assert classes[0]["line_start"] == 1
        assert classes[0]["line_end"] == 50
        assert "BaseService" in classes[0]["inherits"]
        assert "IService" in classes[0]["implements"]
        assert len(classes[0]["methods"]) == 1
        assert classes[0]["methods"][0]["name"] == "get_user"

    def test_json_functions(self):
        """Test JSON functions data."""
        symbols = [
            Symbol(
                name="process_data",
                symbol_type=SymbolType.FUNCTION,
                file_path="utils.py",
                line_start=1,
                language="python",
                visibility="public",
                signature="def process_data(data: dict) -> bool",
                documentation="Process the data."
            ),
        ]
        report = CodeAnalysisReport(symbols)
        json_data = report.generate_json()

        functions = json_data["functions"]
        assert len(functions) == 1
        assert functions[0]["name"] == "process_data"
        assert functions[0]["signature"] == "def process_data(data: dict) -> bool"

    def test_json_hierarchy(self):
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
                metadata={"bases": ["Base"], "implements": ["IChild"]}
            ),
        ]
        report = CodeAnalysisReport(symbols)
        json_data = report.generate_json()

        hierarchy = json_data["hierarchy"]
        assert len(hierarchy) == 1
        assert hierarchy[0]["class"] == "Child"
        assert "Base" in hierarchy[0]["inherits"]
        assert "IChild" in hierarchy[0]["implements"]

    def test_json_dependencies(self):
        """Test JSON dependencies data."""
        symbols = []
        dependencies = [
            {"type": "import", "source": "main.py", "target": "os"},
            {"type": "call", "caller": "main", "callee": "helper"},
        ]
        report = CodeAnalysisReport(symbols, dependencies)
        json_data = report.generate_json()

        deps = json_data["dependencies"]
        assert "imports" in deps
        assert "calls" in deps
        assert len(deps["imports"]) == 1
        assert len(deps["calls"]) == 1


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
        assert "## Code Analysis" in markdown
        assert "### Classes" in markdown

        # Check classes are listed
        assert "BaseService" in markdown
        assert "UserService" in markdown
        assert "Inherits: BaseService" in markdown

        # Check methods are listed
        assert "save" in markdown
        assert "get_user" in markdown
        assert "list_users" in markdown

        # Check function is listed
        assert "helper_function" in markdown

        # Check mermaid (inheritance exists)
        assert "```mermaid" in markdown
        assert "BaseService <|-- UserService" in markdown

    def test_complete_typescript_analysis(self):
        """Test report with TypeScript-style symbols (interfaces, implements)."""
        symbols = [
            Symbol(
                name="IUserService",
                symbol_type=SymbolType.INTERFACE,
                file_path="user.ts",
                line_start=1,
                language="typescript",
                visibility="public",
                signature="interface IUserService",
                documentation="User service interface."
            ),
            Symbol(
                name="UserServiceImpl",
                symbol_type=SymbolType.CLASS,
                file_path="user.ts",
                line_start=10,
                language="typescript",
                visibility="public",
                signature="class UserServiceImpl implements IUserService",
                metadata={"implements": ["IUserService"]}
            ),
            Symbol(
                name="getUser",
                symbol_type=SymbolType.METHOD,
                file_path="user.ts",
                line_start=15,
                language="typescript",
                visibility="public",
                signature="getUser(id: string): User",
                metadata={"parent_class": "UserServiceImpl"}
            ),
        ]

        report = CodeAnalysisReport(symbols)
        markdown = report.generate_markdown()

        # Check interfaces section
        assert "### Interfaces" in markdown
        assert "interface IUserService" in markdown
        assert "User service interface" in markdown

        # Check classes section
        assert "### Classes" in markdown
        assert "UserServiceImpl implements IUserService" in markdown
        assert "Implements: IUserService" in markdown

        # Check mermaid
        assert "```mermaid" in markdown
        assert "<<interface>>" in markdown
        assert "IUserService <|.. UserServiceImpl" in markdown
