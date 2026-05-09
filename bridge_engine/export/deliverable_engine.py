class DeliverableEngine:
    """Creates external deliverables from completed workflows."""

    def build(self, workflow: dict, output_type: str):
        return {
            "workflow_id": workflow.get("id"),
            "output_type": output_type,
            "status": "ready",
            "formats": [
                "pdf",
                "markdown",
                "slides",
                "study_deck",
                "checklist",
            ],
        }
