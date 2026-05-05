from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

app = Flask(__name__)

DATA_FILE = "data/bridge_paths.json"


def load_paths():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_paths(paths):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(paths, f, indent=2)


def fallback_path(interest, learning_goal):
    return [
        {
            "title": "Define the real outcome",
            "why": f"This makes {learning_goal} feel useful instead of random.",
            "checkpoint": f"Write how learning {learning_goal} helps you with {interest}.",
        },
        {
            "title": f"Learn one useful concept from {learning_goal}",
            "why": "Small wins reduce friction and make starting easier.",
            "checkpoint": "Explain the concept in 2-3 sentences.",
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


def ai_steps(interest, learning_goal):
    print("AI FUNCTION CALLED")

    if OpenAI is None:
        print("AI ERROR: OpenAI package not installed.")
        return fallback_path(interest, learning_goal)

    if not os.getenv("OPENAI_API_KEY"):
        print("AI ERROR: OPENAI_API_KEY is missing.")
        return fallback_path(interest, learning_goal)

    client = OpenAI()

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": "You generate structured ADHD-friendly bridge learning plans. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": f"""
Create a bridge learning path.

Interest: {interest}
Learning goal: {learning_goal}

Return ONLY valid JSON in this exact format:

[
  {{
    "title": "Step title",
    "why": "Why it matters",
    "checkpoint": "What user must do"
  }}
]

Rules:
- Exactly 4 steps.
- Make every step specific to the user's interest.
- Make every step practical, short, and connected to a real output.
- Each step should take about 5-15 minutes.
- Make it feel useful, not academic.
- No markdown.
- No explanation outside the JSON.
"""
                }
            ],
        )

        text = response.output_text.strip()
        print("RAW AI OUTPUT:", text)

        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()

        steps = json.loads(text)

        cleaned = []
        for step in steps[:4]:
            cleaned.append({
                "title": step.get("title", "Untitled step"),
                "why": step.get("why", "This connects learning to your goal."),
                "checkpoint": step.get("checkpoint", "Complete a short checkpoint."),
            })

        return cleaned if cleaned else fallback_path(interest, learning_goal)

    except Exception as e:
        print("AI ERROR:", e)
        return fallback_path(interest, learning_goal)


def generate_path(interest, learning_goal):
    steps = ai_steps(interest, learning_goal)

    formatted_steps = []
    for i, step in enumerate(steps, start=1):
        formatted_steps.append({
            "id": i,
            "title": step["title"],
            "status": "unlocked" if i == 1 else "locked",
            "why": step["why"],
            "checkpoint": step["checkpoint"],
            "answer": ""
        })

    return {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "interest": interest,
        "learning_goal": learning_goal,
        "title": f"Learn {learning_goal} through {interest}",
        "steps": formatted_steps
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
                        message="Nice — next step unlocked."
                    ))

    return redirect(url_for("path_detail", path_id=path_id))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=6060, debug=True)

