"""CodeSight — AI-powered document search engine.

Hybrid BM25 + vector retrieval with Claude answer synthesis.
"""

from .api import CodeSight
from .types import Answer, IndexStats, RepoStatus, SearchResult

__all__ = ["CodeSight", "Answer", "IndexStats", "RepoStatus", "SearchResult"]
