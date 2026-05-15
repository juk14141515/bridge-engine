"""Realtime reward runtime.

Adaptive reward scheduling.
"""

from __future__ import annotations

from typing import Dict


class RealtimeRewardRuntime:
    def generate_rewards(self, runtime_state: Dict) -> Dict:
        if runtime_state.get("engagement") == "immersed":
            return {
                "reward_style": "achievement_unlock",
                "reward_frequency": "milestone",
            }

        return {
            "reward_style": "micro_feedback",
            "reward_frequency": "high",
        }
