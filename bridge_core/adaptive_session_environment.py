"""Adaptive session environment.

Shapes sessions around real-world user conditions.
"""

from __future__ import annotations

from typing import Dict


class AdaptiveSessionEnvironment:
    def build(self, runtime_state: Dict) -> Dict:
        return {
            "focus_mode": self._focus_mode(runtime_state),
            "session_length": self._session_length(runtime_state),
            "complexity": self._complexity(runtime_state),
            "reentry_support": self._reentry_support(runtime_state),
        }

    def _focus_mode(self, runtime_state: Dict) -> str:
        if runtime_state.get("interrupted"):
            return "quick_resume_mode"
        if runtime_state.get("hyperfocused"):
            return "deep_flow_mode"
        return "balanced_focus_mode"

    def _session_length(self, runtime_state: Dict) -> str:
        if runtime_state.get("low_energy"):
            return "short"
        if runtime_state.get("high_focus"):
            return "extended"
        return "adaptive"

    def _complexity(self, runtime_state: Dict) -> str:
        if runtime_state.get("overwhelmed"):
            return "reduced"
        return "adaptive"

    def _reentry_support(self, runtime_state: Dict) -> str:
        if runtime_state.get("dropoff_risk"):
            return "high"
        return "balanced"
