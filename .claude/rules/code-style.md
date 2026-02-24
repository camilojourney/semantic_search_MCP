# Code Style — codesight

## Python

- **Version:** Python 3.11+ (use `match` statements, `tomllib`, new union syntax `X | Y`)
- **Line length:** 100 chars (configured in `pyproject.toml`)
- **Formatter/linter:** `ruff` — run `ruff check src/ tests/` before committing
- **Type annotations:** Required on all public functions and methods
- **Imports:** `ruff` handles ordering — `isort`-compatible grouping

## Pydantic

All data models use Pydantic v2. Use `model_config = ConfigDict(...)` not class `Config`.
Settings in `config.py` use `pydantic_settings.BaseSettings`.

## Embedding Models

| Model | Dims | Use case |
|-------|------|----------|
| `all-MiniLM-L6-v2` | 384 | Default — fast, no API key |
| `nomic-embed-text-v1.5` | 768 | Better NL+code balance |
| `jina-embeddings-v2-base-code` | 768 | Best for code-only search |

When adding a new model, add it to this table and to the validation allowlist in `config.py`.

## Async

Use `asyncio` for I/O-bound operations (file reading in bulk indexing). CPU-bound embedding should stay synchronous unless batch sizes > 512 chunks.

## Error Handling

- Raise `ValueError` for invalid inputs caught at the tool boundary
- Use `logger.warning` for recoverable issues (file unreadable, encoding error)
- Never silently swallow exceptions in `indexer.py` or `search.py`
