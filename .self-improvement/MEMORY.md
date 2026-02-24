# Self-Improvement Memory — codesight

## Project State

- **Version:** v0.1 (all core features implemented)
- **Test coverage:** 0% (no tests yet — P1 priority)
- **Last audit:** Never

## Architecture Facts

- Package: `src/semantic_search_mcp/` (NOT `src/codesight/`)
- Run command: `python -m semantic_search_mcp`
- Data dir: `~/.semantic-search/data/` (default)
- No external API keys required

## Security Invariants (NEVER violate)

1. No writes to `repo_path` — read-only
2. All resolved paths start with `repo_path` — no path traversal
3. No full file content in search results — chunks only
4. Content hash verified before returning results
5. Data dir isolated from repo_path

## Known Issues

_None recorded yet._

## Lessons

_No lessons yet — first session._
