class RealityLayerEngine:
    """Represents the external systems where real-world friction occurs."""

    INTEGRATIONS = [
        "browser_extension",
        "ide_integrations",
        "google_docs",
        "notion",
        "github",
        "canvas_lms",
        "blackboard",
        "obsidian",
        "calendar",
        "reminders",
        "wearables",
        "screen_state_understanding",
    ]

    def connect(self, integration_name: str):
        return {
            "integration": integration_name,
            "status": "scaffolded",
            "purpose": "reduce friction where execution actually happens",
        }

    def recommended_integrations(self, objective: str):
        objective = objective.lower()

        if "code" in objective:
            return ["github", "ide_integrations"]

        if "school" in objective or "assignment" in objective:
            return ["canvas_lms", "google_docs"]

        if "planning" in objective:
            return ["calendar", "notion"]

        return ["browser_extension", "reminders"]
