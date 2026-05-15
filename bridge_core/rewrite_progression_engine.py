from __future__ import annotations

from typing import Any, Dict


REWRITE_WEIGHTS = {
    "make_easier": 12,
    "break_smaller": 18,
    "give_example": 15,
    "explain_differently": 10,
    "continue": 5,
}


class RewriteProgressionEngine:
    def score(self, mode: str, before_prompt: str = "", after_prompt: str = "") -> Dict[str, Any]:
        base = REWRITE_WEIGHTS.get(mode, 8)
        before_words = len((before_prompt or "").split())
        after_words = len((after_prompt or "").split())
        shortened = before_words > 0 and after_words <= before_words
        score = min(base + (8 if shortened else 3), 100)
        return {
            "mode": mode,
            "rewrite_score": score,
            "shortened_prompt": shortened,
            "before_words": before_words,
            "after_words": after_words,
            "recommendation": self.recommendation(mode, score),
        }

    def recommendation(self, mode: str, score: int) -> str:
        if mode == "break_smaller":
            return "Continue with smaller steps until output improves."
        if mode == "give_example":
            return "Follow with a user-owned version after the example."
        if score >= 20:
            return "Rewrite likely improved momentum."
        return "Try a different rewrite mode if the user remains stuck."
