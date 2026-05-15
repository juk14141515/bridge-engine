"""Live interactive runtime engine.

Creates immersive adaptive runtime loops.

Purpose:
Transform learning/execution into an evolving interactive environment.
"""

from __future__ import annotations

from typing import Dict, List


class LiveInteractiveRuntimeEngine:
    def generate_live_runtime(
        self,
        workspace: Dict,
        profile: Dict,
        engagement_state: Dict,
    ) -> Dict:
        modes = self._runtime_modes(profile, engagement_state)

        return {
            "runtime_modes": modes,
            "live_events": self._live_events(engagement_state),
            "reward_runtime": self._reward_runtime(engagement_state),
            "challenge_runtime": self._challenge_runtime(workspace),
            "immersion_state": self._immersion_state(engagement_state),
        }

    def _runtime_modes(self, profile: Dict, engagement: Dict) -> List[str]:
        modes = ["adaptive_progression"]

        if "gaming" in profile.get("interests", []):
            modes += ["quest_runtime", "xp_runtime"]

        if engagement.get("state") == "immersed":
            modes += ["deep_focus_runtime", "combo_runtime"]

        if engagement.get("state") == "disengaging":
            modes += ["micro_reward_runtime", "recovery_runtime"]

        return sorted(set(modes))

    def _live_events(self, engagement: Dict) -> List[Dict]:
        events = []

        if engagement.get("state") == "immersed":
            events.append({
                "type": "focus_chain",
                "reward": "+combo",
            })

        if engagement.get("state") == "disengaging":
            events.append({
                "type": "momentum_recovery",
                "reward": "+micro_win",
            })

        return events

    def _reward_runtime(self, engagement: Dict) -> Dict:
        if engagement.get("state") == "immersed":
            return {
                "frequency": "milestone",
                "style": "achievement_unlocks",
            }

        return {
            "frequency": "high",
            "style": "instant_feedback",
        }

    def _challenge_runtime(self, workspace: Dict) -> Dict:
        category = workspace.get("category", "general")

        mapping = {
            "language_learning": "conversation_battles",
            "coding_project": "debug_quests",
            "essay_writing": "argument_chains",
            "study": "knowledge_duels",
        }

        return {
            "primary_challenge": mapping.get(category, "adaptive_challenges")
        }

    def _immersion_state(self, engagement: Dict) -> str:
        if engagement.get("state") == "immersed":
            return "flow_state"

        if engagement.get("state") == "disengaging":
            return "recovery_state"

        return "active_state"
