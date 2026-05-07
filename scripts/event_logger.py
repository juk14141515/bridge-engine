"""
Bridge Engine Event Logger

Purpose:
- Create structured behavioral training data.
- Standardize logging across all engines.
- Enable future personalization, analytics, and adaptive learning.
"""

import json
import os
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
EVENT_FILE = os.path.join(DATA_DIR, "event_log.json")


def load_events():
    if not os.path.exists(EVENT_FILE):
        return []
    try:
        with open(EVENT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_events(events):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(EVENT_FILE, "w", encoding="utf-8") as f:
        json.dump(events[-5000:], f, indent=2)


def log_event(event_type, payload=None):
    if payload is None:
        payload = {}

    events = load_events()

    entry = {
        "event_type": event_type,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "payload": payload,
    }

    events.append(entry)
    save_events(events)

    return entry


if __name__ == "__main__":
    demo = log_event("system_test", {"source": "event_logger"})
    print(json.dumps(demo, indent=2))
