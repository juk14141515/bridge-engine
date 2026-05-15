"""Adaptive interest discovery engine.

Learns evolving interests from:
- workspace usage
- completed tasks
- recurring themes
- user language
- successful completion paths
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, List


class InterestDiscoveryEngine:
    def discover(
        self,
        existing_interests: List[str],
        user_outputs: List[str],
    ) -> Dict:
        text = " ".join(user_outputs).lower()

        candidate_map = {
            "coding": ["code", "python", "app", "build", "software"],
            "investing": ["stocks", "investing", "trading", "finance"],
            "fitness": ["gym", "workout", "fitness", "lifting"],
            "gaming": ["game", "gaming", "quest", "level"],
            "music": ["music", "song", "playlist"],
            "psychology": ["mind", "adhd", "psychology", "behavior"],
            "dogs": ["dog", "puppy", "ponder"],
        }

        scores = Counter()

        for category, keywords in candidate_map.items():
            for keyword in keywords:
                if keyword in text:
                    scores[category] += 1

        discovered = [
            interest
            for interest, score in scores.items()
            if score >= 2 and interest not in existing_interests
        ]

        return {
            "existing_interests": existing_interests,
            "discovered_interests": discovered,
            "interest_scores": dict(scores),
        }
