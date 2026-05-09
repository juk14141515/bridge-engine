class ExecutionPhysicsEngine:
    """Models how momentum forms, collapses, and recovers during execution."""

    def analyze(self, runtime_data: dict):
        return {
            "momentum_score": self.calculate_momentum(runtime_data),
            "flow_probability": self.calculate_flow(runtime_data),
            "avoidance_risk": self.calculate_avoidance(runtime_data),
            "collapse_risk": self.calculate_collapse(runtime_data),
            "recommended_shift": self.recommend(runtime_data),
        }

    def calculate_momentum(self, runtime_data: dict):
        progress = runtime_data.get("progress", 0.2)
        friction = runtime_data.get("friction", 0.3)
        return round(max(0.0, progress - friction), 2)

    def calculate_flow(self, runtime_data: dict):
        return runtime_data.get("engagement", 0.4)

    def calculate_avoidance(self, runtime_data: dict):
        return runtime_data.get("avoidance", 0.2)

    def calculate_collapse(self, runtime_data: dict):
        return runtime_data.get("collapse_risk", 0.1)

    def recommend(self, runtime_data: dict):
        if runtime_data.get("collapse_risk", 0) > 0.6:
            return "reduce_scope_and_restore_momentum"

        if runtime_data.get("engagement", 0) < 0.3:
            return "identity_reinforcement"

        return "maintain_execution_velocity"
