from datetime import datetime


class UniversalTaskRuntime:
    """Core execution orchestrator for completion workflows."""

    def initialize(self, workflow: dict):
        return {
            "workflow_id": workflow.get("id"),
            "status": "running",
            "current_step": 1,
            "momentum_score": 50,
            "progress_confidence": 50,
            "last_activity": datetime.utcnow().isoformat(),
            "interruption_detected": False,
            "stuck_detected": False,
            "recommended_next_action": workflow.get("steps", [])[0] if workflow.get("steps") else None,
        }

    def detect_stuck_state(self, runtime_state: dict, inactivity_minutes: int):
        if inactivity_minutes > 45:
            runtime_state["stuck_detected"] = True
            runtime_state["momentum_score"] -= 10

        return runtime_state

    def recover_interruption(self, runtime_state: dict):
        runtime_state["interruption_detected"] = False
        runtime_state["recommended_mode"] = "recovery"
        return runtime_state
