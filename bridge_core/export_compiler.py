"""Export compiler for Bridge Engine.

Converts live artifacts into export-safe payloads for copy, markdown, txt,
and future PDF/docx compilation.
"""

from __future__ import annotations

from typing import Any, Dict


EXPORT_FORMATS = [
    "plain_text",
    "markdown",
    "json",
]


class ExportCompiler:
    def __init__(self, artifact: Dict[str, Any]):
        self.artifact = artifact

    def compile(self, export_format: str = "markdown") -> Dict[str, Any]:
        export_format = export_format if export_format in EXPORT_FORMATS else "markdown"

        final_output = str(self.artifact.get("final_output") or "")
        sections = self.artifact.get("sections") or {}

        if export_format == "plain_text":
            content = self._plain_text(final_output)
        elif export_format == "json":
            content = {
                "artifact": self.artifact,
                "sections": sections,
            }
        else:
            content = self._markdown(sections, final_output)

        return {
            "format": export_format,
            "content": content,
            "filename": self._filename(export_format),
        }

    def _markdown(self, sections: Dict[str, Any], fallback: str) -> str:
        if not sections:
            return fallback
        blocks = []
        for key, value in sections.items():
            title = key.replace("_", " ").title()
            blocks.append(f"# {title}\n\n{value}")
        return "\n\n".join(blocks).strip()

    def _plain_text(self, text: str) -> str:
        return text.replace("#", "").strip()

    def _filename(self, export_format: str) -> str:
        task = str(self.artifact.get("task") or "bridge_output")
        safe = "_".join(task.lower().split())[:48]
        ext = {
            "markdown": "md",
            "plain_text": "txt",
            "json": "json",
        }.get(export_format, "txt")
        return f"{safe}.{ext}"
