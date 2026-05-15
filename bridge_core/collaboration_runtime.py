from __future__ import annotations

from typing import Dict, List


class CollaborationRuntime:
    def build_room(self, workspace_id: str, users: List[str]) -> Dict[str, object]:
        return {
            'workspace_id': workspace_id,
            'participants': users,
            'mode': 'collaborative',
        }
