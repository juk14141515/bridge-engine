"""
Curriculum Sequencing Engine

Builds pacing-aware, interactive learning roadmaps from ontology, prerequisites,
mastery, and adaptive difficulty. Designed to avoid passive "watch a video" learning.
Every sequence item should require the learner to create, explain, apply, or reflect.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

LEVEL_THRESHOLDS = {
    "beginner": 0,
    "intermediate": 40,
    "advanced": 70,
}

INTERACTIVE_TASKS = {
    "web_design": [
        "Create a tiny HTML/CSS artifact using this concept.",
        "Modify one visible element and explain what changed.",
        "Fix a small broken example involving this concept."
    ],
    "filmmaking": [
        "Record or storyboard a 10-second example using this concept.",
        "Compare two shots/scenes and explain how this concept changes the feeling.",
        "Create a before/after version using this concept."
    ],
    "spanish": [
        "Say or write three original examples using this concept.",
        "Use this concept in a real sentence about your life.",
        "Teach this concept back in your own words."
    ],
    "writing_assignment": [
        "Create one usable sentence or checklist item for the assignment.",
        "Apply this concept to the current assignment draft.",
        "Explain how this concept affects the final deliverable."
    ],
    "general_learning": [
        "Create one visible artifact that proves you used this concept.",
        "Explain this concept like you are teaching a friend.",
        "Apply this concept to a new example."
    ]
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


def level_for_score(score):
    if score >= LEVEL_THRESHOLDS["advanced"]:
        return "advanced"
    if score >= LEVEL_THRESHOLDS["intermediate"]:
        return "intermediate"
    return "beginner"


def interactive_prompt(domain, concept, level):
    options = INTERACTIVE_TASKS.get(domain, INTERACTIVE_TASKS["general_learning"])
    base = options[0 if level == "beginner" else 1 if level == "intermediate" else 2]
    return f"{base} Concept: {concept}."


def main():
    ontology = load_json("educational_ontology_latest.json", {})
    graph = load_json("prerequisite_graph_latest.json", {})
    mastery = load_json("mastery_tracking_latest.json", {})
    difficulty = load_json("adaptive_difficulty_latest.json", {})
    profile = load_json("adaptive_user_profile_latest.json", {})

    concept_domains = ontology.get("concept_domains", {})
    mastery_by_concept = {item.get("concept"): item for item in mastery.get("mastery_items", [])}
    graph_nodes = graph.get("nodes", [])

    activation_profile = profile.get("activation_profile", "standard")
    global_mode = difficulty.get("global_difficulty_mode", "balanced")
    base_minutes = 3 if global_mode == "recovery_first" or activation_profile == "micro_start_needed" else 8

    sequences_by_domain = {}
    flat_sequence = []

    # Ready concepts first, then blocked concepts after prerequisites.
    sorted_nodes = sorted(
        graph_nodes,
        key=lambda n: (
            0 if n.get("unlock_status") == "ready" else 1,
            n.get("mastery_score", 0),
            n.get("concept", "")
        )
    )

    for order, node in enumerate(sorted_nodes, start=1):
        concept = node.get("concept")
        domain = concept_domains.get(concept, node.get("domain", "general_learning"))
        mastery_score = mastery_by_concept.get(concept, {}).get("mastery_score", node.get("mastery_score", 0))
        level = level_for_score(mastery_score)
        ready = node.get("unlock_status") == "ready"
        item = {
            "order": order,
            "concept": concept,
            "domain": domain,
            "level": level,
            "unlock_status": node.get("unlock_status"),
            "unmet_prerequisites": node.get("unmet_prerequisites", []),
            "estimated_minutes": base_minutes if level == "beginner" else base_minutes + 5,
            "mode": "micro_interactive" if base_minutes <= 3 else "guided_interactive",
            "learning_action": interactive_prompt(domain, concept, level),
            "proof_required": {
                "type": "artifact_or_explain_back",
                "description": "User must create, explain, apply, or correct something. Passive watching does not count.",
                "acceptable_evidence": ["typed answer", "project artifact", "voice explanation", "photo/screenshot", "checklist output"]
            },
            "can_start_now": ready,
        }
        sequences_by_domain.setdefault(domain, []).append(item)
        flat_sequence.append(item)

    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "purpose": "Create interactive, mastery-aware learning roadmaps that require active work.",
        "global_mode": global_mode,
        "activation_profile": activation_profile,
        "sequence_count": len(flat_sequence),
        "next_best_items": [item for item in flat_sequence if item.get("can_start_now")][:8],
        "blocked_items": [item for item in flat_sequence if not item.get("can_start_now")][:12],
        "sequences_by_domain": sequences_by_domain,
        "anti_passive_learning_rules": [
            "Do not count watching a video as completion by itself.",
            "Every lesson requires a learner-produced artifact, explanation, application, correction, or reflection.",
            "Resources may support learning, but the path advances only after active evidence."
        ]
    }
    save_json("curriculum_sequence_latest.json", payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
