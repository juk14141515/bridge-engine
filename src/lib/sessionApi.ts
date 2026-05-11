import { fetchJson } from './runtimeApi';

/** Maps onboarding / interest ids to `completion_engine.SUPPORTED_FRAMES` keys. */
export function normalizeFrameForSession(frame: string | undefined): string {
  const f = (frame || 'gaming').toLowerCase().trim();
  if (f === 'creativity') return 'creative';
  if (f === 'general') return 'gaming';
  return f;
}

export interface RuntimeStepPayload {
  id: string;
  title: string;
  prompt?: string;
  why?: string;
  action?: string;
  output_slot?: string;
  status?: string;
  user_output?: string;
  help_variants?: Record<string, string>;
}

export interface RuntimeStatePayload {
  mode?: string;
  status?: string;
  rewrite_count?: number;
  current_step_index?: number;
  completion_rate?: number;
  momentum_state?: string;
  momentum_label?: string;
  friction_level?: string;
}

export interface IntelligencePayload {
  completion_rate?: number;
  average_output_size?: number;
  state?: string;
  recommendation?: string;
}

export interface NextPromptPayload {
  type?: string;
  title?: string;
  prompt?: string;
  message?: string;
  remaining?: number;
  current_output?: string;
  generated_at?: string;
}

export interface WorkspaceEnvelope {
  ok: boolean;
  workspace: Record<string, unknown> & {
    id: string;
    task?: string;
    title?: string;
    frame?: string;
    supports?: string[];
    status?: string;
    current_step_index?: number;
    steps?: RuntimeStepPayload[];
    artifact?: Record<string, unknown>;
    events?: unknown[];
  };
  session: WorkspaceEnvelope['workspace'];
  runtime_state: RuntimeStatePayload;
  intelligence: IntelligencePayload;
  next_prompt: NextPromptPayload;
  artifact_preview: Record<string, unknown>;
  memory_summary: Record<string, unknown>;
  rewrite_options: string[];
  current_step: RuntimeStepPayload | null;
  progress: { done: number; total: number; percent: number };
}

export interface RecentWorkspaceSummary {
  id: string;
  title?: string;
  task?: string;
  frame?: string;
  status?: string;
  current_step_index?: number;
  updated_at?: string;
  progress_done?: number;
  progress_total?: number;
}

export async function createSession(body: {
  task: string;
  frame?: string;
  supports?: string[];
  category?: string;
  user_words?: string;
}): Promise<WorkspaceEnvelope> {
  const frame = normalizeFrameForSession(body.frame);
  return fetchJson<WorkspaceEnvelope>('/api/session/create', {
    method: 'POST',
    body: JSON.stringify({ ...body, frame }),
  });
}

export async function continueSession(body: {
  workspace_id: string;
  output?: string;
  user_output?: string;
}): Promise<WorkspaceEnvelope> {
  return fetchJson<WorkspaceEnvelope>('/api/session/continue', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function rewriteSession(body: {
  workspace_id: string;
  mode: string;
  frame?: string;
}): Promise<WorkspaceEnvelope> {
  const frame = normalizeFrameForSession(body.frame);
  return fetchJson<WorkspaceEnvelope>('/api/session/rewrite', {
    method: 'POST',
    body: JSON.stringify({ ...body, frame }),
  });
}

export async function exportSession(body: { workspace_id: string }): Promise<{
  ok: boolean;
  format: string;
  markdown: string;
  plain_text: string;
  title?: string;
}> {
  return fetchJson('/api/session/export', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function fetchWorkspace(workspaceId: string): Promise<WorkspaceEnvelope> {
  return fetchJson<WorkspaceEnvelope>(`/api/workspace/${encodeURIComponent(workspaceId)}`);
}

export async function fetchRecentWorkspaces(limit = 20): Promise<{
  ok: boolean;
  workspaces: RecentWorkspaceSummary[];
}> {
  return fetchJson(`/api/workspaces/recent?limit=${limit}`);
}

export async function saveWorkspace(workspace: Record<string, unknown>): Promise<WorkspaceEnvelope> {
  return fetchJson<WorkspaceEnvelope>('/api/workspace/save', {
    method: 'POST',
    body: JSON.stringify({ workspace }),
  });
}
