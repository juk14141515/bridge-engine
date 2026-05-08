"""
Execution Reinforcement Engine

Learns which intervention structures appear most likely to improve:
- task initiation
- completion
- understanding
- return rate
- retention
- reduced overwhelm

Core philosophy:
Starting difficulty is not automatically laziness or lack of discipline.
It may be activation friction, unclear prerequisites, cognitive overload,
false fluency, environment mismatch, or emotional resistance.

This engine separates:
- Knowledge failure: user starts but misunderstands/does not retain material.
- Activation failure: user understands/intends to work but cannot initiate or sustain action.

This is intentionally active-work oriented: interventions should help users create,
apply, explain, or produce evidence, not passively consume videos.
"""

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

INTERVENTIONS = {
    "movement_first": {
        "label": "Movement first",
        "description": "Stand up, walk, stretch, or change physical state before starting.",
        "best_for": ["activation_failure", "overwhelm", "low_energy"],
        "active_proof": "Return and open the task after movement."
    },
    "three_minute_start": {
        "label": "3-minute start",
        "description": "Do the smallest visible first action for only 3 minutes.",
        "best_for": ["activation_failure", "avoidance", "unclear_start"],
        "active_proof": "Submit or save the tiny visible output."
    },
    "visible_progress": {
        "label": "Visible progress artifact",
        "description": "Create a tiny artifact so progress becomes real and visible.",
        "best_for": ["activation_failure", "motivation_drop", "low_reward"],
        "active_proof": "Upload, type, or describe the artifact."
    },
    "environment_switch": {
        "label": "Environment switch",
        "description": "Move to a different desk, room, library, cafe, or body position.",
        "best_for": ["activation_failure", "stale_context", "distraction_loop"],
        "active_proof": "Confirm new environment and restart the micro-task."
    },
    "voice_input": {
        "label": "Voice input",
        "description": "Speak the first draft, explanation, or confusion before typing.",
        "best_for": ["writing_block", "overwhelm", "low_text_tolerance"],
        "active_proof": "Capture a voice note or convert one sentence to text."
    },
    "body_doubling": {
        "label": "Body doubling",
        "description": "Work with another person present, on call, or using a timed accountability session.",
        "best_for": ["activation_failure", "avoidance", "lonely_work"],
        "active_proof": "Complete one timed micro-session."
    },
    "visual_checkpoint": {
        "label": "Visual checkpoint",
        "description": "Make the next step concrete with a checklist, screenshot, card, or visible marker.",
        "best_for": ["unclear_start", "memory_load", "multi_step_task"],
        "active_proof": "Create or check off one visible checkpoint."
    },
    "low_shame_recovery": {
        "label": "Low-shame recovery",
        "description": "Restart without punishment, streak loss, or guilt language.",
        "best_for": ["overwhelm", "abandoned_path", "return_after_gap"],
        "active_proof": "Accept a restart step and complete one tiny action."
    },
    "explain_back": {
        "label": "Explain-back check",
        "description": "Explain the concept in your own words before moving forward.",
        "best_for": ["knowledge_failure", "false_fluency", "weak_recall"],
        "active_proof": "Write or speak an explanation with an example."
    },
    "prerequisite_micro_task": {
        "label": "Prerequisite micro-task",
        "description": "Return to the smallest missing prerequisite instead of forcing the advanced task.",
        "best_for": ["knowledge_failure", "prerequisite_gap"],
        "active_proof": "Complete one prerequisite artifact/check."
    }
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_json(name, default):
    path = DATA_DIR / name
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def save_json(name, payload):
    (DATA_DIR / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def classify_failure(profile, mastery, recall, misconceptions, curriculum):
    completion_rate = profile.get("completion_rate", 0) if isinstance(profile, dict) else 0
    activation_profile = profile.get("activation_profile", "unknown") if isinstance(profile, dict) else "unknown"
    unanswered = sum(1 for item in recall.get("evidence", []) if not item.get("response_present")) if isinstance(recall, dict) else 0
    misconception_count = misconceptions.get("misconception_count", 0) if isinstance(misconceptions, dict) else 0
    ready_items = curriculum.get("next_best_items", []) if isinstance(curriculum, dict) else []
    blocked_items = curriculum.get("blocked_items", []) if isinstance(curriculum, dict) else []

    knowledge_risk = 0
    activation_risk = 0

    if misconception_count:
        knowledge_risk += min(misconception_count * 6, 60)
    if unanswered > 10:
        knowledge_risk += 20
    if blocked_items and len(blocked_items) > len(ready_items):
        knowledge_risk += 20

    if completion_rate < 25:
        activation_risk += 35
    if activation_profile == "micro_start_needed":
        activation_risk += 35
    if unanswered > 10:
        activation_risk += 10

    if knowledge_risk >= activation_risk + 20:
        primary = "knowledge_failure"
    elif activation_risk >= knowledge_risk + 20:
        primary = "activation_failure"
    else:
        primary = "mixed_failure"

    return {
        "primary_failure_mode": primary,
        "knowledge_risk": min(knowledge_risk, 100),
        "activation_risk": min(activation_risk, 100),
        "signals": {
            "completion_rate": completion_rate,
            "activation_profile": activation_profile,
            "unanswered_recall_checks": unanswered,
            "misconception_count": misconception_count,
            "ready_curriculum_items": len(ready_items),
            "blocked_curriculum_items": len(blocked_items),
        }
    }


def choose_interventions(classification, profile, misconceptions, curriculum):
    primary = classification["primary_failure_mode"]
    ranked = []

    if primary == "activation_failure":
        order = ["three_minute_start", "movement_first", "visible_progress", "environment_switch", "low_shame_recovery", "body_doubling"]
    elif primary == "knowledge_failure":
        order = ["prerequisite_micro_task", "explain_back", "visual_checkpoint", "three_minute_start", "low_shame_recovery"]
    else:
        order = ["three_minute_start", "prerequisite_micro_task", "visible_progress", "explain_back", "movement_first", "low_shame_recovery"]

    feature_counts = Counter()
    for feature, count in profile.get("likely_effective_features", []) if isinstance(profile, dict) else []:
        feature_counts[feature] = count

    for idx, key in enumerate(order):
        item = dict(INTERVENTIONS[key])
        base_score = 100 - (idx * 8)
        if key == "movement_first" and feature_counts.get("walking_mode", 0) > 0:
            base_score += 8
        if key == "visible_progress" and feature_counts.get("visible_artifact", 0) > 0:
            base_score += 8
        if key == "visual_checkpoint" and feature_counts.get("clear_checkpoint", 0) > 0:
            base_score += 8
        if key == "low_shame_recovery" and feature_counts.get("recovery_mode", 0) > 0:
            base_score += 8
        ranked.append({
            "id": key,
            "score": min(base_score, 100),
            **item,
        })

    return ranked


def main():
    profile_payload = load_json("adaptive_user_profile_latest.json", {})
    profile = profile_payload.get("profile", profile_payload) if isinstance(profile_payload, dict) else {}
    mastery = load_json("mastery_tracking_latest.json", {})
    recall = load_json("recall_evidence_latest.json", {})
    misconceptions = load_json("misconception_detection_latest.json", {})
    curriculum = load_json("curriculum_sequence_latest.json", {})
    events = load_json("pipeline_latest.json", {})

    classification = classify_failure(profile, mastery, recall, misconceptions, curriculum)
    interventions = choose_interventions(classification, profile, misconceptions, curriculum)

    reinforcement_memory = load_json("execution_reinforcement_memory.json", {"intervention_stats": {}})
    stats = reinforcement_memory.get("intervention_stats", {})
    for intervention in interventions:
        stats.setdefault(intervention["id"], {
            "shown": 0,
            "accepted": 0,
            "completed": 0,
            "reduced_overwhelm": 0,
            "improved_recall": 0,
            "last_score": intervention["score"]
        })
        stats[intervention["id"]]["last_score"] = intervention["score"]

    reinforcement_memory = {
        "updated_at": now_iso(),
        "intervention_stats": stats,
        "learning_note": "Stats are placeholders until real event ingestion records accepted/completed/reduced_overwhelm outcomes."
    }
    save_json("execution_reinforcement_memory.json", reinforcement_memory)

    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "purpose": "Separate activation failure from knowledge failure and reinforce interventions that improve execution outcomes.",
        "classification": classification,
        "recommended_interventions": interventions,
        "active_learning_requirement": {
            "rule": "Intervention success requires active evidence, not passive content consumption.",
            "examples": ["artifact created", "task opened", "explain-back submitted", "micro-step completed", "environment changed", "voice note captured"]
        },
        "metrics_to_learn_over_time": [
            "start_rate_after_intervention",
            "completion_rate_after_intervention",
            "recall_score_after_intervention",
            "overwhelm_reduction",
            "return_rate",
            "time_to_first_action",
            "path_continuation_rate"
        ],
        "personal_mission_alignment": [
            "Built for users who want to work but struggle to initiate.",
            "Avoids shame-based productivity framing.",
            "Treats task initiation as a design problem, not a character flaw.",
            "Supports active treatment/accommodation workflows without claiming to replace medical care."
        ]
    }
    save_json("execution_reinforcement_latest.json", payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
