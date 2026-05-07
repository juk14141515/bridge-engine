"""
Recommendation API Engine

Generates stable JSON payloads that Flask/Codex UI can expose as API routes later.
This is not a live route yet; it creates API-ready data files.
"""

import json
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


def priority_score(item):
    priority = item.get("priority", "low")
    return {"high": 100, "medium": 60, "low": 25}.get(priority, 10)


def main():
    coach = load_json("ai_coach_cards_latest.json", {"cards": []})
    resources = load_json("resource_intelligence_latest.json", {"resources": []})
    profile = load_json("adaptive_user_profile_latest.json", {})
    backend = load_json("adaptive_backend_brain_latest.json", {})
    assignment = load_json("assignment_parser_latest.json", {})

    cards = coach.get("cards", []) if isinstance(coach, dict) else []
    cards = sorted(cards, key=priority_score, reverse=True)
    top_resources = resources.get("resources", [])[:5] if isinstance(resources, dict) else []

    best_next_action = None
    if cards:
        first = cards[0]
        best_next_action = {
            "title": first.get("title"),
            "message": first.get("message"),
            "action": first.get("suggested_action", "Start with a 2-5 minute visible step."),
            "mode": first.get("mode", "guided_progress"),
        }
    else:
        best_next_action = {
            "title": "Create one visible win",
            "message": "Start with the smallest action that produces visible progress.",
            "action": "Do a 3-minute micro-start.",
            "mode": "micro_start",
        }

    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "api_version": 1,
        "best_next_action": best_next_action,
        "coach_cards": cards,
        "recommended_resources": top_resources,
        "profile_summary": {
            "activation_profile": profile.get("activation_profile"),
            "preferred_context_guess": profile.get("preferred_context_guess"),
            "reward_profile": profile.get("reward_profile"),
        },
        "path_strategy": {
            "best_default_features": backend.get("best_default_features", []),
            "promoted": backend.get("promoted"),
            "suppressed": backend.get("suppressed"),
        },
        "assignment_summary": {
            "assignment_type": assignment.get("assignment_type"),
            "risk_flags": assignment.get("risk_flags", []),
            "recommended_first_action": assignment.get("recommended_first_action"),
        },
        "future_flask_routes": [
            "/api/coach",
            "/api/recommendations",
            "/api/profile",
            "/api/resources",
            "/api/assignment/latest"
        ]
    }

    (DATA_DIR / "recommendation_api_latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
