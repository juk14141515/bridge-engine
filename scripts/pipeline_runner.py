"""
Bridge Engine Pipeline Runner

Cron-safe orchestration layer for backend learning/intelligence scripts.
- Runs engines in dependency order.
- Uses the current venv Python via sys.executable.
- Never crashes the whole pipeline if one engine fails.
- Writes pipeline health snapshots and run logs.
- Designed for overnight/continuous learning automation.
"""

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SCRIPT_DIR = BASE_DIR / "scripts"
DATA_DIR.mkdir(exist_ok=True)

REGISTRY_PATH = DATA_DIR / "engine_registry.json"
LATEST_PATH = DATA_DIR / "pipeline_latest.json"
HISTORY_PATH = DATA_DIR / "pipeline_history.jsonl"

DEFAULT_ENGINES = [
    {"name": "sqlite_event_logger", "script": "sqlite_event_logger.py", "enabled": True, "stage": "foundation"},
    {"name": "assignment_parser", "script": "assignment_parser_engine.py", "enabled": True, "stage": "intake"},
    {"name": "concept_extraction", "script": "concept_extraction_engine.py", "enabled": True, "stage": "learning"},
    {"name": "mastery_tracking", "script": "mastery_tracking_engine.py", "enabled": True, "stage": "learning"},
    {"name": "spaced_review", "script": "spaced_review_engine.py", "enabled": True, "stage": "learning"},
    {"name": "knowledge_checks", "script": "knowledge_check_engine.py", "enabled": True, "stage": "validation"},
    {"name": "recall_evidence", "script": "recall_evidence_engine.py", "enabled": True, "stage": "validation"},
    {"name": "adaptive_user_profile", "script": "adaptive_user_profile_engine.py", "enabled": True, "stage": "personalization"},
    {"name": "resource_intelligence", "script": "resource_intelligence_engine.py", "enabled": True, "stage": "recommendation"},
    {"name": "backend_foundation", "script": "backend_foundation_engine.py", "enabled": True, "stage": "foundation"},
    {"name": "coach_memory", "script": "coach_memory_engine.py", "enabled": True, "stage": "coach"},
    {"name": "recommendation_api", "script": "recommendation_api_engine.py", "enabled": True, "stage": "api_ready"},
]


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def save_json(path, payload):
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def ensure_registry():
    registry = load_json(REGISTRY_PATH, None)
    if not registry:
        registry = {
            "version": 1,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "engines": DEFAULT_ENGINES,
            "notes": [
                "Set enabled=false to temporarily disable a script.",
                "Pipeline runner skips missing scripts safely.",
                "Runtime and failures are written after each run."
            ]
        }
        save_json(REGISTRY_PATH, registry)
        return registry

    existing = {engine.get("name"): engine for engine in registry.get("engines", [])}
    changed = False
    for default_engine in DEFAULT_ENGINES:
        if default_engine["name"] not in existing:
            registry.setdefault("engines", []).append(default_engine)
            changed = True
    if changed:
        registry["updated_at"] = now_iso()
        save_json(REGISTRY_PATH, registry)
    return registry


def run_engine(engine):
    started = time.time()
    script_name = engine.get("script")
    script_path = SCRIPT_DIR / script_name

    if not engine.get("enabled", True):
        return {
            "name": engine.get("name"),
            "script": script_name,
            "status": "skipped_disabled",
            "duration_seconds": 0,
            "stdout_tail": "",
            "stderr_tail": "",
        }

    if not script_path.exists():
        return {
            "name": engine.get("name"),
            "script": script_name,
            "status": "skipped_missing",
            "duration_seconds": 0,
            "stdout_tail": "",
            "stderr_tail": f"Missing script: {script_path}",
        }

    try:
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=int(engine.get("timeout_seconds", 90)),
            check=False,
        )
        status = "ok" if proc.returncode == 0 else "failed"
        return {
            "name": engine.get("name"),
            "script": script_name,
            "status": status,
            "returncode": proc.returncode,
            "duration_seconds": round(time.time() - started, 3),
            "stdout_tail": proc.stdout[-2000:],
            "stderr_tail": proc.stderr[-2000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "name": engine.get("name"),
            "script": script_name,
            "status": "timeout",
            "duration_seconds": round(time.time() - started, 3),
            "stdout_tail": (exc.stdout or "")[-2000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-2000:] if isinstance(exc.stderr, str) else "timeout",
        }
    except Exception as exc:
        return {
            "name": engine.get("name"),
            "script": script_name,
            "status": "error",
            "duration_seconds": round(time.time() - started, 3),
            "stdout_tail": "",
            "stderr_tail": str(exc),
        }


def update_registry_with_results(registry, results):
    by_name = {result["name"]: result for result in results}
    for engine in registry.get("engines", []):
        result = by_name.get(engine.get("name"))
        if not result:
            continue
        engine["last_run_at"] = now_iso()
        engine["last_status"] = result.get("status")
        engine["last_duration_seconds"] = result.get("duration_seconds")
        engine["failure_count"] = engine.get("failure_count", 0)
        if result.get("status") not in ["ok", "skipped_disabled", "skipped_missing"]:
            engine["failure_count"] += 1
        elif result.get("status") == "ok":
            engine["failure_count"] = 0
    registry["updated_at"] = now_iso()
    save_json(REGISTRY_PATH, registry)


def append_history(payload):
    with HISTORY_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


def main():
    started = time.time()
    registry = ensure_registry()
    engines = registry.get("engines", [])
    results = [run_engine(engine) for engine in engines]
    ok_count = sum(1 for r in results if r.get("status") == "ok")
    failed = [r for r in results if r.get("status") not in ["ok", "skipped_disabled", "skipped_missing"]]

    payload = {
        "ok": len(failed) == 0,
        "generated_at": now_iso(),
        "duration_seconds": round(time.time() - started, 3),
        "python": sys.executable,
        "engine_count": len(results),
        "ok_count": ok_count,
        "failed_count": len(failed),
        "results": results,
        "next_actions": [
            "Check failed_count after cron runs.",
            "Use engine_registry.json to disable unstable engines.",
            "Surface pipeline_latest.json in a future admin dashboard."
        ]
    }

    update_registry_with_results(registry, results)
    save_json(LATEST_PATH, payload)
    append_history({k: payload[k] for k in ["ok", "generated_at", "duration_seconds", "engine_count", "ok_count", "failed_count"]})
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
