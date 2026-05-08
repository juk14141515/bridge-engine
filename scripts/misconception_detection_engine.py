"""
Misconception Detection Engine

Detects likely root misunderstandings from prerequisite chains, mastery weakness,
recall evidence, and curriculum blocking. This is designed to catch false confidence
and prerequisite-level confusion before users are pushed into harder tasks.
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


def main():
    graph = load_json("prerequisite_graph_latest.json", {})
    mastery = load_json("mastery_tracking_latest.json", {})
    recall = load_json("recall_evidence_latest.json", {})
    ontology = load_json("educational_ontology_latest.json", {})

    mastery_by = {item.get("concept"): item for item in mastery.get("mastery_items", [])}
    concept_domains = ontology.get("concept_domains", {}) if isinstance(ontology, dict) else {}
    recall_by_concept = {}
    for item in recall.get("evidence", []):
        recall_by_concept.setdefault(item.get("concept"), []).append(item)

    misconceptions = []
    for node in graph.get("nodes", []):
        concept = node.get("concept")
        domain = concept_domains.get(concept, node.get("domain", "general_learning"))
        unmet = node.get("unmet_prerequisites", [])
        concept_score = mastery_by.get(concept, {}).get("mastery_score", node.get("mastery_score", 0))
        concept_recall = recall_by_concept.get(concept, [])
        answered = [r for r in concept_recall if r.get("response_present")]
        weak_answers = [r for r in answered if r.get("response_score", 0) < 35]

        if unmet:
            root_causes = []
            for prereq in unmet:
                prereq_score = mastery_by.get(prereq, {}).get("mastery_score", 0)
                root_causes.append({
                    "concept": prereq,
                    "domain": concept_domains.get(prereq, domain),
                    "mastery_score": prereq_score,
                    "reason": "required prerequisite is weak or missing"
                })
            misconceptions.append({
                "type": "prerequisite_gap",
                "concept": concept,
                "domain": domain,
                "severity": "high" if len(unmet) >= 2 else "medium",
                "evidence": {
                    "concept_mastery_score": concept_score,
                    "unmet_prerequisites": unmet,
                },
                "likely_root_causes": root_causes,
                "recommended_intervention": "return_to_prerequisite_micro_task",
                "coach_language": f"This may not be a motivation issue. {concept} may feel hard because prerequisite pieces are still shaky."
            })

        if weak_answers:
            misconceptions.append({
                "type": "weak_recall_or_false_fluency",
                "concept": concept,
                "domain": domain,
                "severity": "medium",
                "evidence": {
                    "weak_answer_count": len(weak_answers),
                    "average_response_score": round(sum(r.get("response_score", 0) for r in weak_answers) / len(weak_answers), 2),
                },
                "likely_root_causes": [{"concept": concept, "domain": domain, "reason": "answer exists but lacks strong explanation/application evidence"}],
                "recommended_intervention": "explain_back_with_example",
                "coach_language": f"You may recognize {concept}, but the system needs stronger proof that you can use it."
            })

    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "purpose": "Catch prerequisite gaps, weak recall, and possible false understanding before harder progression.",
        "misconception_count": len(misconceptions),
        "misconceptions": misconceptions[:150],
        "rules": [
            "Do not treat failure to start as laziness when prerequisite gaps exist.",
            "If advanced concepts are weak, inspect prerequisite concepts first.",
            "False fluency should trigger explain-back and application checks, not shame."
        ]
    }
    save_json("misconception_detection_latest.json", payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
