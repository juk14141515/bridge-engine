// Runtime API client for Bridge Engine.
//
// All session/workspace calls go through `fetchJson`, which uses a relative
// `/api/...` path so the Vite dev proxy can forward to Flask
// (http://127.0.0.1:6060). For production hosting, set `VITE_API_BASE` to an
// absolute origin and the same paths will work.
//
// The legacy `runtimeApi` + `safeFetch` helpers remain so older pages (Lanes,
// NewTask) keep compiling. They hit deprecated routes that no longer exist in
// the new runtime; the user-facing flow lives on /home, /start, and
// /workspace/:id.

const ENV_BASE = ((import.meta as unknown as { env?: Record<string, string> }).env?.VITE_API_BASE ?? "").replace(/\/$/, "");

// Empty base means "use a relative URL" so the Vite proxy can forward it.
export const API_BASE = ENV_BASE;

export class ApiError extends Error {
  status: number;
  body?: unknown;

  constructor(message: string, status: number, body?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

export async function fetchJson<T = unknown>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const url = path.startsWith("http") ? path : `${API_BASE}${path}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((init.headers as Record<string, string>) ?? {}),
  };

  let response: Response;
  try {
    response = await fetch(url, { ...init, headers });
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "Network error contacting Bridge runtime.";
    throw new ApiError(message, 0);
  }

  const text = await response.text();
  let body: unknown = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }

  if (!response.ok) {
    const message =
      (body && typeof body === "object" && "error" in body && typeof (body as { error: unknown }).error === "string"
        ? (body as { error: string }).error
        : null) ?? response.statusText ?? `Request failed (${response.status})`;
    throw new ApiError(message, response.status, body);
  }

  return (body ?? ({} as unknown)) as T;
}

// ---------------------------------------------------------------------------
// Legacy helpers kept for backwards compatibility with older pages
// (LanesPage, NewTaskPage). The new runtime lives in `sessionApi.ts`.
// ---------------------------------------------------------------------------

const LEGACY_BASE_URL = ENV_BASE || "http://127.0.0.1:6060";

export type ApiResult<T> =
  | { ok: true; data: T; error: null }
  | { ok: false; data: null; error: string };

export type RuntimeLane = {
  workflow_id: string;
  title: string;
  status: string;
  recommended_mode?: string;
  momentum_score?: number;
  progress_confidence?: number;
  [key: string]: unknown;
};

export type RuntimeStep = {
  workflow_id?: string;
  status?: string;
  current_objective?: string;
  objective?: string;
  current_step?: string;
  step?: string;
  why_this_matters?: string;
  why?: string;
  interaction_type?: string;
  progress_confidence?: number;
  momentum_score?: number;
  [key: string]: unknown;
};

export type NewTaskPayload = {
  content: string;
  interest_frame: string;
  custom_interest?: string;
  cognitive_mode?: string;
};

export async function safeFetch<T>(path: string, init: RequestInit = {}): Promise<ApiResult<T>> {
  try {
    const response = await fetch(`${LEGACY_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init.headers,
      },
    });

    if (!response.ok) {
      return { ok: false, data: null, error: `Backend responded ${response.status}` };
    }

    const text = await response.text();
    const data = text ? (JSON.parse(text) as T) : ({} as T);
    return { ok: true, data, error: null };
  } catch {
    return { ok: false, data: null, error: "Backend unavailable" };
  }
}

export const runtimeApi = {
  baseUrl: LEGACY_BASE_URL,

  getLanes() {
    return safeFetch<{ lanes?: RuntimeLane[] } | RuntimeLane[]>("/api/lanes");
  },

  createTask(payload: NewTaskPayload) {
    return safeFetch<RuntimeLane | { lane?: RuntimeLane; workflow_id?: string }>("/api/tasks", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  getNext(workflowId: string) {
    return safeFetch<RuntimeStep>(`/api/runtime/next?workflow_id=${encodeURIComponent(workflowId)}`);
  },

  sendFeedback(workflowId: string, feedback: string, step?: RuntimeStep) {
    return safeFetch<RuntimeStep | { ok: boolean }>("/api/runtime/feedback", {
      method: "POST",
      body: JSON.stringify({ workflow_id: workflowId, feedback, step }),
    });
  },

  submitProof(workflowId: string, proof_text: string) {
    return safeFetch<RuntimeStep | { ok: boolean }>("/api/runtime/proof", {
      method: "POST",
      body: JSON.stringify({ workflow_id: workflowId, proof_text }),
    });
  },

  exportWorkflow(workflowId: string, format: string) {
    return safeFetch<{ content?: string; url?: string; format?: string }>(
      `/api/export/${encodeURIComponent(workflowId)}?format=${encodeURIComponent(format)}`,
    );
  },
};
