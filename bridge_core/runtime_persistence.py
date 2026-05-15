from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

BASE = Path('.bridge_runtime')
BASE.mkdir(exist_ok=True)


def session_path(session_id: str) -> Path:
    return BASE / f'{session_id}.json'


def save_session(workspace: Dict[str, Any]) -> str:
    session_id = str(workspace.get('id') or 'session')
    path = session_path(session_id)
    path.write_text(json.dumps(workspace, indent=2), encoding='utf-8')
    return str(path)


def load_session(session_id: str) -> Dict[str, Any]:
    path = session_path(session_id)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))
