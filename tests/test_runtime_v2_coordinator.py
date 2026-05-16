from bridge_core.runtime_v2_coordinator import RuntimeV2Coordinator


def test_runtime_v2_continue_flow():
    workspace = {
        'id': 'demo',
        'task': 'Learn Spanish through music',
        'category': 'language_learning',
        'frame': 'music',
        'steps': [
            {
                'id': 's1',
                'title': 'First phrase',
                'prompt': 'Write one phrase',
                'status': 'active',
            }
        ],
        'artifact': {
            'sections': {}
        }
    }

    result = RuntimeV2Coordinator(workspace).continue_session('Hola amigo')

    assert result['progress']['done'] >= 1
    assert result['evaluation']['completion_score'] >= 1
    assert result['motivation']['state'] in ['starting', 'momentum', 'deep_flow']


def test_runtime_v2_rejects_weak_continue_without_advancing():
    workspace = {
        'id': 'essay-demo',
        'task': 'Write an essay about attention',
        'category': 'essay_writing',
        'frame': 'gaming',
        'current_step_index': 0,
        'steps': [
            {
                'id': 's1',
                'title': 'Open the map',
                'prompt': 'Write one concrete sentence about the essay.',
                'status': 'active',
                'output_slot': 'brain_dump',
            }
        ],
        'artifact': {
            'sections': {}
        }
    }

    result = RuntimeV2Coordinator(workspace).continue_session('starting the essay')

    assert result['workspace']['current_step_index'] == 0
    assert result['progress']['done'] == 0
    assert result['workspace']['artifact']['sections'] == {}
    assert result['verification']['verified'] is False
    assert result['verification']['confidence_score'] < 50
    assert result['verification']['flags']


def test_runtime_export():
    workspace = {
        'task': 'Essay draft',
        'artifact': {
            'final_output': 'Hello world',
            'sections': {
                'intro': 'Test intro'
            }
        }
    }

    payload = RuntimeV2Coordinator(workspace).export('markdown')
    assert payload['format'] == 'markdown'
