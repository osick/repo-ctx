"""
Smalltalk method body parser.

Parses individual method source code to extract:
- Method selector (unary, binary, keyword)
- Parameters
- Temporaries
- Return statements
- Documentation comments
"""

import re
from dataclasses import dataclass, field


@dataclass
class ParsedMethod:
    """Parsed method information."""
    selector: str
    parameters: list[str] = field(default_factory=list)
    temporaries: list[str] = field(default_factory=list)
    documentation: str = ""
    return_expression: str = ""
    body: str = ""
    selector_type: str = "unary"  # unary, binary, keyword


class MethodParser:
    """
    Parser for Smalltalk method source code.

    Handles the LL(1) Smalltalk grammar for method definitions.
    """

    # Pattern for keyword selector parts: `keyword: parameter`
    KEYWORD_PATTERN = re.compile(r"(\w+):\s*(\w+)")

    # Pattern for binary selector: `+ other` or `<= other`
    BINARY_PATTERN = re.compile(r"^([+\-*/\\<>=@%|&?,~]+)\s+(\w+)")

    # Pattern for unary selector: just a word
    UNARY_PATTERN = re.compile(r"^(\w+)\s*$")

    # Pattern for temporaries: `| temp1 temp2 |`
    TEMPORARIES_PATTERN = re.compile(r"^\s*\|\s*([^|]*)\s*\|", re.MULTILINE)

    # Pattern for return statement: `^ expression`
    RETURN_PATTERN = re.compile(r"\^\s*(.+?)(?:\.|$)", re.DOTALL)

    # Pattern for documentation comment: "comment text" (with optional leading whitespace)
    DOC_PATTERN = re.compile(r'^\s*"([^"]*)"', re.MULTILINE)

    def parse(self, source: str) -> ParsedMethod:
        """
        Parse a method's source code.

        Args:
            source: The method source code

        Returns:
            ParsedMethod with extracted information
        """
        lines = source.strip().split("\n")
        if not lines:
            return ParsedMethod(selector="")

        # Parse the selector line(s)
        selector_info = self._parse_selector(lines)

        # Find where the body starts (after selector line)
        body_start = selector_info.get("body_start_line", 1)
        body_lines = lines[body_start:]
        body_text = "\n".join(body_lines)

        # Parse temporaries
        temporaries = self._parse_temporaries(body_text)

        # Parse documentation comment
        documentation = self._parse_documentation(body_text)

        # Parse return expression
        return_expr = self._parse_return(body_text)

        return ParsedMethod(
            selector=selector_info["selector"],
            parameters=selector_info.get("parameters", []),
            temporaries=temporaries,
            documentation=documentation,
            return_expression=return_expr,
            body=body_text,
            selector_type=selector_info.get("type", "unary"),
        )

    def _parse_selector(self, lines: list[str]) -> dict:
        """
        Parse the method selector from the first line(s).

        Args:
            lines: Lines of the method source

        Returns:
            Dictionary with selector, parameters, type, and body_start_line
        """
        if not lines:
            return {"selector": "", "parameters": [], "type": "unary", "body_start_line": 0}

        first_line = lines[0].strip()

        # Try keyword selector first (most complex)
        keywords = self.KEYWORD_PATTERN.findall(first_line)
        if keywords:
            # Multi-keyword or single keyword
            selector = "".join(k[0] + ":" for k in keywords)
            parameters = [k[1] for k in keywords]

            # Check if selector continues on next lines
            body_start = 1
            for i in range(1, len(lines)):
                line = lines[i].strip()
                more_keywords = self.KEYWORD_PATTERN.findall(line)
                if more_keywords and not line.startswith("|") and not line.startswith('"'):
                    selector += "".join(k[0] + ":" for k in more_keywords)
                    parameters.extend(k[1] for k in more_keywords)
                    body_start = i + 1
                else:
                    break

            return {
                "selector": selector,
                "parameters": parameters,
                "type": "keyword",
                "body_start_line": body_start,
            }

        # Try binary selector
        binary_match = self.BINARY_PATTERN.match(first_line)
        if binary_match:
            return {
                "selector": binary_match.group(1),
                "parameters": [binary_match.group(2)],
                "type": "binary",
                "body_start_line": 1,
            }

        # Must be unary selector
        unary_match = re.match(r"^(\w+)", first_line)
        if unary_match:
            return {
                "selector": unary_match.group(1),
                "parameters": [],
                "type": "unary",
                "body_start_line": 1,
            }

        return {"selector": first_line, "parameters": [], "type": "unary", "body_start_line": 1}

    def _parse_temporaries(self, body: str) -> list[str]:
        """
        Parse temporary variable declarations.

        Args:
            body: The method body

        Returns:
            List of temporary variable names
        """
        match = self.TEMPORARIES_PATTERN.search(body)
        if match:
            var_string = match.group(1)
            return [v.strip() for v in var_string.split() if v.strip()]
        return []

    def _parse_documentation(self, body: str) -> str:
        """
        Parse the documentation comment (first string literal).

        Args:
            body: The method body

        Returns:
            Documentation string or empty string
        """
        match = self.DOC_PATTERN.search(body)
        if match:
            return match.group(1).strip()
        return ""

    def _parse_return(self, body: str) -> str:
        """
        Parse the return expression.

        Args:
            body: The method body

        Returns:
            Return expression or empty string
        """
        match = self.RETURN_PATTERN.search(body)
        if match:
            return match.group(1).strip()
        return ""

    def extract_message_sends(self, body: str) -> list[str]:
        """
        Extract message sends from a method body.

        This is a simplified extraction that finds identifiers
        followed by message patterns.

        Args:
            body: The method body

        Returns:
            List of message selectors found in the body
        """
        messages = []

        # Find unary message sends: `receiver selector`
        unary_pattern = re.compile(r"(\w+)\s+(\w+)(?:\s|\.|\]|\))")
        for match in unary_pattern.finditer(body):
            messages.append(match.group(2))

        # Find keyword message sends: `receiver key1: arg1 key2: arg2`
        keyword_pattern = re.compile(r"(\w+:)(?:\s*\w+\s*)+")
        for match in keyword_pattern.finditer(body):
            # Collect all keywords in this message
            full_match = match.group(0)
            keywords = re.findall(r"(\w+):", full_match)
            if keywords:
                messages.append("".join(k + ":" for k in keywords))

        return list(set(messages))  # Remove duplicates
