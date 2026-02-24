# Security Rules — codesight

> Gates that require confirmation before proceeding.

## Hard Invariants (Never Bypass)

1. **Read-only on indexed repos** — the server reads files to build an index. It NEVER writes to, deletes from, or modifies any file in any indexed repository. Any write operation to a `repo_path` location is a critical bug.

2. **Path traversal prevention** — all `repo_path` inputs must be:
   - Resolved to an absolute path (`Path(repo_path).resolve()`)
   - Checked that they exist and are directories
   - Never allowed to contain `..` after resolution
   - Optionally whitelisted against `CODESIGHT_ALLOWED_PATHS`

3. **No full file exposure** — MCP tools return chunks with file path + line range only. Never return entire file contents. The 1KB chunk limit is intentional.

4. **Content hash integrity** — `sha256(chunk_content)[:16]` must be computed before storage. Never skip hash checking on re-index.

5. **Data directory isolation** — indexes always stored in `~/.semantic-search/data/`, never inside the indexed repo. This prevents accidental indexing of the index.

## Confirmation Required Before

- Any change to `repo_path` validation logic
- Any change that could expose more than chunk-sized content
- New MCP tools that accept file paths as input
- Any network calls (this is a local-only tool by design)

## Environment Variables with Security Impact

| Variable | Risk | Rule |
|----------|------|------|
| `CODESIGHT_ALLOWED_PATHS` | Path whitelist bypass | Validate as real directories |
| `SEMANTIC_SEARCH_DATA_DIR` | Index location | Must be outside any repo root |
| `CODESIGHT_EMBEDDING_MODEL` | Model substitution | Validate model name against allowlist |
