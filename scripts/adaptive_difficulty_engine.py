"""
Adaptive Difficulty Engine

Learns when paths/tasks should be easier, harder, shorter, or recovery-focused.
Uses mastery, recall evidence, profile, and path completion signals.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


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


def difficulty_for_mastery(score, activation_profile):
    if activation_profile == "micro_start_needed":
        if score < 40:
            return "micro_easy"
        if score < 70:
            return "guided_standard"
        return "gentle_challenge"
    if score < 30:
        return "easy_guided"
    if score < 70:
        return "standard"
    return "challenge"


def main():
    mastery = load_json("mastery_tracking_latest.json", {})
    profile = load_json("adaptive_user_profile_latest.json", {})
    recall = load_json("recall_evidence_latest.json", {})
    paths = load_json("bridge_paths.json", [])

    activation_profile = profile.get("activation_profile", "unknown")
    completion_rate = profile.get("completion_rate", 0)
    recall_evidence = recall.get("evidence", []) if isinstance(recall, dict) else []
    unanswered_count = sum(1 for item in recall_evidence if not item.get("response_present"))

    adjustments = []
    for item in mastery.get("mastery_items", []):
        score = item.get("mastery_score", 0)
        concept = item.get("concept", "unknown")
        mode = difficulty_for_mastery(score, activation_profile)
        recommendation = {
            "concept": concept,
            "domain": item.get("domain"),
            "current_mastery_score": score,
            "recommended_difficulty": mode,
            "recommended_minutes": 3 if mode == "micro_easy" else 8 if "guided" in mode else 15,
            "recommended_support": [],
        }
        if score < 40:
            recommendation["recommended_support"] = ["example_first", "explain_like_friend", "one_tiny_check"]
        elif score < 70:
            recommendation["recommended_support"] = ["guided_practice", "feedback_check", "short_application"]
        else:
            recommendation["recommended_support"] = ["transfer_task", "challenge_variant", "teach_back"]
        adjustments.append(recommendation)

    global_mode = "recovery_first" if completion_rate < 25 or unanswered_count > 10 else "balanced"
    if completion_rate > 70 and unanswered_count < 3:
        global_mode = "challenge_ready"

    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "purpose": "Adapt task difficulty based on mastery, recall evidence, and activation behavior.",
        "global_difficulty_mode": global_mode,
        "activation_profile": activation_profile,
        "completion_rate": completion_rate,
        "unanswered_recall_checks": unanswered_count,
        "adjustments": adjustments[:150],
        "rules": [
            "Low mastery + low activation => micro_easy tasks.",
            "Developing mastery => guided practice.",
            "Strong mastery => transfer/challenge tasks.",
            "Difficulty should adapt without shame or punishment."
        ]
    }
    save_json("adaptive_difficulty_latest.json", payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
