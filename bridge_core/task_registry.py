"""Canonical task registry for Bridge Engine runtime.

The registry is intentionally dependency-light so every backend layer can agree
on the same task/category names. Frontend labels can change, but these canonical
keys should stay stable for persistence, artifact routing, and exports.
"""

from __future__ import annotations

from typing import Dict, Iterable

TASK_TYPES: Dict[str, Dict[str, str]] = {
    "essay_writing": {
        "label": "Essay / writing",
        "artifact_type": "document_draft",
        "final_output": "polished draft",
        "intent": "Turn scattered thoughts into a structured written piece.",
    },
    "language_learning": {
        "label": "Language learning",
        "artifact_type": "language_practice_set",
        "final_output": "practice sheet",
        "intent": "Build usable practice through phrases, memory hooks, and mini-output.",
    },
    "coding_project": {
        "label": "Coding / project",
        "artifact_type": "implementation_plan",
        "final_output": "ship checklist",
        "intent": "Move a project from ambiguity into executable slices.",
    },
    "study_prep": {
        "label": "Study / test prep",
        "artifact_type": "study_guide",
        "final_output": "review sheet",
        "intent": "Convert material into recall prompts and a usable study guide.",
    },
    "difficult_conversation": {
        "label": "Difficult conversation",
        "artifact_type": "conversation_draft",
        "final_output": "message or talking points",
        "intent": "Turn emotional ambiguity into clear, kind, usable words.",
    },
    "professional_strategy": {
        "label": "Professional strategy",
        "artifact_type": "decision_memo",
        "final_output": "strategy memo",
        "intent": "Turn complex work into a clear decision/output artifact.",
    },
    "life_admin": {
        "label": "Life admin",
        "artifact_type": "action_plan",
        "final_output": "done list",
        "intent": "Reduce friction and create visible progress in practical tasks.",
    },
    "general": {
        "label": "General Bridge",
        "artifact_type": "completion_plan",
        "final_output": "finished output",
        "intent": "Create a low-friction path into the work.",
    },
}

ALIASES = {
    "essay": "essay_writing",
    "paper": "essay_writing",
    "writing": "essay_writing",
    "language": "language_learning",
    "learn_language": "language_learning",
    "spanish": "language_learning",
    "code": "coding_project",
    "coding": "coding_project",
    "project": "coding_project",
    "study": "study_prep",
    "exam": "study_prep",
    "test": "study_prep",
    "conversation": "difficult_conversation",
    "relationship": "difficult_conversation",
    "professional": "professional_strategy",
    "strategy": "professional_strategy",
    "memo": "professional_strategy",
    "business": "professional_strategy",
    "chores": "life_admin",
    "cleaning": "life_admin",
    "admin": "life_admin",
}

KEYWORDS = {
    "language_learning": [
        "spanish", "french", "german", "italian", "japanese", "korean", "mandarin",
        "language", "vocabulary", "grammar", "pronunciation", "duolingo", "conversation practice",
        "learn spanish", "hablar", "español",
    ],
    "essay_writing": [
        "essay", "paper", "paragraph", "thesis", "writing assignment", "draft", "write-up",
        "research paper", "introduction", "conclusion",
    ],
    "coding_project": [
        "code", "coding", "bug", "app", "website", "python", "react", "typescript",
        "javascript", "backend", "frontend", "repo", "feature", "ship", "build",
    ],
    "study_prep": [
        "study", "exam", "quiz", "test", "flashcards", "chapter", "memorize", "notes",
        "lecture", "learn for", "review",
    ],
    "difficult_conversation": [
        "conversation", "apology", "message", "text", "relationship", "boundary", "talk to",
        "girlfriend", "boyfriend", "friend", "parent", "roommate", "conflict",
    ],
    "professional_strategy": [
        "memo", "strategy", "product", "business", "decision", "proposal", "client",
        "meeting", "roadmap", "pitch", "investor", "market", "professional",
    ],
    "life_admin": [
        "chores", "room", "laundry", "clean", "email", "errands", "admin", "bills",
        "schedule", "appointment", "reset my space", "organize",
    ],
}


def normalize_category(category: str | None) -> str:
    key = (category or "").strip().lower().replace(" ", "_").replace("-", "_")
    if not key:
        return "general"
    if key in TASK_TYPES:
        return key
    return ALIASES.get(key, "general")


def detect_task_type(task: str, category: str = "") -> str:
    normalized = normalize_category(category)
    if normalized != "general":
        return normalized

    text = f"{task or ''} {category or ''}".lower()
    for task_type, words in KEYWORDS.items():
        if _contains_any(text, words):
            return task_type
    return "general"


def get_task_type(task_type: str) -> Dict[str, str]:
    return TASK_TYPES.get(normalize_category(task_type), TASK_TYPES["general"])


def legacy_task_type(task_type: str) -> str:
    """Map canonical keys to the short keys older code expects."""
    return {
        "essay_writing": "essay",
        "language_learning": "language_learning",
        "coding_project": "coding_project",
        "study_prep": "study",
        "difficult_conversation": "relationship",
        "professional_strategy": "professional_strategy",
        "life_admin": "chores",
        "general": "generic",
    }.get(task_type, "generic")


def _contains_any(text: str, words: Iterable[str]) -> bool:
    return any(word in text for word in words)
