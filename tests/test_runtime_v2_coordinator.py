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
