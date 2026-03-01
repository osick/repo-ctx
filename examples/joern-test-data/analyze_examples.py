#!/usr/bin/env python3
"""
Analyze all example code files and write output to expected-output directories.

Usage:
    python analyze_examples.py              # Analyze all languages
    python analyze_examples.py python java  # Analyze specific languages

Outputs per language in expected-output/<lang>/:
    - symbols.json     : Extracted symbols (JSON)
    - symbols.txt      : Extracted symbols (text)
    - dep-graph.json   : Dependency graph (JSON)
    - dep-graph.dot    : Dependency graph (DOT format)
    - complete-report.md : Combined report with all inputs and outputs

If Joern is installed, also generates (LLM-friendly format):
    - cpg-analysis.md  : Combined CPG analysis report (markdown)
    - cpg-methods.md   : Methods with context (markdown)
    - cpg-types.md     : Types with inheritance (markdown)
    - cpg-calls.md     : Call graph (markdown)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from repo_ctx.analysis import CodeAnalyzer, DependencyGraph, GraphType
from repo_ctx.analysis.models import Symbol, SymbolType
from repo_ctx.joern import queries
from repo_ctx.joern.formatter import CPGFormatter


# Language file extension mappings for syntax highlighting
LANG_EXTENSIONS = {
    "python": "python",
    "javascript": "javascript",
    "typescript": "typescript",
    "java": "java",
    "kotlin": "kotlin",
    "c": "c",
    "cpp": "cpp",
    "go": "go",
    "php": "php",
    "ruby": "ruby",
    "swift": "swift",
    "csharp": "csharp",
}


def generate_combined_report(
    lang: str,
    src_dir: Path,
    files: Dict[str, str],
    all_symbols: List[Symbol],
    stats: Dict[str, Any],
    symbols_json: Dict[str, Any],
    dep_graph_dot: Optional[str],
    dep_graph_json: Optional[str],
    cpg_methods: Optional[str] = None,
    cpg_types: Optional[str] = None,
    cpg_calls: Optional[str] = None,
) -> str:
    """Generate a combined markdown report with all inputs and outputs."""

    syntax = LANG_EXTENSIONS.get(lang, lang)
    report_lines = []

    # Header
    report_lines.extend([
        f"# {lang.title()} Code Analysis Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Source Directory:** `{src_dir}`",
        f"**Files Analyzed:** {len(files)}",
        "",
        "---",
        "",
        "## Table of Contents",
        "",
        "1. [Source Files](#source-files)",
        "2. [Analysis Summary](#analysis-summary)",
        "3. [Extracted Symbols](#extracted-symbols)",
        "4. [Dependency Graph](#dependency-graph)",
    ])

    if cpg_methods or cpg_types or cpg_calls:
        report_lines.append("5. [CPG Analysis (Joern)](#cpg-analysis-joern)")

    report_lines.extend([
        "",
        "---",
        "",
    ])

    # Section 1: Source Files
    report_lines.extend([
        "## Source Files",
        "",
        "The following source files were analyzed:",
        "",
    ])

    for file_path, code in sorted(files.items()):
        file_name = Path(file_path).name
        rel_path = Path(file_path).relative_to(src_dir) if str(file_path).startswith(str(src_dir)) else file_name

        report_lines.extend([
            f"### `{rel_path}`",
            "",
            "**Description:** Source code file containing definitions and logic.",
            "",
            f"```{syntax}",
            code.rstrip(),
            "```",
            "",
        ])

    report_lines.append("---\n")

    # Section 2: Analysis Summary
    report_lines.extend([
        "## Analysis Summary",
        "",
        "Overview of the code analysis results.",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Files Analyzed | {len(files)} |",
        f"| Total Symbols | {stats.get('total_symbols', 0)} |",
    ])

    for stype, count in stats.get("by_type", {}).items():
        report_lines.append(f"| {stype.title()}s | {count} |")

    report_lines.extend(["", "---", ""])

    # Section 3: Extracted Symbols
    report_lines.extend([
        "## Extracted Symbols",
        "",
        "Symbols extracted from the source code using static analysis.",
        "",
    ])

    # Group symbols by type
    symbols_by_type: Dict[str, List[Symbol]] = {}
    for s in all_symbols:
        stype = s.symbol_type.value
        if stype not in symbols_by_type:
            symbols_by_type[stype] = []
        symbols_by_type[stype].append(s)

    # Symbol type explanations
    type_explanations = {
        "class": "Classes define object blueprints with attributes and methods.",
        "interface": "Interfaces define contracts that classes must implement.",
        "function": "Functions are reusable blocks of code that perform specific tasks.",
        "method": "Methods are functions defined within a class.",
        "enum": "Enums define a set of named constant values.",
        "variable": "Variables store data values.",
        "constant": "Constants are immutable values defined at compile time.",
        "property": "Properties are class attributes with getter/setter access.",
    }

    for stype, symbols in sorted(symbols_by_type.items()):
        explanation = type_explanations.get(stype, f"{stype.title()} definitions found in the code.")
        report_lines.extend([
            f"### {stype.title()}s ({len(symbols)})",
            "",
            f"*{explanation}*",
            "",
            "| Name | File | Line | Visibility |",
            "|------|------|------|------------|",
        ])

        for s in symbols:
            file_name = Path(s.file_path).name if s.file_path else "N/A"
            visibility = s.visibility or "public"
            report_lines.append(f"| `{s.name}` | {file_name} | {s.line_start} | {visibility} |")

        report_lines.append("")

    # JSON output
    report_lines.extend([
        "### Symbols JSON Output",
        "",
        "Machine-readable symbol data for programmatic access.",
        "",
        "```json",
        json.dumps(symbols_json, indent=2),
        "```",
        "",
        "---",
        "",
    ])

    # Section 4: Dependency Graph
    report_lines.extend([
        "## Dependency Graph",
        "",
        "Visual representation of code dependencies and relationships.",
        "",
    ])

    if dep_graph_dot:
        report_lines.extend([
            "### DOT Format",
            "",
            "The DOT format can be visualized using Graphviz:",
            "```bash",
            f"dot -Tpng dep-graph.dot -o dep-graph.png",
            "```",
            "",
            "```dot",
            dep_graph_dot.rstrip(),
            "```",
            "",
        ])

    if dep_graph_json:
        report_lines.extend([
            "### JSON Graph Format (JGF)",
            "",
            "JSON Graph Format for programmatic graph processing.",
            "",
            "```json",
            dep_graph_json.rstrip(),
            "```",
            "",
        ])

    report_lines.append("---\n")

    # Section 5: CPG Analysis (if available)
    if cpg_methods or cpg_types or cpg_calls:
        report_lines.extend([
            "## CPG Analysis (Joern)",
            "",
            "Advanced code analysis using Joern's Code Property Graph.",
            "",
        ])

        if cpg_types:
            report_lines.extend([
                "### Types and Inheritance",
                "",
                "*Type declarations with their inheritance hierarchy.*",
                "",
                cpg_types.rstrip(),
                "",
            ])

        if cpg_methods:
            report_lines.extend([
                "### Methods and Functions",
                "",
                "*Method signatures with parameters and return types.*",
                "",
                cpg_methods.rstrip(),
                "",
            ])

        if cpg_calls:
            report_lines.extend([
                "### Call Graph",
                "",
                "*Function/method call relationships showing who calls whom.*",
                "",
                cpg_calls.rstrip(),
                "",
            ])

    # Footer
    report_lines.extend([
        "---",
        "",
        "*Report generated by repo-ctx analyze_examples.py*",
    ])

    return "\n".join(report_lines)


def analyze_language(lang: str, src_dir: Path, out_dir: Path, analyzer: CodeAnalyzer):
    """Analyze a single language directory."""
    if not src_dir.exists():
        print(f"  Skipping {lang} - directory not found")
        return

    print(f"\nAnalyzing: {lang}")
    print(f"  Source: {src_dir}")
    print(f"  Output: {out_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)

    # Collect source files
    files = {}
    for file_path in src_dir.rglob("*"):
        if file_path.is_file() and analyzer.detect_language(str(file_path)):
            try:
                files[str(file_path)] = file_path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue

    if not files:
        print(f"  No supported files found in {lang}")
        return

    # Variables to collect for combined report
    all_symbols = []
    stats = {}
    symbols_json = {}
    dep_graph_dot = None
    dep_graph_json = None
    cpg_methods_content = None
    cpg_types_content = None
    cpg_calls_content = None

    # Analyze files
    print(f"  - Extracting symbols from {len(files)} files...")
    try:
        results = analyzer.analyze_files(files)
        all_symbols = analyzer.aggregate_symbols(results)
        stats = analyzer.get_statistics(all_symbols)

        # Write JSON output
        symbols_json = {
            "language": lang,
            "files_analyzed": len(files),
            "statistics": stats,
            "symbols": [
                {
                    "name": s.name,
                    "type": s.symbol_type.value,
                    "file": s.file_path,
                    "line": s.line_start,
                    "signature": s.signature,
                    "visibility": s.visibility,
                }
                for s in all_symbols
            ],
        }
        (out_dir / "symbols.json").write_text(
            json.dumps(symbols_json, indent=2), encoding="utf-8"
        )
        print(f"    Saved: symbols.json ({len(all_symbols)} symbols)")

        # Write text output
        lines = [
            f"Language: {lang}",
            f"Files analyzed: {len(files)}",
            f"Total symbols: {stats['total_symbols']}",
            "",
            "Symbols by type:",
        ]
        for stype, count in stats.get("by_type", {}).items():
            lines.append(f"  {stype}: {count}")
        lines.append("")
        lines.append("Symbols:")
        for s in all_symbols:
            lines.append(f"  {s.symbol_type.value}: {s.name} ({s.file_path}:{s.line_start})")

        (out_dir / "symbols.txt").write_text("\n".join(lines), encoding="utf-8")
        print(f"    Saved: symbols.txt")

    except Exception as e:
        print(f"    Error extracting symbols: {e}")

    # Generate dependency graph
    print("  - Generating dependency graph...")
    try:
        graph_builder = DependencyGraph()
        all_dependencies = []

        for file_path, code in files.items():
            deps = analyzer.extract_dependencies(code, file_path)
            # Convert Dependency objects to dicts expected by DependencyGraph
            for dep in deps:
                dep_dict = {
                    "type": dep.dependency_type,
                    "source": dep.source,
                    "target": dep.target,
                    "file": dep.file_path,
                    "line": dep.line,
                    "is_external": dep.is_external,
                }
                # Add caller/callee for call dependencies
                if dep.dependency_type == "call":
                    dep_dict["caller"] = dep.source
                    dep_dict["callee"] = dep.target
                all_dependencies.append(dep_dict)

        graph_result = graph_builder.build(
            symbols=all_symbols,
            dependencies=all_dependencies,
            graph_type=GraphType.CLASS,
            graph_id=str(src_dir),
            graph_label=f"Dependency Graph: {lang}",
        )

        # Write JSON and capture for combined report
        dep_graph_json = graph_builder.to_json(graph_result)
        (out_dir / "dep-graph.json").write_text(dep_graph_json, encoding="utf-8")
        print(f"    Saved: dep-graph.json")

        # Write DOT and capture for combined report
        dep_graph_dot = graph_builder.to_dot(graph_result)
        (out_dir / "dep-graph.dot").write_text(dep_graph_dot, encoding="utf-8")
        print(f"    Saved: dep-graph.dot")

    except Exception as e:
        print(f"    Error generating graph: {e}")

    # CPG analysis with Joern (if available)
    if analyzer.is_joern_available():
        print("  - Running CPG queries (LLM-friendly format)...")
        formatter = CPGFormatter()

        try:
            # Run LLM-friendly queries
            methods_result = analyzer.run_cpg_query(str(src_dir), queries.QUERY_LLM_METHODS)
            types_result = analyzer.run_cpg_query(str(src_dir), queries.QUERY_LLM_TYPES)
            calls_result = analyzer.run_cpg_query(str(src_dir), queries.QUERY_LLM_CALLS)

            methods_output = methods_result.get("output", "") if methods_result.get("success") else ""
            types_output = types_result.get("output", "") if types_result.get("success") else ""
            calls_output = calls_result.get("output", "") if calls_result.get("success") else ""

            # Generate combined report
            if methods_output or types_output or calls_output:
                combined_report = formatter.format_combined_report(
                    methods_output=methods_output,
                    types_output=types_output,
                    calls_output=calls_output,
                    source_path=str(src_dir),
                    language=lang,
                )
                (out_dir / "cpg-analysis.md").write_text(combined_report, encoding="utf-8")
                print(f"    Saved: cpg-analysis.md (combined report)")

            # Generate individual reports and capture for combined report
            if methods_output:
                cpg_methods_content = formatter.format_methods_report(
                    methods_output, str(src_dir), lang
                )
                (out_dir / "cpg-methods.md").write_text(cpg_methods_content, encoding="utf-8")
                print(f"    Saved: cpg-methods.md")

            if types_output:
                cpg_types_content = formatter.format_types_report(
                    types_output, str(src_dir), lang
                )
                (out_dir / "cpg-types.md").write_text(cpg_types_content, encoding="utf-8")
                print(f"    Saved: cpg-types.md")

            if calls_output:
                cpg_calls_content = formatter.format_calls_report(
                    calls_output, str(src_dir), lang
                )
                (out_dir / "cpg-calls.md").write_text(cpg_calls_content, encoding="utf-8")
                print(f"    Saved: cpg-calls.md")

        except Exception as e:
            print(f"    Error running CPG queries: {e}")

    # Generate combined markdown report
    print("  - Generating combined report...")
    try:
        combined_md = generate_combined_report(
            lang=lang,
            src_dir=src_dir,
            files=files,
            all_symbols=all_symbols,
            stats=stats,
            symbols_json=symbols_json,
            dep_graph_dot=dep_graph_dot,
            dep_graph_json=dep_graph_json,
            cpg_methods=cpg_methods_content,
            cpg_types=cpg_types_content,
            cpg_calls=cpg_calls_content,
        )
        (out_dir / "complete-report.md").write_text(combined_md, encoding="utf-8")
        print(f"    Saved: complete-report.md")
    except Exception as e:
        print(f"    Error generating combined report: {e}")


def main():
    script_dir = Path(__file__).parent
    output_base = script_dir / "expected-output"

    # All available languages
    all_languages = [
        "c", "cpp", "go", "php", "ruby", "swift", "csharp",
        "python", "javascript", "java", "kotlin"
    ]

    # Get languages to analyze from args or use all
    languages = sys.argv[1:] if len(sys.argv) > 1 else all_languages

    print("=" * 50)
    print("repo-ctx Example Code Analyzer")
    print("=" * 50)

    # Initialize analyzer with tree-sitter for reliable local analysis
    # Joern is still used for CPG queries if available
    analyzer = CodeAnalyzer(use_treesitter=True)

    # Check Joern availability
    if analyzer.is_joern_available():
        print(f"\nJoern detected: {analyzer.get_joern_version()}")
        print("CPG analysis enabled for additional languages")
    else:
        print("\nJoern not found - using tree-sitter only")
        print("Install Joern for additional analysis: https://joern.io/")

    print(f"\nLanguages to analyze: {', '.join(languages)}")

    # Analyze each language
    for lang in languages:
        src_dir = script_dir / lang
        out_dir = output_base / lang
        analyze_language(lang, src_dir, out_dir, analyzer)

    print("\n" + "=" * 50)
    print("Analysis complete!")
    print(f"\nOutput files in: {output_base}/<language>/")
    print("\nFiles generated:")
    print("  - complete-report.md : Combined report with all inputs/outputs")
    print("  - symbols.json       : Extracted symbols (JSON)")
    print("  - symbols.txt        : Extracted symbols (text)")
    print("  - dep-graph.json     : Dependency graph (JSON)")
    print("  - dep-graph.dot      : Dependency graph (DOT)")
    if analyzer.is_joern_available():
        print("\nCPG analysis (LLM-friendly markdown):")
        print("  - cpg-analysis.md : Combined code analysis report")
        print("  - cpg-methods.md  : Methods with file, line, signature")
        print("  - cpg-types.md    : Types with inheritance hierarchy")
        print("  - cpg-calls.md    : Call graph (who calls whom)")
    print("\nTo visualize DOT files:")
    print("  dot -Tpng expected-output/python/dep-graph.dot -o dep-graph.png")
    print("=" * 50)


if __name__ == "__main__":
    main()
