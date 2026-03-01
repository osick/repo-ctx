"""LLM prompt templates for documentation enhancement."""

import json
import logging
import re

logger = logging.getLogger("repo_ctx.analysis.prompts")


def sanitize_json_string(content: str) -> str:
    """Sanitize JSON string to fix common LLM output issues.

    Handles:
    - Invalid escape sequences (\\U, \\x, etc.)
    - Unescaped backslashes in file paths
    - Trailing commas
    - Single quotes instead of double quotes

    Args:
        content: Raw JSON string from LLM.

    Returns:
        Sanitized JSON string.
    """
    if not content:
        return content

    # Fix invalid escape sequences by escaping backslashes that aren't valid escapes
    # Valid JSON escapes: \", \\, \/, \b, \f, \n, \r, \t, \uXXXX
    def fix_escapes(match):
        char = match.group(1)
        if char in ('"', '\\', '/', 'b', 'f', 'n', 'r', 't'):
            return match.group(0)  # Valid escape, keep as-is
        elif char == 'u':
            # Check if it's a valid \uXXXX sequence
            full_match = match.group(0)
            if len(full_match) >= 6:
                return full_match  # Potentially valid unicode escape
            return '\\\\' + char  # Invalid, escape the backslash
        else:
            # Invalid escape like \U, \x, \d - escape the backslash
            return '\\\\' + char

    # Pattern matches backslash followed by any character
    content = re.sub(r'\\(.)', fix_escapes, content)

    # Remove trailing commas before } or ]
    content = re.sub(r',(\s*[}\]])', r'\1', content)

    return content

# File-level enhancement prompt - analyzes source code and documents all symbols at once
FILE_ENHANCEMENT_PROMPT = """Analyze this source file and provide documentation for the listed symbols.

## Source File: {file_path}
## Language: {language}

```{language}
{source_code}
```

## Symbols to Document:
{symbols_list}

## Instructions:
1. Read and understand the source code
2. For each symbol listed above, provide a clear 1-3 sentence documentation
3. If existing documentation is already good, keep it or improve it slightly
4. Focus on WHAT the symbol does, not implementation details
5. For classes: describe purpose and key responsibilities
6. For functions/methods: describe what it does, key parameters, and return value

Respond with valid JSON only (no markdown, no explanation):
{{
  "file_documentation": "2-3 sentence summary of what this file/module does",
  "symbols": {{
    "SymbolName1": "Documentation for SymbolName1...",
    "SymbolName2": "Documentation for SymbolName2..."
  }}
}}
"""

# Symbol explanation prompt - evaluates and enhances symbol documentation
SYMBOL_EXPLANATION_PROMPT = """Analyze this code symbol and provide a concise explanation.

Symbol: {name}
Type: {symbol_type}
Signature: {signature}
Existing Documentation: {documentation}

Instructions:
1. Evaluate if the existing documentation is sufficient:
   - Does it explain what the symbol does?
   - Does it document parameters and return value (if applicable)?
   - Does it mention important side effects or considerations?

2. If sufficient: respond with QUALITY: SUFFICIENT
3. If insufficient or missing: provide a clear 2-3 sentence explanation

Response format (use exactly this format):
QUALITY: [SUFFICIENT|ENHANCED|MISSING]
EXPLANATION: [Your explanation or "See documentation" if sufficient]
"""

# Documentation sufficiency check - quick evaluation
SUFFICIENCY_CHECK_PROMPT = """Evaluate if this documentation is sufficient for understanding the code.

Symbol: {name}
Type: {symbol_type}
Signature: {signature}
Documentation: {documentation}

Criteria for "sufficient":
- Explains what the symbol does
- Documents parameters (if function/method)
- Documents return value (if applicable)
- Notes important side effects

Respond with only one word: SUFFICIENT or INSUFFICIENT
"""

# File summary prompt - aggregates symbol information into file-level summary
FILE_SUMMARY_PROMPT = """Summarize this source file based on its symbols.

File: {file_path}
Language: {language}
Line Count: {line_count}

Classes ({class_count}):
{classes}

Functions ({function_count}):
{functions}

Symbol Documentation:
{symbol_docs}

Provide a 2-4 sentence summary explaining:
- The main purpose of this file
- Key classes and their responsibilities
- Key functions and what they do
"""

# Class summary prompt - generates class-level documentation
CLASS_SUMMARY_PROMPT = """Summarize this class based on its structure and methods.

Class: {name}
File: {file_path}
Parent Class: {parent_class}
Interfaces: {interfaces}

Methods ({method_count}):
{methods}

Attributes:
{attributes}

Provide a 2-3 sentence summary explaining:
- The purpose of this class
- Key functionality it provides
- Its role in the class hierarchy (if applicable)
"""

# Module summary prompt - aggregates file information into module-level summary
MODULE_SUMMARY_PROMPT = """Summarize this module based on its contents.

Module: {name}
Path: {path}
Has __init__.py: {has_init}

Files ({file_count}):
{files}

Submodules:
{submodules}

File Summaries:
{file_docs}

Provide a 2-4 sentence summary explaining:
- The main purpose of this module
- Key components and their functionality
- Its role in the overall architecture
"""

# Package summary prompt - top-level package documentation
PACKAGE_SUMMARY_PROMPT = """Summarize this package based on its modules.

Package: {name}
Version: {version}
Total Modules: {module_count}
Total Files: {file_count}
Total Symbols: {symbol_count}

Modules:
{modules}

Public API:
{public_api}

Module Summaries:
{module_docs}

Provide a 3-5 sentence summary explaining:
- The main purpose of this package
- Key features and capabilities
- Target use cases
- Architecture overview (if complex)
"""


def format_symbol_prompt(
    name: str,
    symbol_type: str,
    signature: str | None,
    documentation: str | None,
) -> str:
    """Format the symbol explanation prompt.

    Args:
        name: Symbol name.
        symbol_type: Type of symbol (function, class, method, etc.).
        signature: Symbol signature.
        documentation: Existing documentation.

    Returns:
        Formatted prompt string.
    """
    return SYMBOL_EXPLANATION_PROMPT.format(
        name=name,
        symbol_type=symbol_type,
        signature=signature or "N/A",
        documentation=documentation or "None",
    )


def format_file_prompt(
    file_path: str,
    language: str,
    line_count: int,
    classes: list[str],
    functions: list[str],
    symbol_docs: list[tuple[str, str]],  # (name, doc)
) -> str:
    """Format the file summary prompt.

    Args:
        file_path: Path to file.
        language: Programming language.
        line_count: Number of lines.
        classes: List of class names.
        functions: List of function names.
        symbol_docs: List of (name, documentation) tuples.

    Returns:
        Formatted prompt string.
    """
    classes_text = "\n".join(f"  - {c}" for c in classes) if classes else "  None"
    functions_text = "\n".join(f"  - {f}" for f in functions) if functions else "  None"
    symbol_docs_text = "\n".join(
        f"  - {name}: {doc[:100]}..." if len(doc) > 100 else f"  - {name}: {doc}"
        for name, doc in symbol_docs
    ) if symbol_docs else "  None"

    return FILE_SUMMARY_PROMPT.format(
        file_path=file_path,
        language=language,
        line_count=line_count,
        class_count=len(classes),
        classes=classes_text,
        function_count=len(functions),
        functions=functions_text,
        symbol_docs=symbol_docs_text,
    )


def format_class_prompt(
    name: str,
    file_path: str,
    parent_class: str | None,
    interfaces: list[str],
    methods: list[str],
    attributes: list[str],
) -> str:
    """Format the class summary prompt.

    Args:
        name: Class name.
        file_path: Path to containing file.
        parent_class: Parent class name.
        interfaces: List of implemented interfaces.
        methods: List of method names.
        attributes: List of attribute names.

    Returns:
        Formatted prompt string.
    """
    methods_text = "\n".join(f"  - {m}" for m in methods) if methods else "  None"
    attributes_text = "\n".join(f"  - {a}" for a in attributes) if attributes else "  None"
    interfaces_text = ", ".join(interfaces) if interfaces else "None"

    return CLASS_SUMMARY_PROMPT.format(
        name=name,
        file_path=file_path,
        parent_class=parent_class or "None",
        interfaces=interfaces_text,
        method_count=len(methods),
        methods=methods_text,
        attributes=attributes_text,
    )


def format_module_prompt(
    name: str,
    path: str,
    has_init: bool,
    files: list[str],
    submodules: list[str],
    file_docs: list[tuple[str, str]],  # (file_path, doc)
) -> str:
    """Format the module summary prompt.

    Args:
        name: Module name.
        path: Module path.
        has_init: Whether module has __init__.py.
        files: List of file paths.
        submodules: List of submodule names.
        file_docs: List of (file_path, documentation) tuples.

    Returns:
        Formatted prompt string.
    """
    files_text = "\n".join(f"  - {f}" for f in files) if files else "  None"
    submodules_text = "\n".join(f"  - {s}" for s in submodules) if submodules else "  None"
    file_docs_text = "\n".join(
        f"  - {path}: {doc[:150]}..." if len(doc) > 150 else f"  - {path}: {doc}"
        for path, doc in file_docs
    ) if file_docs else "  None"

    return MODULE_SUMMARY_PROMPT.format(
        name=name,
        path=path,
        has_init="Yes" if has_init else "No",
        file_count=len(files),
        files=files_text,
        submodules=submodules_text,
        file_docs=file_docs_text,
    )


def format_package_prompt(
    name: str,
    version: str | None,
    modules: list[str],
    public_api: list[str],
    module_docs: list[tuple[str, str]],  # (module_name, doc)
    file_count: int,
    symbol_count: int,
) -> str:
    """Format the package summary prompt.

    Args:
        name: Package name.
        version: Package version.
        modules: List of module names.
        public_api: List of public API symbols.
        module_docs: List of (module_name, documentation) tuples.
        file_count: Total number of files.
        symbol_count: Total number of symbols.

    Returns:
        Formatted prompt string.
    """
    modules_text = "\n".join(f"  - {m}" for m in modules) if modules else "  None"
    api_text = "\n".join(f"  - {a}" for a in public_api[:20]) if public_api else "  None"
    if len(public_api) > 20:
        api_text += f"\n  ... and {len(public_api) - 20} more"
    module_docs_text = "\n".join(
        f"  - {name}: {doc[:150]}..." if len(doc) > 150 else f"  - {name}: {doc}"
        for name, doc in module_docs
    ) if module_docs else "  None"

    return PACKAGE_SUMMARY_PROMPT.format(
        name=name,
        version=version or "N/A",
        module_count=len(modules),
        file_count=file_count,
        symbol_count=symbol_count,
        modules=modules_text,
        public_api=api_text,
        module_docs=module_docs_text,
    )


def parse_symbol_response(response: str) -> tuple[str, str]:
    """Parse the LLM response for symbol explanation.

    Args:
        response: LLM response text.

    Returns:
        Tuple of (quality, explanation).
    """
    quality = "enhanced"
    explanation = ""

    lines = response.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line.upper().startswith("QUALITY:"):
            quality_value = line.split(":", 1)[1].strip().upper()
            if quality_value in ("SUFFICIENT", "ENHANCED", "MISSING"):
                quality = quality_value.lower()
        elif line.upper().startswith("EXPLANATION:"):
            explanation = line.split(":", 1)[1].strip()

    # If no structured response, treat entire response as explanation
    if not explanation and response:
        explanation = response.strip()

    return quality, explanation


def format_file_enhancement_prompt(
    file_path: str,
    language: str,
    source_code: str,
    symbols: list[dict],
    max_code_chars: int = 12000,
) -> str:
    """Format the file enhancement prompt with source code context.

    Args:
        file_path: Path to the source file.
        language: Programming language.
        source_code: Full source code of the file.
        symbols: List of symbol dictionaries with name, type, documentation.
        max_code_chars: Maximum characters of source code to include.

    Returns:
        Formatted prompt string.
    """
    # Truncate source code if too long
    if len(source_code) > max_code_chars:
        source_code = source_code[:max_code_chars] + "\n\n... [truncated]"

    # Build symbols list with existing docs
    symbols_lines = []
    for s in symbols:
        name = s.get("name", "")
        stype = s.get("type", "symbol")
        existing_doc = s.get("documentation", "")
        if existing_doc:
            symbols_lines.append(f"- {name} ({stype}): existing doc: \"{existing_doc[:100]}...\"" if len(existing_doc) > 100 else f"- {name} ({stype}): existing doc: \"{existing_doc}\"")
        else:
            symbols_lines.append(f"- {name} ({stype}): no documentation")

    symbols_list = "\n".join(symbols_lines) if symbols_lines else "None"

    return FILE_ENHANCEMENT_PROMPT.format(
        file_path=file_path,
        language=language,
        source_code=source_code,
        symbols_list=symbols_list,
    )


def parse_file_enhancement_response(response: str) -> dict:
    """Parse the LLM response for file enhancement.

    Handles common LLM JSON issues like invalid escapes and trailing commas.

    Args:
        response: LLM response text (should be JSON).

    Returns:
        Dictionary with file_documentation and symbols dict.
    """
    default = {"file_documentation": None, "symbols": {}}

    if not response:
        return default

    # Try to extract JSON from the response
    content = response.strip()

    # Remove markdown code blocks if present
    if content.startswith("```"):
        lines = content.split("\n")
        # Find start and end of code block
        start_idx = 1 if lines[0].startswith("```") else 0
        end_idx = len(lines)
        for i in range(len(lines) - 1, 0, -1):
            if lines[i].strip() == "```":
                end_idx = i
                break
        content = "\n".join(lines[start_idx:end_idx])

    # Attempt 1: Try parsing as-is
    try:
        data = json.loads(content)
        return {
            "file_documentation": data.get("file_documentation"),
            "symbols": data.get("symbols", {}),
        }
    except json.JSONDecodeError:
        pass  # Try sanitization

    # Attempt 2: Try with sanitized JSON
    try:
        sanitized = sanitize_json_string(content)
        data = json.loads(sanitized)
        logger.debug("JSON parsing succeeded after sanitization")
        return {
            "file_documentation": data.get("file_documentation"),
            "symbols": data.get("symbols", {}),
        }
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse file enhancement response as JSON: {e}")
        logger.debug(f"Original response (first 500 chars): {content[:500]}")
        logger.debug(f"Sanitized response (first 500 chars): {sanitized[:500]}")

    # Attempt 3: Try to extract JSON object using regex as last resort
    try:
        # Find JSON object boundaries
        json_match = re.search(r'\{[^{}]*"file_documentation"[^{}]*\}', content, re.DOTALL)
        if json_match:
            extracted = sanitize_json_string(json_match.group())
            data = json.loads(extracted)
            logger.debug("JSON parsing succeeded after regex extraction")
            return {
                "file_documentation": data.get("file_documentation"),
                "symbols": data.get("symbols", {}),
            }
    except (json.JSONDecodeError, AttributeError):
        pass

    return default
