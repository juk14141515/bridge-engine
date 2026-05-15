from __future__ import annotations

from typing import Dict, List


class TaskDecomposer:
    def decompose(self, task: str) -> Dict[str, List[str]]:
        return {
            'task': task,
            'micro_steps': [
                'Open the workspace',
                'Write one rough idea',
                'Expand the strongest idea',
                'Refine and export',
            ],
        }
