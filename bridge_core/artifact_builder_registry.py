"""Artifact builder registry.

Every task should generate a real output.
"""

from __future__ import annotations

from typing import Dict


class ArtifactBuilderRegistry:
    def build_artifact(self, category: str, content: str) -> Dict:
        builders = {
            "essay": self._essay_artifact,
            "coding": self._coding_artifact,
            "study": self._study_artifact,
            "fitness": self._fitness_artifact,
            "general": self._general_artifact,
        }

        builder = builders.get(category, self._general_artifact)
        return builder(content)

    def _essay_artifact(self, content: str) -> Dict:
        return {
            "type": "essay_draft",
            "content": content,
        }

    def _coding_artifact(self, content: str) -> Dict:
        return {
            "type": "code_workspace",
            "content": content,
        }

    def _study_artifact(self, content: str) -> Dict:
        return {
            "type": "study_sheet",
            "content": content,
        }

    def _fitness_artifact(self, content: str) -> Dict:
        return {
            "type": "fitness_plan",
            "content": content,
        }

    def _general_artifact(self, content: str) -> Dict:
        return {
            "type": "workspace_output",
            "content": content,
        }
