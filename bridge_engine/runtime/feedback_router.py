class FeedbackRouter:
    def apply_feedback(self, runtime_state, feedback: str):
        runtime_state.add_feedback(feedback)

        if feedback == "too_much":
            runtime_state.next_best_action = "Reduce scope and complete a 5-minute version"
            runtime_state.momentum_score *= 0.9

        elif feedback == "faster":
            runtime_state.next_best_action = "Skip explanation and continue execution"
            runtime_state.momentum_score *= 1.1

        elif feedback == "more_visual":
            runtime_state.next_best_action = "Switch to visual walkthrough mode"

        elif feedback == "helpful":
            runtime_state.next_best_action = "Continue current execution path"
            runtime_state.momentum_score *= 1.05

        else:
            runtime_state.next_best_action = "Regenerate simplified next step"

        return runtime_state
