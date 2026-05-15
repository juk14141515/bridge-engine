"""Workspace persistence layer.

Stores resumable workspace state for ANY task type.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


BASE_DIR = Path("runtime_data/workspaces")
BASE_DIR.mkdir(parents=True, exist_ok=True)


class WorkspacePersistence:
    def workspace_path(self, workspace_id: str) -> Path:
        return BASE_DIR / f"{workspace_id}.json"

    def save_workspace(self, workspace: Dict[str, Any]) -> str:
        workspace_id = workspace.get("id")
        if not workspace_id:
            raise ValueError("workspace missing id")

        path = self.workspace_path(workspace_id)
        path.write_text(json.dumps(workspace, indent=2), encoding="utf-8")
        return str(path)

    def load_workspace(self, workspace_id: str) -> Dict[str, Any]:
        path = self.workspace_path(workspace_id)
        if not path.exists():
            raise FileNotFoundError(f"workspace not found: {workspace_id}")

        return json.loads(path.read_text(encoding="utf-8"))

    def update_workspace(self, workspace_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        workspace = self.load_workspace(workspace_id)
        workspace.update(updates)
        self.save_workspace(workspace)
        return workspace

    def list_workspaces(self) -> list[str]:
        return sorted(p.stem for p in BASE_DIR.glob("*.json"))
