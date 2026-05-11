from flask import Blueprint, jsonify, request

from bridge_core.completion_engine import BridgeCompletionEngine
from bridge_core.rewrite_engine import RewriteEngine
from bridge_core.artifact_engine import ArtifactEngine
from bridge_core.progression_engine import ProgressionEngine
from bridge_core.session_intelligence import SessionIntelligence
from bridge_core.memory_engine import MemoryEngine
from bridge_core.sql_store import BridgeSqlStore

runtime_api = Blueprint('runtime_api', __name__, url_prefix='/api')

store = BridgeSqlStore()
completion_engine = BridgeCompletionEngine()
rewrite_engine = RewriteEngine()
artifact_engine = ArtifactEngine()
progression_engine = ProgressionEngine()
session_intelligence = SessionIntelligence()
memory_engine = MemoryEngine()


def ok(payload, status=200):
    return jsonify({'ok': True, **payload}), status


def fail(message, status=400):
    return jsonify({'ok': False, 'error': message}), status


def normalize_session(payload):
    session = payload.get('session') or payload
    if not isinstance(session, dict):
        return {}
    return session


@runtime_api.post('/session/create')
def api_session_create():
    data = request.get_json(silent=True) or {}
    task = (data.get('task') or data.get('learning_goal') or '').strip()
    if not task:
        return fail('task is required')

    session = completion_engine.create_session(
        task=task,
        frame=data.get('frame') or data.get('interest_frame') or 'gaming',
        supports=data.get('supports') or ['step_by_step'],
        user_words=data.get('user_words') or data.get('own_words') or '',
        category=data.get('category') or 'general',
    )
    payload = session.to_dict()
    payload['runtime_state'] = {
        'mode': 'guided_completion',
        'status': payload.get('status', 'active'),
        'rewrite_count': 0,
        'friction_level': 'normal',
        'current_step_index': payload.get('current_step_index', 0),
    }
    payload['intelligence'] = session_intelligence.analyze(payload)
    payload['next_prompt'] = progression_engine.next_step(payload)
    payload['memory_summary'] = memory_engine.summarize_session(payload)
    payload['artifact_preview'] = build_artifact_preview(payload)
    store.save_workspace(payload)
    return ok({'session': payload})


@runtime_api.post('/session/continue')
def api_session_continue():
    data = request.get_json(silent=True) or {}
    session = normalize_session(data)
    if not session:
        workspace_id = data.get('workspace_id') or data.get('session_id')
        session = store.get_workspace(workspace_id) if workspace_id else None
    if not session:
        return fail('session or workspace_id is required')

    output = data.get('output') or data.get('user_output') or ''
    session = advance_session_dict(session, output)
    session['intelligence'] = session_intelligence.analyze(session)
    session['next_prompt'] = progression_engine.next_step(session, output)
    session['memory_summary'] = memory_engine.summarize_session(session)
    session['artifact_preview'] = build_artifact_preview(session)
    store.save_workspace(session)
    return ok({'session': session})


@runtime_api.post('/session/rewrite')
def api_session_rewrite():
    data = request.get_json(silent=True) or {}
    text = data.get('text') or data.get('prompt') or ''
    mode = data.get('mode') or 'make_easier'
    frame = data.get('frame') or 'gaming'

    if mode == 'break_smaller':
        rewritten = rewrite_engine.break_smaller(text)
    elif mode == 'explain_differently':
        rewritten = rewrite_engine.explain_differently(text, frame)
    elif mode == 'give_example':
        rewritten = rewrite_engine.give_example(data.get('task_type') or 'essay')
    else:
        rewritten = rewrite_engine.make_easier(text)

    return ok({'rewrite': rewritten, 'mode': mode})


@runtime_api.post('/session/export')
def api_session_export():
    data = request.get_json(silent=True) or {}
    session = normalize_session(data)
    if not session:
        workspace_id = data.get('workspace_id') or data.get('session_id')
        session = store.get_workspace(workspace_id) if workspace_id else None
    if not session:
        return fail('session or workspace_id is required')

    title = session.get('task') or session.get('title') or 'Bridge Export'
    content = export_session_text(session)
    exported = artifact_engine.export_markdown(title, content)
    return ok({'format': 'markdown', 'content': exported})


@runtime_api.get('/workspace/<workspace_id>')
def api_workspace_get(workspace_id):
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return fail('workspace not found', 404)
    return ok({'workspace': workspace})


@runtime_api.get('/workspaces/recent')
def api_workspaces_recent():
    limit = int(request.args.get('limit', 20))
    return ok({'workspaces': store.list_workspaces(limit=limit)})


@runtime_api.post('/workspace/save')
def api_workspace_save():
    data = request.get_json(silent=True) or {}
    workspace = data.get('workspace') or data.get('session') or data
    if not isinstance(workspace, dict) or not workspace.get('id'):
        return fail('workspace with id is required')
    store.save_workspace(workspace)
    return ok({'workspace': workspace})


def advance_session_dict(session, output):
    steps = session.get('steps', [])
    idx = int(session.get('current_step_index', 0) or 0)
    if idx < len(steps):
        steps[idx]['status'] = 'done'
        steps[idx]['user_output'] = output
        steps[idx]['answer'] = output
        if idx + 1 < len(steps):
            steps[idx + 1]['status'] = 'active'
        session['current_step_index'] = idx + 1
    if session.get('current_step_index', 0) >= len(steps):
        session['status'] = 'complete'
    else:
        session['status'] = 'active'
    session['steps'] = steps
    session.setdefault('events', []).append({'kind': 'continued', 'step_index': idx})
    return session


def build_artifact_preview(session):
    task = (session.get('task') or session.get('title') or '').lower()
    if any(word in task for word in ['essay', 'paper', 'writing', 'paragraph']):
        return artifact_engine.build_essay_outline(session)
    if any(word in task for word in ['study', 'quiz', 'learn']):
        return artifact_engine.build_flashcards(session.get('task', 'Study'), ['core concept', 'example', 'definition'])
    if any(word in task for word in ['code', 'app', 'website', 'python']):
        return artifact_engine.build_code_scaffold(session.get('task', 'Bridge Project'))
    return {'type': 'general', 'message': 'Keep building the workspace artifact.'}


def export_session_text(session):
    lines = []
    for step in session.get('steps', []):
        lines.append(f"## {step.get('title', 'Step')}")
        lines.append(step.get('user_output') or step.get('answer') or step.get('checkpoint') or '')
        lines.append('')
    return '\n'.join(lines).strip()


def register_runtime_api(app):
    app.register_blueprint(runtime_api)
    return app
