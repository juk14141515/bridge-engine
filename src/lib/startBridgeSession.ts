import { createSession, type NormalizedRuntimeContract } from './runtimeApi';
import { frameBlurb, frameEmoji, frameTitle } from './onboardingOptions';
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
  interests?: string[];
  supports?: string[];
}): Promise<{
  workspaceId: string;
  ribbon: EntryRibbonState;
  resolvedFrame: string;
  initialContract: NormalizedRuntimeContract;
}> {
  const trimmed = params.task.trim();
  if (trimmed.length < 1) {
    throw new Error('Task is too short');
  }
  const resolvedFrame = params.frame?.trim() ?? '';
  if (!resolvedFrame) {
    throw new Error('Personal interest is required');
  }
  const supports = params.supports?.length ? params.supports : ['step_by_step'];
  const interests = params.interests?.length ? params.interests : [resolvedFrame];
  const contract = await createSession({
    task: trimmed,
    frame: resolvedFrame,
    interests,
    supports,
    user_words: trimmed,
  });
  const workspaceId = contract.workspace?.id;
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
  return { workspaceId, ribbon, resolvedFrame, initialContract: contract };
}
