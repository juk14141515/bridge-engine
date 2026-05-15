from __future__ import annotations

from typing import Any, Dict


class RealtimeSync:
    def payload(self, workspace: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'workspace_id': workspace.get('id'),
            'updated_at': workspace.get('updated_at'),
            'status': workspace.get('status'),
        }
