"""Environmental intelligence runtime.

Adapts the experience to the user's real-world context.
"""

from __future__ import annotations

from typing import Dict


class EnvironmentalIntelligenceRuntime:
    def build_environment_runtime(self, context: Dict) -> Dict:
        environment = context.get("environment", "default")
        energy = context.get("energy", "normal")
        available_minutes = context.get("available_minutes", 25)

        return {
            "environment_mode": self._environment_mode(environment),
            "session_design": self._session_design(energy, available_minutes),
            "interaction_density": self._interaction_density(environment),
            "recommended_runtime": self._recommended_runtime(environment, energy),
        }

    def _environment_mode(self, environment: str) -> str:
        mapping = {
            "commute": "passive_audio_mode",
            "walking": "voice_interaction_mode",
            "public": "minimal_focus_mode",
            "desktop": "deep_workspace_mode",
            "mobile": "micro_interaction_mode",
            "night": "calm_low_stimulation_mode",
        }
        return mapping.get(environment, "adaptive_mode")

    def _session_design(self, energy: str, minutes: int) -> str:
        if minutes <= 5:
            return "micro_session"
        if energy == "low":
            return "recovery_session"
        if energy == "high":
            return "deep_focus_session"
        return "balanced_session"

    def _interaction_density(self, environment: str) -> str:
        if environment in ["public", "commute"]:
            return "minimal"
        return "adaptive"

    def _recommended_runtime(self, environment: str, energy: str) -> str:
        if environment == "walking":
            return "voice_learning_runtime"
        if energy == "low":
            return "low_friction_runtime"
        return "immersive_runtime"
