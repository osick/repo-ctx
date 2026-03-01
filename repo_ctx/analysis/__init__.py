"""Code analysis module for extracting symbols and dependencies."""
from .models import Symbol, SymbolType, Dependency, CallEdge, DocQuality
from .python_extractor import PythonExtractor
from .javascript_extractor import JavaScriptExtractor
from .java_extractor import JavaExtractor
from .kotlin_extractor import KotlinExtractor
from .code_analyzer import CodeAnalyzer
from .dependency_graph import (
    DependencyGraph,
    DependencyGraphResult,
    GraphType,
    EdgeRelation,
    GraphNode,
    GraphEdge,
)
from .report_generator import CodeAnalysisReport
from .architecture import (
    DSMBuilder,
    DSMResult,
    CycleDetector,
    CycleInfo,
    BreakupSuggestion,
    analyze_architecture,
)
from .architecture_rules import (
    LayerDetector,
    LayerInfo,
    ArchitectureRules,
    ArchitectureViolation,
    LayerRule,
    DependencyRule,
    RuleParser,
    analyze_with_rules,
)
from .structural_metrics import (
    XSCalculator,
    XSMetrics,
    XSInput,
    XSGrader,
    HotspotDetector,
    Hotspot,
    MetricsComparison,
    analyze_structure,
    # Coupling metrics
    CouplingAnalyzer,
    CouplingAnalysisResult,
    NodeCouplingMetrics,
    PackageCouplingMetrics,
    analyze_coupling,
)
from .file_enhancer import FileEnhancer
from .codebase_summarizer import CodebaseSummarizer
from .prompts import (
    format_symbol_prompt,
    format_file_prompt,
    parse_symbol_response,
    format_file_enhancement_prompt,
    parse_file_enhancement_response,
)

__all__ = [
    "Symbol",
    "SymbolType",
    "DocQuality",
    "Dependency",
    "CallEdge",
    "PythonExtractor",
    "JavaScriptExtractor",
    "JavaExtractor",
    "KotlinExtractor",
    "CodeAnalyzer",
    "DependencyGraph",
    "DependencyGraphResult",
    "GraphType",
    "EdgeRelation",
    "GraphNode",
    "GraphEdge",
    "CodeAnalysisReport",
    # Architecture analysis
    "DSMBuilder",
    "DSMResult",
    "CycleDetector",
    "CycleInfo",
    "BreakupSuggestion",
    "analyze_architecture",
    # Layer detection & architecture rules
    "LayerDetector",
    "LayerInfo",
    "ArchitectureRules",
    "ArchitectureViolation",
    "LayerRule",
    "DependencyRule",
    "RuleParser",
    "analyze_with_rules",
    # Structural metrics (XS)
    "XSCalculator",
    "XSMetrics",
    "XSInput",
    "XSGrader",
    "HotspotDetector",
    "Hotspot",
    "MetricsComparison",
    "analyze_structure",
    # Coupling metrics
    "CouplingAnalyzer",
    "CouplingAnalysisResult",
    "NodeCouplingMetrics",
    "PackageCouplingMetrics",
    "analyze_coupling",
    # File enhancement
    "FileEnhancer",
    "CodebaseSummarizer",
    "format_symbol_prompt",
    "format_file_prompt",
    "parse_symbol_response",
    "format_file_enhancement_prompt",
    "parse_file_enhancement_response",
]
