"""Voice learning runtime.

Voice should be a first-class learning system.

Supports:
- speaking practice
- conversational learning
- verbal recall
- verbal reflection
- pronunciation loops
- confidence building
- interview simulations
- presentation practice
- language immersion
"""

from __future__ import annotations

from typing import Dict


class VoiceLearningRuntime:
    def build_voice_session(
        self,
        category: str,
        profile: Dict,
    ) -> Dict:
        return {
            "voice_mode": self._voice_mode(category),
            "conversation_style": self._conversation_style(profile),
            "speech_feedback": True,
            "repetition_loops": True,
            "live_speaking_prompts": True,
            "confidence_support": True,
            "reflection_prompts": self._reflection_prompts(category),
        }

    def _voice_mode(self, category: str) -> str:
        mapping = {
            "language_learning": "language_immersion",
            "essay_writing": "argument_speaking",
            "coding_project": "architecture_explanation",
            "study": "teach_back_mode",
        }

        return mapping.get(category, "adaptive_voice_mode")

    def _conversation_style(self, profile: Dict) -> str:
        if profile.get("interaction_style") == "professional":
            return "professional_dialogue"

        return "supportive_dialogue"

    def _reflection_prompts(self, category: str):
        prompts = {
            "language_learning": "Say the phrase naturally without reading.",
            "essay_writing": "Explain your thesis out loud.",
            "coding_project": "Describe the system architecture verbally.",
            "study": "Teach the topic back in your own words.",
        }

        return prompts.get(category, "Explain what you learned today.")
