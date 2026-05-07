"""
Concept Extraction Engine

Turns goals, assignments, and paths into actual learning concepts.
This helps Bridge Engine ensure users are learning real material, not just completing tasks.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

CONCEPT_MAP = {
    "web_design": [
        "HTML structure", "CSS selectors", "spacing", "typography", "responsive layout", "buttons/forms", "visual hierarchy"
    ],
    "filmmaking": [
        "shot composition", "storyboarding", "lighting", "pacing", "scene emotion", "editing continuity", "sound design"
    ],
    "spanish": [
        "common phrases", "nouns", "gender agreement", "verb conjugation", "sentence structure", "pronunciation", "contextual vocabulary"
    ],
    "math": [
        "definitions", "worked examples", "pattern recognition", "problem setup", "error checking", "transfer practice"
    ],
    "writing_assignment": [
        "thesis", "outline", "source evidence", "citation", "paragraph structure", "revision", "rubric alignment"
    ],
    "investing_probability": [
        "probability", "expected value", "risk/reward", "sample size", "win rate", "drawdown", "position sizing"
    ]
}

KEYWORD_DOMAINS = {
    "web_design": ["html", "css", "website", "landing page", "frontend", "responsive", "button"],
    "filmmaking": ["film", "movie", "scene", "shot", "edit", "storyboard", "camera"],
    "spanish": ["spanish", "español", "translate", "language"],
    "math": ["math", "algebra", "function", "slope", "factor", "equation", "probability"],
    "writing_assignment": ["essay", "paper", "thesis", "sources", "mla", "apa", "draft"],
    "investing_probability": ["invest", "trading", "stock", "expected value", "risk", "win rate"]
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


def infer_domains(text):
    lower = text.lower()
    domains = []
    for domain, words in KEYWORD_DOMAINS.items():
        score = sum(1 for word in words if word in lower)
        if score:
            domains.append((domain, score))
    domains.sort(key=lambda x: x[1], reverse=True)
    return [d for d, _ in domains[:3]] or ["general_learning"]


def extract_from_paths(paths):
    extracted = []
    for path in paths:
        text = " ".join([
            str(path.get("interest", "")),
            str(path.get("learning_goal", "")),
            str(path.get("title", "")),
            " ".join(step.get("title", "") + " " + step.get("checkpoint", "") for step in path.get("steps", []))
        ])
        domains = infer_domains(text)
        concepts = []
        for domain in domains:
            concepts.extend(CONCEPT_MAP.get(domain, []))
        extracted.append({
            "path_id": path.get("id"),
            "title": path.get("title"),
            "domains": domains,
            "concepts": sorted(set(concepts))[:12],
            "learning_goal": path.get("learning_goal"),
            "interest": path.get("interest")
        })
    return extracted


def extract_from_assignment(assignment):
    raw = assignment.get("raw_text_preview", "") if isinstance(assignment, dict) else ""
    kind = assignment.get("assignment_type", "") if isinstance(assignment, dict) else ""
    text = raw + " " + kind + " " + " ".join(assignment.get("requirements", [])) if isinstance(assignment, dict) else raw
    domains = infer_domains(text)
    concepts = []
    for domain in domains:
        concepts.extend(CONCEPT_MAP.get(domain, []))
    return {
        "domains": domains,
        "concepts": sorted(set(concepts))[:12],
        "source": "assignment_parser_latest"
    }


def main():
    paths = load_json("bridge_paths.json", [])
    assignment = load_json("assignment_parser_latest.json", {})
    path_concepts = extract_from_paths(paths)
    assignment_concepts = extract_from_assignment(assignment)

    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "purpose": "Identify actual concepts users need to learn inside each execution path.",
        "path_concepts": path_concepts,
        "assignment_concepts": assignment_concepts,
        "next_use": [
            "Feed concepts into mastery tracking.",
            "Generate knowledge checks for each concept.",
            "Schedule spaced review for weak concepts.",
            "Avoid path completion without concept evidence."
        ]
    }
    (DATA_DIR / "concept_extraction_latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
