"""
SQLite Event Logger for Bridge Engine

Creates a local SQLite foundation for real events before moving to Postgres.
Keeps synthetic data separate from real app events.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "bridge_engine.db"
DATA_DIR.mkdir(exist_ok=True)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def connect():
    return sqlite3.connect(DB_PATH)


def init_db():
    with connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'local_default',
            event_type TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'app',
            timestamp TEXT NOT NULL,
            payload_json TEXT NOT NULL DEFAULT '{}',
            synthetic INTEGER NOT NULL DEFAULT 0
        )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_user_time ON events(user_id, timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")


def log_event(event_type, payload=None, user_id="local_default", source="app", synthetic=False):
    init_db()
    payload = payload or {}
    with connect() as conn:
        conn.execute(
            "INSERT INTO events (user_id, event_type, source, timestamp, payload_json, synthetic) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, event_type, source, now_iso(), json.dumps(payload), 1 if synthetic else 0),
        )


def latest_events(limit=50):
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, user_id, event_type, source, timestamp, payload_json, synthetic FROM events ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [
        {
            "id": r[0],
            "user_id": r[1],
            "event_type": r[2],
            "source": r[3],
            "timestamp": r[4],
            "payload": json.loads(r[5] or "{}"),
            "synthetic": bool(r[6]),
        }
        for r in rows
    ]


def main():
    init_db()
    log_event("backend_logger_healthcheck", {"message": "SQLite event logger initialized"}, source="worker")
    payload = {"ok": True, "db_path": str(DB_PATH), "latest_events": latest_events(10)}
    (DATA_DIR / "sqlite_event_logger_latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
