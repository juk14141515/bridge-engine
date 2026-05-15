import { createSession, normalizeFrameForSession } from './sessionApi';
import {
  frameBlurb,
  frameEmoji,
  frameTitle,
  pickSurpriseFrame,
  SURPRISE_FRAME_ID,
} from './onboardingOptions';
import { logSessionIssue } from './sessionDiagnostics';

export interface EntryRibbonState {
  task: string;
  frameTitle: string;
  frameEmoji: string;
  frameBlurb: string;
}

export async function openBridgeSession(params: {
  task: string;
  frame: string | null;
  supports?: string[];
}): Promise<{ workspaceId: string; ribbon: EntryRibbonState; resolvedFrame: string }> {
  const trimmed = params.task.trim();
  if (trimmed.length < 3) {
    throw new Error('Task is too short');
  }
  const picked =
    !params.frame || params.frame === SURPRISE_FRAME_ID ? pickSurpriseFrame() : params.frame;
  const resolvedFrame = normalizeFrameForSession(picked);
  const supports = params.supports?.length ? params.supports : ['step_by_step'];
  const envelope = await createSession({
    task: trimmed,
    frame: resolvedFrame,
    supports,
    user_words: trimmed,
  });
  const workspaceId = envelope?.workspace?.id;
  if (!workspaceId) {
    logSessionIssue('missing_session_payload', { phase: 'create', task: trimmed });
    throw new Error('Session could not be created. Try again.');
  }
  const ribbon: EntryRibbonState = {
    task: trimmed,
    frameTitle: frameTitle(resolvedFrame),
    frameEmoji: frameEmoji(resolvedFrame),
    frameBlurb: frameBlurb(resolvedFrame),
  };
  return { workspaceId, ribbon, resolvedFrame };
}
