from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from codesight import chunker


def _find_nth(haystack: str, needle: str, occurrence: int = 1) -> int:
    start = -1
    for _ in range(occurrence):
        start = haystack.index(needle, start + 1)
    return start


@dataclass
class FakeNode:
    type: str
    start_byte: int
    end_byte: int
    start_point: tuple[int, int]
    end_point: tuple[int, int]
    children: list["FakeNode"] = field(default_factory=list)
    is_named: bool = True
    has_error: bool = False
    _fields: dict[str, "FakeNode"] = field(default_factory=dict)
    parent: "FakeNode | None" = None

    def __post_init__(self) -> None:
        for child in self.children:
            child.parent = self

    def child_by_field_name(self, name: str):
        return self._fields.get(name)


@dataclass
class FakeTree:
    root_node: FakeNode


class FakeParser:
    def __init__(self, root: FakeNode) -> None:
        self.root = root

    def parse(self, _source: bytes) -> FakeTree:
        return FakeTree(root_node=self.root)


def _mk_node(
    source: str,
    node_type: str,
    snippet: str,
    *,
    occurrence: int = 1,
    name: str | None = None,
    children: list[FakeNode] | None = None,
    has_error: bool = False,
) -> FakeNode:
    start = _find_nth(source, snippet, occurrence=occurrence)
    end = start + len(snippet)
    start_line = source[:start].count("\n")
    end_line = source[:end].count("\n")
    node = FakeNode(
        type=node_type,
        start_byte=start,
        end_byte=end,
        start_point=(start_line, 0),
        end_point=(end_line, 0),
        children=children or [],
        has_error=has_error,
    )
    if name:
        name_start = source.index(name, start, end)
        name_end = name_start + len(name)
        name_node = FakeNode(
            type="identifier",
            start_byte=name_start,
            end_byte=name_end,
            start_point=(source[:name_start].count("\n"), 0),
            end_point=(source[:name_end].count("\n"), 0),
            children=[],
        )
        node._fields["name"] = name_node
    return node


def _mk_root(source: str, children: list[FakeNode]) -> FakeNode:
    return FakeNode(
        type="module",
        start_byte=0,
        end_byte=len(source),
        start_point=(0, 0),
        end_point=(source.count("\n"), 0),
        children=children,
    )


def test_spec_004_001_ast_chunking_supported_languages(monkeypatch: pytest.MonkeyPatch):
    """SPEC-004-001: All supported languages route through AST parsing."""
    source = "def alpha():\n    return 1\n"

    for language in chunker._AST_SCOPE_NODE_TYPES:
        scope_type = next(iter(chunker._AST_SCOPE_NODE_TYPES[language]))
        scope_node = _mk_node(source, scope_type, "def alpha():\n    return 1\n", name="alpha")
        root = _mk_root(source, [scope_node])
        monkeypatch.setattr(
            chunker,
            "_load_tree_sitter_parser",
            lambda _lang, root=root: FakeParser(root),
        )
        ast_chunks, fallback = chunker._chunk_file_ast(source, f"demo.{language}", language)
        assert fallback == "none"
        assert ast_chunks is not None
        assert len(ast_chunks) == 1
        assert ast_chunks[0].content.strip().startswith("def alpha")


def test_spec_004_002_hierarchical_scope_headers(monkeypatch: pytest.MonkeyPatch):
    """SPEC-004-002: Nested scopes include full path in context headers."""
    source = "class Foo:\n    def bar(self):\n        return 1\n"
    method = _mk_node(
        source,
        "function_definition",
        "def bar(self):\n        return 1\n",
        name="bar",
    )
    class_body = _mk_node(
        source,
        "class_body",
        "def bar(self):\n        return 1\n",
        children=[method],
    )
    klass = _mk_node(
        source,
        "class_definition",
        "class Foo:\n    def bar(self):\n        return 1\n",
        name="Foo",
        children=[class_body],
    )
    root = _mk_root(source, [klass])
    monkeypatch.setattr(chunker, "_load_tree_sitter_parser", lambda _lang: FakeParser(root))

    ast_chunks, fallback = chunker._chunk_file_ast(source, "demo.py", "python", max_chars=30)
    assert fallback == "none"
    assert ast_chunks is not None
    assert len(ast_chunks) == 1
    assert "class Foo > function bar" in ast_chunks[0].context_header


def test_spec_004_003_recursive_split_for_oversized_nodes(monkeypatch: pytest.MonkeyPatch):
    """SPEC-004-003: Oversized classes recurse to child scope chunks."""
    methods: list[FakeNode] = []
    method_text = []
    for i in range(10):
        method_src = f"    def method_{i}(self):\n        return {i}\n"
        method_text.append(method_src)
    source = "class Big:\n" + "".join(method_text)

    for i in range(10):
        methods.append(
            _mk_node(
                source,
                "function_definition",
                f"def method_{i}(self):\n        return {i}\n",
                name=f"method_{i}",
            )
        )
    class_body = _mk_node(source, "class_body", "".join(method_text), children=methods)
    klass = _mk_node(source, "class_definition", source, name="Big", children=[class_body])
    root = _mk_root(source, [klass])
    monkeypatch.setattr(chunker, "_load_tree_sitter_parser", lambda _lang: FakeParser(root))

    ast_chunks, fallback = chunker._chunk_file_ast(source, "big.py", "python", max_chars=60)
    assert fallback == "none"
    assert ast_chunks is not None
    assert len(ast_chunks) == 10
    assert all("function method_" in c.scope for c in ast_chunks)


def test_spec_004_004_unsupported_language_sliding_fallback():
    """SPEC-004-004: Unsupported languages use window fallback."""
    source = "\n".join(f"line {i}" for i in range(1, 9))
    chunks = chunker.chunk_file(source, "script.lua", max_lines=3, overlap_lines=1)
    assert chunks
    assert chunks[0].language == "unknown"
    expected = chunker._split_by_windows(source.split("\n"), "script.lua", "unknown", 3, 1)
    assert [c.content for c in chunks] == [c.content for c in expected]


def test_spec_004_005_parse_error_falls_back_to_regex(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
):
    """SPEC-004-005: Severe parse errors trigger regex fallback with warning."""
    source = "def bad(:\n  pass\n"
    good = _mk_node(source, "function_definition", "def bad(:\n  pass\n", name="bad")
    bad = _mk_node(source, "ERROR", "def bad(:\n  pass\n", has_error=True)
    root = _mk_root(source, [bad, good, bad, bad, bad])
    monkeypatch.setattr(chunker, "_load_tree_sitter_parser", lambda _lang: FakeParser(root))

    chunks = chunker.chunk_file(source, "broken.py")
    assert chunks
    assert "falling back to regex chunking" in caplog.text


def test_edge_004_001_syntax_error_logs_warning_and_falls_back(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
):
    source = "def fail(:\n    pass\n"
    err = _mk_node(source, "ERROR", "def fail(:\n    pass\n", has_error=True)
    root = _mk_root(source, [err, err, err, err, err])
    monkeypatch.setattr(chunker, "_load_tree_sitter_parser", lambda _lang: FakeParser(root))

    result = chunker.chunk_file(source, "fail.py")
    assert result
    assert "AST parse failed for fail.py" in caplog.text


def test_edge_004_002_mixed_language_html_uses_window_fallback():
    source = "<html>\n<script>const x = 1;</script>\n</html>\n"
    chunks = chunker.chunk_file(source, "index.html", max_lines=2, overlap_lines=0)
    assert len(chunks) >= 1
    assert chunks[0].language == "unknown"


def test_edge_004_003_nested_past_depth_stops_recursion(monkeypatch: pytest.MonkeyPatch):
    parts = []
    for i in range(7):
        parts.append(f"class L{i}:\n")
    source = "".join(parts) + "    pass\n"

    leaf = _mk_node(source, "class_definition", "class L6:\n    pass\n", name="L6")
    chain = leaf
    for i in reversed(range(6)):
        body = _mk_node(
            source,
            "class_body",
            f"class L{i+1}:\n",
            occurrence=1,
            children=[chain],
        )
        chain = _mk_node(
            source,
            "class_definition",
            f"class L{i}:\nclass L{i+1}:\n",
            name=f"L{i}",
            children=[body],
        )
    root = _mk_root(source, [chain])
    monkeypatch.setattr(chunker, "_load_tree_sitter_parser", lambda _lang: FakeParser(root))

    ast_chunks, fallback = chunker._chunk_file_ast(
        source,
        "deep.py",
        "python",
        max_chars=10,
        max_tree_depth=5,
    )
    assert fallback == "none"
    assert ast_chunks is not None
    assert len(ast_chunks) >= 1


def test_edge_004_004_empty_file_returns_no_chunks():
    assert chunker.chunk_file("", "empty.py") == []
    assert chunker.chunk_file("   \n", "empty.py") == []


def test_edge_004_005_single_massive_function_splits_by_statement_boundaries(
    monkeypatch: pytest.MonkeyPatch,
):
    source = (
        "def giant():\n"
        "    x = 1;\n"
        "    y = 2;\n"
        "    z = 3;\n"
        "    return x + y + z;\n"
    )
    func = _mk_node(source, "function_definition", source, name="giant")
    root = _mk_root(source, [func])
    monkeypatch.setattr(chunker, "_load_tree_sitter_parser", lambda _lang: FakeParser(root))

    ast_chunks, fallback = chunker._chunk_file_ast(source, "giant.py", "python", max_chars=24)
    assert fallback == "none"
    assert ast_chunks is not None
    assert len(ast_chunks) > 1
    for item in ast_chunks[:-1]:
        line = item.content.strip().splitlines()[-1]
        assert line.endswith(";") or line.endswith(":") or line.endswith("{") or line.endswith("}")


def test_edge_004_006_binary_file_like_content_is_skipped():
    source = "def x():\n\x00\x00\x00"
    assert chunker.chunk_file(source, "binary.py") == []


def test_spec_004_005_partially_valid_tree_keeps_ast_chunks(monkeypatch: pytest.MonkeyPatch):
    """SPEC-004-005: Minor parse errors keep valid AST chunks."""
    source = (
        "def ok_1():\n    return 1\n"
        "def ok_2():\n    return 2\n"
        "def ok_3():\n    return 3\n"
        "def ok_4():\n    return 4\n"
        "def ok_5():\n    return 5\n"
    )
    nodes = [
        _mk_node(source, "function_definition", f"def ok_{i}():\n    return {i}\n", name=f"ok_{i}")
        for i in range(1, 6)
    ]
    err = _mk_node(source, "ERROR", "def ok_1():\n    return 1\n", has_error=True)
    root = _mk_root(source, [*nodes, err])  # 1/6 errors -> below threshold.
    monkeypatch.setattr(chunker, "_load_tree_sitter_parser", lambda _lang: FakeParser(root))

    chunks = chunker.chunk_file(source, "partial.py")
    assert len(chunks) >= 5
    assert all("function ok_" in c.scope for c in chunks[:5])
