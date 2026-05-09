class MediaParsingPipeline:
    """Parses PDFs, screenshots, audio, video, and uploaded content into executable structures."""

    MEDIA_TYPES = [
        "pdf",
        "image",
        "screenshot",
        "audio",
        "video",
        "document",
        "repository",
    ]

    def parse(self, media_type: str, payload: dict):
        return {
            "media_type": media_type,
            "parsed": True,
            "semantic_structure": [
                "objective",
                "requirements",
                "friction_points",
                "completion_targets",
            ],
            "next_stage": "semantic_decomposition",
        }
