"""Tests for Cincom VisualWorks Smalltalk extractor."""
import pytest
from pathlib import Path

from repo_ctx.analysis.smalltalk import (
    CincomSmalltalkExtractor,
    create_extractor,
)
from repo_ctx.analysis.models import SymbolType


@pytest.fixture
def extractor():
    """Create a Cincom VisualWorks extractor instance."""
    return CincomSmalltalkExtractor()


@pytest.fixture
def visualworks_fileout():
    """Load the VisualWorks sample file."""
    sample_path = Path(__file__).parent.parent / "examples" / "joern-test-data" / "smalltalk" / "visualworks" / "sample.st"
    return sample_path.read_text()


class TestCincomExtractor:
    """Tests for CincomSmalltalkExtractor."""

    def test_dialect_identifier(self, extractor):
        """Should have correct dialect identifier."""
        assert extractor.DIALECT == "visualworks"

    def test_supports_visualworks_dialect(self):
        """Should support visualworks, cincom, and vw dialects."""
        assert CincomSmalltalkExtractor.supports_dialect("visualworks")
        assert CincomSmalltalkExtractor.supports_dialect("cincom")
        assert CincomSmalltalkExtractor.supports_dialect("vw")
        assert CincomSmalltalkExtractor.supports_dialect("VISUALWORKS")  # Case insensitive

    def test_does_not_support_standard(self):
        """Should not support standard dialect."""
        assert not CincomSmalltalkExtractor.supports_dialect("standard")
        assert not CincomSmalltalkExtractor.supports_dialect("squeak")
        assert not CincomSmalltalkExtractor.supports_dialect("pharo")

    def test_extract_classes(self, extractor, visualworks_fileout):
        """Should extract classes from VisualWorks file-out."""
        symbols = extractor.extract_symbols(visualworks_fileout, "sample.st")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]

        class_names = [c.name for c in classes]
        assert "Shape" in class_names
        assert "Circle" in class_names
        assert "Rectangle" in class_names

    def test_class_metadata_has_dialect(self, extractor, visualworks_fileout):
        """Classes should have dialect in metadata."""
        symbols = extractor.extract_symbols(visualworks_fileout, "sample.st")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]

        for cls in classes:
            assert cls.metadata.get("dialect") == "visualworks"

    def test_method_metadata_has_dialect(self, extractor, visualworks_fileout):
        """Methods should have dialect in metadata."""
        symbols = extractor.extract_symbols(visualworks_fileout, "sample.st")
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]

        for method in methods:
            assert method.metadata.get("dialect") == "visualworks"

    def test_namespace_in_superclass(self, extractor, visualworks_fileout):
        """Should extract namespace from superclass reference."""
        symbols = extractor.extract_symbols(visualworks_fileout, "sample.st")
        classes = {s.name: s for s in symbols if s.symbol_type == SymbolType.CLASS}

        # Shape's superclass is #{Core.Object}
        shape = classes.get("Shape")
        assert shape is not None
        superclass = shape.metadata.get("superclass")
        # Should extract just "Object" from "Core.Object"
        assert superclass == "Object"

        # Should also have namespace info
        superclass_ns = shape.metadata.get("superclass_namespace")
        assert superclass_ns == "Core"

    def test_class_instance_variables(self, extractor, visualworks_fileout):
        """Should extract class instance variables."""
        symbols = extractor.extract_symbols(visualworks_fileout, "sample.st")
        classes = {s.name: s for s in symbols if s.symbol_type == SymbolType.CLASS}

        # Circle has defaultColor as class instance variable
        circle = classes.get("Circle")
        assert circle is not None
        class_inst_vars = circle.metadata.get("class_instance_variables", [])
        assert "defaultColor" in class_inst_vars

    def test_privacy_flag(self, extractor):
        """Should extract privacy flag from VisualWorks class."""
        code = """Smalltalk defineClass: #PrivateClass
\tsuperclass: #{Core.Object}
\tindexedType: #none
\tprivate: true
\tinstanceVariableNames: ''
\tclassInstanceVariableNames: ''
\timports: ''
\tcategory: 'Test'!
"""
        symbols = extractor.extract_symbols(code, "test.st")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]

        assert len(classes) == 1
        assert classes[0].visibility == "private"
        assert classes[0].metadata.get("is_private") is True

    def test_public_class(self, extractor, visualworks_fileout):
        """Public classes should have public visibility."""
        symbols = extractor.extract_symbols(visualworks_fileout, "sample.st")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]

        # All classes in sample are public
        for cls in classes:
            assert cls.visibility == "public"


class TestFactoryWithCincom:
    """Test factory function with Cincom/VisualWorks dialect."""

    def test_create_extractor_with_visualworks_dialect(self):
        """Factory should create CincomSmalltalkExtractor for visualworks dialect."""
        extractor = create_extractor(dialect="visualworks")
        assert isinstance(extractor, CincomSmalltalkExtractor)

    def test_create_extractor_with_cincom_dialect(self):
        """Factory should create CincomSmalltalkExtractor for cincom dialect."""
        extractor = create_extractor(dialect="cincom")
        assert isinstance(extractor, CincomSmalltalkExtractor)

    def test_create_extractor_with_vw_dialect(self):
        """Factory should create CincomSmalltalkExtractor for vw dialect."""
        extractor = create_extractor(dialect="vw")
        assert isinstance(extractor, CincomSmalltalkExtractor)

    def test_auto_detect_visualworks_format(self, visualworks_fileout):
        """Factory should auto-detect VisualWorks format."""
        extractor = create_extractor(code=visualworks_fileout)
        assert isinstance(extractor, CincomSmalltalkExtractor)


class TestNamespaceReferences:
    """Test namespace reference extraction."""

    def test_extract_namespace_references_from_method(self, extractor):
        """Should extract namespace references from method body."""
        code = """Smalltalk defineClass: #TestClass
\tsuperclass: #{Core.Object}
\tindexedType: #none
\tprivate: false
\tinstanceVariableNames: ''
\tclassInstanceVariableNames: ''
\timports: ''
\tcategory: 'Test'!

!TestClass methodsFor: 'accessing'!

useOtherClass
\t^#{Graphics.Color} red! !
"""
        symbols = extractor.extract_symbols(code, "test.st")
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]

        assert len(methods) == 1
        method = methods[0]
        namespace_refs = method.metadata.get("namespace_references", [])
        assert "Graphics.Color" in namespace_refs


class TestDependencyExtraction:
    """Test dependency extraction for Cincom VisualWorks."""

    def test_extract_inheritance_dependencies(self, extractor, visualworks_fileout):
        """Should extract inheritance relationships."""
        dependencies = extractor.extract_dependencies(visualworks_fileout, "sample.st")

        # Find inheritance dependencies
        inherits = [d for d in dependencies if d["type"] == "inherits"]

        # Circle inherits from Shape
        circle_inherits = [d for d in inherits if d["from"] == "Circle"]
        assert len(circle_inherits) == 1
        assert circle_inherits[0]["to"] == "Shape"

    def test_extract_namespace_reference_dependencies(self, extractor):
        """Should extract namespace reference dependencies."""
        code = """Smalltalk defineClass: #TestClass
\tsuperclass: #{Core.Object}
\tindexedType: #none
\tprivate: false
\tinstanceVariableNames: ''
\tclassInstanceVariableNames: ''
\timports: ''
\tcategory: 'Test'!

!TestClass methodsFor: 'accessing'!

getColor
\t^#{Graphics.Color} blue! !
"""
        dependencies = extractor.extract_dependencies(code, "test.st")

        # Find namespace reference dependencies
        refs = [d for d in dependencies if d["type"] == "references"]
        assert len(refs) > 0

        # Should have Graphics.Color reference
        color_refs = [r for r in refs if "Graphics.Color" in r["to"]]
        assert len(color_refs) >= 1


class TestClassExtensions:
    """Test class extension parsing for VisualWorks."""

    def test_class_extension_variables(self, extractor, visualworks_fileout):
        """Should merge class extension variables."""
        symbols = extractor.extract_symbols(visualworks_fileout, "sample.st")
        classes = {s.name: s for s in symbols if s.symbol_type == SymbolType.CLASS}

        # Circle has class extension: Circle class\n\tinstanceVariableNames: 'defaultColor '
        circle = classes.get("Circle")
        assert circle is not None

        # The class instance variables should include defaultColor
        class_inst_vars = circle.metadata.get("class_instance_variables", [])
        assert "defaultColor" in class_inst_vars
