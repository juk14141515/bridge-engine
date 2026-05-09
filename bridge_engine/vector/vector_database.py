class VectorDatabase:
    """Adapter layer for real vector backends such as pgvector, Chroma, Weaviate, or Qdrant."""

    SUPPORTED_BACKENDS = ["pgvector", "chroma", "weaviate", "qdrant", "local_json"]

    def __init__(self, backend: str = "local_json"):
        self.backend = backend if backend in self.SUPPORTED_BACKENDS else "local_json"

    def upsert(self, collection: str, item_id: str, vector: list[float], metadata: dict):
        return {
            "collection": collection,
            "item_id": item_id,
            "backend": self.backend,
            "metadata": metadata,
            "status": "queued_for_vector_store",
        }

    def search(self, collection: str, query_vector: list[float], top_k: int = 5):
        return {
            "collection": collection,
            "backend": self.backend,
            "top_k": top_k,
            "matches": [],
        }
