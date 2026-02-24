# Playbook: Development Setup

## Prerequisites

- Python 3.11+
- `uv` (recommended) or `pip`

## Setup

```bash
cd codesight
pip install -e ".[dev]"
# or with uv:
uv pip install -e ".[dev]"
```

## Run Locally

```bash
# Run the MCP server (STDIO mode)
python -m semantic_search_mcp

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python -m semantic_search_mcp

# Connect to Claude Code
claude mcp add codesight -- python -m semantic_search_mcp
```

## Tests

```bash
pytest tests/ -x -v
```

## Lint

```bash
ruff check src/ tests/
ruff format src/ tests/ --check  # dry run
```

## Environment Variables

See `.env.example` for all configuration options.
Set `SEMANTIC_SEARCH_DATA_DIR` to a non-default path during testing to avoid polluting your real indexes.

## Directory Layout

See `ARCHITECTURE.md` for the full source layout.
See `.claude/rules/structure.md` for where new files should go.
