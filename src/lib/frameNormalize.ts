import { logSessionIssue } from './sessionDiagnostics';

/** Must match `bridge_core.completion_engine.SUPPORTED_FRAMES`. */
const RUNTIME_FRAME_IDS = new Set([
  'gaming',
  'music',
  'fitness',
  'investing',
  'systems',
  'creative',
  'relationship',
  'coding',
]);

const FRAME_ALIASES: Record<string, string> = {
  creativity: 'creative',
  creativeness: 'creative',
  general: 'gaming',
  movement: 'fitness',
  visual: 'creative',
  entrepreneurship: 'investing',
  logic: 'systems',
  surprise: 'gaming',
  __surprise__: 'gaming',
};

export function normalizeFrameForSession(frame: string | undefined): string {
  const raw = (frame || 'gaming').toLowerCase().trim();
  const aliased = FRAME_ALIASES[raw] ?? raw;
  if (!RUNTIME_FRAME_IDS.has(aliased)) {
    if (raw && raw !== 'gaming') {
      logSessionIssue('invalid_frame', { frame: raw, resolved: 'gaming' });
    }
    return 'gaming';
  }
  return aliased;
}
