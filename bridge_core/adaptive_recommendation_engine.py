"""Adaptive recommendation engine.

Suggests better bridges and paths over time.
"""

from __future__ import annotations

from typing import Dict, List


class AdaptiveRecommendationEngine:
    def recommend(
        self,
        interest_scores: Dict,
        path_scores: Dict,
    ) -> Dict:
        strongest_interest = self._strongest_interest(interest_scores)
        strongest_path = self._strongest_path(path_scores)

        return {
            "recommended_interest": strongest_interest,
            "recommended_path": strongest_path,
            "suggestion": self._build_suggestion(
                strongest_interest,
                strongest_path,
            ),
        }

    def _strongest_interest(self, scores: Dict) -> str:
        if not scores:
            return "general"

        return max(scores.items(), key=lambda x: x[1])[0]

    def _strongest_path(self, path_scores: Dict) -> str:
        paths = path_scores.get("best_paths", [])
        if not paths:
            return "general_path"

        return paths[0][0]

    def _build_suggestion(self, interest: str, path: str) -> str:
        return (
            f"You seem to work best through '{interest}' styled progression. "
            f"Your strongest completion path so far is '{path}'."
        )
