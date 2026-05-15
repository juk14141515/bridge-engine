from __future__ import annotations

from typing import Any, Dict, Optional

from bridge_core.adaptive_interaction_selector import AdaptiveInteractionSelector
from bridge_core.adaptive_pacing_engine import AdaptivePacingEngine
from bridge_core.adaptive_runtime_engine import AdaptiveRuntimeEngine
from bridge_core.adaptive_session_environment import AdaptiveSessionEnvironment
from bridge_core.artifact_builder_registry import ArtifactBuilderRegistry
from bridge_core.comeback_runtime import ComebackRuntime
from bridge_core.completion_gate_engine import CompletionGateEngine
from bridge_core.contextual_intelligence_runtime import ContextualIntelligenceRuntime
from bridge_core.dynamic_challenge_chain import DynamicChallengeChain
from bridge_core.engagement_score_engine import EngagementScoreEngine
from bridge_core.environmental_intelligence_runtime import EnvironmentalIntelligenceRuntime
from bridge_core.immersive_interaction_runtime import ImmersiveInteractionRuntime
from bridge_core.interest_translation_engine import InterestTranslationEngine
from bridge_core.interruption_recovery_runtime import InterruptionRecoveryRuntime
from bridge_core.live_interactive_runtime_engine import LiveInteractiveRuntimeEngine
from bridge_core.multimodal_experiential_runtime import MultimodalExperientialRuntime
from bridge_core.multimodal_pathway_selector import MultimodalPathwaySelector
from bridge_core.passive_reinforcement_runtime import PassiveReinforcementRuntime
from bridge_core.realtime_reward_runtime import RealtimeRewardRuntime
from bridge_core.runtime_minigame_engine import RuntimeMinigameEngine
from bridge_core.runtime_schema import build_envelope, ensure_workspace
from bridge_core.runtime_simulation_engine import RuntimeSimulationEngine
from bridge_core.universal_task_planner import UniversalTaskPlanner
from bridge_core.verification_engine import VerificationEngine
from bridge_core.voice_learning_runtime import VoiceLearningRuntime
from bridge_core.workspace_persistence import WorkspacePersistence


class MasterRuntimeOrchestrator:
    """Top-level Bridge runtime contract.

    Coordinates planning, interaction, verification, adaptation, reward,
    persistence, continuation, and export-ready state in one response shape.
    """

    def __init__(self, profile: Optional[Dict[str, Any]] = None, context: Optional[Dict[str, Any]] = None):
        self.profile = profile or {}
        self.context = context or {}
        self.persistence = WorkspacePersistence()

    def build_contract(self, workspace: Dict[str, Any], latest_output: str = "", persist: bool = False) -> Dict[str, Any]:
        workspace = ensure_workspace(workspace)
        category = workspace.get("category", "general")
        runtime_state = workspace.get("runtime_state", {})

        verification = VerificationEngine().verify_progress(workspace, latest_output)
        gate = CompletionGateEngine().evaluate(verification)
        adaptive_state = AdaptiveRuntimeEngine().analyze_state(workspace, latest_output)
        adaptive_adjustments = AdaptiveRuntimeEngine().generate_runtime_adjustment(adaptive_state)

        engagement = EngagementScoreEngine().calculate({
            "momentum_bonus": 20 if adaptive_state.get("momentum_detected") else 0,
            "friction_penalty": 25 if adaptive_state.get("friction_detected") else 0,
            "challenge_bonus": 10 if gate.get("advance") else 0,
        })
        runtime_state["engagement_state"] = engagement.get("state")
        runtime_state["high_friction"] = adaptive_state.get("friction_detected", False)
        runtime_state["high_momentum"] = adaptive_state.get("momentum_detected", False)
        workspace["runtime_state"] = runtime_state

        immersive = ImmersiveInteractionRuntime().build_interaction_stack(self.profile, workspace, runtime_state)

        if persist and workspace.get("id"):
            try:
                self.persistence.save_workspace(workspace)
            except Exception:
                pass

        envelope = build_envelope(workspace)
        envelope.update({
            "orchestrator": "master_runtime_orchestrator_v1",
            "plan": UniversalTaskPlanner().build_plan(workspace.get("task", ""), category),
            "verification": verification,
            "gate": gate,
            "adaptive_state": adaptive_state,
            "adaptive_adjustments": adaptive_adjustments,
            "engagement": engagement,
            "contextual_runtime": ContextualIntelligenceRuntime().build_contextual_runtime(self.profile, runtime_state, workspace),
            "environmental_runtime": EnvironmentalIntelligenceRuntime().build_environment_runtime(self.context),
            "session_environment": AdaptiveSessionEnvironment().build(runtime_state),
            "interest_translation": InterestTranslationEngine().build_translation_layer(self.profile, workspace.get("task", "")),
            "multimodal_runtime": MultimodalExperientialRuntime().build_runtime(self.profile, workspace),
            "pathways": MultimodalPathwaySelector().select_paths(workspace.get("task", ""), self.profile),
            "interaction_runtime": immersive,
            "interaction_selection": AdaptiveInteractionSelector().select(self.profile, runtime_state, immersive.get("interaction_modes", [])),
            "challenge_chain": DynamicChallengeChain().build_chain(engagement.get("engagement_score", 50)),
            "live_runtime": LiveInteractiveRuntimeEngine().generate_live_runtime(workspace, self.profile, {"state": engagement.get("state")}),
            "minigame": RuntimeMinigameEngine().generate(category),
            "simulation": RuntimeSimulationEngine().generate(category),
            "rewards": RealtimeRewardRuntime().generate_rewards({"engagement": engagement.get("state")}),
            "voice_runtime": VoiceLearningRuntime().build_voice_session(category, self.profile),
            "passive_reinforcement": PassiveReinforcementRuntime().generate(workspace),
            "recovery": InterruptionRecoveryRuntime().recover(workspace),
            "comeback": ComebackRuntime().generate_reentry(workspace),
            "artifact_target": ArtifactBuilderRegistry().build_artifact(category, workspace.get("artifact", {}).get("final_output", "")),
            "pacing": AdaptivePacingEngine().adjust({
                "high_risk": engagement.get("state") == "disengaging",
                "high_flow": engagement.get("state") == "immersed",
            }),
        })
        return envelope
