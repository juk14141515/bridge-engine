import json
import os
from datetime import datetime


DATA_SOURCE_PATH = "data/data_sources.json"


class DataSourceCycle:
    """Tracks future data sources and adaptive integrations."""

    DEFAULT_SOURCES = {
        "assignment_inputs": [
            "pdf_upload",
            "photo_upload",
            "text_paste",
            "google_docs",
            "canvas_lms",
        ],
        "learning_signals": [
            "completion_speed",
            "hesitation",
            "feedback",
            "rewrites",
            "dropoff_points",
        ],
        "interaction_sources": [
            "voice",
            "matching",
            "multiple_choice",
            "code_editor",
            "drag_drop",
        ],
        "future_ai_sources": [
            "ocr",
            "document_parsing",
            "semantic_task_breakdown",
            "misconception_detection",
            "adaptive_generation",
        ],
    }

    def run(self):
        os.makedirs("data", exist_ok=True)

        payload = {
            "updated_at": datetime.utcnow().isoformat(),
            "sources": self.DEFAULT_SOURCES,
        }

        with open(DATA_SOURCE_PATH, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

        return payload


if __name__ == "__main__":
    cycle = DataSourceCycle()
    print(cycle.run())
