import json
from pathlib import Path


LANE_FILE = Path("data/runtime_lanes.json")


class LaneStore:
    def __init__(self):
        LANE_FILE.parent.mkdir(parents=True, exist_ok=True)

    def load(self):
        if not LANE_FILE.exists():
            return []

        return json.loads(LANE_FILE.read_text())

    def save(self, lanes):
        LANE_FILE.write_text(json.dumps(lanes, indent=2))

    def upsert_lane(self, lane):
        lanes = self.load()

        updated = False

        for index, existing in enumerate(lanes):
            if existing.get("workflow_id") == lane.get("workflow_id"):
                lanes[index] = lane
                updated = True
                break

        if not updated:
            lanes.insert(0, lane)

        self.save(lanes)
        return lane
