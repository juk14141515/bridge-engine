"""Engagement score engine.

Unified engagement metric.
"""

from __future__ import annotations

from typing import Dict


class EngagementScoreEngine:
    def calculate(self, signals: Dict) -> Dict:
        score = 50

        score += signals.get("momentum_bonus", 0)
        score -= signals.get("boredom_penalty", 0)
        score -= signals.get("friction_penalty", 0)
        score += signals.get("challenge_bonus", 0)

        score = max(0, min(score, 100))

        return {
            "engagement_score": score,
            "state": self._state(score),
        }

    def _state(self, score: int) -> str:
        if score >= 80:
            return "immersed"
        if score <= 35:
            return "disengaging"
        return "engaged"
