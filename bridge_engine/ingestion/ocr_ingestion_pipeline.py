class OCRIngestionPipeline:
    """Processes screenshots, PDFs, handwritten notes, and uploads."""

    def ingest(self, source_type: str, payload: dict):
        return {
            "source_type": source_type,
            "classification": self.classify(source_type),
            "parsed": True,
            "next_action": "semantic_decomposition",
        }

    def classify(self, source_type: str):
        mapping = {
            "pdf": "assignment",
            "screenshot": "study_material",
            "repo": "coding_project",
            "notes": "knowledge_capture",
        }

        return mapping.get(source_type, "general")
