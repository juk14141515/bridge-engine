class PersistenceLayer:
    """Database abstraction for users, workflows, events, memory, and graph state."""

    SUPPORTED_BACKENDS = ["sqlite", "postgres", "supabase", "local_json"]

    def __init__(self, backend: str = "sqlite"):
        self.backend = backend if backend in self.SUPPORTED_BACKENDS else "sqlite"

    def save(self, table: str, payload: dict):
        return {
            "backend": self.backend,
            "table": table,
            "payload": payload,
            "status": "queued_for_persistence",
        }

    def load(self, table: str, query: dict):
        return {
            "backend": self.backend,
            "table": table,
            "query": query,
            "records": [],
        }
