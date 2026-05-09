from enum import Enum


class RuntimeStatus(str, Enum):
    CREATED = "created"
    UNDERSTOOD = "understood"
    PLANNED = "planned"
    ACTIVE_STEP = "active_step"
    PROOF_SUBMITTED = "proof_submitted"
    CONTINUED = "continued"
    COMPLETED = "completed"
    EXPORTED = "exported"


VALID_TRANSITIONS = {
    RuntimeStatus.CREATED: [RuntimeStatus.UNDERSTOOD],
    RuntimeStatus.UNDERSTOOD: [RuntimeStatus.PLANNED],
    RuntimeStatus.PLANNED: [RuntimeStatus.ACTIVE_STEP],
    RuntimeStatus.ACTIVE_STEP: [RuntimeStatus.PROOF_SUBMITTED, RuntimeStatus.CONTINUED],
    RuntimeStatus.PROOF_SUBMITTED: [RuntimeStatus.CONTINUED, RuntimeStatus.COMPLETED],
    RuntimeStatus.CONTINUED: [RuntimeStatus.ACTIVE_STEP, RuntimeStatus.COMPLETED],
    RuntimeStatus.COMPLETED: [RuntimeStatus.EXPORTED],
    RuntimeStatus.EXPORTED: [],
}


class RuntimeStateMachine:
    def can_transition(self, current_status: str, next_status: str) -> bool:
        current = RuntimeStatus(current_status)
        target = RuntimeStatus(next_status)
        return target in VALID_TRANSITIONS[current]

    def transition(self, runtime_state: dict, next_status: str) -> dict:
        current_status = runtime_state.get("status", RuntimeStatus.CREATED.value)

        if not self.can_transition(current_status, next_status):
            runtime_state["transition_warning"] = f"Invalid transition: {current_status} -> {next_status}"
            return runtime_state

        runtime_state["status"] = next_status
        runtime_state.setdefault("state_history", []).append(next_status)
        return runtime_state
