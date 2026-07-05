"""DDL for the disposable index store (index.db). The lived state (usage,
manifest) lives in the core store, never here — this whole file can be
dropped and re-derived from the markdown at any time."""

MEMORIES = """
CREATE TABLE IF NOT EXISTS memories (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  space TEXT NOT NULL,
  content TEXT NOT NULL,
  topic TEXT,
  bubble TEXT,
  created_at TEXT,
  pointer TEXT NOT NULL,
  meta TEXT NOT NULL DEFAULT '{}',
  provenance TEXT NOT NULL DEFAULT 'sweep',
  source_path TEXT NOT NULL,
  source_hash TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mem_dims ON memories(space, kind, topic);
CREATE INDEX IF NOT EXISTS idx_mem_src  ON memories(source_path);
"""

# external-content FTS5, trigger-synced (the standard pattern)
FTS = """
CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
  content, content='memories', content_rowid='rowid', tokenize='unicode61');
CREATE TRIGGER IF NOT EXISTS mem_ai AFTER INSERT ON memories BEGIN
  INSERT INTO memories_fts(rowid, content) VALUES (new.rowid, new.content);
END;
CREATE TRIGGER IF NOT EXISTS mem_ad AFTER DELETE ON memories BEGIN
  INSERT INTO memories_fts(memories_fts, rowid, content) VALUES('delete', old.rowid, old.content);
END;
CREATE TRIGGER IF NOT EXISTS mem_au AFTER UPDATE ON memories BEGIN
  INSERT INTO memories_fts(memories_fts, rowid, content) VALUES('delete', old.rowid, old.content);
  INSERT INTO memories_fts(rowid, content) VALUES (new.rowid, new.content);
END;
"""

EMBEDDINGS = """
CREATE TABLE IF NOT EXISTS embeddings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  memory_id TEXT NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
  surface TEXT NOT NULL,
  text TEXT NOT NULL,
  model TEXT NOT NULL,
  dim INTEGER NOT NULL,
  content_hash TEXT NOT NULL,
  UNIQUE(memory_id, surface, model)
);
"""

DROP_ALL = """
DROP TRIGGER IF EXISTS mem_ai;
DROP TRIGGER IF EXISTS mem_ad;
DROP TRIGGER IF EXISTS mem_au;
DROP TABLE IF EXISTS memories_fts;
DROP TABLE IF EXISTS embeddings;
DROP TABLE IF EXISTS memories;
"""
