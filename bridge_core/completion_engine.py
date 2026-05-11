"""Adaptive completion engine for Bridge Engine.

This module is intentionally dependency-light so it can be used by Flask routes,
CLI scripts, tests, or future SQL-backed workers. It turns a task + interest
frame + support needs into a guided completion session that can continue until
the user has a usable finished output.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid


SUPPORTED_FRAMES: Dict[str, Dict[str, str]] = {
    "gaming": {
        "unit": "quest",
        "progress": "XP",
        "final": "boss fight",
        "tone": "clear, quest-like, reward-driven",
    },
    "fitness": {
        "unit": "rep",
        "progress": "sets",
        "final": "cooldown review",
        "tone": "warmup, reps, sets, cooldown",
    },
    "investing": {
        "unit": "thesis checkpoint",
        "progress": "conviction",
        "final": "decision memo",
        "tone": "thesis, evidence, risk, decision",
    },
    "coding": {
        "unit": "ship slice",
        "progress": "commits",
        "final": "working demo",
        "tone": "debug loops, small commits, ship useful increments",
    },
    "music": {
        "unit": "measure",
        "progress": "layers",
        "final": "performance pass",
        "tone": "rhythm, layers, repeatable practice",
    },
    "creative": {
        "unit": "draft pass",
        "progress": "versions",
        "final": "final cut",
        "tone": "messy first draft, shape, polish",
    },
    "relationship": {
        "unit": "clarity prompt",
        "progress": "care points",
        "final": "conversation draft",
        "tone": "careful, emotionally safe, clear boundaries",
    },
    "systems": {
        "unit": "lever",
        "progress": "feedback loops",
        "final": "operating loop",
        "tone": "inputs, outputs, bottlenecks, feedback",
    },
}

SUPPORT_MODIFIERS: Dict[str, Dict[str, Any]] = {
    "adhd": {
        "max_words": 70,
        "rule": "Use one obvious next action, fewer choices, and visible progress.",
    },
    "dyslexia": {
        "max_words": 60,
        "rule": "Use short lines, simple wording, bullets, and generous spacing.",
    },
    "anxiety": {
        "max_words": 80,
        "rule": "Lower pressure, avoid shame, make imperfect work acceptable.",
    },
    "low_energy": {
        "max_words": 55,
        "rule": "Make the action tiny enough to start while tired.",
    },
    "visual_first": {
        "max_words": 75,
        "rule": "Start with a visual map, boxes, labels, or spatial structure.",
    },
    "examples_first": {
        "max_words": 90,
        "rule": "Show an example before asking the user to produce their own.",
    },
    "step_by_step": {
        "max_words": 85,
        "rule": "Number actions and keep the sequence linear.",
    },
    "professional": {
        "max_words": 90,
        "rule": "Use concise, direct language. Skip motivational softening. Frame each step as a decision or deliverable.",
    },
}


@dataclass
class BridgeStep:
    id: str
    title: str
    prompt: str
    why: str
    action: str
    output_slot: str
    status: str = "pending"
    user_output: str = ""
    help_variants: Dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BridgeSession:
    id: str
    task: str
    frame: str
    supports: List[str]
    user_words: str = ""
    category: str = "general"
    status: str = "active"
    current_step_index: int = 0
    steps: List[BridgeStep] = field(default_factory=list)
    artifact: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["steps"] = [step.to_dict() for step in self.steps]
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BridgeSession":
        steps_in: List[Dict[str, Any]] = data.get("steps") or []
        steps: List[BridgeStep] = []
        for s in steps_in:
            hv = s.get("help_variants")
            if not isinstance(hv, dict):
                hv = {}
            steps.append(
                BridgeStep(
                    id=str(s.get("id", "")),
                    title=str(s.get("title", "")),
                    prompt=str(s.get("prompt", "")),
                    why=str(s.get("why", "")),
                    action=str(s.get("action", "")),
                    output_slot=str(s.get("output_slot", "")),
                    status=str(s.get("status", "pending")),
                    user_output=str(s.get("user_output", "") or s.get("answer", "")),
                    help_variants=hv,
                    created_at=str(s.get("created_at") or datetime.utcnow().isoformat()),
                    completed_at=s.get("completed_at"),
                )
            )
        return cls(
            id=str(data["id"]),
            task=str(data.get("task", "")),
            frame=str(data.get("frame", "gaming")),
            supports=list(data.get("supports") or []),
            user_words=str(data.get("user_words", "")),
            category=str(data.get("category", "general")),
            status=str(data.get("status", "active")),
            current_step_index=int(data.get("current_step_index", 0) or 0),
            steps=steps,
            artifact=dict(data.get("artifact") or {}),
            events=list(data.get("events") or []),
            created_at=str(data.get("created_at") or datetime.utcnow().isoformat()),
            updated_at=str(data.get("updated_at") or datetime.utcnow().isoformat()),
        )


class BridgeCompletionEngine:
    """Creates and advances interest-translated completion sessions."""

    def create_session(
        self,
        task: str,
        frame: str = "gaming",
        supports: Optional[List[str]] = None,
        user_words: str = "",
        category: str = "general",
    ) -> BridgeSession:
        supports = supports or ["step_by_step"]
        normalized_frame = self.normalize_frame(frame)
        session = BridgeSession(
            id=self._new_id(),
            task=task.strip(),
            frame=normalized_frame,
            supports=supports,
            user_words=user_words.strip(),
            category=category,
        )
        session.steps = self.decompose_task(session)
        session.artifact = self.initial_artifact(session)
        session.events.append(self._event("session_created", {"frame": normalized_frame, "supports": supports}))
        return session

    def advance(self, session: BridgeSession, user_output: str = "") -> BridgeSession:
        if not session.steps:
            session.steps = self.decompose_task(session)
        if session.current_step_index >= len(session.steps):
            session.status = "complete"
            return session

        step = session.steps[session.current_step_index]
        step.status = "done"
        step.user_output = user_output.strip()
        step.completed_at = datetime.utcnow().isoformat()
        session.artifact = self.update_artifact(session, step)
        session.events.append(self._event("step_completed", {"step_id": step.id, "title": step.title}))
        session.current_step_index += 1

        if session.current_step_index >= len(session.steps):
            session.status = "complete"
            session.events.append(self._event("session_completed", {"artifact_sections": list(session.artifact.keys())}))
        else:
            session.steps[session.current_step_index].status = "active"

        session.updated_at = datetime.utcnow().isoformat()
        return session

    def rewrite_current_step(self, session: BridgeSession, mode: str) -> Dict[str, Any]:
        current = self.current_step(session)
        if not current:
            return {"message": "No active step."}
        return {
            "mode": mode,
            "step_id": current.id,
            "title": current.title,
            "prompt": self.contextual_rewrite(current, session, mode),
        }

    def current_step(self, session: BridgeSession) -> Optional[BridgeStep]:
        if not session.steps or session.current_step_index >= len(session.steps):
            return None
        step = session.steps[session.current_step_index]
        if step.status == "pending":
            step.status = "active"
        return step

    def decompose_task(self, session: BridgeSession) -> List[BridgeStep]:
        frame = SUPPORTED_FRAMES[self.normalize_frame(session.frame)]
        task_type = self.classify_task(session.task, session.category)
        base = self._task_template(task_type)
        steps: List[BridgeStep] = []
        for idx, item in enumerate(base, start=1):
            title = self._frame_title(item["title"], frame, idx)
            prompt = self._apply_supports(item["prompt"].format(task=session.task, unit=frame["unit"]), session.supports)
            action = item["action"].format(task=session.task, unit=frame["unit"], final=frame["final"])
            why = item["why"].format(task=session.task, progress=frame["progress"])
            steps.append(BridgeStep(
                id=f"s{idx}",
                title=title,
                prompt=prompt,
                why=why,
                action=action,
                output_slot=item["slot"],
                status="active" if idx == 1 else "pending",
                help_variants={
                    "make_easier": self._make_easier(action),
                    "example": item.get("example", "Use a rough placeholder. Perfect comes later."),
                    "explain_differently": self._explain_differently(action, frame),
                    "break_smaller": self._break_smaller(action),
                },
            ))
        return steps

    def contextual_rewrite(self, step: BridgeStep, session: BridgeSession, mode: str) -> str:
        variants = step.help_variants or {}
        if mode in variants:
            return variants[mode]
        if mode == "frame_shift":
            frame = SUPPORTED_FRAMES[self.normalize_frame(session.frame)]
            return f"Think of this as one {frame['unit']}: {step.action}"
        return step.prompt

    def update_artifact(self, session: BridgeSession, step: BridgeStep) -> Dict[str, Any]:
        artifact = dict(session.artifact or {})
        artifact.setdefault("task", session.task)
        artifact.setdefault("frame", session.frame)
        artifact.setdefault("sections", {})
        artifact["sections"][step.output_slot] = step.user_output or f"TODO: {step.action}"
        artifact["updated_at"] = datetime.utcnow().isoformat()
        return artifact

    def initial_artifact(self, session: BridgeSession) -> Dict[str, Any]:
        return {
            "task": session.task,
            "frame": session.frame,
            "supports": session.supports,
            "sections": {},
            "export_formats": ["markdown", "plain_text", "checklist"],
            "created_at": datetime.utcnow().isoformat(),
        }

    def export_markdown(self, session: BridgeSession) -> str:
        lines = [f"# {session.task}", "", f"Frame: {session.frame}", ""]
        for step in session.steps:
            status = "x" if step.status == "done" else " "
            lines.append(f"- [{status}] **{step.title}**")
            if step.user_output:
                lines.append(f"  - Output: {step.user_output}")
        sections = session.artifact.get("sections", {}) if session.artifact else {}
        if sections:
            lines.extend(["", "## Draft / Work Output"])
            for name, value in sections.items():
                lines.extend([f"### {name.replace('_', ' ').title()}", str(value), ""])
        return "\n".join(lines).strip() + "\n"

    def normalize_frame(self, frame: str) -> str:
        key = (frame or "gaming").lower().strip().replace(" ", "_")
        return key if key in SUPPORTED_FRAMES else "gaming"

    def classify_task(self, task: str, category: str = "general") -> str:
        text = f"{task} {category}".lower()
        if any(word in text for word in ["essay", "paper", "paragraph", "writing", "draft"]):
            return "essay"
        if any(word in text for word in ["study", "exam", "quiz", "learn", "chapter"]):
            return "study"
        if any(word in text for word in ["relationship", "conversation", "text", "girlfriend", "boundary"]):
            return "relationship"
        if any(word in text for word in ["clean", "chores", "room", "laundry"]):
            return "chores"
        return "generic"

    def _task_template(self, task_type: str) -> List[Dict[str, str]]:
        templates = {
            "essay": [
                {"title": "Open the map", "prompt": "Write one messy sentence about what {task} is really about.", "action": "Create a rough thesis seed for {task}.", "why": "This turns blank-page pressure into first {progress}.", "slot": "thesis_seed", "example": "Example: This paper is really about how pressure changes people."},
                {"title": "Collect useful gear", "prompt": "List 3 possible points or examples. They can be ugly.", "action": "Create three support points for {task}.", "why": "Support points become the inventory you use later.", "slot": "support_points", "example": "Point 1: cause. Point 2: effect. Point 3: counterargument."},
                {"title": "Build the first room", "prompt": "Turn one point into 3 rough sentences: claim, evidence idea, explanation.", "action": "Draft one body paragraph piece for {task}.", "why": "One paragraph proves the essay can exist.", "slot": "body_paragraph_seed", "example": "Claim: ___. Evidence: ___. This matters because ___."},
                {"title": "Boss fight draft", "prompt": "Combine the thesis seed and paragraph seed into a mini draft outline.", "action": "Create the first complete outline for the {final}.", "why": "The outline becomes a finishable artifact instead of scattered thoughts.", "slot": "draft_outline", "example": "Intro → Point 1 → Point 2 → Point 3 → Conclusion."},
            ],
            "study": [
                {"title": "Spawn point", "prompt": "Write the one thing you need to know first for {task}.", "action": "Pick the smallest concept that unlocks the rest.", "why": "A small start creates {progress} without overload.", "slot": "first_concept"},
                {"title": "Practice round", "prompt": "Make one tiny example or flashcard for that concept.", "action": "Create one recall prompt for {task}.", "why": "Recall beats rereading for learning.", "slot": "recall_prompt"},
                {"title": "Challenge round", "prompt": "Answer your prompt without looking, then fix it.", "action": "Run one active recall rep.", "why": "Mistakes show exactly where to focus next.", "slot": "recall_attempt"},
                {"title": "Level summary", "prompt": "Write a 3-bullet summary in your own words.", "action": "Create a restartable summary for the {final}.", "why": "A short summary makes tomorrow easier.", "slot": "summary"},
            ],
            "relationship": [
                {"title": "Name the signal", "prompt": "Write what you feel and what you need, without blaming anyone.", "action": "Create a clear emotional readout for {task}.", "why": "Clarity lowers pressure before action.", "slot": "feeling_need"},
                {"title": "Draft the safe line", "prompt": "Write one calm sentence you could say or send.", "action": "Create a low-pressure conversation opener.", "why": "One sentence is easier than the whole conversation.", "slot": "opener"},
                {"title": "Prepare the boundary", "prompt": "Write what you are asking for and what you are not asking for.", "action": "Create a boundary/clarity statement.", "why": "Boundaries protect the conversation from spiraling.", "slot": "boundary"},
                {"title": "Final care pass", "prompt": "Rewrite it to sound honest, kind, and direct.", "action": "Create the final message or talking points for the {final}.", "why": "A final pass makes it usable in real life.", "slot": "final_message"},
            ],
            "chores": [
                {"title": "Start tile", "prompt": "Pick one visible object and move it where it belongs.", "action": "Create the first visible win for {task}.", "why": "Visible progress creates {progress} fast.", "slot": "first_win"},
                {"title": "Clear one zone", "prompt": "Choose one tiny zone and reset only that zone.", "action": "Finish one small zone.", "why": "One zone beats trying to clean everything.", "slot": "zone_done"},
                {"title": "Trash/resource sweep", "prompt": "Remove trash or collect supplies for two minutes.", "action": "Reduce friction around {task}.", "why": "Less clutter makes the next action easier.", "slot": "friction_removed"},
                {"title": "Reset checkpoint", "prompt": "Take one quick note or photo of what improved.", "action": "Lock in the progress from the {final}.", "why": "Noticing progress teaches your brain the task was worth starting.", "slot": "completion_note"},
            ],
            "generic": [
                {"title": "Tiny entry", "prompt": "Write the smallest visible version of {task}.", "action": "Create a first checkpoint for {task}.", "why": "Starting creates {progress}; perfection comes later.", "slot": "first_checkpoint"},
                {"title": "Useful middle", "prompt": "Write the next two actions that would move it forward.", "action": "Create the next action pair.", "why": "Two actions are enough to keep going without overwhelm.", "slot": "next_actions"},
                {"title": "Work pass", "prompt": "Do or draft the first action for five minutes.", "action": "Produce one real piece of work.", "why": "A real work piece turns planning into completion.", "slot": "work_piece"},
                {"title": "Finish marker", "prompt": "Decide what counts as done for today.", "action": "Create a completion definition for the {final}.", "why": "A finish marker prevents endless open loops.", "slot": "done_definition"},
            ],
        }
        return templates.get(task_type, templates["generic"])

    def _apply_supports(self, text: str, supports: List[str]) -> str:
        active = [SUPPORT_MODIFIERS[s]["rule"] for s in supports if s in SUPPORT_MODIFIERS]
        if not active:
            return text
        return f"{text}\n\nSupport style: " + " ".join(active)

    def _frame_title(self, base_title: str, frame: Dict[str, str], idx: int) -> str:
        return f"{frame['unit'].title()} {idx}: {base_title}"

    def _make_easier(self, action: str) -> str:
        return f"Do only the first 60 seconds: {action}. Stop after the smallest visible mark."

    def _break_smaller(self, action: str) -> str:
        return f"1) Open the place this belongs. 2) Type one ugly line. 3) Save it. That counts toward: {action}"

    def _explain_differently(self, action: str, frame: Dict[str, str]) -> str:
        return f"Think of it as one {frame['unit']}, not the whole project. Your only job is: {action}"

    def _event(self, kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"id": self._new_id(), "kind": kind, "payload": payload, "created_at": datetime.utcnow().isoformat()}

    def _new_id(self) -> str:
        return uuid.uuid4().hex[:12]
