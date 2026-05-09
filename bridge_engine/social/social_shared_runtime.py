class SocialSharedRuntime:
    """Supports collaborative execution, accountability, and relationship bridges."""

    FEATURES = [
        "shared_goals",
        "accountability_partners",
        "mentor_paths",
        "team_workflows",
        "relationship_bridges",
        "collaborative_execution",
        "learning_communities",
    ]

    def create_shared_runtime(self, participants: list[str], objective: str):
        return {
            "participants": participants,
            "objective": objective,
            "shared_state": "active",
            "collaboration_mode": self.detect_mode(objective),
        }

    def detect_mode(self, objective: str):
        if "relationship" in objective.lower() or "partner" in objective.lower():
            return "relationship_bridge"

        if "team" in objective.lower():
            return "team_execution"

        return "shared_learning"
