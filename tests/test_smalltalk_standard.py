"""Tests for Standard Smalltalk (Squeak/Pharo) extractor."""
import pytest
from pathlib import Path

from repo_ctx.analysis.smalltalk import (
    StandardSmalltalkExtractor,
    create_extractor,
)
from repo_ctx.analysis.models import SymbolType


@pytest.fixture
def extractor():
    """Create a Standard Smalltalk extractor instance."""
    return StandardSmalltalkExtractor()


@pytest.fixture
def sample_fileout():
    """Load the standard Smalltalk sample file."""
    sample_path = Path(__file__).parent.parent / "examples" / "joern-test-data" / "smalltalk" / "sample.st"
    return sample_path.read_text()


class TestStandardExtractor:
    """Tests for StandardSmalltalkExtractor."""

    def test_dialect_identifier(self, extractor):
        """Should have correct dialect identifier."""
        assert extractor.DIALECT == "standard"

    def test_supports_standard_dialect(self):
        """Should support standard, squeak, and pharo dialects."""
        assert StandardSmalltalkExtractor.supports_dialect("standard")
        assert StandardSmalltalkExtractor.supports_dialect("squeak")
        assert StandardSmalltalkExtractor.supports_dialect("pharo")
        assert StandardSmalltalkExtractor.supports_dialect("STANDARD")  # Case insensitive

    def test_does_not_support_visualworks(self):
        """Should not support visualworks dialect."""
        assert not StandardSmalltalkExtractor.supports_dialect("visualworks")
        assert not StandardSmalltalkExtractor.supports_dialect("cincom")

    def test_extract_classes(self, extractor, sample_fileout):
        """Should extract classes from standard file-out."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]

        class_names = [c.name for c in classes]
        assert "Shape" in class_names
        assert "Circle" in class_names
        assert "Rectangle" in class_names
        assert "Square" in class_names
        assert "ShapeCollection" in class_names

    def test_class_metadata_has_dialect(self, extractor, sample_fileout):
        """Classes should have dialect in metadata."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]

        for cls in classes:
            assert cls.metadata.get("dialect") == "standard"

    def test_method_metadata_has_dialect(self, extractor, sample_fileout):
        """Methods should have dialect in metadata."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]

        for method in methods:
            assert method.metadata.get("dialect") == "standard"

    def test_class_visibility_public(self, extractor, sample_fileout):
        """Standard classes should be public (no privacy support)."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]

        for cls in classes:
            assert cls.visibility == "public"

    def test_class_without_class_instance_variables(self, extractor, sample_fileout):
        """Standard format doesn't have class instance variables in definition."""
        symbols = extractor.extract_symbols(sample_fileout, "sample.st")
        classes = {s.name: s for s in symbols if s.symbol_type == SymbolType.CLASS}

        # Standard format doesn't use classInstanceVariableNames in class definition
        # (though classes may have class-side instance variables defined elsewhere)
        shape = classes.get("Shape")
        assert shape is not None
        # The metadata should not have class_instance_variables key from standard parser
        assert "class_instance_variables" not in shape.metadata


class TestFactoryWithStandard:
    """Test factory function with standard dialect."""

    def test_create_extractor_with_standard_dialect(self):
        """Factory should create StandardSmalltalkExtractor for standard dialect."""
        extractor = create_extractor(dialect="standard")
        assert isinstance(extractor, StandardSmalltalkExtractor)

    def test_create_extractor_with_squeak_dialect(self):
        """Factory should create StandardSmalltalkExtractor for squeak dialect."""
        extractor = create_extractor(dialect="squeak")
        assert isinstance(extractor, StandardSmalltalkExtractor)

    def test_create_extractor_with_pharo_dialect(self):
        """Factory should create StandardSmalltalkExtractor for pharo dialect."""
        extractor = create_extractor(dialect="pharo")
        assert isinstance(extractor, StandardSmalltalkExtractor)

    def test_auto_detect_squeak_format(self, sample_fileout):
        """Factory should auto-detect Squeak format."""
        extractor = create_extractor(code=sample_fileout)
        assert isinstance(extractor, StandardSmalltalkExtractor)


class TestDependencyExtraction:
    """Test dependency extraction for standard Smalltalk."""

    def test_extract_inheritance_dependencies(self, extractor, sample_fileout):
        """Should extract inheritance relationships."""
        dependencies = extractor.extract_dependencies(sample_fileout, "sample.st")

        # Find inheritance dependencies
        inherits = [d for d in dependencies if d["type"] == "inherits"]

        # Circle inherits from Shape
        circle_inherits = [d for d in inherits if d["from"] == "Circle"]
        assert len(circle_inherits) == 1
        assert circle_inherits[0]["to"] == "Shape"

        # Square inherits from Rectangle
        square_inherits = [d for d in inherits if d["from"] == "Square"]
        assert len(square_inherits) == 1
        assert square_inherits[0]["to"] == "Rectangle"

    def test_extract_call_dependencies(self, extractor, sample_fileout):
        """Should extract method call relationships."""
        dependencies = extractor.extract_dependencies(sample_fileout, "sample.st")

        # Find call dependencies
        calls = [d for d in dependencies if d["type"] == "calls"]

        # Should have some method calls
        assert len(calls) > 0
