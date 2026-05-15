"""Unified runtime orchestrator.

This is the central brain of Bridge Engine.

It connects:
- adaptive profiles
- interest translation
- task planning
- verification
- adaptive difficulty
- challenge generation
- persistence
- exports
- progression

Goal:
Create a runtime that continuously adapts and becomes harder to abandon.
"""

from __future__ import annotations

from typing import Dict

from bridge_core.adaptive_runtime_engine import AdaptiveRuntimeEngine
from bridge_core.completion_gate_engine import CompletionGateEngine
from bridge_core.enjoyment_mapper import EnjoymentMapper
from bridge_core.interactive_challenge_engine import InteractiveChallengeEngine
from bridge_core.interest_translation_engine import InterestTranslationEngine
from bridge_core.universal_task_planner import UniversalTaskPlanner
from bridge_core.verification_engine import VerificationEngine


class RuntimeOrchestrator:
    def __init__(self):
        self.runtime_engine = AdaptiveRuntimeEngine()
        self.gate_engine = CompletionGateEngine()
        self.challenge_engine = InteractiveChallengeEngine()
        self.translation_engine = InterestTranslationEngine()
        self.verification_engine = VerificationEngine()
        self.task_planner = UniversalTaskPlanner()
        self.enjoyment_mapper = EnjoymentMapper()

    def build_runtime(
        self,
        profile: Dict,
        workspace: Dict,
        latest_output: str = "",
    ) -> Dict:
        task = workspace.get("task", "")
        category = workspace.get("category", "general")

        translation = self.translation_engine.build_translation_layer(
            profile,
            task,
        )

        plan = self.task_planner.build_plan(task, category)

        verification = self.verification_engine.verify_progress(
            workspace,
            latest_output,
        )

        gate = self.gate_engine.evaluate(verification)

        adaptive_state = self.runtime_engine.analyze_state(
            workspace,
            latest_output,
        )

        adjustments = self.runtime_engine.generate_runtime_adjustment(
            adaptive_state,
        )

        challenge = self.challenge_engine.generate_challenge(
            category,
            workspace,
        )

        enjoyment = self.enjoyment_mapper.map_experience(
            task,
            profile.get("interests", []),
        )

        return {
            "translation_layer": translation,
            "plan": plan,
            "verification": verification,
            "gate": gate,
            "adaptive_state": adaptive_state,
            "adjustments": adjustments,
            "challenge": challenge,
            "enjoyment": enjoyment,
        }
