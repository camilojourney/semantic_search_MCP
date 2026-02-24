# Spec 003: Incremental Refresh

**Status:** Planned
**Target Version:** v0.3

## Summary

Instead of full re-indexing on changes, use git-diff to identify changed files and only re-embed those. Reduces refresh time from minutes to seconds on large repos.

## Acceptance Criteria

- [ ] `git diff --name-only <last-indexed-commit>` identifies changed files
- [ ] Only changed files are re-chunked and re-embedded
- [ ] Deleted files have their vectors and FTS entries removed
- [ ] Renamed files handled correctly (delete old, insert new)
- [ ] `index(force_rebuild=True)` still triggers full rebuild
- [ ] Staleness threshold: configurable via `SEMANTIC_SEARCH_STALE_MINUTES` (default: 60)

## API / Tool Surface

No new tools. `status()` reports last-indexed commit hash.

## Edge Cases

- Non-git repo: fall back to mtime-based staleness check
- Merge commits: diff against merge base
- Binary files changed: skip (already filtered)
- Very large diff (>1000 files): full rebuild is cheaper

## Out of Scope

- Tracking untracked files (outside git) — mtime fallback handles this
- Submodule support

## Test Plan

- `tests/test_incremental.py` — modify one file, verify only that file re-indexed
- Verify deleted file vectors removed from LanceDB
- Verify non-git repo falls back to mtime
