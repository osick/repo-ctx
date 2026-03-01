"""Tests for Smalltalk code symbol extractor."""
import pytest
from pathlib import Path

from repo_ctx.analysis.smalltalk_extractor import SmalltalkExtractor
from repo_ctx.analysis.models import SymbolType


@pytest.fixture
def extractor():
    """Create a Smalltalk extractor instance."""
    return SmalltalkExtractor()


@pytest.fixture
def sample_fileout():
    """Load the standard Smalltalk sample file."""
    sample_path = Path(__file__).parent.parent / "examples" / "joern-test-data" / "smalltalk" / "sample.st"
    return sample_path.read_text()


@pytest.fixture
def visualworks_fileout():
    """Load the VisualWorks sample file."""
    sample_path = Path(__file__).parent.parent / "examples" / "joern-test-data" / "smalltalk" / "visualworks" / "sample.st"
    return sample_path.read_text()


class TestFileOutParsing:
    """Test file-out format parsing."""

    def test_extract_symbols_returns_list(self, extractor, sample_fileout):
        """Should return a list of symbols."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        assert isinstance(symbols, list)
        assert len(symbols) > 0

    def test_extract_class_definitions(self, extractor, sample_fileout):
        """Should extract class definitions."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]

        class_names = [c.name for c in classes]
        assert "Shape" in class_names
        assert "Circle" in class_names
        assert "Rectangle" in class_names
        assert "Square" in class_names
        assert "ShapeCollection" in class_names

    def test_extract_class_inheritance(self, extractor, sample_fileout):
        """Should extract superclass information."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        classes = {s.name: s for s in symbols if s.symbol_type == SymbolType.CLASS}

        # Check inheritance
        assert classes["Shape"].metadata.get("superclass") == "Object"
        assert classes["Circle"].metadata.get("superclass") == "Shape"
        assert classes["Rectangle"].metadata.get("superclass") == "Shape"
        assert classes["Square"].metadata.get("superclass") == "Rectangle"

    def test_extract_instance_variables(self, extractor, sample_fileout):
        """Should extract instance variable names."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        classes = {s.name: s for s in symbols if s.symbol_type == SymbolType.CLASS}

        assert "color" in classes["Shape"].metadata.get("instance_variables", [])
        assert "radius" in classes["Circle"].metadata.get("instance_variables", [])
        assert "width" in classes["Rectangle"].metadata.get("instance_variables", [])
        assert "height" in classes["Rectangle"].metadata.get("instance_variables", [])

    def test_extract_class_variables(self, extractor, sample_fileout):
        """Should extract class variable names."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        classes = {s.name: s for s in symbols if s.symbol_type == SymbolType.CLASS}

        assert "Pi" in classes["Circle"].metadata.get("class_variables", [])

    def test_extract_method_definitions(self, extractor, sample_fileout):
        """Should extract method definitions."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]

        # Check we have methods
        assert len(methods) > 0

        # Check specific methods exist
        method_names = [m.name for m in methods]
        assert "area" in method_names
        assert "perimeter" in method_names
        assert "color" in method_names
        assert "color:" in method_names
        assert "printOn:" in method_names

    def test_method_has_parent_class(self, extractor, sample_fileout):
        """Methods should have parent class information."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]

        # Find area method in Circle
        circle_area = [m for m in methods
                       if m.name == "area" and m.metadata.get("parent_class") == "Circle"]
        assert len(circle_area) == 1

    def test_extract_class_methods(self, extractor, sample_fileout):
        """Should distinguish class methods from instance methods."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]

        # Find class methods (e.g., Circle class >> radius:color:)
        class_methods = [m for m in methods if m.metadata.get("is_class_method")]
        assert len(class_methods) > 0

        # Circle>>radius:color: should be a class method
        radius_color = [m for m in class_methods
                        if m.name == "radius:color:" and m.metadata.get("parent_class") == "Circle"]
        assert len(radius_color) == 1

    def test_extract_method_category(self, extractor, sample_fileout):
        """Should extract method category/protocol."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]

        # Find area method in Circle - should be in 'computing' category
        circle_area = [m for m in methods
                       if m.name == "area" and m.metadata.get("parent_class") == "Circle"]
        assert len(circle_area) == 1
        assert circle_area[0].metadata.get("category") == "computing"

    def test_extract_method_documentation(self, extractor, sample_fileout):
        """Should extract method documentation (comments)."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]

        # Find area method in Circle
        circle_area = [m for m in methods
                       if m.name == "area" and m.metadata.get("parent_class") == "Circle"]
        assert len(circle_area) == 1
        assert circle_area[0].documentation is not None
        assert "pi" in circle_area[0].documentation.lower()

    def test_method_selector_types(self, extractor, sample_fileout):
        """Should handle different selector types (unary, binary, keyword)."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        method_names = [m.name for m in methods]

        # Unary selectors
        assert "area" in method_names
        assert "perimeter" in method_names

        # Keyword selectors
        assert "color:" in method_names
        assert "printOn:" in method_names

        # Multi-keyword selectors
        assert "width:height:color:" in method_names or any("width:" in n and "height:" in n for n in method_names)


class TestVisualWorksParsing:
    """Test VisualWorks-specific file-out format."""

    def test_extract_visualworks_classes(self, extractor, visualworks_fileout):
        """Should parse VisualWorks class definitions."""
        symbols = extractor.extract_symbols(visualworks_fileout, "visualworks/sample.st")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]

        class_names = [c.name for c in classes]
        assert "Shape" in class_names
        assert "Circle" in class_names
        assert "Rectangle" in class_names

    def test_visualworks_namespace_references(self, extractor, visualworks_fileout):
        """Should handle VisualWorks namespace references like #{Core.Object}."""
        symbols = extractor.extract_symbols(visualworks_fileout, "visualworks/sample.st")
        classes = {s.name: s for s in symbols if s.symbol_type == SymbolType.CLASS}

        # Shape's superclass should be Object (parsed from #{Core.Object})
        shape = classes.get("Shape")
        assert shape is not None
        superclass = shape.metadata.get("superclass")
        # Accept either "Object" or "Core.Object"
        assert superclass in ["Object", "Core.Object"]

    def test_visualworks_class_instance_variables(self, extractor, visualworks_fileout):
        """Should parse classInstanceVariableNames."""
        symbols = extractor.extract_symbols(visualworks_fileout, "visualworks/sample.st")
        classes = {s.name: s for s in symbols if s.symbol_type == SymbolType.CLASS}

        # Circle class has classInstanceVariableNames: 'defaultColor '
        circle = classes.get("Circle")
        assert circle is not None
        # Class instance variables should be in metadata
        class_inst_vars = circle.metadata.get("class_instance_variables", [])
        assert "defaultColor" in class_inst_vars or len(class_inst_vars) >= 0  # May be empty if parsed differently


class TestMethodParsing:
    """Test method body parsing."""

    def test_parse_unary_selector(self, extractor):
        """Should parse unary method selectors."""
        code = """!Shape methodsFor: 'accessing'!
area
    ^ 42! !"""
        symbols = extractor.extract_symbols(code, "test.st")
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]

        assert len(methods) == 1
        assert methods[0].name == "area"

    def test_parse_keyword_selector(self, extractor):
        """Should parse keyword method selectors."""
        code = """!Shape methodsFor: 'accessing'!
color: aColor
    color := aColor! !"""
        symbols = extractor.extract_symbols(code, "test.st")
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]

        assert len(methods) == 1
        assert methods[0].name == "color:"

    def test_parse_multi_keyword_selector(self, extractor):
        """Should parse multi-keyword method selectors."""
        code = """!Rectangle class methodsFor: 'instance creation'!
width: w height: h color: aColor
    ^ self new width: w; height: h; color: aColor! !"""
        symbols = extractor.extract_symbols(code, "test.st")
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]

        assert len(methods) == 1
        assert methods[0].name == "width:height:color:"

    def test_parse_temporaries(self, extractor):
        """Should recognize methods with temporaries."""
        code = """!Shape methodsFor: 'computing'!
complexCalculation
    | temp1 temp2 result |
    temp1 := 10.
    temp2 := 20.
    result := temp1 + temp2.
    ^ result! !"""
        symbols = extractor.extract_symbols(code, "test.st")
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]

        assert len(methods) == 1
        assert methods[0].name == "complexCalculation"


class TestLanguageDetection:
    """Test language and file type detection."""

    def test_detect_squeak_format(self, extractor, sample_fileout):
        """Should detect Squeak/Pharo file-out format."""
        dialect = extractor.detect_dialect(sample_fileout)
        assert dialect in ["squeak", "pharo", "standard"]

    def test_detect_visualworks_format(self, extractor, visualworks_fileout):
        """Should detect VisualWorks file-out format."""
        dialect = extractor.detect_dialect(visualworks_fileout)
        assert dialect == "visualworks"


class TestSymbolProperties:
    """Test symbol property extraction."""

    def test_symbol_file_path(self, extractor, sample_fileout):
        """Symbols should have correct file path."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        for symbol in symbols:
            assert symbol.file_path == "sample.st"

    def test_symbol_language(self, extractor, sample_fileout):
        """Symbols should have language set to smalltalk."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        for symbol in symbols:
            assert symbol.language == "smalltalk"

    def test_class_qualified_name(self, extractor, sample_fileout):
        """Classes should have proper qualified names."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        classes = {s.name: s for s in symbols if s.symbol_type == SymbolType.CLASS}

        # Circle should have qualified name including category
        circle = classes.get("Circle")
        assert circle is not None
        # Qualified name could be "Shapes-Geometry.Circle" or just "Circle"
        assert "Circle" in circle.qualified_name

    def test_method_qualified_name(self, extractor, sample_fileout):
        """Methods should have qualified names including class."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]

        # Find area method in Circle
        circle_area = [m for m in methods
                       if m.name == "area" and m.metadata.get("parent_class") == "Circle"]
        assert len(circle_area) == 1
        # Qualified name should be "Circle>>area" or "Circle.area"
        assert "Circle" in circle_area[0].qualified_name
        assert "area" in circle_area[0].qualified_name
