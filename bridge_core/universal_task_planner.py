"""Universal task planner.

Transforms ANY task into:
- setup
- momentum
- execution
- verification
- completion
- export
"""

from __future__ import annotations

from typing import Dict, List


class UniversalTaskPlanner:
    def build_plan(self, task: str, category: str = "general") -> Dict:
        phases = [
            {
                "id": "setup",
                "title": "Reduce friction and prepare",
            },
            {
                "id": "momentum",
                "title": "Create an easy first win",
            },
            {
                "id": "execution",
                "title": "Build the core work",
            },
            {
                "id": "verification",
                "title": "Verify understanding or completion",
            },
            {
                "id": "completion",
                "title": "Finalize the result",
            },
            {
                "id": "export",
                "title": "Export or share the artifact",
            },
        ]

        return {
            "task": task,
            "category": category,
            "phases": phases,
            "total_phases": len(phases),
        }
