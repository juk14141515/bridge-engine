"""Multimodal pathway selector.

Allows multiple interactive paths for the SAME learning target.
"""

from __future__ import annotations

from typing import Dict, List


class MultimodalPathwaySelector:
    def select_paths(
        self,
        learning_target: str,
        profile: Dict,
    ) -> Dict:
        preferences = profile.get("learning_preferences", [])
        interests = profile.get("interests", [])

        pathways = ["textual"]

        if "visual" in preferences:
            pathways += ["diagrammatic", "whiteboard"]

        if "audio" in preferences:
            pathways += ["voice", "conversation"]

        if "gaming" in interests:
            pathways += ["quests", "challenge_ladders"]

        pathways += [
            "simulation",
            "teach_back",
            "active_recall",
        ]

        return {
            "learning_target": learning_target,
            "pathways": sorted(set(pathways)),
            "adaptive_switching": True,
        }
