"""SQLite persistence layer for Bridge Engine.

This is a lightweight step toward real SQL integration. It uses only Python's
standard library so the current app can adopt it without new dependencies.
Future Postgres/Supabase support can keep the same method names.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class BridgeSqlStore:
    def __init__(self, db_path: str = "data/bridge_engine.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ensure_schema()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def ensure_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS workspaces (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    task TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    frame TEXT DEFAULT 'gaming',
                    supports_json TEXT DEFAULT '[]',
                    status TEXT DEFAULT 'active',
                    current_step_index INTEGER DEFAULT 0,
                    artifact_json TEXT DEFAULT '{}',
                    raw_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS workspace_steps (
                    id TEXT PRIMARY KEY,
                    workspace_id TEXT NOT NULL,
                    step_index INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    why TEXT DEFAULT '',
                    action TEXT DEFAULT '',
                    output_slot TEXT DEFAULT '',
                    status TEXT DEFAULT 'pending',
                    user_output TEXT DEFAULT '',
                    help_variants_json TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS workspace_events (
                    id TEXT PRIMARY KEY,
                    workspace_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    payload_json TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS user_profile (
                    id TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_workspaces_updated_at ON workspaces(updated_at DESC);
                CREATE INDEX IF NOT EXISTS idx_steps_workspace ON workspace_steps(workspace_id, step_index);
                CREATE INDEX IF NOT EXISTS idx_events_workspace ON workspace_events(workspace_id, created_at DESC);
                """
            )

    def save_workspace(self, workspace: Dict[str, Any]) -> str:
        now = datetime.utcnow().isoformat()
        workspace_id = workspace["id"]
        title = workspace.get("title") or workspace.get("task") or "Untitled Bridge"
        steps = workspace.get("steps", [])
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO workspaces (
                    id, title, task, category, frame, supports_json, status,
                    current_step_index, artifact_json, raw_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    task=excluded.task,
                    category=excluded.category,
                    frame=excluded.frame,
                    supports_json=excluded.supports_json,
                    status=excluded.status,
                    current_step_index=excluded.current_step_index,
                    artifact_json=excluded.artifact_json,
                    raw_json=excluded.raw_json,
                    updated_at=excluded.updated_at
                """,
                (
                    workspace_id,
                    title,
                    workspace.get("task", ""),
                    workspace.get("category", "general"),
                    workspace.get("frame", "gaming"),
                    json.dumps(workspace.get("supports", [])),
                    workspace.get("status", "active"),
                    int(workspace.get("current_step_index", 0)),
                    json.dumps(workspace.get("artifact", {})),
                    json.dumps(workspace),
                    workspace.get("created_at", now),
                    now,
                ),
            )
            conn.execute("DELETE FROM workspace_steps WHERE workspace_id = ?", (workspace_id,))
            for idx, step in enumerate(steps):
                conn.execute(
                    """
                    INSERT INTO workspace_steps (
                        id, workspace_id, step_index, title, prompt, why, action,
                        output_slot, status, user_output, help_variants_json,
                        created_at, completed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        step.get("id", f"s{idx + 1}"),
                        workspace_id,
                        idx,
                        step.get("title", "Untitled step"),
                        step.get("prompt", step.get("checkpoint", "")),
                        step.get("why", ""),
                        step.get("action", ""),
                        step.get("output_slot", ""),
                        step.get("status", "pending"),
                        step.get("user_output", step.get("answer", "")),
                        json.dumps(step.get("help_variants", {})),
                        step.get("created_at", now),
                        step.get("completed_at"),
                    ),
                )
            for event in workspace.get("events", []):
                conn.execute(
                    """
                    INSERT OR IGNORE INTO workspace_events (id, workspace_id, kind, payload_json, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        event.get("id"),
                        workspace_id,
                        event.get("kind", "event"),
                        json.dumps(event.get("payload", {})),
                        event.get("created_at", now),
                    ),
                )
        return workspace_id

    def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute("SELECT raw_json FROM workspaces WHERE id = ?", (workspace_id,)).fetchone()
        if not row:
            return None
        return json.loads(row["raw_json"])

    def list_workspaces(self, limit: int = 25) -> List[Dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT id, title, task, frame, status, current_step_index, updated_at, raw_json FROM workspaces ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) | {"raw": json.loads(row["raw_json"])} for row in rows]

    def save_profile(self, profile: Dict[str, Any], profile_id: str = "default") -> None:
        now = datetime.utcnow().isoformat()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO user_profile (id, payload_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET payload_json=excluded.payload_json, updated_at=excluded.updated_at
                """,
                (profile_id, json.dumps(profile), now),
            )

    def get_profile(self, profile_id: str = "default") -> Optional[Dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute("SELECT payload_json FROM user_profile WHERE id = ?", (profile_id,)).fetchone()
        return json.loads(row["payload_json"]) if row else None
