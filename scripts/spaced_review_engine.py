"""
Spaced Review Engine

Schedules lightweight reviews for weak/developing concepts so users actually retain material.
Designed to be cron-safe and JSON-output-first for later UI integration.
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

REVIEW_INTERVALS = {
    "weak": [0, 1, 3, 7],
    "developing": [1, 4, 10],
    "strong": [7, 21],
}


def now_utc():
    return datetime.now(timezone.utc)


def load_json(name, default):
    path = DATA_DIR / name
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def make_review_prompt(concept, level):
    if level == "weak":
        return f"Explain {concept} in one sentence, then apply it to a tiny example."
    if level == "developing":
        return f"Use {concept} in a new example without looking back."
    return f"Teach {concept} to someone else or transfer it to a different project."


def main():
    mastery = load_json("mastery_tracking_latest.json", {})
    items = mastery.get("mastery_items", []) if isinstance(mastery, dict) else []

    schedule = []
    current = now_utc()
    for item in items:
        level = item.get("mastery_level", "weak")
        concept = item.get("concept", "unknown concept")
        for days in REVIEW_INTERVALS.get(level, [1, 3, 7]):
            due = current + timedelta(days=days)
            schedule.append({
                "concept": concept,
                "domain": item.get("domain"),
                "mastery_level": level,
                "review_due_at": due.isoformat(),
                "review_type": "same_day" if days == 0 else f"{days}_day_review",
                "prompt": make_review_prompt(concept, level),
                "estimated_minutes": 2 if level == "weak" else 5,
                "path_id": item.get("path_id"),
            })

    payload = {
        "ok": True,
        "generated_at": current.isoformat(),
        "purpose": "Auto-schedule concept reviews so users retain actual material.",
        "review_count": len(schedule),
        "reviews": schedule[:100],
        "rules": [
            "Weak concepts get faster reviews.",
            "Reviews must be short enough to reduce avoidance.",
            "Strong concepts should be transferred to new contexts."
        ]
    }
    (DATA_DIR / "spaced_review_latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
