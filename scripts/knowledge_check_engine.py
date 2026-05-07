"""
Knowledge Check Engine

Generates quick, low-friction checks for weak/developing concepts.
Goal: prove actual understanding with recall/application, not just task completion.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

QUESTION_TEMPLATES = {
    "weak": [
        "Explain {concept} in one sentence without looking it up.",
        "Give one tiny example of {concept}.",
        "What would be a common mistake someone makes with {concept}?",
    ],
    "developing": [
        "Apply {concept} to a new situation different from the original path.",
        "Compare {concept} to a related idea in your own words.",
    ],
    "strong": [
        "Teach {concept} to a beginner using an example.",
        "Create a transfer task that uses {concept} in a different domain.",
    ],
}

DOMAIN_HINTS = {
    "spanish": "Use a simple phrase or sentence as the example.",
    "writing_assignment": "Use a school assignment or essay example.",
    "web_design": "Use a tiny webpage/component example.",
    "filmmaking": "Use a shot, scene, or editing example.",
    "math": "Use a small numeric or visual example.",
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


def build_check(item):
    concept = item.get("concept", "the concept")
    level = item.get("mastery_level", "weak")
    domain = item.get("domain", "general")
    templates = QUESTION_TEMPLATES.get(level, QUESTION_TEMPLATES["weak"])
    checks = []
    for idx, template in enumerate(templates, start=1):
        checks.append({
            "id": f"{concept.lower().replace(' ', '_')}_{idx}",
            "concept": concept,
            "domain": domain,
            "mastery_level": level,
            "prompt": template.format(concept=concept),
            "hint": DOMAIN_HINTS.get(domain, "Use a concrete real-world example."),
            "evidence_type": "recall" if idx == 1 else "application",
            "estimated_minutes": 2,
            "success_criteria": [
                "Answer is specific, not vague.",
                "Answer uses an example or application.",
                "User can explain why it works."
            ]
        })
    return checks


def main():
    mastery = load_json("mastery_tracking_latest.json", {})
    items = mastery.get("mastery_items", []) if isinstance(mastery, dict) else []

    checks = []
    for item in items:
        if item.get("mastery_level") in ["weak", "developing", "strong"]:
            checks.extend(build_check(item))

    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "purpose": "Generate lightweight knowledge checks for actual learning validation.",
        "check_count": len(checks),
        "checks": checks[:150],
        "rules": [
            "Weak concepts get recall + tiny example checks.",
            "Developing concepts get application checks.",
            "Strong concepts get teach-back or transfer checks.",
            "Checks should feel like proof of understanding, not punishment."
        ]
    }
    (DATA_DIR / "knowledge_checks_latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
