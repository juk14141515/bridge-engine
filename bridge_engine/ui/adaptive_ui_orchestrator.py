class AdaptiveUIOrchestrator:
    """Dynamically changes the interface based on execution state."""

    def adapt(self, runtime_state: dict):
        momentum = runtime_state.get("momentum_score", 50)

        if momentum < 40:
            return {
                "layout": "focus_mode",
                "step_size": "tiny",
                "visual_density": "low",
            }

        if momentum > 75:
            return {
                "layout": "expert_mode",
                "step_size": "large",
                "visual_density": "high",
            }

        return {
            "layout": "adaptive",
            "step_size": "medium",
            "visual_density": "balanced",
        }
