"""Deep immersion layer — narrative continuity without childish tone."""

from __future__ import annotations

from typing import Any, Dict, Optional

_ARC_TEMPLATES: Dict[str, Dict[str, str]] = {
    "writing": {
        "mission": "Draft mission",
        "phase": "mission_phase",
        "arc": "progression_arc",
    },
    "essay": {
        "mission": "Essay mission",
        "phase": "mission_phase",
        "arc": "progression_arc",
    },
    "coding": {
        "mission": "Build operation",
        "phase": "build_phase",
        "arc": "mastery_arc",
    },
    "language": {
        "mission": "Mastery path",
        "phase": "practice_phase",
        "arc": "mastery_arc",
    },
    "general": {
        "mission": "Focus session",
        "phase": "session_phase",
        "arc": "progression_arc",
    },
}


def build_immersion_state(
    workspace: Dict[str, Any],
    profile: Optional[Dict[str, Any]] = None,
    *,
    frame: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate ambient immersion metadata for the frontend."""
    profile = profile or {}
    category = str(workspace.get("category") or "general").lower()
    if "essay" in category or "essay" in str(workspace.get("task", "")).lower():
        category = "essay"
    template = _ARC_TEMPLATES.get(category, _ARC_TEMPLATES["general"])
    frame_key = (frame or workspace.get("frame") or "general").replace(" ", "_")
    task = str(workspace.get("task") or workspace.get("title") or "your work").strip()
    steps = workspace.get("steps") or []
    idx = int(workspace.get("current_step_index", 0) or 0)
    total = max(1, len(steps))
    progress_ratio = min(1.0, idx / total)

    tone = profile.get("preferred_tone", "calm")
    professional = "professional" in (workspace.get("supports") or [])

    ambient = "focused_studio"
    if tone == "gentle":
        ambient = "soft_focus"
    elif professional:
        ambient = "strategic_workspace"

    phase_labels = _phase_labels(professional, total)
    phase = phase_labels[min(idx, len(phase_labels) - 1)]

    narrative = _narrative_thread(task, frame_key, phase, professional)
    mission = f"{template['mission']}: {task[:72]}" if len(task) > 72 else f"{template['mission']}: {task}"

    return {
        "ambient_state": ambient,
        "narrative_thread": narrative,
        "mission_continuity": mission,
        "challenge_arc": _challenge_arc(progress_ratio, professional),
        "progression_arc": _progression_arc(progress_ratio, idx, total),
        "mastery_arc": _mastery_arc(progress_ratio, professional),
        "identity_reinforcement": _identity_line(frame_key, professional),
        "session_phase": phase,
        "tone": "professional" if professional else tone,
    }


def _phase_labels(professional: bool, total: int) -> list[str]:
    if professional:
        base = ["intake", "alignment", "decomposition", "execution", "refinement", "completion"]
    else:
        base = ["intake", "motivation_bridge", "decomposition", "guided_execution", "refinement", "completion"]
    if total <= len(base):
        return base[: max(total, 1)]
    return base


def _narrative_thread(task: str, frame: str, phase: str, professional: bool) -> str:
    if professional:
        return f"Operating on «{task[:48]}» — current phase: {phase.replace('_', ' ')}."
    frame_note = {
        "gaming": "quest-log pacing",
        "music": "rhythm and repetition",
        "fitness": "steady reps forward",
        "investing": "thesis-driven steps",
    }.get(frame, "steady forward motion")
    return f"You are moving through {phase.replace('_', ' ')} with {frame_note}."


def _challenge_arc(ratio: float, professional: bool) -> str:
    if ratio < 0.25:
        return "orientation" if professional else "warmup_round"
    if ratio < 0.6:
        return "active_engagement"
    if ratio < 0.9:
        return "precision_pass"
    return "final_push"


def _progression_arc(ratio: float, idx: int, total: int) -> str:
    return f"step {idx + 1} of {total} ({int(ratio * 100)}% path)"


def _mastery_arc(ratio: float, professional: bool) -> str:
    if ratio < 0.5:
        return "foundation" if professional else "learning_loop"
    if ratio < 0.85:
        return "integration"
    return "demonstration"


def _identity_line(frame: str, professional: bool) -> str:
    if professional:
        return "You are building reliable output, one decision at a time."
    lines = {
        "gaming": "You learn by playing forward — each step is a save point.",
        "music": "You learn by layering — each step adds a measure.",
        "creative": "You learn by drafting — each step is a new version.",
    }
    return lines.get(frame, "You learn by doing — each step counts.")
