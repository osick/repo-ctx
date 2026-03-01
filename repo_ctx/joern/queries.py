"""
Built-in CPGQL query templates for common code analysis tasks.

These queries can be used directly with JoernCLI.run_query() or
as templates for custom queries.
"""

# =============================================================================
# METHOD/FUNCTION QUERIES
# =============================================================================

QUERY_ALL_METHODS = """cpg.method.filter(_.isExternal == false).map(m =>
  s"${m.name}|${m.fullName}|${m.filename}|${m.lineNumber.getOrElse(0)}|${m.lineNumberEnd.getOrElse(0)}|${m.signature}"
).l"""

QUERY_METHOD_NAMES = """cpg.method.filter(_.isExternal == false).name.l"""

QUERY_METHOD_SIGNATURES = """cpg.method.filter(_.isExternal == false).map(m =>
  s"${m.name}: ${m.signature}"
).l"""

QUERY_METHOD_LOCATIONS = """cpg.method.filter(_.isExternal == false).map(m =>
  s"${m.filename}:${m.lineNumber.getOrElse(0)} ${m.name}"
).l"""

# =============================================================================
# TYPE/CLASS QUERIES
# =============================================================================

QUERY_ALL_TYPES = """cpg.typeDecl.filter(_.isExternal == false).map(t =>
  s"${t.name}|${t.fullName}|${t.filename}|${t.lineNumber.getOrElse(0)}|${t.inheritsFromTypeFullName.mkString(",")}"
).l"""

QUERY_TYPE_NAMES = """cpg.typeDecl.filter(_.isExternal == false).name.l"""

QUERY_INHERITANCE = """cpg.typeDecl.filter(_.isExternal == false)
  .filter(_.inheritsFromTypeFullName.nonEmpty)
  .map(t => s"${t.name}|${t.inheritsFromTypeFullName.mkString(",")}")
  .l"""

# =============================================================================
# MEMBER/FIELD QUERIES
# =============================================================================

QUERY_ALL_MEMBERS = """cpg.member.map(m =>
  s"${m.typeDecl.name.headOption.getOrElse("")}|${m.name}|${m.typeFullName}"
).l"""

# =============================================================================
# CALL GRAPH QUERIES
# =============================================================================

QUERY_CALL_GRAPH = """cpg.call.filter(c => c.method.isExternal == false).map(c =>
  s"${c.method.name.headOption.getOrElse("")}|${c.name}|${c.lineNumber.getOrElse(0)}"
).l"""

QUERY_CALLS_IN_METHOD = """cpg.method.name("{method_name}").call.map(c =>
  s"${c.name}|${c.lineNumber.getOrElse(0)}|${c.code}"
).l"""

# =============================================================================
# PARAMETER QUERIES
# =============================================================================

QUERY_PARAMETERS = """cpg.method.filter(_.isExternal == false).map(m =>
  s"${m.name}|${m.parameter.map(p => s"${p.name}:${p.typeFullName}").mkString(",")}"
).l"""

QUERY_METHOD_PARAMETERS = """cpg.method.name("{method_name}").parameter.map(p =>
  s"${p.name}|${p.typeFullName}|${p.index}"
).l"""

# =============================================================================
# DATA FLOW QUERIES
# =============================================================================

QUERY_DATA_FLOW = """cpg.call.where(_.method.isExternal).reachableBy(cpg.call.argument).l"""

# =============================================================================
# LOCAL VARIABLE QUERIES
# =============================================================================

QUERY_LOCALS = """cpg.local.map(l =>
  s"${l.method.name.headOption.getOrElse("")}|${l.name}|${l.typeFullName}"
).l"""

# =============================================================================
# COMPLEXITY/METRICS QUERIES
# =============================================================================

QUERY_COMPLEXITY = """cpg.method.filter(_.isExternal == false).map(m =>
  s"${m.name}|${m.controlStructure.size}"
).l"""

QUERY_LARGE_METHODS = """cpg.method.filter(_.isExternal == false)
  .filter(_.numberOfLines > {threshold})
  .map(m => s"${m.name}|${m.numberOfLines}|${m.filename}")
  .l"""

QUERY_MANY_PARAMETERS = """cpg.method.filter(_.isExternal == false)
  .filter(_.parameter.size > {threshold})
  .map(m => s"${m.name}|${m.parameter.size}")
  .l"""

# =============================================================================
# FILE QUERIES
# =============================================================================

QUERY_FILES = """cpg.file.name.l"""

QUERY_METHODS_BY_FILE = """cpg.file.name("{filename}").method.filter(_.isExternal == false).name.l"""

# =============================================================================
# COMMENT/DOCUMENTATION QUERIES
# =============================================================================

QUERY_COMMENTS = """cpg.comment.map(c =>
  s"${c.filename}|${c.lineNumber.getOrElse(0)}|${c.code.take(100)}"
).l"""

# =============================================================================
# COMBINED EXTRACTION QUERIES
# =============================================================================

# Extracts all symbols in a structured format for parsing
# NOTE: This uses a block expression {} to combine multiple collections
# Filters out Joern internal artifacts: <module>, <init>, <meta*>, ANY, etc.
# Note: Additional filtering happens in mapper.py as backup
QUERY_EXTRACT_ALL = """{
  val methods = cpg.method.filter(_.isExternal == false).filterNot(m => m.name.startsWith("<") || m.name.contains("metaClass")).map(m =>
    s"METHOD|${m.name}|${m.fullName}|${m.filename}|${m.lineNumber.getOrElse(0)}|${m.lineNumberEnd.getOrElse(0)}|${m.signature}|${m.parameter.filterNot(p => p.name == "self" || p.name == "this").map(p => p.name + ":" + p.typeFullName).mkString(";")}"
  ).l
  val types = cpg.typeDecl.filter(_.isExternal == false).filterNot(t => t.name.startsWith("<") || t.name == "ANY" || t.name.contains("meta")).map(t =>
    s"TYPE|${t.name}|${t.fullName}|${t.filename}|${t.lineNumber.getOrElse(0)}|${t.inheritsFromTypeFullName.mkString(";")}"
  ).l
  val members = cpg.member.filterNot(m => m.name.startsWith("<")).map(m =>
    s"MEMBER|${m.name}|${m.typeFullName}|${m.typeDecl.fullName.headOption.getOrElse("")}"
  ).l
  val calls = cpg.call.filter(c => c.method.isExternal == false).filterNot(c => c.name.startsWith("<")).map(c =>
    s"CALL|${c.method.name.headOption.getOrElse("")}|${c.name}|${c.lineNumber.getOrElse(0)}"
  ).l
  methods ++ types ++ members ++ calls
}"""


def format_query(query_template: str, **kwargs) -> str:
    """
    Format a query template with parameters.

    Args:
        query_template: Query template with {param} placeholders.
        **kwargs: Parameters to substitute.

    Returns:
        Formatted query string.
    """
    return query_template.format(**kwargs)


# =============================================================================
# LLM-FRIENDLY QUERIES (filtered, with context)
# =============================================================================

# These queries filter out Joern internal artifacts and provide rich context
# suitable for LLM code analysis.
#
# NOTE: All queries must be single expressions (no val declarations) as they
# are wrapped in: val result = {query}

# Methods with full context, filtering internals
# Output format: name|fullName|file|lineStart|lineEnd|parameters
# Uses parameters instead of signature (works for dynamic languages like Python with type hints)
QUERY_LLM_METHODS = """cpg.method.filter(_.isExternal == false).filterNot(m => m.name.startsWith("<") || m.name.contains("metaClass")).map(m => s"${m.name}|${m.fullName}|${m.filename}|${m.lineNumber.getOrElse(0)}|${m.lineNumberEnd.getOrElse(0)}|${m.parameter.filterNot(p => p.name == "self" || p.name == "this").map(p => p.name + ":" + p.typeFullName.replace("__builtin.", "").replace("ANY", "any")).mkString(", ")}").l"""

# Types with inheritance, filtering internals
# Output format: name|fullName|file|line|inheritsFrom
QUERY_LLM_TYPES = """cpg.typeDecl.filter(_.isExternal == false).filterNot(t => t.name.startsWith("<") || t.name.contains("meta") || t.name == "ANY").map(t => s"${t.name}|${t.fullName}|${t.filename}|${t.lineNumber.getOrElse(0)}|${t.inheritsFromTypeFullName.mkString(",")}").l"""

# Call graph with context, filtering operators
# Output format: caller|callee|line
QUERY_LLM_CALLS = """cpg.call.filter(c => c.method.isExternal == false).filterNot(c => c.name.startsWith("<")).filterNot(c => c.method.name.startsWith("<")).map(c => s"${c.method.name}|${c.name}|${c.lineNumber.getOrElse(0)}").l"""

# Class members/fields
# Output format: className|memberName|type
QUERY_LLM_MEMBERS = """cpg.member.filterNot(m => m.name.startsWith("<")).filterNot(m => m.typeDecl.name.startsWith("<")).map(m => s"${m.typeDecl.name}|${m.name}|${m.typeFullName}").l"""

# Comprehensive code summary - methods grouped by class
# Output format: CLASS:className|file|line|method1,method2,...
QUERY_LLM_SUMMARY = """cpg.typeDecl.filter(_.isExternal == false).filterNot(t => t.name.startsWith("<") || t.name.contains("meta") || t.name == "ANY").map(t => s"CLASS:${t.name}|${t.filename}|${t.lineNumber.getOrElse(0)}|${cpg.method.filter(_.typeDecl.name == t.name).filterNot(_.name.startsWith("<")).name.l.mkString(",")}").l"""

# Query categories for documentation
QUERY_CATEGORIES = {
    "methods": {
        "description": "Queries for extracting method/function information",
        "queries": {
            "QUERY_ALL_METHODS": "Extract all methods with full metadata",
            "QUERY_METHOD_NAMES": "List all method names",
            "QUERY_METHOD_SIGNATURES": "Get method signatures",
            "QUERY_METHOD_LOCATIONS": "Get method file locations",
            "QUERY_LLM_METHODS": "LLM-friendly: methods with context, no internals",
        },
    },
    "types": {
        "description": "Queries for extracting type/class information",
        "queries": {
            "QUERY_ALL_TYPES": "Extract all type declarations",
            "QUERY_TYPE_NAMES": "List all type names",
            "QUERY_INHERITANCE": "Get class inheritance relationships",
            "QUERY_LLM_TYPES": "LLM-friendly: types with context, no internals",
        },
    },
    "calls": {
        "description": "Queries for call graph analysis",
        "queries": {
            "QUERY_CALL_GRAPH": "Extract call relationships",
            "QUERY_CALLS_IN_METHOD": "Get calls within a specific method",
            "QUERY_LLM_CALLS": "LLM-friendly: calls with context, no operators",
        },
    },
    "metrics": {
        "description": "Queries for code metrics and complexity",
        "queries": {
            "QUERY_COMPLEXITY": "Get cyclomatic complexity (control structure count)",
            "QUERY_LARGE_METHODS": "Find methods exceeding line threshold",
            "QUERY_MANY_PARAMETERS": "Find methods with many parameters",
        },
    },
    "llm": {
        "description": "LLM-optimized queries with filtering and rich context",
        "queries": {
            "QUERY_LLM_METHODS": "Methods with file, line, signature (no internals)",
            "QUERY_LLM_TYPES": "Types with inheritance (no internals)",
            "QUERY_LLM_CALLS": "Call graph (no operators)",
            "QUERY_LLM_MEMBERS": "Class members/fields",
            "QUERY_LLM_SUMMARY": "Comprehensive code summary",
        },
    },
}
