"""
Bridge Engine Context Intelligence Engine

Purpose:
- Learn when, where, and under what state a user is most likely to start/finish.
- Score contexts such as morning/afternoon/night, desk/walking/public, low/focused/hyperfocus.
- Recommend the best task mode for the user's current context.

Run manually:
    python scripts/context_intelligence_engine.py

Suggested cron:
    20,50 * * * * cd /home/ubuntu/bridge-engine && /home/ubuntu/bridge-engine/venv/bin/python scripts/context_intelligence_engine.py >> /home/ubuntu/bridge-engine/data/context_intelligence.log 2>&1
"""

import json
import os
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
PATHS_FILE = os.path.join(DATA_DIR, "bridge_paths.json")
PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")
CONTEXT_FILE = os.path.join(DATA_DIR, "context_intelligence_latest.json")
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, "notifications.json")

TIME_BUCKETS = {
    "morning": range(5, 12),
    "afternoon": range(12, 18),
    "night": list(range(18, 24)) + list(range(0, 5)),
}


def now_stamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default


def save_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def parse_hour(value):
    if not value:
        return None
    try:
        return datetime.strptime(value[:19], "%Y-%m-%d %H:%M:%S").hour
    except Exception:
        return None


def bucket_for_hour(hour):
    if hour is None:
        return "unknown"
    for name, hours in TIME_BUCKETS.items():
        if hour in hours:
            return name
    return "unknown"


def progress_percent(path):
    steps = path.get("steps", [])
    if not steps:
        return 0
    done = len([s for s in steps if s.get("status") == "done"])
    return int((done / len(steps)) * 100)


def collect_context_signals(paths):
    buckets = {
        "time_of_day": {"morning": {"attempts": 0, "successes": 0}, "afternoon": {"attempts": 0, "successes": 0}, "night": {"attempts": 0, "successes": 0}, "unknown": {"attempts": 0, "successes": 0}},
        "energy_mode": {},
        "environment": {},
        "session_length": {"short": {"attempts": 0, "successes": 0}, "medium": {"attempts": 0, "successes": 0}, "long": {"attempts": 0, "successes": 0}},
    }

    for path in paths:
        for step in path.get("steps", []):
            completed = step.get("status") == "done"
            created_at = path.get("created_at")
            completed_at = step.get("completed_at") or created_at
            bucket = bucket_for_hour(parse_hour(completed_at or created_at))
            buckets["time_of_day"].setdefault(bucket, {"attempts": 0, "successes": 0})
            buckets["time_of_day"][bucket]["attempts"] += 1
            if completed:
                buckets["time_of_day"][bucket]["successes"] += 1

            energy = step.get("energy_mode") or path.get("adaptive_context", {}).get("energy_mode") or "unknown"
            buckets["energy_mode"].setdefault(energy, {"attempts": 0, "successes": 0})
            buckets["energy_mode"][energy]["attempts"] += 1
            if completed:
                buckets["energy_mode"][energy]["successes"] += 1

            environment = step.get("environment") or path.get("environment") or "unknown"
            buckets["environment"].setdefault(environment, {"attempts": 0, "successes": 0})
            buckets["environment"][environment]["attempts"] += 1
            if completed:
                buckets["environment"][environment]["successes"] += 1

            minutes = step.get("estimated_minutes") or path.get("adaptive_context", {}).get("preferred_task_minutes") or 10
            try:
                minutes = int(minutes)
            except Exception:
                minutes = 10
            size = "short" if minutes <= 5 else "medium" if minutes <= 15 else "long"
            buckets["session_length"][size]["attempts"] += 1
            if completed:
                buckets["session_length"][size]["successes"] += 1

    return buckets


def score_bucket(bucket):
    attempts = bucket.get("attempts", 0)
    successes = bucket.get("successes", 0)
    if attempts == 0:
        return 0
    return int((successes / attempts) * 100)


def score_contexts(signals):
    scores = {}
    for category, data in signals.items():
        scores[category] = {}
        for key, bucket in data.items():
            scores[category][key] = {
                "score": score_bucket(bucket),
                "attempts": bucket.get("attempts", 0),
                "successes": bucket.get("successes", 0),
            }
    return scores


def best_key(scores, category, fallback):
    items = scores.get(category, {})
    if not items:
        return fallback
    filtered = {k: v for k, v in items.items() if k != "unknown" and v.get("attempts", 0) > 0}
    if not filtered:
        return fallback
    return max(filtered.items(), key=lambda pair: (pair[1].get("score", 0), pair[1].get("attempts", 0)))[0]


def build_recommendation(scores, profile):
    best_time = best_key(scores, "time_of_day", "night")
    best_energy = best_key(scores, "energy_mode", profile.get("energy_mode", "focused"))
    best_environment = best_key(scores, "environment", "desk")
    best_session = best_key(scores, "session_length", "medium")

    if best_session == "short":
        task_mode = "micro_start"
        minutes = 5
    elif best_session == "long":
        task_mode = "deep_work"
        minutes = 25
    else:
        task_mode = "guided_progress"
        minutes = 10

    return {
        "best_time_of_day": best_time,
        "best_energy_mode": best_energy,
        "best_environment": best_environment,
        "best_session_length": best_session,
        "recommended_task_mode": task_mode,
        "recommended_minutes": minutes,
        "message": f"Best current pattern: {best_session} {task_mode} tasks during {best_time}, ideally in {best_environment} mode.",
    }


def update_profile(profile, recommendation):
    profile.setdefault("context_intelligence", {})
    profile["context_intelligence"]["last_updated"] = now_stamp()
    profile["context_intelligence"].update(recommendation)
    return profile


def add_notification(recommendation):
    notifications = load_json(NOTIFICATIONS_FILE, [])
    notifications.insert(0, {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "kind": "context_intelligence",
        "title": "Context pattern updated",
        "message": recommendation["message"],
        "priority": "normal",
        "created_at": now_stamp(),
        "read": False,
    })
    save_json(NOTIFICATIONS_FILE, notifications[-100:])


def main():
    paths = load_json(PATHS_FILE, [])
    profile = load_json(PROFILE_FILE, {})
    signals = collect_context_signals(paths)
    scores = score_contexts(signals)
    recommendation = build_recommendation(scores, profile)
    profile = update_profile(profile, recommendation)

    output = {
        "generated_at": now_stamp(),
        "purpose": "Learn the best timing, environment, energy state, and session length for each user.",
        "signals": signals,
        "scores": scores,
        "recommendation": recommendation,
        "future_inputs": [
            "in_person_vs_online",
            "before_food_vs_after_food",
            "music_on_vs_silence",
            "walking_vs_desk",
            "public_place_vs_home",
            "body_doubling_vs_solo",
        ],
    }

    save_json(CONTEXT_FILE, output)
    save_json(PROFILE_FILE, profile)
    add_notification(recommendation)

    print(json.dumps({
        "ok": True,
        "generated_at": output["generated_at"],
        "recommendation": recommendation,
    }, indent=2))


if __name__ == "__main__":
    main()
