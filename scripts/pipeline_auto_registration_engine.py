"""
Pipeline Auto-Registration Engine

Automatically discovers *_engine.py files inside scripts/
and syncs them into data/engine_registry.json.

This prevents manual registry maintenance as the adaptive
backend grows.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPT_DIR = BASE_DIR / "scripts"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

REGISTRY_PATH = DATA_DIR / "engine_registry.json"

EXCLUDED = {
    "pipeline_runner.py",
    "install_api_routes_patch.py",
    "__init__.py",
}


STAGE_RULES = {
    "foundation": ["foundation", "logger", "backend"],
    "learning": ["learning", "mastery", "review", "knowledge", "recall", "misconception", "curriculum"],
    "memory": ["memory", "semantic"],
    "simulation": ["simulation", "path_filter"],
    "api_ready": ["api", "schema", "normalization"],
    "coach": ["coach", "recommendation"],
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def detect_stage(script_name: str) -> str:
    lowered = script_name.lower()
    for stage, keywords in STAGE_RULES.items():
        if any(keyword in lowered for keyword in keywords):
            return stage
    return "general"


def load_registry():
    if REGISTRY_PATH.exists():
        try:
            return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "version": 2,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "engines": [],
    }


def save_registry(payload):
    payload["updated_at"] = now_iso()
    REGISTRY_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def discover_engines():
    engines = []

    for path in sorted(SCRIPT_DIR.glob("*_engine.py")):
        if path.name in EXCLUDED:
            continue

        engines.append({
            "name": path.stem.replace("_engine", ""),
            "script": path.name,
            "enabled": True,
            "stage": detect_stage(path.name),
            "auto_registered": True,
            "discovered_at": now_iso(),
        })

    return engines


def merge_registry(existing, discovered):
    existing_map = {
        item.get("script"): item
        for item in existing.get("engines", [])
    }

    merged = []

    for item in discovered:
        current = existing_map.get(item["script"], {})

        merged.append({
            **item,
            "enabled": current.get("enabled", True),
            "failure_count": current.get("failure_count", 0),
            "last_run_at": current.get("last_run_at"),
            "last_status": current.get("last_status"),
            "last_duration_seconds": current.get("last_duration_seconds"),
        })

    return merged


def main():
    registry = load_registry()
    discovered = discover_engines()
    merged = merge_registry(registry, discovered)

    payload = {
        "version": 2,
        "created_at": registry.get("created_at", now_iso()),
        "updated_at": now_iso(),
        "engine_count": len(merged),
        "engines": merged,
        "notes": [
            "Registry generated automatically from scripts/*_engine.py",
            "Disable engines by setting enabled=false in engine_registry.json",
            "Pipeline runner reads this registry dynamically"
        ]
    }

    save_registry(payload)

    print(json.dumps({
        "ok": True,
        "generated_at": now_iso(),
        "engine_count": len(merged),
        "sample_engines": merged[:10],
    }, indent=2))


if __name__ == "__main__":
    main()
