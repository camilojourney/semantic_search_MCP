# Design System — codesight

**Last updated:** 2026-03-06
**Status:** DEFINED — applies to Streamlit demo theming and any future web surfaces

---

## Brand Identity

codesight is a consulting tool deployed at enterprise clients. The visual language must signal: trustworthy, professional, enterprise-grade. Clients will judge whether to trust it with their confidential documents based partly on whether it looks like a serious tool.

**Aesthetic:** Clean, professional, minimal. Like a well-designed internal enterprise tool. Not: startup SaaS. Not: developer prototype. The closest reference: Notion, Linear, or a clean B2B dashboard.

**Color approach:** Light mode primary (enterprise clients default to light mode). Dark code blocks for contrast.

---

## Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| `--color-bg` | `#ffffff` | Primary background |
| `--color-bg-subtle` | `#f8fafc` | Page background, subtle surfaces |
| `--color-surface` | `#ffffff` | Cards, panels |
| `--color-surface-raised` | `#f1f5f9` | Hover states, secondary surfaces |
| `--color-border` | `#e2e8f0` | Dividers, input borders |
| `--color-border-strong` | `#cbd5e1` | Focused borders, prominent separators |
| `--color-text-primary` | `#0f172a` | Primary text |
| `--color-text-secondary` | `#475569` | Labels, descriptions |
| `--color-text-muted` | `#94a3b8` | Placeholder text, timestamps |
| `--color-accent` | `#0f766e` | Primary interactive (teal — trust + intelligence) |
| `--color-accent-hover` | `#0d6558` | Hover state |
| `--color-accent-light` | `#ccfbf1` | Accent backgrounds (badges, highlights) |
| `--color-success` | `#059669` | Answer found, index complete |
| `--color-warning` | `#d97706` | Indexing in progress, low confidence |
| `--color-danger` | `#dc2626` | Errors, failed queries |
| `--color-code-bg` | `#1e293b` | Code block backgrounds (dark even in light mode) |
| `--color-code-text` | `#e2e8f0` | Code block text |

**Why teal?** Signals intelligence and trust simultaneously. Distinct from generic blue (enterprise software) and purple (AI startup). Appropriate for a tool handling confidential documents.

---

## Typography

| Token | Value | Usage |
|-------|-------|-------|
| `--font-sans` | `'Inter', system-ui, sans-serif` | All UI text |
| `--font-mono` | `'JetBrains Mono', 'Fira Code', monospace` | File paths, citations, code |
| `--font-size-xs` | `11px` | File paths, meta labels |
| `--font-size-sm` | `13px` | Secondary text, citations |
| `--font-size-base` | `15px` | Body text, chat messages |
| `--font-size-lg` | `18px` | Section headings |
| `--font-size-xl` | `24px` | Page headings |
| `--font-size-2xl` | `32px` | Hero (landing page only) |
| `--line-height-tight` | `1.35` | Headings |
| `--line-height-normal` | `1.65` | Body text (slightly looser for readability) |

---

## Spacing

4px grid.

| Token | Value | Usage |
|-------|-------|-------|
| `--space-1` | `4px` | Tight (inline badges) |
| `--space-2` | `8px` | Small gaps |
| `--space-3` | `12px` | Component padding |
| `--space-4` | `16px` | Standard padding |
| `--space-6` | `24px` | Section spacing |
| `--space-8` | `32px` | Large sections |
| `--space-12` | `48px` | Page spacing |

---

## Component Tokens

### Chat Interface

The primary UI is a question/answer chat. Key requirements:

| Element | Value |
|---------|-------|
| Input field border radius | `12px` |
| Input field padding | `12px 16px` |
| Input field height | `52px` |
| Submit button | Teal accent, right-aligned inside input |
| Answer bubble background | `--color-surface-raised` |
| Answer bubble border radius | `12px` |
| Answer bubble padding | `16px 20px` |
| Question bubble background | `--color-accent-light` |
| Citation font | `--font-mono`, `--font-size-xs` |
| Citation color | `--color-text-muted` |

### Citation Display

Citations are the most important element after the answer itself. Format:

```
▸ contracts/vendor-agreement.pdf — Page 12, Section "Payment Terms"
▸ policies/data-retention.docx — Section 3.2
```

- Monospace font for file paths
- Subtle background highlight on hover (links to original chunk)
- Always displayed below the answer, clearly separated

### Status Indicators

| State | Color | Label |
|-------|-------|-------|
| Indexing | `--color-warning` | Indexing (N docs) |
| Ready | `--color-success` | N documents indexed |
| Error | `--color-danger` | Index failed |
| Empty | `--color-text-muted` | No documents indexed |

### Progress Bar (indexing)

- Background: `--color-border`
- Fill: `--color-accent`
- Height: `4px`
- Border radius: `2px`
- Must show % complete + document count

---

## Streamlit Theme Config

For the demo (`demo/app.py`), apply via `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#0f766e"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8fafc"
textColor = "#0f172a"
font = "sans serif"
```

---

## Responsive Breakpoints

| Breakpoint | Width | Notes |
|------------|-------|-------|
| Mobile | `375px` | Secondary — demo is desktop-first |
| Desktop | `1024px` | Primary target for client demos |
| Wide | `1440px` | Sidebar + chat layout |

---

## Demo Layout

```
┌─────────────────────────────────────────────┐
│ codesight          [folder: /contracts] [●] │  ← header + index status
├───────────┬─────────────────────────────────┤
│           │                                 │
│  Index    │   Chat                          │
│  Status   │                                 │
│  ───────  │   [Previous Q&A history]        │
│  N docs   │                                 │
│  indexed  │   ─────────────────────────     │
│           │                                 │
│  Sources  │   [Answer bubble]               │
│  ───────  │   ▸ file.pdf — Page 3           │
│  file1    │   ▸ file2.docx — §2.1           │
│  file2    │                                 │
│  file3    │   ─────────────────────────     │
│           │                                 │
│           │   [Ask a question...        >]  │
└───────────┴─────────────────────────────────┘
```
