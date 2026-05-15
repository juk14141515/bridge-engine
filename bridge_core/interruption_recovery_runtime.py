"""Interruption recovery runtime.

Handles task interruptions gracefully.
"""

from __future__ import annotations

from typing import Dict


class InterruptionRecoveryRuntime:
    def recover(self, workspace: Dict) -> Dict:
        return {
            "resume_anchor": workspace.get("current_step_index", 0),
            "tiny_restart_step": True,
            "context_rebuild": True,
            "friction_reduction": True,
            "motivational_reentry": "Resume with one tiny action.",
        }
