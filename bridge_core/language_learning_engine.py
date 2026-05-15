from __future__ import annotations

from typing import Dict, List


BEGINNER_SPANISH = [
    'Hola',
    'Como estas',
    'Donde esta el bano',
    'Quiero comida',
]


def generate_language_session(goal: str) -> Dict[str, List[str]]:
    return {
        'goal': goal,
        'micro_lessons': BEGINNER_SPANISH,
        'practice_mode': 'conversation',
        'review_enabled': True,
    }
