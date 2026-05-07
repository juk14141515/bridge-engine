"""
Bridge Engine Complex Path Simulation Engine

Purpose:
- Simulate difficult, multi-step, real-world tasks before real users arrive.
- Model complexity, dependencies, hidden subtasks, avoidance risk, and recovery plans.
- Generate smart structures for hard-to-simulate user requirements like:
  - semester plans
  - syllabi
  - long assignments
  - filmmaking projects
  - web apps
  - startup builds
  - work schedules
  - college workload clusters

Ethical note:
Synthetic complexity data is for product testing and path-quality improvement only.
It must not be presented as real user traction.

Run manually:
    python scripts/complex_path_simulation_engine.py

Cron suggestion:
    40 * * * * cd /home/ubuntu/bridge-engine && /home/ubuntu/bridge-engine/venv/bin/python scripts/complex_path_simulation_engine.py >> /home/ubuntu/bridge-engine/data/complex_path_simulation.log 2>&1
"""

import json
import os
import random
from datetime import datetime, timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "complex_path_simulation_latest.json")
EVENTS_FILE = os.path.join(DATA_DIR, "synthetic_complex_path_events.json")
FILTER_FILE = os.path.join(DATA_DIR, "complex_path_filter_latest.json")
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, "notifications.json")

COMPLEX_SCENARIOS = [
    {
        "scenario_id": "semester_overload",
        "title": "Semester Overload Plan",
        "domain": "college",
        "difficulty": "hard",
        "hidden_subtasks": ["read syllabus", "find deadlines", "rank assignments", "schedule recovery", "email professor if needed"],
        "risk_factors": ["deadline clustering", "unclear instructions", "avoidance", "sleep disruption"],
        "best_structures": ["calendar_chunking", "micro_start", "deadline_risk_map", "recovery_buffer"],
    },
    {
        "scenario_id": "research_paper",
        "title": "Research Paper Execution Plan",
        "domain": "school_assignment",
        "difficulty": "hard",
        "hidden_subtasks": ["choose topic", "find sources", "outline", "bad first draft", "revise", "citations"],
        "risk_factors": ["blank page paralysis", "too much reading", "perfectionism", "citation anxiety"],
        "best_structures": ["bad_first_draft", "source_micro_goal", "outline_first", "checkpoint_rewards"],
    },
    {
        "scenario_id": "make_a_movie",
        "title": "Short Film / Movie Project",
        "domain": "filmmaking",
        "difficulty": "hard",
        "hidden_subtasks": ["idea", "script", "shot list", "schedule shoot", "film", "edit", "sound", "export"],
        "risk_factors": ["too much equipment", "unclear story", "editing overwhelm", "perfectionism"],
        "best_structures": ["phone_only_mode", "15_second_scene", "storyboard_3_frames", "publishable_microfilm"],
    },
    {
        "scenario_id": "web_app_build",
        "title": "Build a Web App",
        "domain": "coding_project",
        "difficulty": "hard",
        "hidden_subtasks": ["define MVP", "create files", "build route", "make UI", "save data", "deploy", "test"],
        "risk_factors": ["scope creep", "setup friction", "debugging fatigue", "unclear next step"],
        "best_structures": ["single_feature_mvp", "visible_artifact", "codex_prompt", "deploy_checkpoint"],
    },
    {
        "scenario_id": "startup_validation",
        "title": "Startup Idea Validation",
        "domain": "business",
        "difficulty": "hard",
        "hidden_subtasks": ["problem statement", "target user", "landing page", "user interview", "offer", "feedback loop"],
        "risk_factors": ["analysis paralysis", "fear of rejection", "too broad idea", "no feedback"],
        "best_structures": ["one_user_profile", "landing_page_mvp", "interview_script", "tiny_offer"],
    },
    {
        "scenario_id": "work_school_balance",
        "title": "Work + School Schedule Plan",
        "domain": "life_planning",
        "difficulty": "medium_hard",
        "hidden_subtasks": ["collect schedule", "identify gaps", "protect sleep", "rank deadlines", "plan recovery"],
        "risk_factors": ["time blindness", "fatigue", "overcommitment", "missed transitions"],
        "best_structures": ["energy_blocks", "transition_prompts", "calendar_overlay", "low_energy_tasks"],
    }
]

SIM_USERS = [
    {"id": "adhd_student", "activation": 0.35, "overwhelm_sensitivity": 0.8, "responds_to": ["micro_start", "walking", "clear_checkpoint", "visual_plan"]},
    {"id": "burnout_user", "activation": 0.28, "overwhelm_sensitivity": 0.9, "responds_to": ["recovery_buffer", "gentle_language", "low_energy_tasks"]},
    {"id": "hyperfocus_builder", "activation": 0.75, "overwhelm_sensitivity": 0.35, "responds_to": ["challenge", "visible_artifact", "deep_work", "deploy_checkpoint"]},
    {"id": "busy_worker_student", "activation": 0.45, "overwhelm_sensitivity": 0.65, "responds_to": ["calendar_overlay", "energy_blocks", "deadline_risk_map"]},
    {"id": "creative_project_user", "activation": 0.58, "overwhelm_sensitivity": 0.55, "responds_to": ["storyboard_3_frames", "phone_only_mode", "publishable_microfilm", "music_supported"]}
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


def build_complex_path(scenario):
    due_days = random.choice([2, 4, 7, 14, 21, 30])
    due_date = (datetime.now() + timedelta(days=due_days)).strftime("%Y-%m-%d")
    steps = []

    for idx, subtask in enumerate(scenario["hidden_subtasks"], start=1):
        steps.append({
            "step": idx,
            "name": subtask,
            "estimated_minutes": random.choice([3, 5, 10, 15, 25, 45]),
            "activation_cost": random.choice(["low", "medium", "high"]),
            "dependency": idx - 1 if idx > 1 else None,
            "recommended_mode": random.choice(["micro_start", "guided", "deep_work", "walking", "recovery"]),
        })

    return {
        "scenario_id": scenario["scenario_id"],
        "title": scenario["title"],
        "domain": scenario["domain"],
        "difficulty": scenario["difficulty"],
        "due_date": due_date,
        "steps": steps,
        "risk_factors": scenario["risk_factors"],
        "best_structures": scenario["best_structures"],
    }


def simulate_complex_outcome(user, path):
    completed_steps = 0
    overwhelmed = False
    recovery_used = False
    events = []

    for step in path["steps"]:
        activation = user["activation"]
        if step["activation_cost"] == "high":
            activation -= 0.18
        if step["estimated_minutes"] >= 25:
            activation -= 0.12
        if step["recommended_mode"] in user["responds_to"]:
            activation += 0.18
        if any(structure in user["responds_to"] for structure in path["best_structures"]):
            activation += 0.12

        risk_pressure = len(path["risk_factors"]) * 0.04
        overwhelm_chance = min(0.9, user["overwhelm_sensitivity"] * risk_pressure)
        if random.random() < overwhelm_chance:
            overwhelmed = True
            if "recovery_buffer" in path["best_structures"] or "recovery" == step["recommended_mode"]:
                recovery_used = True
                activation += 0.15

        completed = random.random() < max(0.05, min(0.95, activation))
        if completed:
            completed_steps += 1

        events.append({
            "step_name": step["name"],
            "completed": completed,
            "activation_cost": step["activation_cost"],
            "estimated_minutes": step["estimated_minutes"],
            "recommended_mode": step["recommended_mode"],
        })

    completion_rate = int((completed_steps / len(path["steps"])) * 100) if path["steps"] else 0

    if completion_rate >= 80:
        verdict = "path_works"
    elif completion_rate >= 45:
        verdict = "needs_finish_support"
    elif overwhelmed:
        verdict = "needs_recovery_first"
    else:
        verdict = "needs_lower_activation"

    return {
        "synthetic": True,
        "created_at": now_stamp(),
        "user_id": user["id"],
        "scenario_id": path["scenario_id"],
        "domain": path["domain"],
        "difficulty": path["difficulty"],
        "due_date": path["due_date"],
        "completed_steps": completed_steps,
        "total_steps": len(path["steps"]),
        "completion_rate": completion_rate,
        "overwhelmed": overwhelmed,
        "recovery_used": recovery_used,
        "verdict": verdict,
        "events": events,
        "risk_factors": path["risk_factors"],
        "best_structures": path["best_structures"],
    }


def analyze(events):
    grouped = {}
    for event in events:
        key = f"{event['user_id']}::{event['scenario_id']}"
        item = grouped.setdefault(key, {
            "user_id": event["user_id"],
            "scenario_id": event["scenario_id"],
            "domain": event["domain"],
            "runs": 0,
            "avg_completion": 0,
            "completion_values": [],
            "overwhelm_count": 0,
            "recovery_success_count": 0,
            "verdicts": {},
            "recommended_structures": {},
        })
        item["runs"] += 1
        item["completion_values"].append(event["completion_rate"])
        if event["overwhelmed"]:
            item["overwhelm_count"] += 1
        if event["recovery_used"] and event["completion_rate"] >= 45:
            item["recovery_success_count"] += 1
        item["verdicts"][event["verdict"]] = item["verdicts"].get(event["verdict"], 0) + 1
        for structure in event["best_structures"]:
            item["recommended_structures"][structure] = item["recommended_structures"].get(structure, 0) + 1

    filters = []
    for item in grouped.values():
        item["avg_completion"] = int(sum(item["completion_values"]) / len(item["completion_values"])) if item["completion_values"] else 0
        del item["completion_values"]
        best_verdict = max(item["verdicts"].items(), key=lambda x: x[1])[0] if item["verdicts"] else "unknown"
        top_structures = sorted(item["recommended_structures"].items(), key=lambda x: x[1], reverse=True)[:4]
        action = "standard_plan"
        if best_verdict == "needs_recovery_first":
            action = "recovery_first_plan"
        elif best_verdict == "needs_lower_activation":
            action = "micro_start_plan"
        elif best_verdict == "needs_finish_support":
            action = "checkpoint_finish_plan"
        elif best_verdict == "path_works":
            action = "scale_complexity"
        filters.append({
            "user_id": item["user_id"],
            "scenario_id": item["scenario_id"],
            "domain": item["domain"],
            "action": action,
            "avg_completion": item["avg_completion"],
            "overwhelm_rate": int((item["overwhelm_count"] / max(1, item["runs"])) * 100),
            "recommended_structures": [x[0] for x in top_structures],
            "dominant_verdict": best_verdict,
        })

    return grouped, filters


def add_notification(summary):
    notifications = load_json(NOTIFICATIONS_FILE, [])
    notifications.insert(0, {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "kind": "complex_path_simulation",
        "title": "Complex path simulation updated",
        "message": f"Generated {summary['new_events']} complex synthetic paths and {summary['filter_count']} filters.",
        "priority": "normal",
        "created_at": now_stamp(),
        "read": False,
    })
    save_json(NOTIFICATIONS_FILE, notifications[-100:])


def main():
    events = load_json(EVENTS_FILE, [])
    new_events = []

    for _ in range(36):
        scenario = random.choice(COMPLEX_SCENARIOS)
        user = random.choice(SIM_USERS)
        path = build_complex_path(scenario)
        new_events.append(simulate_complex_outcome(user, path))

    events.extend(new_events)
    events = events[-5000:]
    grouped, filters = analyze(events)

    output = {
        "generated_at": now_stamp(),
        "synthetic": True,
        "purpose": "Simulate complex real-world execution paths and discover safer/effective structures.",
        "total_events": len(events),
        "analysis": grouped,
        "guardrails": [
            "Synthetic data is for product testing only.",
            "Do not present synthetic outcomes as real user outcomes.",
            "Use this to make difficult tasks safer, clearer, and more accessible."
        ]
    }

    filter_output = {
        "generated_at": now_stamp(),
        "synthetic": True,
        "purpose": "Filter complex paths into smarter structures based on simulated risk and completion.",
        "filters": filters,
        "usage": "Future assignment/syllabus/project planners should use these filters to choose recovery-first, micro-start, finish-support, or scale-complexity plans."
    }

    save_json(EVENTS_FILE, events)
    save_json(OUTPUT_FILE, output)
    save_json(FILTER_FILE, filter_output)

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
