"""Generic adaptive runtime engine.

This layer is intentionally task-agnostic.
It should support:
- essays
- coding
- studying
- fitness
- business tasks
- cleaning
- learning languages
- life organization
- creative work
- anything else the user wants to complete

The runtime adapts based on:
- friction
- momentum
- completion history
- preferred framing
- cognitive load
- user energy
"""

from __future__ import annotations

from typing import Any, Dict


class AdaptiveRuntimeEngine:
    def analyze_state(self, workspace: Dict[str, Any], user_output: str) -> Dict[str, Any]:
        text = (user_output or "").lower()

        friction = any(
            phrase in text
            for phrase in [
                "confused",
                "hard",
                "stuck",
                "overwhelmed",
                "don't understand",
                "too much",
            ]
        )

        momentum = any(
            phrase in text
            for phrase in [
                "finished",
                "done",
                "easy",
                "i got it",
                "completed",
                "working",
            ]
        )

        return {
            "friction_detected": friction,
            "momentum_detected": momentum,
            "recommended_mode": self._recommend_mode(friction, momentum),
        }

    def _recommend_mode(self, friction: bool, momentum: bool) -> str:
        if friction:
            return "reduce_cognitive_load"
        if momentum:
            return "increase_challenge"
        return "normal_progression"

    def generate_runtime_adjustment(self, state: Dict[str, Any]) -> Dict[str, Any]:
        mode = state.get("recommended_mode", "normal_progression")

        adjustments = {
            "reduce_cognitive_load": {
                "step_size": "smaller",
                "rewrite_mode": "adhd_mode",
                "tone": "supportive",
            },
            "increase_challenge": {
                "step_size": "larger",
                "rewrite_mode": "advanced_mode",
                "tone": "momentum",
            },
            "normal_progression": {
                "step_size": "normal",
                "rewrite_mode": "standard",
                "tone": "neutral",
            },
        }

        return adjustments.get(mode, adjustments["normal_progression"])
