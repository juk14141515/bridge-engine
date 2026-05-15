/** Dev-visible logging for session data issues (no user-facing strings). */

export type SessionDiagnosticCode =
  | 'missing_frame'
  | 'invalid_frame'
  | 'invalid_category'
  | 'missing_session_payload'
  | 'hydration_mismatch'
  | 'unknown_support'
  | 'internal_artifact_key';

export function logSessionIssue(code: SessionDiagnosticCode, details: Record<string, unknown>): void {
  console.warn(`[Bridge] ${code}`, details);
}
