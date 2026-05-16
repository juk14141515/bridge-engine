from __future__ import annotations

from typing import Any, Dict

from bridge_core.adaptive_profile_memory import AdaptiveProfileMemory
from bridge_core.adaptive_step_engine import next_adaptive_move
from bridge_core.completion_engine_v2 import CompletionEngineV2
from bridge_core.completion_gate_engine import CompletionGateEngine
from bridge_core.evaluation_engine import EvaluationEngine
from bridge_core.export_compiler import ExportCompiler
from bridge_core.friction_engine import FrictionEngine
from bridge_core.motivation_runtime import MotivationRuntime
from bridge_core.realtime_sync import RealtimeSync
from bridge_core.rewrite_progression_engine import RewriteProgressionEngine
from bridge_core.runtime_persistence import save_session
from bridge_core.runtime_schema import build_envelope, ensure_workspace, runtime_event, utc_now
from bridge_core.task_decomposition import TaskDecomposer
from bridge_core.verification_engine import VerificationEngine
from bridge_core.vector_memory import VectorMemory
from bridge_core.workspace_intelligence import WorkspaceIntelligence


class RuntimeV2Coordinator:
    def __init__(self, workspace: Dict[str, Any]):
        self.workspace = ensure_workspace(workspace)
        self.memory = AdaptiveProfileMemory(self.workspace.get("profile"))
        self.vector_memory = VectorMemory()

    def continue_session(self, output: str) -> Dict[str, Any]:
        verification = VerificationEngine().verify_progress(self.workspace, output)
        gate = CompletionGateEngine().evaluate(verification)
        if not gate.get("advance"):
            envelope = self._checkpoint_envelope(output, verification, gate)
            save_session(self.workspace)
            return envelope

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

        envelope["verification"] = verification
        envelope["gate"] = gate
        envelope["evaluation"] = evaluation
        envelope["friction"] = friction
        envelope["motivation"] = motivation
        envelope["task_decomposition"] = decomposition
        envelope["sync"] = sync_payload
        envelope["workspace_summary"] = workspace_summary
        envelope["profile"] = self.memory.profile

        save_session(engine.workspace)
        return envelope

    def _checkpoint_envelope(
        self,
        output: str,
        verification: Dict[str, Any],
        gate: Dict[str, Any],
    ) -> Dict[str, Any]:
        current_index = int(self.workspace.get("current_step_index", 0) or 0)
        steps = self.workspace.get("steps") or []
        if 0 <= current_index < len(steps):
            steps[current_index]["status"] = "active"
            steps[current_index]["last_unverified_output"] = (output or "").strip()

        runtime_state = self.workspace.setdefault("runtime_state", {})
        runtime_state["last_verification"] = verification
        runtime_state["verification_blocked"] = True
        runtime_state["updated_at"] = utc_now()
        self.workspace["updated_at"] = utc_now()
        self.workspace.setdefault("events", []).append(
            runtime_event(
                "verification_checkpoint",
                {
                    "step_index": current_index,
                    "flags": verification.get("flags", []),
                    "confidence_score": verification.get("confidence_score", 0),
                },
            )
        )

        adaptive = next_adaptive_move(self.workspace, output)
        adaptive["message"] = verification.get("message")
        adaptive["prompt"] = verification.get("message")
        intelligence = WorkspaceIntelligence(self.workspace).summary()
        intelligence["adaptive_move"] = adaptive
        envelope = build_envelope(
            self.workspace,
            intelligence=intelligence,
            next_prompt=adaptive,
            artifact_preview=self.workspace.get("artifact", {}),
        )
        envelope["verification"] = verification
        envelope["gate"] = gate
        envelope["evaluation"] = EvaluationEngine().score_output(output)
        envelope["friction"] = FrictionEngine().detect(output)
        envelope["motivation"] = MotivationRuntime().build_status(envelope.get("progress", {}).get("done", 0))
        envelope["task_decomposition"] = TaskDecomposer().decompose(self.workspace.get("task", ""))
        envelope["sync"] = RealtimeSync().payload(self.workspace)
        envelope["workspace_summary"] = intelligence
        envelope["profile"] = self.memory.profile
        return envelope

    def export(self, export_format: str = "markdown") -> Dict[str, Any]:
        artifact = self.workspace.get("artifact", {})
        return ExportCompiler(artifact).compile(export_format)

    def rewrite_score(self, mode: str, before_prompt: str, after_prompt: str) -> Dict[str, Any]:
        return RewriteProgressionEngine().score(mode, before_prompt, after_prompt)
