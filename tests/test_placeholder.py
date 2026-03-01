"""
Placeholder test module. Replace with real tests.

Priority test coverage:
1. test_security.py — read-only invariant, path traversal prevention
2. test_search.py — round-trip: index fixture folder, search, verify top result
3. test_indexer.py — content hashing, incremental updates, document parsing
4. test_parsers.py — PDF/DOCX/PPTX text extraction
"""


def test_placeholder():
    """Placeholder — replace with real tests."""
    assert True


def test_import():
    """Verify the package is importable after rename."""
    from codesight import Answer, CodeSight, IndexStats, SearchResult
    assert CodeSight is not None
    assert Answer is not None
    assert SearchResult is not None
    assert IndexStats is not None
