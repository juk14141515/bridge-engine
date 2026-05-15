"""Adaptive user profile store.

Persistent evolving user model.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


BASE_DIR = Path("runtime_data/profiles")
BASE_DIR.mkdir(parents=True, exist_ok=True)


class UserProfileStore:
    def profile_path(self, user_id: str) -> Path:
        return BASE_DIR / f"{user_id}.json"

    def load_profile(self, user_id: str) -> Dict:
        path = self.profile_path(user_id)

        if not path.exists():
            return {
                "user_id": user_id,
                "interests": [],
                "path_scores": {},
                "completion_patterns": {},
            }

        return json.loads(path.read_text(encoding="utf-8"))

    def save_profile(self, user_id: str, profile: Dict):
        path = self.profile_path(user_id)
        path.write_text(json.dumps(profile, indent=2), encoding="utf-8")
