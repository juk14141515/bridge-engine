from __future__ import annotations

from typing import Dict


class LiveSessionRuntime:
    def connect_payload(self, workspace_id: str) -> Dict[str, str]:
        return {
            'workspace_id': workspace_id,
            'transport': 'websocket',
            'status': 'ready',
        }
