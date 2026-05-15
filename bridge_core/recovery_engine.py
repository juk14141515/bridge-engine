from __future__ import annotations

from typing import Any, Dict


def build_recovery_payload(workspace: Dict[str, Any]) -> Dict[str, Any]:
    task = workspace.get('task', 'unfinished task')
    idx = int(workspace.get('current_step_index', 0) or 0)
    steps = workspace.get('steps') or []
    current = steps[idx] if idx < len(steps) else {}

    return {
        'resume_available': True,
        'message': f'Continue where you left off: {task}',
        'current_step': current,
        'resume_action': 'continue_session',
    }
