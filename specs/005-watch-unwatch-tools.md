# Spec 005: Watch and Unwatch Tools

**Status:** Planned

## Summary

Add `watch(repo_path)` and `unwatch(repo_path)` MCP tools. `watch` registers a repo for automatic background indexing. `unwatch` removes it. This eliminates the need for manual `index()` calls.

## Acceptance Criteria

- [ ] `watch(repo_path)` registers repo, triggers immediate index if not yet indexed
- [ ] `unwatch(repo_path)` removes repo from watch list
- [ ] `status()` reports all watched repos and their freshness
- [ ] Background refresh runs when `search()` detects stale index
- [ ] Watch list persisted in `SEMANTIC_SEARCH_DATA_DIR` across process restarts

## API / Tool Surface

```python
watch(repo_path: str = ".") -> WatchStatus
unwatch(repo_path: str = ".") -> bool  # True if was watched
```

## Edge Cases

- Path no longer exists at process restart: log warning, remove from watch list
- Watch list with 20+ repos: refresh runs lazily (on search), not eagerly
- Concurrent search + refresh: lock to avoid partial reads

## Out of Scope

- Filesystem watcher (inotify/FSEvents) — too complex, staleness-on-search is sufficient
- Remote repo paths

## Test Plan

- `tests/test_watch.py` — watch/unwatch round-trip
- Watch list persists across process restart
- `status()` reflects watched repos correctly
