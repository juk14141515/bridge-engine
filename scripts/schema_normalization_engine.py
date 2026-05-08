"""
Schema Normalization Engine

Creates a UI/API-ready normalized snapshot across Bridge Engine outputs.
This gives Codex/frontend a stable contract instead of forcing the UI to read
many unrelated JSON files directly.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

SOURCE_FILES = {
    "profile": "adaptive_user_profile_latest.json",
    "memory": "semantic_memory_latest.json",
    "interventions": "execution_reinforcement_latest.json",
    "curriculum": "curriculum_sequence_latest.json",
    "curriculum_simplified": "curriculum_simplification_latest.json",
    "mastery": "mastery_tracking_latest.json",
    "concepts": "concept_extraction_latest.json",
    "ontology": "educational_ontology_latest.json",
    "prerequisites": "prerequisite_graph_latest.json",
    "misconceptions": "misconception_detection_latest.json",
    "events": "events_latest.json",
    "simulations": "adaptive_simulation_evolution_latest.json",
    "recommendations": "recommendation_api_latest.json",
    "health": "system_health_latest.json",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_json(filename, default=None):
    path = DATA_DIR / filename
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"ok": False, "error": str(exc), "file": filename}
    return default if default is not None else {"ok": False, "missing": True, "file": filename}


def save_json(filename, payload):
    (DATA_DIR / filename).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main():
    sources = {key: load_json(filename) for key, filename in SOURCE_FILES.items()}

    profile_raw = sources["profile"]
    profile = profile_raw.get("profile", profile_raw) if isinstance(profile_raw, dict) else {}
    health = sources["health"] if isinstance(sources["health"], dict) else {}
    simplified = sources["curriculum_simplified"] if isinstance(sources["curriculum_simplified"], dict) else {}
    curriculum = sources["curriculum"] if isinstance(sources["curriculum"], dict) else {}
    execution = sources["interventions"] if isinstance(sources["interventions"], dict) else {}
    memory = sources["memory"] if isinstance(sources["memory"], dict) else {}
    events = sources["events"] if isinstance(sources["events"], dict) else {}

    normalized = {
        "ok": True,
        "generated_at": now_iso(),
        "schema_version": "2026-05-bridge-engine-v1",
        "app_state": {
            "health_score": health.get("health_score"),
            "health_status": health.get("status"),
            "activation_profile": profile.get("activation_profile"),
            "primary_failure_mode": execution.get("classification", {}).get("primary_failure_mode"),
            "knowledge_risk": execution.get("classification", {}).get("knowledge_risk"),
            "activation_risk": execution.get("classification", {}).get("activation_risk"),
        },
        "today": {
            "focus_lane": simplified.get("focus_lane", {}),
            "next_best_items": curriculum.get("next_best_items", [])[:6],
            "top_interventions": execution.get("recommended_interventions", [])[:5],
            "coach_memories": memory.get("memories", [])[:8],
        },
        "learning": {
            "mastery_items": sources["mastery"].get("mastery_items", []) if isinstance(sources["mastery"], dict) else [],
            "concept_domains": sources["ontology"].get("concept_domains", {}) if isinstance(sources["ontology"], dict) else {},
            "misconceptions": sources["misconceptions"].get("misconceptions", []) if isinstance(sources["misconceptions"], dict) else [],
            "prerequisite_nodes": sources["prerequisites"].get("nodes", []) if isinstance(sources["prerequisites"], dict) else [],
        },
        "behavior": {
            "event_signals": events.get("behavior_signals", {}),
            "recent_events": events.get("recent_events", [])[-20:],
            "simulation_summary": {
                "avg_success_score": sources["simulations"].get("avg_success_score") if isinstance(sources["simulations"], dict) else None,
                "evolved_rules": sources["simulations"].get("evolved_rules", []) if isinstance(sources["simulations"], dict) else [],
            },
        },
        "api_routes": [
            "/api/profile", "/api/memory", "/api/interventions", "/api/curriculum", "/api/mastery",
            "/api/recovery", "/api/coach", "/api/system-health", "/api/events", "/api/simulations", "/api/state"
        ],
        "ui_contract_notes": [
            "Render today.focus_lane before full curriculum for high-friction users.",
            "Do not expose full blocked graphs by default.",
            "Every completion should ask for active evidence, not passive consumption.",
            "Use app_state.health_status to warn admins before UI rollout."
        ],
    }

    save_json("api_state_latest.json", normalized)
    save_json("schema_normalization_latest.json", {
        "ok": True,
        "generated_at": now_iso(),
        "normalized_output": "api_state_latest.json",
        "source_files": SOURCE_FILES,
        "schema_version": normalized["schema_version"],
    })
    print(json.dumps(normalized, indent=2))


if __name__ == "__main__":
    main()
