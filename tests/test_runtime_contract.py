from bridge_core.task_registry import detect_task_type
from bridge_core.task_decomposition import TaskDecomposer


def test_language_detection():
    assert detect_task_type('I want to learn Spanish') == 'language_learning'


def test_task_decomposition():
    payload = TaskDecomposer().decompose('Write my psychology paper')
    assert len(payload['micro_steps']) >= 1
