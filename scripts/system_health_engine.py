"""
System Health Engine

Checks whether Bridge Engine's adaptive backend is healthy enough for UI/API use.
Detects stale outputs, malformed/missing files, pipeline failures, and memory growth risk.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

CRITICAL_OUTPUTS = {
    "pipeline": "pipeline_latest.json",
    "events": "events_latest.json",
    "profile": "adaptive_user_profile_latest.json",
    "memory": "semantic_memory_latest.json",
    "interventions": "execution_reinforcement_latest.json",
    "curriculum": "curriculum_sequence_latest.json",
    "mastery": "mastery_tracking_latest.json",
    "ontology": "educational_ontology_latest.json",
    "misconceptions": "misconception_detection_latest.json",
    "recommendations": "recommendation_api_latest.json",
}

STALE_MINUTES_WARNING = 60 * 6
STALE_MINUTES_CRITICAL = 60 * 24


def now_utc():
    return datetime.now(timezone.utc)


def now_iso():
    return now_utc().isoformat()


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, str(exc)


def age_minutes(path):
    if not path.exists():
        return None
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return round((now_utc() - modified).total_seconds() / 60, 2)


def score_health(checks, pipeline):
    score = 100
    for check in checks:
        if check["status"] == "missing":
            score -= 12
        elif check["status"] == "malformed_json":
            score -= 15
        elif check["status"] == "stale_critical":
            score -= 10
        elif check["status"] == "stale_warning":
            score -= 4
    if isinstance(pipeline, dict):
        score -= pipeline.get("failed_count", 0) * 8
    return max(0, min(score, 100))


def main():
    checks = []
    loaded = {}

    for name, filename in CRITICAL_OUTPUTS.items():
        path = DATA_DIR / filename
        if not path.exists():
            checks.append({"name": name, "file": filename, "status": "missing", "age_minutes": None})
            continue
        payload, err = load_json(path)
        age = age_minutes(path)
        if err:
            checks.append({"name": name, "file": filename, "status": "malformed_json", "age_minutes": age, "error": err})
            continue
        loaded[name] = payload
        if age is not None and age > STALE_MINUTES_CRITICAL:
            status = "stale_critical"
        elif age is not None and age > STALE_MINUTES_WARNING:
            status = "stale_warning"
        else:
            status = "ok"
        checks.append({"name": name, "file": filename, "status": status, "age_minutes": age, "ok_field": payload.get("ok") if isinstance(payload, dict) else None})

    pipeline = loaded.get("pipeline", {})
    health_score = score_health(checks, pipeline)
    failed = [c for c in checks if c["status"] not in ["ok"]]

    payload = {
        "ok": health_score >= 70,
        "generated_at": now_iso(),
        "health_score": health_score,
        "status": "healthy" if health_score >= 85 else "watch" if health_score >= 70 else "needs_attention",
        "checks": checks,
        "failed_or_warning_count": len(failed),
        "pipeline_summary": {
            "engine_count": pipeline.get("engine_count"),
            "ok_count": pipeline.get("ok_count"),
            "failed_count": pipeline.get("failed_count"),
            "duration_seconds": pipeline.get("duration_seconds"),
        } if isinstance(pipeline, dict) else {},
        "recommendations": [
            "Run python scripts/pipeline_runner.py if outputs are stale or missing.",
            "Inspect data/pipeline_latest.json if failed_count is above 0.",
            "Before real users, connect this health payload to an admin dashboard.",
            "Use health_score below 70 as a block before deploying UI changes."
        ]
    }
    (DATA_DIR / "system_health_latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
