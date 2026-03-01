# NEXT — codesight

Current top priorities. Updated 2026-03-01 after v0.3 ship.

## Status

- **v0.1** — Core hybrid search engine — done
- **v0.2** — Enterprise pivot (parsers, Python API, Streamlit) — done
- **v0.3** — Pluggable LLM, configurable embeddings, reranking — done
- **v0.4** — Docker + FastAPI deployment — **next**

## P0 — Before v0.4

These unblock the production deployment spec:

- [ ] **Write test suite** — only 2 placeholder tests exist. Need real coverage for:
  - `api.py` — index/search/ask/status round-trip
  - `llm.py` — backend factory, each backend validates env vars
  - `embeddings.py` — LocalEmbedder + APIEmbedder factory
  - `search.py` — reranker integration, RRF merge correctness
  - `parsers.py` — PDF/DOCX/PPTX extraction
  - `config.py` — env var parsing, embedding registry
  - Security invariants: path traversal, read-only, chunk size limits
- [ ] **Fix spec 004 format** — already done (template applied), but tree-sitter chunking itself is deferred to Future

## P1 — Build v0.4 (Spec 008: Docker + FastAPI)

The next spec to implement. Delivers the production deployment package:

1. `src/codesight/web/server.py` — FastAPI app with /api/search, /api/ask, /api/index, /api/status
2. `src/codesight/web/static/` — minimal HTML/JS/CSS chat UI (replaces Streamlit for production)
3. Auth middleware — X-API-Key header validation
4. `Dockerfile` — single-command deployment with pre-downloaded embedding model
5. `docker-compose.yml` — dev/demo compose config
6. Add `[server]` optional dependency group: `fastapi>=0.110`, `uvicorn>=0.30`

Key decisions to make (open questions in spec 008):
- Static SPA vs server-rendered HTML for chat UI?
- WebSocket streaming for LLM responses or plain HTTP?
- Pre-download embedding model in Docker image (~500MB) or on first run?
- Separate admin API key for /api/index?

## P2 — Backlog

- [ ] Spec 003: Incremental refresh (v0.5) — skip unchanged files on re-index
- [ ] Spec 004: Tree-sitter chunking (future) — AST-aware chunking for better code search
- [ ] Benchmark Precision@10 with model-quality-auditor across embedding models
- [ ] First security-sentinel audit on v0.3 codebase
- [ ] Streamlit demo polish (keep as local dev tool alongside production FastAPI)

## Blocked

_Nothing blocked._
