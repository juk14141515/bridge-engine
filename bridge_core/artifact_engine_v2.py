"""Artifact engine V2.

Responsible for continuously building the user's final output while they work.
Every completed step updates a living artifact.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


def now() -> str:
    return datetime.utcnow().isoformat()


class ArtifactEngine:
    def __init__(self, workspace: Dict[str, Any]):
        self.workspace = workspace
        self.artifact = workspace.get("artifact") or {}
        self.sections = self.artifact.setdefault("sections", {})

    def apply_step_output(self, step: Dict[str, Any], output: str) -> Dict[str, Any]:
        slot = str(step.get("output_slot") or step.get("id") or "notes")
        current = str(self.sections.get(slot) or "")

        merged = output.strip() if not current else f"{current}\n\n{output.strip()}"
        self.sections[slot] = merged

        self.artifact["updated_at"] = now()
        self.artifact["final_output"] = self.compile_preview()
        return self.artifact

    def compile_preview(self) -> str:
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
