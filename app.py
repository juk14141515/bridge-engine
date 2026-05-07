from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import re
import traceback
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

app = Flask(__name__)

DATA_FILE = "data/bridge_paths.json"
PROFILE_FILE = "data/profile.json"
SKILL_TREE_FILE = "data/skill_tree.json"
NOTIFICATIONS_FILE = "data/notifications.json"
APP_BLOCK_FILE = "data/app_block_intents.json"
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
KEEP_GOING_MODE = os.getenv("KEEP_GOING_MODE", "momentum")  # momentum | paywall
FREE_PATH_LIMIT = int(os.getenv("FREE_PATH_LIMIT", "3"))

ENERGY_MODES = {
    "low": {
        "label": "Low Energy",
        "minutes": 5,
        "difficulty_bias": "micro",
        "instruction": "Make the next step tiny, obvious, and impossible to overthink.",
    },
    "focused": {
        "label": "Focused",
        "minutes": 10,
        "difficulty_bias": "starter",
        "instruction": "Make the next step practical and clearly tied to a useful output.",
    },
    "hyperfocus": {
        "label": "Hyperfocus",
        "minutes": 20,
        "difficulty_bias": "intermediate",
        "instruction": "Offer a deeper challenge, but keep it scoped enough to avoid burnout.",
    },
}


def now_stamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_json_file(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default


def save_json_file(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def load_paths():
    return load_json_file(DATA_FILE, [])


def save_paths(paths):
    save_json_file(DATA_FILE, paths)


def default_profile():
    return {
        "name": "Julio",
        "core_interests": ["coding", "investing", "building useful tools"],
        "learning_style": "project_based",
        "motivation_type": "visible_progress",
        "preferred_task_minutes": 10,
        "difficulty": "starter",
        "energy_mode": "focused",
        "adaptation": {
            "preferred_step_size": "normal",
            "needs_more_guidance": False,
            "likes_challenge": False,
            "avoidance_count": 0,
            "overwhelm_count": 0,
            "flow_count": 0,
        },
        "created_at": now_stamp(),
        "updated_at": now_stamp(),
    }


def load_profile():
    profile = load_json_file(PROFILE_FILE, default_profile())
    base = default_profile()
    base.update(profile)
    base["adaptation"] = {**default_profile()["adaptation"], **profile.get("adaptation", {})}
    return base


def save_profile(profile):
    profile["updated_at"] = now_stamp()
    save_json_file(PROFILE_FILE, profile)


def default_skill_tree():
    return {
        "nodes": {
            "coding": {"xp": 0, "level": 0, "unlocked": True},
            "finance_coding": {"xp": 0, "level": 0, "unlocked": True},
            "language": {"xp": 0, "level": 0, "unlocked": True},
            "math": {"xp": 0, "level": 0, "unlocked": True},
            "creative": {"xp": 0, "level": 0, "unlocked": True},
            "fitness": {"xp": 0, "level": 0, "unlocked": True},
            "general": {"xp": 0, "level": 0, "unlocked": True},
        },
        "last_updated": now_stamp(),
    }


def load_skill_tree():
    tree = load_json_file(SKILL_TREE_FILE, default_skill_tree())
    base = default_skill_tree()
    base["nodes"].update(tree.get("nodes", {}))
    base["last_updated"] = tree.get("last_updated", base["last_updated"])
    return base


def save_skill_tree(tree):
    tree["last_updated"] = now_stamp()
    save_json_file(SKILL_TREE_FILE, tree)


def load_notifications():
    return load_json_file(NOTIFICATIONS_FILE, [])


def save_notifications(items):
    save_json_file(NOTIFICATIONS_FILE, items[-50:])


def add_notification(kind, title, message, priority="normal", action_url=None):
    items = load_notifications()
    items.insert(0, {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "kind": kind,
        "title": title,
        "message": message,
        "priority": priority,
        "action_url": action_url,
        "created_at": now_stamp(),
        "read": False,
    })
    save_notifications(items)


def load_app_block_intents():
    return load_json_file(APP_BLOCK_FILE, {
        "enabled": False,
        "mode": "focus_session",
        "blocked_apps": [],
        "allowed_apps": [],
        "notes": "Placeholder for future desktop/mobile integration. Backend stores intent; actual blocking requires OS/browser/mobile permissions.",
        "updated_at": now_stamp(),
    })


def save_app_block_intents(payload):
    payload["updated_at"] = now_stamp()
    save_json_file(APP_BLOCK_FILE, payload)


def clean_phrase(value):
    value = (value or "").strip()
    return re.sub(r"\s+", " ", value)


def display_learning_goal(value):
    value = clean_phrase(value)
    lowered = value.lower()
    if lowered.startswith("learning "):
        return value[9:].strip()
    if lowered.startswith("learn "):
        return value[6:].strip()
    return value


def normalize_energy_mode(mode):
    mode = (mode or "focused").lower().strip()
    return mode if mode in ENERGY_MODES else "focused"


def progress_percent(path):
    total = len(path.get("steps", []))
    done = len([s for s in path.get("steps", []) if s.get("status") == "done"])
    return int((done / total) * 100) if total else 0


def classify_bridge(interest, learning_goal):
    text = f"{interest} {learning_goal}".lower()
    if any(word in text for word in ["spanish", "language", "french", "japanese"]):
        return "language"
    if any(word in text for word in ["trading", "invest", "stock", "bot", "finance", "probability", "expected value"]):
        return "finance_coding"
    if any(word in text for word in ["code", "coding", "python", "website", "app", "flask", "html", "css"]):
        return "coding"
    if any(word in text for word in ["film", "movie", "script", "video", "story"]):
        return "creative"
    if any(word in text for word in ["math", "statistics", "stats", "algebra", "calculus"]):
        return "math"
    if any(word in text for word in ["fitness", "lifting", "nutrition", "workout", "health"]):
        return "fitness"
    return "general"


def get_adaptive_context(paths, interest, learning_goal, profile=None):
    profile = profile or load_profile()
    learning_goal_l = display_learning_goal(learning_goal).lower()
    interest_l = clean_phrase(interest).lower()
    energy_mode = normalize_energy_mode(profile.get("energy_mode"))
    energy = ENERGY_MODES[energy_mode]
    adaptation = profile.get("adaptation", {})

    total_paths = len(paths)
    completed_paths = 0
    partial_paths = 0
    repeated_topic_count = 0
    total_done_steps = 0
    total_steps = 0
    today_completions = 0
    today_str = str(date.today())

    for path in paths:
        progress = progress_percent(path)
        if progress == 100:
            completed_paths += 1
        elif progress > 0:
            partial_paths += 1

        if learning_goal_l and learning_goal_l in path.get("learning_goal", "").lower():
            repeated_topic_count += 1
        if interest_l and interest_l in path.get("interest", "").lower():
            repeated_topic_count += 1

        steps = path.get("steps", [])
        total_steps += len(steps)
        done_steps = [s for s in steps if s.get("status") == "done"]
        total_done_steps += len(done_steps)
        today_completions += len([
            s for s in done_steps
            if str(s.get("completed_at", "")).startswith(today_str)
        ])

    completion_rate = int((total_done_steps / total_steps) * 100) if total_steps else 0

    if energy_mode == "low" or adaptation.get("overwhelm_count", 0) > adaptation.get("flow_count", 0):
        difficulty = "micro"
    elif energy_mode == "hyperfocus" or (completion_rate >= 70 and completed_paths >= 1):
        difficulty = "intermediate"
    elif total_paths >= 3 and completion_rate < 30:
        difficulty = "micro"
    else:
        difficulty = profile.get("difficulty", energy["difficulty_bias"]) or energy["difficulty_bias"]

    momentum_score = min(100, (total_done_steps * 12) + (completed_paths * 20) + (today_completions * 10) + (adaptation.get("flow_count", 0) * 5))

    if momentum_score >= 70:
        momentum_state = "hot"
    elif momentum_score >= 30:
        momentum_state = "building"
    else:
        momentum_state = "starting"

    return {
        "total_paths": total_paths,
        "completed_paths": completed_paths,
        "partial_paths": partial_paths,
        "repeated_topic_count": repeated_topic_count,
        "completion_rate": completion_rate,
        "difficulty": difficulty,
        "momentum_score": momentum_score,
        "momentum_state": momentum_state,
        "today_completions": today_completions,
        "bridge_type": classify_bridge(interest, learning_goal),
        "preferred_task_minutes": energy["minutes"],
        "energy_mode": energy_mode,
        "energy_label": energy["label"],
        "energy_instruction": energy["instruction"],
        "adaptation": adaptation,
    }


def get_keep_going_gate(paths, context):
    if KEEP_GOING_MODE == "paywall" and len(paths) >= FREE_PATH_LIMIT:
        return {
            "allowed": False,
            "mode": "paywall",
            "title": "Keep Going locked",
            "message": "Free path limit reached. This is where a future subscription gate can unlock unlimited continuation paths.",
            "cta": "Upgrade placeholder",
        }

    if context.get("momentum_state") == "hot":
        return {
            "allowed": True,
            "mode": "momentum_push",
            "title": "You are in momentum mode",
            "message": "You have enough progress that the app should offer a harder follow-up while motivation is high.",
            "cta": "Keep going with a challenge",
        }

    return {
        "allowed": True,
        "mode": "momentum_build",
        "title": "Keep Going available",
        "message": "The app will create a small next step to preserve momentum without overwhelming you.",
        "cta": "Keep going",
    }


def adjust_checkpoint_for_energy(checkpoint, context):
    energy_mode = context.get("energy_mode", "focused")
    minutes = context.get("preferred_task_minutes", 10)
    if energy_mode == "low":
        return f"LOW ENERGY VERSION: Do only the first tiny part in {minutes} minutes: {checkpoint}"
    if energy_mode == "hyperfocus":
        return f"HYPERFOCUS VERSION: Spend up to {minutes} minutes and add one measurable improvement after this: {checkpoint}"
    return f"FOCUSED VERSION ({minutes} minutes): {checkpoint}"


def local_adaptive_path(interest, learning_goal, context=None, continuation=False):
    interest = clean_phrase(interest)
    learning = display_learning_goal(learning_goal)
    context = context or {}
    difficulty = context.get("difficulty", "starter")
    bridge_type = context.get("bridge_type") or classify_bridge(interest, learning)

    time_box = f"{context.get('preferred_task_minutes', 10)} minutes"
    prefix = "Next-level: " if continuation else ""

    templates = {
        "language": [
            {"title": f"{prefix}Build a tiny {learning} version of your {interest} screen", "why": f"You get an immediate visible result while using {learning} in a real interface.", "checkpoint": f"Create or sketch one small {interest} screen with 8 labels translated into {learning}. Keep it under {time_box}."},
            {"title": f"Make a 10-word {learning} UI bank for {interest}", "why": f"A reusable word bank makes {learning} feel like a tool for building, not memorizing.", "checkpoint": f"Write 10 words or phrases your {interest} project would actually display, then add the English meaning beside each one."},
            {"title": f"Add a translation toggle idea to {interest}", "why": "Switching between versions forces recall while keeping the reward tied to the project.", "checkpoint": "Describe or code one button/card that shows English on one side and the target language on the other."},
            {"title": f"Demo the {learning} version out loud", "why": "Speaking the project text connects recognition, recall, and real usage.", "checkpoint": f"Read your 8-10 {learning} labels out loud once and mark the 3 weakest words for tomorrow."},
        ],
        "finance_coding": [
            {"title": f"{prefix}Create a tiny decision table for {interest}", "why": f"A table turns {learning} into something that can improve real decisions.", "checkpoint": f"Make a 5-row table with columns: setup, chance of win, possible gain, possible loss, and decision. Time-box: {time_box}."},
            {"title": f"Calculate one simple {learning} example for {interest}", "why": "One concrete calculation is enough to make the concept useful instead of abstract.", "checkpoint": "Pick one row from the table and calculate whether the expected outcome is positive or negative."},
            {"title": f"Turn {learning} into a rule for {interest}", "why": "Rules are how learning becomes automation.", "checkpoint": "Write one if/then rule your bot or investing workflow could use based on the calculation."},
            {"title": f"Score whether the rule improves {interest}", "why": "A measurable score creates feedback, which is how the system learns over time.", "checkpoint": "Rate the rule 1-10 for usefulness and write one thing you would test next."},
        ],
        "coding": [
            {"title": f"{prefix}Build the smallest visible {interest} artifact", "why": f"A visible artifact gives quick reward and makes {learning} easier to start.", "checkpoint": f"Create one file, screen, or mockup that shows {learning} being used inside {interest}. Time-box: {time_box}."},
            {"title": f"Extract one reusable {learning} pattern for {interest}", "why": "Patterns are easier to reuse than isolated facts.", "checkpoint": f"Write one tiny example of {learning} and label what each part does."},
            {"title": f"Add the pattern to your {interest} project", "why": "Applying immediately converts studying into building.", "checkpoint": "Add or describe one feature that uses the pattern, even if it is rough."},
            {"title": "Save the next upgrade idea", "why": "A clear next step helps you restart later when motivation drops.", "checkpoint": "Write the next 10-minute improvement you would make when you come back."},
        ],
        "creative": [
            {"title": f"{prefix}Turn {learning} into a scene for {interest}", "why": "Story gives the material emotional weight, which makes it easier to remember.", "checkpoint": f"Write a 6-line scene, shot list, or storyboard where {learning} affects what happens."},
            {"title": f"Create a prop or visual for {learning}", "why": "A visual artifact makes abstract material easier to use.", "checkpoint": "Make one symbol, chart, object, or frame that represents the concept."},
            {"title": f"Explain {learning} through {interest}", "why": "Teaching through the thing you like proves understanding.", "checkpoint": f"Record or write a 30-second explanation of {learning} using your {interest} example."},
            {"title": "Cut it into a final mini-demo", "why": "A finished mini-demo creates closure and momentum.", "checkpoint": "Pick the best piece and write what you would improve in version two."},
        ],
        "math": [
            {"title": f"{prefix}Create a real-number example from {interest}", "why": f"Numbers from {interest} make {learning} feel relevant.", "checkpoint": f"Write one realistic mini-problem using numbers from {interest}."},
            {"title": f"Solve one tiny {learning} piece", "why": "A small solved example lowers friction and builds confidence.", "checkpoint": "Solve only the first step and write what the number means in plain English."},
            {"title": f"Use the answer to make a decision in {interest}", "why": "Decision-making makes math practical.", "checkpoint": "Write one decision you would make differently because of the result."},
            {"title": "Create a repeatable mini-template", "why": "Templates let you reuse the skill without starting from scratch.", "checkpoint": "Write a 3-line template you can reuse with new numbers later."},
        ],
        "fitness": [
            {"title": f"{prefix}Connect {learning} to one fitness decision", "why": f"Fitness turns {learning} into something you can feel and track.", "checkpoint": f"Write one {interest} question that {learning} could answer, such as recovery, calories, volume, or progress."},
            {"title": f"Make a tiny {learning} tracker", "why": "Tracking makes learning visible and personal.", "checkpoint": "Create a 3-row table with input, result, and decision columns."},
            {"title": f"Apply the result to {interest}", "why": "A changed routine makes the learning real.", "checkpoint": "Write one small adjustment you would make based on the tracker."},
            {"title": "Choose tomorrow's measurement", "why": "One next measurement keeps the loop alive without overload.", "checkpoint": "Pick one thing to measure tomorrow and why it matters."},
        ],
        "general": [
            {"title": f"{prefix}Build one visible artifact for {interest}", "why": f"A visible artifact gives your brain a reason to engage with {learning}.", "checkpoint": f"Create a tiny file, note, table, card, or sketch that connects {learning} to {interest}."},
            {"title": f"Find the first useful piece of {learning}", "why": "The first useful piece is easier to start than the whole subject.", "checkpoint": "Write one concept and one example of how it affects your project."},
            {"title": f"Use it immediately in {interest}", "why": "Immediate use creates momentum.", "checkpoint": "Add, change, or describe one project feature using the concept."},
            {"title": "Choose the next smallest upgrade", "why": "Small next actions help you restart when motivation drops.", "checkpoint": "Write the next 10-minute upgrade and why it is worth doing."},
        ],
    }

    steps = templates.get(bridge_type, templates["general"])
    adjusted = []
    for step in steps:
        item = dict(step)
        item["checkpoint"] = adjust_checkpoint_for_energy(item["checkpoint"], context)
        item["energy_mode"] = context.get("energy_mode", "focused")
        item["estimated_minutes"] = context.get("preferred_task_minutes", 10)
        item["difficulty"] = difficulty
        adjusted.append(item)
    return adjusted


def fallback_path(interest, learning_goal):
    context = get_adaptive_context([], interest, learning_goal)
    return local_adaptive_path(interest, learning_goal, context)


def safe_json_loads(raw_text):
    text = (raw_text or "").strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        first = text.find("{")
        last = text.rfind("}")
        if first != -1 and last != -1 and last > first:
            return json.loads(text[first:last + 1])
        raise


def validate_steps(payload):
    raw_steps = payload.get("steps", []) if isinstance(payload, dict) else []
    cleaned = []
    for step in raw_steps[:4]:
        if not isinstance(step, dict):
            continue
        title = clean_phrase(step.get("title", ""))
        why = clean_phrase(step.get("why", ""))
        checkpoint = clean_phrase(step.get("checkpoint", ""))
        if title and why and checkpoint:
            cleaned.append({"title": title, "why": why, "checkpoint": checkpoint})
    return cleaned if len(cleaned) == 4 else None


def generate_ai_steps(interest, learning_goal, context=None):
    interest = clean_phrase(interest)
    learning_goal = display_learning_goal(learning_goal)
    context = context or {}

    if OpenAI is None:
        return None, "OpenAI package is not installed. Run: python -m pip install -r requirements.txt"

    if not os.getenv("OPENAI_API_KEY"):
        return None, "OPENAI_API_KEY is missing. Put it in C:\\Users\\zjuli\\bridge-engine\\.env"

    client = OpenAI()

    system_prompt = """
You are Bridge Engine, an advanced ADHD-friendly project-learning architect.

Your job is NOT to make a school lesson plan.
Your job is to convert a learning goal into a useful mini-project path that the user would actually want to finish.

Core philosophy:
- Interest creates activation.
- Output creates reward.
- Learning should be embedded inside the project, not separated from it.
- Every step must create visible progress toward something real.

Hard rules:
- Return only valid JSON.
- Top-level object must have a key named steps.
- Exactly 4 steps.
- Each step must have title, why, checkpoint.
- Do not use generic titles like "Define the real outcome", "Learn one concept", "Apply it", or "Review the result".
- Do not write broad study advice.
- Do not say "research", "study", or "understand" unless paired with a concrete action.
- Make the steps feel like a build challenge, not homework.
""".strip()

    user_prompt = f"""
Create a Bridge Path for this user.

Interest / motivation source:
{interest}

Learning goal:
{learning_goal}

Adaptive context from previous paths:
- Total saved paths: {context.get('total_paths', 0)}
- Completion rate: {context.get('completion_rate', 0)}%
- Recommended difficulty: {context.get('difficulty', 'starter')}
- Momentum state: {context.get('momentum_state', 'starting')}
- Energy mode: {context.get('energy_label', 'Focused')}
- Energy instruction: {context.get('energy_instruction', '')}

Return JSON exactly like this:
{{
  "steps": [
    {{
      "title": "Specific action title",
      "why": "One sentence explaining why this directly helps the user's interest/project.",
      "checkpoint": "A concrete task the user can complete to prove progress."
    }}
  ]
}}

Make the path advanced and personalized:
- Step 1 should create an immediate useful output, not just define a goal.
- Step 2 should teach the first concept through a tiny applied example.
- Step 3 should force the user to use the concept inside the interest/project.
- Step 4 should produce a measurable upgrade, demo, or reflection tied to the output.
- Mention the user's interest directly in each step.
- Make checkpoints specific enough that the user knows exactly what to do.
- Use real artifacts when possible: a file, mini app, table, script, dashboard card, script outline, flashcard set, calculator, checklist, or demo.
- Follow the energy instruction exactly.
- Make the language direct and motivating.

Return only JSON. No markdown. No extra commentary.
""".strip()

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    text = response.choices[0].message.content.strip()
    print("RAW AI OUTPUT:", text)
    payload = safe_json_loads(text)
    steps = validate_steps(payload)

    if not steps:
        return None, f"AI returned invalid step JSON: {text[:500]}"

    return steps, ""


def build_steps(interest, learning_goal, paths=None, continuation=False):
    paths = paths or []
    profile = load_profile()
    context = get_adaptive_context(paths, interest, learning_goal, profile)
    print("AI FUNCTION CALLED")
    try:
        steps, error = generate_ai_steps(interest, learning_goal, context)
        if steps:
            return steps, "ai", "", context
        print("AI FALLBACK REASON:", error)
        return local_adaptive_path(interest, learning_goal, context, continuation), "local_adaptive", error, context
    except Exception:
        error = traceback.format_exc()
        print("FULL AI ERROR:")
        print(error)
        return local_adaptive_path(interest, learning_goal, context, continuation), "local_adaptive", error.splitlines()[-1] if error else "Unknown AI error", context


def generate_path(interest, learning_goal, existing_paths=None, continuation=False, parent_id=None):
    interest = clean_phrase(interest)
    learning_goal = display_learning_goal(learning_goal)
    steps, source, error, context = build_steps(interest, learning_goal, existing_paths or [], continuation)

    formatted_steps = []
    for i, step in enumerate(steps, start=1):
        formatted_steps.append({
            "id": i,
            "title": step["title"],
            "status": "unlocked" if i == 1 else "locked",
            "why": step["why"],
            "checkpoint": step["checkpoint"],
            "answer": "",
            "energy_mode": step.get("energy_mode", context.get("energy_mode")),
            "estimated_minutes": step.get("estimated_minutes", context.get("preferred_task_minutes")),
            "difficulty": step.get("difficulty", context.get("difficulty")),
            "feedback": [],
        })

    return {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "created_at": now_stamp(),
        "interest": interest,
        "learning_goal": learning_goal,
        "title": f"Learn {learning_goal} through {interest}",
        "source": source,
        "ai_model": DEFAULT_MODEL if source == "ai" else "local_adaptive",
        "ai_error": error,
        "adaptive_context": context,
        "keep_going_gate": get_keep_going_gate(existing_paths or [], context),
        "parent_id": parent_id,
        "is_continuation": continuation,
        "steps": formatted_steps,
        "events": [],
    }


def recommend_next_action(paths, profile=None):
    profile = profile or load_profile()
    active_paths = [p for p in paths if progress_percent(p) < 100]
    energy_mode = normalize_energy_mode(profile.get("energy_mode"))
    if active_paths:
        path = active_paths[0]
        unlocked = [s for s in path.get("steps", []) if s.get("status") == "unlocked"]
        if unlocked:
            step = unlocked[0]
            return {
                "type": "continue_step",
                "title": f"Continue: {step.get('title')}",
                "why": f"You already have an unlocked step. Current energy mode is {ENERGY_MODES[energy_mode]['label']}, so the app should keep the next move small enough to start.",
                "path_id": path.get("id"),
                "step_id": step.get("id"),
            }

    interests = profile.get("core_interests", []) or ["building useful tools"]
    interest = interests[0]
    return {
        "type": "new_path",
        "title": f"Start a {ENERGY_MODES[energy_mode]['minutes']}-minute path around {interest}",
        "why": "Starting small keeps the system from becoming another overwhelming to-do list.",
        "interest": interest,
    }


def update_skill_tree(path, step):
    tree = load_skill_tree()
    bridge_type = path.get("adaptive_context", {}).get("bridge_type") or classify_bridge(path.get("interest", ""), path.get("learning_goal", ""))
    node = tree.setdefault("nodes", {}).setdefault(bridge_type, {"xp": 0, "level": 0, "unlocked": True})
    node["xp"] = int(node.get("xp", 0)) + 10
    node["level"] = node["xp"] // 50
    node["unlocked"] = True
    node["last_activity"] = now_stamp()
    save_skill_tree(tree)
    return tree


def apply_feedback_adaptation(profile, feedback_type, energy_mode):
    adaptation = profile.setdefault("adaptation", default_profile()["adaptation"])
    energy_mode = normalize_energy_mode(energy_mode)

    if feedback_type in ["too_hard", "overwhelmed", "avoided"]:
        adaptation["overwhelm_count"] = adaptation.get("overwhelm_count", 0) + 1
        adaptation["needs_more_guidance"] = True
        adaptation["preferred_step_size"] = "smaller"
        profile["energy_mode"] = "low"
        profile["preferred_task_minutes"] = 5
    elif feedback_type in ["too_easy", "want_more"]:
        adaptation["likes_challenge"] = True
        adaptation["preferred_step_size"] = "larger"
        if energy_mode != "low":
            profile["energy_mode"] = "hyperfocus"
            profile["preferred_task_minutes"] = 20
    elif feedback_type in ["flow", "worked_well"]:
        adaptation["flow_count"] = adaptation.get("flow_count", 0) + 1
        adaptation["preferred_step_size"] = "normal"
        if energy_mode == "low":
            profile["energy_mode"] = "focused"
            profile["preferred_task_minutes"] = 10
    elif feedback_type == "not_interested":
        adaptation["avoidance_count"] = adaptation.get("avoidance_count", 0) + 1
        adaptation["needs_more_guidance"] = True

    return profile


def update_profile_from_completion(profile, path, step):
    interest = path.get("interest")
    if interest and interest not in profile.get("core_interests", []):
        profile.setdefault("core_interests", []).append(interest)

    events = profile.setdefault("events", [])
    events.append({
        "type": "step_completed",
        "path_id": path.get("id"),
        "step_id": step.get("id"),
        "learning_goal": path.get("learning_goal"),
        "interest": interest,
        "energy_mode": step.get("energy_mode") or profile.get("energy_mode"),
        "created_at": now_stamp(),
    })
    profile["last_completed_at"] = now_stamp()
    save_profile(profile)


@app.route("/")
def index():
    paths = load_paths()
    profile = load_profile()
    for path in paths:
        path["progress"] = progress_percent(path)
    recommendation = recommend_next_action(paths, profile)
    return render_template("index.html", paths=paths, profile=profile, recommendation=recommendation)


@app.route("/create", methods=["POST"])
def create():
    interest = request.form.get("interest", "").strip()
    learning_goal = request.form.get("learning_goal", "").strip()
    energy_mode = request.form.get("energy_mode", "").strip()
    if energy_mode:
        profile_data = load_profile()
        profile_data["energy_mode"] = normalize_energy_mode(energy_mode)
        save_profile(profile_data)

    if not interest or not learning_goal:
        return redirect(url_for("index"))

    paths = load_paths()
    new_path = generate_path(interest, learning_goal, paths)
    paths.insert(0, new_path)
    save_paths(paths)

    return redirect(url_for("path_detail", path_id=new_path["id"]))


@app.route("/path/<path_id>")
def path_detail(path_id):
    paths = load_paths()
    path = next((p for p in paths if p["id"] == path_id), None)

    if not path:
        return "Path not found", 404

    path["progress"] = progress_percent(path)
    if "keep_going_gate" not in path:
        path["keep_going_gate"] = get_keep_going_gate(paths, path.get("adaptive_context", {}))
    message = request.args.get("message", "")

    return render_template("path.html", path=path, message=message)


@app.route("/keep-going/<path_id>", methods=["POST"])
def keep_going(path_id):
    paths = load_paths()
    parent = next((p for p in paths if p.get("id") == path_id), None)
    if not parent:
        return "Path not found", 404

    context = parent.get("adaptive_context", {})
    gate = get_keep_going_gate(paths, context)
    if not gate.get("allowed"):
        parent["keep_going_gate"] = gate
        save_paths(paths)
        return redirect(url_for("path_detail", path_id=path_id, message=gate.get("message", "Keep Going is locked.")))

    next_path = generate_path(
        parent.get("interest", ""),
        parent.get("learning_goal", ""),
        paths,
        continuation=True,
        parent_id=path_id,
    )
    next_path["title"] = f"Keep Going: {next_path['title']}"
    paths.insert(0, next_path)
    save_paths(paths)
    add_notification("momentum", "Momentum path created", f"New follow-up path created for {parent.get('learning_goal')}.", "normal", f"/path/{next_path['id']}")
    return redirect(url_for("path_detail", path_id=next_path["id"], message="Momentum path created."))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    profile_data = load_profile()
    if request.method == "POST":
        profile_data["name"] = request.form.get("name", profile_data.get("name", "")).strip() or profile_data.get("name", "")
        interests = request.form.get("core_interests", "")
        if interests:
            profile_data["core_interests"] = [clean_phrase(x) for x in interests.split(",") if clean_phrase(x)]
        profile_data["learning_style"] = request.form.get("learning_style", profile_data.get("learning_style", "project_based"))
        profile_data["motivation_type"] = request.form.get("motivation_type", profile_data.get("motivation_type", "visible_progress"))
        profile_data["energy_mode"] = normalize_energy_mode(request.form.get("energy_mode", profile_data.get("energy_mode", "focused")))
        try:
            profile_data["preferred_task_minutes"] = int(request.form.get("preferred_task_minutes", profile_data.get("preferred_task_minutes", 10)))
        except ValueError:
            profile_data["preferred_task_minutes"] = 10
        save_profile(profile_data)
        return redirect(url_for("profile"))
    return jsonify(profile_data)


@app.route("/energy", methods=["GET", "POST"])
def energy():
    profile_data = load_profile()
    if request.method == "POST":
        mode = normalize_energy_mode(request.form.get("energy_mode") or (request.json or {}).get("energy_mode"))
        profile_data["energy_mode"] = mode
        profile_data["preferred_task_minutes"] = ENERGY_MODES[mode]["minutes"]
        save_profile(profile_data)
        add_notification("energy", f"Energy mode set to {ENERGY_MODES[mode]['label']}", ENERGY_MODES[mode]["instruction"], "normal")
        return jsonify({"ok": True, "energy_mode": mode, "profile": profile_data})
    return jsonify({"current": profile_data.get("energy_mode", "focused"), "modes": ENERGY_MODES})


@app.route("/feedback/<path_id>/<int:step_id>", methods=["POST"])
def step_feedback(path_id, step_id):
    payload = request.get_json(silent=True) or request.form
    feedback_type = clean_phrase(payload.get("feedback_type", "worked_well"))
    note = clean_phrase(payload.get("note", ""))
    paths = load_paths()
    profile_data = load_profile()

    for path in paths:
        if path.get("id") == path_id:
            for step in path.get("steps", []):
                if step.get("id") == step_id:
                    feedback = {
                        "type": feedback_type,
                        "note": note,
                        "energy_mode": profile_data.get("energy_mode"),
                        "created_at": now_stamp(),
                    }
                    step.setdefault("feedback", []).append(feedback)
                    path.setdefault("events", []).append({"type": "step_feedback", "step_id": step_id, **feedback})
                    profile_data = apply_feedback_adaptation(profile_data, feedback_type, profile_data.get("energy_mode"))
                    path["adaptive_context"] = get_adaptive_context(paths, path.get("interest", ""), path.get("learning_goal", ""), profile_data)
                    path["keep_going_gate"] = get_keep_going_gate(paths, path.get("adaptive_context", {}))
                    save_profile(profile_data)
                    save_paths(paths)
                    add_notification("adaptation", "Learning style updated", f"Feedback received: {feedback_type}. Future steps will adapt.", "normal", f"/path/{path_id}")
                    return jsonify({"ok": True, "feedback": feedback, "profile": profile_data, "adaptive_context": path["adaptive_context"]})

    return jsonify({"ok": False, "error": "Path or step not found"}), 404


@app.route("/skill-tree")
def skill_tree():
    return jsonify(load_skill_tree())


@app.route("/notifications")
def notifications():
    return jsonify(load_notifications())


@app.route("/app-block", methods=["GET", "POST"])
def app_block():
    payload = load_app_block_intents()
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        payload["enabled"] = str(data.get("enabled", payload.get("enabled", False))).lower() in ["1", "true", "yes", "on"]
        payload["mode"] = clean_phrase(data.get("mode", payload.get("mode", "focus_session")))
        blocked = data.get("blocked_apps", payload.get("blocked_apps", []))
        allowed = data.get("allowed_apps", payload.get("allowed_apps", []))
        if isinstance(blocked, str):
            blocked = [clean_phrase(x) for x in blocked.split(",") if clean_phrase(x)]
        if isinstance(allowed, str):
            allowed = [clean_phrase(x) for x in allowed.split(",") if clean_phrase(x)]
        payload["blocked_apps"] = blocked
        payload["allowed_apps"] = allowed
        save_app_block_intents(payload)
        add_notification("focus", "App block intent updated", "Focus/app-block settings saved for future implementation.", "normal")
        return jsonify({"ok": True, "app_block": payload})
    return jsonify(payload)


@app.route("/api/recommendation")
def api_recommendation():
    paths = load_paths()
    profile_data = load_profile()
    return jsonify(recommend_next_action(paths, profile_data))


@app.route("/debug/ai")
def debug_ai():
    return jsonify({
        "openai_package_loaded": OpenAI is not None,
        "openai_api_key_loaded": bool(os.getenv("OPENAI_API_KEY")),
        "model": DEFAULT_MODEL,
        "data_file": DATA_FILE,
        "keep_going_mode": KEEP_GOING_MODE,
        "free_path_limit": FREE_PATH_LIMIT,
    })


@app.route("/debug/paths")
def debug_paths():
    paths = load_paths()
    return jsonify({
        "count": len(paths),
        "latest": paths[0] if paths else None,
    })


@app.route("/complete/<path_id>/<int:step_id>", methods=["POST"])
def complete_step(path_id, step_id):
    answer = request.form.get("answer", "").strip()
    paths = load_paths()
    profile_data = load_profile()

    for path in paths:
        if path["id"] == path_id:
            for step in path["steps"]:
                if step["id"] == step_id and step["status"] == "unlocked":
                    step["status"] = "done"
                    step["answer"] = answer
                    step["completed_at"] = now_stamp()

                    path.setdefault("events", []).append({
                        "type": "step_completed",
                        "step_id": step_id,
                        "answer_length": len(answer),
                        "energy_mode": profile_data.get("energy_mode"),
                        "created_at": now_stamp(),
                    })

                    for next_step in path["steps"]:
                        if next_step["id"] == step_id + 1 and next_step["status"] == "locked":
                            next_step["status"] = "unlocked"

                    path["progress"] = progress_percent(path)
                    path["adaptive_context"] = get_adaptive_context(paths, path.get("interest", ""), path.get("learning_goal", ""), profile_data)
                    path["keep_going_gate"] = get_keep_going_gate(paths, path.get("adaptive_context", {}))
                    update_profile_from_completion(profile_data, path, step)
                    tree = update_skill_tree(path, step)
                    save_paths(paths)
                    add_notification("progress", "Step completed", f"You gained XP in {path['adaptive_context'].get('bridge_type', 'general')}.", "normal", f"/path/{path_id}")
                    return redirect(url_for(
                        "path_detail",
                        path_id=path_id,
                        message="Nice — next step unlocked.",
                    ))

    return redirect(url_for("path_detail", path_id=path_id))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=6060, debug=True)
