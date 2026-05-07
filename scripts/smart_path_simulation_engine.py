"""
Bridge Engine Smart Path Simulation Engine

Purpose:
- Generate synthetic user/path/event data during the learning phase.
- Score which paths are most effective for different simulated users.
- Create a smart path filter so Bridge Engine can recommend better paths over time.

Important:
Synthetic data is for testing and product learning only. Never market it as real user traction.

Run manually:
    python scripts/smart_path_simulation_engine.py

Cron suggestion:
    25 * * * * cd /home/ubuntu/bridge-engine && /home/ubuntu/bridge-engine/venv/bin/python scripts/smart_path_simulation_engine.py >> /home/ubuntu/bridge-engine/data/smart_path_simulation.log 2>&1
"""

import json
import os
import random
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
GOAL_DIR = os.path.join(BASE_DIR, "goal_templates")

SIM_EVENTS_FILE = os.path.join(DATA_DIR, "synthetic_path_events.json")
SMART_PATHS_FILE = os.path.join(DATA_DIR, "smart_path_rankings_latest.json")
SMART_FILTER_FILE = os.path.join(DATA_DIR, "smart_path_filter_latest.json")
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, "notifications.json")

SIMULATED_USERS = [
    {
        "id": "adhd_overwhelmed_student",
        "label": "Overwhelmed student",
        "traits": ["low_activation", "school_friction", "avoids_vague_tasks", "needs_micro_steps"],
        "preferred_modalities": ["walking", "hands_on", "visual"],
        "avoid": ["long_reading", "large_assignments", "strict_streaks"],
        "base_completion": 0.28,
    },
    {
        "id": "night_hyperfocus_builder",
        "label": "Night hyperfocus builder",
        "traits": ["hyperfocus", "project_driven", "likes_challenge", "night_performer"],
        "preferred_modalities": ["hands_on", "music_supported", "gamified"],
        "avoid": ["slow_theory", "over_explaining"],
        "base_completion": 0.72,
    },
    {
        "id": "audio_walking_learner",
        "label": "Audio/walking learner",
        "traits": ["movement_helps", "listening_preference", "low_desk_tolerance"],
        "preferred_modalities": ["audio", "walking", "social_teaching"],
        "avoid": ["silent_studying", "long_screen_sessions"],
        "base_completion": 0.52,
    },
    {
        "id": "visual_project_learner",
        "label": "Visual project learner",
        "traits": ["visual_progress", "project_driven", "needs_examples"],
        "preferred_modalities": ["visual", "hands_on", "gamified"],
        "avoid": ["abstract_theory", "unclear_output"],
        "base_completion": 0.61,
    },
    {
        "id": "burnout_recovery_user",
        "label": "Burnout recovery user",
        "traits": ["low_energy", "needs_gentle_language", "restart_sensitive"],
        "preferred_modalities": ["walking", "audio", "writing"],
        "avoid": ["pressure", "competitive_rankings", "too_many_steps"],
        "base_completion": 0.34,
    }
]

PATH_FEATURES = [
    "micro_start",
    "visible_artifact",
    "project_first",
    "walking_mode",
    "audio_mode",
    "music_supported",
    "visual_example",
    "clear_checkpoint",
    "challenge_mode",
    "recovery_mode",
    "low_text",
    "deadline_aware",
    "skill_tree",
    "outside_app_ready"
]


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


def available_goal_templates():
    if not os.path.exists(GOAL_DIR):
        return ["general"]
    goals = []
    for name in os.listdir(GOAL_DIR):
        if name.endswith(".json"):
            goals.append(name.replace(".json", ""))
    return goals or ["general"]


def synthetic_path(goal_id):
    features = random.sample(PATH_FEATURES, random.randint(3, 6))
    return {
        "goal_id": goal_id,
        "path_id": f"synthetic_{goal_id}_{random.randint(1000, 9999)}",
        "features": features,
        "estimated_minutes": random.choice([3, 5, 10, 15, 25]),
        "difficulty": random.choice(["easy", "medium", "hard"]),
        "modality": random.choice(["hands_on", "visual", "audio", "walking", "music_supported", "reading", "gamified"]),
        "output_type": random.choice(["artifact", "checklist", "reflection", "prototype", "summary", "finished_task"]),
    }


def simulate_outcome(user, path):
    score = user["base_completion"]
    features = set(path["features"])

    if "micro_start" in features and "low_activation" in user["traits"]:
        score += 0.18
    if "recovery_mode" in features and ("restart_sensitive" in user["traits"] or "low_energy" in user["traits"]):
        score += 0.16
    if "visible_artifact" in features and ("visual_progress" in user["traits"] or "project_driven" in user["traits"]):
        score += 0.14
    if "project_first" in features and "project_driven" in user["traits"]:
        score += 0.16
    if "walking_mode" in features and "walking" in user["preferred_modalities"]:
        score += 0.12
    if "audio_mode" in features and "audio" in user["preferred_modalities"]:
        score += 0.12
    if "challenge_mode" in features and "likes_challenge" in user["traits"]:
        score += 0.13
    if "clear_checkpoint" in features and "avoids_vague_tasks" in user["traits"]:
        score += 0.15
    if "low_text" in features and "long_reading" in user["avoid"]:
        score += 0.1

    if path["difficulty"] == "hard" and ("low_energy" in user["traits"] or "low_activation" in user["traits"]):
        score -= 0.22
    if path["estimated_minutes"] >= 25 and ("low_activation" in user["traits"] or "low_desk_tolerance" in user["traits"]):
        score -= 0.18
    if path["modality"] == "reading" and "long_reading" in user["avoid"]:
        score -= 0.16

    score = max(0.03, min(0.95, score))
    completed = random.random() < score
    started = completed or random.random() < min(0.95, score + 0.2)

    if completed:
        feedback = random.choice(["flow", "worked_well", "want_more", "clear"])
    elif started:
        feedback = random.choice(["partial", "too_hard", "bored", "unclear"])
    else:
        feedback = random.choice(["avoided", "overwhelmed", "not_started"])

    return {
        "synthetic": True,
        "created_at": now_stamp(),
        "user_id": user["id"],
        "user_label": user["label"],
        "goal_id": path["goal_id"],
        "path_id": path["path_id"],
        "path_features": path["features"],
        "modality": path["modality"],
        "difficulty": path["difficulty"],
        "estimated_minutes": path["estimated_minutes"],
        "predicted_fit_score": round(score, 3),
        "started": started,
        "completed": completed,
        "feedback": feedback,
    }


def analyze_events(events):
    rankings = {}
    for event in events:
        key = f"{event['user_id']}::{event['goal_id']}"
        item = rankings.setdefault(key, {
            "user_id": event["user_id"],
            "goal_id": event["goal_id"],
            "total": 0,
            "started": 0,
            "completed": 0,
            "features": {},
            "modalities": {},
            "difficulties": {},
            "feedback": {},
        })
        item["total"] += 1
        if event.get("started"):
            item["started"] += 1
        if event.get("completed"):
            item["completed"] += 1
        for feature in event.get("path_features", []):
            bucket = item["features"].setdefault(feature, {"seen": 0, "completed": 0})
            bucket["seen"] += 1
            if event.get("completed"):
                bucket["completed"] += 1
        modality = event.get("modality", "unknown")
        item["modalities"][modality] = item["modalities"].get(modality, 0) + (1 if event.get("completed") else 0)
        diff = event.get("difficulty", "unknown")
        item["difficulties"][diff] = item["difficulties"].get(diff, 0) + (1 if event.get("completed") else 0)
        fb = event.get("feedback", "unknown")
        item["feedback"][fb] = item["feedback"].get(fb, 0) + 1

    for item in rankings.values():
        total = max(1, item["total"])
        item["start_rate"] = int((item["started"] / total) * 100)
        item["completion_rate"] = int((item["completed"] / total) * 100)
        feature_scores = []
        for feature, bucket in item["features"].items():
            if bucket["seen"]:
                feature_scores.append({
                    "feature": feature,
                    "score": int((bucket["completed"] / bucket["seen"]) * 100),
                    "seen": bucket["seen"],
                })
        item["top_features"] = sorted(feature_scores, key=lambda x: (x["score"], x["seen"]), reverse=True)[:5]
        item["best_modality"] = max(item["modalities"].items(), key=lambda x: x[1])[0] if item["modalities"] else "unknown"
        item["best_difficulty"] = max(item["difficulties"].items(), key=lambda x: x[1])[0] if item["difficulties"] else "unknown"

    return rankings


def build_smart_filter(rankings):
    filters = []
    for _, item in rankings.items():
        action = "balanced"
        if item["completion_rate"] < 35:
            action = "micro_recovery_first"
        elif item["completion_rate"] > 65:
            action = "challenge_and_scale"
        elif item["start_rate"] > 60 and item["completion_rate"] < 55:
            action = "finish_support"

        filters.append({
            "user_id": item["user_id"],
            "goal_id": item["goal_id"],
            "action": action,
            "required_features": [f["feature"] for f in item["top_features"][:3]],
            "avoid_features": [],
            "best_modality": item["best_modality"],
            "best_difficulty": item["best_difficulty"],
            "completion_rate": item["completion_rate"],
            "start_rate": item["start_rate"],
        })
    return filters


def add_notification(summary):
    notifications = load_json(NOTIFICATIONS_FILE, [])
    notifications.insert(0, {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "kind": "smart_path_simulation",
        "title": "Smart path simulation updated",
        "message": f"Generated {summary['new_events']} synthetic path events. Smart filters: {summary['filter_count']}.",
        "priority": "normal",
        "created_at": now_stamp(),
        "read": False,
    })
    save_json(NOTIFICATIONS_FILE, notifications[-100:])


def main():
    goals = available_goal_templates()
    events = load_json(SIM_EVENTS_FILE, [])
    new_events = []

    for _ in range(60):
        user = random.choice(SIMULATED_USERS)
        goal_id = random.choice(goals)
        path = synthetic_path(goal_id)
        new_events.append(simulate_outcome(user, path))

    events.extend(new_events)
    events = events[-5000:]
    rankings = analyze_events(events)
    filters = build_smart_filter(rankings)

    rankings_payload = {
        "generated_at": now_stamp(),
        "synthetic": True,
        "purpose": "Rank simulated path effectiveness by user archetype and goal.",
        "total_events": len(events),
        "rankings": rankings,
        "guardrails": [
            "Synthetic data is only for testing adaptive behavior.",
            "Do not report synthetic events as real users.",
            "Use simulations to identify safer, lower-friction path designs before launch."
        ]
    }

    filter_payload = {
        "generated_at": now_stamp(),
        "synthetic": True,
        "purpose": "Filter and recommend smart path structures for different user types.",
        "filters": filters,
        "usage": "Future path generation should prefer required_features and best_modality for matching users/goals.",
    }

    save_json(SIM_EVENTS_FILE, events)
    save_json(SMART_PATHS_FILE, rankings_payload)
    save_json(SMART_FILTER_FILE, filter_payload)

    summary = {
        "ok": True,
        "generated_at": now_stamp(),
        "new_events": len(new_events),
        "total_events": len(events),
        "filter_count": len(filters),
        "sample_filters": filters[:5],
    }
    add_notification(summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
