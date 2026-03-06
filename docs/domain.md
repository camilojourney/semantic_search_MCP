# Domain Profile: codesight

## Domain

Hybrid BM25 + vector search engine for document collections, deployed as a consulting tool. The product is the consulting engagement, not the software. The engine runs 100% locally for search/indexing (no data leaves the client's machine) — only LLM answer synthesis optionally calls an external API. The read-only invariant is the most critical security constraint.

## Non-Obvious Constraints

- **Read-only is the hardest invariant.** The engine NEVER writes to the indexed folder. Data goes: folder → index (in `~/.codesight/data/`). Never the reverse. Any code path that writes to the indexed folder is the worst possible bug — it could corrupt client documents.
- **RRF k=60 constant should not change without benchmarking.** Reciprocal Rank Fusion merges BM25 and vector rankings. The k=60 constant balances recall vs precision. Changing it shifts the merge behavior in ways that are hard to predict without evaluation. Don't touch it without running the eval suite.
- **Hybrid search beats vector-only for scoped document sets.** Vector search misses exact keyword matches (contract numbers, dates, vendor names, section references). BM25 misses semantic synonyms. RRF merges both. For the typical client use case (contracts, policies, technical specs), pure vector is wrong.
- **Content hash deduplication on re-index is a cost and time saver.** `sha256(chunk_content)[:16]` before embedding. Unchanged content is never re-embedded. For large document collections re-indexed after minor edits, this prevents expensive and slow re-embedding of the entire corpus.
- **Path traversal is a security constraint.** `folder_path` inputs must be validated against a whitelist or resolved to real paths. Never allow `../` escapes. An attacker could index `/etc/passwd` if path validation is missing.
- **Consulting model means the demo is the sales pitch.** "Point it at a folder, ask questions" must work in under 5 minutes. The TTFHW (Time To First Hello World) is the close. A complex setup flow kills the deal.
- **LanceDB + SQLite FTS5 is the dual-write store.** LanceDB for vectors, SQLite FTS5 for BM25 keyword search. Both write to `~/.codesight/data/<folder_hash>/`. The FTS5 virtual table is kept in sync via SQLite triggers — do not modify the trigger schema without testing extensively.
- **The data directory is outside the indexed folder.** Indexes live in `~/.codesight/data/`, not inside the client's document folder. This is intentional — it prevents index files from being indexed, and it enforces the read-only invariant for the indexed folder.

## Production Environment

- **Deployment:** Docker container on client infrastructure (Azure, AWS, GCP, on-prem, or a laptop)
- **Runtime:** Python, pip-installed
- **Search:** LanceDB (vectors, local files) + SQLite FTS5 (keywords, local files)
- **Embedding:** sentence-transformers model (~270MB, CPU/GPU, downloaded once locally)
- **LLM:** Pluggable — Claude API, Azure OpenAI, OpenAI API, or Ollama (local). Client chooses.
- **Interface:** Streamlit web chat UI, CLI, planned Teams/Slack bots
- **Scale:** Hundreds to thousands of documents per deployment (not millions — this is scoped document work)
- **Cost:** Zero ongoing search cost (local index). LLM answer synthesis cost depends on client's chosen backend.

## Known Anti-Patterns

- **Writing to the indexed folder:** The most critical violation. The engine is read-only with respect to the data it indexes.
- **Vector-only search:** Misses exact keyword matches. Always use BM25 + vector + RRF.
- **Returning full file contents in search results:** Search returns chunks (50-500 lines), never entire files. Full file exposure exceeds LLM context windows and is a data exposure risk.
- **Re-embedding unchanged content on re-index:** Expensive and slow. Always check content hash before embedding.
- **Changing the data directory location:** `~/.codesight/data/` is the fixed path. Moving it invalidates all existing indexes silently — users would get empty results on all queries.
- **Changing the FTS5 trigger schema without testing:** The SQLite triggers that sync chunks → chunks_fts are subtle. Incorrect triggers produce silent search failures (no results for keyword queries).
- **Bypassing path validation:** Allows directory traversal attacks and indexing of system files.

## Glossary

- **RRF:** Reciprocal Rank Fusion. The merge algorithm that combines BM25 and vector search rankings. Formula: `score = sum 1/(k + rank_i)` where k=60.
- **BM25:** Best Match 25. A probabilistic keyword ranking algorithm. Used for exact keyword matching via SQLite FTS5.
- **FTS5:** Full-Text Search version 5. SQLite's built-in full-text search extension. Used for the BM25 keyword index.
- **LanceDB:** A local vector database. Used for storing and querying embedding vectors.
- **Cross-encoder reranking:** A second-stage model that re-scores the top-K chunks for precision. Adds +17-22pp over hybrid alone.
- **RAG:** Retrieval-Augmented Generation. The pattern of retrieving relevant chunks and using them as context for LLM answer generation.
- **Hybrid search:** The combination of BM25 (keyword) and vector (semantic) search, merged via RRF.
- **Content hash:** `sha256(chunk_content)[:16]`. Used for deduplication on re-index — unchanged chunks are not re-embedded.
- **Consulting engagement:** The business model. codesight is deployed as a deliverable within a consulting project, not sold as a standalone SaaS subscription.
- **TTFHW:** Time To First Hello World. The elapsed time from "download the tool" to "got my first answer from my documents." This is the sales demo metric.
