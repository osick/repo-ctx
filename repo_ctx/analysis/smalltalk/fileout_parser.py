"""
Smalltalk file-out format parser.

Parses the chunk-based file-out format used by Smalltalk environments
to export source code. Supports both standard Squeak/Pharo format and
Cincom VisualWorks format.

File-out format uses `!` as chunk delimiter:
- Each chunk is executable Smalltalk that recreates objects
- Class definitions: `Foo subclass:#Bar instanceVariableNames:'baz'...!`
- Method chunks: `!ClassName methodsFor: 'category'!` followed by method code
"""

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Iterator


class ChunkType(Enum):
    """Types of chunks in a file-out."""
    COMMENT = auto()           # File header comment
    CLASS_DEFINITION = auto()  # Class definition (subclass:...)
    CLASS_COMMENT = auto()     # Class documentation
    METHOD_HEADER = auto()     # !ClassName methodsFor: 'category'!
    METHOD_BODY = auto()       # Method source code
    EXPRESSION = auto()        # Executable expression
    EMPTY = auto()             # Empty chunk


@dataclass
class ClassDefinition:
    """Parsed class definition."""
    name: str
    superclass: str
    instance_variables: list[str] = field(default_factory=list)
    class_variables: list[str] = field(default_factory=list)
    class_instance_variables: list[str] = field(default_factory=list)
    pool_dictionaries: list[str] = field(default_factory=list)
    category: str = ""
    comment: str = ""
    is_private: bool = False
    namespace: str = ""
    line_number: int = 0


@dataclass
class MethodDefinition:
    """Parsed method definition."""
    selector: str
    class_name: str
    category: str
    source: str
    is_class_method: bool = False
    stamp: str = ""
    line_number: int = 0


@dataclass
class Chunk:
    """A parsed chunk from a file-out."""
    chunk_type: ChunkType
    content: str
    line_number: int = 0
    # Parsed data (depends on chunk type)
    class_def: ClassDefinition | None = None
    method_def: MethodDefinition | None = None


class FileOutParser:
    """
    Parser for Smalltalk file-out format.

    Handles both standard Squeak/Pharo format and VisualWorks format.
    """

    # Patterns for class definitions
    # Standard: Object subclass: #Shape instanceVariableNames: 'color' ...
    STANDARD_CLASS_PATTERN = re.compile(
        r"(\w+)\s+subclass:\s*#(\w+)\s+"
        r"instanceVariableNames:\s*'([^']*)'\s+"
        r"classVariableNames:\s*'([^']*)'\s+"
        r"poolDictionaries:\s*'([^']*)'\s+"
        r"category:\s*'([^']*)'",
        re.DOTALL
    )

    # VisualWorks: Smalltalk defineClass: #Shape superclass: #{Core.Object} ...
    VISUALWORKS_CLASS_PATTERN = re.compile(
        r"Smalltalk\s+defineClass:\s*#(\w+)\s+"
        r"superclass:\s*#\{([^}]+)\}\s+"
        r"indexedType:\s*#(\w+)\s+"
        r"private:\s*(true|false)\s+"
        r"instanceVariableNames:\s*'([^']*)'\s+"
        r"classInstanceVariableNames:\s*'([^']*)'\s+"
        r"imports:\s*'([^']*)'\s+"
        r"category:\s*'([^']*)'",
        re.DOTALL
    )

    # Method header: ClassName methodsFor: 'category' stamp: 'author date'
    # Note: The leading ! is the chunk delimiter, not part of the content
    METHOD_HEADER_PATTERN = re.compile(
        r"^(\w+)(\s+class)?\s+methodsFor:\s*'([^']*)'"
        r"(?:\s+stamp:\s*'([^']*)')?",
        re.DOTALL
    )

    # Class comment: ClassName commentStamp: 'author date' prior: 0
    CLASS_COMMENT_PATTERN = re.compile(
        r"^(\w+)\s+commentStamp:\s*'([^']*)'\s+prior:\s*(\d+)",
        re.DOTALL
    )

    # VisualWorks class extension: ClassName class
    CLASS_EXTENSION_PATTERN = re.compile(
        r"^(\w+)\s+class\s*$",
        re.MULTILINE
    )

    def __init__(self):
        """Initialize the file-out parser."""
        self._current_class = None
        self._current_category = None
        self._is_class_side = False
        self._current_stamp = ""

    def parse(self, code: str) -> list[Chunk]:
        """
        Parse a file-out into chunks.

        Args:
            code: The file-out source code

        Returns:
            List of parsed Chunk objects
        """
        chunks = []
        line_number = 1

        for raw_chunk, chunk_line in self._split_chunks(code):
            chunk = self._parse_chunk(raw_chunk, chunk_line)
            if chunk:
                chunks.append(chunk)

        return chunks

    def _split_chunks(self, code: str) -> Iterator[tuple[str, int]]:
        """
        Split code into chunks delimited by `!`.

        Handles:
        - `!` as chunk delimiter
        - `!!` as escaped `!` within strings
        - Empty chunks between `! !`

        Yields:
            Tuples of (chunk_content, line_number)
        """
        # Replace escaped !! with placeholder
        placeholder = "\x00BANG\x00"
        code = code.replace("!!", placeholder)

        line_number = 1
        current_chunk = []
        chunk_start_line = 1

        i = 0
        while i < len(code):
            char = code[i]

            if char == "!":
                # End of chunk
                chunk_content = "".join(current_chunk).strip()
                if chunk_content:
                    # Restore escaped bangs
                    chunk_content = chunk_content.replace(placeholder, "!")
                    yield (chunk_content, chunk_start_line)

                current_chunk = []
                chunk_start_line = line_number + 1
            else:
                current_chunk.append(char)
                if char == "\n":
                    line_number += 1

            i += 1

        # Handle final chunk if no trailing !
        final_chunk = "".join(current_chunk).strip()
        if final_chunk:
            final_chunk = final_chunk.replace(placeholder, "!")
            yield (final_chunk, chunk_start_line)

    def _parse_chunk(self, content: str, line_number: int) -> Chunk | None:
        """
        Parse a single chunk and determine its type.

        Args:
            content: The chunk content
            line_number: Line number where chunk starts

        Returns:
            Parsed Chunk object or None for empty chunks
        """
        if not content or content.isspace():
            return None

        # Check for file header comment (starts with quote)
        if content.startswith("'") or content.startswith('"'):
            return Chunk(
                chunk_type=ChunkType.COMMENT,
                content=content,
                line_number=line_number,
            )

        # Check for class comment
        comment_match = self.CLASS_COMMENT_PATTERN.match(content)
        if comment_match:
            class_name = comment_match.group(1)
            return Chunk(
                chunk_type=ChunkType.CLASS_COMMENT,
                content=content,
                line_number=line_number,
                class_def=ClassDefinition(name=class_name, superclass=""),
            )

        # Check for method header
        method_match = self.METHOD_HEADER_PATTERN.match(content)
        if method_match:
            class_name = method_match.group(1)
            is_class_side = method_match.group(2) is not None
            category = method_match.group(3)
            stamp = method_match.group(4) or ""

            self._current_class = class_name
            self._is_class_side = is_class_side
            self._current_category = category
            self._current_stamp = stamp

            return Chunk(
                chunk_type=ChunkType.METHOD_HEADER,
                content=content,
                line_number=line_number,
            )

        # Check for standard class definition
        class_match = self.STANDARD_CLASS_PATTERN.search(content)
        if class_match:
            class_def = self._parse_standard_class(class_match, line_number)
            return Chunk(
                chunk_type=ChunkType.CLASS_DEFINITION,
                content=content,
                line_number=line_number,
                class_def=class_def,
            )

        # Check for VisualWorks class definition
        vw_match = self.VISUALWORKS_CLASS_PATTERN.search(content)
        if vw_match:
            class_def = self._parse_visualworks_class(vw_match, line_number)
            return Chunk(
                chunk_type=ChunkType.CLASS_DEFINITION,
                content=content,
                line_number=line_number,
                class_def=class_def,
            )

        # Check for VisualWorks class extension (e.g., "Circle class")
        ext_match = self.CLASS_EXTENSION_PATTERN.match(content)
        if ext_match:
            # This is a class-side extension marker in VisualWorks
            return Chunk(
                chunk_type=ChunkType.EXPRESSION,
                content=content,
                line_number=line_number,
            )

        # If we're in a method context, this is a method body
        if self._current_class:
            method_def = self._parse_method_body(content, line_number)
            chunk = Chunk(
                chunk_type=ChunkType.METHOD_BODY,
                content=content,
                line_number=line_number,
                method_def=method_def,
            )
            return chunk

        # Default: treat as expression
        return Chunk(
            chunk_type=ChunkType.EXPRESSION,
            content=content,
            line_number=line_number,
        )

    def _parse_standard_class(self, match: re.Match, line_number: int = 0) -> ClassDefinition:
        """Parse a standard Squeak/Pharo class definition."""
        superclass = match.group(1)
        name = match.group(2)
        inst_vars = self._parse_variable_names(match.group(3))
        class_vars = self._parse_variable_names(match.group(4))
        pool_dicts = self._parse_variable_names(match.group(5))
        category = match.group(6)

        return ClassDefinition(
            name=name,
            superclass=superclass,
            instance_variables=inst_vars,
            class_variables=class_vars,
            pool_dictionaries=pool_dicts,
            category=category,
            line_number=line_number,
        )

    def _parse_visualworks_class(self, match: re.Match, line_number: int = 0) -> ClassDefinition:
        """Parse a VisualWorks class definition."""
        name = match.group(1)
        superclass_ref = match.group(2)  # e.g., "Core.Object"
        # indexed_type = match.group(3)  # e.g., "none"
        is_private = match.group(4) == "true"
        inst_vars = self._parse_variable_names(match.group(5))
        class_inst_vars = self._parse_variable_names(match.group(6))
        # imports = match.group(7)
        category = match.group(8)

        # Extract simple class name from namespace reference
        superclass = superclass_ref.split(".")[-1] if "." in superclass_ref else superclass_ref

        return ClassDefinition(
            name=name,
            superclass=superclass,
            instance_variables=inst_vars,
            class_instance_variables=class_inst_vars,
            category=category,
            is_private=is_private,
            namespace=superclass_ref.rsplit(".", 1)[0] if "." in superclass_ref else "",
            line_number=line_number,
        )

    def _parse_variable_names(self, var_string: str) -> list[str]:
        """Parse space-separated variable names."""
        if not var_string:
            return []
        return [v.strip() for v in var_string.split() if v.strip()]

    def _parse_method_body(self, content: str, line_number: int = 0) -> MethodDefinition:
        """
        Parse a method body chunk.

        Args:
            content: The method source code
            line_number: Line number where method starts

        Returns:
            MethodDefinition with parsed selector and source
        """
        selector = self._extract_selector(content)

        return MethodDefinition(
            selector=selector,
            class_name=self._current_class or "",
            category=self._current_category or "",
            source=content,
            is_class_method=self._is_class_side,
            stamp=self._current_stamp,
            line_number=line_number,
        )

    def _extract_selector(self, method_source: str) -> str:
        """
        Extract the method selector from source code.

        Handles:
        - Unary: `area` -> "area"
        - Binary: `+ other` -> "+"
        - Keyword: `at: index put: value` -> "at:put:"

        Args:
            method_source: The method source code

        Returns:
            The method selector string
        """
        lines = method_source.strip().split("\n")
        if not lines:
            return ""

        # First line(s) contain the selector
        first_line = lines[0].strip()

        # Remove any leading comment
        if first_line.startswith('"'):
            # Find end of comment
            end_quote = first_line.find('"', 1)
            if end_quote > 0:
                first_line = first_line[end_quote + 1:].strip()

        # Check for keyword selector (contains colons followed by parameter names)
        keyword_pattern = re.compile(r"(\w+:)\s*\w+")
        keywords = keyword_pattern.findall(first_line)
        if keywords:
            return "".join(keywords)

        # Check for binary selector
        binary_pattern = re.compile(r"^([+\-*/\\<>=@%|&?,~]+)\s+\w+")
        binary_match = binary_pattern.match(first_line)
        if binary_match:
            return binary_match.group(1)

        # Unary selector - just the first word
        unary_pattern = re.compile(r"^(\w+)")
        unary_match = unary_pattern.match(first_line)
        if unary_match:
            return unary_match.group(1)

        return first_line.split()[0] if first_line.split() else ""

    def get_classes(self, chunks: list[Chunk]) -> list[ClassDefinition]:
        """
        Extract all class definitions from parsed chunks.

        Args:
            chunks: List of parsed chunks

        Returns:
            List of ClassDefinition objects
        """
        classes = []
        class_comments = {}

        # First pass: collect class comments
        for chunk in chunks:
            if chunk.chunk_type == ChunkType.CLASS_COMMENT and chunk.class_def:
                # The next EXPRESSION chunk after this is the actual comment
                class_name = chunk.class_def.name
                # Store for lookup
                class_comments[class_name] = None

        # Second pass: collect classes and associate comments
        for i, chunk in enumerate(chunks):
            if chunk.chunk_type == ChunkType.CLASS_DEFINITION and chunk.class_def:
                class_def = chunk.class_def
                # Look for associated comment
                if class_def.name in class_comments:
                    # Find the comment content in subsequent chunks
                    for j in range(i + 1, min(i + 3, len(chunks))):
                        if chunks[j].chunk_type == ChunkType.EXPRESSION:
                            # Check if this looks like a comment (just text, no code)
                            content = chunks[j].content
                            if not any(c in content for c in [":", ":=", "^"]):
                                class_def.comment = content
                                break
                classes.append(class_def)

        return classes

    def get_methods(self, chunks: list[Chunk]) -> list[MethodDefinition]:
        """
        Extract all method definitions from parsed chunks.

        Args:
            chunks: List of parsed chunks

        Returns:
            List of MethodDefinition objects
        """
        methods = []

        for chunk in chunks:
            if chunk.chunk_type == ChunkType.METHOD_BODY and chunk.method_def:
                methods.append(chunk.method_def)

        return methods

    def detect_dialect(self, code: str) -> str:
        """
        Detect the Smalltalk dialect from file-out content.

        Args:
            code: The file-out source code

        Returns:
            Dialect identifier: "visualworks", "squeak", "pharo", or "standard"
        """
        # Check for VisualWorks markers
        if "Smalltalk defineClass:" in code or "#{" in code:
            return "visualworks"

        # Check for Pharo markers
        if "Pharo" in code or "'From Pharo" in code:
            return "pharo"

        # Check for Squeak markers
        if "Squeak" in code or "'From Squeak" in code:
            return "squeak"

        # Default to standard
        return "standard"
