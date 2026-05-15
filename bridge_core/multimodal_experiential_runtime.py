"""Multimodal experiential runtime.

Bridge should not feel limited to text chat.

This layer enables:
- visual learning
- vocal learning
- speaking practice
- auditory reinforcement
- diagrams
- whiteboards
- interactive builders
- simulations
- collaborative environments
- multimodal reinforcement

Goal:
Adapt to HOW people actually learn.
"""

from __future__ import annotations

from typing import Dict, List


class MultimodalExperientialRuntime:
    def build_runtime(
        self,
        profile: Dict,
        workspace: Dict,
    ) -> Dict:
        cognitive = profile.get("cognitive_profile", {})
        preferences = profile.get("learning_preferences", [])

        return {
            "modalities": self._modalities(preferences, cognitive),
            "voice_runtime": self._voice_runtime(profile),
            "visual_runtime": self._visual_runtime(profile),
            "interactive_runtime": self._interactive_runtime(workspace),
            "memory_reinforcement": self._memory_reinforcement(profile),
            "sensory_density": self._sensory_density(profile),
        }

    def _modalities(self, preferences: List[str], cognitive: Dict) -> List[str]:
        modes = ["text"]

        if "visual" in preferences:
            modes += ["diagrams", "visual_maps", "whiteboard"]

        if "audio" in preferences:
            modes += ["voice", "speaking", "listening"]

        if cognitive.get("adhd"):
            modes += ["interactive", "rapid_feedback"]

        return sorted(set(modes))

    def _voice_runtime(self, profile: Dict) -> Dict:
        return {
            "enabled": True,
            "conversation_learning": True,
            "pronunciation_feedback": True,
            "voice_reflection": True,
            "speech_practice": True,
            "adaptive_speaking_mode": self._speaking_mode(profile),
        }

    def _speaking_mode(self, profile: Dict) -> str:
        if profile.get("interaction_style") == "professional":
            return "executive_conversation"

        return "guided_conversation"

    def _visual_runtime(self, profile: Dict) -> Dict:
        return {
            "mindmaps": True,
            "visual_progression": True,
            "diagram_generation": True,
            "concept_mapping": True,
        }

    def _interactive_runtime(self, workspace: Dict) -> Dict:
        category = workspace.get("category", "general")

        return {
            "sandbox_mode": True,
            "simulation_mode": True,
            "adaptive_builder": category,
            "live_interaction": True,
        }

    def _memory_reinforcement(self, profile: Dict) -> Dict:
        return {
            "spaced_repetition": True,
            "active_recall": True,
            "multimodal_recall": True,
            "voice_repetition": True,
        }

    def _sensory_density(self, profile: Dict) -> str:
        if profile.get("interaction_style") == "minimal":
            return "low"

        return "adaptive"
