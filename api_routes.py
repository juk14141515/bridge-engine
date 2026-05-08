"""
Bridge Engine Adaptive API Routes

Stable JSON endpoints for the future UI/mobile layer.
This module is intentionally read-only for now: it exposes current backend
state from data/*.json without changing user state.

Register from app.py with:
    from api_routes import register_adaptive_api_routes
    register_adaptive_api_routes(app)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from flask import jsonify

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(filename: str, default: Any = None) -> Any:
    path = DATA_DIR / filename
    if default is None:
        default = {}
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "ok": False,
            "error": f"failed_to_read_{filename}",
            "detail": str(exc),
            "filename": filename,
        }
    return default


def _payload(name: str, filename: str, default: Any = None) -> Dict[str, Any]:
    data = _load_json(filename, default if default is not None else {})
    return {
        "ok": True,
        "endpoint": f"/api/{name}",
        "source_file": filename,
        "served_at": _now_iso(),
        "data": data,
    }


def _api_state() -> Dict[str, Any]:
    state = _load_json("api_state_latest.json", {})
    if state:
        return state
    return {
        "ok": False,
        "message": "api_state_latest.json has not been generated yet. Run scripts/schema_normalization_engine.py or scripts/pipeline_runner.py.",
        "served_at": _now_iso(),
    }


def register_adaptive_api_routes(app):
    """Attach stable adaptive API endpoints to a Flask app."""

    @app.get("/api")
    def api_index():
        return jsonify({
            "ok": True,
            "name": "Bridge Engine Adaptive API",
            "served_at": _now_iso(),
            "routes": {
                "state": "/api/state",
                "profile": "/api/profile",
                "memory": "/api/memory",
                "interventions": "/api/interventions",
                "curriculum": "/api/curriculum",
                "mastery": "/api/mastery",
                "recovery": "/api/recovery",
                "coach": "/api/coach",
                "health": "/api/system-health",
                "events": "/api/events",
                "simulations": "/api/simulations",
                "schemas": "/api/schemas",
            },
            "notes": [
                "Read-only JSON endpoints for the UI layer.",
                "Frontend should prefer /api/state for the main dashboard.",
                "Individual endpoints exist for focused UI panels."
            ]
        })

    @app.get("/api/state")
    def api_state():
        return jsonify(_api_state())

    @app.get("/api/profile")
    def api_profile():
        return jsonify(_payload("profile", "adaptive_user_profile_latest.json", {}))

    @app.get("/api/memory")
    def api_memory():
        return jsonify(_payload("memory", "semantic_memory_latest.json", {"memories": []}))

    @app.get("/api/interventions")
    def api_interventions():
        return jsonify(_payload("interventions", "execution_reinforcement_latest.json", {"recommended_interventions": []}))

    @app.get("/api/curriculum")
    def api_curriculum():
        return jsonify({
            "ok": True,
            "served_at": _now_iso(),
            "sequence": _load_json("curriculum_sequence_latest.json", {}),
            "simplification": _load_json("curriculum_simplification_latest.json", {}),
            "prerequisites": _load_json("prerequisite_graph_latest.json", {}),
            "ontology": _load_json("educational_ontology_latest.json", {}),
        })

    @app.get("/api/mastery")
    def api_mastery():
        return jsonify({
            "ok": True,
            "served_at": _now_iso(),
            "mastery": _load_json("mastery_tracking_latest.json", {}),
            "reviews": _load_json("spaced_review_latest.json", {}),
            "knowledge_checks": _load_json("knowledge_checks_latest.json", {}),
            "recall_evidence": _load_json("recall_evidence_latest.json", {}),
            "misconceptions": _load_json("misconception_detection_latest.json", {}),
        })

    @app.get("/api/recovery")
    def api_recovery():
        state = _api_state()
        return jsonify({
            "ok": True,
            "served_at": _now_iso(),
            "focus_lane": state.get("today", {}).get("focus_lane", {}),
            "top_interventions": state.get("today", {}).get("top_interventions", []),
            "activation_profile": state.get("app_state", {}).get("activation_profile"),
            "primary_failure_mode": state.get("app_state", {}).get("primary_failure_mode"),
        })

    @app.get("/api/coach")
    def api_coach():
        state = _api_state()
        return jsonify({
            "ok": True,
            "served_at": _now_iso(),
            "coach_memories": state.get("today", {}).get("coach_memories", []),
            "next_best_items": state.get("today", {}).get("next_best_items", []),
            "top_interventions": state.get("today", {}).get("top_interventions", []),
            "memory": _load_json("semantic_memory_latest.json", {}),
            "coach_cards": _load_json("ai_coach_cards_latest.json", {}),
        })

    @app.get("/api/system-health")
    def api_system_health():
        return jsonify({
            "ok": True,
            "served_at": _now_iso(),
            "health": _load_json("system_health_latest.json", {}),
            "pipeline": _load_json("pipeline_latest.json", {}),
            "registry": _load_json("engine_registry.json", {}),
        })

    @app.get("/api/events")
    def api_events():
        return jsonify(_payload("events", "events_latest.json", {"recent_events": []}))

    @app.get("/api/simulations")
    def api_simulations():
        return jsonify({
            "ok": True,
            "served_at": _now_iso(),
            "adaptive_simulation_evolution": _load_json("adaptive_simulation_evolution_latest.json", {}),
            "smart_path_filters": _load_json("smart_path_filter_latest.json", {}),
            "complex_path_filter": _load_json("complex_path_filter_latest.json", {}),
        })

    @app.get("/api/schemas")
    def api_schemas():
        return jsonify({
            "ok": True,
            "served_at": _now_iso(),
            "api_state_schema": _load_json("api_state_latest.json", {}).get("schema_version"),
            "assignment_intake_schema": _load_json("assignment_intake_schema.json", {}),
            "event_schema": _load_json("events_latest.json", {}).get("schema", {}),
            "route_contract": {
                "primary_dashboard_source": "/api/state",
                "read_only_v1": True,
                "write_endpoints_planned": [
                    "/api/events/ingest",
                    "/api/assignment/parse",
                    "/api/coach/feedback"
                ]
            }
        })

    return app
