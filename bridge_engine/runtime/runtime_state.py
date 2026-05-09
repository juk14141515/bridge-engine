from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict


@dataclass
class RuntimeState:
    lane_id: str
    user_goal: str
    interest_frame: str
    cognitive_mode: str
    task_type: str
    current_status: str = "created"
    progress: float = 0.0
    momentum_score: float = 0.5
    active_step_index: int = 0
    next_best_action: str = ""
    resume_point: str = ""
    feedback_history: List[Dict] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def update_status(self, status: str):
        self.current_status = status
        self.updated_at = datetime.utcnow().isoformat()

    def add_feedback(self, feedback: str):
        self.feedback_history.append({
            "feedback": feedback,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self.updated_at = datetime.utcnow().isoformat()
