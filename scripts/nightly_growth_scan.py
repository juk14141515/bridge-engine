"""
Bridge Engine nightly growth scanner.

Purpose:
- Run from cron or Task Scheduler while the user is away.
- Read local usage data.
- Detect momentum, friction, burnout risk, abandoned paths, and skill-tree progress.
- Write a machine-readable report to data/nightly_growth_report.json.

Run manually:
    python scripts/nightly_growth_scan.py

Example cron on Ubuntu:
    0 7 * * * cd /home/ubuntu/bridge-engine && /home/ubuntu/bridge-engine/venv/bin/python scripts/nightly_growth_scan.py

This script does not call paid AI APIs. It is local/rule-based by design.
"""

import json
import os
from datetime import datetime, date

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
PATHS_FILE = os.path.join(DATA_DIR, "bridge_paths.json")
PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")
SKILL_TREE_FILE = os.path.join(DATA_DIR, "skill_tree.json")
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, "notifications.json")
REPORT_FILE = os.path.join(DATA_DIR, "nightly_growth_report.json")


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


def progress_percent(path):
    steps = path.get("steps", [])
    if not steps:
        return 0
    done = len([s for s in steps if s.get("status") == "done"])
    return int((done / len(steps)) * 100)


def detect_friction(paths):
    abandoned = []
    overwhelmed = []
    slow = []

    for path in paths:
        progress = progress_percent(path)
        events = path.get("events", [])
        feedback_text = " ".join(str(e).lower() for e in events)

        if progress == 0:
            abandoned.append({
                "path_id": path.get("id"),
                "title": path.get("title"),
                "reason": "No steps completed yet.",
            })
        elif 0 < progress < 50:
            slow.append({
                "path_id": path.get("id"),
                "title": path.get("title"),
                "progress": progress,
                "reason": "Partial progress but not enough momentum yet.",
            })

        if any(word in feedback_text for word in ["too_hard", "overwhelmed", "avoided"]):
            overwhelmed.append({
                "path_id": path.get("id"),
                "title": path.get("title"),
                "reason": "User feedback indicates friction or overwhelm.",
            })

    return {
        "abandoned_paths": abandoned[:10],
        "slow_paths": slow[:10],
        "overwhelm_flags": overwhelmed[:10],
    }


def detect_flow(paths):
    today = str(date.today())
    completed_today = []
    continuation_candidates = []

    for path in paths:
        done_steps = [s for s in path.get("steps", []) if s.get("status") == "done"]
        today_steps = [s for s in done_steps if str(s.get("completed_at", "")).startswith(today)]
        if today_steps:
            completed_today.append({
                "path_id": path.get("id"),
                "title": path.get("title"),
                "steps_completed_today": len(today_steps),
            })
        if progress_percent(path) >= 75:
            continuation_candidates.append({
                "path_id": path.get("id"),
                "title": path.get("title"),
                "recommendation": "Offer Keep Going continuation or next-level challenge.",
            })

    state = "hot" if len(completed_today) >= 3 else "building" if completed_today else "cold"
    return {
        "flow_state": state,
        "completed_today": completed_today,
        "continuation_candidates": continuation_candidates[:10],
    }


def recommend_actions(friction, flow, profile):
    actions = []
    if friction["overwhelm_flags"]:
        actions.append({
            "type": "simplify",
            "title": "Switch next tasks to Low Energy mode",
            "why": "Repeated overwhelm should reduce step size instead of adding guilt.",
        })
    if friction["abandoned_paths"]:
        actions.append({
            "type": "momentum_recovery",
            "title": "Offer a 3-minute restart task",
            "why": "Abandoned paths need a tiny re-entry point, not a full restart.",
        })
    if flow["flow_state"] == "hot":
        actions.append({
            "type": "challenge",
            "title": "Offer a harder Keep Going challenge",
            "why": "The user is in momentum; challenge can increase retention if scoped carefully.",
        })
    if not actions:
        actions.append({
            "type": "tiny_win",
            "title": "Offer one tiny visible artifact task",
            "why": "Default to a small win when signal is unclear.",
        })
    return actions


def append_notifications(actions):
    notifications = load_json(NOTIFICATIONS_FILE, [])
    for action in actions:
        notifications.insert(0, {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "kind": "nightly_growth_scan",
            "title": action["title"],
            "message": action["why"],
            "priority": "normal",
            "created_at": now_stamp(),
            "read": False,
        })
    save_json(NOTIFICATIONS_FILE, notifications[-50:])


def main():
    paths = load_json(PATHS_FILE, [])
    profile = load_json(PROFILE_FILE, {})
    skill_tree = load_json(SKILL_TREE_FILE, {})

    friction = detect_friction(paths)
    flow = detect_flow(paths)
    actions = recommend_actions(friction, flow, profile)

    report = {
        "generated_at": now_stamp(),
        "summary": {
            "path_count": len(paths),
            "profile_name": profile.get("name"),
            "flow_state": flow["flow_state"],
            "skill_nodes": list((skill_tree.get("nodes") or {}).keys()),
        },
        "friction_detection": friction,
        "flow_detection": flow,
        "recommended_actions": actions,
        "next_system_moves": [
            "Create UI cards for momentum recovery.",
            "Add a 3-minute restart task button for abandoned paths.",
            "Add reminders/push notifications when user enters hot momentum state.",
            "Use feedback data to tune future path difficulty.",
        ],
    }

    save_json(REPORT_FILE, report)
    append_notifications(actions)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
