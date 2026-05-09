class CognitiveStateEngine:
    """Estimates execution state and adjusts runtime support.

    All numeric cognitive outputs are normalized to the 0.0-1.0 range so
    synthetic and real telemetry can be compared safely over time.
    """

    def evaluate(self, signals: dict):
        normalized = self.normalize_signals(signals)

        return {
            "confidence_estimate": self.estimate_confidence(normalized),
            "overwhelm_estimate": self.estimate_overwhelm(normalized),
            "attention_state": self.estimate_attention(normalized),
            "burnout_probability": self.estimate_burnout(normalized),
            "recommended_runtime_mode": self.recommend_mode(normalized),
            "normalized_signals": normalized,
        }

    def clamp01(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, value))

    def normalize_count(self, value, soft_max=10):
        """Convert raw counts like retries/tab switches into a probability-like score."""
        try:
            value = float(value)
        except (TypeError, ValueError):
            return 0.0
        if value <= 1:
            return self.clamp01(value)
        return self.clamp01(value / soft_max)

    def normalize_signals(self, signals: dict):
        return {
            "hesitation": self.clamp01(signals.get("hesitation", 0.2)),
            "retry_density": self.normalize_count(signals.get("retry_density", 0), soft_max=10),
            "fatigue_score": self.clamp01(signals.get("fatigue_score", 0.1)),
            "tab_switching": bool(signals.get("tab_switching", False)),
            "inactivity_bursts": self.normalize_count(signals.get("inactivity_bursts", 0), soft_max=8),
            "abandonment_events": self.normalize_count(signals.get("abandonment_events", 0), soft_max=5),
        }

    def estimate_confidence(self, signals: dict):
        hesitation = signals.get("hesitation", 0.2)
        retry_pressure = signals.get("retry_density", 0.0) * 0.25
        return self.clamp01(max(0.1, 1 - hesitation - retry_pressure))

    def estimate_overwhelm(self, signals: dict):
        retry_density = signals.get("retry_density", 0.1)
        inactivity = signals.get("inactivity_bursts", 0.0)
        abandonment = signals.get("abandonment_events", 0.0)
        fatigue = signals.get("fatigue_score", 0.1)
        return self.clamp01((retry_density * 0.45) + (inactivity * 0.2) + (abandonment * 0.2) + (fatigue * 0.15))

    def estimate_attention(self, signals: dict):
        if signals.get("tab_switching") or signals.get("inactivity_bursts", 0) > 0.5:
            return "fragmented"
        return "focused"

    def estimate_burnout(self, signals: dict):
        fatigue = signals.get("fatigue_score", 0.1)
        abandonment = signals.get("abandonment_events", 0.0)
        return self.clamp01((fatigue * 0.75) + (abandonment * 0.25))

    def recommend_mode(self, signals: dict):
        burnout = self.estimate_burnout(signals)
        overwhelm = self.estimate_overwhelm(signals)

        if burnout > 0.7:
            return "burnout_recovery"

        if overwhelm > 0.6:
            return "micro_step_mode"

        if overwhelm < 0.25 and burnout < 0.25:
            return "fast_or_expert_mode"

        return "adaptive"
