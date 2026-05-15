"""Interaction mode registry.

Defines reusable interaction systems for many runtime situations.
"""

from __future__ import annotations

from typing import Dict


INTERACTION_MODES = {
    "rapid_recall": {
        "type": "memory_loop",
        "description": "Fast active recall rounds",
    },
    "conversation_simulation": {
        "type": "simulation",
        "description": "Interactive roleplay conversation",
    },
    "debug_missions": {
        "type": "challenge",
        "description": "Solve bugs to unlock progression",
    },
    "argument_battles": {
        "type": "logic_game",
        "description": "Strengthen arguments through challenge rounds",
    },
    "knowledge_duels": {
        "type": "quiz_battle",
        "description": "Rapid-fire understanding checks",
    },
    "quests": {
        "type": "progression_system",
        "description": "Task progression through quest chains",
    },
    "boss_battles": {
        "type": "milestone_event",
        "description": "Large completion milestone",
    },
    "micro_wins": {
        "type": "motivation",
        "description": "Tiny instant-success loops",
    },
    "teach_back": {
        "type": "understanding_check",
        "description": "Explain concept back in own words",
    },
}


class InteractionModeRegistry:
    def get(self, mode: str) -> Dict:
        return INTERACTION_MODES.get(mode, {})
