"""
Unit tests for Joern CPG parser.
"""

import pytest

from repo_ctx.joern.parser import (
    CPGParser,
    CPGMethod,
    CPGType,
    CPGMember,
    CPGCall,
    CPGParseResult,
)


class TestCPGParser:
    """Test CPGParser class."""

    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return CPGParser()

    def test_parse_output_empty(self, parser):
        """Test parsing empty output."""
        result = parser.parse_output("")
        assert len(result.methods) == 0
        assert len(result.types) == 0
        assert len(result.members) == 0
        assert len(result.calls) == 0

    def test_parse_output_methods(self, parser):
        """Test parsing METHOD records."""
        output = """METHOD|test_func|module.test_func|test.py|10|15|test_func(x: int)|x:int"""
        result = parser.parse_output(output)

        assert len(result.methods) == 1
        method = result.methods[0]
        assert method.name == "test_func"
        assert method.full_name == "module.test_func"
        assert method.filename == "test.py"
        assert method.line_start == 10
        assert method.line_end == 15
        assert method.signature == "test_func(x: int)"
        assert len(method.parameters) == 1
        assert method.parameters[0] == ("x", "int")

    def test_parse_output_types(self, parser):
        """Test parsing TYPE records."""
        output = """TYPE|MyClass|module.MyClass|test.py|5|BaseClass;Interface"""
        result = parser.parse_output(output)

        assert len(result.types) == 1
        type_decl = result.types[0]
        assert type_decl.name == "MyClass"
        assert type_decl.full_name == "module.MyClass"
        assert type_decl.filename == "test.py"
        assert type_decl.line_start == 5
        assert "BaseClass" in type_decl.inherits_from
        assert "Interface" in type_decl.inherits_from

    def test_parse_output_members(self, parser):
        """Test parsing MEMBER records."""
        output = """MEMBER|my_field|str|module.MyClass"""
        result = parser.parse_output(output)

        assert len(result.members) == 1
        member = result.members[0]
        assert member.name == "my_field"
        assert member.type_name == "str"
        assert member.parent_type == "module.MyClass"

    def test_parse_output_calls(self, parser):
        """Test parsing CALL records."""
        output = """CALL|main|print|25"""
        result = parser.parse_output(output)

        assert len(result.calls) == 1
        call = result.calls[0]
        assert call.caller == "main"
        assert call.callee == "print"
        assert call.line_number == 25

    def test_parse_output_mixed(self, parser):
        """Test parsing mixed record types."""
        output = """METHOD|func1|mod.func1|test.py|1|5|func1()|
TYPE|Class1|mod.Class1|test.py|10|
MEMBER|field1|int|mod.Class1
CALL|func1|print|3"""
        result = parser.parse_output(output)

        assert len(result.methods) == 1
        assert len(result.types) == 1
        assert len(result.members) == 1
        assert len(result.calls) == 1

    def test_parse_output_invalid_lines_skipped(self, parser):
        """Test that invalid lines are skipped."""
        output = """METHOD|func1|mod.func1|test.py|1|5|func1()|
invalid line without enough fields
SHORT
METHOD|func2|mod.func2|test.py|10|15|func2()|"""
        result = parser.parse_output(output)

        # Should have parsed 2 methods, skipped invalid lines
        assert len(result.methods) == 2


class TestParseMethodsOutput:
    """Test CPGParser.parse_methods method."""

    @pytest.fixture
    def parser(self):
        return CPGParser()

    def test_parse_methods_basic(self, parser):
        """Test parsing basic method output."""
        output = """main|module.main|main.c|1|10|int main(void)
helper|module.helper|main.c|12|20|void helper(int x)"""
        methods = parser.parse_methods(output)

        assert len(methods) == 2
        assert methods[0].name == "main"
        assert methods[0].line_start == 1
        assert methods[1].name == "helper"
        assert methods[1].signature == "void helper(int x)"

    def test_parse_methods_scala_list_format(self, parser):
        """Test parsing Scala List() format."""
        output = 'List("main|module.main|main.c|1|10|int main(void)")'
        methods = parser.parse_methods(output)

        assert len(methods) == 1
        assert methods[0].name == "main"


class TestParseTypesOutput:
    """Test CPGParser.parse_types method."""

    @pytest.fixture
    def parser(self):
        return CPGParser()

    def test_parse_types_basic(self, parser):
        """Test parsing basic type output."""
        output = """Shape|module.Shape|shapes.py|5|
Rectangle|module.Rectangle|shapes.py|20|Shape"""
        types = parser.parse_types(output)

        assert len(types) == 2
        assert types[0].name == "Shape"
        assert len(types[0].inherits_from) == 0
        assert types[1].name == "Rectangle"
        assert "Shape" in types[1].inherits_from

    def test_parse_types_multiple_inheritance(self, parser):
        """Test parsing types with multiple inheritance."""
        output = """MyClass|mod.MyClass|test.py|10|Base1,Base2,Interface"""
        types = parser.parse_types(output)

        assert len(types) == 1
        assert len(types[0].inherits_from) == 3


class TestParseCallsOutput:
    """Test CPGParser.parse_calls method."""

    @pytest.fixture
    def parser(self):
        return CPGParser()

    def test_parse_calls_basic(self, parser):
        """Test parsing basic call output."""
        output = """main|printf|10
process|helper|25
helper|malloc|30"""
        calls = parser.parse_calls(output)

        assert len(calls) == 3
        assert calls[0].caller == "main"
        assert calls[0].callee == "printf"
        assert calls[0].line_number == 10


class TestParseInheritance:
    """Test CPGParser.parse_inheritance method."""

    @pytest.fixture
    def parser(self):
        return CPGParser()

    def test_parse_inheritance_basic(self, parser):
        """Test parsing inheritance output."""
        output = """Rectangle|Shape
Circle|Shape
Square|Rectangle,Shape"""
        inheritance = parser.parse_inheritance(output)

        assert "Rectangle" in inheritance
        assert inheritance["Rectangle"] == ["Shape"]
        assert "Square" in inheritance
        assert len(inheritance["Square"]) == 2


class TestParseComplexity:
    """Test CPGParser.parse_complexity method."""

    @pytest.fixture
    def parser(self):
        return CPGParser()

    def test_parse_complexity_basic(self, parser):
        """Test parsing complexity output."""
        output = """simple_func|1
complex_func|10
very_complex|25"""
        complexity = parser.parse_complexity(output)

        assert complexity["simple_func"] == 1
        assert complexity["complex_func"] == 10
        assert complexity["very_complex"] == 25


class TestParseParameters:
    """Test CPGParser.parse_parameters method."""

    @pytest.fixture
    def parser(self):
        return CPGParser()

    def test_parse_parameters_basic(self, parser):
        """Test parsing parameters output."""
        output = """func1|x:int,y:str
func2|
func3|a:float"""
        params = parser.parse_parameters(output)

        assert len(params["func1"]) == 2
        assert params["func1"][0] == ("x", "int")
        assert params["func1"][1] == ("y", "str")
        assert len(params["func2"]) == 0
        assert len(params["func3"]) == 1


class TestParseSimpleList:
    """Test CPGParser.parse_simple_list method."""

    @pytest.fixture
    def parser(self):
        return CPGParser()

    def test_parse_simple_list_basic(self, parser):
        """Test parsing simple list."""
        output = """item1
item2
item3"""
        items = parser.parse_simple_list(output)
        assert items == ["item1", "item2", "item3"]

    def test_parse_simple_list_with_empty_lines(self, parser):
        """Test parsing list with empty lines."""
        output = """item1

item2

item3"""
        items = parser.parse_simple_list(output)
        assert items == ["item1", "item2", "item3"]


class TestCleanScalaOutput:
    """Test CPGParser._clean_scala_output method."""

    @pytest.fixture
    def parser(self):
        return CPGParser()

    def test_clean_scala_list(self, parser):
        """Test cleaning Scala List() wrapper."""
        output = 'List("item1", "item2", "item3")'
        cleaned = parser._clean_scala_output(output)
        assert "item1" in cleaned
        assert "item2" in cleaned
        assert "item3" in cleaned

    def test_clean_json_array(self, parser):
        """Test cleaning JSON array format."""
        output = '["item1", "item2", "item3"]'
        cleaned = parser._clean_scala_output(output)
        assert "item1" in cleaned
        assert "item2" in cleaned

    def test_clean_plain_text(self, parser):
        """Test that plain text is unchanged."""
        output = "plain text output"
        cleaned = parser._clean_scala_output(output)
        assert cleaned == output


class TestDataClasses:
    """Test parser dataclasses."""

    def test_cpg_method_defaults(self):
        """Test CPGMethod default values."""
        method = CPGMethod(
            name="test",
            full_name="mod.test",
            filename="test.py",
            line_start=1,
            line_end=10,
            signature="test()",
        )
        assert method.parameters == []
        assert method.is_external is False

    def test_cpg_type_defaults(self):
        """Test CPGType default values."""
        type_decl = CPGType(
            name="MyClass",
            full_name="mod.MyClass",
            filename="test.py",
            line_start=1,
        )
        assert type_decl.inherits_from == []
        assert type_decl.is_external is False

    def test_cpg_parse_result_defaults(self):
        """Test CPGParseResult default values."""
        result = CPGParseResult()
        assert result.methods == []
        assert result.types == []
        assert result.members == []
        assert result.calls == []
        assert result.raw_output == ""
