# ADR-0001: LanceDB Over ChromaDB for Vector Storage

**Date:** 2026-02-24
**Status:** Accepted

## Context

We need an embedded, file-based vector store. No external server. Must handle millions of vectors locally for single-user use.

Candidates: LanceDB, ChromaDB, FAISS.

## Decision

Use **LanceDB**.

## Consequences

- Apache Arrow columnar format — fast reads, efficient disk use
- No server to manage
- Metadata filtering built-in (needed for `file_glob` filtering)
- Write stability: LanceDB has proven stable; ChromaDB has known HNSW corruption issues on abrupt process exit

## Alternatives Considered

| Store | Rejected Because |
|-------|-----------------|
| ChromaDB | HNSW corruption on abrupt exit; `mcp-vector-search` migrated away from it for this reason |
| FAISS | No built-in metadata filtering; manual everything; overkill for local single-user |
