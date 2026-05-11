def runtime_response(session, intelligence=None, next_prompt=None, artifact_preview=None):
    return {
        'session': session,
        'runtime_state': {
            'status': session.get('status', 'active'),
            'current_step_index': session.get('current_step_index', 0),
            'completion_rate': intelligence.get('completion_rate', 0) if intelligence else 0,
            'momentum_state': intelligence.get('state', 'starting') if intelligence else 'starting',
        },
        'intelligence': intelligence or {},
        'next_prompt': next_prompt or {},
        'artifact_preview': artifact_preview or {},
        'rewrite_options': [
            'make_easier',
            'break_smaller',
            'give_example',
            'explain_differently'
        ]
    }
