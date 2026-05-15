from __future__ import annotations

from typing import Dict


class FrictionEngine:
    def detect(self, output: str) -> Dict[str, str]:
        text = (output or '').lower().strip()
        if not text:
            return {'state': 'blank'}
        if len(text.split()) < 3:
            return {'state': 'hesitant'}
        if 'stuck' in text or 'overwhelmed' in text:
            return {'state': 'overwhelmed'}
        return {'state': 'moving'}
