# Playbook: Investigate a Bug

## 1. Reproduce

```bash
# Isolate to a fresh data dir to avoid cache interference
export SEMANTIC_SEARCH_DATA_DIR=/tmp/codesight-debug-$(date +%s)
python -m semantic_search_mcp
```

Use MCP Inspector to send the exact failing tool call.

## 2. Check Logs

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python -m semantic_search_mcp
```

## 3. Inspect State

For index corruption issues:
```python
import lancedb
db = lancedb.connect("~/.semantic-search/data/<repo-hash>/vectors")
tbl = db.open_table("chunks")
print(tbl.count_rows())
```

For FTS issues:
```python
import sqlite3
conn = sqlite3.connect("~/.semantic-search/data/<repo-hash>/metadata.db")
print(conn.execute("SELECT count(*) FROM chunks_fts").fetchone())
```

## 4. Verify Read-Only Invariant

```bash
# Should find ZERO results — any write to repo_path is a bug
grep -rn "open.*'w'" src/semantic_search_mcp/
```

## 5. Write a Regression Test

Once fixed, add a test in `tests/` that reproduces the bug.
File name: `test_<module>_<bug_description>.py`
