"""
Unit tests for Joern CPG to Symbol mapper.
"""

import pytest

from repo_ctx.analysis.models import Symbol, SymbolType
from repo_ctx.joern.mapper import CPGMapper
from repo_ctx.joern.parser import (
    CPGMethod,
    CPGType,
    CPGMember,
    CPGCall,
    CPGParseResult,
)


class TestCPGMapper:
    """Test CPGMapper class."""

    @pytest.fixture
    def mapper(self):
        """Create mapper instance."""
        return CPGMapper()

    def test_map_method_function(self, mapper):
        """Test mapping a standalone function."""
        method = CPGMethod(
            name="my_function",
            full_name="module.my_function",
            filename="test.py",
            line_start=10,
            line_end=20,
            signature="my_function(x: int) -> str",
            parameters=[("x", "int")],
        )

        symbol = mapper.map_method(method, comment_map={})

        assert symbol is not None
        assert symbol.name == "my_function"
        assert symbol.symbol_type == SymbolType.FUNCTION
        assert symbol.file_path == "test.py"
        assert symbol.line_start == 10
        assert symbol.line_end == 20
        assert symbol.language == "python"
        assert symbol.visibility == "public"

    def test_map_method_class_method(self, mapper):
        """Test mapping a class method."""
        method = CPGMethod(
            name="process",
            full_name="module.MyClass.process",
            filename="test.py",
            line_start=25,
            line_end=35,
            signature="process(self, data: str)",
            parameters=[("self", "MyClass"), ("data", "str")],
        )

        symbol = mapper.map_method(method, comment_map={})

        assert symbol is not None
        assert symbol.name == "process"
        assert symbol.symbol_type == SymbolType.METHOD
        assert symbol.metadata.get("parent_class") == "MyClass"

    def test_map_method_private_python(self, mapper):
        """Test mapping a private Python method."""
        method = CPGMethod(
            name="_private_method",
            full_name="module.Class._private_method",
            filename="test.py",
            line_start=10,
            line_end=15,
            signature="_private_method()",
        )

        symbol = mapper.map_method(method, comment_map={})

        assert symbol is not None
        assert symbol.visibility == "protected"

    def test_map_method_dunder_private(self, mapper):
        """Test mapping a double-underscore private Python method."""
        method = CPGMethod(
            name="__secret",
            full_name="module.Class.__secret",
            filename="test.py",
            line_start=10,
            line_end=15,
            signature="__secret()",
        )

        symbol = mapper.map_method(method, comment_map={})

        assert symbol is not None
        assert symbol.visibility == "private"

    def test_map_method_empty_name(self, mapper):
        """Test mapping method with empty name returns None."""
        method = CPGMethod(
            name="",
            full_name="",
            filename="test.py",
            line_start=1,
            line_end=5,
            signature="",
        )

        symbol = mapper.map_method(method, comment_map={})
        assert symbol is None


class TestMapType:
    """Test CPGMapper.map_type method."""

    @pytest.fixture
    def mapper(self):
        return CPGMapper()

    def test_map_type_class(self, mapper):
        """Test mapping a class type."""
        type_decl = CPGType(
            name="Rectangle",
            full_name="shapes.Rectangle",
            filename="shapes.py",
            line_start=10,
            inherits_from=["Shape"],
        )

        symbol = mapper.map_type(type_decl, comment_map={})

        assert symbol is not None
        assert symbol.name == "Rectangle"
        assert symbol.symbol_type == SymbolType.CLASS
        assert symbol.file_path == "shapes.py"
        assert symbol.language == "python"
        assert "Shape" in symbol.metadata.get("bases", [])

    def test_map_type_interface_java(self, mapper):
        """Test mapping a Java interface."""
        type_decl = CPGType(
            name="IRepository",
            full_name="com.example.IRepository",
            filename="IRepository.java",
            line_start=5,
        )

        symbol = mapper.map_type(type_decl, comment_map={})

        assert symbol is not None
        assert symbol.symbol_type == SymbolType.INTERFACE

    def test_map_type_protocol_swift(self, mapper):
        """Test mapping a Swift protocol."""
        type_decl = CPGType(
            name="ShapeProtocol",
            full_name="Shapes.ShapeProtocol",
            filename="shapes.swift",
            line_start=1,
        )

        symbol = mapper.map_type(type_decl, comment_map={})

        assert symbol is not None
        assert symbol.symbol_type == SymbolType.INTERFACE

    def test_map_type_empty_name(self, mapper):
        """Test mapping type with empty name returns None."""
        type_decl = CPGType(
            name="",
            full_name="",
            filename="test.py",
            line_start=1,
        )

        symbol = mapper.map_type(type_decl, comment_map={})
        assert symbol is None


class TestMapMember:
    """Test CPGMapper.map_member method."""

    @pytest.fixture
    def mapper(self):
        return CPGMapper()

    def test_map_member_public(self, mapper):
        """Test mapping a public member."""
        member = CPGMember(
            name="value",
            type_name="int",
            parent_type="MyClass",
        )

        symbol = mapper.map_member(member)

        assert symbol is not None
        assert symbol.name == "value"
        assert symbol.symbol_type == SymbolType.VARIABLE
        assert symbol.visibility == "public"
        assert symbol.metadata.get("type") == "int"

    def test_map_member_private(self, mapper):
        """Test mapping a private member."""
        member = CPGMember(
            name="_internal",
            type_name="str",
            parent_type="MyClass",
        )

        symbol = mapper.map_member(member)

        assert symbol is not None
        assert symbol.visibility == "private"

    def test_map_member_empty_name(self, mapper):
        """Test mapping member with empty name returns None."""
        member = CPGMember(
            name="",
            type_name="int",
            parent_type="MyClass",
        )

        symbol = mapper.map_member(member)
        assert symbol is None


class TestMapCall:
    """Test CPGMapper.map_call method."""

    @pytest.fixture
    def mapper(self):
        return CPGMapper()

    def test_map_call_basic(self, mapper):
        """Test mapping a basic call."""
        call = CPGCall(
            caller="main",
            callee="process",
            line_number=25,
        )

        dep = mapper.map_call(call)

        assert dep is not None
        assert dep.source == "main"
        assert dep.target == "process"
        assert dep.dependency_type == "call"
        assert dep.line == 25

    def test_map_call_empty_caller(self, mapper):
        """Test mapping call with empty caller returns None."""
        call = CPGCall(
            caller="",
            callee="process",
            line_number=10,
        )

        dep = mapper.map_call(call)
        assert dep is None


class TestMapInheritance:
    """Test CPGMapper.map_inheritance method."""

    @pytest.fixture
    def mapper(self):
        return CPGMapper()

    def test_map_inheritance_single(self, mapper):
        """Test mapping single inheritance."""
        type_decl = CPGType(
            name="Rectangle",
            full_name="shapes.Rectangle",
            filename="shapes.py",
            line_start=10,
            inherits_from=["Shape"],
        )

        deps = mapper.map_inheritance(type_decl)

        assert len(deps) == 1
        assert deps[0].source == "shapes.Rectangle"
        assert deps[0].target == "Shape"
        assert deps[0].dependency_type == "inherits"

    def test_map_inheritance_multiple(self, mapper):
        """Test mapping multiple inheritance."""
        type_decl = CPGType(
            name="Square",
            full_name="shapes.Square",
            filename="shapes.py",
            line_start=20,
            inherits_from=["Rectangle", "Equilateral"],
        )

        deps = mapper.map_inheritance(type_decl)

        assert len(deps) == 2
        targets = [d.target for d in deps]
        assert "Rectangle" in targets
        assert "Equilateral" in targets

    def test_map_inheritance_none(self, mapper):
        """Test mapping type with no inheritance."""
        type_decl = CPGType(
            name="BaseShape",
            full_name="shapes.BaseShape",
            filename="shapes.py",
            line_start=1,
            inherits_from=[],
        )

        deps = mapper.map_inheritance(type_decl)
        assert len(deps) == 0


class TestMapParseResult:
    """Test CPGMapper.map_parse_result method."""

    @pytest.fixture
    def mapper(self):
        return CPGMapper()

    def test_map_parse_result_complete(self, mapper):
        """Test mapping a complete parse result."""
        result = CPGParseResult(
            methods=[
                CPGMethod(
                    name="area",
                    full_name="shapes.Rectangle.area",
                    filename="shapes.py",
                    line_start=15,
                    line_end=17,
                    signature="area(self) -> float",
                ),
            ],
            types=[
                CPGType(
                    name="Rectangle",
                    full_name="shapes.Rectangle",
                    filename="shapes.py",
                    line_start=10,
                    inherits_from=["Shape"],
                ),
            ],
            members=[
                CPGMember(
                    name="width",
                    type_name="float",
                    parent_type="shapes.Rectangle",
                ),
            ],
            calls=[
                CPGCall(
                    caller="area",
                    callee="multiply",
                    line_number=16,
                ),
            ],
        )

        symbols, dependencies = mapper.map_parse_result(result)

        # Should have 1 method + 1 type + 1 member = 3 symbols
        assert len(symbols) == 3

        # Should have 1 call + 1 inheritance = 2 dependencies
        assert len(dependencies) == 2


class TestDetectLanguage:
    """Test language detection."""

    @pytest.fixture
    def mapper(self):
        return CPGMapper()

    @pytest.mark.parametrize(
        "filename,expected",
        [
            ("test.py", "python"),
            ("test.js", "javascript"),
            ("test.ts", "typescript"),
            ("test.java", "java"),
            ("test.kt", "kotlin"),
            ("test.c", "c"),
            ("test.cpp", "cpp"),
            ("test.go", "go"),
            ("test.php", "php"),
            ("test.rb", "ruby"),
            ("test.swift", "swift"),
            ("test.cs", "csharp"),
            ("test.unknown", ""),
            ("", ""),
        ],
    )
    def test_detect_language(self, mapper, filename, expected):
        """Test language detection from filename."""
        assert mapper._detect_language(filename) == expected


class TestDetectVisibility:
    """Test visibility detection."""

    @pytest.fixture
    def mapper(self):
        return CPGMapper()

    def test_python_public(self, mapper):
        """Test Python public visibility."""
        assert mapper._detect_visibility("method", "python") == "public"

    def test_python_protected(self, mapper):
        """Test Python protected visibility."""
        assert mapper._detect_visibility("_method", "python") == "protected"

    def test_python_private(self, mapper):
        """Test Python private visibility."""
        assert mapper._detect_visibility("__method", "python") == "private"

    def test_javascript_private(self, mapper):
        """Test JavaScript private visibility."""
        assert mapper._detect_visibility("#field", "javascript") == "private"

    def test_default_public(self, mapper):
        """Test default public visibility."""
        assert mapper._detect_visibility("method", "unknown") == "public"


class TestExtractParentClass:
    """Test parent class extraction."""

    @pytest.fixture
    def mapper(self):
        return CPGMapper()

    @pytest.mark.parametrize(
        "full_name,expected",
        [
            ("MyClass.myMethod", "MyClass"),
            ("module.MyClass.myMethod", "MyClass"),
            ("myFunction", None),
            ("lowercase.function", None),
            ("", None),
        ],
    )
    def test_extract_parent_class(self, mapper, full_name, expected):
        """Test parent class extraction from full name."""
        assert mapper._extract_parent_class(full_name) == expected


class TestExtractReturnType:
    """Test return type extraction."""

    @pytest.fixture
    def mapper(self):
        return CPGMapper()

    @pytest.mark.parametrize(
        "signature,expected",
        [
            ("method(x: int) -> str", "str"),
            ("method(): ReturnType", "ReturnType"),
            ("void method()", None),
            ("", None),
        ],
    )
    def test_extract_return_type(self, mapper, signature, expected):
        """Test return type extraction from signature."""
        assert mapper._extract_return_type(signature) == expected


class TestIsInternalArtifact:
    """Test internal artifact detection.

    Joern CPG includes internal constructs like ANY, <module>, <init>, etc.
    that should be filtered out from code analysis output.
    """

    @pytest.fixture
    def mapper(self):
        return CPGMapper()

    def test_any_is_internal(self, mapper):
        """ANY is Joern's root type."""
        assert mapper._is_internal_artifact("ANY") is True

    def test_module_is_internal(self, mapper):
        """<module> is Python module namespace."""
        assert mapper._is_internal_artifact("<module>") is True

    def test_init_is_internal(self, mapper):
        """<init> is constructor placeholder."""
        assert mapper._is_internal_artifact("<init>") is True

    def test_clinit_is_internal(self, mapper):
        """<clinit> is static initializer."""
        assert mapper._is_internal_artifact("<clinit>") is True

    def test_lambda_is_internal(self, mapper):
        """<lambda> is anonymous function."""
        assert mapper._is_internal_artifact("<lambda>") is True

    def test_angle_bracket_prefix_is_internal(self, mapper):
        """Any name starting with < is internal."""
        assert mapper._is_internal_artifact("<unknown>") is True
        assert mapper._is_internal_artifact("<operator>") is True

    def test_metaclass_is_internal(self, mapper):
        """metaClass patterns are internal."""
        assert mapper._is_internal_artifact("metaClass") is True
        assert mapper._is_internal_artifact("SomeMetaClass") is True

    def test_normal_class_is_not_internal(self, mapper):
        """Normal class names should not be filtered."""
        assert mapper._is_internal_artifact("MyClass") is False
        assert mapper._is_internal_artifact("UserService") is False

    def test_normal_function_is_not_internal(self, mapper):
        """Normal function names should not be filtered."""
        assert mapper._is_internal_artifact("process_data") is False
        assert mapper._is_internal_artifact("calculateTotal") is False

    def test_empty_name_is_internal(self, mapper):
        """Empty names are treated as internal."""
        assert mapper._is_internal_artifact("") is True
        assert mapper._is_internal_artifact(None) is True

    def test_map_method_filters_internal(self, mapper):
        """map_method should return None for internal artifacts."""
        method = CPGMethod(
            name="<module>",
            full_name=":<module>",
            filename="test.py",
            line_start=1,
            line_end=5,
            signature="<module>()",
        )
        assert mapper.map_method(method, comment_map={}) is None

    def test_map_method_filters_any(self, mapper):
        """map_method should return None for ANY type method."""
        method = CPGMethod(
            name="ANY",
            full_name="ANY",
            filename="N/A",
            line_start=1,
            line_end=1,
            signature="ANY()",
        )
        assert mapper.map_method(method, comment_map={}) is None

    def test_map_type_filters_any(self, mapper):
        """map_type should return None for ANY type."""
        type_decl = CPGType(
            name="ANY",
            full_name="ANY",
            filename="N/A",
            line_start=1,
        )
        assert mapper.map_type(type_decl, comment_map={}) is None

    def test_map_type_filters_module(self, mapper):
        """map_type should return None for <module> type."""
        type_decl = CPGType(
            name="<module>",
            full_name=":<module>",
            filename="",
            line_start=1,
        )
        assert mapper.map_type(type_decl, comment_map={}) is None

    def test_map_member_filters_internal_parent(self, mapper):
        """map_member should return None for members of internal types."""
        member = CPGMember(
            name="value",
            type_name="int",
            parent_type="<module>",
        )
        assert mapper.map_member(member) is None


class TestNormalizeFilepath:
    """Test temp file path normalization.

    Joern's JavaScript/TypeScript frontend (jssrc2cpg) creates temporary files
    during transpilation. These temp file paths leak into the CPG and need
    to be normalized to meaningful placeholders.
    """

    @pytest.fixture
    def mapper(self):
        return CPGMapper()

    def test_regular_filepath_unchanged(self, mapper):
        """Normal file paths should not be modified."""
        assert mapper._normalize_filepath("src/app.js") == "src/app.js"
        assert mapper._normalize_filepath("index.ts") == "index.ts"
        assert mapper._normalize_filepath("/home/user/project/main.py") == "/home/user/project/main.py"

    def test_temp_js_file_normalized(self, mapper):
        """Temp JS files from jssrc2cpg should be normalized."""
        assert mapper._normalize_filepath("tmp0xlcwbg6.js") == "<transpiled>.js"
        assert mapper._normalize_filepath("tmp1bhn3gv0.js") == "<transpiled>.js"

    def test_temp_ts_file_normalized(self, mapper):
        """Temp TS files should be normalized."""
        assert mapper._normalize_filepath("tmpabcdef12.ts") == "<transpiled>.ts"
        assert mapper._normalize_filepath("tmp_xyz_123.tsx") == "<transpiled>.tsx"

    def test_temp_file_in_tmp_dir(self, mapper):
        """Temp files with /tmp/ prefix should be normalized."""
        assert mapper._normalize_filepath("/tmp/tmp0xlcwbg6.js") == "<transpiled>.js"
        assert mapper._normalize_filepath("/tmp/tmpabcdef.ts") == "<transpiled>.ts"

    def test_tmp_prefix_different_extensions(self, mapper):
        """Temp files with various JS-related extensions."""
        assert mapper._normalize_filepath("tmptest123.jsx") == "<transpiled>.jsx"
        assert mapper._normalize_filepath("tmpfile_abc.mjs") == "<transpiled>.mjs"
        assert mapper._normalize_filepath("TmpFile123.JS") == "<transpiled>.JS"

    def test_non_matching_tmp_files_unchanged(self, mapper):
        """Files that start with 'tmp' but aren't temp patterns should be unchanged."""
        # Regular files that happen to start with 'tmp' but have normal names
        assert mapper._normalize_filepath("temporary.py") == "temporary.py"
        assert mapper._normalize_filepath("tmp.txt") == "tmp.txt"

    def test_empty_filepath(self, mapper):
        """Empty filepath should be returned as-is."""
        assert mapper._normalize_filepath("") == ""
        assert mapper._normalize_filepath(None) is None

    def test_windows_style_temp_path(self, mapper):
        """Temp files with Windows-style paths should be normalized."""
        assert mapper._normalize_filepath("C:\\temp\\tmp0xlcwbg6.js") == "<transpiled>.js"

    def test_method_uses_normalized_filepath(self, mapper):
        """Verify map_method uses normalized filepath."""
        method = CPGMethod(
            name="myFunction",
            full_name="module.myFunction",
            filename="tmp0xlcwbg6.js",  # Temp file from jssrc2cpg
            line_start=10,
            line_end=20,
            signature="myFunction()",
        )

        symbol = mapper.map_method(method, comment_map={})

        assert symbol is not None
        assert symbol.file_path == "<transpiled>.js"

    def test_type_uses_normalized_filepath(self, mapper):
        """Verify map_type uses normalized filepath."""
        type_decl = CPGType(
            name="MyClass",
            full_name="MyClass",
            filename="/tmp/tmpabcdef.ts",  # Temp file
            line_start=1,
            inherits_from=[],
        )

        symbol = mapper.map_type(type_decl, comment_map={})

        assert symbol is not None
        assert symbol.file_path == "<transpiled>.ts"

    def test_inheritance_uses_normalized_filepath(self, mapper):
        """Verify map_inheritance uses normalized filepath."""
        type_decl = CPGType(
            name="Child",
            full_name="Child",
            filename="tmpxyz123.tsx",  # Temp file
            line_start=5,
            inherits_from=["Parent"],
        )

        deps = mapper.map_inheritance(type_decl)

        assert len(deps) == 1
        assert deps[0].file_path == "<transpiled>.tsx"
