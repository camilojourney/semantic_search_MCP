# UX State — codesight

**Last updated:** 2026-03-06
**Overall status:** MINIMAL — Streamlit demo only, no production web UI, no design system

---

## Current Surfaces

| Surface | State | Tech | Location |
|---------|-------|------|----------|
| Streamlit web chat UI | Live (demo) | Python Streamlit | `demo/app.py` |
| CLI | Live | Python argparse | `src/codesight/__main__.py` |
| Teams Bot | Planned (Phase 2) | aiohttp + Bot Framework | `src/codesight/bot/` (stub) |
| Slack Bot | Planned | — | — |
| Landing page / product site | None | — | — |

---

## Current UX State

### Streamlit Chat UI (Primary UI)

The Streamlit demo is the web interface used in client demos and initial deployments.

Current state:
- Streamlit auto-theming — no custom design system applied
- Chat interface for Q&A (ask questions, get answers with citations)
- No custom branding or white-label styling
- No file/folder management UI (indexing is CLI-only)
- No progress indicator during indexing of large document collections
- Session-based (no persistent history across browser sessions)
- Mobile: Streamlit is not mobile-optimized

### CLI (Developer Interface)

The CLI is functional and used for indexing, searching, and status checks. Well-structured but no formal UX audit.

### No Product Landing Page

No web-based marketing site, no demo request flow, no pricing page. All sales happen via direct consulting outreach.

---

## Known UX Issues

| Severity | Surface | Issue |
|----------|---------|-------|
| P0 | Demo UI | No progress indicator during indexing — large document sets appear to hang |
| P0 | Demo UI | No clear error messaging when query fails or index is empty |
| P1 | Demo UI | No way to see what documents are indexed from the web UI |
| P1 | Demo UI | Streamlit reloads on configuration change — loses in-progress conversation |
| P1 | Sales | No landing page for consulting leads to evaluate the product pre-meeting |
| P2 | Demo UI | No citation display formatting (citations may be hard to parse) |
| P2 | Demo UI | No "confidence" or "no answer found" state when retrieval returns no relevant results |
| P3 | General | Streamlit default theme doesn't convey enterprise trustworthiness |

---

## Last Audit

No formal UX audit. No Playwright screenshots. No axe-core scan conducted.

---

## Pending UX Work

**Priority 1 (demo quality — most important for sales):**
- [ ] Progress indicator during indexing (streaming logs or spinner with ETA)
- [ ] Clear "no results" state with suggested query refinements
- [ ] Document index listing (what's been indexed, file count, last updated)
- [ ] Error messages with actionable guidance

**Priority 2 (sales support):**
- [ ] Simple one-page product landing (what it is, how it works, contact for pilot)
- [ ] Branded Streamlit theme (professional, enterprise-appropriate)

---

## Design Notes

The Streamlit UI is the demo and the product. David (primary persona) sees this UI during the 30-minute sales demo. If it looks like a developer prototype, it undermines trust. The goal is not to win design awards — it's to look trustworthy and professional enough that David thinks "this is production-grade."

Three things matter most in the demo UI:
1. Fast response time (answer appears within 3 seconds)
2. Clear source citations (David needs to verify answers against his documents)
3. No confusing errors (any error message during the demo kills the deal)
