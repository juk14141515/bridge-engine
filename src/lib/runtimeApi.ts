const API_BASE_URL = "http://127.0.0.1:6060";

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

export const runtimeApi = {
  baseUrl: API_BASE_URL,

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

export async function safeFetch<T>(path: string, init: RequestInit = {}): Promise<ApiResult<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
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

