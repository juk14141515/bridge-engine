class FeedbackRuntimeAdapter:
    def apply_feedback(self, runtime_state: dict, feedback_type: str):
        runtime_state.setdefault('feedback_history', []).append(feedback_type)

        if feedback_type == 'too_much':
            runtime_state['recommended_mode'] = 'smaller_steps'
            runtime_state['momentum_score'] = max(0, runtime_state.get('momentum_score', 50) - 10)

        elif feedback_type == 'faster':
            runtime_state['recommended_mode'] = 'accelerated'
            runtime_state['momentum_score'] = min(100, runtime_state.get('momentum_score', 50) + 8)

        elif feedback_type == 'more_visual':
            runtime_state['interaction_preference'] = 'visual'

        elif feedback_type == 'helpful':
            runtime_state['progress_confidence'] = min(100, runtime_state.get('progress_confidence', 50) + 10)

        else:
            runtime_state['recommended_mode'] = 'adaptive'

        return runtime_state
