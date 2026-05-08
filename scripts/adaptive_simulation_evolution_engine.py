"""
Adaptive Simulation Evolution Engine

Evolves synthetic learner/path simulations using current backend intelligence.
This helps Bridge Engine test path structures before enough real users exist.

The simulation remains clearly marked synthetic and should never be mixed with
real user evidence without labels.
"""

import json
import random
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

SIM_MEMORY_PATH = DATA_DIR / "adaptive_simulation_memory.json"

PROFILES = [
    {
        "id": "activation_blocked_student",
        "activation_friction": 0.85,
        "knowledge_gap": 0.55,
        "overwhelm_sensitivity": 0.8,
        "best_interventions": ["three_minute_start", "low_shame_recovery", "visible_progress"],
    },
    {
        "id": "knowledge_gap_builder",
        "activation_friction": 0.35,
        "knowledge_gap": 0.85,
        "overwhelm_sensitivity": 0.5,
        "best_interventions": ["prerequisite_micro_task", "explain_back", "visual_checkpoint"],
    },
    {
        "id": "overwhelmed_high_ambition_user",
        "activation_friction": 0.7,
        "knowledge_gap": 0.45,
        "overwhelm_sensitivity": 0.9,
        "best_interventions": ["environment_switch", "three_minute_start", "body_doubling"],
    },
    {
        "id": "steady_beginner",
        "activation_friction": 0.25,
        "knowledge_gap": 0.4,
        "overwhelm_sensitivity": 0.35,
        "best_interventions": ["visual_checkpoint", "explain_back", "visible_progress"],
    },
]


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_json(name_or_path, default):
    path = name_or_path if isinstance(name_or_path, Path) else DATA_DIR / name_or_path
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def save_json(name_or_path, payload):
    path = name_or_path if isinstance(name_or_path, Path) else DATA_DIR / name_or_path
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def simulate(profile, curriculum_items, interventions):
    intervention_ids = [i.get("id") for i in interventions]
    best_overlap = len(set(profile["best_interventions"]).intersection(intervention_ids[:3]))
    ready_count = len([item for item in curriculum_items if item.get("can_start_now")])
    blocked_count = len([item for item in curriculum_items if not item.get("can_start_now")])

    base_start = 1 - profile["activation_friction"]
    base_understanding = 1 - profile["knowledge_gap"]
    overwhelm_penalty = profile["overwhelm_sensitivity"] * min(blocked_count / max(len(curriculum_items), 1), 1)
    intervention_boost = best_overlap * 0.12
    micro_boost = 0.08 if any(item.get("mode") == "micro_interactive" for item in curriculum_items[:6]) else 0

    start_probability = max(0.05, min(0.95, base_start + intervention_boost + micro_boost - overwhelm_penalty * 0.25))
    completion_probability = max(0.03, min(0.9, start_probability * (base_understanding + intervention_boost + 0.15)))
    retention_probability = max(0.03, min(0.9, base_understanding + (0.1 if any(i.get("id") == "explain_back" for i in interventions[:3]) else 0)))
    overwhelm_probability = max(0.02, min(0.95, profile["overwhelm_sensitivity"] - intervention_boost - micro_boost))

    success_score = round(((start_probability * 0.3) + (completion_probability * 0.35) + (retention_probability * 0.25) + ((1 - overwhelm_probability) * 0.1)) * 100, 2)

    return {
        "profile_id": profile["id"],
        "synthetic": True,
        "ready_items": ready_count,
        "blocked_items": blocked_count,
        "interventions_tested": intervention_ids[:5],
        "start_probability": round(start_probability, 3),
        "completion_probability": round(completion_probability, 3),
        "retention_probability": round(retention_probability, 3),
        "overwhelm_probability": round(overwhelm_probability, 3),
        "success_score": success_score,
        "recommendation": "promote_structure" if success_score >= 65 else "revise_structure" if success_score >= 40 else "simplify_aggressively",
    }


def main():
    curriculum = load_json("curriculum_sequence_latest.json", {})
    execution = load_json("execution_reinforcement_latest.json", {})
    memory = load_json(SIM_MEMORY_PATH, {"runs": []})

    items = curriculum.get("next_best_items", []) + curriculum.get("blocked_items", [])
    interventions = execution.get("recommended_interventions", [])

    runs = [simulate(profile, items, interventions) for profile in PROFILES]
    avg_success = round(sum(r["success_score"] for r in runs) / max(len(runs), 1), 2)

    evolved_rules = []
    if avg_success < 45:
        evolved_rules.extend(["reduce_session_size", "increase_prerequisite_micro_tasks", "prioritize_low_shame_recovery"])
    elif avg_success < 65:
        evolved_rules.extend(["keep_micro_interactive_mode", "add_visual_checkpoints", "increase_explain_back"])
    else:
        evolved_rules.extend(["allow_gentle_challenge", "preserve_active_evidence", "expand_transfer_tasks"])

    memory.setdefault("runs", []).append({"generated_at": now_iso(), "avg_success": avg_success, "runs": runs, "evolved_rules": evolved_rules})
    memory["runs"] = memory["runs"][-50:]
    save_json(SIM_MEMORY_PATH, memory)

    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "purpose": "Evolve synthetic learner/path simulations to improve adaptive path design before real-user data is sufficient.",
        "synthetic_warning": "These are simulated signals only. Do not treat as real user evidence.",
        "avg_success_score": avg_success,
        "simulation_count": len(runs),
        "runs": runs,
        "evolved_rules": evolved_rules,
        "next_use": [
            "Feed evolved_rules into curriculum and intervention ranking as weak synthetic hints.",
            "Compare synthetic predictions against real event outcomes once testers begin.",
            "Suppress simulation rules that conflict with real user evidence."
        ]
    }
    save_json("adaptive_simulation_evolution_latest.json", payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
