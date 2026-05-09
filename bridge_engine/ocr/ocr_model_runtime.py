class OCRModelRuntime:
    """Runtime scaffold for OCR and media parsing models."""

    MODELS = ["tesseract", "easyocr", "vision_llm", "hybrid_pipeline"]

    def process(self, source_type: str, payload: dict):
        return {
            "source_type": source_type,
            "pipeline": "ocr_media_runtime",
            "detected_structure": [
                "headings",
                "tasks",
                "requirements",
                "references",
            ],
            "status": "parsed",
        }
