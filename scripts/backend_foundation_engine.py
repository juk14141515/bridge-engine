"""
Bridge Engine Backend Foundation Engine

Purpose:
- Consolidate backend intelligence outputs for future UI/Codex work.
- Generate coach-ready data cards without requiring polished frontend work yet.
- Prepare the app for assignment intake, user profiles, event logging, and SQLite migration.

This script is safe to run from cron or manually.
It reads existing JSON data where available and writes stable backend artifacts into data/.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_json(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"WARN: failed to load {path}: {exc}")
    return default


def save_json(path, payload):
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_paths():
    return load_json(DATA_DIR / "bridge_paths.json", [])


def summarize_paths(paths):
    total_paths = len(paths)
    total_steps = 0
    done_steps = 0
    abandoned = 0
    partial = 0

    for path in paths:
        steps = path.get("steps", [])
        total_steps += len(steps)
        done = sum(1 for step in steps if step.get("status") == "done")
        done_steps += done
        if steps and done == 0:
            abandoned += 1
        elif steps and done < len(steps):
            partial += 1

    completion_rate = round((done_steps / total_steps) * 100, 2) if total_steps else 0

    return {
        "total_paths": total_paths,
        "total_steps": total_steps,
        "done_steps": done_steps,
        "completion_rate": completion_rate,
        "abandoned_paths": abandoned,
        "partial_paths": partial,
    }


def generate_ai_coach_cards(paths, context, reward, backend_brain, smart_filters):
    cards = []
    path_summary = summarize_paths(paths)

    if path_summary["abandoned_paths"] > 0:
        cards.append({
            "type": "momentum_rescue",
            "priority": "high",
            "title": "Momentum Rescue Recommended",
            "message": "Some paths have not started yet. Offer a 2-3 minute restart step instead of showing a backlog.",
            "suggested_action": "Create one tiny visible first step.",
            "mode": "recovery",
            "ui_hint": "primary_coach_card"
        })

    context_rec = context.get("recommendation", {}) if isinstance(context, dict) else {}
    if context_rec:
        cards.append({
            "type": "context_recommendation",
            "priority": "medium",
            "title": "Best Current Work Pattern",
            "message": context_rec.get("message", "Use the current best context pattern."),
            "recommended_minutes": context_rec.get("recommended_minutes", 10),
            "recommended_environment": context_rec.get("best_environment", "desk"),
            "recommended_mode": context_rec.get("recommended_task_mode", "guided_progress"),
            "ui_hint": "context_card"
        })

    reward_style = reward.get("reward_style") if isinstance(reward, dict) else None
    if reward_style:
        cards.append({
            "type": "reward_loop",
            "priority": "medium",
            "title": "Reward Loop Strategy",
            "message": f"Current reward strategy: {reward_style}. Keep tasks small, visible, and emotionally safe.",
            "loops": reward.get("loops", []),
            "ui_hint": "reward_card"
        })

    best_features = backend_brain.get("best_default_features", []) if isinstance(backend_brain, dict) else []
    if best_features:
        cards.append({
            "type": "path_strategy",
            "priority": "medium",
            "title": "Path Features to Prefer",
            "message": "Use these features when generating new paths.",
            "features": best_features[:8],
            "ui_hint": "strategy_chip_list"
        })

    filters = smart_filters.get("filters", []) if isinstance(smart_filters, dict) else []
    if filters:
        top = sorted(filters, key=lambda item: item.get("completion_rate", 0), reverse=True)[:3]
        cards.append({
            "type": "smart_path_filter",
            "priority": "medium",
            "title": "Smart Path Patterns Emerging",
            "message": "Synthetic testing is identifying path formats that are more likely to work for specific user types.",
            "top_patterns": top,
            "ui_hint": "advanced_insight_card"
        })

    if not cards:
        cards.append({
            "type": "starter",
            "priority": "low",
            "title": "Start With One Visible Win",
            "message": "Create a small artifact or checkpoint that gives immediate progress feedback.",
            "suggested_action": "Pick one goal and make the first step take under 5 minutes.",
            "ui_hint": "starter_card"
        })

    return cards


def generate_assignment_intake_schema():
    return {
        "version": 1,
        "purpose": "Backend schema for future assignment/syllabus intake UI.",
        "accepted_inputs": [
            "pasted_assignment_text",
            "syllabus_text",
            "deadline",
            "course_name",
            "rubric_text",
            "calendar_export_future",
            "screenshot_or_pdf_future"
        ],
        "parsed_fields": {
            "course": None,
            "assignment_title": None,
            "due_date": None,
            "deliverables": [],
            "requirements": [],
            "hidden_steps": [],
            "estimated_sessions": [],
            "risk_flags": [],
            "recommended_start_mode": "micro_start",
            "recommended_energy_mode": "focused",
            "recovery_buffer_needed": True
        },
        "planning_rules": [
            "Always generate a first step that takes 2-5 minutes.",
            "Separate unclear requirements from actionable steps.",
            "Prefer visible artifacts over vague study goals.",
            "Add recovery buffers for deadlines and overwhelm risk.",
            "Do not shame the user for late or abandoned work."
        ]
    }


def generate_event_schema():
    return {
        "version": 1,
        "purpose": "Every meaningful interaction should become a timestamped event for future personalization.",
        "event_types": [
            "app_opened",
            "path_created",
            "step_started",
            "step_completed",
            "step_skipped",
            "feedback_overwhelmed",
            "feedback_flow",
            "restart_accepted",
            "restart_declined",
            "assignment_uploaded",
            "assignment_parsed",
            "energy_mode_changed",
            "context_logged",
            "resource_clicked",
            "coach_message_shown",
            "coach_message_helpful",
            "notification_sent",
            "notification_dismissed"
        ],
        "minimum_payload": {
            "event_type": "string",
            "timestamp": "iso_datetime",
            "user_id": "future_user_id_or_local_default",
            "source": "app|worker|simulation|manual",
            "payload": {}
        }
    }


def generate_database_migration_plan():
    return {
        "version": 1,
        "recommended_path": ["JSON prototype", "SQLite local/server", "PostgreSQL production"],
        "sqlite_tables": {
            "users": ["id", "created_at", "display_name", "privacy_mode", "timezone"],
            "profiles": ["user_id", "learning_preferences", "energy_patterns", "motivation_patterns", "privacy_settings"],
            "events": ["id", "user_id", "timestamp", "event_type", "payload_json", "source"],
            "paths": ["id", "user_id", "goal_type", "interest", "learning_goal", "status", "created_at"],
            "steps": ["id", "path_id", "title", "status", "difficulty", "modality", "estimated_minutes"],
            "assignments": ["id", "user_id", "course", "title", "due_date", "raw_text", "parsed_json"],
            "recommendations": ["id", "user_id", "generated_at", "type", "priority", "message", "action_json"]
        },
        "privacy_controls_needed": [
            "export_my_data",
            "delete_my_data",
            "disable_personalization",
            "calm_mode",
            "notification_intensity",
            "upload_deletion"
        ],
        "security_notes": [
            "Never commit .env or user data to Git.",
            "Separate real user data from synthetic data.",
            "Avoid positioning as medical treatment or therapy.",
            "Use HTTPS, auth, sessions, and user isolation before public beta."
        ]
    }


def main():
    paths = load_paths()
    context = load_json(DATA_DIR / "context_intelligence_latest.json", {})
    reward = load_json(DATA_DIR / "reward_loop_latest.json", {})
    backend_brain = load_json(DATA_DIR / "adaptive_backend_brain_latest.json", {})
    smart_filters = load_json(DATA_DIR / "smart_path_filter_latest.json", {})

    path_summary = summarize_paths(paths)
    coach_cards = generate_ai_coach_cards(paths, context, reward, backend_brain, smart_filters)

    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "path_summary": path_summary,
        "coach_cards": coach_cards,
        "assignment_intake_schema": generate_assignment_intake_schema(),
        "event_schema": generate_event_schema(),
        "database_migration_plan": generate_database_migration_plan(),
        "smart_filter_count": len(smart_filters.get("filters", [])) if isinstance(smart_filters, dict) else 0,
        "next_backend_priorities": [
            "wire coach_cards into Flask API",
            "add assignment intake route",
            "create SQLite event table",
            "log app_opened/path_created/step_completed events",
            "surface backend_foundation_latest.json in Codex UI"
        ]
    }

    save_json(DATA_DIR / "backend_foundation_latest.json", payload)
    save_json(DATA_DIR / "ai_coach_cards_latest.json", {"generated_at": payload["generated_at"], "cards": coach_cards})
    save_json(DATA_DIR / "assignment_intake_schema.json", payload["assignment_intake_schema"])
    save_json(DATA_DIR / "event_schema.json", payload["event_schema"])
    save_json(DATA_DIR / "database_migration_plan.json", payload["database_migration_plan"])

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
