from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

CACHE = Path('.bridge_cache')
CACHE.mkdir(exist_ok=True)


class OfflineCache:
    def save(self, key: str, payload: Dict[str, Any]) -> None:
        (CACHE / f'{key}.json').write_text(json.dumps(payload), encoding='utf-8')

    def load(self, key: str) -> Dict[str, Any]:
        path = CACHE / f'{key}.json'
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding='utf-8'))
