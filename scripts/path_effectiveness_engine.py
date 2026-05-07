"""
Bridge Engine Path Effectiveness Engine

Purpose:
- Learn which goal paths, modalities, start modes, and task types actually work.
- Score templates based on completion, starts, feedback, and friction.
- Produce recommendations for improving future generated paths.

Run manually:
    python scripts/path_effectiveness_engine.py

Suggested cron:
    10 * * * * cd /home/ubuntu/bridge-engine && /home/ubuntu/bridge-engine/venv/bin/python scripts/path_effectiveness_engine.py >> /home/ubuntu/bridge-engine/data/path_effectiveness.log 2>&1
"""

import json
import os
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
PATHS_FILE = os.path.join(DATA_DIR, "bridge_paths.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "path_effectiveness_latest.json")
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, "notifications.json")


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


def classify_success(path):
    progress = progress_percent(path)
    events = path.get("events", [])
    feedback_blob = " ".join(str(e).lower() for e in events)

    if progress == 100:
        return "completed"
    if progress > 0:
        return "started"
    if any(x in feedback_blob for x in ["overwhelmed", "too_hard", "avoided"]):
        return "friction"
    return "abandoned"


def analyze(paths):
    buckets = {}

    for path in paths:
        context = path.get("adaptive_context", {})
        key = context.get("bridge_type") or path.get("learning_goal") or "general"
        bucket = buckets.setdefault(key, {
            "total": 0,
            "completed": 0,
            "started": 0,
            "abandoned": 0,
            "friction": 0,
            "avg_progress": 0,
            "progress_values": [],
            "common_energy_modes": {},
            "common_sources": {},
        })

        state = classify_success(path)
        progress = progress_percent(path)
        bucket["total"] += 1
        bucket["progress_values"].append(progress)
        if state == "completed":
            bucket["completed"] += 1
        elif state == "started":
            bucket["started"] += 1
        elif state == "friction":
            bucket["friction"] += 1
        else:
            bucket["abandoned"] += 1

        energy = context.get("energy_mode", "unknown")
        bucket["common_energy_modes"][energy] = bucket["common_energy_modes"].get(energy, 0) + 1
        source = path.get("source", "unknown")
        bucket["common_sources"][source] = bucket["common_sources"].get(source, 0) + 1

    results = {}
    for key, bucket in buckets.items():
        total = bucket["total"]
        avg_progress = int(sum(bucket["progress_values"]) / len(bucket["progress_values"])) if bucket["progress_values"] else 0
        completion_rate = int((bucket["completed"] / total) * 100) if total else 0
        start_rate = int(((bucket["completed"] + bucket["started"]) / total) * 100) if total else 0
        friction_rate = int((bucket["friction"] / total) * 100) if total else 0

        if completion_rate >= 50:
            verdict = "working"
        elif start_rate >= 50 and completion_rate < 50:
            verdict = "starts_but_needs_finish_support"
        elif friction_rate >= 30:
            verdict = "too_much_friction"
        else:
            verdict = "needs_better_activation"

        results[key] = {
            **bucket,
            "avg_progress": avg_progress,
            "completion_rate": completion_rate,
            "start_rate": start_rate,
            "friction_rate": friction_rate,
            "verdict": verdict,
        }
        del results[key]["progress_values"]

    return results


def recommendations(results):
    recs = []
    for key, item in results.items():
        verdict = item["verdict"]
        if verdict == "working":
            recs.append({
                "goal_type": key,
                "action": "scale",
                "message": "This path type is working. Create more templates and continuation challenges.",
            })
        elif verdict == "starts_but_needs_finish_support":
            recs.append({
                "goal_type": key,
                "action": "add_finish_support",
                "message": "Users start this path but do not finish. Add smaller milestones, checkpoints, and reward moments.",
            })
        elif verdict == "too_much_friction":
            recs.append({
                "goal_type": key,
                "action": "simplify",
                "message": "This path creates friction. Use micro-starts, examples, and fewer steps.",
            })
        else:
            recs.append({
                "goal_type": key,
                "action": "improve_activation",
                "message": "This path needs a stronger first visible win and clearer emotional payoff.",
            })
    return recs


def notify(recs):
    items = load_json(NOTIFICATIONS_FILE, [])
    for rec in recs[:3]:
        items.insert(0, {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "kind": "path_effectiveness",
            "title": f"Path insight: {rec['goal_type']}",
            "message": rec["message"],
            "priority": "normal",
            "created_at": now_stamp(),
            "read": False,
        })
    save_json(NOTIFICATIONS_FILE, items[-100:])


def main():
    paths = load_json(PATHS_FILE, [])
    results = analyze(paths)
    recs = recommendations(results)
    payload = {
        "generated_at": now_stamp(),
        "purpose": "Learn which path types are effective and how to improve future templates.",
        "results": results,
        "recommendations": recs,
        "next_template_priorities": [
            "web_design",
            "filmmaking",
            "college_assignment",
            "coding_project",
            "investing_project"
        ]
    }
    save_json(OUTPUT_FILE, payload)
    notify(recs)
    print(json.dumps({"ok": True, "generated_at": payload["generated_at"], "recommendations": recs[:5]}, indent=2))


if __name__ == "__main__":
    main()
