"""
Event Ingestion Engine

Creates a simple real-event pipeline for Bridge Engine.
- Reads optional data/event_inbox.json
- Normalizes events into data/events_latest.json
- Appends events to SQLite using sqlite_event_logger when available
- Produces behavioral signals for adaptive learning loops

Supported event types include:
started_task, ignored_intervention, completed_recovery, environment_switch,
recall_answer_submitted, overwhelm_reported, returned_after_abandonment,
path_started, step_completed, intervention_accepted, intervention_completed.
"""

import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "bridge_engine.db"
DATA_DIR.mkdir(exist_ok=True)

EVENT_INBOX = DATA_DIR / "event_inbox.json"
EVENT_LOG = DATA_DIR / "events_log.jsonl"
EVENT_LATEST = DATA_DIR / "events_latest.json"

ALLOWED_EVENTS = {
    "started_task",
    "ignored_intervention",
    "completed_recovery",
    "environment_switch",
    "recall_answer_submitted",
    "overwhelm_reported",
    "returned_after_abandonment",
    "path_started",
    "step_completed",
    "intervention_accepted",
    "intervention_completed",
    "app_opened",
    "coach_message_shown",
    "coach_message_helpful",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def save_json(path, payload):
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def ensure_db():
    with sqlite3.connect(DB_PATH) as conn:
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


def normalize_event(raw):
    event_type = raw.get("event_type") or raw.get("type") or "unknown"
    if event_type not in ALLOWED_EVENTS:
        event_type = "unknown"
    return {
        "event_type": event_type,
        "timestamp": raw.get("timestamp") or now_iso(),
        "user_id": raw.get("user_id", "local_default"),
        "source": raw.get("source", "manual_or_app"),
        "payload": raw.get("payload", {k: v for k, v in raw.items() if k not in ["event_type", "type", "timestamp", "user_id", "source"]}),
        "synthetic": bool(raw.get("synthetic", False)),
    }


def append_event(event):
    with EVENT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    ensure_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO events (user_id, event_type, source, timestamp, payload_json, synthetic) VALUES (?, ?, ?, ?, ?, ?)",
            (event["user_id"], event["event_type"], event["source"], event["timestamp"], json.dumps(event["payload"]), 1 if event["synthetic"] else 0),
        )


def read_recent_events(limit=200):
    events = []
    if EVENT_LOG.exists():
        lines = EVENT_LOG.read_text(encoding="utf-8").splitlines()[-limit:]
        for line in lines:
            try:
                events.append(json.loads(line))
            except Exception:
                continue
    return events


def behavior_signals(events):
    counts = Counter(event.get("event_type") for event in events)
    starts = counts.get("started_task", 0) + counts.get("path_started", 0)
    completions = counts.get("step_completed", 0) + counts.get("intervention_completed", 0)
    overwhelm = counts.get("overwhelm_reported", 0)
    ignored = counts.get("ignored_intervention", 0)
    recovery = counts.get("completed_recovery", 0) + counts.get("returned_after_abandonment", 0)
    return {
        "event_counts": dict(counts),
        "start_events": starts,
        "completion_events": completions,
        "overwhelm_events": overwhelm,
        "ignored_intervention_events": ignored,
        "recovery_events": recovery,
        "start_to_completion_signal": round(completions / starts, 2) if starts else 0,
        "recovery_signal": round(recovery / max(overwhelm, 1), 2) if overwhelm else recovery,
    }


def seed_sample_if_empty():
    if EVENT_INBOX.exists() or EVENT_LOG.exists():
        return []
    return [
        {"event_type": "app_opened", "source": "sample_seed", "synthetic": True, "payload": {"note": "first local seed event"}},
        {"event_type": "coach_message_shown", "source": "sample_seed", "synthetic": True, "payload": {"card": "micro_start"}},
    ]


def main():
    inbox = load_json(EVENT_INBOX, {"events": []})
    raw_events = inbox.get("events", []) if isinstance(inbox, dict) else []
    raw_events.extend(seed_sample_if_empty())

    ingested = []
    for raw in raw_events:
        event = normalize_event(raw)
        append_event(event)
        ingested.append(event)

    if EVENT_INBOX.exists() and raw_events:
        save_json(EVENT_INBOX, {"events": [], "cleared_at": now_iso(), "note": "Events moved into events_log.jsonl and SQLite."})

    recent = read_recent_events(200)
    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "ingested_count": len(ingested),
        "recent_count": len(recent),
        "recent_events": recent[-50:],
        "behavior_signals": behavior_signals(recent),
        "schema": {
            "event_type": sorted(ALLOWED_EVENTS),
            "minimum_fields": ["event_type", "timestamp", "user_id", "source", "payload", "synthetic"]
        },
        "next_use": [
            "Feed behavior_signals into execution reinforcement.",
            "Use recall_answer_submitted events to update recall evidence.",
            "Use overwhelm/recovery events to adapt intervention ranking."
        ]
    }
    save_json(EVENT_LATEST, payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
