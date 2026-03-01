# Market — CodeSight

**Last updated:** 2026-02

---

## The Core Business

CodeSight is a **consulting tool** — your secret weapon for client engagements.

You walk into a company, point CodeSight at their documents, and in hours they have an AI-powered Q&A system. You charge for the engagement ($5K-$25K). The software is the tool; the expertise is the product.

**You are not competing with Microsoft.** You are solving specific document search problems faster and cheaper than any enterprise vendor.

## The Problem

Companies drown in documents — contracts, proposals, policies, technical specs, compliance records. Finding specific information means manually searching through PDFs, scrolling through SharePoint, or asking colleagues who "might remember." Knowledge workers spend 20%+ of their time searching for information.

## Why Now

1. **LLM answer synthesis** — Claude, GPT-4, and local models can synthesize precise answers from document chunks. The missing piece was always retrieval quality.
2. **Local embedding models** — sentence-transformers makes high-quality embeddings free and fast on commodity hardware. No API keys, no cloud required.
3. **Enterprise AI adoption** — companies are actively looking for AI tools that work with their existing documents. The market is ready.
4. **Data privacy concerns** — companies are wary of sending documents to cloud AI services. Local-first search removes that objection.

## Category

AI-powered document search engine — hybrid BM25 + vector retrieval with pluggable LLM answer synthesis. Delivered as a consulting tool.

## Target User

- **Primary:** Mid-size companies (20-500 employees) who need document collections searchable with AI — delivered via consulting engagement
- **Secondary:** Consulting firms, legal teams, and auditors analyzing large document sets for specific projects (due diligence, audits, compliance)
- **Tertiary:** Companies without Microsoft Copilot who want AI-powered document Q&A at a fraction of the cost

## The Wedge

A consulting engagement that delivers immediate value in hours, not months:

```bash
pip install codesight
python -m codesight index /path/to/client-documents
python -m codesight demo  # launches web chat UI → client is amazed
```

No cloud account. No complex setup. No IT ticket. Runs on a laptop or deploys to their cloud in minutes.

## When CodeSight Wins (vs. When It Doesn't)

| Scenario | CodeSight wins | Why |
|----------|---------------|-----|
| Scoped project (due diligence, audit) | Yes | Point at folder, answers in 5 min. Copilot searches everything. |
| Company without M365 Copilot | Yes | 3% of the cost, same quality for document Q&A |
| Sensitive docs that can't go to cloud | Yes | Search is 100% local. LLM can be local too (Ollama) |
| Small company (20-50 people) | Yes | No per-user licensing. ~$50-200/mo total |
| Air-gapped / regulated environments | Yes | Everything runs locally, no internet required |
| Company already has M365 Copilot | Maybe not | Copilot is built into their workflow already |
| Searching across M365 (email, Teams, SharePoint) | No | That's Microsoft's job. CodeSight searches folders. |

## Competitive Landscape

| Tool | Approach | Weakness | Monthly Cost (50 users) |
|------|----------|----------|------------------------|
| **Microsoft Copilot** | Built into M365 | $30/user/mo, requires M365 E3+ | $1,500 |
| **Glean** | Enterprise search | $$$, long implementation | $5,000+ |
| **Azure AI Search** | Cloud search service | Complex setup, needs developer | $500-2,000 |
| **ChatPDF / AskYourPDF** | Single-document Q&A | One file at a time | $20 |
| **LangChain / LlamaIndex** | RAG frameworks | Developer tools, not products | Free (DIY) |
| **CodeSight** | Hybrid search + LLM | Single-machine, not SaaS (yet) | $50-200 (API only) |

### Positioning

```
        ↑ Answer Quality (High)
        |
        |  Glean ●           Microsoft Copilot ●
        |
        |              [CODESIGHT]
        |                  ●
        |
        |  ChatPDF ●
        |
        |              Ctrl+F / grep ●
        ↓ Answer Quality (Low)
←───────────────────────────────────────→
Enterprise (months)          Quick deploy (hours)
```

**CodeSight is the fastest path from "folder of documents" to "AI-powered Q&A."**

## The Data Privacy Story

This is the strongest selling point in enterprise conversations:

```
Search and indexing:
├── Embedding model runs locally (no API, no internet)
├── BM25 keyword index: local SQLite file
├── Vector index: local LanceDB files
└── Documents never leave the machine. Period.

Answer synthesis (the only external call):
├── Option 1: Client's own Claude API key (Anthropic's policy: no training on API data)
├── Option 2: Client's Azure OpenAI (data stays in their Azure tenant)
├── Option 3: Client's OpenAI key
└── Option 4: Local LLM via Ollama (zero internet, everything on-machine)
```

**"Your documents are indexed and searched entirely on your machine. For answers, you choose the AI provider — or run one locally. We are never in the middle."**

## Cost Comparison

| Solution | Monthly cost (50 users) | Setup time | Data leaves? |
|----------|------------------------|------------|-------------|
| Microsoft Copilot | $1,500/mo | License activation | Yes (Microsoft cloud) |
| Azure AI Search + OpenAI | $500-2,000/mo | Weeks (developer needed) | Yes (Azure) |
| Glean | $5,000+/mo | Months | Yes (Glean cloud) |
| **CodeSight + Claude API** | **$50-200/mo** | **Hours** | **Only answer chunks → Anthropic** |
| **CodeSight + Ollama** | **$0/mo** | **Hours** | **No. Nothing leaves.** |

## Business Model

### Phase 1 — Consulting (Current)

- Deliver codesight as part of consulting engagements
- Implementation: connect to client's documents, configure LLM backend, deploy
- Revenue per engagement: $5K-$25K depending on scope
- Build case studies and refine the product with real clients

### Phase 2 — Self-Serve Product

- **Free:** Single folder, local embeddings, CLI + web UI
- **Pro ($29/mo):** Multiple folders, better embeddings, Slack bot, scheduled re-indexing
- **Team ($99/mo):** Shared deployments, enterprise connectors (M365, Google Drive), access controls

### Phase 3 — Enterprise

- **Enterprise (custom):** Self-hosted, SSO, audit logs, custom connectors, SLA

## Scaling Reality

| Client size | Deployment | LLM backend | Monthly cost |
|-------------|-----------|-------------|-------------|
| 5-10 people | Laptop / single VM | Ollama (local) | $0 |
| 20-50 people | VM or Docker on their cloud | Claude/Azure OpenAI API | $50-500 |
| 100+ people | Docker + FastAPI + auth | Azure OpenAI in their tenant | $200-1,000 |
| Air-gapped | On-prem server | Ollama / vLLM | Hardware cost only |

## Growth Strategy

1. **Consulting engagements** — deliver value, build case studies
2. **Open source core** — GitHub credibility drives inbound
3. **Content marketing** — "How to make your company's documents searchable with AI"
4. **Partner channel** — other consultants use codesight in their engagements
5. **Enterprise connectors** — M365/Google Drive connectors create stickiness

## Moats

1. **Hybrid retrieval (BM25 + vector + RRF)** — better results than vector-only alternatives
2. **Data privacy by design** — search is always local, LLM is client's choice
3. **Pluggable LLM** — works with any provider, not locked to one vendor
4. **Document + code support** — handles PDFs, DOCX, PPTX alongside code files
5. **Consulting relationships** — implementation expertise is hard to replicate
6. **Speed to value** — hours from "folder of documents" to "working Q&A system"

## Kill Criteria

- Microsoft Copilot drops to $5/user/mo (eliminates cost advantage)
- No consulting engagement closes after 3 months of outreach
- Glean or Notion ships a "point at folder" feature that's free/cheap
- Local embedding quality stays too far behind cloud (currently competitive for scoped collections)
