"""Completion pattern analyzer.

Learns:
- abandonment patterns
- successful pacing
- best task lengths
- strongest momentum windows
"""

from __future__ import annotations

from typing import Dict, List


class CompletionPatternAnalyzer:
    def analyze(self, sessions: List[Dict]) -> Dict:
        completed = len([s for s in sessions if s.get("status") == "complete"])
        abandoned = len([s for s in sessions if s.get("status") == "abandoned"])
        active = len([s for s in sessions if s.get("status") == "active"])

        total = max(len(sessions), 1)

        return {
            "completion_rate": round(completed / total, 2),
            "abandonment_rate": round(abandoned / total, 2),
            "active_rate": round(active / total, 2),
            "recommended_step_size": self._step_size(completed, abandoned),
        }

    def _step_size(self, completed: int, abandoned: int) -> str:
        if abandoned > completed:
            return "smaller"
        return "normal"
