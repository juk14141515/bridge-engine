class CompletionConfidenceEngine:
    """Estimates completion readiness and execution confidence."""

    def evaluate(self, runtime_state: dict):
        momentum = runtime_state.get("momentum_score", 50)

        return {
            "completion_likelihood": min(momentum + 20, 100),
            "ambiguity_level": max(100 - momentum, 10),
            "recommended_structure": self.structure_level(momentum),
        }

    def structure_level(self, momentum: int):
        if momentum < 40:
            return "high_structure"

        if momentum > 75:
            return "low_structure"

        return "moderate_structure"
