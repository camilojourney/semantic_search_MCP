"""Public Python API for CodeSight.

This is the single entry point for Streamlit, Slack, CLI, and any future interface.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from .config import ServerConfig
from .embeddings import get_embedder
from .indexer import index_repo
from .search import hybrid_search
from .store import ChunkStore
from .types import Answer, IndexStats, RepoStatus, SearchResult

logger = logging.getLogger(__name__)


class CodeSight:
    """AI-powered document search engine.

    Usage:
        engine = CodeSight("/path/to/documents")
        engine.index()
        results = engine.search("payment terms")
        answer = engine.ask("What are the payment terms in the contract?")
    """

    def __init__(
        self,
        folder_path: str | Path,
        config: ServerConfig | None = None,
    ) -> None:
        self.folder_path = Path(folder_path).expanduser().resolve()
        if not self.folder_path.is_dir():
            raise ValueError(f"Not a directory: {self.folder_path}")

        self.config = config or ServerConfig()
        self._store: ChunkStore | None = None
        self._embedder = None

    @property
    def store(self) -> ChunkStore:
        if self._store is None:
            self._store = ChunkStore(self.folder_path, embedding_dim=self.config.embedding_dim)
        return self._store

    @property
    def embedder(self):
        if self._embedder is None:
            self._embedder = get_embedder(self.config.embedding_model, self.config.embedding_dim)
        return self._embedder

    def index(self, force_rebuild: bool = False) -> IndexStats:
        """Index all documents in the folder.

        Handles code files, text files, PDFs, DOCX, and PPTX.
        Unchanged files are skipped (content hash dedup).
        """
        stats = index_repo(self.folder_path, self.config, force_rebuild=force_rebuild)
        # Reset store to pick up new data
        self._store = None
        return stats

    def search(
        self, query: str, top_k: int = 8, file_glob: str | None = None,
    ) -> list[SearchResult]:
        """Hybrid BM25 + vector search. Auto-indexes if needed."""
        self._ensure_indexed()
        return hybrid_search(
            self.store, self.embedder, query,
            top_k=top_k, file_glob=file_glob,
        )

    def ask(self, question: str, top_k: int = 5, file_glob: str | None = None) -> Answer:
        """Ask a question — search + Claude API answer synthesis.

        Retrieves the top matching chunks, sends them as context to Claude,
        and returns a natural language answer with source citations.

        Requires ANTHROPIC_API_KEY environment variable.
        """
        results = self.search(question, top_k=top_k, file_glob=file_glob)

        if not results:
            return Answer(
                text="No relevant documents found. Try indexing first.",
                sources=[],
                model=self.config.llm_model,
            )

        # Build context from search results
        context_parts = []
        for i, r in enumerate(results, 1):
            context_parts.append(
                f"[Source {i}: {r.file_path}, {r.scope}]\n{r.snippet}"
            )
        context = "\n\n---\n\n".join(context_parts)

        # Call Claude API
        answer_text = _call_claude(
            question=question,
            context=context,
            model=self.config.llm_model,
        )

        return Answer(
            text=answer_text,
            sources=results,
            model=self.config.llm_model,
        )

    def status(self) -> RepoStatus:
        """Check index status for this folder."""
        return RepoStatus(
            repo_path=str(self.folder_path),
            indexed=self.store.is_indexed,
            chunk_count=self.store.chunk_count,
            files_indexed=self.store.file_count,
            last_commit=self.store.last_commit,
            last_indexed_at=self.store.last_indexed_at,
            stale=self._is_stale() if self.store.is_indexed else False,
        )

    def _ensure_indexed(self) -> None:
        """Auto-index if not indexed, auto-refresh if stale."""
        if not self.store.is_indexed:
            logger.info("No index found for %s — building now...", self.folder_path)
            self.index()
        elif self._is_stale():
            logger.info("Index is stale for %s — refreshing...", self.folder_path)
            self.index()

    def _is_stale(self) -> bool:
        """Check if the index is older than the staleness threshold."""
        ts = self.store.last_indexed_at
        if not ts:
            return True
        try:
            indexed_at = datetime.fromisoformat(ts)
            age = (datetime.now(timezone.utc) - indexed_at).total_seconds()
            return age > self.config.stale_threshold_seconds
        except Exception:
            return True


def _call_claude(question: str, context: str, model: str) -> str:
    """Send question + context to Claude API and return the answer text."""
    import anthropic

    client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY env var

    system_prompt = (
        "You are a helpful document assistant. Answer questions based ONLY on the "
        "provided source documents. If the answer is not in the sources, say so. "
        "Always cite which source(s) your answer comes from using [Source N] notation."
    )

    user_message = (
        f"Based on the following documents, answer this question:\n\n"
        f"**Question:** {question}\n\n"
        f"**Documents:**\n\n{context}"
    )

    message = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    return message.content[0].text
