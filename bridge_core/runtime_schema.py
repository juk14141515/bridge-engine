"""Canonical runtime schema helpers for Bridge Engine.

This module keeps API payloads stable for the frontend. Runtime engines can evolve,
but every response should preserve the same top-level envelope shape so the UI
never has to guess whether a field is called session, workspace, workflow, lane,
or something else.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from bridge_core.task_registry import detect_task_type, get_task_type, normalize_category

DEFAULT_REWRITE_OPTIONS = [
    "make_easier",
    "break_smaller",
    "give_example",
    "explain_differently",
    "do_first_line",
]


def utc_now() -> str:
    return datetime.utcnow().isoformat()


def as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def ensure_workspace(raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Return a defensive, normalized workspace/session dict.

    This prevents old sessions or partial payloads from losing task/frame/category
    context when reloaded from SQLite or sent back from the frontend.
    """
    workspace: Dict[str, Any] = deepcopy(raw or {})

    workspace_id = workspace.get("id") or workspace.get("workspace_id") or workspace.get("session_id")
    if workspace_id:
        workspace["id"] = str(workspace_id)

    task = str(workspace.get("task") or workspace.get("title") or workspace.get("user_words") or "").strip()
    workspace["task"] = task
    workspace["title"] = str(workspace.get("title") or task or "Bridge session")

    category = detect_task_type(task, str(workspace.get("category") or ""))
    workspace["category"] = category
    workspace["category_info"] = get_task_type(category)

    frame = str(workspace.get("frame") or workspace.get("interest_frame") or "gaming").strip().lower()
    workspace["frame"] = frame or "gaming"
    workspace["interest_frame"] = workspace["frame"]

    supports = [str(s) for s in as_list(workspace.get("supports")) if str(s).strip()]
    workspace["supports"] = supports or ["step_by_step"]

    workspace["status"] = str(workspace.get("status") or "active")
    workspace["current_step_index"] = int(workspace.get("current_step_index", 0) or 0)
    workspace["steps"] = [normalize_step(step, i) for i, step in enumerate(as_list(workspace.get("steps")), start=1) if isinstance(step, dict)]

    artifact = workspace.get("artifact") if isinstance(workspace.get("artifact"), dict) else {}
    workspace["artifact"] = ensure_artifact(artifact, workspace)

    workspace["events"] = [event for event in as_list(workspace.get("events")) if isinstance(event, dict)]
    workspace["created_at"] = str(workspace.get("created_at") or utc_now())
    workspace["updated_at"] = str(workspace.get("updated_at") or utc_now())

    runtime_state = workspace.get("runtime_state") if isinstance(workspace.get("runtime_state"), dict) else {}
    workspace["runtime_state"] = ensure_runtime_state(runtime_state, workspace)
    return workspace


def normalize_step(step: Dict[str, Any], index: int = 1) -> Dict[str, Any]:
    normalized = dict(step)
    normalized["id"] = str(normalized.get("id") or f"s{index}")
    normalized["title"] = str(normalized.get("title") or f"Step {index}")
    normalized["prompt"] = str(normalized.get("prompt") or normalized.get("action") or "")
    normalized["why"] = str(normalized.get("why") or "This keeps the Bridge moving.")
    normalized["action"] = str(normalized.get("action") or normalized.get("prompt") or "")
    normalized["output_slot"] = str(normalized.get("output_slot") or f"step_{index}")
    normalized["status"] = str(normalized.get("status") or "pending")
    normalized["user_output"] = str(normalized.get("user_output") or normalized.get("answer") or "")
    hv = normalized.get("help_variants")
    normalized["help_variants"] = hv if isinstance(hv, dict) else {}
    return normalized


def ensure_artifact(artifact: Dict[str, Any], workspace: Dict[str, Any]) -> Dict[str, Any]:
    category = workspace.get("category") or detect_task_type(workspace.get("task", ""), "")
    category_info = get_task_type(str(category))
    normalized = dict(artifact or {})
    normalized["task"] = str(normalized.get("task") or workspace.get("task") or "")
    normalized["frame"] = str(normalized.get("frame") or workspace.get("frame") or "gaming")
    normalized["category"] = str(normalized.get("category") or category)
    normalized["type"] = str(normalized.get("type") or category_info.get("artifact_type") or "completion_plan")
    normalized["supports"] = as_list(normalized.get("supports") or workspace.get("supports"))
    sections = normalized.get("sections")
    normalized["sections"] = sections if isinstance(sections, dict) else {}
    normalized["final_output"] = normalized.get("final_output") or ""
    normalized["export_formats"] = as_list(normalized.get("export_formats")) or ["markdown", "plain_text"]
    normalized["updated_at"] = str(normalized.get("updated_at") or utc_now())
    normalized["created_at"] = str(normalized.get("created_at") or workspace.get("created_at") or utc_now())
    return normalized


def ensure_runtime_state(state: Dict[str, Any], workspace: Dict[str, Any]) -> Dict[str, Any]:
    steps = workspace.get("steps") or []
    done = len([s for s in steps if isinstance(s, dict) and s.get("status") == "done"])
    total = len(steps)
    idx = int(workspace.get("current_step_index", 0) or 0)
    normalized = dict(state or {})
    normalized["mode"] = str(normalized.get("mode") or "guided_completion")
    normalized["status"] = str(workspace.get("status") or normalized.get("status") or "active")
    normalized["current_step_index"] = idx
    normalized["completion_rate"] = int((done / total) * 100) if total else 0
    normalized["rewrite_count"] = int(normalized.get("rewrite_count", 0) or 0)
    normalized["category"] = workspace.get("category")
    normalized["frame"] = workspace.get("frame")
    normalized["updated_at"] = str(workspace.get("updated_at") or utc_now())
    return normalized


def current_step(workspace: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    steps = workspace.get("steps") or []
    idx = int(workspace.get("current_step_index", 0) or 0)
    if 0 <= idx < len(steps):
        step = steps[idx]
        return step if isinstance(step, dict) else None
    return None


def progress(workspace: Dict[str, Any]) -> Dict[str, int]:
    steps = workspace.get("steps") or []
    done = len([s for s in steps if isinstance(s, dict) and s.get("status") == "done"])
    total = len(steps)
    return {"done": done, "total": total, "percent": int((done / total) * 100) if total else 0}


def build_envelope(
    workspace: Dict[str, Any],
    *,
    intelligence: Optional[Dict[str, Any]] = None,
    next_prompt: Optional[Dict[str, Any]] = None,
    artifact_preview: Optional[Dict[str, Any]] = None,
    memory_summary: Optional[Dict[str, Any]] = None,
    rewrite_options: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    normalized = ensure_workspace(workspace)
    return {
        "workspace": normalized,
        "session": normalized,
        "runtime_state": normalized.get("runtime_state", {}),
        "intelligence": intelligence or {},
        "next_prompt": next_prompt or {},
        "artifact_preview": artifact_preview or normalized.get("artifact", {}),
        "memory_summary": memory_summary or {},
        "rewrite_options": list(rewrite_options or DEFAULT_REWRITE_OPTIONS),
        "current_step": current_step(normalized),
        "progress": progress(normalized),
    }


def runtime_event(kind: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "kind": kind,
        "payload": payload or {},
        "created_at": utc_now(),
    }
