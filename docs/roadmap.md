# Roadmap — codesight

_Aligned with RESEARCH.md (enterprise knowledge appliance) + STACK-VALIDATION.md_
_Updated: 2026-03-03_

---

## v0.1 — Hybrid Code Search Engine ✅ DONE

- [x] Hybrid BM25 + vector retrieval with RRF merge
- [x] LanceDB vectors + SQLite FTS5 sidecar
- [x] Language-aware regex chunking (10 languages)
- [x] `all-MiniLM-L6-v2` local embeddings (no API key)
- [x] `.gitignore`-aware file walking
- [x] Content hashing (skip unchanged chunks)

## v0.2 — Enterprise Document Search ✅ DONE

- [x] Package rename: `semantic_search_mcp` → `codesight`
- [x] Document parsers: PDF (pymupdf), DOCX (python-docx), PPTX (python-pptx)
- [x] Document-aware chunking (paragraph boundaries, page metadata)
- [x] Python API: `CodeSight` class with `index()`, `search()`, `ask()`, `status()`
- [x] Claude answer synthesis with source citations
- [x] Streamlit web chat UI (`demo/app.py`)
- [x] CLI: `python -m codesight index|search|ask|status|demo`
- [x] Auto-index on first search, auto-refresh when stale

## v0.3 — Pluggable LLM + Better Embeddings ✅ DONE (current)

- [x] Pluggable LLM backend: Claude, Azure OpenAI, OpenAI, Ollama
- [x] `CODESIGHT_LLM_BACKEND` config
- [ ] Upgrade embedding to `nomic-embed-text-v1.5` (768 dims, 8K context)
- [ ] Optional API embedding (OpenAI, Voyage) via `CODESIGHT_EMBEDDING_BACKEND`
- [ ] Cross-encoder reranker after RRF

## v0.4 — Production Deployment + M365 Connectors ⏰ NEXT — Due Mar 14

_This is the consulting-ready version. Must have before first client demo._

- [ ] **Dockerfile** for single-command deployment
- [ ] **FastAPI web server** (replaces Streamlit for multi-user production)
- [ ] **Basic auth middleware** (API key or Bearer token)
- [ ] **Microsoft Graph connector** — SharePoint + OneDrive (priority #1 connector)
- [ ] **Outlook/Exchange connector** — email indexing via Graph API
- [ ] **Email parsing** — `.eml`, `.msg`, `.xlsx` file formats
- [ ] **Document sync** — pull from Azure Blob, S3, local mount
- [ ] Concurrent request handling (async search + LLM calls)

## v0.5 — ACL Enforcement ⏰ Due Mar 21

_The core differentiator. This is what makes CodeSight enterprise-grade._

- [ ] **SSO integration** — OIDC/OAuth2 identity resolution
- [ ] **Group membership mapping** — Entra ID / Active Directory groups
- [ ] **Query-time permission filtering** — construct ACL filter from user identity
- [ ] **SharePoint permission sync** — map Graph API permissions to search filters
- [ ] **Audit logging** — every query logged with user, results, permissions applied
- [ ] Filter applied BEFORE LLM sees any content (security guarantee)

## v0.6 — Multi-Strategy Retrieval ⏰ Due Mar 28

_Not everything is RAG. Auto-pick the right strategy per query._

- [ ] **CAG mode** — corpus < 200 pages → dump full context to LLM (skip embeddings)
- [ ] **JIT mode** — live data queries → fetch from Graph API / IMAP at query time
- [ ] **Agentic RAG** — complex multi-source questions → planner picks retrieval chain
- [ ] **Auto-detection** — analyze corpus size + query type → select strategy
- [ ] **RAG** remains default for 200-50K page corpora

## v0.7 — Scale + Advanced Features

- [ ] **Qdrant option** for large deployments (>500K docs) — Mode A at scale
- [ ] **Azure AI Search** integration for Mode B (native security trimming)
- [ ] Incremental refresh (git-diff + file-watcher based)
- [ ] Slack Bot — slash commands + thread Q&A
- [ ] Google Drive connector

## v1.0 — Production Ready

- [ ] Comprehensive test suite (unit + integration + e2e)
- [ ] SSO production hardening (SAML + OIDC)
- [ ] Apple Silicon GPU acceleration (MPS backend)
- [ ] Batch embedding optimization
- [ ] Multi-folder search (cross-collection queries)
- [ ] Compliance reporting (SOC2, HIPAA audit trail)
- [ ] PyPI package publishing

---

## Revenue Milestones

| Version | Date | Milestone |
|---------|------|-----------|
| v0.3 | Now | Demo-ready (laptop, single user) |
| v0.4 | Mar 14 | First consulting demo (multi-user, Docker, M365) |
| v0.5 | Mar 21 | Enterprise-grade (ACL, audit, SSO) |
| v0.6 | Mar 28 | Competitive edge (multi-strategy retrieval) |
| v1.0 | May | Production deployments, first paying clients |
