from datetime import datetime
from uuid import uuid4

from flask import Blueprint, jsonify, request

from bridge_core.completion_engine import BridgeCompletionEngine, BridgeSession
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

REWRITE_OPTIONS = ['make_easier', 'break_smaller', 'give_example', 'explain_differently']


def ok(payload, status=200):
    return jsonify({'ok': True, **payload}), status


def fail(message, status=400):
    return jsonify({'ok': False, 'error': message}), status


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
    if not isinstance(session, dict):
        return {}
    return session


def build_artifact_preview(session):
    task = (session.get('task') or session.get('title') or '').lower()
    if any(word in task for word in ['essay', 'paper', 'writing', 'paragraph']):
        return artifact_engine.build_essay_outline(session)
    if any(word in task for word in ['study', 'quiz', 'learn', 'exam']):
        return artifact_engine.build_flashcards(session.get('task', 'Study'), ['core concept', 'example', 'definition'])
    if any(word in task for word in ['code', 'app', 'website', 'python']):
        return artifact_engine.build_code_scaffold(session.get('task', 'Bridge Project'))
    if any(word in task for word in ['relationship', 'text', 'conversation', 'boundary']):
        return {
            'type': 'relationship_workspace',
            'sections': session.get('artifact', {}).get('sections', {}),
        }
    return {'type': 'general', 'sections': session.get('artifact', {}).get('sections', {})}


def export_session_text(session):
    lines = []
    for step in session.get('steps', []):
        lines.append(f"## {step.get('title', 'Step')}")
        lines.append(step.get('user_output') or step.get('answer') or step.get('prompt') or '')
        lines.append('')
    sections = (session.get('artifact') or {}).get('sections', {})
    if sections:
        lines.append('## Artifact sections')
        for name, value in sections.items():
            lines.append(f"### {name}")
            lines.append(str(value))
            lines.append('')
    return '\n'.join(lines).strip()


def enrich_session(session: dict) -> dict:
    """Full runtime envelope for the adaptive UI."""
    if not session:
        return {}
    intel = session_intelligence.analyze(session)
    next_prompt = progression_engine.next_step(session)
    artifact_preview = build_artifact_preview(session)
    memory_summary = memory_engine.summarize_session(session)
    steps = session.get('steps', [])
    idx = int(session.get('current_step_index', 0) or 0)
    current_step = steps[idx] if idx < len(steps) else None
    done = len([s for s in steps if s.get('status') == 'done'])
    total = len(steps)
    rs = session.setdefault('runtime_state', {})
    rs.setdefault('mode', 'guided_completion')
    rs['status'] = session.get('status', 'active')
    rs['current_step_index'] = idx
    rs['completion_rate'] = intel.get('completion_rate', 0)
    rs['momentum_state'] = intel.get('state', 'starting')
    rs['momentum_label'] = _momentum_label(intel.get('state', 'starting'))
    rs['friction_level'] = 'high' if intel.get('state') == 'stuck' else 'normal'

    return {
        'workspace': session,
        'session': session,
        'runtime_state': rs,
        'intelligence': intel,
        'next_prompt': next_prompt,
        'artifact_preview': artifact_preview,
        'memory_summary': memory_summary,
        'rewrite_options': REWRITE_OPTIONS,
        'current_step': current_step,
        'progress': {
            'done': done,
            'total': total,
            'percent': int((done / total) * 100) if total else 0,
        },
    }


def _momentum_label(state: str) -> str:
    return {
        'starting': 'Finding rhythm',
        'building': 'Momentum building',
        'flow': 'Flow state',
        'stuck': 'Low-friction mode',
    }.get(state, 'Adaptive')


def advance_with_engine(session_dict: dict, output: str) -> dict:
    sess = BridgeSession.from_dict(session_dict)
    completion_engine.advance(sess, output or '')
    return sess.to_dict()


@runtime_api.post('/session/create')
def api_session_create():
    data = request.get_json(silent=True) or {}
    task = (data.get('task') or data.get('learning_goal') or '').strip()
    if not task:
        return fail('task is required')

    supports_raw = data.get('supports') or ['step_by_step']
    if not isinstance(supports_raw, list):
        supports_raw = [str(supports_raw)]
    supports = [_normalize_support(s) for s in supports_raw if s]

    session = completion_engine.create_session(
        task=task,
        frame=data.get('frame') or data.get('interest_frame') or 'gaming',
        supports=supports,
        user_words=(data.get('user_words') or data.get('own_words') or '').strip(),
        category=data.get('category') or 'general',
    )
    payload = session.to_dict()
    payload['title'] = payload.get('task', 'Bridge workspace')
    payload.setdefault('runtime_state', {})
    payload['runtime_state'].setdefault('rewrite_count', 0)
    store.save_workspace(payload)
    return ok(enrich_session(payload))


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
    updated = advance_with_engine(session, output)
    store.save_workspace(updated)
    return ok(enrich_session(updated))


@runtime_api.post('/session/rewrite')
def api_session_rewrite():
    data = request.get_json(silent=True) or {}
    mode = data.get('mode') or 'make_easier'
    frame = data.get('frame') or 'gaming'

    session = normalize_session(data)
    if not session:
        wid = data.get('workspace_id') or data.get('session_id')
        session = store.get_workspace(wid) if wid else None
    if not session:
        return fail('session or workspace_id is required')

    steps = session.get('steps', [])
    idx = int(session.get('current_step_index', 0) or 0)
    if idx >= len(steps):
        return fail('no active step to rewrite')

    step = steps[idx]
    base = (step.get('prompt') or step.get('action') or '').strip()
    if mode == 'break_smaller':
        rewritten = rewrite_engine.break_smaller(base)
        if isinstance(rewritten, list):
            step['prompt'] = '\n'.join(rewritten)
        else:
            step['prompt'] = str(rewritten)
    elif mode == 'explain_differently':
        step['prompt'] = rewrite_engine.explain_differently(base, frame)
    elif mode == 'give_example':
        task_type = completion_engine.classify_task(session.get('task', ''), session.get('category', ''))
        step['prompt'] = f"{rewrite_engine.give_example(task_type)}\n\nThen: {base}"
    else:
        step['prompt'] = rewrite_engine.make_easier(base)

    rs = session.setdefault('runtime_state', {})
    rs['rewrite_count'] = int(rs.get('rewrite_count', 0)) + 1
    session.setdefault('events', []).append(
        {
            'id': uuid4().hex[:12],
            'kind': 'rewrite_applied',
            'payload': {'mode': mode, 'step_index': idx},
            'created_at': datetime.utcnow().isoformat(),
        },
    )
    store.save_workspace(session)
    return ok(enrich_session(session))


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
    exported_md = artifact_engine.export_markdown(title, content)
    plain = completion_engine.export_markdown(BridgeSession.from_dict(session))
    return ok({
        'format': 'markdown',
        'markdown': exported_md,
        'plain_text': plain,
        'title': title,
    })


@runtime_api.get('/workspace/<workspace_id>')
def api_workspace_get(workspace_id):
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return fail('workspace not found', 404)
    return ok(enrich_session(workspace))


@runtime_api.get('/workspaces/recent')
def api_workspaces_recent():
    limit = int(request.args.get('limit', 20))
    rows = store.list_workspaces(limit=limit)
    summaries = []
    for row in rows:
        raw = row.get('raw') or {}
        steps = raw.get('steps') or []
        done = len([s for s in steps if s.get('status') == 'done'])
        summaries.append({
            'id': row.get('id'),
            'title': row.get('title'),
            'task': row.get('task'),
            'frame': row.get('frame'),
            'status': row.get('status'),
            'current_step_index': row.get('current_step_index'),
            'updated_at': row.get('updated_at'),
            'progress_done': done,
            'progress_total': len(steps),
        })
    return ok({'workspaces': summaries})


@runtime_api.post('/workspace/save')
def api_workspace_save():
    data = request.get_json(silent=True) or {}
    workspace = data.get('workspace') or data.get('session') or data
    if not isinstance(workspace, dict) or not workspace.get('id'):
        return fail('workspace with id is required')
    store.save_workspace(workspace)
    return ok(enrich_session(workspace))


def register_runtime_api(app):
    app.register_blueprint(runtime_api)
    return app
