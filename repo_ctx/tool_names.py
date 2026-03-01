"""Tool naming conventions for repo-ctx MCP server.

All tools use the ctx-<action> naming convention.
"""

# =============================================================================
# CANONICAL TOOLS (ctx- prefix)
# =============================================================================

CTX_TOOLS = {
    # Repository management
    "ctx-index": "Index a repository or group",
    "ctx-list": "List indexed repositories",
    "ctx-search": "Unified search (repos or symbols)",
    "ctx-docs": "Get repository documentation",

    # Code analysis
    "ctx-analyze": "Analyze code and extract symbols",
    "ctx-symbol": "Get detailed symbol information",
    "ctx-symbols": "List all symbols in a file",
    "ctx-graph": "Generate dependency graph",

    # Architecture
    "ctx-dsm": "Generate Design Structure Matrix",
    "ctx-cycles": "Detect dependency cycles",
    "ctx-layers": "Detect architectural layers",
    "ctx-architecture": "Analyze architecture with rules",
    "ctx-metrics": "Calculate XS complexity metrics",

    # Export
    "ctx-llmstxt": "Generate compact llms.txt summary",
    "ctx-dump": "Export repository analysis",

    # Joern CPG
    "ctx-query": "Run CPGQL query (requires Joern)",
    "ctx-export": "Export CPG graph (requires Joern)",
    "ctx-status": "Show system status and capabilities",
}
