"""Comeback runtime.

Makes returning feel easy instead of painful.
"""

from __future__ import annotations

from typing import Dict


class ComebackRuntime:
    def generate_reentry(self, workspace: Dict) -> Dict:
        return {
            "message": "Welcome back. Start with one tiny step.",
            "resume_point": workspace.get("current_step_index", 0),
            "recommended_mode": "low_friction_restart",
            "reward": "comeback_bonus",
        }
