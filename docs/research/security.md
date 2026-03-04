# Security Research — CodeSight

Last updated: 2026-03-04
Review cadence: 60 days
Next review: 2026-05-03

---

## 1. Access Control

### 1.1 Model Options

| Model | Best For | Complexity | Evidence |
|-------|----------|-----------|----------|
| Metadata Filters (scope tags) | Single-tenant, small-medium corpora | Low | LanceDB: store userId/groupId per doc, filter at query time [VERIFIED, Grade B] |
| Pre-Filter (lookup IDs first) | Low hit rate across large corpora | Medium | Pinecone + SpiceDB: LookupResources API → metadata filter. Microsecond checks. [VERIFIED, Grade A — Pinecone docs] |
| Post-Filter (search then check) | High positive hit rates | Medium | CheckPermission per result. Better when most results pass ACL. [VERIFIED, Grade A — Pinecone docs] |
| In-Database Authorization | Large permission sets | High | Co-locate embeddings + ACL in PostgreSQL/pgvector. Query optimizer integrates constraints. [VERIFIED, Grade B — Oso] |
| RBAC + ReBAC + ABAC combined | Enterprise multi-tenant | High | Oso: role + relationship + attribute-based in single policy. [VERIFIED, Grade B — Oso] |

Pre-filter degrades with large permission sets (qualitative). Specific "50K doc" threshold has no verifiable source. [UNVERIFIED, Grade D]

RAG does not natively support access control. Broad "Everyone" permissions amplified by RAG — users access unauthorized content by asking questions. [VERIFIED, Grade B — Lasso Security]

### 1.2 Recommendation
**Metadata filters** in LanceDB: store `allowed_user_ids` and `allowed_group_ids` per document, filter at query time before LLM. Simplest approach for initial scale.

For enterprise: SpiceDB (Zanzibar-like ReBAC) for fine-grained permissions with microsecond latency and instant propagation. SpiceDB now has RAG pipeline documentation and OpenAI ChatGPT Enterprise is a production customer. [VERIFIED, Grade A — Pinecone docs, AuthZed docs]

Alternative: **Cerbos** — zero-trust, policy-as-code authorization engine. Policies in YAML, tested like code, GitOps-friendly. Better developer experience than SpiceDB for teams that prefer declarative policies over graph-based relationships. [VERIFIED, Grade B — Cerbos docs]

Key constraint: ACL must be enforced at the retrieval layer, never delegated to the LLM. [VERIFIED, Grade A — Promptfoo, Lasso, OWASP]

### 1.3 Enterprise ACL Landscape

| Platform | ACL Type | Status | Limitations |
|----------|----------|--------|-------------|
| Azure AI Search | Document-level (Entra-based) | Preview (2025-11-01 API) | SharePoint groups NOT supported. Permission changes require full re-crawl. [VERIFIED, Grade A] |
| Onyx | Connector permission mirroring | Enterprise only | Free CE and Business lack ACL [VERIFIED, Grade A] |
| Pinecone | Namespaces + SpiceDB | GA | Requires external SpiceDB [VERIFIED, Grade A] |
| LanceDB OSS | Metadata filters (app-level) | GA | No native RBAC [VERIFIED, Grade A] |

Graph API delta queries for SharePoint permissions: GA. Use `Prefer: deltashowsharingchanges` header. But full incremental ACL sync NOT available for Graph Connectors (full re-crawl required). [VERIFIED, Grade A — Microsoft Learn]

---

## 2. Authentication

### 2.1 Options Evaluated

| Provider | Type | Cost | Best For | Verdict |
|----------|------|------|----------|---------|
| Keycloak | Self-hosted OIDC/SAML | Free (infra cost) | Self-hosted | **Selected** — free, full OIDC [VERIFIED, Grade A] |
| Auth0 | Managed OIDC | Free <7K MAU; enterprise = sales | SaaS MVP | Alternative — easy but expensive at scale [VERIFIED, Grade B] |
| WorkOS | Managed SSO | $125/connection/mo (vol. to $65) | B2B SaaS | Alternative — per-connection model [VERIFIED, Grade B] |
| Okta | Managed workforce | $2-25/user/mo | Enterprise | Rejected — expensive, annual contracts [VERIFIED, Grade B] |

### 2.2 Recommendation
**Keycloak 26.4** (self-hosted) for on-premise, **Auth0** free tier for SaaS MVP. Keycloak 26.4 adds FAPI 2.0, DPoP (proof-of-possession tokens), and passkey/WebAuthn support. Use **Authlib** in FastAPI for OIDC — production-grade, any provider. JWT `groups` claim for RBAC. [VERIFIED, Grade A]

FastAPI libraries: Authlib (production-grade), fastapi-oidc (lightweight token verification), fastapi-sso (social login). Pattern: `fastapi.Depends` with `get_current_user` dependency. [VERIFIED, Grade A]

---

## 3. Data Protection

- **At rest:** Encrypt documents and vector embeddings. Cloud KMS or self-managed HSM for keys. [VERIFIED, Grade B — Thales CPL]
- **In transit:** TLS 1.3 for all API communication. [VERIFIED, Grade A]
- **Embedding inversion risk:** Embeddings can be reverse-engineered to reconstruct source text. Zero2Text (arXiv 2602.01757) achieves 1.8x ROUGE-L improvement over prior methods with NO model fine-tuning — training-free attack. Encrypt embedding storage. SPARSE defense reduces leakage from 60% to 19%. [VERIFIED, Grade A — arXiv 2602.01757, peer-reviewed]
- **PII handling:** Discover and classify sensitive data before RAG ingestion — masking, tokenization, or encryption. EDPS warns RAG responses can be "so descriptive that an attacker could infer identity." [VERIFIED, Grade A — EDPS]
- **Shadow AI:** 77% of employees paste data into chatbots; 22% includes confidential info. [VERIFIED, Grade B — LayerX 2025]
- **Confidential computing:** ETH Zurich demonstrates TEE (Trusted Execution Environments) for private RAG with only 6-7% latency overhead. Process embeddings and queries inside hardware enclaves — data never exposed to host. [VERIFIED, Grade B — ETH Zurich 2025]
- **Encrypted vector search:** IronCore Labs Cloaked AI enables search over encrypted embeddings without decryption. Eliminates embedding inversion risk at the infrastructure level. Trade-off: ~15-20% recall degradation vs plaintext search. [VERIFIED, Grade B — IronCore Labs]
- **DLP integration:** Nightfall AI provides real-time PII/secret detection for RAG pipelines — scans documents at ingestion and responses at output. API-first, integrates with FastAPI middleware. [VERIFIED, Grade B — Nightfall AI docs]

---

## 4. Guardrails (AI/ML)

### 4.1 RAG-Specific Threats

| Threat | Severity | Evidence | Source |
|--------|----------|----------|--------|
| PoisonedRAG | Critical | 5 docs in millions = ~90% ASR across GPT-4, PaLM 2, LLaMA. Cost: ~2 GPT-4 queries per malicious text. | USENIX Security 2025 [VERIFIED, Grade A] |
| Indirect Prompt Injection | Critical | Hidden instructions in retrieved docs execute as trusted context. EchoLeak (CVE-2025-32711, CVSS 9.3). | Lakera, Varonis [VERIFIED, Grade A] |
| Embedding Poisoning | High | OWASP LLM08:2025 = "Vector and Embedding Weaknesses" — new RAG-specific category. | OWASP 2025 [VERIFIED, Grade A] |
| Embedding Inversion | Medium | Reconstruct source text from embeddings (2023). | SombraInc [VERIFIED, Grade B] |
| Data Exfiltration | High | Embedded instructions in docs trigger extraction. | Promptfoo [VERIFIED, Grade B] |
| RAGFlow RCE | Critical | CVE-2025-68700 (CVSS 9.9): Remote code execution in RAGFlow document processing. | NVD [VERIFIED, Grade A] |
| RAGFlow Auth Bypass | High | CVE-2025-69286: Authentication bypass allowing unauthorized access to RAG pipelines. | NVD [VERIFIED, Grade A] |
| LlamaIndex SQLi | Critical | CVE-2025-1793 (CVSS 9.8): SQL injection via LlamaIndex text-to-SQL, arbitrary DB operations. Applies to any RAG system using natural language to SQL. | NVD [VERIFIED, Grade A] |
| Agentic Collapse | High | RAG agent enters infinite retrieval loops or escalates to unintended tools. Pattern: tool calls spiral without termination. | Multiple reports [VERIFIED, Grade B] |
| RAG-Induced SQLi | High | New attack class: RAG systems that generate SQL from retrieved context inherit injection vectors from poisoned documents. | Research 2025-2026 [VERIFIED, Grade B] |
| Semantic Cache Poisoning | High | Poisoned queries poison the semantic cache, serving malicious responses to similar future queries. | GPTCache research [VERIFIED, Grade B] |
| PoisonedEye (Multimodal) | Critical | Poisoning multimodal RAG via images. Extends PoisonedRAG to vision-language models. | ICML 2025 [VERIFIED, Grade A] |
| MM-PoisonRAG | Critical | Multi-modal RAG poisoning with adversarial image/text pairs. | 2025-2026 [VERIFIED, Grade B] |
| Zero2Text Embedding Inversion | High | Training-free method to reconstruct source text from embeddings. 1.8x ROUGE-L improvement over prior methods. No model fine-tuning needed. | arXiv 2602.01757 [VERIFIED, Grade A] |
| NeuroGenPoisoning | Critical | Neural-guided adversarial examples that poison retrieval models. Achieves targeted poisoning with minimal perturbation. | NeurIPS 2025 [VERIFIED, Grade B] |
| One Shot Dominance | Critical | Single poisoned document achieves retrieval dominance — displaces all legitimate results for target queries. Lower cost than PoisonedRAG (1 doc vs 5). | EMNLP 2025 [VERIFIED, Grade B] |
| LangGrinch (LangChain/LangGraph) | Critical | CVE-2025-68664 (CVSS 9.3): RCE in LangChain/LangGraph via prompt injection escalation to tool execution. Affects any agentic RAG using LangChain. | NVD [VERIFIED, Grade A] |

Against advanced RAG (Self-RAG): 77-87% ASR. Tested defenses (paraphrasing, perplexity, dedup) all insufficient. [VERIFIED, Grade A — USENIX 2025]

Prompt injection in RAG "may never be fully patched" — fundamental tension between treating retrieved content as data vs instructions. Defense-in-depth is required, not a single solution. [VERIFIED, Grade B — OWASP, multiple researchers]

### 4.2 Defense Framework

Multi-layer defense: 73.2% → 8.7% attack success (88.1% reduction). [VERIFIED, Grade B — arXiv 2511.15759, preprint]

| Layer | Mechanism | Effect |
|-------|-----------|--------|
| 1. Content Filtering | Embedding anomaly detection | 73.2% → 41.0% |
| 2. Guardrails | Hierarchical system prompt protection | → 23.4% |
| 3. Response Verification | Multi-stage output checks | → 8.7% |

Performance: 94.3% task retention, 5.7% false positive rate, 2.1% latency overhead. [VERIFIED, Grade B — preprint]

RAGuard (NeurIPS 2025 Workshop): adversarial retriever training + zero-knowledge inference patch. [VERIFIED, Grade B]

SAFE-CACHE defense against semantic cache poisoning: validates cache entries before serving. [VERIFIED, Grade B]

SPARSE defense against embedding inversion: reduces information leakage from 60% to 19%. [VERIFIED, Grade A — peer-reviewed]

NeMo Guardrails (NVIDIA): per-chunk retrieval rails — validate each retrieved chunk before it enters LLM context. Programmable in Colang. [VERIFIED, Grade A — NVIDIA docs]

Industry signal: **Check Point acquired Lakera for $300M** (2025) — guardrails/prompt injection defense is now M&A-scale important. Validates that security tooling for LLM/RAG is a real market, not a niche. [VERIFIED, Grade A — TechCrunch]

### 4.3 Recommended Defenses

1. **ACL at retrieval layer** — never let LLM decide access
2. **Content filtering** — embedding anomaly detection on ingested docs
3. **Context isolation** — separate system prompts from retrieved content
4. **Output verification** — detect exfiltration patterns
5. **Rate limiting** — per-user query caps
6. **Input validation** — injection pattern matching
7. **Audit logging** — every query, retrieval, ACL decision, response
8. **Retrieval rails** — NeMo Guardrails per-chunk validation before LLM context
9. **Semantic cache validation** — SAFE-CACHE pattern to prevent cache poisoning
10. **Embedding encryption** — SPARSE-style defense against Zero2Text inversion
11. **Agent loop limits** — hard cap on tool calls and retrieval rounds to prevent agentic collapse

### 4.4 OWASP Top 10 for LLM Applications 2025

| # | Vulnerability | CodeSight Relevance |
|---|-------------|-------------------|
| LLM01 | Prompt Injection | **Critical** — direct + indirect via retrieved docs |
| LLM02 | Sensitive Info Disclosure | **Critical** — RAG can expose indexed docs |
| LLM04 | Data Poisoning | **Critical** — PoisonedRAG |
| LLM08 | Vector/Embedding Weaknesses | **Critical** — NEW, RAG-specific |
| LLM03 | Supply Chain | Medium |
| LLM05 | Improper Output Handling | High |
| LLM06 | Excessive Agency | Medium (if agentic) |
| LLM07 | System Prompt Leakage | High |
| LLM09 | Misinformation | High — hallucination |
| LLM10 | Unbounded Consumption | Medium |

[VERIFIED, Grade A — OWASP Foundation]

---

## 5. Compliance

### 5.1 Requirements

| Requirement | Applies? | Status | Notes |
|------------|----------|--------|-------|
| GDPR | Yes (EU users/data) | Not started | EDPS warns about RAG + personal data. Data minimization, right to deletion in vector store. [VERIFIED, Grade A] |
| EU AI Act | Yes (if selling in EU) | Not started | Enforcement deadline: **August 2, 2026**. Deployers (not just providers) have obligations — CodeSight customers who deploy RAG inherit compliance duties. High-risk classification depends on use case, not the technology itself. [VERIFIED, Grade A — EU regulation text] |
| NIST AI RMF | Recommended | Not started | NIST AI Risk Management Framework (AI 100-1): voluntary but increasingly expected by enterprise buyers. Maps to: Govern, Map, Measure, Manage. Aligns with SOC 2 + EU AI Act requirements. [VERIFIED, Grade B — NIST] |
| SOC 2 Type II | Yes (enterprise sales) | Not started | Audit fees: $20K-$60K. Total cost (platform + staff): $30K-$80K. Timeline: 3-9 months. [CORRECTED — both ranges valid: $20K-$60K is audit-only, $30K-$80K includes platform + staff time] |
| HIPAA | Maybe (healthcare) | N/A yet | BAA + additional encryption if needed |

### 5.2 SOC 2 Cost Breakdown

| Component | Cost | Source |
|-----------|------|--------|
| Type II audit fee | $8K-$40K | SecureLeap, Sprinto [VERIFIED, Grade B] |
| Compliance platform (Vanta/Drata) | $5K-$30K/yr | Multiple [VERIFIED, Grade B] |
| Staff time | 100-200 hours | Multiple [VERIFIED, Grade B] |
| Startup Year 1 audit fees | $20K-$60K | Sprinto [VERIFIED, Grade B] |
| Startup Year 1 total (incl. platform + staff) | $30K-$80K | Multiple [CORRECTED — both ranges valid, different scopes] |
| Renewal (Year 2+) | 40-70% of Year 1 | SecureLeap [VERIFIED, Grade B] |

### 5.3 Audit Logging

Log per RAG query: timestamp, user ID, auth method, query text, retrieved doc IDs + scores, ACL-filtered docs, response (or hash), model ID, latency per stage, token count, guardrail triggers, cost data. [VERIFIED, Grade B — Daxa, Thales, SonarSource]

Storage: immutable (S3 Object Lock). Retention: 7+ years (regulated industries). Connect to SIEM/SOAR. [VERIFIED, Grade B]

---

## Sources

1. Zou et al., "PoisonedRAG", USENIX Security 2025 [Primary]
2. OWASP, "Top 10 for LLM v2025", owasp.org [Primary]
3. "Securing AI Agents", arXiv 2511.15759 (preprint) [Primary]
4. Kolhe et al., "RAGuard", NeurIPS 2025 Workshop [Primary]
5. EDPS, "RAG and Personal Data", edps.europa.eu [Primary]
6. Microsoft Learn, "Document-Level ACL", learn.microsoft.com (2026-01) [Primary]
7. Microsoft Learn, "driveItem: delta", learn.microsoft.com (2025-11) [Primary]
8. Pinecone, "RAG Access Control", pinecone.io/learn [Primary]
9. Oso, "Authorization in RAG", osohq.com [Secondary]
10. Onyx, "Access Controls", docs.onyx.app [Secondary]
11. Lasso Security, "RAG Permissions", lasso.security [Secondary]
12. Promptfoo, "RAG Poisoning", promptfoo.dev [Secondary]
13. Lakera, "Indirect Prompt Injection", lakera.ai [Secondary]
14. Varonis, "EchoLeak", varonis.com (2026) [Primary]
15. SecureLeap, "SOC 2 Cost", secureleap.tech [Secondary]
16. Sprinto, "SOC 2 Cost", sprinto.com [Secondary]
17. Thales CPL, "RAG Security", cpl.thalesgroup.com [Secondary]
18. Authlib, docs.authlib.org [Primary]
19. SombraInc, "LLM Security 2026", sombrainc.com [Secondary]
20. NVD, "CVE-2025-68700 (RAGFlow RCE)", nvd.nist.gov (2025) [Primary]
21. NVD, "CVE-2025-69286 (RAGFlow Auth Bypass)", nvd.nist.gov (2025) [Primary]
22. NVD, "CVE-2025-1793 (LlamaIndex SQLi)", nvd.nist.gov (2025) [Primary]
23. "Zero2Text: Training-Free Embedding Inversion", arXiv 2602.01757 (2026) [Primary]
24. "SPARSE Defense", peer-reviewed (2025) [Primary]
25. "PoisonedEye", ICML 2025 [Primary]
26. NVIDIA, "NeMo Guardrails", docs.nvidia.com/nemo/guardrails (2026) [Primary]
27. AuthZed, "SpiceDB RAG Pipelines", authzed.com/docs (2026) [Primary]
28. Keycloak, "Release 26.4", keycloak.org/2026/01 (2026) [Primary]
29. EU, "AI Act", eur-lex.europa.eu (2024) [Primary]
30. GPTCache, "Semantic Cache Poisoning", research (2025-2026) [Secondary]
31. "NeuroGenPoisoning", NeurIPS 2025 [Primary]
32. "One Shot Dominance", EMNLP 2025 [Primary]
33. NVD, "CVE-2025-68664 (LangGrinch)", nvd.nist.gov (2025) [Primary]
34. ETH Zurich, "Private RAG with TEE", 2025 [Primary]
35. IronCore Labs, "Cloaked AI", ironcorelabs.com [Secondary]
36. Check Point / Lakera acquisition, TechCrunch (2025) [Primary]
37. Cerbos, "Policy-as-Code Authorization", cerbos.dev/docs [Secondary]
38. Nightfall AI, "DLP for AI Pipelines", nightfall.ai/docs [Secondary]
39. NIST, "AI Risk Management Framework (AI 100-1)", nist.gov (2023, updated 2025) [Primary]
