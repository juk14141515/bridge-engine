"""
Mastery Tracking Engine

Tracks learning evidence beyond simple completion.
Mastery is modeled as: exposure + practice + recall + application + transfer + confidence.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

MASTERY_WEIGHTS = {
    "exposure": 10,
    "practice": 20,
    "recall": 20,
    "application": 25,
    "transfer": 20,
    "confidence": 5,
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


def evidence_from_path(path, concept):
    steps = path.get("steps", [])
    done_steps = [s for s in steps if s.get("status") == "done"]
    text_blob = " ".join(
        [path.get("title", ""), path.get("learning_goal", ""), path.get("interest", "")] +
        [s.get("title", "") + " " + s.get("checkpoint", "") + " " + s.get("answer", "") for s in steps]
    ).lower()

    concept_terms = [part.lower() for part in concept.replace("/", " ").split() if len(part) > 2]
    mentioned = any(term in text_blob for term in concept_terms)

    evidence = {
        "exposure": mentioned or bool(steps),
        "practice": bool(done_steps),
        "recall": any(len(s.get("answer", "")) >= 40 for s in done_steps),
        "application": any(word in text_blob for word in ["built", "created", "changed", "made", "applied", "draft"]),
        "transfer": False,
        "confidence": any(word in text_blob for word in ["understand", "clear", "easy", "confident"]),
    }
    return evidence


def score_evidence(evidence):
    return sum(MASTERY_WEIGHTS[k] for k, v in evidence.items() if v)


def main():
    concepts_payload = load_json("concept_extraction_latest.json", {})
    paths = load_json("bridge_paths.json", [])
    path_lookup = {p.get("id"): p for p in paths}

    mastery_items = []
    for item in concepts_payload.get("path_concepts", []):
        path = path_lookup.get(item.get("path_id"), {})
        for concept in item.get("concepts", []):
            evidence = evidence_from_path(path, concept)
            score = score_evidence(evidence)
            mastery_items.append({
                "path_id": item.get("path_id"),
                "concept": concept,
                "domain": item.get("domains", ["general"])[0] if item.get("domains") else "general",
                "mastery_score": min(score, 100),
                "evidence": evidence,
                "mastery_level": "strong" if score >= 75 else "developing" if score >= 40 else "weak",
                "next_learning_need": "transfer_task" if score >= 60 else "practice_and_recall"
            })

    assignment = concepts_payload.get("assignment_concepts", {})
    for concept in assignment.get("concepts", []):
        mastery_items.append({
            "path_id": None,
            "concept": concept,
            "domain": assignment.get("domains", ["assignment"])[0] if assignment.get("domains") else "assignment",
            "mastery_score": 10,
            "evidence": {"exposure": True, "practice": False, "recall": False, "application": False, "transfer": False, "confidence": False},
            "mastery_level": "weak",
            "next_learning_need": "practice_and_recall"
        })

    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "purpose": "Track whether users are actually learning material, not just completing tasks.",
        "mastery_items": mastery_items,
        "mastery_model": MASTERY_WEIGHTS,
        "recommendations": [
            "Weak concepts should get explain-it-back checks.",
            "Developing concepts should get application tasks.",
            "Strong concepts should get transfer tasks.",
            "Completion should not equal mastery unless application/recall evidence exists."
        ]
    }
    (DATA_DIR / "mastery_tracking_latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
