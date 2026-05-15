"""Interactive challenge engine.

This system creates:
- mini games
- interactive challenges
- checkpoints
- active recall tasks
- drag/drop style logic scaffolds
- momentum streaks
- dopamine rewards
- progress loops

The purpose is making difficult tasks feel interactive.
"""

from __future__ import annotations

from typing import Any, Dict


class InteractiveChallengeEngine:
    def generate_challenge(
        self,
        task_type: str,
        workspace: Dict[str, Any],
    ) -> Dict[str, Any]:
        challenge_map = {
            "essay": self._essay_challenge,
            "coding": self._coding_challenge,
            "language": self._language_challenge,
            "fitness": self._fitness_challenge,
            "study": self._study_challenge,
        }

        handler = challenge_map.get(task_type, self._generic_challenge)
        return handler(workspace)

    def _essay_challenge(self, workspace: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "speed_outline",
            "title": "Build 3 core ideas in under 2 minutes",
            "reward": 15,
        }

    def _coding_challenge(self, workspace: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "debug_mission",
            "title": "Fix one bug before unlocking next step",
            "reward": 25,
        }

    def _language_challenge(self, workspace: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "recall_combo",
            "title": "Translate 5 phrases without hints",
            "reward": 10,
        }

    def _fitness_challenge(self, workspace: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "micro_workout",
            "title": "Complete a 5 minute activation set",
            "reward": 20,
        }

    def _study_challenge(self, workspace: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "active_recall",
            "title": "Teach the concept back in your own words",
            "reward": 20,
        }

    def _generic_challenge(self, workspace: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "momentum_step",
            "title": "Complete the smallest possible next step",
            "reward": 5,
        }
