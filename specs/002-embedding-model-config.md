# Spec 002: Embedding Model Configuration

**Status:** Planned
**Target Version:** v0.2

## Summary

Allow users to configure the embedding model via environment variable. Add `nomic-embed-text-v1.5` and `jina-embeddings-v2-base-code` as options for better retrieval quality on code-heavy repos.

## Acceptance Criteria

- [ ] `SEMANTIC_SEARCH_EMBEDDING_MODEL` env var selects the model
- [ ] Supported values: `all-MiniLM-L6-v2` (default), `nomic-embed-text-v1.5`, `jina-embeddings-v2-base-code`
- [ ] Invalid model name fails fast with clear error message
- [ ] Changing the model invalidates existing index (different dims/space)
- [ ] Model name stored in index metadata for staleness detection
- [ ] File preamble (imports + docstring) prepended to chunk context before embedding

## API / Tool Surface

Environment variable — no tool API change.

```bash
SEMANTIC_SEARCH_EMBEDDING_MODEL=nomic-embed-text-v1.5 python -m semantic_search_mcp
```

## Edge Cases

- User changes model after indexing: auto-rebuild index with new model
- Model not installed: clear error with `pip install` command
- Dim mismatch between stored vectors and loaded model: detected via metadata

## Out of Scope

- API-based embedding models (OpenAI, etc.) — local-only for now
- Multiple models simultaneously — one model per index

## Test Plan

- `tests/test_embeddings.py` — all three models load and produce correct-dimension vectors
- `tests/test_config.py` — invalid model name raises ValueError with helpful message
- Integration: index with model A, change to model B, verify auto-rebuild
