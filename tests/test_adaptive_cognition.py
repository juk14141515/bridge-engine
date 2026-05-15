from bridge_core.adaptive_cognition_runtime import apply_adaptive_cognition
from bridge_core.friction_detection import detect_friction
from bridge_core.interaction_rotation import select_interaction
from bridge_core.runtime_memory import build_runtime_profile, update_runtime_memory


def _workspace():
    return {
        'id': 'ws-test',
        'task': 'Write an essay about videogames',
        'category': 'essay',
        'frame': 'gaming',
        'supports': ['step_by_step'],
        'current_step_index': 1,
        'steps': [
            {'id': 's1', 'title': 'Bridge', 'status': 'done'},
            {'id': 's2', 'title': 'Draft', 'status': 'active'},
        ],
        'runtime_state': {},
    }


def test_memory_tracks_rewrites_and_builds_profile():
    ws = _workspace()
    update_runtime_memory(ws, {'type': 'continue', 'user_output': 'ok'})
    update_runtime_memory(ws, {'type': 'rewrite', 'successful': True})
    profile = build_runtime_profile(ws)
    assert profile['preferred_complexity'] in {'low', 'medium', 'high'}
    assert ws['runtime_memory']['rewrite_count'] == 1


def test_friction_detects_short_responses():
    ws = _workspace()
    state = detect_friction(ws, 'idk')
    assert state['friction_level'] >= 0.55
    assert state['intervention_strategy']


def test_interaction_rotation_avoids_immediate_repeat():
    ws = _workspace()
    update_runtime_memory(ws, {'type': 'interaction_record', 'interaction_type': 'writing'})
    first = select_interaction(ws, build_runtime_profile(ws), {'mode': 'balanced'})
    second = select_interaction(ws, build_runtime_profile(ws), {'mode': 'balanced'})
    assert first['current'] != second['current'] or first['current'] == 'writing'


def test_apply_adaptive_cognition_expands_frontend_layers():
    ws = _workspace()
    cognition = apply_adaptive_cognition(ws, event={'type': 'continue', 'user_output': 'A full sentence answer.'})
    assert cognition['immersion_state'].get('narrative_thread')
    assert cognition['friction_state'].get('friction_level') is not None
    assert cognition['momentum_state'].get('pace_modifier')
    assert cognition['interaction_rotation'].get('current')
    assert cognition['reward_state'].get('message')
