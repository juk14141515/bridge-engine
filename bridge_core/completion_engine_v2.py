"""Completion Engine V2 orchestration layer.

This is the artifact-first runtime engine. It wraps an existing workspace/session,
normalizes it, applies user output to the living artifact, and returns a stable
frontend-safe envelope.
"""

from __future__ import annotations

from typing import Any, Dict

from bridge_core.adaptive_step_engine import next_adaptive_move
from bridge_core.artifact_engine_v2 import ArtifactEngine
from bridge_core.runtime_schema import build_envelope, ensure_workspace, utc_now
from bridge_core.workspace_intelligence import WorkspaceIntelligence


class CompletionEngineV2:
    def __init__(self, workspace: Dict[str, Any]):
        self.workspace = ensure_workspace(workspace)

    def continue_with_output(self, user_output: str) -> Dict[str, Any]:
        output = (user_output or '').strip()
        steps = self.workspace.get('steps') or []
        idx = int(self.workspace.get('current_step_index', 0) or 0)

        if idx < len(steps):
            step = steps[idx]
            step['status'] = 'done'
            step['user_output'] = output
            step['completed_at'] = utc_now()
            self.workspace['artifact'] = ArtifactEngine(self.workspace).apply_step_output(step, output)
            self.workspace['current_step_index'] = idx + 1

        if self.workspace['current_step_index'] >= len(steps):
            self.workspace['status'] = 'complete'
        elif steps:
            steps[self.workspace['current_step_index']]['status'] = 'active'

        self.workspace['updated_at'] = utc_now()
        adaptive = next_adaptive_move(self.workspace, output)
        intelligence = WorkspaceIntelligence(self.workspace).summary()
        intelligence['adaptive_move'] = adaptive

        return build_envelope(
            self.workspace,
            intelligence=intelligence,
            next_prompt=adaptive,
            artifact_preview=self.workspace.get('artifact', {}),
        )

    def envelope(self) -> Dict[str, Any]:
        return build_envelope(
            self.workspace,
            intelligence=WorkspaceIntelligence(self.workspace).summary(),
            artifact_preview=self.workspace.get('artifact', {}),
        )
