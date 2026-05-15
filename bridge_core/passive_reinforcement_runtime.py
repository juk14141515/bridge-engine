"""Passive reinforcement runtime.

Learning should continue even outside focused sessions.
"""

from __future__ import annotations

from typing import Dict


class PassiveReinforcementRuntime:
    def generate(self, workspace: Dict) -> Dict:
        category = workspace.get("category", "general")

        return {
            "passive_prompts": True,
            "ambient_review": True,
            "micro_recall": True,
            "background_reinforcement": self._background_reinforcement(category),
        }

    def _background_reinforcement(self, category: str) -> str:
        mapping = {
            "language_learning": "phrase_loops",
            "essay_writing": "argument_reminders",
            "coding_project": "architecture_prompts",
            "study": "memory_reinforcement",
        }

        return mapping.get(category, "adaptive_reinforcement")
