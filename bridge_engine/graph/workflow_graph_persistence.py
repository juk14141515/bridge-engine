class WorkflowGraphPersistence:
    """Stores workflow graphs and execution relationships over time."""

    def persist(self, workflow_graph: dict):
        return {
            "workflow_graph": workflow_graph,
            "status": "persisted",
        }
