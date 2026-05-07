"""
Bridge Engine Adaptive Learning Engine

Purpose:
- Personalize task generation and pacing per user.
- Adapt based on behavior, energy, momentum, and friction.
- Help users start difficult tasks more consistently.
- Make learning/project execution feel rewarding and accessible.

IMPORTANT:
This system is NOT intended to diagnose or medically treat ADHD.
It is a personalization engine focused on momentum, clarity, activation, and adaptive learning support.
"""

import json
import os
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")
RETENTION_FILE = os.path.join(DATA_DIR, "retention_metrics_latest.json")
ADAPTIVE_OUTPUT_FILE = os.path.join(DATA_DIR, "adaptive_learning_latest.json")


def now_stamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default


def save_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def determine_learning_mode(profile, retention):
    completion_rate = retention.get("completion_rate", 0)
    energy = profile.get("default_energy", "focused")
    blockers = profile.get("common_blockers", [])

    if completion_rate < 20:
        return "micro_activation"

    if "too many steps" in blockers:
        return "guided_breakdown"

    if energy == "hyperfocus":
        return "challenge_expansion"

    return "balanced_learning"


def build_adaptive_rules(profile, retention):
    learning_formats = profile.get("learning_formats", [])
    reward_preferences = profile.get("reward_preferences", [])
    blockers = profile.get("common_blockers", [])

    rules = []

    if "building projects" in learning_formats:
        rules.append("Convert concepts into small real-world builds whenever possible.")

    if "visual diagrams" in learning_formats:
        rules.append("Prioritize visual progress and diagrams over dense text explanations.")

    if "too much reading" in blockers:
        rules.append("Reduce long text walls and split instructions into short checkpoints.")

    if "visible progress" in profile.get("motivation_triggers", []):
        rules.append("Always show visible progress movement after completion.")

    if "future-self projections" in reward_preferences:
        rules.append("Show projected growth outcomes and future skill simulations.")

    if retention.get("completion_rate", 0) < 30:
        rules.append("Default new tasks into low-friction micro-start format.")

    return rules


def build_next_action_strategy(profile, retention):
    energy = profile.get("default_energy", "focused")
    session_length = profile.get("best_session_length", "5 minutes")

    if energy == "low":
        return {
            "recommended_task_style": "micro_task",
            "recommended_length": session_length,
            "prompting_style": "gentle_and_clear",
            "focus": "starting momentum",
        }

    if energy == "hyperfocus":
        return {
            "recommended_task_style": "deep_build",
            "recommended_length": "25 minutes",
            "prompting_style": "challenge_based",
            "focus": "high-impact progress",
        }

    return {
        "recommended_task_style": "guided_progress",
        "recommended_length": session_length,
        "prompting_style": "structured_and_rewarding",
        "focus": "consistent advancement",
    }


def build_output(profile, retention):
    mode = determine_learning_mode(profile, retention)
    rules = build_adaptive_rules(profile, retention)
    next_actions = build_next_action_strategy(profile, retention)

    return {
        "generated_at": now_stamp(),
        "adaptive_learning_mode": mode,
        "personalization_summary": {
            "primary_context": profile.get("primary_context"),
            "motivation_triggers": profile.get("motivation_triggers", []),
            "common_blockers": profile.get("common_blockers", []),
            "learning_formats": profile.get("learning_formats", []),
            "energy_mode": profile.get("default_energy"),
        },
        "adaptive_rules": rules,
        "next_action_strategy": next_actions,
        "mission": "Help users consistently start, continue, and complete meaningful work using adaptive structure and personalized momentum systems.",
        "guardrails": [
            "Avoid manipulative addiction mechanics.",
            "Optimize for sustainable progress and healthy momentum.",
            "Reduce shame and restart friction.",
            "Respect user autonomy and energy levels.",
        ],
    }


def main():
    profile = load_json(PROFILE_FILE, {})
    retention = load_json(RETENTION_FILE, {})

    output = build_output(profile, retention)
    save_json(ADAPTIVE_OUTPUT_FILE, output)

    print(json.dumps({
        "ok": True,
        "generated_at": output["generated_at"],
        "mode": output["adaptive_learning_mode"],
        "rules": output["adaptive_rules"][:5],
    }, indent=2))


if __name__ == "__main__":
    main()
