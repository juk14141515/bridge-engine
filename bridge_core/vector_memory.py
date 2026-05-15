from __future__ import annotations

from typing import Dict, List


class VectorMemory:
    def __init__(self):
        self.memories: List[Dict[str, str]] = []

    def store(self, text: str, category: str) -> None:
        self.memories.append({'text': text, 'category': category})

    def search(self, query: str) -> List[Dict[str, str]]:
        q = query.lower()
        return [m for m in self.memories if q in m['text'].lower()]
