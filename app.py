from flask import Flask, render_template, request, redirect, url_for
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
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


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
    value = re.sub(r"\s+", " ", value)
    return value


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
        # Last-resort extraction if the model accidentally adds text around JSON.
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            return json.loads(text[first_brace:last_brace + 1])
        raise


def validate_steps(payload, interest, learning_goal):
    if isinstance(payload, list):
        raw_steps = payload
    elif isinstance(payload, dict):
        raw_steps = payload.get("steps", [])
    else:
        raw_steps = []

    cleaned = []
    for step in raw_steps[:4]:
        if not isinstance(step, dict):
            continue
        title = clean_phrase(step.get("title", ""))
        why = clean_phrase(step.get("why", ""))
        checkpoint = clean_phrase(step.get("checkpoint", ""))
        if title and why and checkpoint:
            cleaned.append({
                "title": title,
                "why": why,
                "checkpoint": checkpoint,
            })

    if len(cleaned) == 4:
        return cleaned

    print(f"AI WARNING: Expected 4 valid steps, got {len(cleaned)}. Using fallback.")
    return fallback_path(interest, learning_goal)


def ai_steps(interest, learning_goal):
    interest = clean_phrase(interest)
    learning_goal = display_learning_goal(learning_goal)

    print("AI FUNCTION CALLED")

    if OpenAI is None:
        print("AI ERROR: OpenAI package not installed. Run: python -m pip install openai")
        return fallback_path(interest, learning_goal)

    if not os.getenv("OPENAI_API_KEY"):
        print("AI ERROR: OPENAI_API_KEY is missing. Check your .env file.")
        return fallback_path(interest, learning_goal)

    client = OpenAI()

    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You generate ADHD-friendly bridge learning plans. "
                        "Return ONLY a valid JSON object with a top-level key named steps."
                    ),
                },
                {
                    "role": "user",
                    "content": f"""
Create a bridge learning path.

Interest: {interest}
Learning goal: {learning_goal}

Return JSON exactly like this:
{{
  "steps": [
    {{
      "title": "Step title",
      "why": "Why this matters",
      "checkpoint": "What the user must do"
    }}
  ]
}}

Rules:
- Exactly 4 steps.
- Make every step specific to the user's interest and learning goal.
- Make every step practical, short, and connected to a real output.
- Each step should take about 5-15 minutes.
- Avoid generic titles like "Define the real outcome" unless the title is specific to the project.
- Make it feel useful, not academic.
- No markdown.
- No explanation outside the JSON.
""",
                },
            ],
        )

        text = response.choices[0].message.content.strip()
        print("RAW AI OUTPUT:", text)
        payload = safe_json_loads(text)
        return validate_steps(payload, interest, learning_goal)

    except Exception:
        print("FULL AI ERROR:")
        traceback.print_exc()
        return fallback_path(interest, learning_goal)


def generate_path(interest, learning_goal):
    interest = clean_phrase(interest)
    learning_goal = display_learning_goal(learning_goal)
    steps = ai_steps(interest, learning_goal)

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
        "steps": formatted_steps,
    }


def progress_percent(path):
    total = len(path["steps"])
    done = len([s for s in path["steps"] if s["status"] == "done"])
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
