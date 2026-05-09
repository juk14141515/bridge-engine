from datetime import datetime


class LiveRuntimeOrchestrator:
    """Coordinates live execution state, runtime adaptation, and orchestration."""

    def orchestrate(self, runtime_state: dict):
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "runtime_mode": self.select_runtime(runtime_state),
            "ui_update_required": True,
            "agent_coordination_required": True,
            "next_best_action": runtime_state.get("recommended_next_action"),
        }

    def select_runtime(self, runtime_state: dict):
        if runtime_state.get("stuck_detected"):
            return "recovery_runtime"

        if runtime_state.get("momentum_score", 50) > 80:
            return "high_velocity_runtime"

        return "adaptive_runtime"
