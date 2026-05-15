"""Adaptive pacing engine.

Adjusts runtime pacing based on engagement state.
"""

from __future__ import annotations

from typing import Dict


class AdaptivePacingEngine:
    def adjust(self, engagement: Dict) -> Dict:
        if engagement.get("high_risk"):
            return {
                "step_size": "tiny",
                "session_length": "short",
                "reward_frequency": "high",
            }

        if engagement.get("high_flow"):
            return {
                "step_size": "larger",
                "session_length": "extended",
                "reward_frequency": "milestone",
            }

        return {
            "step_size": "normal",
            "session_length": "balanced",
            "reward_frequency": "balanced",
        }
