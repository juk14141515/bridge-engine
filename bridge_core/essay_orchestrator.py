from __future__ import annotations

from typing import Dict, List


ESSAY_FLOW = [
    'brain_dump',
    'outline',
    'thesis',
    'body_paragraphs',
    'revision',
    'final_polish',
]


def build_essay_runtime(topic: str) -> Dict[str, List[str]]:
    return {
        'topic': topic,
        'stages': ESSAY_FLOW,
        'export_ready': True,
    }
