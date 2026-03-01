"""
Parser for Joern CPG query output.

This module parses the structured output from CPGQL queries
and converts it into Python data structures.
"""

import json
import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CPGComment:
    """Parsed comment from CPG."""

    file_path: str
    line_number: int
    code: str


@dataclass
class CPGMethod:
    """Parsed method/function from CPG."""

    name: str
    full_name: str
    filename: str
    line_start: int
    line_end: int
    signature: str
    parameters: list[tuple[str, str]] = field(default_factory=list)
    is_external: bool = False


@dataclass
class CPGType:
    """Parsed type declaration from CPG."""

    name: str
    full_name: str
    filename: str
    line_start: int
    inherits_from: list[str] = field(default_factory=list)
    is_external: bool = False


@dataclass
class CPGMember:
    """Parsed class member from CPG."""

    name: str
    type_name: str
    parent_type: str


@dataclass
class CPGCall:
    """Parsed call site from CPG."""

    caller: str
    callee: str
    line_number: int


@dataclass
class CPGDataFlow:
    """Parsed data flow from CPG."""

    source_file: str
    source_line: int
    source_code: str
    sink_file: str
    sink_line: int
    sink_code: str


@dataclass
class CPGParseResult:
    """Complete parsed result from CPG extraction."""

    methods: list[CPGMethod] = field(default_factory=list)
    types: list[CPGType] = field(default_factory=list)
    members: list[CPGMember] = field(default_factory=list)
    calls: list[CPGCall] = field(default_factory=list)
    comments: list[CPGComment] = field(default_factory=list)
    data_flows: list[CPGDataFlow] = field(default_factory=list)
    raw_output: str = ""


class CPGParser:
    """
    Parser for CPGQL query output.

    Handles various output formats from Joern queries and converts
    them into structured Python objects.
    """

    # Regex patterns for parsing
    SCALA_LIST_PATTERN = re.compile(r"List\((.*)\)", re.DOTALL)
    SCALA_STRING_PATTERN = re.compile(r'"([^"]*)"')

    def __init__(self):
        """Initialize the parser."""
        pass

    def parse_output(
        self,
        output: str,
        comments_output: str | None = None,
        data_flow_output: str | None = None,
    ) -> CPGParseResult:
        """
        Parse combined extraction output.

        Expects output from QUERY_EXTRACT_ALL format with lines like:
        - METHOD|name|fullName|filename|lineStart|lineEnd|signature|params
        - TYPE|name|fullName|filename|lineStart|inheritsFrom
        - MEMBER|name|typeName|parentType
        - CALL|caller|callee|lineNumber

        Args:
            output: Raw output from Joern query.
            comments_output: Optional raw output from comments query.
            data_flow_output: Optional raw output from data flow query.

        Returns:
            CPGParseResult with parsed data.
        """
        result = CPGParseResult(raw_output=output)

        # Clean output - remove Scala List wrapper if present
        cleaned = self._clean_scala_output(output)

        for line in cleaned.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            parts = line.split("|")
            if len(parts) < 2:
                continue

            record_type = parts[0].upper()

            try:
                if record_type == "METHOD":
                    method = self._parse_method_line(parts)
                    if method:
                        result.methods.append(method)
                elif record_type == "TYPE":
                    type_decl = self._parse_type_line(parts)
                    if type_decl:
                        result.types.append(type_decl)
                elif record_type == "MEMBER":
                    member = self._parse_member_line(parts)
                    if member:
                        result.members.append(member)
                elif record_type == "CALL":
                    call = self._parse_call_line(parts)
                    if call:
                        result.calls.append(call)
            except Exception as e:
                logger.warning(f"Failed to parse line: {line}, error: {e}")

        if comments_output:
            result.comments = self._parse_comments(comments_output)

        if data_flow_output:
            result.data_flows = self._parse_data_flows(data_flow_output)

        return result

    def _parse_data_flows(self, output: str) -> list[CPGDataFlow]:
        """
        Parse output from QUERY_DATA_FLOW.

        This is a placeholder implementation as the output format of
        `reachableBy` is complex. It assumes a simplified format.
        """
        flows = []
        # Placeholder parsing. The actual output is a graph path.
        # A real implementation would need to parse the path structure.
        # For now, we'll assume a simplified pipe-separated format per line.
        # "source_file|source_line|source_code|sink_file|sink_line|sink_code"
        cleaned = self._clean_scala_output(output)
        for line in cleaned.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = line.split("|")
            if len(parts) >= 6:
                flows.append(
                    CPGDataFlow(
                        source_file=parts[0],
                        source_line=self._safe_int(parts[1]),
                        source_code=parts[2],
                        sink_file=parts[3],
                        sink_line=self._safe_int(parts[4]),
                        sink_code=parts[5],
                    )
                )
        return flows

    def _parse_comments(self, output: str) -> list[CPGComment]:
        """
        Parse output from QUERY_COMMENTS.

        Format: filename|lineNumber|code
        """
        comments = []
        cleaned = self._clean_scala_output(output)

        for line in cleaned.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            parts = line.split("|")
            if len(parts) >= 3:
                comments.append(
                    CPGComment(
                        file_path=parts[0],
                        line_number=self._safe_int(parts[1]),
                        code="|".join(parts[2:]),
                    )
                )

        return comments

    def _clean_scala_output(self, output: str) -> str:
        """
        Clean Scala output format.

        Handles:
        - List(...) wrappers
        - Scala string escaping
        - Extra whitespace
        """
        # Remove List() wrapper
        match = self.SCALA_LIST_PATTERN.search(output)
        if match:
            inner = match.group(1)
            # Extract strings from List
            strings = self.SCALA_STRING_PATTERN.findall(inner)
            return "\n".join(strings)

        # If output looks like JSON array
        if output.strip().startswith("["):
            try:
                items = json.loads(output)
                if isinstance(items, list):
                    return "\n".join(str(item) for item in items)
            except json.JSONDecodeError:
                pass

        return output

    def _parse_method_line(self, parts: list[str]) -> CPGMethod | None:
        """
        Parse a METHOD line.

        Format: METHOD|name|fullName|filename|lineStart|lineEnd|signature|params
        """
        if len(parts) < 7:
            return None

        parameters = []
        if len(parts) > 7 and parts[7]:
            # Parse parameters: "name1:type1;name2:type2"
            for param in parts[7].split(";"):
                if ":" in param:
                    pname, ptype = param.split(":", 1)
                    parameters.append((pname, ptype))

        return CPGMethod(
            name=parts[1],
            full_name=parts[2],
            filename=parts[3],
            line_start=self._safe_int(parts[4]),
            line_end=self._safe_int(parts[5]),
            signature=parts[6],
            parameters=parameters,
        )

    def _parse_type_line(self, parts: list[str]) -> CPGType | None:
        """
        Parse a TYPE line.

        Format: TYPE|name|fullName|filename|lineStart|inheritsFrom
        """
        if len(parts) < 5:
            return None

        inherits = []
        if len(parts) > 5 and parts[5]:
            inherits = [t.strip() for t in parts[5].split(";") if t.strip()]

        return CPGType(
            name=parts[1],
            full_name=parts[2],
            filename=parts[3],
            line_start=self._safe_int(parts[4]),
            inherits_from=inherits,
        )

    def _parse_member_line(self, parts: list[str]) -> CPGMember | None:
        """
        Parse a MEMBER line.

        Format: MEMBER|name|typeName|parentType
        """
        if len(parts) < 4:
            return None

        return CPGMember(
            name=parts[1],
            type_name=parts[2],
            parent_type=parts[3],
        )

    def _parse_call_line(self, parts: list[str]) -> CPGCall | None:
        """
        Parse a CALL line.

        Format: CALL|caller|callee|lineNumber
        """
        if len(parts) < 4:
            return None

        return CPGCall(
            caller=parts[1],
            callee=parts[2],
            line_number=self._safe_int(parts[3]),
        )

    def parse_methods(self, output: str) -> list[CPGMethod]:
        """
        Parse output from QUERY_ALL_METHODS.

        Format: name|fullName|filename|lineStart|lineEnd|signature
        """
        methods = []
        cleaned = self._clean_scala_output(output)

        for line in cleaned.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            parts = line.split("|")
            if len(parts) >= 6:
                methods.append(
                    CPGMethod(
                        name=parts[0],
                        full_name=parts[1],
                        filename=parts[2],
                        line_start=self._safe_int(parts[3]),
                        line_end=self._safe_int(parts[4]),
                        signature=parts[5],
                    )
                )

        return methods

    def parse_types(self, output: str) -> list[CPGType]:
        """
        Parse output from QUERY_ALL_TYPES.

        Format: name|fullName|filename|lineStart|inheritsFrom
        """
        types = []
        cleaned = self._clean_scala_output(output)

        for line in cleaned.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            parts = line.split("|")
            if len(parts) >= 4:
                inherits = []
                if len(parts) > 4 and parts[4]:
                    inherits = [t.strip() for t in parts[4].split(",") if t.strip()]

                types.append(
                    CPGType(
                        name=parts[0],
                        full_name=parts[1],
                        filename=parts[2],
                        line_start=self._safe_int(parts[3]),
                        inherits_from=inherits,
                    )
                )

        return types

    def parse_calls(self, output: str) -> list[CPGCall]:
        """
        Parse output from QUERY_CALL_GRAPH.

        Format: caller|callee|lineNumber
        """
        calls = []
        cleaned = self._clean_scala_output(output)

        for line in cleaned.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            parts = line.split("|")
            if len(parts) >= 3:
                calls.append(
                    CPGCall(
                        caller=parts[0],
                        callee=parts[1],
                        line_number=self._safe_int(parts[2]),
                    )
                )

        return calls

    def parse_inheritance(self, output: str) -> dict[str, list[str]]:
        """
        Parse output from QUERY_INHERITANCE.

        Format: typeName|baseType1,baseType2

        Returns:
            Dictionary mapping type names to their base types.
        """
        inheritance = {}
        cleaned = self._clean_scala_output(output)

        for line in cleaned.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            parts = line.split("|")
            if len(parts) >= 2:
                type_name = parts[0]
                bases = [t.strip() for t in parts[1].split(",") if t.strip()]
                inheritance[type_name] = bases

        return inheritance

    def parse_complexity(self, output: str) -> dict[str, int]:
        """
        Parse output from QUERY_COMPLEXITY.

        Format: methodName|controlStructureCount

        Returns:
            Dictionary mapping method names to complexity values.
        """
        complexity = {}
        cleaned = self._clean_scala_output(output)

        for line in cleaned.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            parts = line.split("|")
            if len(parts) >= 2:
                complexity[parts[0]] = self._safe_int(parts[1])

        return complexity

    def parse_parameters(self, output: str) -> dict[str, list[tuple[str, str]]]:
        """
        Parse output from QUERY_PARAMETERS.

        Format: methodName|param1:type1,param2:type2

        Returns:
            Dictionary mapping method names to parameter lists.
        """
        parameters = {}
        cleaned = self._clean_scala_output(output)

        for line in cleaned.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            parts = line.split("|")
            if len(parts) >= 2:
                method_name = parts[0]
                params = []
                if parts[1]:
                    for param in parts[1].split(","):
                        if ":" in param:
                            pname, ptype = param.split(":", 1)
                            params.append((pname.strip(), ptype.strip()))
                parameters[method_name] = params

        return parameters

    def parse_simple_list(self, output: str) -> list[str]:
        """
        Parse a simple list of strings.

        Handles Scala List() format and JSON arrays.
        """
        cleaned = self._clean_scala_output(output)
        return [line.strip() for line in cleaned.split("\n") if line.strip()]

    def _safe_int(self, value: str, default: int = 0) -> int:
        """Safely convert string to int."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
