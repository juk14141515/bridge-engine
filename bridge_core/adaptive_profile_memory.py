from __future__ import annotations

from typing import Any, Dict


class AdaptiveProfileMemory:
    def __init__(self, profile: Dict[str, Any] | None = None):
        self.profile = profile or {}

    def update(self, event: Dict[str, Any]) -> Dict[str, Any]:
        prefs = self.profile.setdefault('preferences', {})
        frame = event.get('frame')
        if frame:
            prefs['preferred_frame'] = frame

        if event.get('rewrite_mode') == 'break_smaller':
            prefs['needs_small_steps'] = True

        return self.profile
