"""Rotate interaction modalities to reduce fatigue."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from bridge_core.runtime_memory import update_runtime_memory

INTERACTION_TYPES: List[str] = [
    "writing",
    "speaking",
    "simulation",
    "micro_challenge",
    "visual_mapping",
    "scenario_solving",
    "reflection",
    "active_recall",
    "guided_creation",
    "roleplay",
    "timed_challenge",
    "coaching",
    "storytelling",
    "debate",
    "build_mode",
]

_CATEGORY_DEFAULTS: Dict[str, List[str]] = {
    "writing": ["writing", "reflection", "guided_creation", "storytelling"],
    "essay": ["writing", "reflection", "guided_creation", "debate"],
    "coding": ["build_mode", "micro_challenge", "guided_creation", "coaching"],
    "language": ["speaking", "active_recall", "simulation", "writing"],
    "general": ["writing", "reflection", "scenario_solving", "coaching"],
}


def select_interaction(
    workspace: Dict[str, Any],
    profile: Optional[Dict[str, Any]] = None,
    momentum_state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Pick the next interaction modality; avoid immediate repeats unless strongly preferred."""
    profile = profile or build_profile_fallback(workspace)
    momentum_state = momentum_state or {}
    memory = workspace.get("runtime_memory") or {}
    history: List[str] = list(memory.get("interaction_history") or [])
    last = history[-1] if history else memory.get("last_interaction")
    prefs = profile.get("preferred_interaction_modes") or []

    category = str(workspace.get("category") or "general").lower()
    pool = list(_CATEGORY_DEFAULTS.get(category, _CATEGORY_DEFAULTS["general"]))

    mode = momentum_state.get("mode")
    if mode == "overwhelm":
        pool = ["writing", "reflection", "coaching", "guided_creation"]
    elif mode == "high_momentum" or mode == "deep_engagement":
        pool.extend(["simulation", "micro_challenge", "scenario_solving", "debate"])
    elif mode == "boredom":
        pool = ["micro_challenge", "simulation", "roleplay", "timed_challenge", "storytelling"]

    dominant = profile.get("dominant_interaction_type")
    if dominant and int((memory.get("preferred_interactions") or {}).get(dominant, 0)) >= 3:
        if dominant not in pool:
            pool.append(dominant)

    # dedupe preserve order
    seen = set()
    ordered: List[str] = []
    for item in pool:
        if item not in seen and item in INTERACTION_TYPES:
            seen.add(item)
            ordered.append(item)
    if not ordered:
        ordered = ["writing", "reflection", "coaching"]

    preferred = [p for p in prefs if p in ordered]
    candidates = preferred + [p for p in ordered if p not in preferred]

    current = None
    if last and last in candidates:
        start = (candidates.index(last) + 1) % len(candidates)
        rotated = candidates[start:] + candidates[:start]
        current = rotated[0] if rotated[0] != last else (rotated[1] if len(rotated) > 1 else candidates[0])
    if not current:
        for candidate in candidates:
            if candidate != last:
                current = candidate
                break
    current = current or candidates[0]

    if current:
        update_runtime_memory(
            workspace,
            {"type": "interaction_record", "interaction_type": current},
        )

    return {
        "current": current,
        "previous": last,
        "candidates": candidates[:6],
        "avoid_repeat": current != last,
        "rotation_reason": _rotation_reason(last, current, mode),
    }


def build_profile_fallback(workspace: Dict[str, Any]) -> Dict[str, Any]:
    from bridge_core.runtime_memory import build_runtime_profile

    return build_runtime_profile(workspace)


def _rotation_reason(previous: Optional[str], current: str, mode: Optional[str]) -> str:
    if not previous:
        return "opening_variety"
    if previous == current:
        return "user_preference_locked"
    if mode == "overwhelm":
        return "reduce_cognitive_load"
    if mode in ("high_momentum", "deep_engagement"):
        return "deepen_engagement"
    if mode == "boredom":
        return "increase_novelty"
    return "prevent_fatigue"
