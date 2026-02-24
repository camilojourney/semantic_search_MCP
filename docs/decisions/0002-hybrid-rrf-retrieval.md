# ADR-0002: Hybrid BM25 + Vector + RRF Retrieval

**Date:** 2026-02-24
**Status:** Accepted

## Context

Pure vector search misses exact keyword matches (function names, error codes, variable names). Pure BM25 misses semantic similarity ("authenticate" vs "validate_token"). We need both.

## Decision

Use **hybrid retrieval**: BM25 via SQLite FTS5 + vector search via LanceDB, merged with Reciprocal Rank Fusion (RRF).

```
Query → ┬→ BM25 (FTS5)     → top 20 candidates ─┐
        │                                          ├─ RRF merge → top K
        └→ Vector (LanceDB) → top 20 candidates ─┘
```

RRF formula: `score(d) = Σ 1 / (k + rank(d))` where k=60.

## Consequences

- Significantly better retrieval than vector-only (our key differentiator vs `mcp-vector-search`)
- Zero additional infrastructure — FTS5 is built into Python's `sqlite3`
- BM25 and vector indexes must stay in sync (handled by `indexer.py`)

## Alternatives Considered

| Approach | Rejected Because |
|----------|-----------------|
| Vector-only | Misses exact keyword matches; `mcp-vector-search` does this — not differentiated |
| BM25-only | Misses semantic similarity; grep-level capability |
| Cross-encoder re-ranking | Too slow for interactive MCP use; overkill at this scale |
