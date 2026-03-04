"""SQLite database helpers for workspace multi-tenancy."""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1
CORRUPTED_DB_MESSAGE = (
    "workspaces.db appears corrupted. Run 'codesight workspace repair' or restore from backup."
)


class WorkspaceDB:
    """Workspace metadata DB manager with bootstrap and transactional helpers."""

    # // SPEC-013-001: Auto-create ~/.codesight/workspaces.db on first use.
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path or Path.home() / ".codesight" / "workspaces.db").expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._bootstrap()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Yield a connection configured for row access and foreign key checks."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        except sqlite3.DatabaseError as exc:
            raise self._translate_db_error(exc) from exc
        finally:
            conn.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Yield a connection inside BEGIN/COMMIT with automatic rollback."""
        with self.connection() as conn:
            try:
                conn.execute("BEGIN")
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    def _bootstrap(self) -> None:
        # // SPEC-013-001: Run integrity_check before migrations/bootstrap.
        try:
            with self.connection() as conn:
                integrity = conn.execute("PRAGMA integrity_check").fetchone()
                if integrity is None or integrity[0] != "ok":
                    raise RuntimeError(CORRUPTED_DB_MESSAGE)

                # // SPEC-013-001: All DDL is executed in one transaction.
                ddl_statements = [
                    """
                    CREATE TABLE IF NOT EXISTS workspaces (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                        description TEXT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        last_synced_at TEXT NULL,
                        sync_status TEXT NOT NULL
                            CHECK(sync_status IN ('never', 'syncing', 'ok', 'error'))
                    )
                    """,
                    """
                    CREATE INDEX IF NOT EXISTS idx_workspaces_name_nocase
                        ON workspaces(name COLLATE NOCASE)
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS data_sources (
                        id TEXT PRIMARY KEY,
                        workspace_id TEXT NOT NULL,
                        source_type TEXT NOT NULL,
                        source_config TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
                    )
                    """,
                    """
                    CREATE INDEX IF NOT EXISTS idx_data_sources_workspace
                        ON data_sources(workspace_id)
                    """,
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_data_sources_unique
                        ON data_sources(workspace_id, source_type, source_config)
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS workspace_access (
                        id TEXT PRIMARY KEY,
                        workspace_id TEXT NOT NULL,
                        email TEXT NOT NULL,
                        granted_at TEXT NOT NULL,
                        FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
                    )
                    """,
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_workspace_access_lookup
                        ON workspace_access(workspace_id, email)
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS sync_runs (
                        id TEXT PRIMARY KEY,
                        workspace_id TEXT NOT NULL,
                        started_at TEXT NOT NULL,
                        completed_at TEXT NULL,
                        status TEXT NOT NULL CHECK(status IN ('running', 'ok', 'error')),
                        files_added INTEGER NOT NULL DEFAULT 0,
                        files_updated INTEGER NOT NULL DEFAULT 0,
                        files_deleted INTEGER NOT NULL DEFAULT 0,
                        error_message TEXT NULL,
                        FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
                    )
                    """,
                    """
                    CREATE INDEX IF NOT EXISTS idx_sync_runs_workspace_started
                        ON sync_runs(workspace_id, started_at DESC)
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS schema_version (
                        version INTEGER NOT NULL,
                        applied_at TEXT NOT NULL
                    )
                    """,
                ]

                conn.execute("BEGIN")
                try:
                    for statement in ddl_statements:
                        conn.execute(statement)
                    conn.execute(
                        """
                        INSERT INTO schema_version(version, applied_at)
                        SELECT ?, ?
                        WHERE NOT EXISTS (SELECT 1 FROM schema_version)
                        """,
                        (SCHEMA_VERSION, self._utc_now()),
                    )
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise
        except sqlite3.DatabaseError as exc:
            raise self._translate_db_error(exc) from exc

    def _translate_db_error(self, exc: sqlite3.DatabaseError) -> Exception:
        message = str(exc).lower()
        corruption_signals = (
            "malformed",
            "not a database",
            "file is encrypted",
            "database disk image is malformed",
        )
        if any(signal in message for signal in corruption_signals):
            # // EDGE-013-006: Corrupted DB fails deterministically with repair guidance.
            return RuntimeError(CORRUPTED_DB_MESSAGE)
        return exc

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()
