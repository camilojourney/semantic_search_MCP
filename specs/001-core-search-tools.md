# Spec 001: Core Search Tools

**Status:** Implemented
**Target Version:** v0.1 ✅

## Summary

The three MCP tools that form codesight's primary interface: `search`, `index`, and `status`. These provide hybrid BM25+vector semantic search over local codebases.

## Acceptance Criteria

- [x] `search(query, repo_path?, top_k?, file_glob?)` returns ranked code chunks
- [x] `index(repo_path?, force_rebuild?)` builds or rebuilds the search index
- [x] `status(repo_path?)` returns index health and staleness info
- [x] Auto-index on first `search` call if no index exists
- [x] Auto-refresh when index is stale (file modification detected)
- [x] `.gitignore`-aware file walking (skip `node_modules/`, `.git/`, `dist/`, etc.)
- [x] Language-aware chunking for 10 languages
- [x] Content hashing — skip re-embedding unchanged chunks

## API / Tool Surface

```python
search(query: str, repo_path: str = ".", top_k: int = 10, file_glob: str = "**/*") -> list[Chunk]
index(repo_path: str = ".", force_rebuild: bool = False) -> IndexStatus
status(repo_path: str = ".") -> IndexStatus
```

## Edge Cases

- Empty repo: `index` returns immediately with 0 chunks, `search` returns empty list
- Binary files: skipped by file walker
- Very large files (>1MB): configurable size limit, skip or truncate
- Non-UTF-8 files: skip with warning logged

## Out of Scope

- Writing to `repo_path` — codesight is strictly read-only
- Remote repository support — local paths only
- Authentication — no API keys required for local embeddings

## Test Plan

- `tests/test_search.py` — round-trip: index a test repo, search, verify top result
- `tests/test_indexer.py` — content hashing skips unchanged, re-indexes changed
- `tests/test_security.py` — path traversal blocked, no writes to repo_path
