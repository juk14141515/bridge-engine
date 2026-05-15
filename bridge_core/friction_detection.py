"""Emotional friction detection and intervention selection."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

from bridge_core.friction_engine import FrictionEngine

_DISENGAGE = re.compile(
    r"\b(idk|i don'?t know|dunno|whatever|skip|bored|stuck|can'?t|hate|ugh|nvm)\b",
    re.I,
)


def detect_friction(
    workspace: Dict[str, Any],
    user_output: str = "",
    *,
    signals: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Detect disengagement and recommend a calm intervention."""
    signals = signals or {}
    memory = workspace.get("runtime_memory") or {}
    runtime_state = workspace.get("runtime_state") or {}
    text = (user_output or "").strip()
    words = text.split()
    legacy = FrictionEngine().detect(text)

    level = 0.15
    causes: list[str] = []

    if not text:
        level = 0.45
        causes.append("empty_response")
    elif len(words) <= 2 or len(text) < 12:
        level = 0.55
        causes.append("extremely_short_response")
    elif _DISENGAGE.search(text):
        level = max(level, 0.65)
        causes.append("disengaged_language")

    if int(memory.get("rewrite_count", 0)) >= 2:
        level = max(level, 0.6)
        causes.append("repeated_rewrites")

    if int(memory.get("short_response_count", 0)) >= 2:
        level = max(level, 0.5)
        causes.append("shallow_engagement_pattern")

    if signals.get("inactive"):
        level = max(level, 0.7)
        causes.append("inactivity")

    if signals.get("skipped"):
        level = max(level, 0.65)
        causes.append("skipped_step")

    if legacy.get("state") == "overwhelmed":
        level = max(level, 0.75)
        causes.append("overwhelm_language")

    if runtime_state.get("high_friction"):
        level = max(level, 0.6)

    level = min(1.0, round(level, 2))
    cause = causes[0] if causes else "none"
    strategy = _intervention_strategy(level, cause, workspace)

    return {
        "friction_level": level,
        "probable_cause": cause,
        "intervention_strategy": strategy,
        "legacy_state": legacy.get("state", "moving"),
    }


def _intervention_strategy(level: float, cause: str, workspace: Dict[str, Any]) -> str:
    supports = workspace.get("supports") or []
    if level >= 0.7:
        if "professional" in supports:
            return "split_into_smaller_win"
        return "convert_into_challenge"
    if level >= 0.55:
        if cause == "repeated_rewrites":
            return "switch_interaction_type"
        return "simplify"
    if level >= 0.4:
        return "reduce_pressure"
    if cause == "inactivity":
        return "offer_voice_mode"
    if level >= 0.25:
        return "add_novelty"
    return "maintain_flow"
