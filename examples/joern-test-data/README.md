# Joern CPG Test Data

This directory contains sample code files for testing repo-ctx code analysis with both tree-sitter and Joern CPG.

## Quick Start

```bash
# Analyze all example files
python analyze_examples.py

# Or use the shell script
./analyze_examples.sh

# Analyze specific languages only
python analyze_examples.py python java kotlin

# Check Joern status
repo-ctx cpg status
```

Output files are generated in `expected-output/<language>/`:
- `symbols.json` / `symbols.txt` - Extracted symbols
- `dep-graph.json` / `dep-graph.dot` - Dependency graphs
- `cpg-*.txt` - CPGQL query results (if Joern is installed)

## Directory Structure

```
joern-test-data/
├── c/
│   └── sample.c           # C: functions, structs, pointers
├── cpp/
│   └── sample.cpp         # C++: classes, templates, virtual functions
├── go/
│   └── sample.go          # Go: structs, interfaces, goroutines
├── php/
│   └── sample.php         # PHP: classes, interfaces, traits
├── ruby/
│   └── sample.rb          # Ruby: classes, modules, blocks
├── swift/
│   └── sample.swift       # Swift: protocols, structs, async
├── csharp/
│   └── Sample.cs          # C#: classes, generics, LINQ, async
├── python/
│   └── sample.py          # Python: classes, decorators, async
├── javascript/
│   └── sample.js          # JavaScript: classes, closures, async
├── java/
│   └── Sample.java        # Java: classes, generics, streams
├── kotlin/
│   └── sample.kt          # Kotlin: data classes, coroutines, DSL
└── expected-output/
    ├── symbols.json       # Expected symbol extraction format
    └── queries/
        └── basic_queries.sc  # Example CPGQL queries
```

## Common Pattern

All sample files implement a similar domain model to enable cross-language comparison:

1. **Shape Interface/Protocol** - Abstract shape with `area()` and `perimeter()` methods
2. **Rectangle Class** - Concrete shape with width and height
3. **Circle Class** - Concrete shape with radius
4. **ShapeManager Class** - Collection manager with filtering and async processing
5. **Factory Pattern** - Shape creation with validation

## Running Joern Analysis

### Prerequisites

1. Install Joern (requires JDK 19+):
   ```bash
   curl -L "https://github.com/joernio/joern/releases/latest/download/joern-install.sh" -o joern-install.sh
   chmod u+x joern-install.sh
   ./joern-install.sh
   ```

2. Verify installation:
   ```bash
   joern --version
   ```

### Parsing Code

Generate CPG for a language:

```bash
# Parse C code
joern-parse c/sample.c --output c.cpg

# Parse Python code
joern-parse python/sample.py --output python.cpg

# Parse Java code
joern-parse java/Sample.java --output java.cpg
```

### Running Queries

Interactive mode:
```bash
joern
> importCpg("python.cpg")
> cpg.method.name.l
> cpg.typeDecl.name.l
> cpg.call.code.l
```

Script mode:
```bash
joern --script expected-output/queries/basic_queries.sc \
      --param cpgFile=python.cpg \
      --param outFile=output.txt
```

### Exporting Graphs

Export to various formats:

```bash
# Export as GraphViz DOT
joern-export --repr=all --format=dot --out=dot-output

# Export as GraphML
joern-export --repr=all --format=graphml --out=graphml-output

# Export for Neo4j
joern-export --repr=all --format=neo4jcsv --out=neo4j-output
```

## Language Frontend Reference

| Language | Frontend | Command |
|----------|----------|---------|
| C/C++ | c2cpg | `joern-parse sample.c` |
| Java | javasrc2cpg | `joern-parse Sample.java` |
| JavaScript/TypeScript | jssrc2cpg | `joern-parse sample.js` |
| Python | pysrc2cpg | `joern-parse sample.py` |
| Go | gosrc2cpg | `joern-parse sample.go` |
| PHP | php2cpg | `joern-parse sample.php` |
| Ruby | rubysrc2cpg | `joern-parse sample.rb` |
| Swift | swiftsrc2cpg | `joern-parse sample.swift` |
| C# | csharpsrc2cpg | `joern-parse Sample.cs` |
| Kotlin | kotlin2cpg | `joern-parse sample.kt` |

## Expected Symbols per File

Each sample file should produce approximately:

| Symbol Type | Count | Examples |
|-------------|-------|----------|
| Classes/Types | 4-6 | Shape, Rectangle, Circle, ShapeManager |
| Methods | 15-25 | area, perimeter, printInfo, addShape |
| Members/Fields | 5-10 | width, height, radius, shapes |
| Constructors | 3-5 | Rectangle(), Circle(), ShapeManager() |

## CPGQL Query Examples

### List all methods
```scala
cpg.method.filter(_.isExternal == false).name.l
```

### List all classes
```scala
cpg.typeDecl.filter(_.isExternal == false).name.l
```

### Find method calls
```scala
cpg.call.map(c => (c.method.name.head, c.name)).l
```

### Find class hierarchy
```scala
cpg.typeDecl
   .filter(_.inheritsFromTypeFullName.nonEmpty)
   .map(t => (t.name, t.inheritsFromTypeFullName))
   .l
```

### Find complex methods (many control structures)
```scala
cpg.method
   .filter(_.controlStructure.size > 3)
   .map(m => (m.name, m.controlStructure.size))
   .l
```

## Visualization

### Using GraphViz

```bash
joern-export --repr=cpg14 --format=dot --out=cpg-dot
dot -Tpng cpg-dot/0-cpg.dot -o cpg.png
```

### Using Neo4j

```bash
joern-export --repr=all --format=neo4jcsv --out=neo4j-export
# Import into Neo4j using neo4j-admin import
```

## Integration with repo-ctx

These test files are used by repo-ctx's Joern integration to:

1. Verify symbol extraction accuracy
2. Test CPGQL query execution
3. Validate cross-language analysis
4. Benchmark performance

Run the test suite:
```bash
pytest tests/test_joern_*.py -v
```
