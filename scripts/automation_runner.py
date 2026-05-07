"""
Bridge Engine Automation Runner

Purpose:
- Run multiple self-learning / retention jobs from one cron-friendly command.
- Keep the product improving while the server is online 24/7.
- Avoid paid AI calls by default; this is local/rule-based infrastructure.

Run manually:
    python scripts/automation_runner.py

Recommended cron:
    */30 * * * * cd /home/ubuntu/bridge-engine && /home/ubuntu/bridge-engine/venv/bin/python scripts/automation_runner.py >> /home/ubuntu/bridge-engine/data/automation_runner.log 2>&1
"""

import json
import os
from datetime import datetime, date

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
PATHS_FILE = os.path.join(DATA_DIR, "bridge_paths.json")
PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, "notifications.json")
AUTOMATION_STATE_FILE = os.path.join(DATA_DIR, "automation_state.json")
SELF_LEARNING_FILE = os.path.join(DATA_DIR, "self_learning_latest.json")
RETENTION_FILE = os.path.join(DATA_DIR, "retention_metrics_latest.json")


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


def add_notification(kind, title, message, priority="normal", action_url=None):
    items = load_json(NOTIFICATIONS_FILE, [])
    recent_duplicate = any(
        n.get("kind") == kind and n.get("title") == title and str(n.get("created_at", "")).startswith(str(date.today()))
        for n in items[:10]
    )
    if recent_duplicate:
        return
    items.insert(0, {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "kind": kind,
        "title": title,
        "message": message,
        "priority": priority,
        "action_url": action_url,
        "created_at": now_stamp(),
        "read": False,
    })
    save_json(NOTIFICATIONS_FILE, items[-100:])


def compute_retention_metrics(paths):
    total_paths = len(paths)
    started_paths = len([p for p in paths if progress_percent(p) > 0])
    completed_paths = len([p for p in paths if progress_percent(p) == 100])
    abandoned_paths = len([p for p in paths if progress_percent(p) == 0])
    partial_paths = len([p for p in paths if 0 < progress_percent(p) < 100])

    total_steps = 0
    done_steps = 0
    feedback_events = 0
    overwhelm_events = 0
    flow_events = 0

    for path in paths:
        for step in path.get("steps", []):
            total_steps += 1
            if step.get("status") == "done":
                done_steps += 1
            for feedback in step.get("feedback", []):
                feedback_events += 1
                if feedback.get("type") in ["too_hard", "overwhelmed", "avoided"]:
                    overwhelm_events += 1
                if feedback.get("type") in ["flow", "worked_well", "want_more"]:
                    flow_events += 1

    completion_rate = int((done_steps / total_steps) * 100) if total_steps else 0
    start_rate = int((started_paths / total_paths) * 100) if total_paths else 0

    if overwhelm_events > flow_events:
        recommended_mode = "low"
    elif flow_events >= 3 and completion_rate >= 50:
        recommended_mode = "hyperfocus"
    else:
        recommended_mode = "focused"

    return {
        "generated_at": now_stamp(),
        "total_paths": total_paths,
        "started_paths": started_paths,
        "completed_paths": completed_paths,
        "partial_paths": partial_paths,
        "abandoned_paths": abandoned_paths,
        "total_steps": total_steps,
        "done_steps": done_steps,
        "completion_rate": completion_rate,
        "start_rate": start_rate,
        "feedback_events": feedback_events,
        "overwhelm_events": overwhelm_events,
        "flow_events": flow_events,
        "recommended_energy_mode": recommended_mode,
    }


def build_self_learning_summary(paths, profile, retention):
    insights = []
    actions = []

    if retention["total_paths"] == 0:
        insights.append("No user paths exist yet. The system should focus on onboarding and first path creation.")
        actions.append({"type": "onboarding", "title": "Create first-path suggestions", "priority": "high"})
    if retention["abandoned_paths"] > 0:
        insights.append("Some paths were created but never started. This suggests start friction or weak first-step activation.")
        actions.append({"type": "momentum_recovery", "title": "Offer a 3-minute restart task for abandoned paths", "priority": "high"})
    if retention["overwhelm_events"] > retention["flow_events"]:
        insights.append("Overwhelm feedback is higher than flow feedback. The app should reduce task size and increase guidance.")
        actions.append({"type": "simplify", "title": "Switch default generation toward low-energy micro steps", "priority": "high"})
    if retention["flow_events"] >= 3:
        insights.append("Flow feedback is building. The app can introduce challenge mode and continuation paths.")
        actions.append({"type": "challenge", "title": "Offer Keep Going challenge paths", "priority": "medium"})
    if retention["completion_rate"] < 25 and retention["total_steps"] > 0:
        insights.append("Completion rate is low. Improve first-step clarity and reduce checkpoint size.")
        actions.append({"type": "clarity", "title": "Rewrite checkpoints to be more concrete", "priority": "high"})
    if not insights:
        insights.append("Not enough signal yet. Keep collecting completion, feedback, and path creation data.")
        actions.append({"type": "data_collection", "title": "Collect more usage events", "priority": "normal"})

    return {
        "generated_at": now_stamp(),
        "profile_snapshot": {
            "name": profile.get("name"),
            "energy_mode": profile.get("energy_mode"),
            "learning_style": profile.get("learning_style"),
            "motivation_type": profile.get("motivation_type"),
            "core_interests": profile.get("core_interests", []),
        },
        "retention_metrics": retention,
        "insights": insights,
        "recommended_actions": actions,
        "product_learning_goal": "Improve activation, continuation, and restart momentum without relying on paid AI calls.",
    }


def update_profile_recommendations(profile, retention):
    profile.setdefault("automation", {})
    profile["automation"]["last_recommendation_at"] = now_stamp()
    profile["automation"]["recommended_energy_mode"] = retention["recommended_energy_mode"]
    profile["automation"]["retention_completion_rate"] = retention["completion_rate"]
    return profile


def main():
    paths = load_json(PATHS_FILE, [])
    profile = load_json(PROFILE_FILE, {})
    state = load_json(AUTOMATION_STATE_FILE, {"runs": 0})

    retention = compute_retention_metrics(paths)
    summary = build_self_learning_summary(paths, profile, retention)
    profile = update_profile_recommendations(profile, retention)

    save_json(RETENTION_FILE, retention)
    save_json(SELF_LEARNING_FILE, summary)
    save_json(PROFILE_FILE, profile)

    for action in summary["recommended_actions"][:3]:
        add_notification(
            "automation_recommendation",
            action["title"],
            f"Priority: {action['priority']}. Generated by automation runner.",
            action.get("priority", "normal"),
        )

    state["runs"] = int(state.get("runs", 0)) + 1
    state["last_run_at"] = now_stamp()
    state["last_completion_rate"] = retention["completion_rate"]
    save_json(AUTOMATION_STATE_FILE, state)

    print(json.dumps({
        "ok": True,
        "ran_at": now_stamp(),
        "runs": state["runs"],
        "retention": retention,
        "actions": summary["recommended_actions"],
    }, indent=2))


if __name__ == "__main__":
    main()
