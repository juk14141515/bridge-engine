class OutcomeSimulationEngine:
    """Simulates likely execution outcomes before runtime selection."""

    def simulate(self, objective: str, user_profile: dict):
        completion_probability = self.estimate_completion_probability(user_profile)

        return {
            "objective": objective,
            "completion_probability": completion_probability,
            "friction_points": self.detect_friction(user_profile),
            "recommended_path": self.select_path(user_profile, completion_probability),
            "risk_factors": self.detect_risks(user_profile),
        }

    def estimate_completion_probability(self, user_profile: dict):
        momentum = user_profile.get("momentum", 0.5)
        overwhelm = user_profile.get("overwhelm", 0.2)
        return round(max(0.05, momentum - overwhelm), 2)

    def detect_friction(self, user_profile: dict):
        return [
            "ambiguity",
            "task_initiation",
            "context_switching",
            "motivation_decay",
        ]

    def detect_risks(self, user_profile: dict):
        risks = []

        if user_profile.get("adhd"):
            risks.append("attention_fragmentation")

        if user_profile.get("burnout"):
            risks.append("pacing_collapse")

        return risks

    def select_path(self, user_profile: dict, probability: float):
        if probability < 0.35:
            return "low_friction_recovery_path"

        if user_profile.get("expert"):
            return "expert_acceleration_path"

        return "adaptive_execution_path"
