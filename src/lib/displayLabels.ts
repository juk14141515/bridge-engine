import { ALL_FRAMES, SUPPORT_CHIPS } from './onboardingOptions';
import { normalizeFrameForSession } from './sessionApi';
import { logSessionIssue } from './sessionDiagnostics';
import { ApiError } from './runtimeApi';

const ARTIFACT_SECTION_LABELS: Record<string, string> = {
  thesis_seed: 'Thesis',
  support_points: 'Main points',
  body_paragraph_seed: 'Draft section',
  draft_outline: 'Outline',
  first_concept: 'First concept',
  recall_prompt: 'Practice prompt',
  recall_attempt: 'Your attempt',
  summary: 'Summary',
  feeling_need: 'What you feel and need',
  opener: 'Opening line',
  boundary: 'Boundary',
  final_message: 'Final message',
  first_win: 'First win',
  zone_done: 'Zone cleared',
  friction_removed: 'Friction removed',
  completion_note: 'Progress note',
  first_checkpoint: 'First checkpoint',
  next_actions: 'Next actions',
  work_piece: 'Work piece',
  done_definition: 'Done for today',
};

const INTERNAL_ARTIFACT_KEYS = new Set([
  'not_found',
  'notfound',
  'undefined',
  'null',
  'error',
  'none',
  'missing',
  'n/a',
  'na',
]);

const INTERNAL_TASK_SNIPPETS = [
  'make progress on coding project',
  'coding project',
  'sample task',
  'placeholder',
  'demo task',
  'todo:',
];

export function resolveFrameId(frame: string | undefined | null): string {
  return normalizeFrameForSession(frame ?? undefined);
}

export function frameTitleSafe(frame: string | undefined | null): string {
  const raw = frame?.trim() ?? '';
  if (!raw) return 'Your interest';
  const id = resolveFrameId(raw);
  const known = ALL_FRAMES.find((f) => f.id === id);
  if (known) return known.title;
  if (id !== raw) {
    logSessionIssue('invalid_frame', { frame });
  }
  return raw;
}

export function frameEmojiSafe(frame: string | undefined | null): string {
  const id = resolveFrameId(frame);
  return ALL_FRAMES.find((f) => f.id === id)?.emoji ?? '✨';
}

export function frameBlurbSafe(frame: string | undefined | null): string {
  const id = resolveFrameId(frame);
  return ALL_FRAMES.find((f) => f.id === id)?.blurb ?? '';
}

export function supportTitleSafe(id: string | undefined | null): string {
  if (!id) return '';
  const known = SUPPORT_CHIPS.find((s) => s.id === id);
  if (known) return known.title;
  logSessionIssue('unknown_support', { support: id });
  return '';
}

export function isInternalArtifactKey(key: string): boolean {
  const k = key.trim().toLowerCase();
  return INTERNAL_ARTIFACT_KEYS.has(k) || k.startsWith('__');
}

export function artifactSectionLabel(key: string): string | null {
  if (isInternalArtifactKey(key)) {
    logSessionIssue('internal_artifact_key', { key });
    return null;
  }
  if (ARTIFACT_SECTION_LABELS[key]) return ARTIFACT_SECTION_LABELS[key];
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function sessionTaskLabel(
  task: string | undefined | null,
  title: string | undefined | null,
): string {
  const t = (task && task.trim()) || (title && title.trim()) || '';
  if (!t) return 'Your task';
  const lower = t.toLowerCase();
  if (INTERNAL_TASK_SNIPPETS.some((s) => lower.includes(s))) {
    logSessionIssue('missing_session_payload', { reason: 'prototype_task_text', task: t });
    return 'Your task';
  }
  return t;
}

export function sanitizeApiMessage(message: string, fallback: string): string {
  const m = message.trim().toLowerCase();
  if (!m) return fallback;
  if (m.includes('workspace not found') || m === 'not found') {
    return "Couldn't load this session.";
  }
  if (m.includes('step not found') || m.includes('path or step')) {
    return "This step couldn't be loaded. Try again.";
  }
  if (m.includes('task is required')) {
    return 'Please describe what you want to work on (a few words is enough).';
  }
  if (m.includes('network') || m.includes('failed to fetch')) {
    return "Couldn't reach the server. Check that Bridge is running, then try again.";
  }
  if (
    m.includes('undefined') ||
    m.includes('placeholder') ||
    m.includes('demo') ||
    m.includes('mock') ||
    m.includes('sample')
  ) {
    return fallback;
  }
  return message;
}

export function formatUserApiError(e: unknown, fallback: string): string {
  if (e instanceof ApiError) {
    if (e.status === 0) {
      return "Couldn't reach the server. Start Bridge on port 6060, then try again.";
    }
    return sanitizeApiMessage(e.message, fallback);
  }
  if (e instanceof Error) {
    return sanitizeApiMessage(e.message, fallback);
  }
  return fallback;
}
