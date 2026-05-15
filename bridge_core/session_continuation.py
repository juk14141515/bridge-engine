from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from bridge_core.artifact_engine_v2 import ArtifactEngine
from bridge_core.runtime_schema import ensure_workspace, runtime_event


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def continue_session_state(session: Dict[str, Any], user_output: str) -> Dict[str, Any]:
    """Advance one workspace step and update the living artifact.

    This function is intentionally small and deterministic so the Flask API,
    tests, and future realtime/websocket layer can all share the same step-loop
    behavior.
    """
    workspace = ensure_workspace(session)
    steps = workspace.get("steps") or []
    idx = int(workspace.get("current_step_index", 0) or 0)

    if not steps:
        workspace["status"] = "active"
        workspace["updated_at"] = now()
        return workspace

    if idx >= len(steps):
        workspace["status"] = "complete"
        workspace.setdefault("runtime_state", {})["status"] = "complete"
        workspace["updated_at"] = now()
        return workspace

    current = steps[idx]
    current["user_output"] = user_output or ""
    current["status"] = "done"
    current["completed_at"] = now()

    workspace["artifact"] = ArtifactEngine(workspace).apply_step_output(current, user_output or "")
    workspace.setdefault("events", []).append(
        runtime_event(
            "step_completed",
            {
                "step_id": current.get("id"),
                "step_index": idx,
                "output_slot": current.get("output_slot"),
            },
        )
    )

    next_index = idx + 1
    if next_index < len(steps):
        workspace["current_step_index"] = next_index
        steps[next_index]["status"] = "active"
        workspace["status"] = "active"
    else:
        workspace["current_step_index"] = next_index
        workspace["status"] = "complete"

    total = len(steps)
    done = len([step for step in steps if step.get("status") == "done"])
    runtime_state = workspace.setdefault("runtime_state", {})
    runtime_state["current_step_index"] = workspace["current_step_index"]
    runtime_state["completion_rate"] = int((done / total) * 100) if total else 0
    runtime_state["status"] = workspace["status"]
    runtime_state["updated_at"] = now()
    workspace["updated_at"] = now()
    return workspace
