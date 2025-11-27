-- Migration 002: Code Analysis Schema
-- Add tables for semantic code analysis, symbol extraction, and dependency mapping

-- Symbols table (functions, classes, variables, modules)
CREATE TABLE IF NOT EXISTS symbols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository_id INTEGER NOT NULL,
    version_id INTEGER,
    file_path TEXT NOT NULL,
    symbol_type TEXT NOT NULL, -- function, class, variable, module, interface, method
    name TEXT NOT NULL,
    qualified_name TEXT, -- full.module.path.name
    line_start INTEGER NOT NULL,
    line_end INTEGER,
    column_start INTEGER,
    signature TEXT, -- function(args) -> return
    visibility TEXT, -- public, private, protected, internal
    language TEXT NOT NULL,
    documentation TEXT,
    is_exported BOOLEAN DEFAULT 0,
    complexity INTEGER, -- cyclomatic complexity (future)
    metadata JSON, -- language-specific fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repository_id) REFERENCES libraries(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name);
CREATE INDEX IF NOT EXISTS idx_symbols_qualified ON symbols(qualified_name);
CREATE INDEX IF NOT EXISTS idx_symbols_type ON symbols(symbol_type);
CREATE INDEX IF NOT EXISTS idx_symbols_file ON symbols(file_path);
CREATE INDEX IF NOT EXISTS idx_symbols_lang ON symbols(language);
CREATE INDEX IF NOT EXISTS idx_symbols_repo ON symbols(repository_id);

-- Full-text search on symbol names and documentation
CREATE VIRTUAL TABLE IF NOT EXISTS symbols_fts USING fts5(
    name, qualified_name, documentation,
    content='symbols', content_rowid='id'
);

-- Triggers to keep FTS table in sync
CREATE TRIGGER IF NOT EXISTS symbols_fts_insert AFTER INSERT ON symbols BEGIN
    INSERT INTO symbols_fts(rowid, name, qualified_name, documentation)
    VALUES (new.id, new.name, new.qualified_name, new.documentation);
END;

CREATE TRIGGER IF NOT EXISTS symbols_fts_delete AFTER DELETE ON symbols BEGIN
    DELETE FROM symbols_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS symbols_fts_update AFTER UPDATE ON symbols BEGIN
    DELETE FROM symbols_fts WHERE rowid = old.id;
    INSERT INTO symbols_fts(rowid, name, qualified_name, documentation)
    VALUES (new.id, new.name, new.qualified_name, new.documentation);
END;

-- Dependencies between symbols
CREATE TABLE IF NOT EXISTS dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_symbol_id INTEGER NOT NULL,
    target_symbol_id INTEGER NOT NULL,
    dependency_type TEXT NOT NULL, -- import, call, inherit, compose, implement
    location_file TEXT,
    location_line INTEGER,
    is_external BOOLEAN DEFAULT 0, -- external library
    external_module TEXT, -- e.g., "numpy", "express"
    strength INTEGER DEFAULT 1, -- number of references
    metadata JSON,
    FOREIGN KEY (source_symbol_id) REFERENCES symbols(id) ON DELETE CASCADE,
    FOREIGN KEY (target_symbol_id) REFERENCES symbols(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_deps_source ON dependencies(source_symbol_id);
CREATE INDEX IF NOT EXISTS idx_deps_target ON dependencies(target_symbol_id);
CREATE INDEX IF NOT EXISTS idx_deps_type ON dependencies(dependency_type);
CREATE UNIQUE INDEX IF NOT EXISTS idx_deps_unique ON dependencies(source_symbol_id, target_symbol_id, dependency_type, location_line);

-- Call graph edges (optimized for graph queries)
CREATE TABLE IF NOT EXISTS call_graph (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caller_id INTEGER NOT NULL,
    callee_id INTEGER NOT NULL,
    call_count INTEGER DEFAULT 1,
    call_locations JSON, -- [{file, line}]
    FOREIGN KEY (caller_id) REFERENCES symbols(id) ON DELETE CASCADE,
    FOREIGN KEY (callee_id) REFERENCES symbols(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_callgraph_caller ON call_graph(caller_id);
CREATE INDEX IF NOT EXISTS idx_callgraph_callee ON call_graph(callee_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_callgraph_unique ON call_graph(caller_id, callee_id);

-- Analysis cache (avoid re-parsing unchanged files)
CREATE TABLE IF NOT EXISTS analysis_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    file_hash TEXT NOT NULL, -- SHA256 of file content
    last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    symbols_count INTEGER DEFAULT 0,
    dependencies_count INTEGER DEFAULT 0,
    UNIQUE(repository_id, file_path),
    FOREIGN KEY (repository_id) REFERENCES libraries(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cache_repo ON analysis_cache(repository_id);
CREATE INDEX IF NOT EXISTS idx_cache_hash ON analysis_cache(file_hash);

-- Circular dependencies (pre-computed for performance)
CREATE TABLE IF NOT EXISTS circular_dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository_id INTEGER NOT NULL,
    cycle_hash TEXT NOT NULL, -- hash of sorted cycle
    cycle_path JSON NOT NULL, -- ["A", "B", "C", "A"]
    cycle_length INTEGER NOT NULL,
    severity TEXT, -- LOW, MEDIUM, HIGH
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(repository_id, cycle_hash),
    FOREIGN KEY (repository_id) REFERENCES libraries(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_circular_repo ON circular_dependencies(repository_id);
CREATE INDEX IF NOT EXISTS idx_circular_severity ON circular_dependencies(severity);
