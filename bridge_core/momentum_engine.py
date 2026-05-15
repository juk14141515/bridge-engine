"""Momentum engine.

Tracks user momentum and flow state.
"""

from __future__ import annotations

from typing import Dict


class MomentumEngine:
    def calculate(self, signals: Dict) -> Dict:
        score = 50

        if signals.get("completed_recently"):
            score += 20

        if signals.get("high_response_speed"):
            score += 10

        if signals.get("stalled"):
            score -= 25

        if signals.get("frustrated"):
            score -= 20

        state = "balanced"
        if score >= 75:
            state = "high_flow"
        elif score <= 35:
            state = "low_momentum"

        return {
            "momentum_score": max(0, min(score, 100)),
            "state": state,
        }
