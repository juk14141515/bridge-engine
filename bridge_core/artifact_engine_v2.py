"""Artifact engine V2.

Responsible for continuously building the user's final output while they work.
Every completed step updates a living artifact. The engine now compiles useful
category-specific previews instead of only listing raw sections.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ArtifactEngine:
    def __init__(self, workspace: Dict[str, Any]):
        self.workspace = workspace
        self.artifact = workspace.get("artifact") or {}
        self.sections = self.artifact.setdefault("sections", {})

    def apply_step_output(self, step: Dict[str, Any], output: str) -> Dict[str, Any]:
        slot = str(step.get("output_slot") or step.get("id") or "notes")
        current = str(self.sections.get(slot) or "")
        cleaned = (output or "").strip()

        merged = cleaned if not current else f"{current}\n\n{cleaned}"
        self.sections[slot] = merged

        self.artifact["updated_at"] = now()
        self.artifact["final_output"] = self.compile_preview()
        return self.artifact

    def compile_preview(self) -> str:
        category = str(self.artifact.get("category") or self.workspace.get("category") or "general")
        if category == "language_learning":
            return self._compile_language_practice_sheet()
        if category == "essay_writing":
            return self._compile_essay_draft()
        if category == "coding_project":
            return self._compile_coding_plan()
        return self._compile_generic_sections()

    def _compile_language_practice_sheet(self) -> str:
        task = self.artifact.get("task") or self.workspace.get("task") or "Language practice"
        frame = self.artifact.get("frame") or self.workspace.get("frame") or "something you enjoy"
        first = self.sections.get("first_concept") or self.sections.get("phrase_bank") or "Start with one phrase you can actually use."
        recall = self.sections.get("recall_prompt") or "Cover the phrase and say it without looking."
        attempt = self.sections.get("recall_attempt") or "Write or speak one tiny attempt. Mistakes are useful."
        summary = self.sections.get("summary") or "Save the phrases you would reuse tomorrow."
        return (
            f"# Practice Sheet: {task}\n\n"
            f"Frame: {frame}\n\n"
            f"## 1. Useful Phrase / Concept\n{first}\n\n"
            f"## 2. Quick Recall Prompt\n{recall}\n\n"
            f"## 3. Practice Attempt\n{attempt}\n\n"
            f"## 4. Tomorrow's Restart Point\n{summary}"
        ).strip()

    def _compile_essay_draft(self) -> str:
        task = self.artifact.get("task") or self.workspace.get("task") or "Essay"
        brain_dump = self.sections.get("brain_dump") or self.sections.get("first_concept") or ""
        outline = self.sections.get("outline") or self.sections.get("recall_prompt") or ""
        thesis = self.sections.get("thesis") or ""
        body = self.sections.get("body_paragraphs") or self.sections.get("recall_attempt") or ""
        revision = self.sections.get("revision") or self.sections.get("summary") or ""
        draft_parts = []
        if thesis:
            draft_parts.append(f"## Thesis\n{thesis}")
        if outline:
            draft_parts.append(f"## Outline\n{outline}")
        if body:
            draft_parts.append(f"## Draft Paragraphs\n{body}")
        if revision:
            draft_parts.append(f"## Revision Notes\n{revision}")
        if not draft_parts and brain_dump:
            draft_parts.append(f"## Brain Dump\n{brain_dump}")
        return f"# Essay Draft: {task}\n\n" + "\n\n".join(draft_parts or ["Start by adding one rough sentence."])

    def _compile_coding_plan(self) -> str:
        task = self.artifact.get("task") or self.workspace.get("task") or "Coding project"
        first = self.sections.get("first_concept") or "Define the smallest visible feature."
        middle = self.sections.get("recall_prompt") or "List the file or component to touch first."
        attempt = self.sections.get("recall_attempt") or "Implement the smallest working slice."
        summary = self.sections.get("summary") or "Write what changed and what remains."
        return (
            f"# Implementation Plan: {task}\n\n"
            f"## Smallest Visible Feature\n{first}\n\n"
            f"## First File / Component\n{middle}\n\n"
            f"## Implementation Slice\n{attempt}\n\n"
            f"## Ship Checklist\n{summary}"
        ).strip()

    def _compile_generic_sections(self) -> str:
        lines = []
        for key, value in self.sections.items():
            if not value:
                continue
            pretty = key.replace("_", " ").title()
            lines.append(f"## {pretty}\n{value}")
        return "\n\n".join(lines).strip()

    def export_payload(self) -> Dict[str, Any]:
        return {
            "type": self.artifact.get("type", "document"),
            "category": self.artifact.get("category"),
            "task": self.artifact.get("task"),
            "frame": self.artifact.get("frame"),
            "final_output": self.artifact.get("final_output", ""),
            "sections": self.sections,
            "updated_at": self.artifact.get("updated_at", now()),
        }
