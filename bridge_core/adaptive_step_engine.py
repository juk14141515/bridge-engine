"""Adaptive step engine for Bridge Runtime V2.

This layer keeps the user moving when a task is too large, vague, or emotionally
heavy. It does not require an LLM; it produces deterministic fallback steps that
are safe for the runtime and useful for the UI.
"""

from __future__ import annotations

from typing import Any, Dict, List


def estimate_friction(user_output: str, rewrite_count: int = 0) -> str:
    text = (user_output or "").strip().lower()
    if rewrite_count >= 3:
        return "high"
    if not text:
        return "blank"
    if len(text.split()) <= 4:
        return "low_output"
    stuck_words = ["idk", "i don't know", "dont know", "stuck", "can't", "cant", "overwhelmed", "too much"]
    if any(word in text for word in stuck_words):
        return "stuck"
    return "moving"


def shrink_step(step: Dict[str, Any], level: int = 1) -> Dict[str, Any]:
    action = str(step.get("action") or step.get("prompt") or "make one mark")
    if level <= 1:
        prompt = f"Do the first tiny visible part only: {action}"
    elif level == 2:
        prompt = "Type one ugly sentence, fragment, or bullet. Stop there."
    else:
        prompt = "Open the workspace and write one word related to this. That counts."
    return {**step, "prompt": prompt, "adapted": True, "adaptation_level": level}


def next_adaptive_move(workspace: Dict[str, Any], user_output: str = "") -> Dict[str, Any]:
    state = workspace.get("runtime_state") or {}
    steps: List[Dict[str, Any]] = workspace.get("steps") or []
    idx = int(workspace.get("current_step_index", 0) or 0)
    step = steps[idx] if idx < len(steps) else {}
    friction = estimate_friction(user_output, int(state.get("rewrite_count", 0) or 0))

    if friction in {"blank", "stuck", "low_output", "high"}:
        level = {"blank": 3, "stuck": 2, "low_output": 1, "high": 2}.get(friction, 1)
        return {
            "kind": "shrink_step",
            "friction": friction,
            "step": shrink_step(step, level),
            "message": "Bridge made the next move smaller so momentum can continue.",
        }

    return {
        "kind": "continue",
        "friction": friction,
        "step": step,
        "message": "User is moving; continue normal progression.",
    }
