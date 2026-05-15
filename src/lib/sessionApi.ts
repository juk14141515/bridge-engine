export { normalizeFrameForSession } from './frameNormalize';

export type {
  CreateSessionPayload,
  ExportFormat,
  NormalizedRuntimeContract,
  RecentWorkspaceSummary,
  RewriteMode,
  RuntimeExportResult,
  RuntimeWorkspace,
} from './runtimeApi';

export {
  continueSession,
  createSession,
  exportSession,
  fetchJson,
  getRecentWorkspaces,
  getWorkspace,
  saveWorkspace,
  rewriteSession,
  ApiError,
  API_BASE,
} from './runtimeApi';

import {
  getRecentWorkspaces,
  getWorkspace,
  type NormalizedRuntimeContract,
} from './runtimeApi';

/** Back-compat alias for older pages */
export type WorkspaceEnvelope = NormalizedRuntimeContract & {
  workspace: NormalizedRuntimeContract['workspace'];
  session: NormalizedRuntimeContract['workspace'];
};

export const fetchWorkspace = getWorkspace;
export const fetchRecentWorkspaces = getRecentWorkspaces;
