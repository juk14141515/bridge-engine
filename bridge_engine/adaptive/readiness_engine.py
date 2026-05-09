class ReadinessEngine:
    """Detects momentum/readiness state for adaptive pacing."""

    STATES = [
        "frozen",
        "hesitant",
        "warming_up",
        "moving",
        "locked_in",
    ]

    def detect(self, metrics: dict):
        completion_speed = metrics.get("completion_speed", 0)
        helped_count = metrics.get("helped_count", 0)
        too_much_count = metrics.get("too_much_count", 0)
        continuation_count = metrics.get("continuation_count", 0)

        if too_much_count >= 3:
            return "frozen"

        if continuation_count <= 1:
            return "hesitant"

        if helped_count >= 2 and completion_speed > 0:
            return "warming_up"

        if helped_count >= 4 and continuation_count >= 3:
            return "moving"

        if helped_count >= 8 and completion_speed >= 2:
            return "locked_in"

        return "hesitant"
