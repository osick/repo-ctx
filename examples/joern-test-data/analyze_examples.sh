#!/bin/bash
# Analyze all example code files and write output to expected-output directories
#
# Usage:
#   ./analyze_examples.sh              # Analyze all languages
#   ./analyze_examples.sh python       # Analyze specific language
#   ./analyze_examples.sh python java  # Analyze multiple specific languages
#
# Outputs per language in expected-output/<lang>/:
#   - complete-report.md : Combined report with all inputs and outputs
#   - symbols.json       : Extracted symbols (JSON)
#   - symbols.txt        : Extracted symbols (text)
#   - dep-graph.json     : Dependency graph (JSON)
#   - dep-graph.dot      : Dependency graph (DOT format)
#
# If Joern is installed, also generates (LLM-friendly markdown):
#   - cpg-analysis.md  : Combined CPG analysis report
#   - cpg-methods.md   : Methods with parameters and context
#   - cpg-types.md     : Types with inheritance hierarchy
#   - cpg-calls.md     : Call graph (who calls whom)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_BASE="$SCRIPT_DIR/expected-output"

# All available languages
ALL_LANGUAGES=("c" "cpp" "go" "php" "ruby" "swift" "csharp" "python" "javascript" "java" "kotlin")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if specific languages requested
if [ $# -gt 0 ]; then
    LANGUAGES=("$@")
else
    LANGUAGES=("${ALL_LANGUAGES[@]}")
fi

echo "=============================================="
echo "repo-ctx Example Code Analyzer"
echo "=============================================="
echo ""

# Check Joern availability
JOERN_AVAILABLE=false
if command -v joern &> /dev/null; then
    JOERN_AVAILABLE=true
    echo -e "${GREEN}Joern detected - CPG analysis enabled${NC}"
    echo -e "${YELLOW}Note: CPG queries take ~15-20 seconds each${NC}"
else
    echo -e "${YELLOW}Joern not found - skipping CPG analysis${NC}"
    echo "  Install Joern for additional analysis: https://joern.io/"
fi
echo ""
echo "Languages to analyze: ${LANGUAGES[*]}"
echo ""

# LLM-friendly queries (same as in Python version)
QUERY_LLM_METHODS='cpg.method.filter(_.isExternal == false).filterNot(m => m.name.startsWith("<") || m.name.contains("metaClass")).map(m => s"${m.name}|${m.fullName}|${m.filename}|${m.lineNumber.getOrElse(0)}|${m.lineNumberEnd.getOrElse(0)}|${m.parameter.filterNot(p => p.name == "self" || p.name == "this").map(p => p.name + ":" + p.typeFullName.replace("__builtin.", "").replace("ANY", "any")).mkString(", ")}").l'

QUERY_LLM_TYPES='cpg.typeDecl.filter(_.isExternal == false).filterNot(t => t.name.startsWith("<") || t.name.contains("meta") || t.name == "ANY").map(t => s"${t.name}|${t.fullName}|${t.filename}|${t.lineNumber.getOrElse(0)}|${t.inheritsFromTypeFullName.mkString(",")}").l'

QUERY_LLM_CALLS='cpg.call.filter(c => c.method.isExternal == false).filterNot(c => c.name.startsWith("<")).filterNot(c => c.method.name.startsWith("<")).map(c => s"${c.method.name}|${c.name}|${c.lineNumber.getOrElse(0)}").l'

# Function to analyze a language
analyze_language() {
    local lang=$1
    local src_dir="$SCRIPT_DIR/$lang"
    local out_dir="$OUTPUT_BASE/$lang"

    # Check if source directory exists
    if [ ! -d "$src_dir" ]; then
        echo -e "${YELLOW}Skipping $lang - directory not found${NC}"
        return
    fi

    echo -e "${GREEN}Analyzing: $lang${NC}"
    echo "  Source: $src_dir"
    echo "  Output: $out_dir"

    # Create output directory
    mkdir -p "$out_dir"

    # Tree-sitter analysis (always available for supported languages)
    echo -n "  - Extracting symbols... "
    # Use Python API directly for reliable tree-sitter analysis
    if uv run python -c "
import sys
import json
from pathlib import Path
sys.path.insert(0, '$SCRIPT_DIR/../..')
from repo_ctx.analysis import CodeAnalyzer

src_dir = Path('$src_dir')
out_dir = Path('$out_dir')
lang = '$lang'

# Use tree-sitter for reliable local analysis
analyzer = CodeAnalyzer(use_treesitter=True)

files = {}
for f in src_dir.rglob('*'):
    if f.is_file() and analyzer.detect_language(str(f)):
        try:
            files[str(f)] = f.read_text(encoding='utf-8')
        except:
            pass

if not files:
    sys.exit(1)

results = analyzer.analyze_files(files)
all_symbols = analyzer.aggregate_symbols(results)
stats = analyzer.get_statistics(all_symbols)

# Write JSON
symbols_json = {
    'language': lang,
    'files_analyzed': len(files),
    'statistics': stats,
    'symbols': [
        {
            'name': s.name,
            'type': s.symbol_type.value,
            'file': s.file_path,
            'line': s.line_start,
            'signature': s.signature,
            'visibility': s.visibility,
        }
        for s in all_symbols
    ],
}
(out_dir / 'symbols.json').write_text(json.dumps(symbols_json, indent=2), encoding='utf-8')

# Write text
lines = [f'Language: {lang}', f'Files analyzed: {len(files)}', f'Total symbols: {stats[\"total_symbols\"]}', '', 'Symbols by type:']
for stype, count in stats.get('by_type', {}).items():
    lines.append(f'  {stype}: {count}')
lines.extend(['', 'Symbols:'])
for s in all_symbols:
    lines.append(f'  {s.symbol_type.value}: {s.name} ({s.file_path}:{s.line_start})')
(out_dir / 'symbols.txt').write_text('\n'.join(lines), encoding='utf-8')

print(f'{len(all_symbols)} symbols')
" 2>/dev/null; then
        echo -e "${GREEN}symbols.json, symbols.txt${NC}"
    else
        echo -e "${YELLOW}skipped (unsupported)${NC}"
    fi

    # Dependency graph
    echo -n "  - Generating dependency graph... "
    # Use Python API directly for reliable dependency extraction
    if uv run python -c "
import sys
import json
from pathlib import Path
sys.path.insert(0, '$SCRIPT_DIR/../..')
from repo_ctx.analysis import CodeAnalyzer, DependencyGraph, GraphType

src_dir = Path('$src_dir')
out_dir = Path('$out_dir')
lang = '$lang'

analyzer = CodeAnalyzer(use_treesitter=True)

files = {}
for f in src_dir.rglob('*'):
    if f.is_file() and analyzer.detect_language(str(f)):
        try:
            files[str(f)] = f.read_text(encoding='utf-8')
        except:
            pass

if not files:
    sys.exit(1)

results = analyzer.analyze_files(files)
all_symbols = analyzer.aggregate_symbols(results)

graph_builder = DependencyGraph()
all_dependencies = []

for file_path, code in files.items():
    deps = analyzer.extract_dependencies(code, file_path)
    for dep in deps:
        dep_dict = {
            'type': dep.dependency_type,
            'source': dep.source,
            'target': dep.target,
            'file': dep.file_path,
            'line': dep.line,
            'is_external': dep.is_external,
        }
        if dep.dependency_type == 'call':
            dep_dict['caller'] = dep.source
            dep_dict['callee'] = dep.target
        all_dependencies.append(dep_dict)

graph_result = graph_builder.build(
    symbols=all_symbols,
    dependencies=all_dependencies,
    graph_type=GraphType.CLASS,
    graph_id=str(src_dir),
    graph_label=f'Dependency Graph: {lang}',
)

(out_dir / 'dep-graph.json').write_text(graph_builder.to_json(graph_result), encoding='utf-8')
(out_dir / 'dep-graph.dot').write_text(graph_builder.to_dot(graph_result), encoding='utf-8')
print('done')
" 2>/dev/null; then
        echo -e "${GREEN}dep-graph.json, dep-graph.dot${NC}"
    else
        echo -e "${YELLOW}skipped${NC}"
    fi

    # Joern CPG analysis (if available)
    if [ "$JOERN_AVAILABLE" = true ]; then
        echo "  - Running CPG queries (LLM-friendly format)..."

        # Methods with parameters
        echo -n "      Methods... "
        if timeout 60 uv run repo-ctx cpg query "$src_dir" "$QUERY_LLM_METHODS" 2>/dev/null | \
           uv run python -c "
import sys
from repo_ctx.joern.formatter import CPGFormatter
formatter = CPGFormatter()
raw = sys.stdin.read()
# Extract just the output part after 'Output:'
if 'Output:' in raw:
    raw = raw.split('Output:', 1)[1].strip()
print(formatter.format_methods_report(raw, '$src_dir', '$lang'))
" > "$out_dir/cpg-methods.md" 2>/dev/null; then
            echo -e "${GREEN}cpg-methods.md${NC}"
        else
            echo -e "${YELLOW}failed${NC}"
        fi

        # Types with inheritance
        echo -n "      Types... "
        if timeout 60 uv run repo-ctx cpg query "$src_dir" "$QUERY_LLM_TYPES" 2>/dev/null | \
           uv run python -c "
import sys
from repo_ctx.joern.formatter import CPGFormatter
formatter = CPGFormatter()
raw = sys.stdin.read()
if 'Output:' in raw:
    raw = raw.split('Output:', 1)[1].strip()
print(formatter.format_types_report(raw, '$src_dir', '$lang'))
" > "$out_dir/cpg-types.md" 2>/dev/null; then
            echo -e "${GREEN}cpg-types.md${NC}"
        else
            echo -e "${YELLOW}failed${NC}"
        fi

        # Call graph
        echo -n "      Calls... "
        if timeout 60 uv run repo-ctx cpg query "$src_dir" "$QUERY_LLM_CALLS" 2>/dev/null | \
           uv run python -c "
import sys
from repo_ctx.joern.formatter import CPGFormatter
formatter = CPGFormatter()
raw = sys.stdin.read()
if 'Output:' in raw:
    raw = raw.split('Output:', 1)[1].strip()
print(formatter.format_calls_report(raw, '$src_dir', '$lang'))
" > "$out_dir/cpg-calls.md" 2>/dev/null; then
            echo -e "${GREEN}cpg-calls.md${NC}"
        else
            echo -e "${YELLOW}failed${NC}"
        fi
    fi

    # Generate combined markdown report
    echo -n "  - Generating combined report... "
    uv run python -c "
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '$SCRIPT_DIR/../..')
from repo_ctx.analysis import CodeAnalyzer

src_dir = Path('$src_dir')
out_dir = Path('$out_dir')
lang = '$lang'

# Language syntax highlighting
LANG_SYNTAX = {
    'python': 'python', 'javascript': 'javascript', 'typescript': 'typescript',
    'java': 'java', 'kotlin': 'kotlin', 'c': 'c', 'cpp': 'cpp',
    'go': 'go', 'php': 'php', 'ruby': 'ruby', 'swift': 'swift', 'csharp': 'csharp'
}
syntax = LANG_SYNTAX.get(lang, lang)

# Collect source files
analyzer = CodeAnalyzer(use_treesitter=True)
files = {}
for f in src_dir.rglob('*'):
    if f.is_file() and analyzer.detect_language(str(f)):
        try:
            files[str(f)] = f.read_text(encoding='utf-8')
        except:
            pass

# Read existing outputs
symbols_json = {}
dep_graph_dot = ''
dep_graph_json = ''
cpg_methods = ''
cpg_types = ''
cpg_calls = ''

if (out_dir / 'symbols.json').exists():
    symbols_json = json.loads((out_dir / 'symbols.json').read_text())
if (out_dir / 'dep-graph.dot').exists():
    dep_graph_dot = (out_dir / 'dep-graph.dot').read_text()
if (out_dir / 'dep-graph.json').exists():
    dep_graph_json = (out_dir / 'dep-graph.json').read_text()
if (out_dir / 'cpg-methods.md').exists():
    cpg_methods = (out_dir / 'cpg-methods.md').read_text()
if (out_dir / 'cpg-types.md').exists():
    cpg_types = (out_dir / 'cpg-types.md').read_text()
if (out_dir / 'cpg-calls.md').exists():
    cpg_calls = (out_dir / 'cpg-calls.md').read_text()

# Build report
lines = [
    f'# {lang.title()} Code Analysis Report',
    '',
    f'**Generated:** {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}',
    f'**Source Directory:** \`{src_dir}\`',
    f'**Files Analyzed:** {len(files)}',
    '',
    '---',
    '',
    '## Table of Contents',
    '',
    '1. [Source Files](#source-files)',
    '2. [Extracted Symbols](#extracted-symbols)',
    '3. [Dependency Graph](#dependency-graph)',
]
if cpg_methods or cpg_types or cpg_calls:
    lines.append('4. [CPG Analysis (Joern)](#cpg-analysis-joern)')
lines.extend(['', '---', '', '## Source Files', '', 'The following source files were analyzed:', ''])

for fpath, code in sorted(files.items()):
    fname = Path(fpath).name
    lines.extend([f'### \`{fname}\`', '', '**Description:** Source code file.', '', f'\`\`\`{syntax}', code.rstrip(), '\`\`\`', ''])

lines.extend(['---', '', '## Extracted Symbols', '', 'Symbols extracted via static analysis.', ''])
if symbols_json and 'symbols' in symbols_json:
    lines.extend(['| Name | Type | File | Line |', '|------|------|------|------|'])
    for s in symbols_json['symbols'][:50]:  # Limit for readability
        lines.append(f'| \`{s[\"name\"]}\` | {s[\"type\"]} | {Path(s[\"file\"]).name if s[\"file\"] else \"N/A\"} | {s[\"line\"]} |')
    if len(symbols_json['symbols']) > 50:
        lines.append(f'| ... | ({len(symbols_json[\"symbols\"]) - 50} more) | | |')
lines.append('')

lines.extend(['---', '', '## Dependency Graph', '', 'Code dependencies and relationships.', ''])
if dep_graph_dot:
    lines.extend(['### DOT Format', '', '\`\`\`dot', dep_graph_dot.rstrip(), '\`\`\`', ''])

lines.append('---')
if cpg_methods or cpg_types or cpg_calls:
    lines.extend(['', '## CPG Analysis (Joern)', '', 'Advanced analysis using Joern.', ''])
    if cpg_types:
        lines.extend(['### Types', '', cpg_types.rstrip(), ''])
    if cpg_methods:
        lines.extend(['### Methods', '', cpg_methods.rstrip(), ''])
    if cpg_calls:
        lines.extend(['### Calls', '', cpg_calls.rstrip(), ''])

lines.extend(['', '---', '', '*Report generated by repo-ctx*'])
(out_dir / 'complete-report.md').write_text('\n'.join(lines), encoding='utf-8')
print('complete-report.md')
" 2>/dev/null && echo -e "${GREEN}done${NC}" || echo -e "${YELLOW}skipped${NC}"

    echo ""
}

# Analyze each language
for lang in "${LANGUAGES[@]}"; do
    analyze_language "$lang"
done

echo "=============================================="
echo -e "${GREEN}Analysis complete!${NC}"
echo ""
echo "Output files in: $OUTPUT_BASE/<language>/"
echo ""
echo "Files generated:"
echo "  - complete-report.md : Combined report with all inputs/outputs"
echo "  - symbols.json       : Extracted symbols (JSON)"
echo "  - symbols.txt        : Extracted symbols (text)"
echo "  - dep-graph.json     : Dependency graph (JSON)"
echo "  - dep-graph.dot      : Dependency graph (DOT)"
if [ "$JOERN_AVAILABLE" = true ]; then
    echo ""
    echo "CPG analysis (LLM-friendly markdown):"
    echo "  - cpg-methods.md  : Methods with parameters"
    echo "  - cpg-types.md    : Types with inheritance"
    echo "  - cpg-calls.md    : Call graph"
fi
echo ""
echo "To visualize DOT files:"
echo "  dot -Tpng expected-output/python/dep-graph.dot -o dep-graph.png"
echo "=============================================="
