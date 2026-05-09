import json
import os
from datetime import datetime

from bridge_engine.adaptive.readiness_engine import ReadinessEngine


DATA_PATH = "data/adaptive_learning_state.json"


class AdaptiveLearningCycle:
    """Cron-safe adaptive learning updater."""

    def __init__(self):
        self.readiness_engine = ReadinessEngine()

    def load_state(self):
        if not os.path.exists(DATA_PATH):
            return {
                "updated_at": None,
                "users": {},
            }

        with open(DATA_PATH, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def save_state(self, state):
        os.makedirs("data", exist_ok=True)

        with open(DATA_PATH, "w", encoding="utf-8") as handle:
            json.dump(state, handle, indent=2)

    def update_user(self, user_id: str, metrics: dict):
        state = self.load_state()

        readiness = self.readiness_engine.detect(metrics)

        state["users"][user_id] = {
            "metrics": metrics,
            "readiness": readiness,
            "updated_at": datetime.utcnow().isoformat(),
        }

        state["updated_at"] = datetime.utcnow().isoformat()

        self.save_state(state)

        return state["users"][user_id]


if __name__ == "__main__":
    cycle = AdaptiveLearningCycle()

    result = cycle.update_user(
        "demo-user",
        {
            "completion_speed": 2,
            "helped_count": 4,
            "too_much_count": 0,
            "continuation_count": 3,
        },
    )

    print(result)
