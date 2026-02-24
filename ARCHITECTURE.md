# Architecture — codesight

> Guided tour of the codebase. WHY things are built, not just WHAT.
> **Last Updated:** 2026-02-24

---

## System Overview

```
Claude Code (user)
      │
      │  MCP JSON-RPC over STDIO
      ▼
semantic_search_mcp server  (src/semantic_search_mcp/)
      │
      ├── search(query) ─────────────────────────────────┐
      │     │                                            │
      │     ├──► BM25 via SQLite FTS5  → top 20         │
      │     └──► Vector via wam   → top 20          │
      │                                     │           │
      │                               RRF merge         │
      │                                     │           │
      │                               top K chunks ◄────┘
      │
      ├── index(repo_path)
      │     ├── Walk files (.gitignore-aware)
      │     ├── Chunk (language-aware regex)
      │     ├── Embed (sentence-transformers)
      │     └── Store (LanceDB + FTS5 sidecar)
      │
      └── status(repo_path) → freshness check

Storage: ~/.semantic-search/data/<repo_hash>/
         ├── lancedb/   (vectors)
         └── fts.db     (SQLite with FTS5)
```

---

## Source Layout (`src/semantic_search_mcp/`)

| File            | Purpose                                                                  |
| --------------- | ------------------------------------------------------------------------ |
| `server.py`     | FastMCP entry point. Registers the 3 MCP tools.                          |
| `indexer.py`    | Orchestrates the index pipeline: walk → chunk → embed → store.           |
| `search.py`     | Hybrid retrieval: BM25 + vector → RRF merge → return chunks.             |
| `chunker.py`    | Language-aware regex chunking. Prepends context headers to chunks.       |
| `embeddings.py` | sentence-transformers wrapper. Handles model loading + MPS acceleration. |
| `store.py`      | LanceDB + SQLite FTS5 dual-write. Content hash deduplication.            |
| `config.py`     | Pydantic settings from env vars. Single config object across the app.    |
| `git_utils.py`  | .gitignore-aware file walking via `pathspec`.                            |
| `types.py`      | Shared Pydantic models (Chunk, SearchResult, IndexStatus).               |
| `__main__.py`   | `python -m semantic_search_mcp` entry point.                             |

**Do not add modules at the top level** — new capabilities go inside existing modules or as new submodules imported from `server.py`.

---

## The 5 MCP Tools

```python
search(query, repo_path?, top_k?, file_glob?) → list[SearchResult]
index(repo_path?, force_rebuild?) → IndexStatus
status(repo_path?) → IndexStatus
watch(repo_path?) → None          # planned v0.3
unwatch(repo_path?) → None        # planned v0.3
```

Tool signatures are the public API contract. **Never change them without a spec and human approval.** Claude Code caches tool definitions — a signature change breaks active sessions.

---

## Retrieval Pipeline (The Core)

```
query string
    │
    ├──────────────────────────────────────────────┐
    │                                              │
    ▼                                              ▼
SQLite FTS5                                    LanceDB
BM25 keyword matching                     vector similarity
(exact function names,                   (semantic meaning,
 error codes, literals)                   concept proximity)
    │                                              │
    └──────────────┬───────────────────────────────┘
                   ▼
          Reciprocal Rank Fusion
          score = Σ 1/(k + rank_i)  where k=60
                   │
                   ▼
            top K chunks
         (with file path + line range)
```

**Why hybrid matters:** Pure vector search misses exact keyword matches (function names, error codes). Pure BM25 misses semantic synonyms. RRF merges both with zero extra infrastructure — SQLite FTS5 is built into Python's `sqlite3`.

---

## Storage Layout

All indexes live in `~/.semantic-search/data/` (outside the indexed repo — never write inside it).

```
~/.semantic-search/data/
└── <sha256(repo_path)[:16]>/
    ├── lancedb/          ← LanceDB vector tables
    │   └── chunks.lance  ← chunk_id, embedding, metadata
    └── fts.db            ← SQLite with FTS5 virtual table
        ├── chunks         ← chunk_id, content, file_path, lines
        └── chunks_fts     ← FTS5 index (auto-synced via triggers)
```

**Content hashing:** Each chunk is hashed `sha256(content)[:16]`. On re-index, unchanged chunks are skipped entirely — no re-embedding, no write.

---

## Chunking Strategy

Language-aware regex splits on scope boundaries (class/function/block) for 10 languages: Python, JS, TS, Go, Rust, Java, Ruby, PHP, C, C++. Unknown languages fall back to sliding window with overlap.

Each chunk gets a context header prepended before embedding:
```
# File: src/auth/jwt.py
# Scope: function validate_token
# Lines: 45-82
```

**Why context headers:** The embedding model needs to know WHERE a chunk lives, not just what it says. Stripping the header gives the user the raw source; keeping it improves retrieval relevance.

---

## Embedding Model

Default: `all-MiniLM-L6-v2` (384 dims, fast, no API key).
Configurable via `CODESIGHT_EMBEDDING_MODEL` env var.
Better options: `jina-embeddings-v2-base-code` (768 dims, code-specific).

**Model mismatch guard:** If a repo was indexed with model A and the current model is B, the server detects the dimension mismatch and forces a full rebuild.

---

## What NOT to Change Without Discussion

1. **RRF k=60 constant** — changing this shifts recall/precision tradeoff. Benchmark before changing.
2. **Data directory location** (`~/.semantic-search/data/`) — changing this invalidates all existing user indexes.
3. **MCP tool signatures** — Claude Code caches them. Breaking change requires version bump.
4. **Content hash algorithm** — changing from `sha256[:16]` invalidates all deduplication state.
5. **FTS5 trigger schema** — the SQLite triggers that sync FTS5 from the chunks table. Incorrect triggers cause silent search failures.
