"""
Educational Ontology Engine

Canonicalizes concept -> domain mappings so downstream engines don't inherit
incorrect domains from broad path titles like "Learn Spanish through film".

Outputs:
- data/educational_ontology_latest.json
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

CANONICAL_CONCEPT_DOMAINS = {
    # Web design / frontend
    "HTML structure": "web_design",
    "CSS selectors": "web_design",
    "responsive layout": "web_design",
    "buttons/forms": "web_design",
    "spacing": "web_design",
    "typography": "web_design",
    "visual hierarchy": "web_design",

    # Filmmaking
    "shot composition": "filmmaking",
    "storyboarding": "filmmaking",
    "lighting": "filmmaking",
    "pacing": "filmmaking",
    "scene emotion": "filmmaking",
    "editing continuity": "filmmaking",
    "sound design": "filmmaking",

    # Spanish / language learning
    "common phrases": "spanish",
    "nouns": "spanish",
    "gender agreement": "spanish",
    "verb conjugation": "spanish",
    "sentence structure": "spanish",
    "pronunciation": "spanish",
    "contextual vocabulary": "spanish",

    # Writing / school assignments
    "thesis": "writing_assignment",
    "outline": "writing_assignment",
    "source evidence": "writing_assignment",
    "citation": "writing_assignment",
    "paragraph structure": "writing_assignment",
    "revision": "writing_assignment",
    "rubric alignment": "writing_assignment",

    # Math / investing
    "probability": "math",
    "expected value": "investing_probability",
    "risk/reward": "investing_probability",
    "sample size": "investing_probability",
    "win rate": "investing_probability",
    "drawdown": "investing_probability",
    "position sizing": "investing_probability",
}

DOMAIN_LABELS = {
    "web_design": "Web Design",
    "filmmaking": "Filmmaking",
    "spanish": "Spanish / Language Learning",
    "writing_assignment": "Academic Writing",
    "math": "Math",
    "investing_probability": "Investing Probability",
    "general_learning": "General Learning",
}

DOMAIN_PRIORITY = [
    "spanish",
    "filmmaking",
    "web_design",
    "writing_assignment",
    "math",
    "investing_probability",
    "general_learning",
]


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


def infer_domain(concept, fallback_domains=None):
    if concept in CANONICAL_CONCEPT_DOMAINS:
        return CANONICAL_CONCEPT_DOMAINS[concept]
    fallback_domains = fallback_domains or []
    for domain in DOMAIN_PRIORITY:
        if domain in fallback_domains:
            return domain
    return fallback_domains[0] if fallback_domains else "general_learning"


def main():
    concept_payload = load_json("concept_extraction_latest.json", {})
    concept_domains = {}
    concept_sources = {}

    for path_item in concept_payload.get("path_concepts", []):
        fallback_domains = path_item.get("domains", [])
        for concept in path_item.get("concepts", []):
            concept_domains[concept] = infer_domain(concept, fallback_domains)
            concept_sources.setdefault(concept, []).append({
                "source": "path",
                "path_id": path_item.get("path_id"),
                "path_title": path_item.get("title"),
                "fallback_domains": fallback_domains,
            })

    assignment = concept_payload.get("assignment_concepts", {})
    for concept in assignment.get("concepts", []):
        fallback_domains = assignment.get("domains", [])
        concept_domains[concept] = infer_domain(concept, fallback_domains)
        concept_sources.setdefault(concept, []).append({
            "source": "assignment",
            "fallback_domains": fallback_domains,
        })

    domains = {}
    for concept, domain in concept_domains.items():
        domains.setdefault(domain, []).append(concept)

    payload = {
        "ok": True,
        "generated_at": now_iso(),
        "purpose": "Canonical concept-to-domain routing for curriculum, resources, simulations, and UI.",
        "concept_count": len(concept_domains),
        "domain_count": len(domains),
        "concept_domains": concept_domains,
        "domains": {domain: sorted(items) for domain, items in sorted(domains.items())},
        "domain_labels": DOMAIN_LABELS,
        "concept_sources": concept_sources,
        "routing_rules": [
            "Prefer canonical concept mappings over inherited path domains.",
            "Use path/assignment domains only as fallback context.",
            "A path can be interdisciplinary, but each concept should have its own canonical domain."
        ]
    }
    save_json("educational_ontology_latest.json", payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
