from datetime import datetime
from uuid import uuid4

from flask import Blueprint, jsonify, request

from bridge_core.completion_engine import BridgeCompletionEngine
from bridge_core.export_compiler import ExportCompiler
from bridge_core.rewrite_engine import RewriteEngine
from bridge_core.runtime_schema import build_envelope, ensure_workspace
from bridge_core.runtime_v2_coordinator import RuntimeV2Coordinator
from bridge_core.sql_store import BridgeSqlStore
from bridge_core.task_registry import detect_task_type

runtime_api = Blueprint('runtime_api', __name__, url_prefix='/api')

store = BridgeSqlStore()
completion_engine = BridgeCompletionEngine()
rewrite_engine = RewriteEngine()

REWRITE_OPTIONS = ['make_easier', 'break_smaller', 'give_example', 'explain_differently']


def ok(payload, status=200):
    return jsonify({'ok': True, **payload}), status


def fail(message, status=400, **extra):
    return jsonify({'ok': False, 'error': message, **extra}), status


SUPPORT_ALIASES = {
    'low_energy_mode': 'low_energy',
    'adhd_focus': 'adhd',
    'dyslexia_friendly': 'dyslexia',
    'anxiety_support': 'anxiety',
    'gamify_it': 'step_by_step',
    'connect_interests': 'visual_first',
}


def _normalize_support(value: str) -> str:
    key = str(value).strip()
    return SUPPORT_ALIASES.get(key, key)


def normalize_session(payload):
    session = payload.get('session') or payload.get('workspace')
    if isinstance(session, dict):
        return ensure_workspace(session)
    return {}


def enrich_session(session: dict) -> dict:
    """Runtime-v2 frontend envelope.

    Every API route returns this shape so the React app never has to guess
    whether the canonical object is called a session, workspace, workflow, or
    lane. Older sessions are normalized through runtime_schema first.
    """
    workspace = ensure_workspace(session)
    envelope = RuntimeV2Coordinator(workspace).continue_session('') if False else build_envelope(
        workspace,
        artifact_preview=workspace.get('artifact', {}),
        rewrite_options=REWRITE_OPTIONS,
    )
    return envelope


def _load_workspace_from_request(data):
    session = normalize_session(data)
    if session:
        return session
    workspace_id = data.get('workspace_id') or data.get('session_id') or data.get('id')
    if workspace_id:
        workspace = store.get_workspace(workspace_id)
        return ensure_workspace(workspace) if workspace else None
    return None


@runtime_api.post('/session/create')
def api_session_create():
    data = request.get_json(silent=True) or {}
    task = (data.get('task') or data.get('learning_goal') or data.get('user_words') or '').strip()
    if not task:
        return fail('task is required', 400, code='missing_task')

    supports_raw = data.get('supports') or ['step_by_step']
    if not isinstance(supports_raw, list):
        supports_raw = [str(supports_raw)]
    supports = [_normalize_support(s) for s in supports_raw if s]

    category = detect_task_type(task, data.get('category') or '')
    session = completion_engine.create_session(
        task=task,
        frame=data.get('frame') or data.get('interest_frame') or 'gaming',
        supports=supports,
        user_words=(data.get('user_words') or data.get('own_words') or task).strip(),
        category=category,
    )
    payload = ensure_workspace(session.to_dict())
    payload['title'] = payload.get('task', 'Bridge workspace')
    payload.setdefault('runtime_state', {})
    payload['runtime_state'].setdefault('rewrite_count', 0)
    payload.setdefault('events', []).append(
        {
            'id': uuid4().hex[:12],
            'kind': 'session_created_v2',
            'payload': {'category': payload.get('category'), 'frame': payload.get('frame')},
            'created_at': datetime.utcnow().isoformat(),
        }
    )
    store.save_workspace(payload)
    return ok(enrich_session(payload))


@runtime_api.post('/session/continue')
def api_session_continue():
    data = request.get_json(silent=True) or {}
    workspace = _load_workspace_from_request(data)
    if not workspace:
        return fail('session or workspace_id is required', 400, code='missing_session')

    output = data.get('output') or data.get('user_output') or data.get('text') or ''
    coordinator = RuntimeV2Coordinator(workspace)
    envelope = coordinator.continue_session(output)
    store.save_workspace(envelope['workspace'])
    return ok(envelope)


@runtime_api.post('/session/rewrite')
def api_session_rewrite():
    data = request.get_json(silent=True) or {}
    mode = data.get('mode') or 'make_easier'
    frame = data.get('frame') or data.get('interest_frame') or 'gaming'

    session = _load_workspace_from_request(data)
    if not session:
        return fail('session or workspace_id is required', 400, code='missing_session')

    steps = session.get('steps', [])
    idx = int(session.get('current_step_index', 0) or 0)
    if idx >= len(steps):
        return fail('no active step to rewrite', 400, code='no_active_step')

    step = steps[idx]
    before = (step.get('prompt') or step.get('action') or '').strip()
    if mode == 'break_smaller':
        rewritten = rewrite_engine.break_smaller(before)
        step['prompt'] = '\n'.join(rewritten) if isinstance(rewritten, list) else str(rewritten)
    elif mode == 'explain_differently':
        step['prompt'] = rewrite_engine.explain_differently(before, frame)
    elif mode == 'give_example':
        task_type = detect_task_type(session.get('task', ''), session.get('category', ''))
        step['prompt'] = f"{rewrite_engine.give_example(task_type)}\n\nThen: {before}"
    else:
        step['prompt'] = rewrite_engine.make_easier(before)

    after = step.get('prompt', '')
    rs = session.setdefault('runtime_state', {})
    rs['rewrite_count'] = int(rs.get('rewrite_count', 0)) + 1
    score = RuntimeV2Coordinator(session).rewrite_score(mode, before, after)
    session.setdefault('events', []).append(
        {
            'id': uuid4().hex[:12],
            'kind': 'rewrite_applied',
            'payload': {'mode': mode, 'step_index': idx, 'score': score},
            'created_at': datetime.utcnow().isoformat(),
        },
    )
    session = ensure_workspace(session)
    store.save_workspace(session)
    envelope = enrich_session(session)
    envelope['rewrite_score'] = score
    return ok(envelope)


@runtime_api.post('/session/export')
def api_session_export():
    data = request.get_json(silent=True) or {}
    session = _load_workspace_from_request(data)
    if not session:
        return fail('session or workspace_id is required', 400, code='missing_session')

    export_format = data.get('format') or data.get('export_format') or 'markdown'
    session = ensure_workspace(session)
    compiled = ExportCompiler(session.get('artifact', {})).compile(export_format)
    markdown = compiled['content'] if compiled['format'] == 'markdown' else ExportCompiler(session.get('artifact', {})).compile('markdown')['content']
    plain_text = compiled['content'] if compiled['format'] == 'plain_text' else ExportCompiler(session.get('artifact', {})).compile('plain_text')['content']
    return ok({
        'format': compiled['format'],
        'content': compiled['content'],
        'markdown': markdown,
        'plain_text': plain_text,
        'filename': compiled['filename'],
        'title': session.get('title') or session.get('task') or 'Bridge Export',
    })


@runtime_api.get('/workspace/<workspace_id>')
def api_workspace_get(workspace_id):
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return fail('workspace not found', 404, code='workspace_not_found')
    workspace = ensure_workspace(workspace)
    store.save_workspace(workspace)
    return ok(enrich_session(workspace))


@runtime_api.get('/workspaces/recent')
def api_workspaces_recent():
    limit = int(request.args.get('limit', 20))
    rows = store.list_workspaces(limit=limit)
    summaries = []
    for row in rows:
        raw = ensure_workspace(row.get('raw') or {})
        steps = raw.get('steps') or []
        done = len([s for s in steps if s.get('status') == 'done'])
        summaries.append({
            'id': row.get('id') or raw.get('id'),
            'title': row.get('title') or raw.get('title'),
            'task': row.get('task') or raw.get('task'),
            'frame': row.get('frame') or raw.get('frame'),
            'category': raw.get('category'),
            'status': row.get('status') or raw.get('status'),
            'current_step_index': row.get('current_step_index') or raw.get('current_step_index'),
            'updated_at': row.get('updated_at') or raw.get('updated_at'),
            'progress_done': done,
            'progress_total': len(steps),
        })
    return ok({'workspaces': summaries})


@runtime_api.post('/workspace/save')
def api_workspace_save():
    data = request.get_json(silent=True) or {}
    workspace = data.get('workspace') or data.get('session') or data
    if not isinstance(workspace, dict) or not workspace.get('id'):
        return fail('workspace with id is required', 400, code='missing_workspace')
    workspace = ensure_workspace(workspace)
    store.save_workspace(workspace)
    return ok(enrich_session(workspace))


def register_runtime_api(app):
    app.register_blueprint(runtime_api)
    return app
