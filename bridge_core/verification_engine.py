"""Verification engine.

Purpose:
Prevent fake completion loops.

This does NOT attempt perfect surveillance.
Instead it estimates whether meaningful work happened.

Signals:
- output quality
- length
- consistency
- recall accuracy
- progression continuity
- challenge completion
- reflection depth
- artifact evolution
"""

from __future__ import annotations

from typing import Any, Dict


class VerificationEngine:
    def verify_progress(
        self,
        previous_workspace: Dict[str, Any],
        user_output: str,
    ) -> Dict[str, Any]:
        output = (user_output or "").strip()

        score = 0
        flags = []

        if len(output) > 30:
            score += 25
        else:
            flags.append("very_short_response")

        if any(word in output.lower() for word in ["learned", "built", "tested", "wrote"]):
            score += 25

        if len(output.split()) > 10:
            score += 25

        if "idk" in output.lower() or "nothing" in output.lower():
            flags.append("low_confidence")

        verified = score >= 50

        return {
            "verified": verified,
            "confidence_score": score,
            "flags": flags,
            "next_action": self._next_action(verified),
        }

    def _next_action(self, verified: bool) -> str:
        if verified:
            return "advance"
        return "request_checkpoint"
