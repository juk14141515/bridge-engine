class ExportEngine:
    """Exports completed workflows into usable formats."""

    EXPORTS = [
        "essay_draft",
        "presentation_outline",
        "study_deck",
        "project_plan",
        "code_task_list",
        "markdown",
        "checklist",
        "pdf",
    ]

    def export(self, workflow: dict, export_type: str):
        return {
            "workflow": workflow.get("title"),
            "export_type": export_type,
            "ready": export_type in self.EXPORTS,
        }
