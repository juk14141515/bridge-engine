"""Contextual intelligence runtime.

Core philosophy:
Immersion should adapt to the user.

Bridge should NOT feel childish unless the user benefits from that style.
Different users require radically different interaction architectures.

Examples:
- child learning multiplication
- ADHD student overwhelmed by essays
- dyslexic learner
- burned out professional
- software engineer shipping production systems
- executive planning strategy
- researcher studying deeply

The runtime therefore adapts:
- interaction density
- emotional tone
- reward visibility
- challenge style
- pacing
- immersion depth
- seriousness/professionalism
- cognitive load
- recovery systems

Goal:
Make the experience feel intentionally designed for THAT person.
"""

from __future__ import annotations

from typing import Dict


class ContextualIntelligenceRuntime:
    def build_contextual_runtime(
        self,
        profile: Dict,
        runtime_state: Dict,
        workspace: Dict,
    ) -> Dict:
        cognitive = profile.get("cognitive_profile", {})
        maturity = profile.get("interaction_style", "adaptive")
        engagement = runtime_state.get("engagement_state", "balanced")

        return {
            "interaction_architecture": self._interaction_architecture(
                maturity,
                engagement,
                cognitive,
            ),
            "tone_runtime": self._tone_runtime(profile),
            "immersion_runtime": self._immersion_runtime(profile),
            "friction_response": self._friction_response(cognitive),
            "reward_visibility": self._reward_visibility(profile),
            "session_shape": self._session_shape(runtime_state),
            "professionalism_layer": self._professionalism_layer(profile),
            "adaptive_complexity": self._adaptive_complexity(runtime_state),
            "continuation_strategy": self._continuation_strategy(runtime_state),
            "environment_feel": self._environment_feel(profile),
        }

    def _interaction_architecture(
        self,
        maturity: str,
        engagement: str,
        cognitive: Dict,
    ) -> str:
        if maturity == "professional":
            return "minimal_high_signal_runtime"

        if maturity == "student":
            return "guided_interactive_runtime"

        if cognitive.get("adhd"):
            return "momentum_driven_runtime"

        if cognitive.get("dyslexia"):
            return "reduced_density_runtime"

        if engagement == "immersed":
            return "deep_flow_runtime"

        return "adaptive_balanced_runtime"

    def _tone_runtime(self, profile: Dict) -> str:
        tone = profile.get("preferred_tone")

        if tone:
            return tone

        if profile.get("interaction_style") == "professional":
            return "focused_professional"

        return "supportive_adaptive"

    def _immersion_runtime(self, profile: Dict) -> str:
        style = profile.get("interaction_style")

        mapping = {
            "professional": "subtle_immersive",
            "student": "guided_immersive",
            "gaming": "high_interaction",
            "minimal": "calm_focus",
        }

        return mapping.get(style, "adaptive_immersive")

    def _friction_response(self, cognitive: Dict) -> str:
        if cognitive.get("overwhelm_sensitive"):
            return "micro_recovery"

        if cognitive.get("high_focus"):
            return "deep_focus_extension"

        return "balanced_support"

    def _reward_visibility(self, profile: Dict) -> str:
        if profile.get("interaction_style") == "professional":
            return "subtle"

        if profile.get("likes_visible_progress"):
            return "high_visibility"

        return "balanced"

    def _session_shape(self, runtime_state: Dict) -> str:
        if runtime_state.get("hyperfocused"):
            return "long_flow_chain"

        if runtime_state.get("overwhelmed"):
            return "single_step_focus"

        return "adaptive_chain"

    def _professionalism_layer(self, profile: Dict) -> str:
        if profile.get("interaction_style") == "professional":
            return "executive_runtime"

        return "general_runtime"

    def _adaptive_complexity(self, runtime_state: Dict) -> str:
        if runtime_state.get("high_friction"):
            return "reduce_complexity"

        if runtime_state.get("high_momentum"):
            return "increase_complexity"

        return "balanced_complexity"

    def _continuation_strategy(self, runtime_state: Dict) -> str:
        if runtime_state.get("dropoff_risk"):
            return "instant_reentry"

        return "progressive_continuation"

    def _environment_feel(self, profile: Dict) -> str:
        if profile.get("interaction_style") == "professional":
            return "calm_premium_workspace"

        if profile.get("interaction_style") == "student":
            return "interactive_guided_workspace"

        return "adaptive_environment"
