# Agent Instructions — codesight

[Project Docs Index]|root: ./docs
|IMPORTANT: Fetch specific files on demand — do not assume content
|architecture: {ARCHITECTURE.md}
|decisions: {docs/decisions/0001-security-invariants.md, docs/decisions/0002-lancedb-over-chromadb.md, docs/decisions/0003-hybrid-rrf-over-vector-only.md}
|playbooks: {docs/playbooks/development.md, docs/playbooks/ship-feature.md, docs/playbooks/investigate-bug.md}
|specs: {specs/README.md, specs/001-hybrid-rrf-retrieval.md, specs/002-language-aware-chunking.md, specs/003-incremental-refresh.md, specs/004-tree-sitter-ast-chunking.md}

---

## Role

codesight is a local MCP server that gives Claude Code semantic search over any codebase. It runs as a subprocess communicating via STDIO JSON-RPC. The user invokes it as an MCP tool — they never interact with the code directly.

**Primary concerns:** retrieval quality, indexing speed, zero data leakage.

## Agent Authority Matrix

### Autonomous — No confirmation needed
- Bug fixes in chunker, embedder, search logic that don't touch security boundaries
- Adding tests, updating docs, improving comments
- Reading any file in the repo
- Running lint and tests (`ruff check`, `pytest`)
- Writing reports to `.self-improvement/reports/`

### Ask First — Propose, wait for approval
- New dependencies in `pyproject.toml`
- Changes to MCP tool signatures (`search`, `index`, `status`, `watch`, `unwatch`)
- Changes to the data directory path or index schema
- New config environment variables

### Never — Hard stop, escalate immediately
- Writing to or deleting files in any indexed repository
- Allowing `repo_path` inputs that traverse outside a validated root
- Returning full file contents from any MCP tool (chunks + line ranges only)
- Committing secrets or API keys

## Workers

| Worker | Trigger | Model |
|--------|---------|-------|
| `manager` | Weekly | Opus |
| `code-improver` | On-demand | Sonnet |
| `security-sentinel` | Weekly | Opus |
| `judge-agent` | Per cycle | Haiku |
| `prompt-optimizer` | Monthly | Sonnet |
| `model-quality-auditor` | Weekly | Sonnet |

## Memory

Each worker with `memory: project` writes to `.claude/agent-memory/<worker>/MEMORY.md`.
Cycle history is in `.self-improvement/memory/trajectory.jsonl`.
Current priorities are in `.self-improvement/NEXT.md`.

## Output Paths

- Worker reports → `.self-improvement/reports/<worker>/YYYY-MM-DD.md`
- Trajectory → `.self-improvement/memory/trajectory.jsonl`
- New specs → `specs/NNN-name.md`
- Decisions → `docs/decisions/NNNN-name.md`
