"""Interest translation engine.

A major problem with personalization systems is shallow mapping.
Example:
- user likes music
- app blindly adds random music references

This engine instead learns:
- specific sub-interests
- emotional engagement styles
- pacing tolerance
- attention retention patterns
- aesthetic preferences
- interaction preferences

Goal:
Make the experience genuinely harder to abandon.
"""

from __future__ import annotations

from typing import Dict, List


class InterestTranslationEngine:
    def build_translation_layer(
        self,
        profile: Dict,
        task: str,
    ) -> Dict:
        interests = profile.get("interests", [])
        micro_interests = profile.get("micro_interests", {})
        engagement = profile.get("engagement_patterns", {})

        dominant_interest = self._dominant_interest(interests)
        dominant_micro = self._dominant_micro_interest(micro_interests)

        return {
            "task": task,
            "theme": dominant_interest,
            "micro_theme": dominant_micro,
            "challenge_style": self._challenge_style(dominant_interest),
            "retention_strategy": self._retention_strategy(engagement),
            "dopamine_pattern": self._dopamine_pattern(engagement),
            "session_structure": self._session_structure(engagement),
            "translation_prompt": self._translation_prompt(
                task,
                dominant_interest,
                dominant_micro,
            ),
        }

    def _dominant_interest(self, interests: List[str]) -> str:
        if not interests:
            return "general"
        return interests[0]

    def _dominant_micro_interest(self, micro_interests: Dict) -> str:
        if not micro_interests:
            return "general"
        return max(micro_interests.items(), key=lambda x: x[1])[0]

    def _challenge_style(self, interest: str) -> str:
        mapping = {
            "gaming": "quest_progression",
            "coding": "ship_iterations",
            "fitness": "rep_system",
            "music": "playlist_progression",
            "investing": "thesis_and_reward",
        }
        return mapping.get(interest, "momentum_progression")

    def _retention_strategy(self, engagement: Dict) -> str:
        if engagement.get("abandons_long_sessions"):
            return "micro_sessions"
        if engagement.get("likes_deep_focus"):
            return "deep_work_blocks"
        return "balanced"

    def _dopamine_pattern(self, engagement: Dict) -> str:
        if engagement.get("needs_fast_rewards"):
            return "high_frequency_rewards"
        return "milestone_rewards"

    def _session_structure(self, engagement: Dict) -> str:
        if engagement.get("easily_overwhelmed"):
            return "single_focus_mode"
        return "multi_stage_mode"

    def _translation_prompt(
        self,
        task: str,
        interest: str,
        micro_interest: str,
    ) -> str:
        return (
            f"Translate '{task}' through the lens of '{interest}' "
            f"with emphasis on '{micro_interest}'."
        )
