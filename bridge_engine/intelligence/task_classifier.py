class TaskClassifier:
    """Classifies ingested tasks into execution categories."""

    CATEGORIES = [
        "essay",
        "coding_project",
        "language_learning",
        "presentation",
        "study_session",
        "business_project",
        "application",
        "fitness",
        "creative_project",
        "relationship_context",
        "social_understanding",
    ]

    def classify(self, text: str):
        lowered = text.lower()

        if "essay" in lowered or "paper" in lowered:
            return "essay"

        if "code" in lowered or "program" in lowered:
            return "coding_project"

        if "spanish" in lowered or "language" in lowered:
            return "language_learning"

        if "girlfriend" in lowered or "relationship" in lowered:
            return "relationship_context"

        if "gaming" in lowered or "game" in lowered:
            return "social_understanding"

        return "study_session"
