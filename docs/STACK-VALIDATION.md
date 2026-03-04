# Stack Validation — Research vs Code vs Market Reality
_Generated: 2026-03-03_

---

## Verdict: Research approach is ✅ CORRECT with 3 updates needed

The RESEARCH.md strategy is sound. The market confirms it. Three additions needed based on 2026 trends.

---

## 1. Research Approach Validation

### ✅ CORRECT: Two Deployment Modes (A + B)
- Market confirms: "On-premise holds 60%+ revenue share" of AI knowledge management
- GoSearch, Glean alternatives all moving toward hybrid deploy options
- **Mode A (local-only)** = real differentiator for finance/legal/defense
- **Mode B (Azure-native)** = fastest path to first customer

### ✅ CORRECT: ACL as Core Differentiator
- Microsoft Copilot STILL failing on data governance in 2026
- Glean does ACLs well but costs $45-50/user/mo — out of reach for mid-market
- "Query-time permission filtering" is the right approach
- **This is the #1 selling point. Research nails it.**

### ✅ CORRECT: Hybrid Retrieval (BM25 + Vector + RRF)
- Code already does this better than research describes
- Glean's own blog confirms "dynamic re-ranking" with permissions as best practice
- Most open-source alternatives (Onyx/Danswer) still do vector-only — weak on exact matches

### ✅ CORRECT: Target Market
- Mid-market (100-2000 employees) underserved
- Glean too expensive, Copilot unreliable, open source too raw
- Consulting delivery model is smart for initial traction

### ✅ CORRECT: Unit Economics
- 90% gross margin on Mode B is realistic
- Infrastructure costs accurate for Azure stack

---

## 2. What Research Gets WRONG or is MISSING

### ⚠️ UPDATE NEEDED: Vector DB Choice

**Research says:** Qdrant (local) or Azure AI Search (cloud)
**Code uses:** LanceDB + SQLite FTS5

**Recommendation: Keep LanceDB for Mode A, add Qdrant as scale option**

| | LanceDB | Qdrant |
|-|---------|--------|
| Deployment | Embedded (zero infra) | Separate server |
| Best for | Single-machine, <500K docs | Multi-node, >500K docs |
| ACL filtering | Metadata filter on query | Payload-based filtering (native) |
| Production readiness | Good for consulting demos | Better for enterprise production |
| Maintenance | Zero (file-based) | Needs Docker/service |

**Decision:** 
- Mode A small (<500 employees): LanceDB (current) — zero infra, perfect for consulting
- Mode A large (>500 employees): Qdrant — scales, native filtering
- Mode B: Azure AI Search (as research says) — native security trimming

Update RESEARCH.md to reflect this tiered approach.

### ⚠️ UPDATE NEEDED: Multi-Strategy Retrieval

**Research says:** RAG only
**2026 reality:** RAG is one tool, not the only tool

Add to research:

| Strategy | When to Use | CodeSight Application |
|----------|------------|----------------------|
| **CAG** | Client corpus < 200 pages, rarely changes | Load everything in context. Demo mode. |
| **RAG** | 200-50,000 pages, weekly updates | Current approach. Production default. |
| **JIT Context** | Live data (M365, email, CRM) | Query Graph API/IMAP live at query time |
| **Agentic RAG** | Complex multi-source questions | Agent plans: "search contracts, then check emails, then cross-reference" |

CodeSight should auto-detect:
- Corpus < 200 pages? → CAG (dump in context, skip embeddings)
- Corpus > 200 pages? → RAG (current hybrid approach)
- Query needs live data? → JIT (connector fetches live)
- Multi-hop question? → Agentic RAG (planner + retriever chain)

### ⚠️ UPDATE NEEDED: M365 Connectors Timeline

**Research says:** Core requirement
**Roadmap says:** v0.7 (way too late)

**Move to v0.4.** Every consulting client will ask "can it search my SharePoint?" on day one. This blocks sales.

### ⚠️ MINOR: Embedding Model

**Research says:** BAAI/bge-large-en-v1.5 or Nomic
**Code uses:** all-MiniLM-L6-v2

Both valid. Research recommends better models. Roadmap already plans upgrade to Nomic. Not blocking.

---

## 3. Competitive Landscape Confirmation (2026)

Research competitive analysis is ACCURATE and current:

| Competitor | Research Claim | 2026 Reality |
|-----------|---------------|--------------|
| Glean | $45-50/user, enterprise-only | Confirmed. Still no mid-market option. |
| Microsoft Copilot | Governance failures | Confirmed. Still surfacing unauthorized docs. |
| Onyx (Danswer) | Basic, no enterprise ACL | Confirmed. MIT license, limited support. |
| GoSearch | Not mentioned | NEW competitor — $8/user, RAG-first, faster deploy than Glean |

**Add GoSearch to competitive analysis.** They're positioning as budget Glean. CodeSight's edge: on-prem + ACL + consulting delivery vs their SaaS-only model.

---

## 4. Updated Tech Stack (Aligned)

### Mode A — Local-Only (Target Architecture)
```
Connectors: SharePoint (Graph API) → Outlook (Graph) → File shares (SMB/local)
     ↓
Ingestion: PDF/DOCX/PPTX/email parsers → structure-aware chunking → overlapping chunks
     ↓
Embeddings: BAAI/bge-large-en-v1.5 (1024 dims) or Nomic-embed-text (768 dims)
     ↓
Storage: LanceDB vectors + SQLite FTS5 keywords (small) | Qdrant + SQLite FTS5 (large)
     ↓
Retrieval: Multi-strategy (CAG | RAG | JIT | Agentic RAG — auto-selected)
     ↓
ACL: Query-time permission filtering (SSO → group membership → filtered retrieval)
     ↓
LLM: Llama 3.1 70B / DeepSeek-V3 / Mistral (via Ollama or vLLM)
     ↓
Interface: FastAPI + Web UI | CLI | Slack Bot
     ↓
Audit: Every query logged with user, results, permissions applied
```

### Mode B — Azure-Native (Target Architecture)
```
Connectors: Microsoft Graph API (SharePoint, OneDrive, Outlook, Teams)
     ↓
Ingestion: Same parsers + Azure AI Document Intelligence for complex PDFs
     ↓
Embeddings: text-embedding-3-small (Azure OpenAI)
     ↓
Storage: Azure AI Search (hybrid + vector + security trimming)
     ↓
Retrieval: Multi-strategy (auto-selected)
     ↓
ACL: Entra ID + security trimming filters (native Azure AI Search)
     ↓
LLM: Azure OpenAI GPT-4o (client's own tenant)
     ↓
Interface: FastAPI + Web UI (Azure App Service)
     ↓
Governance: Purview labels, audit logs, compliance reporting
```

---

## 5. What to Build Next (Priority Order)

1. **ACL enforcement** — the differentiator. Without this, you're just another search tool.
2. **M365 connectors** — SharePoint first. Blocks every enterprise sale.
3. **Docker + FastAPI** — production deployment for multi-user.
4. **Multi-strategy retrieval** — CAG for small corpora, JIT for live data.
5. **Embedding upgrade** — Nomic or bge-large (from MiniLM).
6. **Qdrant option** — for large-scale Mode A deployments.
7. **Email parsing** — .eml, .msg (consulting clients have tons of email).
