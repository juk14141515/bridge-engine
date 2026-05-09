import json
import os
from datetime import datetime


PATH_RECOGNITION_PATH = "data/path_recognition.json"


class PathRecognitionCycle:
    """Learns recurring path structures that successfully move users forward."""

    DEFAULT_PATTERNS = {
        "burnout_recovery": [
            "reduce_scope",
            "restore_confidence",
            "gentle_restart",
            "momentum_rebuild",
        ],
        "expert_execution": [
            "high_context_goal",
            "remove_overexplaining",
            "deliverable_focus",
            "completion_pressure_management",
        ],
        "adhd_flow": [
            "fast_feedback",
            "visible_progress",
            "reduced_text",
            "micro_interactions",
        ],
        "creative_shipping": [
            "idea_capture",
            "prototype_fast",
            "public_iteration",
            "publish_cycle",
        ],
        "deep_learning": [
            "active_recall",
            "applied_examples",
            "adaptive_repetition",
            "knowledge_transfer",
        ],
    }

    def run(self):
        os.makedirs("data", exist_ok=True)

        payload = {
            "updated_at": datetime.utcnow().isoformat(),
            "recognized_patterns": self.DEFAULT_PATTERNS,
        }

        with open(PATH_RECOGNITION_PATH, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

        return payload


if __name__ == "__main__":
    cycle = PathRecognitionCycle()
    print(cycle.run())
