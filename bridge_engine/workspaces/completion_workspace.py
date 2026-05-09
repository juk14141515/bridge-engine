class CompletionWorkspace:
    """Stores in-app execution state for real completion."""

    def create(self, workflow_id: str):
        return {
            "workflow_id": workflow_id,
            "drafts": [],
            "uploads": [],
            "practice": [],
            "exports": [],
            "feedback": [],
            "status": "active",
        }

    def save_draft(self, workspace: dict, draft: dict):
        workspace["drafts"].append(draft)
        return workspace
