from datetime import datetime


class TaskIngestor:
    """Ingests user tasks from multiple sources into Bridge Engine."""

    SUPPORTED_TYPES = [
        "document",
        "pdf",
        "photo",
        "assignment",
        "link",
        "video",
        "repository",
        "notes",
        "lms_export",
        "recording",
        "screenshot",
    ]

    def ingest(self, source_type: str, content: dict):
        return {
            "id": datetime.utcnow().strftime("%Y%m%d%H%M%S"),
            "source_type": source_type,
            "content": content,
            "status": "ingested",
            "created_at": datetime.utcnow().isoformat(),
        }
