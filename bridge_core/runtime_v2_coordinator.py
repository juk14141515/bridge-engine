from __future__ import annotations

from typing import Any, Dict

from bridge_core.adaptive_profile_memory import AdaptiveProfileMemory
from bridge_core.completion_engine_v2 import CompletionEngineV2
from bridge_core.evaluation_engine import EvaluationEngine
from bridge_core.export_compiler import ExportCompiler
from bridge_core.friction_engine import FrictionEngine
from bridge_core.motivation_runtime import MotivationRuntime
from bridge_core.realtime_sync import RealtimeSync
from bridge_core.rewrite_progression_engine import RewriteProgressionEngine
from bridge_core.runtime_persistence import save_session
from bridge_core.runtime_schema import ensure_workspace
from bridge_core.task_decomposition import TaskDecomposer
from bridge_core.vector_memory import VectorMemory
from bridge_core.workspace_intelligence import WorkspaceIntelligence


class RuntimeV2Coordinator:
    def __init__(self, workspace: Dict[str, Any]):
        self.workspace = ensure_workspace(workspace)
        self.memory = AdaptiveProfileMemory(self.workspace.get("profile"))
        self.vector_memory = VectorMemory()

    def continue_session(self, output: str) -> Dict[str, Any]:
        engine = CompletionEngineV2(self.workspace)
        envelope = engine.continue_with_output(output)

        evaluation = EvaluationEngine().score_output(output)
        friction = FrictionEngine().detect(output)
        motivation = MotivationRuntime().build_status(
            envelope.get("progress", {}).get("done", 0)
        )

        self.memory.update({
            "frame": self.workspace.get("frame"),
        })

        self.vector_memory.store(output, self.workspace.get("category", "general"))

        decomposition = TaskDecomposer().decompose(self.workspace.get("task", ""))
        sync_payload = RealtimeSync().payload(self.workspace)
        workspace_summary = WorkspaceIntelligence(self.workspace).summary()

        envelope["evaluation"] = evaluation
        envelope["friction"] = friction
        envelope["motivation"] = motivation
        envelope["task_decomposition"] = decomposition
        envelope["sync"] = sync_payload
        envelope["workspace_summary"] = workspace_summary
        envelope["profile"] = self.memory.profile

        save_session(engine.workspace)
        return envelope

    def export(self, export_format: str = "markdown") -> Dict[str, Any]:
        artifact = self.workspace.get("artifact", {})
        return ExportCompiler(artifact).compile(export_format)

    def rewrite_score(self, mode: str, before_prompt: str, after_prompt: str) -> Dict[str, Any]:
        return RewriteProgressionEngine().score(mode, before_prompt, after_prompt)
