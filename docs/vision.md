# Vision — codesight

## What It Is

codesight is a semantic code search MCP server for Claude Code. It gives Claude precise, hybrid retrieval over local codebases — combining BM25 keyword search with vector semantic search and Reciprocal Rank Fusion.

## The Problem

Claude Code's built-in search is file-glob-based. For large codebases, finding "where does authentication happen" or "show me all error handling patterns" requires many manual searches or reading many files. This is slow and misses semantic relationships.

## The Solution

An MCP server that pre-indexes the codebase and serves sub-second hybrid search results. When you ask Claude to "find where JWT validation happens", it returns the top K most relevant chunks — not just filename matches.

## Key Differentiator

**Hybrid BM25 + vector + RRF** — no competitor does this for a local embedded MCP server. Pure vector search misses exact keyword matches (function names, error codes). Pure BM25 misses semantic equivalence ("authenticate" vs "validate_token"). Combining both via RRF gets best-of-both-worlds results without additional infrastructure.

## Design Principles

1. **Read-only** — codesight never writes to the indexed repository. Zero risk of corruption.
2. **Zero infra** — local embeddings (no API key), embedded vector store (no server), embedded FTS (SQLite).
3. **Simple tool surface** — 3-5 tools, not 17. Claude should not need to learn a new framework to use it.
4. **Correct by default** — auto-index on first search, auto-refresh when stale. Works without setup.

## Target User

A developer using Claude Code on a medium-large codebase (10K–500K lines). They want Claude to find things faster and with better context than grep-based search.
