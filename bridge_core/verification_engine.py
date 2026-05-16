"""Verification engine.

Purpose:
Prevent fake completion loops.

This does NOT attempt perfect surveillance.
Instead it estimates whether meaningful work happened.

Signals:
- output quality
- length
- consistency
- recall accuracy
- progression continuity
- challenge completion
- reflection depth
- artifact evolution
"""

from __future__ import annotations

import re
from typing import Any, Dict


WEAK_EXACT = {
    "starting",
    "idk",
    "i don't know",
    "i dont know",
    "later",
    "done",
    "ok",
    "okay",
    "yes",
    "yeah",
    "yep",
    "nothing",
}

WEAK_PATTERNS = [
    re.compile(r"^starting\b", re.IGNORECASE),
    re.compile(r"^i('?|’)m\s+starting\b", re.IGNORECASE),
    re.compile(r"^working on it$", re.IGNORECASE),
    re.compile(r"^i will\b", re.IGNORECASE),
]

CONTENT_MARKERS = {
    "essay_writing": ["essay", "thesis", "social media", "attention", "paragraph", "argument", "evidence"],
    "language_learning": ["hola", "me llamo", "phrase", "spanish", "bonjour", "gracias", "adios"],
    "conversation": ["felt", "ignored", "tell them", "when", "plans changed", "boundary"],
    "professional": ["memo", "thesis", "evidence", "risk", "decision", "recommendation"],
    "coding_project": ["section", "module", "build", "implement", "intro", "solution"],
    "general": ["need", "about", "because", "three", "sections", "plan"],
}


class VerificationEngine:
    def verify_progress(
        self,
        previous_workspace: Dict[str, Any],
        user_output: str,
    ) -> Dict[str, Any]:
        output = (user_output or "").strip()
        normalized = re.sub(r"\s+", " ", output.lower()).strip(" .!?")
        words = re.findall(r"[\w'’]+", output)
        flags = []

        if not output:
            return self._result(False, 0, ["empty_response"], "Add one rough sentence so Bridge can shape the next step.")

        if normalized in WEAK_EXACT or any(pattern.search(normalized) for pattern in WEAK_PATTERNS):
            return self._result(
                False,
                10,
                ["vague_placeholder"],
                "That sounds like a plan to start. Add one concrete sentence, phrase, point, or detail and Bridge will move you forward.",
            )

        score = 0

        if len(output) >= 24:
            score += 20
        else:
            flags.append("very_short_response")

        if len(words) >= 5:
            score += 20
        else:
            flags.append("few_words")

        if any(word in normalized for word in ["learned", "built", "tested", "wrote", "need", "about", "felt", "hola"]):
            score += 20

        if re.search(r"\b(because|when|about|into|sections?|phrase|sentence|attention|ignored|solution)\b", normalized):
            score += 20

        if self._has_category_marker(previous_workspace, normalized):
            score += 35

        if "idk" in normalized or "nothing" in normalized or "don't know" in normalized or "dont know" in normalized:
            flags.append("low_confidence")
            score = min(score, 20)

        verified = score >= 50

        if not verified and not flags:
            flags.append("needs_more_specific_detail")

        message = (
            "Good rough work. Bridge can use this to build the next step."
            if verified
            else "Almost. Add one concrete detail so Bridge can keep the path honest."
        )
        return self._result(verified, min(score, 100), flags, message)

    def _next_action(self, verified: bool) -> str:
        if verified:
            return "advance"
        return "request_checkpoint"

    def _result(self, verified: bool, score: int, flags: list[str], message: str) -> Dict[str, Any]:
        return {
            "verified": verified,
            "confidence_score": score,
            "flags": flags,
            "message": message,
            "next_action": self._next_action(verified),
        }

    def _has_category_marker(self, workspace: Dict[str, Any], normalized: str) -> bool:
        category = str(workspace.get("category") or "general")
        task = str(workspace.get("task") or "").lower()
        markers = list(CONTENT_MARKERS.get(category, [])) + CONTENT_MARKERS["general"]
        if "essay" in task:
            markers += CONTENT_MARKERS["essay_writing"]
        if "spanish" in task or "language" in task:
            markers += CONTENT_MARKERS["language_learning"]
        if "conversation" in task:
            markers += CONTENT_MARKERS["conversation"]
        if "memo" in task:
            markers += CONTENT_MARKERS["professional"]
        return any(marker in normalized for marker in markers)
