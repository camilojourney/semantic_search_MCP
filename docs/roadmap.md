# Roadmap — codesight

## v0.1 — Hybrid Code Search Engine ✅

- [x] Hybrid BM25 + vector retrieval with RRF merge
- [x] LanceDB vectors + SQLite FTS5 sidecar
- [x] Language-aware regex chunking (10 languages)
- [x] `all-MiniLM-L6-v2` local embeddings (no API key)
- [x] `.gitignore`-aware file walking
- [x] Content hashing (skip unchanged chunks)

## v0.2 — Enterprise Document Search ✅

- [x] Package rename: `semantic_search_mcp` → `codesight`
- [x] Remove MCP layer (server.py, fastmcp dependency)
- [x] Document parsers: PDF (pymupdf), DOCX (python-docx), PPTX (python-pptx)
- [x] Document-aware chunking (paragraph boundaries, page metadata)
- [x] Python API: `CodeSight` class with `index()`, `search()`, `ask()`, `status()`
- [x] Claude answer synthesis: search → context → Claude API → Answer with citations
- [x] Streamlit web chat UI (`demo/app.py`)
- [x] CLI: `python -m codesight index|search|ask|status|demo`
- [x] Auto-index on first search, auto-refresh when stale

## v0.3 — Pluggable LLM + Better Embeddings (Next)

- [ ] Pluggable LLM backend: Claude API, Azure OpenAI, OpenAI, Ollama (local)
- [ ] `CODESIGHT_LLM_BACKEND` config: `claude` | `azure` | `openai` | `ollama`
- [ ] Upgrade default embedding model to `nomic-embed-text-v1.5` (768 dims, 8K context)
- [ ] Optional API embedding support (OpenAI, Voyage) via `CODESIGHT_EMBEDDING_BACKEND`
- [ ] Cross-encoder reranker after RRF for improved precision
- [ ] Configurable embedding model via environment variable (allowlist validation)

## v0.4 — Deployment & Scaling

- [ ] Dockerfile for single-command deployment
- [ ] FastAPI web server (replaces Streamlit for production multi-user)
- [ ] Basic auth middleware (API key or Bearer token)
- [ ] Document sync scripts (pull from S3, Azure Blob, local mount)
- [ ] Concurrent request handling (async search + LLM calls)

## v0.5 — Incremental Refresh

- [ ] Git-diff based incremental indexing (`git diff --name-only`)
- [ ] File-watcher based incremental indexing (for non-git folders)
- [ ] Only re-embed changed files on refresh
- [ ] Delete vectors for removed files
- [ ] Search-triggered staleness check with configurable threshold

## v0.6 — Slack Bot

- [ ] Slack app with slash commands and conversational Q&A
- [ ] Channel-scoped document collections
- [ ] Thread-based follow-up questions
- [ ] Source citation formatting for Slack

## v0.7 — Enterprise Connectors

- [ ] Microsoft 365 Graph API connector (SharePoint, OneDrive)
- [ ] Google Drive connector
- [ ] Scheduled sync / webhook-triggered re-indexing
- [ ] Access control passthrough

## v1.0 — Production Ready

- [ ] Comprehensive test suite
- [ ] SSO / OAuth integration
- [ ] Apple Silicon GPU acceleration (MPS backend)
- [ ] Batch embedding optimization
- [ ] Multi-folder search (cross-collection queries)
- [ ] PyPI package publishing
- [ ] XLSX / email (.eml, .msg) parsing
