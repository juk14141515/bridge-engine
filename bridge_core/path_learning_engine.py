"""Path learning engine.

Tracks which learning/completion paths actually work.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict


class PathLearningEngine:
    def __init__(self):
        self.path_scores = defaultdict(int)

    def record_result(
        self,
        category: str,
        frame: str,
        completed: bool,
    ):
        key = f"{category}:{frame}"

        if completed:
            self.path_scores[key] += 10
        else:
            self.path_scores[key] -= 3

    def best_paths(self) -> Dict:
        ranked = sorted(
            self.path_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return {
            "best_paths": ranked[:10],
        }
