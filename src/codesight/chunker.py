"""Language-aware code chunking + document chunking.

Code: regex-based splitting on top-level function/class boundaries.
Documents: paragraph-aware splitting with page metadata.
Both get context headers prepended to improve embedding quality.
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config import (
    DEFAULT_CHUNK_MAX_LINES,
    DEFAULT_CHUNK_OVERLAP_LINES,
    DEFAULT_DOC_CHUNK_MAX_CHARS,
    DEFAULT_DOC_CHUNK_OVERLAP_CHARS,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Language-specific boundary patterns
# ---------------------------------------------------------------------------

# Each pattern matches the START of a new top-level scope
_BOUNDARY_PATTERNS: dict[str, re.Pattern] = {
    "python": re.compile(r"^(class |def |async def )", re.MULTILINE),
    "javascript": re.compile(
        r"^(export\s+)?(function |class |const \w+ = |let \w+ = |var \w+ = )", re.MULTILINE
    ),
    "typescript": re.compile(
        r"^(export\s+)?(function |class |const \w+ = |let \w+ = |interface |type |enum )",
        re.MULTILINE,
    ),
    "go": re.compile(r"^(func |type )", re.MULTILINE),
    "rust": re.compile(r"^(pub\s+)?(fn |struct |enum |impl |trait |mod )", re.MULTILINE),
    "java": re.compile(
        r"^(public |private |protected )?(static )?(class |interface |enum |void |int |String )",
        re.MULTILINE,
    ),
    "ruby": re.compile(r"^(class |module |def )", re.MULTILINE),
    "php": re.compile(r"^(class |function |public |private |protected )", re.MULTILINE),
    "c": re.compile(r"^(\w+\s+\*?\w+\s*\()", re.MULTILINE),
    "cpp": re.compile(
        r"^(class |struct |namespace |template |(\w+\s+\*?\w+\s*\())", re.MULTILINE
    ),
}

# Map file extension to language key
_EXT_TO_LANG: dict[str, str] = {
    ".py": "python",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript",
    ".ts": "typescript", ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java", ".kt": "java", ".scala": "java",
    ".rb": "ruby", ".rake": "ruby",
    ".php": "php",
    ".c": "c", ".h": "c",
    ".cpp": "cpp", ".hpp": "cpp", ".cc": "cpp", ".cxx": "cpp",
    ".cs": "java",  # close enough for boundary detection
}

# ---------------------------------------------------------------------------
# AST chunking config
# ---------------------------------------------------------------------------

AST_MAX_CHARS = 1500
AST_MIN_CHARS = 100
AST_MAX_TREE_DEPTH = 5
AST_PARSE_ERROR_THRESHOLD = 0.20

_AST_SCOPE_NODE_TYPES: dict[str, set[str]] = {
    "python": {"function_definition", "class_definition"},
    "javascript": {"function_declaration", "class_declaration", "arrow_function"},
    "typescript": {
        "function_declaration",
        "class_declaration",
        "interface_declaration",
        "arrow_function",
    },
    "go": {"function_declaration", "method_declaration", "type_declaration"},
    "rust": {"function_item", "impl_item", "struct_item", "enum_item"},
    "java": {"method_declaration", "class_declaration", "interface_declaration"},
    "ruby": {"method", "class", "module"},
    "php": {"function_definition", "class_declaration", "method_declaration"},
    "c": {"function_definition", "struct_specifier"},
    "cpp": {"function_definition", "class_specifier", "namespace_definition"},
}

_AST_CONTAINER_NODE_TYPES = {
    "program",
    "module",
    "block",
    "body",
    "class_body",
    "declaration_list",
    "source_file",
    "translation_unit",
    "impl_item_list",
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class Chunk:
    """A single chunk of content with metadata."""

    file_path: str  # relative to folder root
    start_line: int  # 1-indexed (line number for code, page number for docs)
    end_line: int  # 1-indexed, inclusive
    content: str  # raw text
    scope: str  # e.g. "function validate_token" or "page 3" or "section Introduction"
    language: str  # e.g. "python", "pdf", "docx"
    context_header: str  # prepended before embedding
    content_hash: str = field(init=False)

    def __post_init__(self):
        self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]

    @property
    def embedding_text(self) -> str:
        """Text sent to the embedding model (context header + content)."""
        return f"{self.context_header}\n{self.content}"

    @property
    def chunk_id(self) -> str:
        """Unique ID: file + line range + hash."""
        return f"{self.file_path}:{self.start_line}-{self.end_line}:{self.content_hash}"


# ---------------------------------------------------------------------------
# Scope detection helpers
# ---------------------------------------------------------------------------


def _detect_scope(first_line: str, language: str) -> str:
    """Extract a human-readable scope label from the first line of a chunk."""
    first_line = first_line.strip()
    if not first_line:
        return "module-level"

    # Python: "def foo(...)" -> "function foo"
    if language == "python":
        m = re.match(r"(async\s+)?def\s+(\w+)", first_line)
        if m:
            return f"function {m.group(2)}"
        m = re.match(r"class\s+(\w+)", first_line)
        if m:
            return f"class {m.group(1)}"

    # JS/TS
    if language in ("javascript", "typescript"):
        m = re.match(r"(?:export\s+)?function\s+(\w+)", first_line)
        if m:
            return f"function {m.group(1)}"
        m = re.match(r"(?:export\s+)?class\s+(\w+)", first_line)
        if m:
            return f"class {m.group(1)}"
        m = re.match(r"(?:export\s+)?(?:const|let|var)\s+(\w+)", first_line)
        if m:
            return f"const {m.group(1)}"

    # Go
    if language == "go":
        m = re.match(r"func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)", first_line)
        if m:
            return f"function {m.group(1)}"
        m = re.match(r"type\s+(\w+)", first_line)
        if m:
            return f"type {m.group(1)}"

    # Rust
    if language == "rust":
        m = re.match(r"(?:pub\s+)?fn\s+(\w+)", first_line)
        if m:
            return f"function {m.group(1)}"
        m = re.match(r"(?:pub\s+)?struct\s+(\w+)", first_line)
        if m:
            return f"struct {m.group(1)}"
        m = re.match(r"(?:pub\s+)?impl\s+(\w+)", first_line)
        if m:
            return f"impl {m.group(1)}"

    # Fallback: use the first significant token
    tokens = first_line.split()
    if tokens:
        return tokens[0]
    return "unknown"


def _make_context_header(file_path: str, scope: str, start_line: int, end_line: int) -> str:
    """Build the context header prepended to chunks before embedding."""
    return f"# File: {file_path}\n# Scope: {scope}\n# Lines: {start_line}-{end_line}"


# ---------------------------------------------------------------------------
# AST chunking helpers
# ---------------------------------------------------------------------------


def _load_tree_sitter_parser(language: str) -> Any | None:
    """Lazy-load a tree-sitter parser for a language from the bundled grammars."""
    try:
        from tree_sitter_languages import get_parser
    except Exception:
        return None

    try:
        return get_parser(language)
    except Exception:
        return None


def _node_text(source: bytes, node: Any) -> str:
    return source[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")


def _first_identifier(node: Any) -> Any | None:
    for child in getattr(node, "children", []):
        if getattr(child, "type", "") in {"identifier", "name", "constant", "type_identifier"}:
            return child
    return None


def _node_name_text(source: bytes, node: Any) -> str | None:
    name_node = None
    if hasattr(node, "child_by_field_name"):
        name_node = node.child_by_field_name("name")
    if name_node is None:
        name_node = _first_identifier(node)
    if name_node is None and getattr(node, "type", "") == "arrow_function":
        parent = getattr(node, "parent", None)
        if parent is not None and hasattr(parent, "child_by_field_name"):
            name_node = parent.child_by_field_name("name")
        if name_node is None and parent is not None:
            name_node = _first_identifier(parent)
    if name_node is None:
        return None
    name = _node_text(source, name_node).strip()
    return name or None


def _scope_prefix(node_type: str) -> str:
    if node_type in {
        "function_definition",
        "function_declaration",
        "method_declaration",
        "function_item",
        "method",
        "method_definition",
        "arrow_function",
    }:
        return "function"
    if node_type in {"class_definition", "class_declaration", "class_specifier", "class"}:
        return "class"
    if node_type in {"interface_declaration"}:
        return "interface"
    if node_type in {"module", "namespace_definition"}:
        return "module"
    if node_type in {"struct_item", "struct_specifier"}:
        return "struct"
    if node_type in {"enum_item"}:
        return "enum"
    if node_type in {"impl_item"}:
        return "impl"
    if node_type in {"type_declaration"}:
        return "type"
    return node_type.replace("_", " ")


def _scope_label(source: bytes, node: Any) -> str:
    node_type = getattr(node, "type", "")
    prefix = _scope_prefix(node_type)
    name = _node_name_text(source, node)
    if name:
        return f"{prefix} {name}"
    return prefix


def _is_error_node(node: Any) -> bool:
    return getattr(node, "type", "") == "ERROR" or bool(getattr(node, "has_error", False))


def _count_top_level_errors(root_node: Any) -> tuple[int, int]:
    top_level = [n for n in getattr(root_node, "children", []) if getattr(n, "is_named", False)]
    if not top_level:
        return 0, 0
    error_count = sum(1 for n in top_level if _is_error_node(n))
    return error_count, len(top_level)


def _direct_scope_children(node: Any, language: str) -> list[Any]:
    """Find direct child scopes while traversing through syntax container nodes."""
    scope_types = _AST_SCOPE_NODE_TYPES.get(language, set())
    if not scope_types:
        return []

    found: list[Any] = []
    queue = list(getattr(node, "children", []))
    while queue:
        current = queue.pop(0)
        if not getattr(current, "is_named", False):
            continue
        if _is_error_node(current):
            continue
        if current.type in scope_types:
            found.append(current)
            continue
        if current.type in _AST_CONTAINER_NODE_TYPES or current.type.endswith("_body"):
            queue.extend(list(getattr(current, "children", [])))
    return found


def _split_leaf_by_statement_boundaries(
    source_text: str,
    max_chars: int,
) -> list[tuple[int, int, str]]:
    """Split a large scope by statement-ish boundaries instead of raw offsets."""
    lines = source_text.splitlines()
    if not lines:
        return []

    segments: list[tuple[int, int, str]] = []
    start = 0
    buf: list[str] = []
    char_count = 0
    for idx, line in enumerate(lines):
        buf.append(line)
        char_count += len(line) + 1
        boundary = (
            not line.strip()
            or line.rstrip().endswith(";")
            or line.rstrip().endswith("{")
            or line.rstrip().endswith("}")
            or line.rstrip().endswith(":")
        )
        if boundary and char_count >= max_chars:
            segments.append((start, idx, "\n".join(buf).strip("\n")))
            start = idx + 1
            buf = []
            char_count = 0

    if buf:
        segments.append((start, len(lines) - 1, "\n".join(buf).strip("\n")))
    return [(s, e, text) for s, e, text in segments if text.strip()]


def _emit_chunk(
    *,
    chunks: list[Chunk],
    file_path: str,
    scope_path: list[str],
    start_line: int,
    end_line: int,
    content: str,
    language: str,
) -> None:
    # SPEC-004-002: Embed full hierarchical scope path in context headers.
    scope = " > ".join(scope_path) if scope_path else "module"
    header = _make_context_header(file_path, scope, start_line, end_line)
    chunks.append(
        Chunk(
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            content=content,
            scope=scope,
            language=language,
            context_header=header,
        )
    )


def _collect_ast_chunks(
    *,
    node: Any,
    source: bytes,
    file_path: str,
    language: str,
    scope_path: list[str],
    max_chars: int,
    min_chars: int,
    depth: int,
    max_tree_depth: int,
    chunks: list[Chunk],
) -> None:
    node_content = _node_text(source, node)
    if not node_content.strip():
        return

    start_line = getattr(node, "start_point")[0] + 1
    end_line = getattr(node, "end_point")[0] + 1

    # SPEC-004-003: Oversized AST scopes recurse into child scopes first.
    if len(node_content) > max_chars:
        # EDGE-004-003: Stop recursion at bounded max_tree_depth.
        if depth >= max_tree_depth:
            _emit_chunk(
                chunks=chunks,
                file_path=file_path,
                scope_path=scope_path,
                start_line=start_line,
                end_line=end_line,
                content=node_content,
                language=language,
            )
            return

        child_scopes = _direct_scope_children(node, language)
        if child_scopes:
            for child in sorted(child_scopes, key=lambda n: n.start_byte):
                child_label = _scope_label(source, child)
                _collect_ast_chunks(
                    node=child,
                    source=source,
                    file_path=file_path,
                    language=language,
                    scope_path=[*scope_path, child_label],
                    max_chars=max_chars,
                    min_chars=min_chars,
                    depth=depth + 1,
                    max_tree_depth=max_tree_depth,
                    chunks=chunks,
                )
            return

        # EDGE-004-005: Leaf oversized scopes split by statement boundaries.
        leaf_segments = _split_leaf_by_statement_boundaries(node_content, max_chars=max_chars)
        if leaf_segments:
            for start_offset, end_offset, segment in leaf_segments:
                segment_start = start_line + start_offset
                segment_end = start_line + end_offset
                _emit_chunk(
                    chunks=chunks,
                    file_path=file_path,
                    scope_path=scope_path,
                    start_line=segment_start,
                    end_line=segment_end,
                    content=segment,
                    language=language,
                )
            return

    _emit_chunk(
        chunks=chunks,
        file_path=file_path,
        scope_path=scope_path,
        start_line=start_line,
        end_line=end_line,
        content=node_content,
        language=language,
    )


def _chunk_file_ast(
    content: str,
    file_path: str,
    language: str,
    max_chars: int = AST_MAX_CHARS,
    min_chars: int = AST_MIN_CHARS,
    max_tree_depth: int = AST_MAX_TREE_DEPTH,
) -> tuple[list[Chunk] | None, str]:
    """Try AST chunking; return (chunks, fallback_mode) where mode is 'none'/'regex'/'sliding'."""
    source = content.encode("utf-8", errors="ignore")
    parser = _load_tree_sitter_parser(language)
    if parser is None:
        logger.debug(
            "No tree-sitter parser for %s; using sliding fallback for %s",
            language,
            file_path,
        )
        return None, "sliding"

    try:
        tree = parser.parse(source)
    except Exception:
        logger.warning(
            "AST parse failed for %s: parser exception - falling back to regex chunking",
            file_path,
        )
        return None, "regex"

    root_node = getattr(tree, "root_node", None)
    if root_node is None:
        return None, "regex"

    error_count, top_count = _count_top_level_errors(root_node)
    if top_count > 0 and (error_count / top_count) > AST_PARSE_ERROR_THRESHOLD:
        # SPEC-004-005
        # EDGE-004-001: Severe syntax errors trigger regex fallback with warning.
        logger.warning(
            "AST parse failed for %s: %d ERROR nodes - falling back to regex chunking",
            file_path,
            error_count,
        )
        return None, "regex"

    scope_nodes = _direct_scope_children(root_node, language)
    if not scope_nodes:
        return None, "regex"

    chunks: list[Chunk] = []
    for node in sorted(scope_nodes, key=lambda n: n.start_byte):
        if _is_error_node(node):
            continue
        label = _scope_label(source, node)
        _collect_ast_chunks(
            node=node,
            source=source,
            file_path=file_path,
            language=language,
            scope_path=[label],
            max_chars=max_chars,
            min_chars=min_chars,
            depth=0,
            max_tree_depth=max_tree_depth,
            chunks=chunks,
        )

    if chunks:
        return chunks, "none"
    return None, "regex"


# ---------------------------------------------------------------------------
# Code chunking
# ---------------------------------------------------------------------------


def _detect_language(file_path: str) -> str:
    """Detect language from file extension."""
    ext = Path(file_path).suffix.lower()
    return _EXT_TO_LANG.get(ext, "unknown")


def chunk_file(
    content: str,
    file_path: str,
    max_lines: int = DEFAULT_CHUNK_MAX_LINES,
    overlap_lines: int = DEFAULT_CHUNK_OVERLAP_LINES,
) -> list[Chunk]:
    """Split source into chunks, preferring AST chunking for supported code languages."""
    # EDGE-004-004: Empty/whitespace-only files never emit chunks.
    if not content.strip():
        return []

    language = _detect_language(file_path)

    # EDGE-004-006: Binary-ish text misidentified as code is skipped.
    if "\x00" in content:
        logger.debug("Skipping binary-like file content for %s", file_path)
        return []

    # SPEC-004-001: Route supported code languages through AST chunking.
    if language in _AST_SCOPE_NODE_TYPES:
        ast_chunks, fallback_mode = _chunk_file_ast(content, file_path, language)
        if ast_chunks is not None:
            return ast_chunks
        if fallback_mode == "regex":
            return _chunk_file_regex(
                content,
                file_path=file_path,
                max_lines=max_lines,
                overlap_lines=overlap_lines,
            )
        if fallback_mode == "sliding":
            lines = content.split("\n")
            return _split_by_windows(lines, file_path, language, max_lines, overlap_lines)

    # SPEC-004-004: Unsupported languages use the existing window fallback.
    # EDGE-004-002: Mixed-language HTML/script files are treated as plain text windows.
    return _chunk_file_regex(
        content,
        file_path=file_path,
        max_lines=max_lines,
        overlap_lines=overlap_lines,
    )


def _chunk_file_regex(
    content: str,
    *,
    file_path: str,
    max_lines: int,
    overlap_lines: int,
) -> list[Chunk]:
    lines = content.split("\n")
    language = _detect_language(file_path)
    pattern = _BOUNDARY_PATTERNS.get(language)
    if pattern:
        return _split_by_boundaries(lines, file_path, language, pattern, max_lines, overlap_lines)
    return _split_by_windows(lines, file_path, language, max_lines, overlap_lines)


def _split_by_boundaries(
    lines: list[str],
    file_path: str,
    language: str,
    pattern: re.Pattern,
    max_lines: int,
    overlap_lines: int,
) -> list[Chunk]:
    """Split on regex-detected scope boundaries."""
    # Find all boundary line indices
    boundary_indices = [0]  # always start at line 0
    for i, line in enumerate(lines):
        if i == 0:
            continue
        if pattern.match(line):
            boundary_indices.append(i)

    chunks: list[Chunk] = []
    for idx, start in enumerate(boundary_indices):
        end = boundary_indices[idx + 1] if idx + 1 < len(boundary_indices) else len(lines)
        segment_lines = lines[start:end]

        if len(segment_lines) <= max_lines:
            scope = _detect_scope(segment_lines[0] if segment_lines else "", language)
            header = _make_context_header(file_path, scope, start + 1, end)
            chunk_content = "\n".join(segment_lines)
            chunks.append(Chunk(
                file_path=file_path,
                start_line=start + 1,
                end_line=end,
                content=chunk_content,
                scope=scope,
                language=language,
                context_header=header,
            ))
        else:
            # Sub-split large scopes with overlapping windows
            sub_chunks = _split_by_windows(
                segment_lines, file_path, language, max_lines, overlap_lines,
                line_offset=start,
            )
            chunks.extend(sub_chunks)

    return chunks


def _split_by_windows(
    lines: list[str],
    file_path: str,
    language: str,
    max_lines: int,
    overlap_lines: int,
    line_offset: int = 0,
) -> list[Chunk]:
    """Fall back to fixed-size overlapping windows."""
    chunks: list[Chunk] = []
    i = 0
    while i < len(lines):
        end = min(i + max_lines, len(lines))
        segment = lines[i:end]
        scope = _detect_scope(segment[0] if segment else "", language)
        start_line = line_offset + i + 1
        end_line = line_offset + end
        header = _make_context_header(file_path, scope, start_line, end_line)
        chunks.append(Chunk(
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            content="\n".join(segment),
            scope=scope,
            language=language,
            context_header=header,
        ))
        i += max_lines - overlap_lines
        if i >= len(lines):
            break

    return chunks


# ---------------------------------------------------------------------------
# Document chunking (new)
# ---------------------------------------------------------------------------


def chunk_document(
    pages: list,  # list[DocumentPage] - import avoided for circular deps
    file_path: str,
    max_chars: int = DEFAULT_DOC_CHUNK_MAX_CHARS,
    overlap_chars: int = DEFAULT_DOC_CHUNK_OVERLAP_CHARS,
) -> list[Chunk]:
    """Split document pages into chunks by paragraph boundaries.

    Each page's text is split into paragraph-sized chunks. The page number
    is used for start_line/end_line, and heading (if any) for scope.
    """
    ext = Path(file_path).suffix.lower().lstrip(".")
    language = ext  # "pdf", "docx", "pptx"

    chunks: list[Chunk] = []

    for page in pages:
        if not page.text.strip():
            continue

        scope = page.heading or f"page {page.page_number}"
        page_chunks = _split_text_by_paragraphs(
            text=page.text,
            file_path=file_path,
            page_number=page.page_number,
            scope=scope,
            language=language,
            max_chars=max_chars,
            overlap_chars=overlap_chars,
        )
        chunks.extend(page_chunks)

    return chunks


def _split_text_by_paragraphs(
    text: str,
    file_path: str,
    page_number: int,
    scope: str,
    language: str,
    max_chars: int,
    overlap_chars: int,
) -> list[Chunk]:
    """Split text into chunks respecting paragraph boundaries."""
    # Split on double newlines (paragraph breaks)
    paragraphs = re.split(r"\n\s*\n", text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    if not paragraphs:
        return []

    chunks: list[Chunk] = []
    current_text = ""
    chunk_idx = 0

    for para in paragraphs:
        # If adding this paragraph exceeds max_chars, flush current chunk
        if current_text and len(current_text) + len(para) + 2 > max_chars:
            chunk_idx += 1
            header = _make_context_header(
                file_path, scope, page_number, page_number,
            )
            chunks.append(Chunk(
                file_path=file_path,
                start_line=page_number,
                end_line=page_number,
                content=current_text,
                scope=scope,
                language=language,
                context_header=header,
            ))
            # Keep overlap from the end of current chunk
            if overlap_chars > 0 and len(current_text) > overlap_chars:
                current_text = current_text[-overlap_chars:]
            else:
                current_text = ""

        if current_text:
            current_text += "\n\n" + para
        else:
            current_text = para

    # Flush remaining text
    if current_text.strip():
        header = _make_context_header(file_path, scope, page_number, page_number)
        chunks.append(Chunk(
            file_path=file_path,
            start_line=page_number,
            end_line=page_number,
            content=current_text,
            scope=scope,
            language=language,
            context_header=header,
        ))

    return chunks
