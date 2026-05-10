from datetime import datetime


class WorkspaceEngine:
    """Persistent workspace orchestration layer."""

    def __init__(self, store=None):
        self.store = store

    def create_workspace(self, session_payload):
        workspace = {
            "id": session_payload.get("id"),
            "title": session_payload.get("task", "Untitled Bridge"),
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "session": session_payload,
            "artifact_state": {
                "draft": {},
                "exports": [],
            },
        }
        if self.store:
            self.store.save_workspace(workspace)
        return workspace

    def save_workspace(self, workspace):
        workspace["updated_at"] = datetime.utcnow().isoformat()
        if self.store:
            self.store.save_workspace(workspace)
        return workspace
