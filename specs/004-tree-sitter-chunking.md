# Spec 004: Tree-sitter Chunking

**Status:** Planned
**Target Version:** v0.4

## Summary

Replace regex-based language-aware chunking with tree-sitter AST parsing. Provides exact AST node boundaries, hierarchical chunking, and correct handling of edge cases that regex misses.

## Acceptance Criteria

- [ ] tree-sitter used for all 10+ supported languages
- [ ] Hierarchical chunking: class → method → block
- [ ] Chunk boundaries align exactly with AST nodes
- [ ] Fallback to window chunking for unsupported languages
- [ ] Average chunk quality improvement measurable via Precision@10 benchmark
- [ ] No regression on existing test suite

## API / Tool Surface

No tool API change — internal chunking implementation only.

## Edge Cases

- Syntax errors in source file: fall back to regex chunking for that file
- Mixed language files (e.g., HTML with embedded JS): chunk by dominant language
- Very deeply nested code: max depth limit to avoid micro-chunks

## Out of Scope

- Full LSP/semantic analysis (that's `serena`'s territory)
- Cross-file reference tracking

## Test Plan

- `tests/test_chunker.py` — tree-sitter output vs regex output on known files
- Benchmark: Precision@10 before/after on standard query set
- Edge case: file with syntax error doesn't crash, falls back gracefully
