"""
Recall Evidence Engine

Converts knowledge-check responses/events into learning evidence.
Prototype behavior:
- Reads knowledge_checks_latest.json.
- Optionally reads data/recall_responses.json if present.
- Scores recall/application confidence with simple heuristics.
- Writes recall_evidence_latest.json for mastery updates later.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


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


def save_json(name, payload):
    (DATA_DIR / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def score_response(text):
    if not text:
        return {
            "answered": False,
            "score": 0,
            "quality": "missing",
            "signals": []
        }
    lower = text.lower().strip()
    signals = []
    score = 0
    if len(lower) >= 30:
        score += 25
        signals.append("specific_length")
    if any(word in lower for word in ["because", "for example", "means", "used to", "works by", "when"]):
        score += 25
        signals.append("explanation_signal")
    if any(char.isdigit() for char in lower) or any(mark in lower for mark in [":", "-", "<", ">", "="]):
        score += 15
        signals.append("concrete_example_signal")
    if any(word in lower for word in ["i think", "not sure", "maybe", "confused"]):
        score -= 10
        signals.append("low_confidence_signal")
    score = max(0, min(score, 100))
    quality = "strong" if score >= 70 else "developing" if score >= 35 else "weak"
    return {"answered": True, "score": score, "quality": quality, "signals": signals}


def main():
    checks_payload = load_json("knowledge_checks_latest.json", {"checks": []})
    responses_payload = load_json("recall_responses.json", {"responses": []})

    responses_by_id = {
        item.get("check_id"): item for item in responses_payload.get("responses", []) if item.get("check_id")
    }

    evidence = []
    for check in checks_payload.get("checks", []):
        response = responses_by_id.get(check.get("id"), {})
        response_text = response.get("answer", "")
        scored = score_response(response_text)
        evidence.append({
            "check_id": check.get("id"),
            "concept": check.get("concept"),
            "domain": check.get("domain"),
            "evidence_type": check.get("evidence_type"),
            "mastery_level_before": check.get("mastery_level"),
            "response_present": scored["answered"],
            "response_score": scored["score"],
            "response_quality": scored["quality"],
            "signals": scored["signals"],
            "mastery_delta": 15 if scored["score"] >= 70 else 7 if scored["score"] >= 35 else 0,
            "next_action": "promote_or_apply" if scored["score"] >= 70 else "retry_with_hint" if scored["answered"] else "ask_check"
        })

    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "purpose": "Score recall/application answers as actual evidence of learning.",
        "evidence_count": len(evidence),
        "evidence": evidence,
        "input_note": "Add data/recall_responses.json with responses to generate real recall evidence."
    }
    save_json("recall_evidence_latest.json", payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
