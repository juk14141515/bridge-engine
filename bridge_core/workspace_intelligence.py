from __future__ import annotations

from typing import Any, Dict


class WorkspaceIntelligence:
    def __init__(self, workspace: Dict[str, Any]):
        self.workspace = workspace

    def summary(self) -> Dict[str, Any]:
        steps = self.workspace.get('steps') or []
        idx = int(self.workspace.get('current_step_index', 0) or 0)
        return {
            'task': self.workspace.get('task'),
            'category': self.workspace.get('category'),
            'current_step_index': idx,
            'remaining_steps': max(len(steps) - idx, 0),
            'momentum_state': 'active' if idx > 0 else 'starting',
        }
