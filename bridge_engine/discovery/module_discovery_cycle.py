import json
import os
from datetime import datetime


DISCOVERY_PATH = "data/module_discovery.json"


class ModuleDiscoveryCycle:
    """Discovers high-frequency learning use cases and interaction needs."""

    DEFAULT_DISCOVERIES = {
        "language_learning": [
            "matching",
            "sentence_builder",
            "podcast_reflection",
            "voice_reflection",
        ],
        "coding_learning": [
            "code_debug",
            "micro_quiz",
            "project_builder",
        ],
        "study_support": [
            "flashcards",
            "recall_testing",
            "summaries",
        ],
        "assignment_support": [
            "photo_drop",
            "document_parse",
            "step_breakdown",
        ],
    }

    def run(self):
        os.makedirs("data", exist_ok=True)

        payload = {
            "updated_at": datetime.utcnow().isoformat(),
            "discoveries": self.DEFAULT_DISCOVERIES,
        }

        with open(DISCOVERY_PATH, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

        return payload


if __name__ == "__main__":
    cycle = ModuleDiscoveryCycle()
    print(cycle.run())
