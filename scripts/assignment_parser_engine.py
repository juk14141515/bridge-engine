"""
Assignment Parser Engine

Prototype parser for pasted assignment/syllabus text.
Future versions can connect OCR, PDFs, Canvas, Google Calendar, etc.
For now it creates structured fields, hidden steps, risk flags, and a micro-start plan.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

INPUT_PATH = DATA_DIR / "assignment_intake_raw.txt"
OUTPUT_PATH = DATA_DIR / "assignment_parser_latest.json"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def read_input():
    if INPUT_PATH.exists():
        return INPUT_PATH.read_text(encoding="utf-8")
    sample = """
Research Paper: Analyze a topic from class using 3 academic sources. Due next Friday.
Requirements: 1200-1500 words, MLA citations, thesis statement, outline, rough draft, final draft.
"""
    INPUT_PATH.write_text(sample.strip(), encoding="utf-8")
    return sample.strip()


def extract_due_date(text):
    patterns = [
        r"due\s+([A-Za-z]+\s+\d{1,2})",
        r"due\s+(next\s+[A-Za-z]+)",
        r"deadline[:\s]+([^\.\n]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def infer_assignment_type(text):
    lower = text.lower()
    if "paper" in lower or "essay" in lower or "thesis" in lower:
        return "writing_assignment"
    if "exam" in lower or "test" in lower or "quiz" in lower:
        return "study_plan"
    if "project" in lower or "presentation" in lower:
        return "project_assignment"
    if "discussion" in lower or "post" in lower:
        return "discussion_post"
    return "general_assignment"


def split_requirements(text):
    candidates = re.split(r"[\n;•\-]+", text)
    cleaned = []
    for item in candidates:
        item = item.strip(" .:\t")
        if len(item) > 8:
            cleaned.append(item)
    return cleaned[:12]


def hidden_steps_for(kind):
    common = [
        "Open the instructions and identify the deliverable.",
        "Create a tiny first draft or outline.",
        "Separate unclear requirements from known requirements.",
        "Schedule at least one recovery buffer before the deadline.",
    ]
    by_kind = {
        "writing_assignment": [
            "Pick a rough topic even if imperfect.",
            "Find one source first, not all sources.",
            "Write a bad thesis draft.",
            "Build a 5-bullet outline before paragraphs.",
            "Convert outline bullets into rough paragraphs.",
            "Add citations after the rough structure exists.",
        ],
        "study_plan": [
            "List tested units.",
            "Make a 10-question self quiz.",
            "Mark weak topics.",
            "Review one weak topic in a 10-minute sprint.",
        ],
        "project_assignment": [
            "Define the smallest presentable version.",
            "Create a visible artifact first.",
            "Break build, review, and polish into separate sessions.",
        ],
        "discussion_post": [
            "Write one sentence opinion first.",
            "Add one quote or reference.",
            "Reply to one peer with a specific observation.",
        ],
    }
    return common + by_kind.get(kind, [])


def risk_flags(text, requirements):
    lower = text.lower()
    flags = []
    if any(term in lower for term in ["final", "major", "research", "presentation"]):
        flags.append("high_weight_assignment")
    if any(term in lower for term in ["source", "citation", "mla", "apa"]):
        flags.append("citation_or_source_complexity")
    if len(requirements) >= 6:
        flags.append("many_requirements")
    if not extract_due_date(text):
        flags.append("missing_or_unclear_deadline")
    if "rough draft" in lower and "final" in lower:
        flags.append("multi_stage_deliverable")
    return flags


def build_plan(text):
    kind = infer_assignment_type(text)
    requirements = split_requirements(text)
    risks = risk_flags(text, requirements)
    hidden_steps = hidden_steps_for(kind)

    plan = {
        "ok": True,
        "generated_at": now_iso(),
        "synthetic_or_manual_input": "manual_or_sample",
        "assignment_type": kind,
        "due_date_detected": extract_due_date(text),
        "raw_text_preview": text[:500],
        "requirements": requirements,
        "hidden_steps": hidden_steps,
        "risk_flags": risks,
        "recommended_start_mode": "micro_start",
        "recommended_first_action": "Open the assignment and write the smallest visible deliverable in one sentence.",
        "estimated_sessions": [
            {"name": "micro_start", "minutes": 5, "goal": "Identify deliverable and first visible artifact."},
            {"name": "structure", "minutes": 15, "goal": "Turn requirements into checklist."},
            {"name": "rough_build", "minutes": 25, "goal": "Create imperfect first version."},
            {"name": "finish_support", "minutes": 20, "goal": "Polish only after rough version exists."},
        ],
        "recovery_plan": {
            "if_overwhelmed": "Do only the 2-minute open-and-highlight step.",
            "if_late": "Switch to minimum viable submission plan.",
            "if_unclear": "List questions separately instead of stopping."
        }
    }
    return plan


def main():
    text = read_input()
    plan = build_plan(text)
    OUTPUT_PATH.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
