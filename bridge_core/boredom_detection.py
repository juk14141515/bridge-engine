"""Boredom detection engine.

Attempts to detect disengagement before abandonment.
"""

from __future__ import annotations

from typing import Dict


class BoredomDetectionEngine:
    def analyze(self, signals: Dict) -> Dict:
        boredom = 0

        if signals.get("slow_responses"):
            boredom += 25

        if signals.get("minimal_outputs"):
            boredom += 25

        if signals.get("repeated_skips"):
            boredom += 35

        if signals.get("inactive"):
            boredom += 20

        return {
            "boredom_score": boredom,
            "high_boredom_risk": boredom >= 60,
        }
