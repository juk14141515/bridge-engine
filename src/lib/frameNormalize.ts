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
  general: 'general',
  movement: 'fitness',
  visual: 'creative',
  entrepreneurship: 'investing',
  logic: 'systems',
  surprise: '',
  __surprise__: '',
};

export function normalizeFrameForSession(frame: string | undefined): string {
  const raw = (frame || '').trim();
  if (!raw) return '';
  const normalizedRaw = raw.toLowerCase();
  const aliased = FRAME_ALIASES[normalizedRaw] ?? normalizedRaw;
  if (!aliased) return '';
  if (!RUNTIME_FRAME_IDS.has(aliased)) {
    logSessionIssue('invalid_frame', { frame: raw, resolved: raw });
    return raw;
  }
  return aliased;
}
