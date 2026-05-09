class SemanticDecompositionEngine:
    """Transforms large ambiguous objectives into executable paths."""

    def decompose(self, objective: str):
        return {
            "objective": objective,
            "dependencies": self.detect_dependencies(objective),
            "cognitive_friction": self.detect_friction(objective),
            "completion_paths": self.generate_paths(objective),
        }

    def detect_dependencies(self, objective: str):
        return [
            "research",
            "planning",
            "execution",
            "review",
        ]

    def detect_friction(self, objective: str):
        lowered = objective.lower()

        if "overdue" in lowered:
            return "avoidance"

        if "10 page" in lowered:
            return "overwhelm"

        return "normal"

    def generate_paths(self, objective: str):
        return [
            {
                "mode": "structured",
                "focus": "clarity",
            },
            {
                "mode": "momentum",
                "focus": "small_wins",
            },
            {
                "mode": "expert",
                "focus": "speed",
            },
        ]
