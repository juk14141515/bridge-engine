"""Enjoyment mapper.

Maps difficult work into the user's interests.
"""

from __future__ import annotations

from typing import Dict, List


class EnjoymentMapper:
    def map_experience(
        self,
        task: str,
        interests: List[str],
    ) -> Dict:
        interest_text = ", ".join(interests) if interests else "general motivation"

        return {
            "task": task,
            "theme": interest_text,
            "challenge_style": self._challenge_style(interests),
            "reward_style": self._reward_style(interests),
            "ui_energy": self._ui_energy(interests),
        }

    def _challenge_style(self, interests: List[str]) -> str:
        if "videogames" in interests:
            return "quest_system"
        if "music" in interests:
            return "playlist_progression"
        return "momentum_progression"

    def _reward_style(self, interests: List[str]) -> str:
        if "videogames" in interests:
            return "xp_unlocks"
        return "progress_rewards"

    def _ui_energy(self, interests: List[str]) -> str:
        if "videogames" in interests:
            return "high_energy"
        return "focused"
