# Research — CodeSight

**Last updated:** 2026-02

---

## 1. Hybrid Retrieval Architecture

### Why Hybrid Matters
Pure vector search misses exact keyword matches (vendor names, contract numbers, dates, section references). Pure BM25 misses semantic synonyms and conceptual relationships ("payment terms" vs "billing schedule"). Hybrid retrieval with Reciprocal Rank Fusion (RRF) combines both with zero extra infrastructure.

**This is CodeSight's main advantage over cloud competitors.** Most cloud search services (Azure AI Search, Glean) use vector-only search. Our hybrid approach catches what they miss.

### Implementation
```
query string
    |
    +------------------------------------------+
    |                                          |
    v                                          v
SQLite FTS5                                LanceDB
BM25 keyword matching                  vector similarity
(exact names, dates,                   (semantic meaning,
 contract numbers)                      concept proximity)
    |                                          |
    +----------------+-------------------------+
                     v
          Reciprocal Rank Fusion
          score = sum 1/(k + rank_i)  where k=60
                     v
              top K chunks
```

### RRF Parameters
- k=60 is the standard constant from the RRF paper (Cormack et al.)
- Changing k shifts recall/precision tradeoff — benchmark before modifying
- Each retriever contributes top 20 results before fusion

### Local vs Cloud Search Quality

For **scoped document collections** (hundreds to thousands of documents), local hybrid search is competitive with cloud:

| Factor | Cloud (Azure AI Search) | CodeSight (local) |
|--------|------------------------|-------------------|
| Embedding model | Large (3072 dims) | Medium (384-768 dims) |
| Keyword matching | Sometimes | Always (BM25 + FTS5) |
| Hybrid fusion | Rare | Always (RRF) |
| Reranking | Sometimes | Planned (cross-encoder) |
| For 500 docs | Overkill | Right-sized |
| For 5M docs | Correct choice | Not designed for this |

**Bottom line:** For the scoped project work we deliver in consulting (500-5K documents), local hybrid search matches or beats cloud vector-only search.

## 2. Embedding Models

### How Local Embedding Works

The embedding model runs on the machine. Downloaded once (~80-270MB), stored in `~/.cache/torch/`. No API call, no internet, no per-query charge. Ever.

```
Document text → model converts to N-dimensional vector (numbers)
"payment terms are net 30" → [0.23, -0.11, 0.87, ...]
Runs on CPU/GPU. Cost: $0.
```

### Model Comparison

| Model | Dims | Context | Size | Quality | Local? | Cost |
|-------|------|---------|------|---------|--------|------|
| all-MiniLM-L6-v2 | 384 | 256 tokens | 80MB | Good | Yes | Free |
| nomic-embed-text-v1.5 | 768 | 8192 tokens | 270MB | Better | Yes | Free |
| mxbai-embed-large | 1024 | 512 tokens | 670MB | Best local | Yes | Free |
| jina-embeddings-v2-base-code | 768 | 8192 tokens | 270MB | Best for code | Yes | Free |
| text-embedding-3-large (OpenAI) | 3072 | 8191 tokens | — | Best overall | No (API) | $0.13/1M tokens |
| voyage-3 (Voyage AI) | 1024 | 32000 tokens | — | Excellent | No (API) | $0.06/1M tokens |

### Embedding Cost: Local vs API

| | Local (nomic-embed-text-v1.5) | API (OpenAI text-embedding-3-large) |
|--|-------------------------------|-------------------------------------|
| Index 500 docs (~50K chunks) | Free, ~30 seconds | ~$5 |
| Each search query | Free, <5ms | ~$0.0001 |
| Monthly cost (50 users, 20 queries/day) | $0 | $50-200 |
| Internet needed | No | Yes |
| Data leaves machine | No | Yes |

**Recommendation:** Default to `nomic-embed-text-v1.5` (local, free, good quality). Offer API embedding as an upgrade option for clients who want maximum quality and don't mind data going to an API.

### Document Update Flow

Only changed content gets re-embedded:
```
Re-index:
   doc1.pdf → chunks → content hash changed?
   ├── chunk 1: hash same → SKIP (no re-embed)
   ├── chunk 2: hash changed → re-embed, store new vector
   └── chunk 3: new chunk → embed, store
   doc2.pdf → hash same → SKIP entirely
```

### MPS Acceleration
On Apple Silicon Macs, sentence-transformers automatically uses MPS (Metal Performance Shaders) for GPU-accelerated embedding.

### Model Mismatch Guard
If a folder was indexed with model A and the current model is B, the dimension mismatch is detected and forces a full rebuild.

## 3. LLM Answer Synthesis

### How It Works

Search is always local. The LLM is only called for `ask()` — to synthesize a human-readable answer from retrieved chunks.

```
question → search(question) → top 5 chunks (local, free)
         → format chunks as context
         → LLM call → Answer(text, sources, model)
```

### LLM Backend Options

| Backend | Where it runs | Quality | Cost/question | Data leaves? | Scales to |
|---------|--------------|---------|---------------|-------------|-----------|
| Claude API | Anthropic cloud | Best | $0.01-0.03 | Yes (chunks) | Unlimited |
| Azure OpenAI | Client's Azure tenant | Great | $0.01-0.03 | No (their tenant) | Unlimited |
| OpenAI API | OpenAI cloud | Great | $0.01-0.03 | Yes (chunks) | Unlimited |
| Ollama (local) | Same machine | Good-Decent | Free | No | ~5 concurrent users |
| vLLM (self-hosted) | Client's GPU server | Good | Hardware cost | No | ~40 concurrent (per A100) |

### Scaling Reality for Answer Synthesis

```
API (Claude / Azure OpenAI):
   50 users × 20 questions/day = 1000 calls/day
   Cost: $10-30/day ($300-900/month)
   All 50 users get answers in 3-5 seconds simultaneously

Local LLM (Ollama, single machine):
   1 user: answer in 5-10 seconds ✅
   5 users at once: last waits ~50 seconds ⚠️
   50 users at once: not feasible ❌

Self-hosted LLM (vLLM on GPU server):
   $1,500-6,000/month for GPU hardware
   Only makes financial sense at very high volume (5000+ questions/day)
```

**Recommendation:** For most consulting deployments (20-50 users), Claude API or Azure OpenAI. Client uses their own API key. For air-gapped environments, Ollama with a small user group.

### System Prompt Design
The system prompt instructs the LLM to:
- Answer based only on the provided document context
- Cite sources by file name and page/section
- Say "I don't have enough information" rather than hallucinate
- Keep answers concise and factual

## 4. Chunking Strategy

### Code Files — Language-Aware Regex Splitting
10 languages supported: Python, JS, TS, Go, Rust, Java, Ruby, PHP, C, C++. Splits on scope boundaries (class/function/block definitions). Unknown languages fall back to sliding window with overlap.

### Documents — Paragraph-Aware Splitting
PDF, DOCX, and PPTX files are split by paragraph boundaries within pages. Each chunk gets metadata:
- `start_line` / `end_line` = page numbers (1-indexed)
- `scope` = heading or "page N"
- `language` = "pdf", "docx", "pptx"

### Context Headers
Each chunk gets a prepended context header before embedding:
```
# File: contracts/vendor-agreement.pdf
# Scope: section Payment Terms
# Lines: 3-3
```

### Deduplication
Content hash: `sha256(content)[:16]` per chunk. On re-index, unchanged chunks are skipped entirely.

## 5. Document Parsing

| Format | Library | Extraction |
|--------|---------|------------|
| PDF | `pymupdf` (fitz) | Text per page |
| DOCX | `python-docx` | Text per paragraph, grouped by heading sections |
| PPTX | `python-pptx` | Text per slide, with slide title detection |
| Code | built-in | `read_text()` → language-aware chunking |
| Text/MD/CSV | built-in | `read_text()` → sliding window chunking |

## 6. Storage Architecture

### LanceDB (Vector Store)
- Serverless, file-based (no database process)
- Columnar storage optimized for vector operations
- Fast ANN (approximate nearest neighbor) search

### SQLite FTS5 (Keyword Index)
- Built into Python's sqlite3 module (no extra dependency)
- Full-text search virtual table with BM25 ranking
- Auto-synced via database triggers

### Storage Layout
```
~/.codesight/data/
+-- <sha256(folder_path)[:12]>/
    |-- lance/            <- LanceDB vector tables
    +-- metadata.db       <- SQLite with FTS5 virtual table
```

All indexes live outside the indexed folder — never write inside the user's documents.

## 7. Performance Characteristics

### Indexing Speed
| Collection Size | Files | Chunks | Index Time (M1) |
|-----------------|-------|--------|------------------|
| Small (50 docs) | ~50 | ~500 | ~5s |
| Medium (500 docs) | ~500 | ~5,000 | ~30s |
| Large (5K docs) | ~5,000 | ~50,000 | ~5 min |

### Search Latency
- Vector search: ~5ms (LanceDB ANN)
- BM25 search: ~2ms (SQLite FTS5)
- RRF merge: ~1ms
- **Search only: <10ms** (always local, always free)
- **Full ask: 3-6s** (includes LLM API call)

## 8. Reranking (Planned — v0.3)

A cross-encoder reranker is a second model that reads the query AND each result together, scoring relevance more accurately than embedding similarity alone.

```
Without reranker:
   search → top 8 chunks → done

With reranker:
   search → top 20 chunks → reranker scores each → top 5 → done
```

Local reranker options:
- `ms-marco-MiniLM-L-6-v2` — small, fast, runs on laptop
- `bge-reranker-v2-m3` — better quality, still local

This is the single biggest quality upgrade remaining after better embeddings.

## 9. Key Technical Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Vector DB | LanceDB | Serverless, no process, file-based |
| Keyword search | SQLite FTS5 | Built into Python, no dependency |
| Fusion | RRF (k=60) | Simple, effective, no tuning needed |
| Code chunking | Language-aware regex | Preserves code scope boundaries |
| Doc chunking | Paragraph-aware | Respects page boundaries, preserves context |
| Embedding | nomic-embed-text-v1.5 (target) | Local, free, good quality, 8K context |
| Answer LLM | Pluggable (Claude/Azure/Ollama) | Client chooses trust level |
| Doc parsing | pymupdf + python-docx + python-pptx | Well-maintained, no external services |
| Deployment | Docker | Runs on any cloud or on-prem |

## 10. Research Directions

1. **Cross-encoder reranking** — biggest remaining quality improvement
2. **Better embeddings** — upgrade to nomic-embed-text-v1.5 as default
3. **Pluggable LLM** — Claude, Azure OpenAI, OpenAI, Ollama backends
4. **Cross-folder search** — index multiple folders and search across them
5. **Enterprise connectors** — Microsoft 365 Graph API, Google Drive API
6. **XLSX parsing** — spreadsheet support (table-aware chunking)
7. **Email parsing** — .eml and .msg file support
8. **OCR** — image-based PDF support via tesseract or similar
9. **Streaming answers** — stream LLM responses for better UX
10. **FastAPI production server** — replace Streamlit for multi-user deployments
