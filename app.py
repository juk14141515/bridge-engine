from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import re
import traceback
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

app = Flask(__name__)

DATA_FILE = "data/bridge_paths.json"
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def load_paths():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_paths(paths):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(paths, f, indent=2)


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


def fallback_path(interest, learning_goal):
    learning = display_learning_goal(learning_goal)
    interest = clean_phrase(interest)
    return [
        {
            "title": "Define the real outcome",
            "why": f"This makes {learning} feel useful instead of random.",
            "checkpoint": f"Write one sentence explaining how {learning} helps with {interest}.",
        },
        {
            "title": f"Learn one useful concept from {learning}",
            "why": "Small wins reduce friction and make starting easier.",
            "checkpoint": "Explain the concept in 2-3 sentences using your own words.",
        },
        {
            "title": f"Apply it to {interest}",
            "why": "Application turns learning into something real.",
            "checkpoint": "Describe what you built, changed, or created.",
        },
        {
            "title": "Review the result",
            "why": "Reflection helps your brain connect effort to reward.",
            "checkpoint": "Write what improved and what the next upgrade should be.",
        },
    ]


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


def generate_ai_steps(interest, learning_goal):
    interest = clean_phrase(interest)
    learning_goal = display_learning_goal(learning_goal)

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

Return JSON exactly like this:
{{
  "steps": [
    {{
      "title": "Specific action title",
      "why": "One sentence explaining why this directly helps the user's interest/project.",
      "checkpoint": "A concrete 5-15 minute task the user can complete to prove progress."
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
- Assume the user may have ADHD and needs short, high-reward actions.
- Keep each checkpoint doable in 5-15 minutes.
- Make the language direct and motivating.

Bad example:
"Learn one useful concept from probability."

Good example:
"Build a 5-trade expected value table for your trading bot."

Bad example:
"Apply Spanish to websites."

Good example:
"Replace 8 homepage labels with Spanish UI phrases and add an English translation note beside each one."

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


def build_steps(interest, learning_goal):
    print("AI FUNCTION CALLED")
    try:
        steps, error = generate_ai_steps(interest, learning_goal)
        if steps:
            return steps, "ai", ""
        print("AI FALLBACK REASON:", error)
        return fallback_path(interest, learning_goal), "fallback", error
    except Exception:
        error = traceback.format_exc()
        print("FULL AI ERROR:")
        print(error)
        return fallback_path(interest, learning_goal), "fallback", error.splitlines()[-1] if error else "Unknown AI error"


def generate_path(interest, learning_goal):
    interest = clean_phrase(interest)
    learning_goal = display_learning_goal(learning_goal)
    steps, source, error = build_steps(interest, learning_goal)

    formatted_steps = []
    for i, step in enumerate(steps, start=1):
        formatted_steps.append({
            "id": i,
            "title": step["title"],
            "status": "unlocked" if i == 1 else "locked",
            "why": step["why"],
            "checkpoint": step["checkpoint"],
            "answer": "",
        })

    return {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "interest": interest,
        "learning_goal": learning_goal,
        "title": f"Learn {learning_goal} through {interest}",
        "source": source,
        "ai_model": DEFAULT_MODEL if source == "ai" else "fallback",
        "ai_error": error,
        "steps": formatted_steps,
    }


def progress_percent(path):
    total = len(path.get("steps", []))
    done = len([s for s in path.get("steps", []) if s.get("status") == "done"])
    return int((done / total) * 100) if total else 0


@app.route("/")
def index():
    paths = load_paths()
    for path in paths:
        path["progress"] = progress_percent(path)
    return render_template("index.html", paths=paths)


@app.route("/create", methods=["POST"])
def create():
    interest = request.form.get("interest", "").strip()
    learning_goal = request.form.get("learning_goal", "").strip()

    if not interest or not learning_goal:
        return redirect(url_for("index"))

    paths = load_paths()
    new_path = generate_path(interest, learning_goal)
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
    message = request.args.get("message", "")

    return render_template("path.html", path=path, message=message)


@app.route("/debug/ai")
def debug_ai():
    return jsonify({
        "openai_package_loaded": OpenAI is not None,
        "openai_api_key_loaded": bool(os.getenv("OPENAI_API_KEY")),
        "model": DEFAULT_MODEL,
        "data_file": DATA_FILE,
    })


@app.route("/complete/<path_id>/<int:step_id>", methods=["POST"])
def complete_step(path_id, step_id):
    answer = request.form.get("answer", "").strip()
    paths = load_paths()

    for path in paths:
        if path["id"] == path_id:
            for step in path["steps"]:
                if step["id"] == step_id and step["status"] == "unlocked":
                    step["status"] = "done"
                    step["answer"] = answer

                    for next_step in path["steps"]:
                        if next_step["id"] == step_id + 1 and next_step["status"] == "locked":
                            next_step["status"] = "unlocked"

                    save_paths(paths)
                    return redirect(url_for(
                        "path_detail",
                        path_id=path_id,
                        message="Nice — next step unlocked.",
                    ))

    return redirect(url_for("path_detail", path_id=path_id))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=6060, debug=True)
