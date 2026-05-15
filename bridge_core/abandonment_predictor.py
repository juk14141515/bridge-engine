"""Abandonment predictor.

Predicts when a user may stop engaging.
"""

from __future__ import annotations

from typing import Dict


class AbandonmentPredictor:
    def predict(self, signals: Dict) -> Dict:
        risk = 0

        if signals.get("high_boredom"):
            risk += 35

        if signals.get("frustration"):
            risk += 35

        if signals.get("long_pause"):
            risk += 20

        if signals.get("failed_checkpoints"):
            risk += 15

        return {
            "dropoff_risk": min(risk, 100),
            "high_risk": risk >= 60,
        }
