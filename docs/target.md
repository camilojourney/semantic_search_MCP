# Target — codesight

## Primary Persona: IT Decision Maker at Mid-Market Company

**Who:** David, 48, IT Director or Department Head at a mid-size company (100-400 employees). Law firm, consulting firm, manufacturing company, or professional services. Has 5-10 years of company documents scattered across SharePoint, email, and network drives. His team spends hours every week hunting for specific information in old contracts, policies, and technical specs.

**Problem:** "Where is the payment terms clause in the vendor contract from 2022?" takes 45 minutes of folder searching. David's team has institutional knowledge locked in documents that nobody can access efficiently. Microsoft Copilot requires M365 E3+ license for every user. He doesn't want another cloud service sending his company's confidential contracts to a third-party server.

**Context:** David has a limited IT budget and a healthy distrust of cloud services with company data. He needs to see a demo before committing. He's not a developer — he needs to understand the value proposition in business terms, not technical terms. He'll decide in a 30-minute meeting.

**What success looks like for David:** During the demo, Juan points the tool at David's own test folder of 50 documents (David provided them). David types "What are the termination clauses in our vendor agreements?" The answer appears in 3 seconds with citations. David thinks: "This would have saved 3 hours last week." He schedules a follow-up for a pilot proposal.

**Frustrations:**
- "We have thousands of contracts. Finding a specific clause takes half a day."
- "I can't send our contracts to an AI chatbot — our clients would never allow it."
- "We tried Microsoft Copilot but it costs $30/user/month and the search isn't even that good."
- "Our IT team doesn't have bandwidth to build something custom."

---

## Secondary Persona: Consulting Firm for Due Diligence

**Who:** Marcus, 38, senior consultant at a boutique consulting or law firm doing M&A due diligence or legal review. Needs to process 500 documents in 2 weeks for a specific project. Not a permanent deployment — a project-specific tool.

**Context:** Marcus will use codesight for the duration of an engagement, then hand it off or decommission it. Values: fast deployment, easy onboarding of documents, accurate citation, and ability to export findings. The Docker container must be deployable on Marcus's laptop or a client-provided VM.

---

## Anti-Persona

**Developer who wants to self-integrate search:** Would rather use LangChain, ChromaDB, or build their own RAG pipeline. This person has the skills to do it themselves and doesn't need a consulting engagement. They might use codesight's open-source core but won't pay for an engagement.

**Technical startup CTO looking for a search product:** Needs multi-tenant SaaS with API access, webhooks, user management, and usage-based pricing. codesight's consulting model is wrong for them.

---

## Design Tiebreaker

When UX decisions conflict, optimize for **David's demo experience**.

The sales moment is when David types a question about his own documents and gets a correct, cited answer in under 5 seconds. Everything else in the UI is secondary. The Streamlit chat interface must be simple enough that David can use it without training. Complex configuration goes in the CLI — the web UI is for the client, not the developer.

---

## Tone of Voice

- Consulting-professional: authoritative, enterprise-appropriate, clear ROI.
- Business language first, technical second. "Finds answers across all your documents in seconds, with source citations" before "hybrid BM25 + vector retrieval with cross-encoder reranking."
- Trust as a lever. "Your documents never leave your server — the search engine runs entirely on your infrastructure." Lead with privacy.
- Confident about the technology. codesight's hybrid approach is genuinely better than cloud search for scoped collections — say so directly with evidence.
- Precise ROI framing: "If your team spends 2 hours/week searching documents, that's 100+ hours/year at $50-150/hour."
