from __future__ import annotations

from typing import Dict


class EvaluationEngine:
    def score_output(self, output: str) -> Dict[str, int]:
        text = (output or '').strip()
        length = len(text.split())
        momentum = min(length * 5, 100)
        return {
            'completion_score': momentum,
            'effort_score': 100 if length > 10 else 40,
        }
