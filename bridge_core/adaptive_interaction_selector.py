"""Adaptive interaction selector.

Selects the best interaction pattern for the current runtime state.
"""

from __future__ import annotations

from typing import Dict, List


class AdaptiveInteractionSelector:
    def select(
        self,
        profile: Dict,
        runtime_state: Dict,
        available_modes: List[str],
    ) -> Dict:
        selected = []

        if runtime_state.get("overwhelmed"):
            selected += ["micro_wins", "teach_back"]

        elif runtime_state.get("hyperfocused"):
            selected += ["boss_battles", "quests"]

        else:
            selected += available_modes[:3]

        if "gaming" in profile.get("interests", []):
            selected += ["quests", "xp_system"]

        return {
            "selected_modes": sorted(set(selected)),
            "runtime_strategy": self._strategy(runtime_state),
        }

    def _strategy(self, runtime_state: Dict) -> str:
        if runtime_state.get("overwhelmed"):
            return "friction_reduction"
        if runtime_state.get("hyperfocused"):
            return "deep_immersion"
        return "balanced_runtime"
