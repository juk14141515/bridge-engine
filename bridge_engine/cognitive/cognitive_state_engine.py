class CognitiveStateEngine:
    """Estimates execution state and adjusts runtime support."""

    def evaluate(self, signals: dict):
        return {
            "confidence_estimate": self.estimate_confidence(signals),
            "overwhelm_estimate": self.estimate_overwhelm(signals),
            "attention_state": self.estimate_attention(signals),
            "burnout_probability": self.estimate_burnout(signals),
            "recommended_runtime_mode": self.recommend_mode(signals),
        }

    def estimate_confidence(self, signals: dict):
        return max(0.1, 1 - signals.get("hesitation", 0.2))

    def estimate_overwhelm(self, signals: dict):
        return signals.get("retry_density", 0.1)

    def estimate_attention(self, signals: dict):
        return "fragmented" if signals.get("tab_switching") else "focused"

    def estimate_burnout(self, signals: dict):
        return signals.get("fatigue_score", 0.1)

    def recommend_mode(self, signals: dict):
        if signals.get("fatigue_score", 0) > 0.7:
            return "burnout_recovery"

        if signals.get("retry_density", 0) > 0.6:
            return "micro_step_mode"

        return "adaptive"
