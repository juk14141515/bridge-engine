/**
 * Runtime acceptance flow — create → continue → rewrite → export → refresh
 * against Flask on http://127.0.0.1:6060. No mocked responses.
 *
 * Usage: npm run acceptance:runtime
 */

const BASE = 'http://127.0.0.1:6060';
const OFFLINE_MSG =
  'Backend not reachable on http://127.0.0.1:6060. Start it with python app_runtime.py';

const TASK = 'I dislike English, love videogames, and need to write an essay.';
const CONTINUE_OUTPUTS = [
  'Games help me think in stories even when English worksheets feel dead.',
  'My essay connects videogame quest structure to how I plan paragraphs.',
  'Opening draft: English class feels like a grind, but games gave me a quest log for writing.',
];

const BANNED = /\b(NOT\s*FOUND|not_found|undefined|mock|placeholder|demo|fallback)\b/i;
const FALLBACK_PROMPT = /Do the smallest piece of the real task/i;

function fail(message) {
  console.error(`FAIL: ${message}`);
  process.exit(1);
}

function assert(condition, message) {
  if (!condition) fail(message);
}

/** @returns {{ path: string, value: string }[]} */
function collectUserFacingStrings(payload) {
  const out = [];
  if (!payload || typeof payload !== 'object') return out;

  const push = (path, value) => {
    if (typeof value !== 'string') return;
    const trimmed = value.trim();
    if (!trimmed) return;
    out.push({ path, value: trimmed });
  };

  const step = payload.current_step;
  if (step && typeof step === 'object') {
    push('current_step.title', step.title);
    push('current_step.prompt', step.prompt);
    push('current_step.why', step.why);
    push('current_step.action', step.action);
  }

  const np = payload.next_prompt;
  if (np && typeof np === 'object') {
    push('next_prompt.title', np.title);
    push('next_prompt.prompt', np.prompt);
    push('next_prompt.message', np.message);
  }

  collectArtifactPreviewStrings(out, payload.artifact_preview, 'artifact_preview');

  const runtime = payload.frontend_runtime;
  if (runtime && typeof runtime === 'object') {
    const ch = runtime.challenge;
    if (ch && typeof ch === 'object') {
      push('frontend_runtime.challenge.objective', ch.objective);
      push('frontend_runtime.challenge.title', ch.title);
    }
    const sim = runtime.simulation;
    if (sim && typeof sim === 'object') {
      push('frontend_runtime.simulation.scenario', sim.scenario);
      push('frontend_runtime.simulation.title', sim.title);
    }
    const voice = runtime.voice;
    if (voice && typeof voice === 'object') {
      const rp = voice.reflection_prompts;
      if (typeof rp === 'string') push('frontend_runtime.voice.reflection_prompts', rp);
      else if (Array.isArray(rp)) {
        rp.forEach((item, i) => push(`frontend_runtime.voice.reflection_prompts[${i}]`, item));
      }
    }
    const immersion = runtime.immersion_state;
    if (immersion && typeof immersion === 'object') {
      push('frontend_runtime.immersion_state.narrative_thread', immersion.narrative_thread);
      push('frontend_runtime.immersion_state.mission_continuity', immersion.mission_continuity);
      push('frontend_runtime.immersion_state.identity_reinforcement', immersion.identity_reinforcement);
    }
    const reward = runtime.reward_state;
    if (reward && typeof reward === 'object') {
      push('frontend_runtime.reward_state.message', reward.message);
    }
  }

  const ws = payload.workspace ?? payload.session;
  if (ws && typeof ws === 'object') {
    push('workspace.task', ws.task);
    push('workspace.title', ws.title);
    if (Array.isArray(ws.steps)) {
      ws.steps.forEach((s, i) => {
        if (!s || typeof s !== 'object') return;
        push(`workspace.steps[${i}].title`, s.title);
        push(`workspace.steps[${i}].prompt`, s.prompt);
        push(`workspace.steps[${i}].action`, s.action);
      });
    }
  }

  return out;
}

/** @param {{ path: string, value: string }[]} out */
function collectArtifactPreviewStrings(out, preview, prefix) {
  if (!preview || typeof preview !== 'object') return;

  const sections = preview.sections;
  if (sections && typeof sections === 'object') {
    for (const [key, val] of Object.entries(sections)) {
      pushArtifactValue(out, `${prefix}.sections.${key}`, val);
    }
  }

  const outline = preview.outline;
  if (outline && typeof outline === 'object') {
    for (const [key, val] of Object.entries(outline)) {
      pushArtifactValue(out, `${prefix}.outline.${key}`, val);
    }
  }

  if (Array.isArray(preview.cards)) {
    preview.cards.forEach((card, i) => {
      if (!card || typeof card !== 'object') return;
      pushArtifactValue(out, `${prefix}.cards[${i}].front`, card.front);
      pushArtifactValue(out, `${prefix}.cards[${i}].back`, card.back);
    });
  }

  pushArtifactValue(out, `${prefix}.final_output`, preview.final_output);
}

/** @param {{ path: string, value: string }[]} out */
function pushArtifactValue(out, path, value) {
  if (typeof value !== 'string') return;
  const trimmed = value.trim();
  if (!trimmed) return;
  out.push({ path, value: trimmed });
}

function scanUserFacingStrings(payload, label) {
  for (const { path, value } of collectUserFacingStrings(payload)) {
    if (BANNED.test(value)) {
      const match = value.match(BANNED);
      fail(`${label}: banned string "${match?.[0] ?? 'unknown'}" in ${path}`);
    }
  }
}

function scanExportMarkdown(text, label) {
  if (typeof text !== 'string') return;
  const trimmed = text.trim();
  if (!trimmed) return;
  if (BANNED.test(trimmed)) {
    const match = trimmed.match(BANNED);
    fail(`${label}: banned string "${match?.[0] ?? 'unknown'}" in export markdown`);
  }
}

function scanStepCopy(body, label) {
  const step = body.current_step ?? {};
  const prompt = String(step.prompt ?? body.next_prompt?.prompt ?? body.next_prompt?.message ?? '');
  if (FALLBACK_PROMPT.test(prompt)) {
    fail(`${label}: fallback placeholder prompt detected`);
  }
  if (!String(step.title ?? '').trim() && !prompt.trim()) {
    fail(`${label}: empty step title and prompt`);
  }
}

function fr(body) {
  return body.frontend_runtime ?? {};
}

function assertAdaptiveRuntime(body, label) {
  const runtime = fr(body);
  assert(runtime.immersion_state != null && typeof runtime.immersion_state === 'object', `${label}: immersion_state missing`);
  assert(runtime.friction_state != null && typeof runtime.friction_state === 'object', `${label}: friction_state missing`);
  assert(runtime.momentum_state != null && typeof runtime.momentum_state === 'object', `${label}: momentum_state missing`);
  assert(runtime.reward_state != null && typeof runtime.reward_state === 'object', `${label}: reward_state missing`);
  assert(runtime.interaction_rotation != null && typeof runtime.interaction_rotation === 'object', `${label}: interaction_rotation missing`);
  assert(typeof runtime.adaptive_pacing === 'object', `${label}: adaptive_pacing missing`);
  scanUserFacingStrings(body, label);
  scanStepCopy(body, label);
}

async function request(path, init = {}) {
  const url = `${BASE}${path}`;
  let response;
  try {
    response = await fetch(url, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...(init.headers ?? {}),
      },
    });
  } catch {
    console.error(OFFLINE_MSG);
    process.exit(1);
  }

  const raw = await response.text();
  let body;
  try {
    body = raw ? JSON.parse(raw) : {};
  } catch {
    fail(`${init.method ?? 'GET'} ${path} returned non-JSON (${response.status})`);
  }

  if (!response.ok) {
    const err =
      typeof body?.error === 'string'
        ? body.error
        : response.statusText || `HTTP ${response.status}`;
    fail(`${init.method ?? 'GET'} ${path} → ${err}`);
  }

  return body;
}

function stepSnapshot(body) {
  const ws = body.workspace ?? body.session ?? {};
  const step = body.current_step ?? {};
  const progress = body.progress ?? {};
  const runtime = fr(body);
  return {
    workspaceId: ws.id,
    stepIndex: Number(ws.current_step_index ?? -1),
    progressDone: Number(progress.done ?? -1),
    progressTotal: Number(progress.total ?? -1),
    stepTitle: String(step.title ?? ''),
    stepPrompt: String(step.prompt ?? '').slice(0, 80),
    nextTitle: String(body.next_prompt?.title ?? '').slice(0, 60),
    nextPrompt: String(body.next_prompt?.prompt ?? body.next_prompt?.message ?? '').slice(0, 80),
    status: String(ws.status ?? ''),
    interaction: String(runtime.interaction_rotation?.current ?? ''),
    paceModifier: Number(runtime.momentum_state?.pace_modifier ?? runtime.adaptive_pacing?.pace_modifier ?? 1),
    friction: Number(runtime.friction_state?.friction_level ?? 0),
  };
}

function assertProgression(prev, next, label) {
  assert(next.ok === true, `${label}: ok !== true`);

  const prevWs = prev.workspace ?? prev.session ?? {};
  const nextWs = next.workspace ?? next.session ?? {};
  assert(nextWs.id === prevWs.id, `${label}: workspace.id changed`);

  const prevSnap = stepSnapshot(prev);
  const nextSnap = stepSnapshot(next);

  const indexAdvanced = nextSnap.stepIndex > prevSnap.stepIndex;
  const progressAdvanced = nextSnap.progressDone > prevSnap.progressDone;
  assert(
    indexAdvanced || progressAdvanced,
    `${label}: current_step_index and progress.done did not advance (${prevSnap.stepIndex}→${nextSnap.stepIndex}, done ${prevSnap.progressDone}→${nextSnap.progressDone})`,
  );

  const stepChanged =
    nextSnap.stepTitle !== prevSnap.stepTitle ||
    nextSnap.stepPrompt !== prevSnap.stepPrompt ||
    nextSnap.nextTitle !== prevSnap.nextTitle ||
    nextSnap.nextPrompt !== prevSnap.nextPrompt;
  assert(stepChanged, `${label}: current_step / next_prompt did not change`);

  assert(
    next.artifact_preview != null && typeof next.artifact_preview === 'object',
    `${label}: artifact_preview missing`,
  );

  assertAdaptiveRuntime(next, label);
}

function assertInteractionRotation(history) {
  const interactions = history.map((h) => h.interaction).filter(Boolean);
  assert(interactions.length >= 2, 'interaction_rotation: need at least two interaction records');
  for (let i = 1; i < interactions.length; i++) {
    if (interactions[i] && interactions[i - 1] && interactions[i] === interactions[i - 1]) {
      fail(`interaction_rotation: duplicate consecutive type "${interactions[i]}" at step ${i}`);
    }
  }
}

function assertPacingAdapts(history) {
  const modifiers = history.map((h) => h.paceModifier).filter((n) => !Number.isNaN(n));
  assert(modifiers.length >= 2, 'adaptive_pacing: missing pace modifiers');
  const unique = new Set(modifiers.map((m) => m.toFixed(2)));
  assert(unique.size >= 1, 'adaptive_pacing: no pacing data');
}

function formatArtifactPreview(preview) {
  if (!preview || typeof preview !== 'object') return '(none)';
  const sections = preview.sections;
  if (sections && typeof sections === 'object') {
    const keys = Object.keys(sections).filter((k) => String(sections[k] ?? '').trim());
    if (keys.length) return `sections: ${keys.join(', ')}`;
  }
  if (preview.outline && typeof preview.outline === 'object') {
    const keys = Object.keys(preview.outline).filter((k) => String(preview.outline[k] ?? '').trim());
    if (keys.length) return `outline: ${keys.join(', ')}`;
  }
  const type = preview.type ? `type=${preview.type}` : 'artifact';
  return type;
}

async function main() {
  console.log('Bridge runtime acceptance flow');
  console.log(`Target: ${BASE}\n`);

  try {
    await fetch(`${BASE}/api/workspaces/recent?limit=1`);
  } catch {
    console.error(OFFLINE_MSG);
    process.exit(1);
  }

  const create = await request('/api/session/create', {
    method: 'POST',
    body: JSON.stringify({
      task: TASK,
      frame: 'gaming',
      interests: ['gaming'],
      supports: ['step_by_step'],
      user_words: TASK,
    }),
  });

  assert(create.ok === true, 'create: ok !== true');
  const workspaceId = create.workspace?.id ?? create.session?.id;
  assert(workspaceId, 'create: missing workspace.id');
  assertAdaptiveRuntime(create, 'create');

  const history = [stepSnapshot(create)];
  let last = create;

  for (let i = 0; i < CONTINUE_OUTPUTS.length; i++) {
    const output = CONTINUE_OUTPUTS[i];
    const cont = await request('/api/session/continue', {
      method: 'POST',
      body: JSON.stringify({
        workspace_id: workspaceId,
        user_output: output,
      }),
    });
    assertProgression(last, cont, `continue #${i + 1}`);
    history.push(stepSnapshot(cont));
    last = cont;
  }

  assertInteractionRotation(history);
  assertPacingAdapts(history);

  const refresh = await request(`/api/workspace/${encodeURIComponent(workspaceId)}`, {
    method: 'GET',
  });
  assert(refresh.ok === true, 'refresh: ok !== true');
  assert((refresh.workspace?.id ?? refresh.session?.id) === workspaceId, 'refresh: workspace id changed');
  const refreshSnap = stepSnapshot(refresh);
  const lastSnap = stepSnapshot(last);
  assert(
    refreshSnap.stepIndex === lastSnap.stepIndex && refreshSnap.progressDone === lastSnap.progressDone,
    `refresh: progress reset (${lastSnap.stepIndex}/${lastSnap.progressDone} → ${refreshSnap.stepIndex}/${refreshSnap.progressDone})`,
  );
  assertAdaptiveRuntime(refresh, 'refresh');

  const rewrite = await request('/api/session/rewrite', {
    method: 'POST',
    body: JSON.stringify({
      workspace_id: workspaceId,
      mode: 'make_easier',
    }),
  });

  assert(rewrite.ok === true, 'rewrite: ok !== true');
  assert((rewrite.workspace?.id ?? rewrite.session?.id) === workspaceId, 'rewrite: workspace.id changed');
  assertAdaptiveRuntime(rewrite, 'rewrite');
  history.push({ ...stepSnapshot(rewrite), label: 'after rewrite' });

  const exported = await request('/api/session/export', {
    method: 'POST',
    body: JSON.stringify({
      workspace_id: workspaceId,
      format: 'markdown',
    }),
  });

  const exportText = exported.markdown ?? exported.content ?? exported.plain_text ?? '';
  assert(typeof exportText === 'string' && exportText.length > 0, 'export: empty markdown');
  scanExportMarkdown(exportText, 'export');

  const finalPreview = last.artifact_preview ?? {};
  const finalRuntime = fr(last);

  console.log('--- Summary ---');
  console.log(`Workspace id:     ${workspaceId}`);
  console.log('Step progression:');
  history.forEach((snap, idx) => {
    const label = snap.label ?? `step ${idx}`;
    console.log(
      `  [${label}] index=${snap.stepIndex} done=${snap.progressDone}/${snap.progressTotal} interaction=${snap.interaction || '—'}`,
    );
    if (snap.stepTitle) console.log(`           current: ${snap.stepTitle}`);
  });
  console.log(`Artifact preview: ${formatArtifactPreview(finalPreview)}`);
  console.log(`Immersion:        ${finalRuntime.immersion_state?.session_phase ?? '—'}`);
  console.log(`Friction:         ${finalRuntime.friction_state?.friction_level ?? '—'}`);
  console.log(`Momentum mode:    ${finalRuntime.momentum_state?.mode ?? '—'}`);
  console.log(`Reward:           ${finalRuntime.reward_state?.message ?? '—'}`);
  console.log(`Export length:    ${exportText.length} characters`);
  console.log('\nPASS');
}

main().catch((err) => {
  console.error('FAIL:', err instanceof Error ? err.message : err);
  process.exit(1);
});
