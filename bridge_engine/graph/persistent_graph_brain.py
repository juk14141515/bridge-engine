from datetime import datetime


class PersistentGraphBrain:
    """Stores relationships between users, interests, workflows, skills, projects, emotions, and outcomes."""

    NODE_TYPES = [
        "user_identity",
        "concept",
        "interest",
        "skill",
        "project",
        "workflow",
        "community",
        "emotional_pattern",
        "successful_path",
        "external_motivator",
    ]

    EDGE_TYPES = [
        "relates_to",
        "motivates",
        "reduces_friction_for",
        "helped_complete",
        "caused_abandonment",
        "translates_into",
        "belongs_to_community",
        "supports_identity",
        "requires_skill",
        "produces_output",
    ]

    def __init__(self):
        self.updated_at = datetime.utcnow().isoformat()

    def build_relationship(self, source: dict, target: dict, edge_type: str, weight: float = 1.0):
        return {
            "source": source,
            "target": target,
            "edge_type": edge_type if edge_type in self.EDGE_TYPES else "relates_to",
            "weight": weight,
            "updated_at": self.updated_at,
        }

    def explain_path(self, objective: str, interest: str):
        return {
            "objective": objective,
            "interest": interest,
            "graph_route": [
                "objective",
                "friction_pattern",
                "identity_bridge",
                "interactive_execution",
                "proof_or_export",
            ],
            "purpose": "turn a vague task into a personalized completion path",
        }
