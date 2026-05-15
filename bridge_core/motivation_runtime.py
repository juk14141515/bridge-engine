from __future__ import annotations

from typing import Dict


class MotivationRuntime:
    def build_status(self, completed_steps: int) -> Dict[str, str]:
        if completed_steps >= 10:
            state = 'deep_flow'
        elif completed_steps >= 5:
            state = 'momentum'
        elif completed_steps >= 1:
            state = 'starting'
        else:
            state = 'idle'

        return {
            'state': state,
            'message': f'Momentum state: {state.replace("_", " ")}',
        }
