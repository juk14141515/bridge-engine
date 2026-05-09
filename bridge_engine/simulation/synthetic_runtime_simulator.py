from datetime import datetime

from bridge_engine.simulation.synthetic_user_profiles import SYNTHETIC_USER_PROFILES
from bridge_engine.execution.execution_physics_engine import ExecutionPhysicsEngine
from bridge_engine.cognitive.cognitive_state_engine import CognitiveStateEngine
from bridge_engine.world.world_model_engine import WorldModelEngine
from bridge_engine.media.adaptive_media_recommendation_layer import AdaptiveMediaRecommendationLayer
from bridge_engine.identity.dynamic_identity_translation_engine import DynamicIdentityTranslationEngine
from bridge_engine.runtime.live_runtime_orchestrator import LiveRuntimeOrchestrator


class SyntheticRuntimeSimulator:
    """Runs synthetic users through Bridge execution systems for learning/testing."""

    def __init__(self):
        self.execution_engine = ExecutionPhysicsEngine()
        self.cognitive_engine = CognitiveStateEngine()
        self.world_engine = WorldModelEngine()
        self.media_engine = AdaptiveMediaRecommendationLayer()
        self.identity_engine = DynamicIdentityTranslationEngine()
        self.runtime_engine = LiveRuntimeOrchestrator()

    def run(self):
        simulations = []

        for profile in SYNTHETIC_USER_PROFILES:
            world = self.world_engine.infer_world(
                profile["goal"],
                profile.get("interests", []),
            )

            execution = self.execution_engine.analyze({
                "progress": profile["telemetry"].get("momentum", 0.5),
                "friction": profile["telemetry"].get("overwhelm", 0.2),
                "engagement": profile["telemetry"].get("momentum", 0.5),
                "collapse_risk": profile["telemetry"].get("overwhelm", 0.2),
            })

            cognitive = self.cognitive_engine.evaluate({
                "retry_density": profile["telemetry"].get("retry_count", 0),
                "fatigue_score": profile["telemetry"].get("fatigue_score", 0.1),
            })

            media = self.media_engine.recommend(
                world["world"],
                {
                    "desired_identity": profile["identity"][0],
                },
            )

            identity_bridge = self.identity_engine.translate(
                profile.get("interests", ["general"])[0],
                world["world"],
            )

            runtime = self.runtime_engine.orchestrate({
                "momentum_score": int(execution["momentum_score"] * 100),
                "stuck_detected": "burnout" in profile.get("friction", []),
                "recommended_next_action": profile["goal"],
            })

            simulations.append({
                "user_id": profile["id"],
                "goal": profile["goal"],
                "world": world,
                "execution": execution,
                "cognitive": cognitive,
                "media": media,
                "identity_bridge": identity_bridge,
                "runtime": runtime,
            })

        return {
            "updated_at": datetime.utcnow().isoformat(),
            "simulation_count": len(simulations),
            "simulations": simulations,
        }
