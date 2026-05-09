class SemanticWorkflowPlanner:
    """Builds adaptive execution workflows from semantic intent."""

    def plan(self, objective: str, profile: dict):
        return {
            "objective": objective,
            "workflow_mode": self.detect_mode(profile),
            "execution_layers": [
                "decomposition",
                "interaction",
                "feedback",
                "export",
            ],
            "adaptive_adjustments": True,
        }

    def detect_mode(self, profile: dict):
        if profile.get("burnout"):
            return "recovery"

        if profile.get("expert"):
            return "accelerated"

        return "adaptive"
