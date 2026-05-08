"""
Semantic Memory Engine

Builds long-term adaptive coaching memory from the current backend outputs.
This is a lightweight JSON-first memory layer before vector embeddings/Postgres.

Purpose:
- Remember recurring friction patterns.
- Remember successful/likely interventions.
- Track concept/domain struggles.
- Preserve low-shame coaching rules.
- Prepare memory cards for UI and API routes.
"""

import json
from collections import Counter
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


def memory_text(kind, title, detail, confidence=0.7, source="system"):
    return {
        "kind": kind,
        "title": title,
        "detail": detail,
        "confidence": confidence,
        "source": source,
        "updated_at": now_iso(),
    }


def main():
    profile_payload = load_json("adaptive_user_profile_latest.json", {})
    profile = profile_payload.get("profile", profile_payload) if isinstance(profile_payload, dict) else {}
    misconceptions = load_json("misconception_detection_latest.json", {})
    execution = load_json("execution_reinforcement_latest.json", {})
    curriculum = load_json("curriculum_sequence_latest.json", {})
    ontology = load_json("educational_ontology_latest.json", {})
    recall = load_json("recall_evidence_latest.json", {})
    existing = load_json("semantic_memory_latest.json", {"memories": []})

    memories = []

    activation_profile = profile.get("activation_profile")
    if activation_profile:
        memories.append(memory_text(
            "activation_pattern",
            "Activation profile",
            f"Current activation profile appears to be {activation_profile}. Default to small, visible starts when resistance is high.",
            0.75,
            "adaptive_user_profile"
        ))

    classification = execution.get("classification", {}) if isinstance(execution, dict) else {}
    if classification:
        memories.append(memory_text(
            "failure_mode",
            "Knowledge vs activation split",
            f"Primary failure mode: {classification.get('primary_failure_mode')} with knowledge risk {classification.get('knowledge_risk')} and activation risk {classification.get('activation_risk')}.",
            0.7,
            "execution_reinforcement"
        ))

    interventions = execution.get("recommended_interventions", []) if isinstance(execution, dict) else []
    if interventions:
        top = interventions[0]
        memories.append(memory_text(
            "intervention_preference",
            "Top current intervention",
            f"Most useful current intervention appears to be {top.get('label')}: {top.get('description')}",
            0.65,
            "execution_reinforcement"
        ))

    domain_counter = Counter()
    concept_counter = Counter()
    for item in misconceptions.get("misconceptions", []) if isinstance(misconceptions, dict) else []:
        domain_counter[item.get("domain", "general_learning")] += 1
        concept_counter[item.get("concept", "unknown")] += 1

    for domain, count in domain_counter.most_common(5):
        memories.append(memory_text(
            "domain_friction",
            f"Recurring friction in {domain}",
            f"Detected {count} misconception/prerequisite warnings in {domain}. Use prerequisite micro-tasks and explain-back checks before advancing.",
            0.7,
            "misconception_detection"
        ))

    ready = curriculum.get("next_best_items", []) if isinstance(curriculum, dict) else []
    if ready:
        first = ready[0]
        memories.append(memory_text(
            "next_best_action",
            "Best current learning entry point",
            f"Start with {first.get('concept')} using mode {first.get('mode')}: {first.get('learning_action')}",
            0.8,
            "curriculum_sequence"
        ))

    unanswered = sum(1 for item in recall.get("evidence", []) if not item.get("response_present")) if isinstance(recall, dict) else 0
    if unanswered:
        memories.append(memory_text(
            "recall_gap",
            "Recall evidence missing",
            f"There are {unanswered} unanswered recall checks. Mastery should remain conservative until users submit active evidence.",
            0.8,
            "recall_evidence"
        ))

    concept_domains = ontology.get("concept_domains", {}) if isinstance(ontology, dict) else {}
    if concept_domains:
        memories.append(memory_text(
            "ontology_map",
            "Canonical learning domains available",
            f"System has {len(concept_domains)} concept-domain mappings for curriculum, resources, and coaching.",
            0.85,
            "educational_ontology"
        ))

    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "purpose": "Long-term adaptive coaching memory for friction, interventions, concepts, and active-learning evidence.",
        "memory_count": len(memories),
        "memories": memories,
        "memory_policy": {
            "privacy_note": "Prototype memory is local JSON. Before real users, move to isolated per-user storage with export/delete controls.",
            "no_medical_claims": True,
            "active_learning_first": True,
            "low_shame_language": True
        },
        "future_embedding_plan": [
            "Store memory cards in SQLite/Postgres.",
            "Create embeddings for memory detail text.",
            "Retrieve memories by current task/context.",
            "Decay stale memories unless reinforced by events."
        ]
    }
    save_json("semantic_memory_latest.json", payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
