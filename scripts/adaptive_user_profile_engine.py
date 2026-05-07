"""
Adaptive User Profile Engine

Builds a living user profile from events, path behavior, context intelligence,
and reward-loop outputs. Designed to eventually become the user's execution fingerprint.
"""

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def save_json(path, payload):
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def infer_profile():
    paths = load_json(DATA_DIR / "bridge_paths.json", [])
    context = load_json(DATA_DIR / "context_intelligence_latest.json", {})
    reward = load_json(DATA_DIR / "reward_loop_latest.json", {})
    smart_filters = load_json(DATA_DIR / "smart_path_filter_latest.json", {})

    interests = Counter()
    learning_goals = Counter()
    completed_steps = 0
    total_steps = 0

    for path in paths:
        if path.get("interest"):
            interests[path.get("interest")] += 1
        if path.get("learning_goal"):
            learning_goals[path.get("learning_goal")] += 1
        for step in path.get("steps", []):
            total_steps += 1
            if step.get("status") == "done":
                completed_steps += 1

    completion_rate = round((completed_steps / total_steps) * 100, 2) if total_steps else 0
    context_rec = context.get("recommendation", {}) if isinstance(context, dict) else {}

    filters = smart_filters.get("filters", []) if isinstance(smart_filters, dict) else []
    feature_counts = Counter()
    modality_counts = Counter()
    for item in filters:
        for feature in item.get("required_features", []):
            feature_counts[feature] += 1
        if item.get("best_modality"):
            modality_counts[item.get("best_modality")] += 1

    profile = {
        "generated_at": now_iso(),
        "user_id": "local_default",
        "profile_stage": "prototype_single_user",
        "interests_detected": interests.most_common(10),
        "learning_goals_detected": learning_goals.most_common(10),
        "completion_rate": completion_rate,
        "activation_profile": "micro_start_needed" if completion_rate < 25 else "standard_start_ok",
        "preferred_context_guess": {
            "time_of_day": context_rec.get("best_time_of_day", "unknown"),
            "environment": context_rec.get("best_environment", "unknown"),
            "energy_mode": context_rec.get("best_energy_mode", "focused"),
            "session_length": context_rec.get("best_session_length", "medium"),
        },
        "reward_profile": {
            "style": reward.get("reward_style", "restart_friction_reducer") if isinstance(reward, dict) else "restart_friction_reducer",
            "task_size": reward.get("task_size", "tiny") if isinstance(reward, dict) else "tiny",
        },
        "likely_effective_features": feature_counts.most_common(10),
        "likely_effective_modalities": modality_counts.most_common(10),
        "rules": [
            "Default to a 2-5 minute first action when completion history is low.",
            "Prefer visible artifacts and clear checkpoints.",
            "Use recovery-first language for abandoned or stalled work.",
            "Adapt modality based on observed completions, not only onboarding answers."
        ]
    }
    return profile


def main():
    profile = infer_profile()
    save_json(DATA_DIR / "adaptive_user_profile_latest.json", profile)
    print(json.dumps({"ok": True, "profile": profile}, indent=2))


if __name__ == "__main__":
    main()
