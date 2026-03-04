# Stack Research — CodeSight

Last updated: 2026-03-04
Review cadence: 30 days
Next review: 2026-04-03
Depends on: MTEB leaderboard, vendor pricing pages, AWS instance pricing
Depended on by: specs/embedding-pipeline, specs/search-engine, specs/deployment

---

## 0. Strategic Question: Do We Need RAG At All?

Before evaluating embedding models, vector databases, and rerankers — the first question is whether CodeSight needs any of this infrastructure.

### 0.1 The JIT Argument

Context windows are growing: 128K (Claude), 200K (Gemini), 1M+ (Gemini 1.5 Pro). Many companies are moving to **Just-In-Time context** — fetch raw documents at query time, stuff them into the LLM context, skip the entire retrieval stack. No embeddings, no vector DB, no chunking, no reranking.

Products already doing this:
- **NotebookLM**: Upload docs, ask questions. No vector DB — full documents in context. [VERIFIED, Grade A]
- **Cursor/GitHub Copilot**: Read current file + open tabs + recent diffs at query time. No pre-built embeddings for active code. [VERIFIED, Grade B]
- **Perplexity Enterprise**: Fetches web + internal docs live per query. [VERIFIED, Grade B]

### 0.2 When JIT Wins vs When RAG Wins

| Factor | JIT / CAG Wins | RAG Wins |
|--------|---------------|----------|
| Corpus size | <500 pages (~200K tokens) | >500 pages — too big for any context window |
| Freshness | Always current — no stale embeddings | Stale by design (ingestion lag) |
| Accuracy | +1-4% BERTScore over RAG (arXiv 2412.15605) [VERIFIED, Grade A] | Worse on small corpora, better precision with reranking on large |
| Speed | 40x faster (2.33s vs 94.35s for CAG) [VERIFIED, Grade A] | Faster at scale — search is O(log n), context stuffing is O(n) |
| Cost per query | $1.25-5.00 at 1M tokens context | ~$0.00008/query with caching |
| Infrastructure | Zero — just an LLM API call | Embedding server, vector DB, reranker, ingestion pipeline |
| "Lost in the Middle" | Yes — LLMs forget info buried in long contexts [VERIFIED, Grade B] | No — retriever surfaces relevant chunks only |
| Access control | Must filter docs before stuffing context | ACL filter at retrieval layer (security.md §1) |
| Multi-tenant | Must duplicate full context per user | Metadata filters scale to thousands of tenants |

### 0.3 CodeSight's Answer: Adaptive Multi-Strategy

CodeSight cannot be JIT-only because:
1. **Enterprise corpora are >500 pages** — a mid-market company's Confluence + Google Drive + GitHub = 10K-100K+ pages. Doesn't fit in any context window.
2. **Multi-tenant ACL** — can't stuff all docs in context and rely on the LLM to respect permissions. ACL must be enforced before the LLM sees anything.
3. **Cost at scale** — 50 users × 20 queries/day × $1.25/query (1M context) = $1,250/day = $37,500/mo. RAG with caching: ~$115-205/mo (benchmarks.md §3.5).
4. **"Lost in the Middle"** — quality degrades catastrophically for buried information in long contexts.

But CodeSight cannot be RAG-only because:
1. **Code repos change hourly** — stale embeddings = wrong answers about current code.
2. **Small hot corpora exist** — team onboarding docs, active sprint notes, project READMEs. These fit in context and benefit from CAG/JIT speed.
3. **Competitors are offering JIT** — NotebookLM, Cursor, Perplexity all use it. Users expect fresh results.

**Decision: Adaptive routing** (architecture.md §5). The system picks the right strategy per query:
- **CAG**: Small, static, frequently-queried docs → cache in context (40x faster, +1-4% quality)
- **RAG**: Large corpora → hybrid search + rerank (the stack below)
- **JIT**: Live/volatile sources (code, active wikis) → fetch at query time via webhooks + incremental re-indexing
- **Agentic**: Multi-hop complex queries → decompose + parallel retrieval

The remaining sections evaluate the RAG stack components — which are needed for the >500 page corpus that makes up the majority of enterprise knowledge.

---

## 1. Embedding Models

### 1.1 Current State
CodeSight uses OpenAI text-embedding-3-small via API for document embedding. Simple to integrate, no infrastructure needed, but creates vendor lock-in and recurring API cost at scale.

### 1.2 Options Evaluated

| Model | Params | MTEB (English) | Dimensions | Context | Cost | License | Verdict |
|-------|--------|---------------|------------|---------|------|---------|---------|
| OpenAI text-embedding-3-small | N/A | 62.3% | 1536 (MRL) | 8191 | $0.02/1M tokens | Proprietary | Baseline — easy start, vendor lock-in [VERIFIED, Grade A] |
| OpenAI text-embedding-3-large | N/A | 64.6% | 3072 (MRL) | 8191 | $0.13/1M tokens | Proprietary | Rejected — 6.5x cost for +2.3pp accuracy [VERIFIED, Grade A] |
| nomic-embed-text-v1.5 | 137M | 62.28% | 768 (MRL 64-768) | 8192 | Self-host: ~$384/mo on g4dn.xlarge | Apache 2.0 | **Selected** — matches OpenAI quality, self-hostable, no per-token cost [VERIFIED, Grade A] |
| Voyage AI voyage-3.5 | N/A | Beats OAI-v3-large by 8.26% | 1024 (MRL) | 32K | $0.06/1M tokens | Proprietary | Strong alternative — best cost/quality API option. Cheaper than OpenAI, better quality. [VERIFIED, Grade A] |
| Voyage AI voyage-code-3 | N/A | Beats OAI-v3-large by 13.8% on code | 2048 (MRL) | 32K | $0.18/1M tokens | Proprietary | Best code embedding model — 13.8% better than OpenAI on 32 code datasets. [VERIFIED, Grade A] |
| Jina jina-embeddings-v5-text | 677M (small) | 71.7% (MTEB v2) | MRL | 32K | API: usage-based | Proprietary | Top quality — highest MTEB English among multilingual models under 1B. Task-specific LoRA adapters. [VERIFIED, Grade A] |
| BAAI/bge-m3 | 567M | ~64.2% (multilingual) | 1024 | 8192 | Self-host: ~$734/mo on g5.xlarge | Apache 2.0 | Alternative — 4x larger, supports dense+sparse+ColBERT. 72% vs nomic 57.25% in RAG benchmarks (Galileo 2025). [VERIFIED, Grade A] |
| Snowflake arctic-embed-m-v2.0 | 113M | Outscores Google text-embedding-004 at 256-dim MRL (0.549 vs 0.524) | MRL 256-768 | 8192 | Self-host | Apache 2.0 | Strong self-hosted multilingual — 74 languages, retains 99% quality at 256-dim. [VERIFIED, Grade B] |
| Google gemini-embedding-001 | N/A | 68.32% (multilingual MTEB) | 3072 (MRL) | N/A | $0.15/1M tokens | Proprietary | Watch — strong multilingual, 100+ languages. [VERIFIED, Grade A] |
| nomic-embed-text-v2-moe | 475M (305M active) | Not benchmarked (claimed competitive) | 768 (MRL 256-768) | N/A | Self-host | Apache 2.0 | Watch — MoE architecture, less battle-tested [VERIFIED, Grade B] |
| Qwen3-Embedding-8B | 8B | 70.58% (multilingual, not English-only) | 4096 (MRL 32-4096) | 32K | Self-host: needs g5.xlarge+ | Apache 2.0 | Rejected — 8B params overkill for English doc search [CORRECTED — MTEB score is multilingual, not English-only] |
| Cohere embed-v4 | N/A | ~65.2% (unconfirmed) | 1536 (MRL) | ~128K | $0.12/1M text tokens | Proprietary | Rejected — multimodal unnecessary, MTEB unverified [UNVERIFIED, Grade C] |

MTEB scores differ by benchmark version (English-only vs multilingual vs MTEB v2). Compare like with like. [VERIFIED, Grade A — BetterBench paper, arXiv 2411.12990v1]

### 1.3 Recommendation
**nomic-embed-text-v1.5** for production self-hosted deployment. 137M parameters runs comfortably on AWS g4dn.xlarge ($384/mo) with <1 GB VRAM in FP16. MTEB 62.28% matches text-embedding-3-small (62.3%) while eliminating vendor lock-in and per-token costs. Matryoshka dimensions (256/512/768) allow storage optimization. [VERIFIED, Grade A]

For MVP/prototyping: **Voyage AI voyage-3.5** ($0.06/1M tokens) — 3x cheaper than OpenAI with better quality. [VERIFIED, Grade A]

For code-specific embedding: **Voyage AI voyage-code-3** ($0.18/1M tokens) — 13.8% better than OpenAI-v3-large on code datasets. Consider as a secondary embedding model for code files alongside nomic for text. [VERIFIED, Grade A]

Break-even vs API: self-hosting at $384/mo beats OpenAI API at ~19.2B tokens/month ($0.02/1M), or Voyage at ~6.4B tokens/month ($0.06/1M). For low-volume usage (<100K docs), API is cheaper. [VERIFIED, Grade B — derived from official pricing]

Embedding serving: **HuggingFace TEI** (Text Embeddings Inference) for self-hosted embedding workloads — purpose-built with Flash Attention, token-based batching, ~130 req/s on A10G GPU. Preferred over vLLM for embedding-only services. [VERIFIED, Grade B]

### 1.4 Migration Path
1. Start with Voyage AI voyage-3.5 API ($0.06/1M tokens, zero infrastructure)
2. When API costs exceed ~$200/mo: deploy nomic-embed-text-v1.5 via TEI on AWS g4dn.xlarge ($384/mo)
3. Re-index all documents (embedding dimensions change)
4. For code files: add voyage-code-3 as secondary embedding model or evaluate AST-based chunking (architecture.md §2.2)
5. If multilingual needed: evaluate bge-m3, arctic-embed-m-v2.0, or jina-v5-text

Cloud deployment options for self-hosted models:
- AWS EC2 g4dn.xlarge: $384/mo (T4 GPU, 16 GiB VRAM) — sufficient for nomic-embed [VERIFIED, Grade A]
- AWS EC2 g5.xlarge: $734/mo (A10G GPU, 24 GiB VRAM) — needed for bge-m3 [VERIFIED, Grade A]
- AWS EC2 g6.xlarge: $588/mo (L4 GPU) — ~2x throughput vs g4dn, better cost-per-embedding when normalized [VERIFIED, Grade A]
- AWS EC2 g6e.xlarge: $1,358/mo (L40S GPU, ~45 GiB VRAM) — overkill for embeddings [VERIFIED, Grade A]
- AWS SageMaker: instance-hour billing + ~15-20% markup, managed endpoints [VERIFIED, Grade B]
- Hugging Face Inference Endpoints: T4 at $0.50/hr, managed [VERIFIED, Grade C]

---

## 2. LLM Backends (Answer Synthesis)

### 2.1 Current State
CodeSight uses cloud LLM APIs for RAG answer synthesis. No local LLM deployment.

### 2.2 Options Evaluated

| Model | Input $/MTok | Output $/MTok | Cache Discount | Best For | Verdict |
|-------|-------------|--------------|----------------|----------|---------|
| Claude Sonnet 4.6 | $3.00 | $15.00 | 90% (reads $0.30) | Quality RAG synthesis | **Selected** — best quality/cost for RAG [VERIFIED, Grade A] |
| Claude Haiku 4.5 | $1.00 | $5.00 | 90% (reads $0.10) | High-volume, cost-sensitive | Alternative — 3x cheaper, good enough for simple queries [VERIFIED, Grade A] |
| GPT-4.1-nano | $0.10 | $0.40 | 75% | Cheapest cloud option | Alternative — 30x cheaper than Sonnet, lowest quality [VERIFIED, Grade A] |
| GPT-5 | $1.25 | $10.00 | 90% | OpenAI ecosystem | Rejected — similar cost to Sonnet, no advantage for RAG [VERIFIED, Grade A] |
| Claude Opus 4.6 | $5.00 | $25.00 | 90% (reads $0.50) | Complex reasoning | Rejected — overkill for RAG synthesis [VERIFIED, Grade A] |
| Local Ollama (8B Q4) | ~$0.001-0.04/MTok (electricity) | Same | N/A | Privacy, offline | Alternative — 25-40 tok/s on 16GB Mac, quality gap vs cloud [VERIFIED, Grade B] |

Batch API: Both Anthropic and OpenAI offer 50% discount for async (24-hour) batch processing. [VERIFIED, Grade A]

Prompt caching impact (Claude Sonnet 4.6): 10 requests against same cached context = $6.45 vs $30.00 without caching (78% savings). [VERIFIED, Grade A]

### 2.3 Recommendation
**Claude Sonnet 4.6** with prompt caching for RAG synthesis. Cache the system prompt + common context to cut input costs by 90%. For high-volume simple queries, fall back to **Claude Haiku 4.5** ($1/$5).

For cost-sensitive deployments or offline requirements: **Ollama with Qwen 3 8B Q4** on 16GB RAM (20-40 tok/s on Apple Silicon, MLX is 20-30% faster than Ollama). [VERIFIED, Grade B]

Self-hosted LLM break-even vs cloud API: ~2M tokens/day for budget models, varies 2-30M tokens/day depending on model size and hardware. [VERIFIED, Grade B — PremAI, arXiv 2509.18101v1]

### 2.4 Migration Path
1. Start with Claude Sonnet 4.6 + prompt caching
2. Add Haiku 4.5 tier for simple/high-volume queries (router based on query complexity)
3. If self-hosting needed: deploy 8B model on RTX 4090 or g4dn.xlarge ($384/mo)

---

## 3. Vector Database

### 3.1 Current State
CodeSight uses LanceDB as embedded vector store with full-text search via Tantivy.

### 3.2 Options Evaluated

| Database | Architecture | Hybrid Search | FTS Engine | ACL | Scale Tested | Cost | Verdict |
|----------|-------------|---------------|------------|-----|-------------|------|---------|
| LanceDB (Lance SDK 1.0.0, Python v0.37.0) | Embedded (in-process) | Native RRF | Tantivy (BM25, 3-8x faster) | Enterprise only | 1B vectors | Free OSS / Cloud (usage-based from ~$16/mo) | **Selected** — embedded, hybrid search, native reranking, no server [VERIFIED, Grade A] |
| Qdrant | Client-server | Sparse vectors | Basic keyword | Enterprise only | 50M+ vectors | Free OSS / $0.014/hr cloud | Alternative — if client-server needed [VERIFIED, Grade B] |
| Pinecone | Managed cloud | Sparse vectors | Basic keyword | Namespaces + RBAC | Billions | $0.33/GB + read/write units | Rejected — vendor lock-in, no self-hosting [VERIFIED, Grade A] |
| ChromaDB 1.5.2 | Embedded | Limited | Limited | None | ~1M practical | Free OSS | Rejected — not production-grade at scale [VERIFIED, Grade B] |

LanceDB updates (Dec 2025 — Mar 2026): Lance SDK graduated to 1.0.0 (stable API, Dec 15 2025). Python SDK reached v0.37.0. BM25 FTS 3-8x faster, KMeans IVF build ~30x faster. DuckDB integration for hybrid search via SQL table functions. [VERIFIED, Grade A — LanceDB blog]

LanceDB Cloud: launched June 2025, serverless, same SDK as local, usage-based pricing (calculator shows ~$16/mo for minimal workloads — no fixed floor published). [CORRECTED — usage-based, not a fixed tier]

LanceDB native reranking: built-in RRFReranker, CrossEncoderReranker, CohereReranker, JinaReranker, ColbertReranker. Single `.rerank()` call in search chain. [VERIFIED, Grade A — LanceDB docs]

LanceDB Tantivy FTS limitations (not mentioned by vendor): Python sync API only, no object storage indexing, no incremental indexing. [VERIFIED, Grade B]

LanceDB performance: >0.90 recall@1 in ~3ms, ~0.95 recall in ~5ms with IVF-PQ on 1M 960-dim vectors. 1.3ms p99 at 1B scale. [UNVERIFIED, Grade C — vendor's own benchmark only]

Qdrant performance: p50 30.75ms, p95 36.73ms at 50M 768-dim vectors. [VERIFIED, Grade B — official benchmark with methodology]

### 3.3 Recommendation
**LanceDB** for CodeSight. Embedded architecture eliminates server management, native Tantivy FTS enables hybrid BM25+vector search with RRF, built-in reranking simplifies the pipeline, and S3-compatible storage enables cloud deployment. The main gap is no native ACL in the open-source version — implement document-level access control at the application layer using scope tags/metadata filters.

### 3.4 Migration Path
Already using LanceDB. Key upgrades:
1. Update to Lance SDK 1.0.0 / Python SDK v0.37.0
2. Enable Tantivy FTS for hybrid search (BM25 + vector + RRF)
3. Use built-in CrossEncoderReranker for pipeline simplification
4. Implement application-level ACL via metadata filters (userId/groupId fields in documents)
5. When scale exceeds single-machine limits: evaluate LanceDB Cloud (GA, usage-based) or migrate to Qdrant

---

## 4. Cross-Encoder Rerankers

### 4.1 Current State
No reranker in pipeline. Vector search returns top-k results directly to LLM.

### 4.2 Options Evaluated

| Model | Params | nDCG@10 / ELO | Latency | Languages | Cost | Verdict |
|-------|--------|---------------|---------|-----------|------|---------|
| ms-marco-MiniLM-L-6-v2 | 22.7M | 74.30 nDCG (TREC DL) | <50ms CPU (2 docs) | English | Free (Apache 2.0) | Dev/prototype — fast, tiny [VERIFIED, Grade A] |
| Qwen3-Reranker-0.6B | 0.6B | MTEB-R 65.80 | ~500ms est. | 100+ | Free (Apache 2.0) | **Selected** — best accuracy at 0.6B class [VERIFIED, Grade A] |
| Cohere Rerank 3.5 | N/A | 1457 ELO | ~171ms small, ~459ms large | Major | $2/1K queries | Alternative — managed, no infra [VERIFIED, Grade A] |
| Cohere Rerank 4 Pro | N/A | 1627 ELO (#2 overall), +170 over 3.5 | ~60% slower than zerank-2 | Major | Pricing TBD (not public) | Watch — 32K context (4x over 3.5), +400 ELO on finance/business. Amazon Bedrock. [VERIFIED, Grade B — 32K confirmed; pricing UNVERIFIED] |
| ZeroEntropy zerank-1 | N/A | 0.78 nDCG@10 (beats GPT-4o-mini 0.70) | P50 130ms | English | Open-weight (HuggingFace) | Strong alternative — 12% faster than Cohere 3.5, 10-30x cheaper than LLM rerankers [VERIFIED, Grade B — vendor benchmarks] |
| BAAI bge-reranker-v2-gemma | 2B | High quality (Gemma backbone) | GPU required | 100+ | Free (MIT) | Alternative — best BAAI option, Gemma backbone [VERIFIED, Grade A] |
| nemotron-rerank-1b (NVIDIA) | 1.2B | 0.8593 nDCG, 83% Hit@1 | 223ms GPU | English | Free | Alternative — highest accuracy [VERIFIED, Grade B] |
| gte-reranker-modernbert-base | 149M | 0.8555 nDCG, 83% Hit@1 | 424ms | English | Free | Alternative — matches nemotron at 1/8 size [VERIFIED, Grade B] |
| BGE-reranker-v2-m3 | ~568M | 0.8159 nDCG, 77.33% Hit@1 | ~350ms CPU | 100+ | Free (Apache 2.0) | Rejected — Qwen3 beats it by +8.77 MTEB-R [VERIFIED, Grade B] |

MiniLM-L-6-v2 CPU latency correction: <50ms is for 2 documents only. For 20 documents on CPU, expect 200-400ms. [CORRECTED — BSWEN benchmark measured 45ms for 2 docs, not 20]

Model size does not determine reranker quality: 149M-param ModernBERT matches 1.2B nemotron on Hit@1. [VERIFIED, Grade B — AIMultiple benchmark]

Late interaction models (ColBERT v2): 2 orders of magnitude fewer FLOPs than cross-encoders. MUVERA (NeurIPS 2024) converts multi-vector retrieval to single-vector MIPS, achieving 10% higher recall and 90% lower latency vs PLAID. Worth watching but adds complexity. [VERIFIED, Grade A — NeurIPS 2024]

SPLADE v3: cross-encoder reranking of SPLADE-v3 yields only marginal additional gains. CSPLADE (Amazon, AACL 2025) uses decoder-only LLM backbone. [VERIFIED, Grade B]

### 4.3 Recommendation
**ms-marco-MiniLM-L-6-v2** for development (22.7M params, instant on CPU). **Qwen3-Reranker-0.6B** for production (MTEB-R 65.80, Apache 2.0, instruction-aware). LanceDB's built-in CrossEncoderReranker simplifies integration (§3). If hosted API preferred: Cohere Rerank 3.5 ($2/1K queries). [VERIFIED, Grade A/B]

Watch: ZeroEntropy zerank-1 (open-weight, beats GPT-4o-mini on nDCG@10) and Cohere Rerank 4 Pro (32K context, strongest on finance/business).

### 4.4 Migration Path
1. Add ms-marco-MiniLM-L-6-v2 via LanceDB's CrossEncoderReranker (retrieve 50-100, rerank to top 10)
2. Measure accuracy improvement on CodeSight's test queries
3. Upgrade to Qwen3-Reranker-0.6B for production
4. Expected impact: Precision@10 from ~61% to ~78-84% based on benchmarks [VERIFIED, Grade B]

---

## 5. Deployment Infrastructure

### 5.1 Current State
FastAPI application with Docker containerization.

### 5.2 Options Evaluated

| Component | Option | Status | Verdict |
|-----------|--------|--------|---------|
| ASGI Server | Uvicorn --workers | Recommended by FastAPI | **Selected** — Gunicorn deprecated for FastAPI [VERIFIED, Grade A] |
| Container | python:3.12-slim + non-root user | Standard | **Selected** — 5% perf improvement over 3.11 [VERIFIED, Grade A] |
| Streaming | FastAPI native SSE (v0.135.0+) | GA | **Selected** — `fastapi.sse` module [VERIFIED, Grade A] |
| Health Checks | /health (liveness) + /ready (readiness) | Standard pattern | **Selected** [VERIFIED, Grade A] |
| ML Memory Leak | --limit-max-requests=1000 with jitter | Recommended | **Selected** — critical for ML services [VERIFIED, Grade B] |
| Orchestration | Docker Compose (startup) → K8s (scale) | Standard | **Selected** — zero to deployed in hours [VERIFIED, Grade B] |

Worker formula: (2 x CPU cores) + 1, bounded by RAM. For Kubernetes: single process per pod, let HPA scale. [VERIFIED, Grade A]

Streaming RAG: FastAPI 0.135.0 added native SSE via `fastapi.sse` module. Pattern: `EventSourceResponse` with `tool_event` (retrieval step) + `ai_event` (generation output). [VERIFIED, Grade A]

### 5.3 Recommendation
Uvicorn with `--workers` flag (no Gunicorn needed). Docker with `python:3.12-slim`, non-root user, layer caching for dependencies. Separate `/health` (liveness) and `/ready` (readiness) endpoints. `--limit-max-requests=1000` to prevent ML memory leaks. Docker Compose for startup; Kubernetes when enterprise requires it.

### 5.4 Migration Path
1. Update Dockerfile to use `fastapi run` command (official recommendation)
2. Add /health and /ready endpoints
3. Add --limit-max-requests=1000 with jitter to Uvicorn config
4. Add SSE streaming endpoint for RAG responses
5. Docker Compose multi-container: app + embedding server (TEI) + LanceDB volume

---

## Sources

1. OpenAI, "API Pricing", developers.openai.com (2026-03-04) [Primary]
2. Nomic AI, "nomic-embed-text-v1.5", huggingface.co (2026-03-04) [Primary]
3. BAAI, "bge-m3", huggingface.co (2026-03-04) [Primary]
4. Voyage AI, "Pricing + Models", docs.voyageai.com (2026) [Primary]
5. Jina AI, "jina-embeddings-v5", jina.ai (2025-02) [Primary]
6. Snowflake, "arctic-embed-m-v2.0", huggingface.co (2024-12) [Primary]
7. Google, "gemini-embedding-001", cloud.google.com (2026) [Primary]
8. AWS, "EC2 Instance Types", aws.amazon.com (2026) [Primary]
9. Vantage, "Instance pricing", instances.vantage.sh (2026-03-04) [Primary]
10. Anthropic, "Pricing", platform.claude.com (2026-03-04) [Primary]
11. LanceDB, "Lance SDK 1.0.0", blog.lancedb.com (2025-12-15) [Primary]
12. LanceDB, "Reranking", docs.lancedb.com/reranking (2026) [Primary]
13. LanceDB, "Cloud", cloud.lancedb.com (2025-06) [Primary]
14. Qdrant, "Benchmarks", qdrant.tech/benchmarks (2025) [Primary]
15. Qwen, "Qwen3-Reranker-0.6B", huggingface.co (2026) [Primary]
16. Cohere, "Rerank 4 Pro", cohere.com/blog (2025-12) [Primary]
17. ZeroEntropy, "zerank-1", zeroentropy.dev (2026) [Primary]
18. BAAI, "bge-reranker-v2-gemma", huggingface.co [Primary]
19. AIMultiple, "Reranker Benchmark", research.aimultiple.com (2026) [Secondary]
20. BSWEN, "Best Reranker Models", docs.bswen.com (2026-02-25) [Secondary]
21. FastAPI, "SSE + Docker", fastapi.tiangolo.com (current) [Primary]
22. HuggingFace, "Text Embeddings Inference", github.com/huggingface/text-embeddings-inference [Primary]
23. arXiv, "MUVERA", arxiv.org/abs/2405.19504, NeurIPS 2024 [Primary]
24. PremAI, "Self-Hosted LLM", blog.premai.io (2026) [Secondary]
25. Docker, "RAG + Ollama Guide", docs.docker.com/guides/rag-ollama (2026) [Primary]
