"""
Curriculum Simplification Engine

Reduces overwhelm for activation-blocked and high-ambition overwhelmed users.
Turns large blocked concept graphs into small unlock loops with fast visible wins.

Goal:
- fewer simultaneous blocked concepts
- more micro-unlocks
- shorter dependency chains
- faster visible wins
- quicker "I can do this" loops
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

MAX_VISIBLE_READY = 3
MAX_VISIBLE_BLOCKED = 3


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_json(name, default):
    path = DATA_DIR / name
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def save_json(name, payload):
    (DATA_DIR / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def simplify_action(item):
    concept = item.get("concept", "this concept")
    domain = item.get("domain", "general_learning")
    if domain == "web_design":
        return f"Create one tiny visible example of {concept}. Stop after one change."
    if domain == "spanish":
        return f"Write or say only one original sentence using {concept}."
    if domain == "writing_assignment":
        return f"Create one usable line for the assignment using {concept}."
    if domain == "filmmaking":
        return f"Storyboard or describe one 5-second shot using {concept}."
    return f"Create one small proof that you used {concept}."


def make_micro_unlock(item, index):
    return {
        "micro_order": index,
        "concept": item.get("concept"),
        "domain": item.get("domain"),
        "mode": "micro_unlock",
        "estimated_minutes": 2,
        "visible_win": True,
        "action": simplify_action(item),
        "done_when": "There is one visible artifact, sentence, note, screenshot, or explanation.",
        "anti_overwhelm_rule": "Do not expand into the full assignment/path yet.",
        "reward_language": "This counts because it creates evidence and lowers the start barrier.",
    }


def main():
    curriculum = load_json("curriculum_sequence_latest.json", {})
    simulation = load_json("adaptive_simulation_evolution_latest.json", {})
    execution = load_json("execution_reinforcement_latest.json", {})

    ready = curriculum.get("next_best_items", []) if isinstance(curriculum, dict) else []
    blocked = curriculum.get("blocked_items", []) if isinstance(curriculum, dict) else []
    sim_runs = simulation.get("runs", []) if isinstance(simulation, dict) else []

    high_friction_profiles = [
        r for r in sim_runs
        if r.get("profile_id") in ["activation_blocked_student", "overwhelmed_high_ambition_user"]
        and r.get("recommendation") == "simplify_aggressively"
    ]

    simplified_ready = ready[:MAX_VISIBLE_READY]
    hidden_blocked = blocked[MAX_VISIBLE_BLOCKED:]
    visible_blocked = blocked[:MAX_VISIBLE_BLOCKED]

    micro_unlocks = []
    order = 1
    for item in simplified_ready:
        micro_unlocks.append(make_micro_unlock(item, order))
        order += 1

    # For blocked items, only expose the prerequisite/root idea, not the full blocked graph.
    for item in visible_blocked:
        prereqs = item.get("unmet_prerequisites", [])
        if prereqs:
            micro_unlocks.append({
                "micro_order": order,
                "concept": prereqs[0],
                "domain": item.get("domain"),
                "mode": "prerequisite_micro_unlock",
                "estimated_minutes": 2,
                "visible_win": True,
                "action": f"Do one tiny prerequisite proof for {prereqs[0]} before returning to {item.get('concept')}.",
                "done_when": "One prerequisite example or explanation exists.",
                "unlocks_toward": item.get("concept"),
                "anti_overwhelm_rule": "Only show the nearest prerequisite, not every dependency.",
                "reward_language": "This is progress because it removes the hidden blocker."
            })
            order += 1

    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "purpose": "Simplify curriculum view for high-friction users by creating small visible unlock loops.",
        "high_friction_profiles_detected": [r.get("profile_id") for r in high_friction_profiles],
        "original_counts": {
            "ready_items": len(ready),
            "blocked_items": len(blocked),
        },
        "simplified_counts": {
            "visible_ready_items": len(simplified_ready),
            "visible_blocked_items": len(visible_blocked),
            "hidden_blocked_items": len(hidden_blocked),
            "micro_unlocks": len(micro_unlocks),
        },
        "focus_lane": {
            "title": "Tiny Wins Lane",
            "description": "Only show the next few actions that can create proof quickly.",
            "max_visible_actions": len(micro_unlocks),
            "micro_unlocks": micro_unlocks,
        },
        "ui_rules": [
            "Do not show the full blocked graph to high-friction users by default.",
            "Show 1-3 ready actions and 1 nearest prerequisite at a time.",
            "Every visible action must produce proof in under 3 minutes.",
            "Use low-shame language and avoid backlog framing."
        ],
        "next_use": [
            "Frontend should render focus_lane before full curriculum graph.",
            "Pipeline should regenerate this after curriculum, simulation, and execution reinforcement.",
            "Real event data should later tune max_visible_actions per user."
        ]
    }
    save_json("curriculum_simplification_latest.json", payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
