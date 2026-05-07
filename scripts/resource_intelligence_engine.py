"""
Resource Intelligence Engine

Ranks learning resources by user style, modality, activation cost, and likely usefulness.
This does not scrape the web yet; it creates a curated/local resource scoring layer
that can later be connected to YouTube, podcasts, articles, course pages, etc.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

RESOURCE_LIBRARY = [
    {
        "id": "web_design_build_card",
        "topic": "web_design",
        "title": "Build a profile card before learning full HTML/CSS",
        "type": "hands_on_project",
        "modality": "hands_on",
        "activation_cost": "low",
        "best_for": ["adhd_overwhelmed_student", "visual_project_learner"],
        "features": ["visible_artifact", "micro_start", "project_first", "low_text"],
    },
    {
        "id": "filmmaking_15_second_scene",
        "topic": "filmmaking",
        "title": "Shoot a 15-second scene with one emotion",
        "type": "micro_project",
        "modality": "visual",
        "activation_cost": "low",
        "best_for": ["creative_project_user", "burnout_recovery_user"],
        "features": ["visible_artifact", "phone_only_mode", "micro_start", "project_first"],
    },
    {
        "id": "assignment_bad_first_draft",
        "topic": "school_assignment",
        "title": "Create a bad first draft before trying to make it good",
        "type": "execution_strategy",
        "modality": "writing",
        "activation_cost": "low",
        "best_for": ["adhd_student", "school_avoidant_learner"],
        "features": ["recovery_mode", "low_text", "clear_checkpoint", "finish_support"],
    },
    {
        "id": "audio_walk_reflection",
        "topic": "general_learning",
        "title": "Walk and record a 60-second voice note explaining the task",
        "type": "movement_audio",
        "modality": "audio_walking",
        "activation_cost": "low",
        "best_for": ["audio_walking_learner", "low_energy_user"],
        "features": ["walking_mode", "audio_mode", "recovery_mode", "low_text"],
    },
    {
        "id": "expected_value_trade_table",
        "topic": "investing_probability",
        "title": "Make a 5-row expected value table for trades",
        "type": "applied_math_project",
        "modality": "hands_on",
        "activation_cost": "medium",
        "best_for": ["project_based_learner", "night_hyperfocus_builder"],
        "features": ["project_first", "visible_artifact", "clear_checkpoint", "challenge_mode"],
    },
]


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def score_resource(resource, profile, backend_brain):
    score = 50
    likely_features = [item[0] if isinstance(item, list) else item for item in profile.get("likely_effective_features", [])]
    likely_modalities = [item[0] if isinstance(item, list) else item for item in profile.get("likely_effective_modalities", [])]
    best_defaults = backend_brain.get("best_default_features", []) if isinstance(backend_brain, dict) else []

    for feature in resource.get("features", []):
        if feature in likely_features:
            score += 8
        if feature in best_defaults:
            score += 5

    if resource.get("modality") in likely_modalities:
        score += 10
    if resource.get("activation_cost") == "low":
        score += 10
    if profile.get("activation_profile") == "micro_start_needed" and "micro_start" in resource.get("features", []):
        score += 12

    return min(score, 100)


def main():
    profile = load_json(DATA_DIR / "adaptive_user_profile_latest.json", {})
    backend_brain = load_json(DATA_DIR / "adaptive_backend_brain_latest.json", {})

    ranked = []
    for resource in RESOURCE_LIBRARY:
        item = dict(resource)
        item["score"] = score_resource(resource, profile, backend_brain)
        item["reason"] = "Matched against current profile, modality patterns, activation cost, and backend-promoted features."
        ranked.append(item)

    ranked.sort(key=lambda item: item["score"], reverse=True)
    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "synthetic_or_curated": True,
        "resources": ranked,
        "next_steps": [
            "Connect this to real YouTube/Spotify/article ingestion later.",
            "Track resource_clicked and resource_helpful events.",
            "Suppress resources that repeatedly cause overwhelm or abandonment."
        ]
    }
    (DATA_DIR / "resource_intelligence_latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
