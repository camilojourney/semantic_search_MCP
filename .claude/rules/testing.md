# Testing — codesight

## Framework

- `pytest` with `pytest-asyncio` (`asyncio_mode = "auto"` in pyproject.toml)
- Test files: `tests/test_<module>.py` mirroring `src/` structure
- Run all: `pytest tests/ -x -v`
- Run fast: `pytest tests/ -x -q --tb=short`

## Required Coverage

These invariants must have tests — they're the security guarantees:

1. Path traversal: `test_security.py` — verify `../` inputs raise `ValueError`
2. Read-only: verify indexer never writes to `repo_path` locations
3. Content hash: verify unchanged chunks are not re-embedded on re-index
4. Chunk size: verify no chunk exceeds 1KB when returned from `search`

## Test Fixtures

Use `tmp_path` (pytest built-in) for temporary index directories.
Use small synthetic repos (3-5 files) for integration tests — never index the codesight repo itself in tests.

## What Not to Test

- Embedding model quality (that's `model-quality-auditor`'s job)
- Retrieval relevance scores (too brittle)
- LanceDB internals — only test our interface to it
