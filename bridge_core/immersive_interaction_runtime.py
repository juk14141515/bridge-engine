"""Immersive interaction runtime.

This layer dynamically selects interaction systems based on:
- task type
- engagement state
- cognitive profile
- user interests
- friction level
- learning target
- runtime momentum

Goal:
Make interaction feel adaptive instead of static.
"""

from __future__ import annotations

from typing import Dict, List


class ImmersiveInteractionRuntime:
    def build_interaction_stack(
        self,
        profile: Dict,
        workspace: Dict,
        runtime_state: Dict,
    ) -> Dict:
        task_type = workspace.get("category", "general")
        engagement = runtime_state.get("engagement_state", "engaged")
        interests = profile.get("interests", [])

        interactions = self._select_interactions(
            task_type,
            engagement,
            interests,
        )

        return {
            "task_type": task_type,
            "engagement_state": engagement,
            "interaction_modes": interactions,
            "ui_runtime_mode": self._ui_mode(engagement),
            "adaptive_density": self._density(runtime_state),
        }

    def _select_interactions(
        self,
        task_type: str,
        engagement: str,
        interests: List[str],
    ) -> List[str]:
        base = ["micro_progress", "adaptive_checkpoints"]

        if task_type == "language_learning":
            base += [
                "rapid_recall",
                "conversation_simulation",
                "pronunciation_loop",
                "memory_chain",
            ]

        elif task_type == "coding_project":
            base += [
                "debug_missions",
                "ship_cycles",
                "architecture_map",
                "live_build_mode",
            ]

        elif task_type == "essay_writing":
            base += [
                "argument_battles",
                "outline_chain",
                "thesis_refinement",
                "draft_combo",
            ]

        elif task_type == "study":
            base += [
                "active_recall",
                "teach_back",
                "speed_rounds",
                "knowledge_duels",
            ]

        if "gaming" in interests:
            base += ["quests", "xp_system", "boss_battles"]

        if engagement == "disengaging":
            base += ["micro_wins", "instant_rewards"]

        return sorted(set(base))

    def _ui_mode(self, engagement: str) -> str:
        if engagement == "immersed":
            return "deep_focus"
        if engagement == "disengaging":
            return "minimal_recovery"
        return "balanced"

    def _density(self, runtime_state: Dict) -> str:
        if runtime_state.get("overwhelmed"):
            return "low"
        if runtime_state.get("hyperfocused"):
            return "high"
        return "balanced"
