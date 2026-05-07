"""
Coach Memory Engine

Creates a lightweight memory/context layer for the AI Coach.
This stores recurring insights, user patterns, and coach tone rules in JSON.
Future versions can move this into SQLite/Postgres + embeddings.
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


def main():
    profile = load_json("adaptive_user_profile_latest.json", {})
    backend = load_json("adaptive_backend_brain_latest.json", {})
    recommendation = load_json("recommendation_api_latest.json", {})
    assignment = load_json("assignment_parser_latest.json", {})
    smart_filters = load_json("smart_path_filter_latest.json", {})

    memory_items = []

    activation_profile = profile.get("activation_profile")
    if activation_profile:
        memory_items.append({
            "type": "activation_pattern",
            "memory": f"User appears to match activation profile: {activation_profile}.",
            "coach_use": "Shrink first steps and reduce vague instructions when activation is low."
        })

    preferred_context = profile.get("preferred_context_guess", {}) if isinstance(profile, dict) else {}
    if preferred_context:
        memory_items.append({
            "type": "context_pattern",
            "memory": f"Preferred context guess: {preferred_context}.",
            "coach_use": "Recommend sessions that match likely best time/environment when possible."
        })

    features = backend.get("best_default_features", []) if isinstance(backend, dict) else []
    if features:
        memory_items.append({
            "type": "effective_features",
            "memory": "Effective defaults currently include: " + ", ".join(features[:8]),
            "coach_use": "Use these as default structure when generating coach guidance."
        })

    assignment_risks = assignment.get("risk_flags", []) if isinstance(assignment, dict) else []
    if assignment_risks:
        memory_items.append({
            "type": "assignment_risk",
            "memory": "Latest assignment risk flags: " + ", ".join(assignment_risks),
            "coach_use": "Prioritize clarity, micro-starts, and recovery buffers."
        })

    filters = smart_filters.get("filters", []) if isinstance(smart_filters, dict) else []
    top_actions = Counter(item.get("action") for item in filters if item.get("action"))
    if top_actions:
        memory_items.append({
            "type": "simulated_path_pattern",
            "memory": "Common simulated path actions: " + ", ".join([f"{k}:{v}" for k, v in top_actions.most_common(5)]),
            "coach_use": "Use simulation patterns as weak hints, never as real-user proof."
        })

    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "memory_items": memory_items,
        "coach_tone_rules": [
            "Use calm, non-shaming language.",
            "Recommend the smallest useful start when resistance is high.",
            "Prefer visible progress over abstract advice.",
            "Avoid guilt, punishment, or manipulative urgency.",
            "Encourage agency: user can always choose easier, harder, or different mode."
        ],
        "coach_prompt_scaffold": {
            "role": "Adaptive execution coach",
            "goal": "Help the user start, recover momentum, and complete meaningful work with low shame and high clarity.",
            "avoid": ["medical claims", "therapy replacement", "guilt language", "infinite engagement loops"]
        }
    }

    save_json("coach_memory_latest.json", payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
