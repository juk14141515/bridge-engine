"""
Bridge Engine Adaptive API Routes

Stable JSON endpoints for the future UI/mobile layer.
V1 exposes read-only adaptive state plus guarded write endpoints for
real events, feedback, and coach conversations.

Register from app.py with:
    from api_routes import register_adaptive_api_routes
    register_adaptive_api_routes(app)
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List

from flask import Response, jsonify, request, stream_with_context

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

EVENTS_JSONL = DATA_DIR / "events.jsonl"
FEEDBACK_JSONL = DATA_DIR / "feedback.jsonl"
COACH_JSONL = DATA_DIR / "coach_conversations.jsonl"
MEMORY_JSONL = DATA_DIR / "semantic_memory_events.jsonl"

ALLOWED_EVENT_TYPES = {
    "app_opened",
    "path_started",
    "started_task",
    "step_completed",
    "overwhelm_reported",
    "completed_recovery",
    "environment_switch",
    "intervention_accepted",
    "intervention_completed",
    "ignored_intervention",
    "recall_answer_submitted",
    "returned_after_abandonment",
    "coach_message_shown",
    "coach_message_helpful",
    "coach_message_unhelpful",
    "ui_panel_opened",
    "focus_lane_started",
    "tiny_win_completed",
}


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


def _save_json(filename: str, payload: Any) -> None:
    (DATA_DIR / filename).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


def _read_jsonl(path: Path, limit: int = 50) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()[-limit:]
    items = []
    for line in lines:
        try:
            items.append(json.loads(line))
        except Exception:
            continue
    return items


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


def _require_api_key(fn):
    """Mobile/API auth shim.

    If BRIDGE_API_KEY is unset, local alpha write endpoints remain open.
    Set BRIDGE_API_KEY before inviting testers.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        expected = os.getenv("BRIDGE_API_KEY", "").strip()
        if not expected:
            return fn(*args, **kwargs)
        provided = request.headers.get("X-Bridge-API-Key", "").strip()
        if provided != expected:
            return jsonify({
                "ok": False,
                "error": "unauthorized",
                "message": "Missing or invalid X-Bridge-API-Key header."
            }), 401
        return fn(*args, **kwargs)
    return wrapper


def _client_user_id() -> str:
    return (
        request.headers.get("X-Bridge-User")
        or request.args.get("user_id")
        or "local_default"
    )


def _safe_payload() -> Dict[str, Any]:
    if not request.is_json:
        return {}
    body = request.get_json(silent=True)
    return body if isinstance(body, dict) else {}


def _event_summary() -> Dict[str, Any]:
    recent = _read_jsonl(EVENTS_JSONL, limit=200)
    counts: Dict[str, int] = {}
    for event in recent:
        kind = event.get("event_type", "unknown")
        counts[kind] = counts.get(kind, 0) + 1
    return {
        "recent_count": len(recent),
        "event_counts": counts,
        "start_events": sum(counts.get(k, 0) for k in ["path_started", "started_task", "focus_lane_started"]),
        "completion_events": sum(counts.get(k, 0) for k in ["step_completed", "intervention_completed", "tiny_win_completed"]),
        "overwhelm_events": counts.get("overwhelm_reported", 0),
        "ignored_intervention_events": counts.get("ignored_intervention", 0),
        "recovery_events": counts.get("completed_recovery", 0) + counts.get("returned_after_abandonment", 0),
    }


def _build_coach_reply(message: str, state: Dict[str, Any]) -> Dict[str, Any]:
    app_state = state.get("app_state", {}) if isinstance(state, dict) else {}
    today = state.get("today", {}) if isinstance(state, dict) else {}
    focus_lane = today.get("focus_lane", {})
    micro_unlocks = focus_lane.get("micro_unlocks", []) if isinstance(focus_lane, dict) else []
    top = micro_unlocks[0] if micro_unlocks else {}

    activation = app_state.get("activation_profile", "unknown")
    failure_mode = app_state.get("primary_failure_mode", "unknown")

    if "overwhelm" in message.lower() or "stuck" in message.lower():
        tone = "recovery"
        reply = "This does not need to become the whole task. Start with one visible proof step, then stop."
    elif "start" in message.lower() or "begin" in message.lower():
        tone = "activation"
        reply = "Your next move should be tiny enough that it feels almost too small to count — but it does count."
    else:
        tone = "coach"
        reply = "I would keep this in Tiny Wins mode and avoid opening the full backlog right now."

    return {
        "reply_id": str(uuid.uuid4()),
        "tone": tone,
        "message": reply,
        "context": {
            "activation_profile": activation,
            "primary_failure_mode": failure_mode,
            "suggested_micro_action": top.get("action"),
            "done_when": top.get("done_when"),
        },
        "safety_note": "Bridge Engine can support execution and learning structure, but it is not medical care or emergency support.",
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
                "live": "/api/live",
                "stream": "/api/live/stream",
                "profile": "/api/profile",
                "memory": "/api/memory",
                "interventions": "/api/interventions",
                "curriculum": "/api/curriculum",
                "mastery": "/api/mastery",
                "recovery": "/api/recovery",
                "coach": "/api/coach",
                "coach_chat": "/api/coach/chat",
                "health": "/api/system-health",
                "events": "/api/events",
                "event_ingest": "/api/events/ingest",
                "feedback_ingest": "/api/feedback",
                "simulations": "/api/simulations",
                "schemas": "/api/schemas",
                "frontend_contract": "/api/frontend-contract",
            },
            "notes": [
                "Frontend should prefer /api/state for the main dashboard.",
                "Use /api/live for polling and /api/live/stream for lightweight Server-Sent Events.",
                "Write endpoints should use X-Bridge-API-Key once BRIDGE_API_KEY is set."
            ]
        })

    @app.get("/api/state")
    def api_state():
        return jsonify(_api_state())

    @app.get("/api/live")
    def api_live():
        state = _api_state()
        health = _load_json("system_health_latest.json", {})
        return jsonify({
            "ok": True,
            "served_at": _now_iso(),
            "state_version": state.get("generated_at") or state.get("served_at"),
            "health_score": health.get("health_score") or state.get("app_state", {}).get("health_score"),
            "focus_lane": state.get("today", {}).get("focus_lane", {}),
            "next_best_items": state.get("today", {}).get("next_best_items", []),
            "top_interventions": state.get("today", {}).get("top_interventions", []),
            "event_summary": _event_summary(),
        })

    @app.get("/api/live/stream")
    def api_live_stream():
        @stream_with_context
        def generate():
            state = _api_state()
            payload = {
                "type": "adaptive_state",
                "served_at": _now_iso(),
                "focus_lane": state.get("today", {}).get("focus_lane", {}),
                "app_state": state.get("app_state", {}),
                "event_summary": _event_summary(),
            }
            yield f"event: adaptive_state\ndata: {json.dumps(payload)}\n\n"
        return Response(generate(), mimetype="text/event-stream")

    @app.get("/api/profile")
    def api_profile():
        return jsonify(_payload("profile", "adaptive_user_profile_latest.json", {}))

    @app.get("/api/memory")
    def api_memory():
        return jsonify({
            **_payload("memory", "semantic_memory_latest.json", {"memories": []}),
            "memory_events": _read_jsonl(MEMORY_JSONL, limit=50),
        })

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
            "recent_conversations": _read_jsonl(COACH_JSONL, limit=20),
        })

    @app.post("/api/coach/chat")
    @_require_api_key
    def api_coach_chat():
        body = _safe_payload()
        message = str(body.get("message", "")).strip()
        if not message:
            return jsonify({"ok": False, "error": "message_required"}), 400
        state = _api_state()
        reply = _build_coach_reply(message, state)
        record = {
            "id": str(uuid.uuid4()),
            "timestamp": _now_iso(),
            "user_id": _client_user_id(),
            "message": message,
            "reply": reply,
            "source": "api_coach_chat",
        }
        _append_jsonl(COACH_JSONL, record)
        _append_jsonl(MEMORY_JSONL, {
            "id": str(uuid.uuid4()),
            "timestamp": _now_iso(),
            "user_id": _client_user_id(),
            "kind": "coach_conversation",
            "summary": message[:240],
            "source": "api_coach_chat",
        })
        return jsonify({"ok": True, "served_at": _now_iso(), "reply": reply})

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
        return jsonify({
            **_payload("events", "events_latest.json", {"recent_events": []}),
            "jsonl_recent": _read_jsonl(EVENTS_JSONL, limit=50),
            "summary": _event_summary(),
        })

    @app.post("/api/events/ingest")
    @_require_api_key
    def api_events_ingest():
        body = _safe_payload()
        event_type = str(body.get("event_type", "")).strip()
        if event_type not in ALLOWED_EVENT_TYPES:
            return jsonify({
                "ok": False,
                "error": "invalid_event_type",
                "allowed_event_types": sorted(ALLOWED_EVENT_TYPES),
            }), 400
        event = {
            "id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": body.get("timestamp") or _now_iso(),
            "user_id": body.get("user_id") or _client_user_id(),
            "source": body.get("source") or "api",
            "payload": body.get("payload") if isinstance(body.get("payload"), dict) else {},
            "synthetic": bool(body.get("synthetic", False)),
        }
        _append_jsonl(EVENTS_JSONL, event)
        _save_json("events_api_latest.json", {
            "ok": True,
            "generated_at": _now_iso(),
            "latest_event": event,
            "summary": _event_summary(),
        })
        return jsonify({"ok": True, "event": event, "summary": _event_summary()}), 201

    @app.post("/api/feedback")
    @_require_api_key
    def api_feedback():
        body = _safe_payload()
        feedback_type = str(body.get("feedback_type", "")).strip() or "general_feedback"
        record = {
            "id": str(uuid.uuid4()),
            "timestamp": _now_iso(),
            "user_id": body.get("user_id") or _client_user_id(),
            "feedback_type": feedback_type,
            "target_type": body.get("target_type"),
            "target_id": body.get("target_id"),
            "rating": body.get("rating"),
            "comment": body.get("comment", ""),
            "payload": body.get("payload") if isinstance(body.get("payload"), dict) else {},
        }
        _append_jsonl(FEEDBACK_JSONL, record)
        if feedback_type in {"helpful", "worked", "too_hard", "too_easy", "overwhelming", "not_relevant"}:
            _append_jsonl(EVENTS_JSONL, {
                "id": str(uuid.uuid4()),
                "event_type": "coach_message_helpful" if feedback_type in {"helpful", "worked"} else "ignored_intervention",
                "timestamp": _now_iso(),
                "user_id": record["user_id"],
                "source": "api_feedback",
                "payload": record,
                "synthetic": False,
            })
        return jsonify({"ok": True, "feedback": record}), 201

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
            "event_schema": {
                "event_type": sorted(ALLOWED_EVENT_TYPES),
                "minimum_fields": ["event_type", "payload"],
                "auth_header_when_enabled": "X-Bridge-API-Key",
            },
            "feedback_schema": {
                "feedback_type": ["helpful", "worked", "too_hard", "too_easy", "overwhelming", "not_relevant", "general_feedback"],
                "minimum_fields": ["feedback_type"],
            },
            "coach_chat_schema": {
                "minimum_fields": ["message"],
                "returns": ["reply", "context", "safety_note"],
            },
            "route_contract": {
                "primary_dashboard_source": "/api/state",
                "live_polling_source": "/api/live",
                "sse_source": "/api/live/stream",
                "read_only_v1": False,
                "write_endpoints": [
                    "/api/events/ingest",
                    "/api/feedback",
                    "/api/coach/chat"
                ]
            }
        })

    @app.get("/api/frontend-contract")
    def api_frontend_contract():
        return jsonify({
            "ok": True,
            "served_at": _now_iso(),
            "recommended_frontend_flow": [
                "Fetch /api/state on initial load.",
                "Render Tiny Wins Lane before full curriculum.",
                "Poll /api/live every 15-30 seconds for alpha UI.",
                "Send real user actions to /api/events/ingest.",
                "Send helpful/not helpful signals to /api/feedback.",
                "Use /api/coach/chat for lightweight coach interactions.",
                "Do not show the full blocked graph by default for high-friction users."
            ],
            "core_panels": {
                "hero": "app_state + today.focus_lane",
                "next_action": "today.next_best_items[0]",
                "interventions": "today.top_interventions",
                "memory": "today.coach_memories",
                "mastery": "/api/mastery",
                "health": "/api/system-health",
                "events": "/api/events",
            },
            "ux_rules": [
                "Show one next action first.",
                "Use low-shame language.",
                "Prefer proof over passive watching.",
                "Make every primary CTA create visible evidence.",
                "Keep recovery mode visually calm and uncluttered."
            ]
        })

    return app
