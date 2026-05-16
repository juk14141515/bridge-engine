from datetime import datetime
from uuid import uuid4

from flask import Blueprint, jsonify, request

from bridge_core.completion_engine import BridgeCompletionEngine
from bridge_core.export_compiler import ExportCompiler
from bridge_core.adaptive_cognition_runtime import apply_adaptive_cognition
from bridge_core.master_runtime_orchestrator import MasterRuntimeOrchestrator
from bridge_core.rewrite_engine import RewriteEngine
from bridge_core.runtime_schema import ensure_workspace
from bridge_core.runtime_v2_coordinator import RuntimeV2Coordinator
from bridge_core.sql_store import BridgeSqlStore
from bridge_core.task_registry import detect_task_type

runtime_api = Blueprint('runtime_api', __name__, url_prefix='/api')

store = BridgeSqlStore()
completion_engine = BridgeCompletionEngine()
rewrite_engine = RewriteEngine()

REWRITE_OPTIONS = ['make_easier', 'break_smaller', 'give_example', 'explain_differently', 'do_first_line']


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


def _profile_from_payload(data: dict, session: dict | None = None) -> dict:
    session = session or {}
    profile = data.get('profile') if isinstance(data.get('profile'), dict) else {}
    interests = data.get('interests') or session.get('interests') or profile.get('interests') or []
    if isinstance(interests, str):
        interests = [interests]
    profile.setdefault('interests', interests)
    profile.setdefault('learning_preferences', data.get('learning_preferences') or profile.get('learning_preferences') or [])
    if data.get('interaction_style'):
        profile['interaction_style'] = data.get('interaction_style')
    if data.get('cognitive_profile'):
        profile['cognitive_profile'] = data.get('cognitive_profile')
    return profile


def _context_from_payload(data: dict) -> dict:
    context = data.get('context') if isinstance(data.get('context'), dict) else {}
    for key in ['environment', 'energy', 'available_minutes']:
        if key in data:
            context[key] = data[key]
    return context


def _event_from_request(data: dict, latest_output: str = '') -> dict:
    event_type = data.get('event_type') or ('continue' if latest_output else 'refresh')
    if data.get('mode') and event_type == 'refresh':
        event_type = 'rewrite'
    return {
        'type': event_type,
        'user_output': latest_output or data.get('user_output') or '',
        'mode': data.get('mode'),
        'successful': True,
    }


def _frontend_runtime(contract: dict, cognition: dict | None = None) -> dict:
    cognition = cognition or contract.get('adaptive_cognition') or {}
    pacing = {**contract.get('pacing', {}), **cognition.get('adaptive_pacing', {})}
    rewards = contract.get('rewards', {})
    reward_state = cognition.get('reward_state', {})
    return {
        'ui_mode': contract.get('contextual_runtime', {}).get('environment_feel', 'adaptive_environment'),
        'interaction_modes': contract.get('interaction_runtime', {}).get('interaction_modes', []),
        'selected_modes': contract.get('interaction_selection', {}).get('selected_modes', []),
        'challenge': contract.get('minigame', {}),
        'simulation': contract.get('simulation', {}),
        'reward': {**rewards, **reward_state},
        'voice': contract.get('voice_runtime', {}),
        'pacing': pacing,
        'verification': contract.get('verification', {}),
        'gate': contract.get('gate', {}),
        'engagement': contract.get('engagement', {}),
        'pathways': contract.get('pathways', {}),
        'immersion_state': cognition.get('immersion_state', {}),
        'friction_state': cognition.get('friction_state', {}),
        'adaptive_pacing': cognition.get('adaptive_pacing', {}),
        'interaction_rotation': cognition.get('interaction_rotation', {}),
        'momentum_state': cognition.get('momentum_state', {}),
        'reward_state': reward_state,
        'identity_state': cognition.get('identity_state', {}),
        'calm_contract': {
            'primary_action_only': pacing.get('step_size') == 'tiny',
            'hide_backend_complexity': True,
            'show_next_step_first': True,
            'focus_mode': cognition.get('momentum_state', {}).get('mode') == 'deep_engagement',
        },
    }


def normalize_session(payload):
    session = payload.get('session') or payload.get('workspace')
    if isinstance(session, dict):
        return ensure_workspace(session)
    return {}


def enrich_session(session: dict, *, data: dict | None = None, latest_output: str = '', persist: bool = False) -> dict:
    data = data or {}
    workspace = ensure_workspace(session)
    profile = _profile_from_payload(data, workspace)
    context = _context_from_payload(data)
    contract = MasterRuntimeOrchestrator(profile=profile, context=context).build_contract(
        workspace,
        latest_output=latest_output,
        persist=persist,
    )
    cognition = apply_adaptive_cognition(
        workspace,
        event=_event_from_request(data, latest_output),
        user_output=latest_output,
    )
    contract['workspace'] = workspace
    contract['session'] = workspace
    contract['adaptive_cognition'] = cognition
    contract['memory_summary'] = cognition.get('runtime_profile', {})
    contract['frontend_runtime'] = _frontend_runtime(contract, cognition)
    contract['rewrite_options'] = REWRITE_OPTIONS
    return contract


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
    payload['interests'] = data.get('interests') or []
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
    return ok(enrich_session(payload, data=data, persist=True))


@runtime_api.post('/session/continue')
def api_session_continue():
    data = request.get_json(silent=True) or {}
    workspace = _load_workspace_from_request(data)
    if not workspace:
        return fail('session or workspace_id is required', 400, code='missing_session')

    output = data.get('output') or data.get('user_output') or data.get('text') or ''
    coordinator = RuntimeV2Coordinator(workspace)
    envelope = coordinator.continue_session(output)
    updated_workspace = ensure_workspace(envelope['workspace'])
    enriched = enrich_session(
        updated_workspace,
        data={**data, 'event_type': 'continue'},
        latest_output=output,
        persist=True,
    )
    if envelope.get('verification'):
        enriched['verification'] = envelope['verification']
        enriched.setdefault('frontend_runtime', {})['verification'] = envelope['verification']
    if envelope.get('gate'):
        enriched['gate'] = envelope['gate']
        enriched.setdefault('frontend_runtime', {})['gate'] = envelope['gate']
    if envelope.get('next_prompt'):
        enriched['next_prompt'] = envelope['next_prompt']
    store.save_workspace(ensure_workspace(enriched['workspace']))
    return ok(enriched)


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
    elif mode == 'do_first_line':
        task_type = detect_task_type(session.get('task', ''), session.get('category', ''))
        step['prompt'] = f"{rewrite_engine.do_first_line(task_type)}\n\nThen keep going with: {before}"
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
    enriched = enrich_session(session, data={**data, 'event_type': 'rewrite', 'mode': mode}, persist=True)
    enriched['rewrite_score'] = score
    store.save_workspace(ensure_workspace(enriched['workspace']))
    return ok(enriched)


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
        'frontend_runtime': _frontend_runtime(enrich_session(session, data=data)),
    })


@runtime_api.get('/workspace/<workspace_id>')
def api_workspace_get(workspace_id):
    workspace = store.get_workspace(workspace_id)
    if not workspace:
        return fail('workspace not found', 404, code='workspace_not_found')
    workspace = ensure_workspace(workspace)
    store.save_workspace(workspace)
    return ok(enrich_session(workspace, persist=True))


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
    return ok(enrich_session(workspace, data=data, persist=True))


def register_runtime_api(app):
    app.register_blueprint(runtime_api)
    return app
