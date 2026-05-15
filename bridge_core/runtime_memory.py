"""Runtime memory — per-workspace engagement and preference signals."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional

DEFAULT_MEMORY: Dict[str, Any] = {
    "pause_count": 0,
    "skipped_steps": 0,
    "rewrite_count": 0,
    "mode_switches": 0,
    "challenge_completions": 0,
    "challenge_attempts": 0,
    "session_returns": 0,
    "continue_count": 0,
    "short_response_count": 0,
    "frustration_signals": 0,
    "successful_reframes": 0,
    "abandonment_points": [],
    "interaction_history": [],
    "preferred_interactions": {},
    "preferred_tone": "calm",
    "preferred_complexity": "medium",
    "last_interaction": None,
    "last_output_length": 0,
    "updated_at": None,
}


def _utc_now() -> str:
    return datetime.utcnow().isoformat()


def _ensure_memory(workspace: Dict[str, Any]) -> Dict[str, Any]:
    memory = workspace.get("runtime_memory")
    if not isinstance(memory, dict):
        memory = deepcopy(DEFAULT_MEMORY)
    else:
        merged = deepcopy(DEFAULT_MEMORY)
        merged.update(memory)
        memory = merged
    workspace["runtime_memory"] = memory
    return memory


def update_runtime_memory(
    workspace: Dict[str, Any],
    event: Dict[str, Any],
) -> Dict[str, Any]:
    """Record a runtime event and mutate workspace.runtime_memory in place."""
    memory = _ensure_memory(workspace)
    event_type = str(event.get("type") or "refresh")
    output = str(event.get("user_output") or "")
    output_len = len(output.strip())
    words = len(output.split())

    memory["updated_at"] = _utc_now()

    if event_type == "session_return":
        memory["session_returns"] = int(memory.get("session_returns", 0)) + 1

    if event_type == "pause":
        memory["pause_count"] = int(memory.get("pause_count", 0)) + 1

    if event_type == "skip_step":
        memory["skipped_steps"] = int(memory.get("skipped_steps", 0)) + 1
        idx = event.get("step_index")
        if idx is not None:
            points: List[Any] = list(memory.get("abandonment_points") or [])
            if idx not in points:
                points.append(idx)
            memory["abandonment_points"] = points[-12:]

    if event_type == "rewrite":
        memory["rewrite_count"] = int(memory.get("rewrite_count", 0)) + 1
        if event.get("successful"):
            memory["successful_reframes"] = int(memory.get("successful_reframes", 0)) + 1

    if event_type == "mode_switch":
        memory["mode_switches"] = int(memory.get("mode_switches", 0)) + 1

    if event_type == "challenge_complete":
        memory["challenge_completions"] = int(memory.get("challenge_completions", 0)) + 1
        memory["challenge_attempts"] = int(memory.get("challenge_attempts", 0)) + 1
    elif event_type == "challenge_attempt":
        memory["challenge_attempts"] = int(memory.get("challenge_attempts", 0)) + 1

    if event_type in ("continue", "create"):
        if event_type == "continue":
            memory["continue_count"] = int(memory.get("continue_count", 0)) + 1
        if output_len > 0:
            if words <= 2 or output_len < 12:
                memory["short_response_count"] = int(memory.get("short_response_count", 0)) + 1
            lowered = output.lower()
            if any(tok in lowered for tok in ("idk", "dunno", "stuck", "boring", "hate", "can't")):
                memory["frustration_signals"] = int(memory.get("frustration_signals", 0)) + 1

    interaction = event.get("interaction_type")
    if interaction:
        history: List[str] = list(memory.get("interaction_history") or [])
        history.append(str(interaction))
        memory["interaction_history"] = history[-24:]
        memory["last_interaction"] = str(interaction)
        prefs = dict(memory.get("preferred_interactions") or {})
        prefs[str(interaction)] = int(prefs.get(str(interaction), 0)) + 1
        memory["preferred_interactions"] = prefs

    memory["last_output_length"] = output_len

    supports = workspace.get("supports") or []
    if "professional" in supports:
        memory["preferred_tone"] = "professional"
    elif memory.get("frustration_signals", 0) >= 2:
        memory["preferred_tone"] = "gentle"
    else:
        memory["preferred_tone"] = "calm"

    rewrites = int(memory.get("rewrite_count", 0))
    shorts = int(memory.get("short_response_count", 0))
    continues = max(1, int(memory.get("continue_count", 0)))
    if rewrites >= 2 or shorts / continues > 0.5:
        memory["preferred_complexity"] = "low"
    elif memory.get("challenge_completions", 0) >= 2 and shorts <= 1:
        memory["preferred_complexity"] = "high"
    else:
        memory["preferred_complexity"] = "medium"

    workspace["runtime_memory"] = memory
    return memory


def build_runtime_profile(workspace: Dict[str, Any]) -> Dict[str, Any]:
    """Derive a stable profile snapshot from accumulated runtime memory."""
    memory = _ensure_memory(workspace)
    continues = max(1, int(memory.get("continue_count", 0)))
    attempts = max(1, int(memory.get("challenge_attempts", 0)))
    prefs = memory.get("preferred_interactions") or {}
    dominant = None
    if prefs:
        dominant = max(prefs.items(), key=lambda item: item[1])[0]

    return {
        "engagement_pattern": _engagement_pattern(memory, continues),
        "preferred_interaction_modes": _top_preferences(prefs, 4),
        "dominant_interaction_type": dominant,
        "pacing_tolerance": _pacing_tolerance(memory),
        "abandonment_risk": len(memory.get("abandonment_points") or []) >= 2,
        "successful_reframe_rate": round(
            int(memory.get("successful_reframes", 0)) / max(1, int(memory.get("rewrite_count", 0))),
            2,
        ),
        "emotional_resistance": _resistance_level(memory, continues),
        "preferred_complexity": memory.get("preferred_complexity", "medium"),
        "preferred_tone": memory.get("preferred_tone", "calm"),
        "challenge_completion_rate": round(
            int(memory.get("challenge_completions", 0)) / attempts,
            2,
        ),
        "session_return_frequency": int(memory.get("session_returns", 0)),
    }


def _engagement_pattern(memory: Dict[str, Any], continues: int) -> str:
    shorts = int(memory.get("short_response_count", 0))
    if shorts / continues > 0.6:
        return "shallow"
    if int(memory.get("challenge_completions", 0)) >= 2 and shorts <= 1:
        return "deep"
    if int(memory.get("rewrite_count", 0)) >= 2:
        return "resistant"
    return "steady"


def _pacing_tolerance(memory: Dict[str, Any]) -> str:
    if int(memory.get("pause_count", 0)) >= 2 or int(memory.get("skipped_steps", 0)) >= 1:
        return "slow"
    if int(memory.get("continue_count", 0)) >= 4 and int(memory.get("short_response_count", 0)) <= 1:
        return "fast"
    return "moderate"


def _resistance_level(memory: Dict[str, Any], continues: int) -> str:
    score = int(memory.get("frustration_signals", 0)) + int(memory.get("rewrite_count", 0))
    if score >= 4 or int(memory.get("short_response_count", 0)) / continues > 0.5:
        return "high"
    if score >= 2:
        return "moderate"
    return "low"


def _top_preferences(prefs: Dict[str, Any], limit: int) -> List[str]:
    if not prefs:
        return []
    ordered = sorted(prefs.items(), key=lambda item: item[1], reverse=True)
    return [name for name, _ in ordered[:limit]]
