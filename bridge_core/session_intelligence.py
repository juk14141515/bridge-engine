class SessionIntelligence:
    """Detects momentum, friction, and avoidance patterns."""

    def analyze(self, session):
        outputs = []
        for step in session.get("steps", []):
            outputs.append(len(step.get("user_output", "").strip()))

        completed = len([
            s for s in session.get("steps", [])
            if s.get("status") == "done"
        ])

        total = max(1, len(session.get("steps", [])))
        completion_rate = int((completed / total) * 100)

        avg_output = sum(outputs) / max(1, len(outputs))

        state = "starting"

        if completion_rate >= 75:
            state = "flow"
        elif avg_output < 10 and completed == 0:
            state = "stuck"
        elif completed >= 1:
            state = "building"

        return {
            "completion_rate": completion_rate,
            "average_output_size": avg_output,
            "state": state,
            "recommendation": self.recommend(state),
        }

    def recommend(self, state):
        recommendations = {
            "starting": "Lower activation energy and create a visible win.",
            "building": "Continue momentum with another achievable checkpoint.",
            "flow": "Increase challenge slightly while preserving momentum.",
            "stuck": "Break the task smaller and provide examples immediately.",
        }
        return recommendations.get(state, "Continue guided support.")
