"""
Prerequisite Graph Engine

Builds concept prerequisites so Bridge Engine can unlock learning in a smarter order.
Reads concept/mastery/ontology outputs and writes data/prerequisite_graph_latest.json.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

PREREQS = {
    "responsive layout": ["HTML structure", "CSS selectors", "spacing"],
    "buttons/forms": ["HTML structure", "CSS selectors"],
    "CSS selectors": ["HTML structure"],
    "editing continuity": ["shot composition", "pacing"],
    "pacing": ["scene emotion"],
    "lighting": ["shot composition"],
    "gender agreement": ["nouns"],
    "sentence structure": ["nouns", "verb conjugation"],
    "contextual vocabulary": ["common phrases"],
    "pronunciation": ["common phrases"],
    "paragraph structure": ["thesis", "outline"],
    "source evidence": ["thesis", "citation"],
    "revision": ["paragraph structure"],
    "rubric alignment": ["outline"],
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


def save_json(name, payload):
    (DATA_DIR / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main():
    concepts_payload = load_json("concept_extraction_latest.json", {})
    mastery_payload = load_json("mastery_tracking_latest.json", {})
    ontology_payload = load_json("educational_ontology_latest.json", {})

    concepts = set()
    for item in concepts_payload.get("path_concepts", []):
        concepts.update(item.get("concepts", []))
    concepts.update(concepts_payload.get("assignment_concepts", {}).get("concepts", []))

    mastery_by_concept = {item.get("concept"): item for item in mastery_payload.get("mastery_items", [])}
    canonical_domains = ontology_payload.get("concept_domains", {}) if isinstance(ontology_payload, dict) else {}

    nodes = []
    edges = []
    unlock_plan = []

    for concept in sorted(concepts):
        prereqs = PREREQS.get(concept, [])
        mastery = mastery_by_concept.get(concept, {})
        score = mastery.get("mastery_score", 0)
        unmet = []
        for pre in prereqs:
            pre_score = mastery_by_concept.get(pre, {}).get("mastery_score", 0)
            edges.append({"from": pre, "to": concept, "type": "prerequisite", "prereq_mastery_score": pre_score})
            if pre_score < 40:
                unmet.append(pre)
        nodes.append({
            "concept": concept,
            "domain": canonical_domains.get(concept, mastery.get("domain", "general")),
            "mastery_score": score,
            "prerequisites": prereqs,
            "unmet_prerequisites": unmet,
            "unlock_status": "ready" if not unmet else "blocked_by_prereqs",
        })
        unlock_plan.append({
            "concept": concept,
            "next_action": "learn_now" if not unmet else "learn_prerequisites_first",
            "unmet_prerequisites": unmet,
        })

    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "purpose": "Order concepts by prerequisite readiness so paths unlock intelligently.",
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "unlock_plan": unlock_plan,
        "rules": [
            "Do not push advanced tasks before prerequisite concepts exist.",
            "Weak prerequisites should trigger micro-review or example-first learning.",
            "Ready concepts can be used in curriculum sequencing."
        ]
    }
    save_json("prerequisite_graph_latest.json", payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
