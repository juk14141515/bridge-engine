def export_runtime(runtime_state):
    return {
        'title': runtime_state.get('title'),
        'status': runtime_state.get('status'),
        'steps': runtime_state.get('steps', []),
        'momentum_score': runtime_state.get('momentum_score', 50),
    }
