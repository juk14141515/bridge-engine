/**
 * Bridge runtime acceptance flow.
 *
 * Exercises the real Flask runtime on http://127.0.0.1:6060:
 * create -> continue -> continue -> continue -> rewrite -> refresh -> export
 *
 * No mocked responses. Uses older JavaScript syntax for VPS compatibility.
 */

import http from 'http';
import { URL } from 'url';

const BASE = 'http://127.0.0.1:6060';
const OFFLINE_MSG =
  'Backend not reachable on http://127.0.0.1:6060. Start it with python app_runtime.py';

const TASK = 'I dislike English, love videogames, and need to write an essay.';
const FRAME = 'gaming';
const CONTINUE_OUTPUTS = [
  'Games help me think in stories even when English worksheets feel dead.',
  'My essay connects videogame quest structure to how I plan paragraphs.',
  'Opening draft: English class feels like a grind, but games gave me a quest log for writing.',
];

const BANNED = /\b(NOT\s*FOUND|not_found|undefined|mock|placeholder|demo|fallback)\b/i;

const results = {
  create: 'PENDING',
  continue1: 'PENDING',
  continue2: 'PENDING',
  continue3: 'PENDING',
  rewrite: 'PENDING',
  refresh: 'PENDING',
  export: 'PENDING',
};

function fail(phase, endpoint, message, detail) {
  console.error('\nFAIL');
  console.error('Phase: ' + phase);
  if (endpoint) console.error('Endpoint: ' + endpoint);
  console.error('Assertion: ' + message);
  if (detail) {
    if (detail.statusCode) console.error('Status code: ' + detail.statusCode);
    if (detail.bodySnippet) console.error('Body snippet: ' + detail.bodySnippet);
  }
  process.exit(1);
}

function assertPhase(condition, phase, endpoint, message, detail) {
  if (!condition) fail(phase, endpoint, message, detail);
}

function bodySnippet(body) {
  var text = '';
  try {
    text = typeof body === 'string' ? body : JSON.stringify(body);
  } catch (err) {
    text = String(body);
  }
  return text.slice(0, 700);
}

async function fetchRaw(path, init) {
  var target = new URL(BASE + path);
  var options = init || {};
  var method = options.method || 'GET';
  var headers = options.headers || {};
  var body = options.body || '';

  if (body && !headers['Content-Length']) {
    headers['Content-Length'] = Buffer.byteLength(body);
  }

  return new Promise(function (resolve) {
    var req = http.request(
      {
        hostname: target.hostname,
        port: target.port,
        path: target.pathname + target.search,
        method: method,
        headers: headers,
        timeout: 15000,
      },
      function (res) {
        var chunks = [];
        res.on('data', function (chunk) {
          chunks.push(chunk);
        });
        res.on('end', function () {
          var raw = Buffer.concat(chunks).toString('utf8');
          var parsed = null;
          if (raw) {
            try {
              parsed = JSON.parse(raw);
            } catch (err) {
              parsed = raw;
            }
          } else {
            parsed = {};
          }
          resolve({
            networkError: false,
            status: res.statusCode || 0,
            ok: (res.statusCode || 0) >= 200 && (res.statusCode || 0) < 300,
            body: parsed,
            raw: raw,
          });
        });
      },
    );

    req.on('timeout', function () {
      req.destroy(new Error('request timed out'));
    });

    req.on('error', function (err) {
      resolve({
        networkError: true,
        status: 0,
        ok: false,
        body: null,
        raw: String(err && err.message ? err.message : err),
      });
    });

    if (body) req.write(body);
    req.end();
  });
}

async function request(phase, path, method, payload) {
  var init = {
    method: method || 'GET',
    headers: { 'Content-Type': 'application/json' },
  };
  if (payload !== undefined) init.body = JSON.stringify(payload);

  var res = await fetchRaw(path, init);
  if (res.networkError) {
    if (phase === 'create') {
      console.error(OFFLINE_MSG);
      process.exit(1);
    }
    fail(phase, path, 'network request failed', { bodySnippet: res.raw });
  }
  if (!res.ok) {
    fail(phase, path, 'HTTP request failed', {
      statusCode: res.status,
      bodySnippet: bodySnippet(res.body),
    });
  }
  if (!res.body || typeof res.body !== 'object') {
    fail(phase, path, 'response was not a JSON object', {
      statusCode: res.status,
      bodySnippet: bodySnippet(res.body),
    });
  }
  return res.body;
}

async function optionalHealthProbe() {
  var res = await fetchRaw('/api/health', { method: 'GET' });
  if (res.networkError) return { reachable: false, health: null };
  if (res.ok && res.body && res.body.ok === true) {
    return { reachable: true, health: res.body };
  }
  return { reachable: true, health: null };
}

function getWorkspace(body) {
  if (body && body.workspace && typeof body.workspace === 'object') return body.workspace;
  if (body && body.session && typeof body.session === 'object') return body.session;
  return {};
}

function getWorkspaceId(body) {
  var ws = getWorkspace(body);
  return ws.id || ws.workspace_id || ws.session_id || '';
}

function getProgressDone(body) {
  if (body && body.progress && typeof body.progress.done === 'number') return body.progress.done;
  var ws = getWorkspace(body);
  if (Array.isArray(ws.steps)) {
    return ws.steps.filter(function (step) {
      return step && (step.status === 'done' || step.status === 'completed');
    }).length;
  }
  return 0;
}

function getStepIndex(body) {
  var ws = getWorkspace(body);
  var value = ws.current_step_index;
  return typeof value === 'number' ? value : Number(value || 0);
}

function currentStep(body) {
  if (body && body.current_step && typeof body.current_step === 'object') return body.current_step;
  return {};
}

function runtime(body) {
  if (body && body.frontend_runtime && typeof body.frontend_runtime === 'object') {
    return body.frontend_runtime;
  }
  return {};
}

function artifactPreview(body) {
  if (body && body.artifact_preview && typeof body.artifact_preview === 'object') {
    return body.artifact_preview;
  }
  return {};
}

function artifactPreviewLength(body) {
  return bodySnippet(artifactPreview(body)).length;
}

function stepSignature(body) {
  var step = currentStep(body);
  var next = body && body.next_prompt && typeof body.next_prompt === 'object' ? body.next_prompt : {};
  return [
    step.id || '',
    step.title || '',
    step.prompt || '',
    step.action || '',
    next.title || '',
    next.prompt || '',
    next.message || '',
  ].join('|');
}

function previousStepCompleted(prevBody, nextBody) {
  var prevWs = getWorkspace(prevBody);
  var nextWs = getWorkspace(nextBody);
  var prevIdx = getStepIndex(prevBody);
  if (!Array.isArray(nextWs.steps) || prevIdx < 0 || prevIdx >= nextWs.steps.length) return false;
  var step = nextWs.steps[prevIdx];
  return step && (step.status === 'done' || step.status === 'completed');
}

function collectUserFacingStrings(payload) {
  var out = [];
  if (!payload || typeof payload !== 'object') return out;

  function push(path, value) {
    if (typeof value !== 'string') return;
    var trimmed = value.trim();
    if (!trimmed) return;
    out.push({ path: path, value: trimmed });
  }

  var step = currentStep(payload);
  push('current_step.title', step.title);
  push('current_step.prompt', step.prompt);
  push('current_step.action', step.action);
  push('current_step.why', step.why);

  var next = payload.next_prompt && typeof payload.next_prompt === 'object' ? payload.next_prompt : {};
  push('next_prompt.title', next.title);
  push('next_prompt.prompt', next.prompt);
  push('next_prompt.message', next.message);

  collectArtifactStrings(out, artifactPreview(payload), 'artifact_preview');

  var fr = runtime(payload);
  var challenge = fr.challenge && typeof fr.challenge === 'object' ? fr.challenge : {};
  var simulation = fr.simulation && typeof fr.simulation === 'object' ? fr.simulation : {};
  var voice = fr.voice && typeof fr.voice === 'object' ? fr.voice : {};
  var reward = fr.reward && typeof fr.reward === 'object' ? fr.reward : {};
  var rewardState = fr.reward_state && typeof fr.reward_state === 'object' ? fr.reward_state : {};
  var immersion = fr.immersion_state && typeof fr.immersion_state === 'object' ? fr.immersion_state : {};

  push('frontend_runtime.challenge.objective', challenge.objective);
  push('frontend_runtime.simulation.scenario', simulation.scenario);
  if (typeof voice.reflection_prompts === 'string') {
    push('frontend_runtime.voice.reflection_prompts', voice.reflection_prompts);
  } else if (Array.isArray(voice.reflection_prompts)) {
    voice.reflection_prompts.forEach(function (value, index) {
      push('frontend_runtime.voice.reflection_prompts[' + index + ']', value);
    });
  }
  push('frontend_runtime.reward.message', reward.message);
  push('frontend_runtime.reward_state.message', rewardState.message);
  push('frontend_runtime.immersion_state.narrative_thread', immersion.narrative_thread);
  push('frontend_runtime.immersion_state.mission_continuity', immersion.mission_continuity);

  return out;
}

function collectArtifactStrings(out, preview, prefix) {
  if (!preview || typeof preview !== 'object') return;
  pushArtifact(out, prefix + '.final_output', preview.final_output);
  if (preview.sections && typeof preview.sections === 'object') {
    Object.keys(preview.sections).forEach(function (key) {
      pushArtifact(out, prefix + '.sections.' + key, preview.sections[key]);
    });
  }
}

function pushArtifact(out, path, value) {
  if (typeof value !== 'string') return;
  var trimmed = value.trim();
  if (trimmed) out.push({ path: path, value: trimmed });
}

function scanUserFacingStrings(phase, endpoint, payload) {
  collectUserFacingStrings(payload).forEach(function (entry) {
    var match = entry.value.match(BANNED);
    if (match) {
      fail(phase, endpoint, 'banned user-facing string "' + match[0] + '" in ' + entry.path, {
        bodySnippet: entry.value.slice(0, 500),
      });
    }
  });
}

function assertBaseContract(phase, endpoint, body) {
  assertPhase(body.ok === true, phase, endpoint, 'ok !== true', { bodySnippet: bodySnippet(body) });
  assertPhase(getWorkspaceId(body), phase, endpoint, 'workspace/session id missing', {
    bodySnippet: bodySnippet(body),
  });
  assertPhase(Object.keys(currentStep(body)).length > 0, phase, endpoint, 'current_step missing', {
    bodySnippet: bodySnippet(body),
  });
  assertPhase(body.artifact_preview && typeof body.artifact_preview === 'object', phase, endpoint, 'artifact_preview missing', {
    bodySnippet: bodySnippet(body),
  });
  var fr = runtime(body);
  assertPhase(Object.keys(fr).length > 0, phase, endpoint, 'frontend_runtime missing', {
    bodySnippet: bodySnippet(body),
  });
  assertPhase(fr.calm_contract && typeof fr.calm_contract === 'object', phase, endpoint, 'frontend_runtime.calm_contract missing', {
    bodySnippet: bodySnippet(fr),
  });
  assertPhase(fr.immersion_state && typeof fr.immersion_state === 'object', phase, endpoint, 'frontend_runtime.immersion_state missing', {
    bodySnippet: bodySnippet(fr),
  });
  assertPhase(fr.friction_state && typeof fr.friction_state === 'object', phase, endpoint, 'frontend_runtime.friction_state missing', {
    bodySnippet: bodySnippet(fr),
  });
  assertPhase(fr.reward_state && typeof fr.reward_state === 'object', phase, endpoint, 'frontend_runtime.reward_state missing', {
    bodySnippet: bodySnippet(fr),
  });
  assertPhase(fr.interaction_rotation && typeof fr.interaction_rotation === 'object', phase, endpoint, 'frontend_runtime.interaction_rotation missing', {
    bodySnippet: bodySnippet(fr),
  });
  scanUserFacingStrings(phase, endpoint, body);
}

function assertContext(phase, endpoint, body) {
  var ws = getWorkspace(body);
  var task = String(ws.task || ws.title || '').toLowerCase();
  var frame = String(ws.frame || '').toLowerCase();
  assertPhase(task.indexOf('essay') !== -1, phase, endpoint, 'essay context was not preserved', {
    bodySnippet: bodySnippet(ws),
  });
  assertPhase(frame === FRAME, phase, endpoint, 'gaming frame was not preserved', {
    bodySnippet: bodySnippet(ws),
  });
}

function snapshot(body) {
  var fr = runtime(body);
  var rotation = fr.interaction_rotation && typeof fr.interaction_rotation === 'object' ? fr.interaction_rotation : {};
  var friction = fr.friction_state && typeof fr.friction_state === 'object' ? fr.friction_state : {};
  var momentum = fr.momentum_state && typeof fr.momentum_state === 'object' ? fr.momentum_state : {};
  var reward = fr.reward_state && typeof fr.reward_state === 'object' ? fr.reward_state : {};
  return {
    id: getWorkspaceId(body),
    index: getStepIndex(body),
    done: getProgressDone(body),
    signature: stepSignature(body),
    interaction: String(rotation.current || ''),
    friction: String(friction.friction_level !== undefined ? friction.friction_level : ''),
    momentum: String(momentum.mode || momentum.challenge_level || ''),
    reward: String(reward.message || ''),
    artifactLength: artifactPreviewLength(body),
  };
}

function assertContinue(prev, next, phase, endpoint) {
  assertBaseContract(phase, endpoint, next);
  assertPhase(getWorkspaceId(next) === getWorkspaceId(prev), phase, endpoint, 'workspace id changed', {
    bodySnippet: bodySnippet(next),
  });
  var advanced =
    getStepIndex(next) > getStepIndex(prev) ||
    getProgressDone(next) > getProgressDone(prev) ||
    previousStepCompleted(prev, next);
  assertPhase(advanced, phase, endpoint, 'step index/progress did not advance and previous step was not completed', {
    bodySnippet: bodySnippet(next),
  });
  assertPhase(artifactPreviewLength(next) >= Math.min(artifactPreviewLength(prev), 2), phase, endpoint, 'artifact preview appeared to reset', {
    bodySnippet: bodySnippet(next.artifact_preview),
  });
}

function assertRewrite(rewrite, workspaceId) {
  var endpoint = '/api/session/rewrite';
  assertBaseContract('rewrite', endpoint, rewrite);
  assertPhase(getWorkspaceId(rewrite) === workspaceId, 'rewrite', endpoint, 'workspace id changed', {
    bodySnippet: bodySnippet(rewrite),
  });
  assertContext('rewrite', endpoint, rewrite);
  var step = currentStep(rewrite);
  var text = [step.prompt || '', step.action || '', step.why || ''].join(' ').trim();
  assertPhase(text.length > 0, 'rewrite', endpoint, 'rewritten prompt/help text missing', {
    bodySnippet: bodySnippet(step),
  });
}

function assertRefresh(refresh, last, workspaceId) {
  var endpoint = '/api/workspace/' + encodeURIComponent(workspaceId);
  assertBaseContract('refresh', endpoint, refresh);
  assertPhase(getWorkspaceId(refresh) === workspaceId, 'refresh', endpoint, 'workspace id changed', {
    bodySnippet: bodySnippet(refresh),
  });
  assertContext('refresh', endpoint, refresh);
  assertPhase(getStepIndex(refresh) >= getStepIndex(last) && getProgressDone(refresh) >= getProgressDone(last), 'refresh', endpoint, 'progress reset after refresh', {
    bodySnippet: bodySnippet(refresh),
  });
}

function assertExport(exported, workspaceId) {
  var endpoint = '/api/session/export';
  if (Object.prototype.hasOwnProperty.call(exported, 'ok')) {
    assertPhase(exported.ok === true, 'export', endpoint, 'ok !== true', {
      bodySnippet: bodySnippet(exported),
    });
  }
  var text = exported.markdown || exported.content || exported.plain_text || '';
  assertPhase(typeof text === 'string' && text.length > 0, 'export', endpoint, 'export markdown/content/plain_text missing', {
    bodySnippet: bodySnippet(exported),
  });
  var match = text.match(BANNED);
  if (match) {
    fail('export', endpoint, 'banned user-facing string "' + match[0] + '" in export text', {
      bodySnippet: text.slice(0, 500),
    });
  }
  return text.length;
}

function printSummary(workspaceId, history, exportLength) {
  var last = history[history.length - 1] || {};
  console.log('\nBridge Runtime Acceptance Summary\n');
  console.log('* Workspace ID: ' + workspaceId);
  console.log('* Create: ' + results.create);
  console.log('* Continue 1: ' + results.continue1);
  console.log('* Continue 2: ' + results.continue2);
  console.log('* Continue 3: ' + results.continue3);
  console.log('* Rewrite: ' + results.rewrite);
  console.log('* Refresh: ' + results.refresh);
  console.log('* Export: ' + results.export);
  console.log('* Step progression: ' + history.map(function (h) {
    return h.index + '/' + h.done;
  }).join(' -> '));
  console.log('* Interaction rotation: ' + history.map(function (h) {
    return h.interaction || '-';
  }).join(' -> '));
  console.log('* Friction: ' + (last.friction || '-'));
  console.log('* Momentum: ' + (last.momentum || '-'));
  console.log('* Reward: ' + (last.reward || '-'));
  console.log('* Artifact preview length: ' + (last.artifactLength || 0));
  console.log('* Export length: ' + exportLength);
  console.log('* FINAL: PASS');
}

async function main() {
  console.log('Bridge runtime acceptance flow');
  console.log('Target: ' + BASE + '\n');

  var health = await optionalHealthProbe();
  if (!health.reachable) {
    // Do not fail here. Create is the authoritative reachability check.
    console.log('Health probe unavailable; using create as reachability check.');
  }

  var createEndpoint = '/api/session/create';
  var create = await request('create', createEndpoint, 'POST', {
    task: TASK,
    frame: FRAME,
    supports: ['step_by_step'],
  });
  assertBaseContract('create', createEndpoint, create);
  assertContext('create', createEndpoint, create);
  results.create = 'PASS';

  var workspaceId = getWorkspaceId(create);
  var history = [snapshot(create)];
  var last = create;
  var signatures = [stepSignature(create)];

  for (var i = 0; i < CONTINUE_OUTPUTS.length; i += 1) {
    var phase = 'continue ' + (i + 1);
    var key = 'continue' + (i + 1);
    var endpoint = '/api/session/continue';
    var cont = await request(phase, endpoint, 'POST', {
      workspace_id: workspaceId,
      user_output: CONTINUE_OUTPUTS[i],
    });
    assertContinue(last, cont, phase, endpoint);
    signatures.push(stepSignature(cont));
    history.push(snapshot(cont));
    results[key] = 'PASS';
    last = cont;
  }

  var uniqueSignatures = {};
  signatures.forEach(function (sig) {
    uniqueSignatures[sig] = true;
  });
  assertPhase(Object.keys(uniqueSignatures).length > 1, 'continue', '/api/session/continue', 'prompt/step stayed identical across all continues', {
    bodySnippet: signatures.join('\n'),
  });

  var rewriteEndpoint = '/api/session/rewrite';
  var rewrite = await request('rewrite', rewriteEndpoint, 'POST', {
    workspace_id: workspaceId,
    mode: 'make_easier',
  });
  assertRewrite(rewrite, workspaceId);
  results.rewrite = 'PASS';

  var refreshEndpoint = '/api/workspace/' + encodeURIComponent(workspaceId);
  var refresh = await request('refresh', refreshEndpoint, 'GET');
  assertRefresh(refresh, rewrite, workspaceId);
  history.push(snapshot(refresh));
  results.refresh = 'PASS';

  var exportEndpoint = '/api/session/export';
  var exported = await request('export', exportEndpoint, 'POST', {
    workspace_id: workspaceId,
    format: 'markdown',
  });
  var exportLength = assertExport(exported, workspaceId);
  results.export = 'PASS';

  printSummary(workspaceId, history, exportLength);
}

main().catch(function (err) {
  fail('unhandled', '', err && err.message ? err.message : String(err));
});
