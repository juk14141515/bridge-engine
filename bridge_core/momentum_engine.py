"""Adaptive difficulty and momentum engine."""

from __future__ import annotations

from typing import Any, Dict, Optional


class MomentumEngine:
    """Legacy score helper — prefer compute_adaptive_momentum for contracts."""

    def calculate(self, signals: Dict) -> Dict:
        state = compute_adaptive_momentum(
            {"runtime_state": signals, "supports": []},
            profile={},
            friction_state={"friction_level": 0.5 if signals.get("frustrated") else 0.2},
        )
        score = 50
        if state.get("challenge_level") == "high":
            score += 25
        elif state.get("challenge_level") == "low":
            score -= 15
        if state.get("pace_modifier", 1.0) > 1.0:
            score += 10
        if signals.get("stalled"):
            score -= 25
        if signals.get("completed_recently"):
            score += 20
        label = "balanced"
        if score >= 75:
            label = "high_flow"
        elif score <= 35:
            label = "low_momentum"
        return {"momentum_score": max(0, min(score, 100)), "state": label, **state}


def compute_adaptive_momentum(
    workspace: Dict[str, Any],
    *,
    profile: Optional[Dict[str, Any]] = None,
    friction_state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Return pacing and challenge knobs for the current session."""
    profile = profile or {}
    friction_state = friction_state or {}
    runtime_state = workspace.get("runtime_state") or {}
    memory = workspace.get("runtime_memory") or {}
    supports = workspace.get("supports") or []

    friction_level = float(friction_state.get("friction_level", 0.2))
    high_friction = bool(runtime_state.get("high_friction")) or friction_level >= 0.55
    high_momentum = bool(runtime_state.get("high_momentum"))
    shallow = (profile.get("engagement_pattern") == "shallow")
    deep = (profile.get("engagement_pattern") == "deep")

    mode = "balanced"
    if high_friction or shallow:
        mode = "overwhelm"
    elif high_momentum and deep:
        mode = "deep_engagement"
    elif high_momentum:
        mode = "high_momentum"
    elif friction_level >= 0.35:
        mode = "low_momentum"
    elif int(memory.get("continue_count", 0)) <= 1 and friction_level < 0.25:
        mode = "boredom"

    pace_modifier = 1.0
    challenge_level = "medium"
    interaction_density = "medium"
    reflection_frequency = "normal"
    reward_frequency = "normal"

    if mode == "overwhelm":
        pace_modifier = 0.75
        challenge_level = "low"
        interaction_density = "low"
        reflection_frequency = "low"
        reward_frequency = "high"
    elif mode == "low_momentum":
        pace_modifier = 0.85
        challenge_level = "low"
        interaction_density = "medium"
        reflection_frequency = "medium"
        reward_frequency = "high"
    elif mode == "boredom":
        pace_modifier = 1.1
        challenge_level = "medium"
        interaction_density = "high"
        reflection_frequency = "low"
        reward_frequency = "medium"
    elif mode == "high_momentum":
        pace_modifier = 1.15
        challenge_level = "high"
        interaction_density = "high"
        reflection_frequency = "low"
        reward_frequency = "medium"
    elif mode == "deep_engagement":
        pace_modifier = 1.2
        challenge_level = "high"
        interaction_density = "medium"
        reflection_frequency = "medium"
        reward_frequency = "low"

    if "adhd" in supports or "low_energy" in supports:
        pace_modifier = min(pace_modifier, 0.9)
        interaction_density = "low"
        reflection_frequency = "low"

    if "professional" in supports:
        reward_frequency = "low"
        reflection_frequency = "medium"

    return {
        "mode": mode,
        "pace_modifier": round(pace_modifier, 2),
        "challenge_level": challenge_level,
        "interaction_density": interaction_density,
        "reflection_frequency": reflection_frequency,
        "reward_frequency": reward_frequency,
    }
