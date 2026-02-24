# codesight

Semantic code search MCP server — hybrid BM25 + vector + RRF retrieval for Claude Code.

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python -m semantic_search_mcp

# Connect to Claude Code
claude mcp add codesight -- python -m semantic_search_mcp
```

## Tools

| Tool | Description |
|------|-------------|
| `search(query, repo_path?, top_k?, file_glob?)` | Hybrid semantic + keyword search. Auto-indexes if needed. |
| `index(repo_path?, force_rebuild?)` | Build or rebuild the search index. |
| `status(repo_path?)` | Check if a repo is indexed and whether the index is stale. |
| `watch(repo_path?)` | Register a repo for automatic refresh. _(planned)_ |
| `unwatch(repo_path?)` | Unregister a repo. _(planned)_ |

## Usage in Claude Code

```
> Search for where JWT validation happens
> Index this repository first, then find auth middleware
> Search for error handling in src/api/**
```

## Architecture

- **Chunking**: Language-aware regex splitting (10 languages) with context headers
- **Embeddings**: `all-MiniLM-L6-v2` via sentence-transformers (local, no API key)
- **Vector store**: LanceDB (serverless, file-based)
- **BM25**: SQLite FTS5 sidecar
- **Retrieval**: Hybrid BM25 + vector with RRF merge

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full system tour.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SEMANTIC_SEARCH_DATA_DIR` | `~/.semantic-search/data` | Where indexes are stored |
| `SEMANTIC_SEARCH_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Embedding model |
| `SEMANTIC_SEARCH_STALE_MINUTES` | `60` | Index freshness threshold |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

See [.env.example](.env.example) for all options.

## Stack

- Python 3.11+
- FastMCP
- LanceDB
- sentence-transformers
- SQLite FTS5
