from datetime import datetime


class UserTelemetryLearning:
    """Learns from interaction telemetry and execution behavior over time."""

    def process(self, telemetry: dict):
        return {
            "processed_at": datetime.utcnow().isoformat(),
            "signals": [
                "hesitation",
                "momentum",
                "abandonment",
                "engagement",
                "interaction_preference",
            ],
            "recommended_runtime_updates": self.recommend(telemetry),
        }

    def recommend(self, telemetry: dict):
        updates = []

        if telemetry.get("rapid_exits"):
            updates.append("reduce_visual_density")

        if telemetry.get("high_completion"):
            updates.append("increase_depth")

        if telemetry.get("voice_usage"):
            updates.append("prioritize_voice_interactions")

        return updates
