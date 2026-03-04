# Market Research — CodeSight

Last updated: 2026-03-04
Review cadence: 60 days
Next review: 2026-05-03

---

## 1. Market Size

- **TAM:** RAG market: $1.2-1.94B (2024/2025) → $9.86-11B by 2030 at 38-49% CAGR. [CORRECTED, Grade A — Grand View Research + MarketsandMarkets. Round 1 used $6.7B from Market.us which was the broader KM market, not RAG-specific]
- **Broader KM market:** $20.15B (2024) → $62.15B by 2033 at 13.6% CAGR. [VERIFIED, Grade A — Grand View Research]
- **SAM:** Enterprise search market: ~$5.8B (2026), 8.9-10.3% CAGR through 2030. Cloud-based = 66% of revenue and growing fastest. [VERIFIED, Grade B — Grand View Research, Mordor Intelligence, Precedence Research]
- **Target segment:** Mid-market companies (50-500 employees) with internal documentation scattered across Google Drive, Confluence, SharePoint who need AI-powered search with proper access controls. Price-sensitive ($20-30/user/mo range), want self-hosted option.

Broader context: Global generative AI market $59B (2025) → $400B by 2031 at 46% CAGR. AI captured ~50% of all global VC funding in 2025 ($202.3B total AI investment). [VERIFIED, Grade B — Statista, Crunchbase]

Enterprise GenAI adoption: 88% of organizations use AI in at least one function (McKinsey Nov 2025 — includes traditional ML, not just GenAI). 71% regularly use generative AI specifically (McKinsey Mar 2025). But only ~33% have scaled org-wide, and >80% report no tangible EBIT impact. [VERIFIED, Grade B]

95% of enterprise GenAI pilots deliver no measurable P&L impact (MIT "GenAI Divide" report, 2025). Note: this finding is contested by at least one rebuttal publication. [VERIFIED, Grade B]

---

## 2. Competitor Matrix

| Name | Type | Pricing | Key Feature | Our Advantage | Our Gap |
|------|------|---------|-------------|---------------|---------|
| Microsoft 365 Copilot | SaaS add-on | $30/user/mo enterprise [VERIFIED, Grade A] | 15M paid seats, M365 integration | Transparent pricing, no over-permissioning risk, self-hostable | No M365 integration, no brand recognition |
| Glean | SaaS enterprise | ~$45-50/user/mo base + ~$15 AI add-on [VERIFIED, Grade C — no official pricing page] | 100+ connectors, knowledge graph, $208M ARR | 3-4x cheaper, self-hosted option, transparent pricing | Fewer connectors, no enterprise customer base |
| Onyx (ex-Danswer) | OSS + SaaS | Free CE / $20/user/mo Business [VERIFIED, Grade A] | Hybrid search, 40+ connectors, MIT license, $10M seed (Khosla + First Round) | More focused on code/technical docs, potentially better code RAG | Fewer connectors, smaller community (17.6K stars) |
| Atlassian Rovo | SaaS add-on | FREE for Premium/Enterprise subscribers (since Apr 2025); standalone $20/user/mo [VERIFIED, Grade A — Atlassian announcement] | Native Jira/Confluence integration, AI agents | Self-hosted option, works beyond Atlassian ecosystem | No Atlassian integration, zero brand |
| Perplexity Enterprise | SaaS | $40/seat/mo (Pro) / $325/seat/mo (Max) [VERIFIED, Grade B] | Web + internal search combined, 500-10K file limits | Self-hosted, no file limits, deeper code RAG | No web search, less brand recognition |
| NotebookLM Plus | Google Workspace | ~$9/license/mo (enterprise) [VERIFIED, Grade A — Google Workspace core service, Feb 2025] | Google Workspace native, VPC-SC, IAM, data residency | Self-hosted, works beyond Google ecosystem, live connectors | No Google integration |
| GoSearch | SaaS | $25/user/mo [VERIFIED, Grade A] | Positions as "Glean at 1/3 cost" | Self-hosted option, lower price | Less established, fewer features |
| Hebbia | SaaS enterprise | $3K-10K/seat/yr [VERIFIED, Grade A — TechCrunch] | Premium vertical for finance/legal, $700M valuation (a16z) | 10-50x cheaper, horizontal play | No finance/legal vertical specialization |
| Azure AI Search | Infrastructure | $74-$2,800+/SU/mo [VERIFIED, Grade A] | Native M365 ACL, agentic retrieval (preview) | Self-contained product vs raw infrastructure | No built-in LLM layer, requires Azure |
| Vectara | SaaS platform | $100K+/yr [VERIFIED, Grade A] | Hallucination prevention, SOC-2 | 10-50x cheaper, self-hosted option | No anti-hallucination features yet |
| Ragie | RAG-as-a-Service | $0-500/mo [VERIFIED, Grade A] | Developer-friendly, SOC 2 Type II | Full product vs API layer, self-hosted | No SOC 2 yet |
| Notion AI | SaaS add-on | ~$20-28/user/mo all-in [VERIFIED, Grade B] | Enterprise Search with citations, MS/Google/Slack/GitHub connectors | Self-hosted, deeper code RAG | No Notion integration |

Indirect competitors (infrastructure/framework layer):
- **Cohere** ($6.8B valuation, $240M ARR) — enterprises build RAG on Cohere APIs instead of buying a product [VERIFIED, Grade A — TechCrunch]
- **LangChain** ($1.1B valuation, $100M Series B mid-2025) — DIY RAG framework, competes for build-vs-buy decision [VERIFIED, Grade A]

### 2.1 Deep Dives

#### Microsoft 365 Copilot

- What they do well: Massive distribution (450M M365 seats), native integration with Word/Excel/Teams/Outlook
- What they do poorly: Over-permissioning is the #1 adoption blocker — 16% of business-critical data overshared, 802K files at risk per org. Active adoption: ~1.81% of M365 users who touch Copilot Chat actually pay (Aug 2025). [CORRECTED — updated from 3.3% to 1.81%; VERIFIED, Grade B]
- Recent changes: EchoLeak vulnerability (CVE-2025-32711, CVSS 9.3) — zero-click prompt injection via emails. Patched. [VERIFIED, Grade A]
- Threat level: **High** (distribution), but over-permissioning and low adoption create market opening

#### Glean

- What they do well: Enterprise-grade, 100+ connectors, knowledge graph, real-time permission inheritance, Glean Agents (100M+ actions/yr), $208M ARR by Dec 2025 (+89% YoY). [VERIFIED, Grade B — Fortune exclusive confirmed $200M+; $208M is Sacra estimate]
- What they do poorly: Extremely expensive (~$45-50/user/mo base + ~$15 AI add-on estimated). No free tier. No self-hosted. Pricing opaque. [VERIFIED, Grade C]
- Recent changes: Series F at $7.2B valuation (June 2025, Wellington Management), $610M total raised. [VERIFIED, Grade A]
- Threat level: **Medium** — targets large enterprise, price excludes mid-market

#### Onyx (formerly Danswer)

- What they do well: Open-source (MIT), hybrid search, 40+ connectors, Netflix/Ramp/Thales as customers. $10M seed (Khosla + First Round, Mar 2025). Deploys in ~30 minutes. [VERIFIED, Grade A]
- What they do poorly: Document-level ACLs Enterprise only. Smaller community than expected.
- Recent changes: Rebranded from Danswer, added agentic deep research, MCP support, 160K+ messages/week peak
- Threat level: **High** — closest competitor, open-source, similar price ($20/user/mo)

#### Atlassian Rovo

- What they do well: FREE for existing Premium/Enterprise Atlassian subscribers (since April 2025). Native Jira/Confluence/Bitbucket integration. AI agents for workflow automation.
- What they do poorly: Limited to Atlassian ecosystem. No self-hosted option for the AI layer. No code-native search.
- Recent changes: Pricing disruption — free bundling is a Trojan horse for all Atlassian shops.
- Threat level: **High** — free bundling with existing subscriptions is the most aggressive pricing move in the space

---

## 3. Pricing Analysis

| Segment | Current Spend | Willingness to Pay | Evidence |
|---------|-------------|-------------------|----------|
| Mid-market (50-500 employees) | $0-30/user/mo | $15-25/user/mo | Onyx at $20, GoSearch at $25 validate range [VERIFIED, Grade A] |
| Enterprise (500+) | $30-65/user/mo | $30-50/user/mo | Glean ~$45-50+, Copilot $30 [VERIFIED, Grade B] |
| Startups/small teams | $0 (OSS) | $0-10/user/mo | Onyx CE free, Ragie free tier [VERIFIED, Grade A] |

Pricing disruption: Atlassian Rovo is FREE for existing subscribers, Notion AI bundled at ~$20-28/mo. The floor is moving toward bundled/free for companies already in an ecosystem. CodeSight's advantage is ecosystem-independence + self-hosted. [VERIFIED, Grade A]

Gartner: 40% of enterprise apps will feature task-specific AI agents by end of 2026 (up from <5% in 2025). Traditional search volume drops 25% by 2026. [VERIFIED, Grade A — Gartner press releases]

---

## 4. Differentiation

1. **Code-native RAG** — AST-based chunking via tree-sitter: +4.3 Recall@5 on code retrieval vs line-based chunking. No competitor implements AST-aware chunking. [VERIFIED, Grade A — cAST paper, EMNLP 2025]
2. **Self-hosted at mid-market price** — $20-25/user/mo on-premise. Only Onyx CE is comparable but ACLs require Enterprise tier. [VERIFIED, Grade A — Onyx pricing page confirms CE lacks document-level ACL]
3. **Access control from day one** — addresses Copilot's #1 adoption blocker. Document-level ACL without Enterprise pricing. [VERIFIED, Grade A — Concentric AI data on over-permissioning; Onyx Enterprise-only ACL]
4. **Transparent pricing** — vs Glean's opaque sales-only model, Copilot's hidden metered costs, and Rovo's ecosystem lock-in. [VERIFIED, Grade B — Glean has no public pricing page; Copilot metered add-ons confirmed by The Register]

---

## 5. Weaknesses to Address

1. **Connector ecosystem** — Glean 100+, Onyx 40+. Must reach Google Drive, Confluence, SharePoint, Slack, GitHub minimum. Action: prioritize top 5 connectors.
2. **Enterprise credibility** — No SOC 2, no named customers. Action: pursue SOC 2 ($30K-$80K Type II first year). [CORRECTED — updated range from $20K-$60K to $30K-$80K based on Round 2 verification]
3. **Brand/distribution** — Zero recognition vs Microsoft (450M seats), Glean ($7.2B, $208M ARR), and free Rovo bundling. Action: open-source community, developer advocacy.
4. **Hallucination controls** — Vectara positions specifically on this. Action: implement and publish benchmarks.
5. **Agentic capabilities** — Glean, Azure, and Rovo moving to agentic retrieval. Forrester: 30% of enterprise vendors launch MCP servers in 2026. Action: add MCP support + multi-step retrieval.
6. **Source attribution** — all major competitors (Glean, Perplexity, NotebookLM, Onyx, Rovo, Notion AI, Copilot) now have citation/source attribution. This is table stakes, not a differentiator. Action: implement citations from day one. [VERIFIED, Grade B]

---

## 6. CIO Requirements (2026)

Top enterprise buyer asks: [VERIFIED, Grade B — Gartner, Forrester, industry surveys]

1. Inherited permissions / RBAC from existing identity providers
2. Comprehensive audit trails (every query, retrieval, response logged)
3. SOC 2 Type II + EU AI Act compliance readiness
4. Data residency options (EU, US, specific regions)
5. Agentic AI governance (what actions can AI agents take?)
6. Demonstrated ROI (measurable productivity gains, not just "AI-powered")

---

## Sources

1. Grand View Research, "RAG Market Size", grandviewresearch.com (2025) [Primary]
2. MarketsandMarkets, "RAG Market", marketsandmarkets.com (2025) [Primary]
3. Grand View Research, "KM Software", grandviewresearch.com (2024) [Secondary]
4. Fortune, "Glean ARR", fortune.com (2025-12) [Primary]
5. Sacra, "Glean Revenue Estimate", sacra.com (2025) [Secondary]
6. TechCrunch, "Glean $7.2B", techcrunch.com (2025-06-10) [Primary]
7. Atlassian, "Rovo Free for Premium", atlassian.com/blog (2025-04-09) [Primary]
8. Perplexity, "Enterprise Pricing", perplexity.ai/pro (2026) [Primary]
9. Google Workspace Updates, "NotebookLM Plus Core Service", workspaceupdates.googleblog.com (2025-02) [Primary]
10. Hebbia, "Series B", techcrunch.com (2025) [Primary]
11. Onyx, "Seed Round", techcrunch.com (2025-03) [Primary]
12. Concentric AI, "Data Risk Report", concentric.ai (2026) [Primary — 550M+ records]
13. Varonis, "EchoLeak", varonis.com/blog (2026) [Primary]
14. The Register, "Copilot Adoption", theregister.com (2026) [Primary]
15. McKinsey, "State of AI" (Nov 2025) [Primary]
16. MIT, "GenAI Divide", via Fortune (2025-08-18) [Primary]
17. Gartner, "AI Agents Prediction", gartner.com (2025-08) [Primary]
18. Forrester, "Predictions 2026", forrester.com (2026) [Primary]
19. Onyx, "Pricing + GitHub", onyx.app / github.com/onyx-dot-app (2026) [Primary]
20. Cohere, "Funding", techcrunch.com (2025) [Primary]
21. LangChain, "Series B", techcrunch.com (2025) [Primary]
22. Notion, "AI Search", notion.so (2025) [Primary]
23. Statista/Crunchbase, GenAI market (2025) [Primary]
24. cAST, arXiv 2506.15655, EMNLP 2025 [Primary]
