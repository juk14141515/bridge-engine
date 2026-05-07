"""
Bridge Engine Reward Loop Engine

Purpose:
- Create ethical dopamine-supporting structure around difficult learning/building tasks.
- Personalize reward timing, task size, recovery prompts, and challenge pacing.
- Run in the background on a VPS/cron without paid AI calls.

This is NOT designed to addict users or maximize screen time.
It is designed to make useful effort feel more rewarding, visible, and restartable.

Run manually:
    python scripts/reward_loop_engine.py

Suggested cron:
    15,45 * * * * cd /home/ubuntu/bridge-engine && /home/ubuntu/bridge-engine/venv/bin/python scripts/reward_loop_engine.py >> /home/ubuntu/bridge-engine/data/reward_loop_engine.log 2>&1
"""

import json
import os
from datetime import datetime, date

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
PATHS_FILE = os.path.join(DATA_DIR, "bridge_paths.json")
PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, "notifications.json")
REWARD_FILE = os.path.join(DATA_DIR, "reward_loop_latest.json")
REWARD_STATE_FILE = os.path.join(DATA_DIR, "reward_loop_state.json")


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


def progress_percent(path):
    steps = path.get("steps", [])
    if not steps:
        return 0
    done = len([s for s in steps if s.get("status") == "done"])
    return int((done / len(steps)) * 100)


def collect_behavior(paths):
    total_paths = len(paths)
    abandoned = 0
    partial = 0
    completed = 0
    total_steps = 0
    done_steps = 0
    feedback_counts = {
        "flow": 0,
        "overwhelm": 0,
        "boredom": 0,
        "confusion": 0,
        "want_more": 0,
        "worked_well": 0,
    }

    for path in paths:
        pct = progress_percent(path)
        if pct == 0:
            abandoned += 1
        elif pct == 100:
            completed += 1
        else:
            partial += 1

        for step in path.get("steps", []):
            total_steps += 1
            if step.get("status") == "done":
                done_steps += 1
            for feedback in step.get("feedback", []):
                kind = str(feedback.get("type", "")).lower()
                if kind in ["flow", "worked_well", "want_more"]:
                    feedback_counts[kind] = feedback_counts.get(kind, 0) + 1
                if kind in ["too_hard", "overwhelmed", "avoided"]:
                    feedback_counts["overwhelm"] += 1
                if kind in ["boring", "bored", "not_interesting"]:
                    feedback_counts["boredom"] += 1
                if kind in ["confused", "unclear", "lost"]:
                    feedback_counts["confusion"] += 1

    completion_rate = int((done_steps / total_steps) * 100) if total_steps else 0
    start_rate = int(((total_paths - abandoned) / total_paths) * 100) if total_paths else 0

    return {
        "total_paths": total_paths,
        "abandoned_paths": abandoned,
        "partial_paths": partial,
        "completed_paths": completed,
        "total_steps": total_steps,
        "done_steps": done_steps,
        "completion_rate": completion_rate,
        "start_rate": start_rate,
        "feedback_counts": feedback_counts,
    }


def determine_reward_style(profile, behavior):
    feedback = behavior["feedback_counts"]
    if feedback["overwhelm"] > feedback["flow"]:
        return "gentle_micro_wins"
    if feedback["boredom"] > 0:
        return "novelty_and_challenge"
    if feedback["want_more"] + feedback["flow"] >= 3:
        return "momentum_streak_builder"
    if behavior["abandoned_paths"] > 0 and behavior["start_rate"] < 30:
        return "restart_friction_reducer"
    return profile.get("reward_style", "balanced_progress")


def generate_reward_plan(profile, behavior):
    style = determine_reward_style(profile, behavior)

    plans = {
        "gentle_micro_wins": {
            "task_size": "tiny",
            "reward_frequency": "high",
            "recommended_prompt": "Just do the smallest visible step. Completion matters more than intensity.",
            "best_ui_pattern": "large progress confirmation + low-pressure next step",
            "avoid": "long task lists, guilt language, streak pressure",
        },
        "novelty_and_challenge": {
            "task_size": "medium",
            "reward_frequency": "variable_but_visible",
            "recommended_prompt": "Try a challenge version or unlock a more interesting build path.",
            "best_ui_pattern": "challenge cards, unlocks, surprise project suggestions",
            "avoid": "repetitive checkpoints and generic tasks",
        },
        "momentum_streak_builder": {
            "task_size": "medium_to_large",
            "reward_frequency": "milestone_based",
            "recommended_prompt": "You have momentum. Keep going with one higher-impact step.",
            "best_ui_pattern": "streak meter, chain progress, next-best-action button",
            "avoid": "interrupting flow with too much explanation",
        },
        "restart_friction_reducer": {
            "task_size": "tiny",
            "reward_frequency": "immediate",
            "recommended_prompt": "Restart with a 3-minute task. No need to catch up first.",
            "best_ui_pattern": "resume button, recovery mode, forgiving streak repair",
            "avoid": "showing a large backlog first",
        },
        "balanced_progress": {
            "task_size": "small",
            "reward_frequency": "steady",
            "recommended_prompt": "Complete one useful checkpoint and bank the win.",
            "best_ui_pattern": "simple progress bar + next action",
            "avoid": "overcomplicated dashboards during onboarding",
        },
    }

    selected = plans[style]
    selected["style"] = style
    return selected


def generate_dopamine_support_loops(behavior, reward_plan):
    loops = []

    loops.append({
        "name": "Instant Visible Progress",
        "trigger": "step_completed",
        "response": "show XP, progress movement, and one sentence of reinforcement",
        "why": "converts invisible effort into visible reward",
    })

    loops.append({
        "name": "Momentum Continuation",
        "trigger": "two_steps_completed_in_session",
        "response": "offer a Keep Going option with a slightly harder but exciting task",
        "why": "uses current energy instead of forcing fixed pacing",
    })

    loops.append({
        "name": "Friction Recovery",
        "trigger": "abandoned_path_or_long_gap",
        "response": reward_plan["recommended_prompt"],
        "why": "removes shame and lowers restart cost",
    })

    loops.append({
        "name": "Novelty Injection",
        "trigger": "boredom_or_repetition_detected",
        "response": "swap task format, add challenge mode, or convert lesson into a small build",
        "why": "adds stimulation to low-dopamine work",
    })

    loops.append({
        "name": "Identity Reinforcement",
        "trigger": "milestone_reached",
        "response": "connect progress to identity: builder, learner, investor, creator",
        "why": "makes effort feel personally meaningful",
    })

    return loops


def add_notification(title, message, priority="normal"):
    notifications = load_json(NOTIFICATIONS_FILE, [])
    duplicate_today = any(
        n.get("title") == title and str(n.get("created_at", "")).startswith(str(date.today()))
        for n in notifications[:20]
    )
    if duplicate_today:
        return
    notifications.insert(0, {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "kind": "reward_loop",
        "title": title,
        "message": message,
        "priority": priority,
        "created_at": now_stamp(),
        "read": False,
    })
    save_json(NOTIFICATIONS_FILE, notifications[-100:])


def update_profile(profile, reward_plan, behavior):
    profile.setdefault("reward_system", {})
    profile["reward_system"]["last_updated"] = now_stamp()
    profile["reward_system"]["reward_style"] = reward_plan["style"]
    profile["reward_system"]["preferred_task_size"] = reward_plan["task_size"]
    profile["reward_system"]["reward_frequency"] = reward_plan["reward_frequency"]
    profile["reward_system"]["completion_rate"] = behavior["completion_rate"]
    profile["reward_system"]["start_rate"] = behavior["start_rate"]
    return profile


def main():
    paths = load_json(PATHS_FILE, [])
    profile = load_json(PROFILE_FILE, {})
    state = load_json(REWARD_STATE_FILE, {"runs": 0})

    behavior = collect_behavior(paths)
    reward_plan = generate_reward_plan(profile, behavior)
    loops = generate_dopamine_support_loops(behavior, reward_plan)
    profile = update_profile(profile, reward_plan, behavior)

    payload = {
        "generated_at": now_stamp(),
        "purpose": "Ethical reward-loop personalization for useful effort, learning, and building.",
        "behavior": behavior,
        "reward_plan": reward_plan,
        "dopamine_support_loops": loops,
        "guardrails": [
            "Do not optimize for addiction or endless screen time.",
            "Optimize for meaningful progress, recovery, and user agency.",
            "Use rewards to help users do things they already value.",
            "Avoid shame-based streak loss or manipulative urgency.",
        ],
    }

    save_json(REWARD_FILE, payload)
    save_json(PROFILE_FILE, profile)

    add_notification(
        "Reward loop updated",
        f"Current reward style: {reward_plan['style']}. Recommended task size: {reward_plan['task_size']}.",
        "normal",
    )

    state["runs"] = int(state.get("runs", 0)) + 1
    state["last_run_at"] = now_stamp()
    state["last_reward_style"] = reward_plan["style"]
    save_json(REWARD_STATE_FILE, state)

    print(json.dumps({
        "ok": True,
        "ran_at": now_stamp(),
        "runs": state["runs"],
        "reward_style": reward_plan["style"],
        "task_size": reward_plan["task_size"],
        "loops": [loop["name"] for loop in loops],
    }, indent=2))


if __name__ == "__main__":
    main()
