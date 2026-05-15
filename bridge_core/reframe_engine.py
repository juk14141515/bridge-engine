from __future__ import annotations

from typing import Dict


FRAMES = {
    'gaming': 'Treat this like unlocking a new skill tree.',
    'music': 'Think of this like learning one small section before the full song.',
    'fitness': 'This is one rep, not the whole workout.',
    'investing': 'Focus on small compounding progress.',
    'systems': 'We are building one stable subsystem at a time.',
}


def build_reframe(task: str, frame: str = 'gaming') -> Dict[str, str]:
    return {
        'frame': frame,
        'message': FRAMES.get(frame, FRAMES['gaming']),
        'task': task,
    }
