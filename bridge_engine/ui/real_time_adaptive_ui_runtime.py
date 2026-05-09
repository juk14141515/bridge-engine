class RealTimeAdaptiveUIRuntime:
    """Changes interface density, pacing, and interactions in real time."""

    def adapt(self, telemetry: dict):
        if telemetry.get("overwhelm"):
            return {
                "layout": "minimal_focus",
                "step_size": "tiny",
                "animations": "reduced",
            }

        if telemetry.get("high_momentum"):
            return {
                "layout": "high_velocity",
                "step_size": "large",
                "parallel_actions": True,
            }

        return {
            "layout": "adaptive_balanced",
            "step_size": "medium",
        }
