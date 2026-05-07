"""
Bridge Engine Goal Execution Engine

Purpose:
- Convert goals into adaptive execution systems.
- Work both INSIDE the app and OUTSIDE the app.
- Generate project-first learning paths.
- Adapt based on energy, momentum, context, and learning style.

Supports:
- web design
- coding
- filmmaking
- investing
- future templates

Future integrations:
- Flask routes
- API endpoints
- mobile app
- daily coach reports
- scheduler
- Codex prompts
- assignment parser
"""

import json
import os
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GOAL_DIR = os.path.join(BASE_DIR, "goal_templates")
DATA_DIR = os.path.join(BASE_DIR, "data")
PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "goal_execution_latest.json")


def now_stamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_json(path, default=None):
    if default is None:
        default = {}
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def load_goal(goal_id):
    path = os.path.join(GOAL_DIR, f"{goal_id}.json")
    return load_json(path, {})


def determine_start_mode(profile):
    energy = profile.get("default_energy", "focused")
    blockers = profile.get("common_blockers", [])

    if energy == "low":
        return "30_second_start"

    if "starting tasks" in blockers or "too many steps" in blockers:
        return "3_minute_start"

    return "10_minute_build"


def choose_modality(profile):
    formats = profile.get("learning_formats", [])
    environment = profile.get("context_intelligence", {}).get("best_environment", "desk")

    if "building projects" in formats:
        return "hands_on"
    if environment == "walking":
        return "walking"
    if "visual diagrams" in formats:
        return "visual"
    if "short videos" in formats:
        return "audio"

    return "hands_on"


def build_execution_path(goal, profile):
    start_mode = determine_start_mode(profile)
    modality = choose_modality(profile)

    first_phase = goal.get("phases", [{}])[0]
    first_project = first_phase.get("projects", ["small starter project"])[0]

    return {
        "generated_at": now_stamp(),
        "goal": goal.get("title"),
        "core_output": goal.get("core_output"),
        "recommended_start_mode": start_mode,
        "recommended_modality": modality,
        "starter_actions": goal.get("starter_modes", {}).get(start_mode, []),
        "first_project": first_project,
        "current_phase": first_phase.get("name"),
        "checkpoint": first_phase.get("checkpoint"),
        "modality_instruction": goal.get("modalities", {}).get(modality),
        "adaptive_rules": goal.get("adaptive_rules", []),
        "outside_app_uses": goal.get("outside_app_uses", []),
        "execution_philosophy": "Projects first. Visible progress fast. Adapt to the user instead of forcing one rigid path.",
    }


def main(goal_id="web_design"):
    profile = load_json(PROFILE_FILE, {})
    goal = load_goal(goal_id)

    if not goal:
        print(json.dumps({"ok": False, "error": f"Goal template '{goal_id}' not found."}, indent=2))
        return

    output = build_execution_path(goal, profile)
    save_json(OUTPUT_FILE, output)

    print(json.dumps({
        "ok": True,
        "goal": output["goal"],
        "start_mode": output["recommended_start_mode"],
        "modality": output["recommended_modality"],
        "first_project": output["first_project"],
    }, indent=2))


if __name__ == "__main__":
    main()
