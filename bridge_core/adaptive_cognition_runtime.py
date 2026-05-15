"""Orchestrates memory, momentum, rotation, friction, and immersion."""

from __future__ import annotations

from typing import Any, Dict, Optional

from bridge_core.friction_detection import detect_friction
from bridge_core.immersion_runtime import build_immersion_state
from bridge_core.interaction_rotation import select_interaction
from bridge_core.momentum_engine import compute_adaptive_momentum
from bridge_core.runtime_memory import build_runtime_profile, update_runtime_memory


def apply_adaptive_cognition(
    workspace: Dict[str, Any],
    *,
    event: Optional[Dict[str, Any]] = None,
    user_output: str = "",
) -> Dict[str, Any]:
    """Update workspace memory and return frontend-safe adaptive layers."""
    evt = dict(event or {})
    if user_output and not evt.get("user_output"):
        evt["user_output"] = user_output
    if evt:
        update_runtime_memory(workspace, evt)

    profile = build_runtime_profile(workspace)
    friction_state = detect_friction(workspace, user_output=user_output)
    momentum_state = compute_adaptive_momentum(
        workspace,
        profile=profile,
        friction_state=friction_state,
    )
    interaction_rotation = select_interaction(workspace, profile, momentum_state)
    immersion_state = build_immersion_state(workspace, profile, frame=workspace.get("frame"))

    adaptive_pacing = {
        "pace_modifier": momentum_state.get("pace_modifier", 1.0),
        "step_size": _step_size(momentum_state),
        "session_length": _session_length(momentum_state),
        "reflection_frequency": momentum_state.get("reflection_frequency", "normal"),
    }

    reward_state = _reward_state(workspace, momentum_state, friction_state)
    identity_state = {
        "frame": workspace.get("frame"),
        "tone": immersion_state.get("tone", "calm"),
        "reinforcement": immersion_state.get("identity_reinforcement"),
        "mission": immersion_state.get("mission_continuity"),
    }

    workspace["runtime_profile"] = profile
    runtime_state = workspace.setdefault("runtime_state", {})
    runtime_state["adaptive_pacing"] = adaptive_pacing
    runtime_state["last_interaction"] = interaction_rotation.get("current")
    runtime_state["friction_level"] = friction_state.get("friction_level")
    runtime_state["high_friction"] = friction_state.get("friction_level", 0) >= 0.55
    runtime_state["high_momentum"] = momentum_state.get("mode") in ("high_momentum", "deep_engagement")

    return {
        "runtime_memory": workspace.get("runtime_memory", {}),
        "runtime_profile": profile,
        "friction_state": friction_state,
        "momentum_state": momentum_state,
        "interaction_rotation": interaction_rotation,
        "immersion_state": immersion_state,
        "adaptive_pacing": adaptive_pacing,
        "reward_state": reward_state,
        "identity_state": identity_state,
    }


def _step_size(momentum: Dict[str, Any]) -> str:
    level = momentum.get("challenge_level", "medium")
    if level == "low":
        return "tiny"
    if level == "high":
        return "standard"
    return "small"


def _session_length(momentum: Dict[str, Any]) -> str:
    density = momentum.get("interaction_density", "medium")
    if density == "low":
        return "short"
    if density == "high":
        return "extended"
    return "medium"


def _reward_state(
    workspace: Dict[str, Any],
    momentum: Dict[str, Any],
    friction: Dict[str, Any],
) -> Dict[str, Any]:
    memory = workspace.get("runtime_memory") or {}
    freq = momentum.get("reward_frequency", "normal")
    return {
        "frequency": freq,
        "ready": friction.get("friction_level", 0) < 0.5 or freq == "high",
        "message": _reward_message(freq, memory),
        "streak": int(memory.get("continue_count", 0)),
    }


def _reward_message(freq: str, memory: Dict[str, Any]) -> str:
    streak = int(memory.get("continue_count", 0))
    if freq == "high":
        return "Small win unlocked — momentum is building."
    if streak >= 3:
        return "Steady progress — your thread is holding."
    return "Progress saved."
