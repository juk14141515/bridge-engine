"""Completion gate engine.

Controls progression through runtime phases.
"""

from __future__ import annotations

from typing import Dict


class CompletionGateEngine:
    def evaluate(self, verification_result: Dict) -> Dict:
        confidence = verification_result.get("confidence_score", 0)
        verified = verification_result.get("verified", False)

        if verified and confidence >= 75:
            return {
                "advance": True,
                "mode": "full_unlock",
            }

        if verified:
            return {
                "advance": True,
                "mode": "soft_unlock",
            }

        return {
            "advance": False,
            "mode": "checkpoint_required",
        }
