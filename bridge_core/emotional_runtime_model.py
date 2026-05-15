"""Emotional runtime model.

Behavioral adaptation layer.
"""

from __future__ import annotations

from typing import Dict


class EmotionalRuntimeModel:
    def infer(self, signals: Dict) -> Dict:
        if signals.get("overwhelmed"):
            return {
                "state": "overwhelmed",
                "ui_mode": "minimal",
                "recommended_response": "reduce_complexity",
            }

        if signals.get("hyperfocused"):
            return {
                "state": "hyperfocused",
                "ui_mode": "immersive",
                "recommended_response": "remove_interruptions",
            }

        return {
            "state": "balanced",
            "ui_mode": "standard",
            "recommended_response": "normal_runtime",
        }
