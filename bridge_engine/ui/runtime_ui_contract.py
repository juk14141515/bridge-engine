class RuntimeUIContract:
    """Cursor/frontend-facing runtime schema contract."""

    def build_payload(self, runtime_state: dict):
        return {
            "lane_id": runtime_state.get("workflow_id"),
            "status": runtime_state.get("status"),
            "momentum_score": runtime_state.get("momentum_score"),
            "progress_confidence": runtime_state.get("progress_confidence"),
            "current_step": runtime_state.get("current_step"),
            "next_best_action": runtime_state.get("recommended_next_action"),
            "adaptive_mode": runtime_state.get("recommended_mode", "normal"),
            "ui_components": [
                "step_card",
                "feedback_controls",
                "resume_button",
                "momentum_bar",
                "adaptive_hint",
            ],
        }
