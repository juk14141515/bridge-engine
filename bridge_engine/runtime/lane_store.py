import json
from pathlib import Path
from dataclasses import asdict


DATA_PATH = Path("data/runtime_lanes.json")


class LaneStore:
    def __init__(self):
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

        if not DATA_PATH.exists():
            DATA_PATH.write_text("[]")

    def load(self):
        return json.loads(DATA_PATH.read_text())

    def save_lane(self, runtime_state):
        lanes = self.load()

        lanes = [
            lane for lane in lanes
            if lane["lane_id"] != runtime_state.lane_id
        ]

        lanes.append(asdict(runtime_state))

        DATA_PATH.write_text(json.dumps(lanes, indent=2))

    def get_lane(self, lane_id: str):
        lanes = self.load()

        for lane in lanes:
            if lane["lane_id"] == lane_id:
                return lane

        return None
