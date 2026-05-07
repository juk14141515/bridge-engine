"""
Bridge Engine Simulated Usage Engine

Purpose:
- Generate realistic synthetic usage before real users arrive.
- Test retention, flow, overwhelm, and reward-loop behavior safely.
- Stress-test the adaptive engine without pretending fake users are real customers.

Ethical guardrail:
Synthetic data must stay labeled as synthetic and should never be mixed with real production analytics without a flag.

Run manually:
    python scripts/simulated_usage_engine.py

Suggested cron for testing only:
    5 * * * * cd /home/ubuntu/bridge-engine && /home/ubuntu/bridge-engine/venv/bin/python scripts/simulated_usage_engine.py >> /home/ubuntu/bridge-engine/data/simulated_usage.log 2>&1
"""

import json
import os
import random
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
SIM_EVENTS_FILE = os.path.join(DATA_DIR, "synthetic_usage_events.json")
SIM_REPORT_FILE = os.path.join(DATA_DIR, "synthetic_usage_report.json")

ARCHETYPES = [
    {
        "name": "overwhelmed_starter",
        "traits": ["low_energy", "needs_clarity", "abandons_large_tasks"],
        "completion_bias": 0.25,
        "feedback_bias": ["too_hard", "overwhelmed", "worked_well"],
    },
    {
        "name": "dopamine_seeker",
        "traits": ["likes_novelty", "needs_visible_progress", "gets_bored_fast"],
        "completion_bias": 0.45,
        "feedback_bias": ["bored", "want_more", "flow"],
    },
    {
        "name": "hyperfocus_builder",
        "traits": ["high_energy", "likes_challenge", "continues_when_hooked"],
        "completion_bias": 0.75,
        "feedback_bias": ["flow", "want_more", "worked_well"],
    },
    {
        "name": "school_avoidant_learner",
        "traits": ["hates_academic_framing", "needs_project_context", "avoids_vague_tasks"],
        "completion_bias": 0.35,
        "feedback_bias": ["unclear", "not_interested", "worked_well"],
    },
    {
        "name": "consistent_grinder",
        "traits": ["steady", "likes_progress", "moderate_energy"],
        "completion_bias": 0.6,
        "feedback_bias": ["worked_well", "flow", "too_easy"],
    },
]

TASK_TYPES = ["micro_task", "project_step", "challenge_step", "recovery_step", "reflection_step", "skill_tree_step"]


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


def simulate_event(archetype):
    task_type = random.choice(TASK_TYPES)
    completed = random.random() < archetype["completion_bias"]
    feedback = random.choice(archetype["feedback_bias"])

    if task_type == "micro_task":
        completed = completed or random.random() < 0.25
    if task_type == "challenge_step" and "low_energy" in archetype["traits"]:
        completed = random.random() < 0.15
        feedback = random.choice(["too_hard", "overwhelmed", "avoided"])
    if task_type == "recovery_step" and "abandons_large_tasks" in archetype["traits"]:
        completed = random.random() < 0.55
        feedback = random.choice(["worked_well", "flow", "clear"])

    return {
        "synthetic": True,
        "created_at": now_stamp(),
        "archetype": archetype["name"],
        "traits": archetype["traits"],
        "task_type": task_type,
        "completed": completed,
        "feedback": feedback,
        "session_minutes": random.choice([3, 5, 8, 10, 15, 20]),
    }


def analyze(events):
    total = len(events)
    completed = len([e for e in events if e.get("completed")])
    completion_rate = int((completed / total) * 100) if total else 0

    by_archetype = {}
    for event in events:
        name = event["archetype"]
        bucket = by_archetype.setdefault(name, {"total": 0, "completed": 0, "feedback": {}})
        bucket["total"] += 1
        if event.get("completed"):
            bucket["completed"] += 1
        fb = event.get("feedback")
        bucket["feedback"][fb] = bucket["feedback"].get(fb, 0) + 1

    recommendations = []
    for name, bucket in by_archetype.items():
        rate = int((bucket["completed"] / bucket["total"]) * 100) if bucket["total"] else 0
        feedback = bucket["feedback"]
        if rate < 35:
            recommendations.append({
                "archetype": name,
                "type": "reduce_friction",
                "recommendation": "Use recovery steps, clearer first actions, and smaller checkpoints.",
            })
        if feedback.get("bored", 0) + feedback.get("not_interested", 0) > feedback.get("flow", 0):
            recommendations.append({
                "archetype": name,
                "type": "increase_novelty",
                "recommendation": "Inject novelty, project choice, skill-tree unlocks, or challenge cards.",
            })
        if feedback.get("too_hard", 0) + feedback.get("overwhelmed", 0) > 1:
            recommendations.append({
                "archetype": name,
                "type": "micro_mode",
                "recommendation": "Default this archetype into low-energy micro tasks until completion improves.",
            })

    return {
        "generated_at": now_stamp(),
        "synthetic": True,
        "total_events": total,
        "completion_rate": completion_rate,
        "by_archetype": by_archetype,
        "recommendations": recommendations,
        "guardrails": [
            "Synthetic results are for product testing only.",
            "Do not market synthetic metrics as real user traction.",
            "Use simulations to reduce harm and improve accessibility before launch.",
        ],
    }


def main():
    events = load_json(SIM_EVENTS_FILE, [])
    new_events = []
    for _ in range(25):
        archetype = random.choice(ARCHETYPES)
        new_events.append(simulate_event(archetype))

    events.extend(new_events)
    events = events[-1000:]
    report = analyze(events)

    save_json(SIM_EVENTS_FILE, events)
    save_json(SIM_REPORT_FILE, report)

    print(json.dumps({
        "ok": True,
        "generated_events": len(new_events),
        "total_events": len(events),
        "completion_rate": report["completion_rate"],
        "recommendations": report["recommendations"][:5],
    }, indent=2))


if __name__ == "__main__":
    main()
