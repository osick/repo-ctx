# ADR-002: Code Dependency Graph Feature

**Status:** Accepted
**Date:** 2025-11-28
**Decision Makers:** Development Team
**Technical Story:** Provide LLMs with structured, deterministic code dependency information

## Context and Problem Statement

Large Language Models (LLMs) need structured information about codebases to provide accurate assistance without parsing entire repositories. Current code analysis provides symbol extraction but lacks relationship information between code elements.

**Key Requirements:**
1. Provide dependency relationships in a standardized, machine-readable format
2. Support multiple granularity levels (file, class, function)
3. Include rich metadata for each node
4. Enable visualization export (DOT, GraphML)
5. Work with both local paths and indexed repositories

## Decision Drivers

* **LLM Consumption:** Format must be JSON-based, deterministic, and well-structured
* **Standardization:** Use established graph formats where possible
* **Extensibility:** Support future relationship types and metadata
* **Tool Interoperability:** Enable export to visualization tools
* **Performance:** Efficient for large codebases

## Considered Options

### Option 1: JSON Graph Format (JGF)
- **Description:** Open specification for representing graphs in JSON
- **Website:** https://jsongraphformat.info/
- **GitHub:** https://github.com/jsongraph/json-graph-specification

### Option 2: GraphML
- **Description:** XML-based graph format with wide tool support
- **Website:** http://graphml.graphdrawing.org/

### Option 3: LSIF (Language Server Index Format)
- **Description:** Microsoft's format for code navigation data
- **Website:** https://microsoft.github.io/language-server-protocol/specifications/lsif/0.6.0/specification/

### Option 4: CycloneDX Dependency Graph
- **Description:** SBOM standard with dependency tracking
- **Website:** https://cyclonedx.org/use-cases/

### Option 5: Custom Format
- **Description:** Design a new code-specific format

## Decision Outcome

**Chosen Option:** JSON Graph Format (JGF) with code-specific extensions

### Rationale

| Criterion | JGF | GraphML | LSIF | CycloneDX | Custom |
|-----------|-----|---------|------|-----------|--------|
| LLM-friendly (JSON) | ++ | - | + | + | ++ |
| Standardized | + | ++ | + | ++ | - |
| Code semantics | - | - | ++ | - | ++ |
| Extensible metadata | ++ | + | + | + | ++ |
| Tool support | + | ++ | + | + | - |
| Simplicity | ++ | - | - | + | + |

**JGF wins because:**
1. **Native JSON** - Optimal for LLM consumption
2. **Simple specification** - Easy to understand and validate
3. **Built-in metadata support** - Can add code-specific info without breaking compatibility
4. **Convertible** - Can export to GraphML/DOT for visualization
5. **Active community** - Maintained specification with clear documentation

### Consequences

**Positive:**
- Clean, standardized JSON output
- Easy to extend with code-specific metadata
- Good tool ecosystem for visualization
- Future-proof format

**Negative:**
- Not code-specific by design (requires extensions)
- Less rich than LSIF for IDE navigation
- Requires conversion for some visualization tools

**Risks:**
- JGF specification changes (mitigated: pin to version 2.0)
- Large graphs may impact performance (mitigated: depth limiting)

## Technical Specification

### Graph Types

| Type | Node Representation | Primary Use Case |
|------|---------------------|------------------|
| `file` | Source files | Architecture overview |
| `module` | Packages/modules | Package structure |
| `class` | Classes/interfaces | OOP design analysis |
| `function` | Functions/methods | Call graph analysis |
| `symbol` | All symbols | Complete dependency map |

### Edge Relations

| Relation | Source | Target | Description |
|----------|--------|--------|-------------|
| `imports` | File/Module | File/Module | Import/include statement |
| `inherits` | Class | Class | Class inheritance |
| `implements` | Class | Interface | Interface implementation |
| `contains` | Class/Module | Method/Function | Containment relationship |
| `calls` | Function | Function | Function/method call |
| `uses` | Any | Class/Type | Type usage (params, returns, fields) |
| `instantiates` | Function | Class | Object creation |

### Node Metadata Schema

```json
{
  "type": "class|function|method|interface|enum|module|file",
  "file": "path/to/file.py",
  "line_start": 10,
  "line_end": 50,
  "language": "python",
  "visibility": "public|private|protected",
  "signature": "class ClassName(BaseClass)",
  "documentation": "Docstring or comment",
  "qualified_name": "module.ClassName",
  "is_exported": true,
  "metrics": {
    "methods": 5,
    "complexity": 12,
    "lines": 40
  }
}
```

### Edge Metadata Schema

```json
{
  "line": 15,
  "import_type": "module|from|star",
  "alias": "np",
  "is_dynamic": false
}
```

### Output Format (JGF v2.0 compliant)

```json
{
  "graph": {
    "id": "repository-id",
    "type": "code-dependency-graph",
    "label": "Human-readable label",
    "directed": true,
    "metadata": {
      "generator": "repo-ctx",
      "version": "0.3.1",
      "generated_at": "ISO-8601 timestamp",
      "graph_type": "class",
      "repository": { ... },
      "statistics": { ... }
    },
    "nodes": { ... },
    "edges": [ ... ]
  }
}
```

### CLI Interface

```bash
# Basic usage
repo-ctx code dep <path>           # Local path
repo-ctx code dep -r <repo-id>     # Indexed repository

# Options
--type, -t    file|module|class|function|symbol (default: class)
--depth, -d   Maximum depth (default: unlimited)
--output, -o  json|dot|graphml (default: json)

# Examples
repo-ctx -o json code dep ./src --type class
repo-ctx code dep -r /owner/repo --type function --depth 3
repo-ctx -o dot code dep ./src > graph.dot
```

### MCP Tool Interface

```json
{
  "name": "repo-ctx-dependency-graph",
  "description": "Generate dependency graph for code analysis",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": { "type": "string" },
      "repoId": { "type": "string" },
      "graphType": {
        "type": "string",
        "enum": ["file", "module", "class", "function", "symbol"]
      },
      "depth": { "type": "integer" },
      "outputFormat": {
        "type": "string",
        "enum": ["json", "dot", "graphml"]
      }
    }
  }
}
```

## Implementation Plan

### Phase 1: Core Implementation
1. Create `DependencyGraph` class in `repo_ctx/analysis/`
2. Implement graph building from existing symbol/dependency data
3. Add JGF JSON serialization

### Phase 2: CLI Integration
1. Add `code dep` subcommand
2. Implement `--type`, `--depth` options
3. Wire up to existing code analysis pipeline

### Phase 3: Export Formats
1. Implement DOT export (GraphViz)
2. Implement GraphML export
3. Add format conversion utilities

### Phase 4: MCP Integration
1. Add `repo-ctx-dependency-graph` tool
2. Support all options from CLI

## References

1. **JSON Graph Format Specification**
   - https://jsongraphformat.info/
   - https://github.com/jsongraph/json-graph-specification

2. **CodexGraph: LLM + Code Graph Databases**
   - https://arxiv.org/html/2408.03910v1
   - https://www.marktechpost.com/2024/08/11/codexgraph-an-artificial-intelligence-ai-system-that-integrates-llm-agents-with-graph-database-interfaces-extracted-from-code-repositories/

3. **DepsRAG: Dependency Graphs for LLMs**
   - https://arxiv.org/html/2405.20455v3/

4. **LSIF (Language Server Index Format)**
   - https://microsoft.github.io/language-server-protocol/specifications/lsif/0.6.0/specification/
   - https://lsif.dev/

5. **GraphML Specification**
   - http://graphml.graphdrawing.org/
   - https://en.wikipedia.org/wiki/GraphML

6. **CycloneDX Dependency Graph**
   - https://cyclonedx.org/use-cases/
   - https://scribesecurity.com/blog/cyclonedx-sbom-dependency-graph/

7. **Code Graph Models (CGM)**
   - https://arxiv.org/pdf/2505.16901

## Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-11-28 | 1.0 | Development Team | Initial decision |
