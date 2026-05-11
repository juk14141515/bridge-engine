import type { BridgeFeedbackItem, EntryMemoryItem } from "../types/bridge";
import type { AdaptiveHelpInput, AdaptiveHelpResult } from "./adaptiveHelp";
import type { NewEntryMemoryItem } from "./entryMemoryService";

const TOKEN_KEY = "bridge.authToken.v1";

export type AuthUser = {
  id: string;
  email: string;
  createdAt: number;
};

export type IntakePreferences = {
  startingFeelsHeavierThanDoing: boolean;
  tooManyOptionsShutMeDown: boolean;
  brainJumpsTracks: boolean;
  readingIsTiring: boolean;
  taskFeelsEmotionallyHeavy: boolean;
  lowFuelSupport: boolean;
  dyslexiaFriendlyReadability: boolean;
  adhdStyleFrictionSupport: boolean;
  depressionLowEnergySupport: boolean;
  learningStyle: string[];
};

export const apiClient = {
  token() {
    return localStorage.getItem(TOKEN_KEY);
  },

  hasSession() {
    return Boolean(this.token());
  },

  setToken(token: string) {
    localStorage.setItem(TOKEN_KEY, token);
  },

  clearToken() {
    localStorage.removeItem(TOKEN_KEY);
  },

  async signup(email: string, password: string) {
    const data = await request<{ token: string; user: AuthUser }>("/api/auth/signup", {
      method: "POST",
      body: { email, password },
    });
    this.setToken(data.token);
    return data;
  },

  async login(email: string, password: string) {
    const data = await request<{ token: string; user: AuthUser }>("/api/auth/login", {
      method: "POST",
      body: { email, password },
    });
    this.setToken(data.token);
    return data;
  },

  me() {
    return request<{ user: AuthUser }>("/api/me", { auth: true });
  },

  getIntake() {
    return request<{ intake: IntakePreferences }>("/api/intake", { auth: true });
  },

  saveIntake(intake: IntakePreferences) {
    return request<{ intake: IntakePreferences }>("/api/intake", {
      method: "POST",
      auth: true,
      body: { intake },
    });
  },

  getEntryMemory() {
    return request<{ entries: EntryMemoryItem[] }>("/api/entry-memory", { auth: true });
  },

  saveEntryMemory(entry: NewEntryMemoryItem) {
    return request<{ entry: EntryMemoryItem; entries: EntryMemoryItem[] }>("/api/entry-memory", {
      method: "POST",
      auth: true,
      body: { entry },
    });
  },

  bridgeOutcome(entry: NewEntryMemoryItem) {
    return request<{ entry: EntryMemoryItem; entries: EntryMemoryItem[] }>("/api/bridge-outcome", {
      method: "POST",
      auth: true,
      body: { entry, outcome: entry.outcome },
    });
  },

  adaptiveHelp(input: AdaptiveHelpInput) {
    return request<{ help: AdaptiveHelpResult }>("/api/adaptive-help", {
      method: "POST",
      auth: this.hasSession(),
      body: input,
    });
  },

  bridgePlan(input: unknown) {
    return request<{ plan: unknown }>("/api/bridge-plan", {
      method: "POST",
      auth: this.hasSession(),
      body: input,
    });
  },

  adaptiveProfile() {
    return request<{ adaptiveProfile: unknown }>("/api/adaptive-profile", { auth: true });
  },

  bridgeFeedback(feedback: Omit<BridgeFeedbackItem, "id">) {
    return request<{ feedback: BridgeFeedbackItem; adaptiveProfile?: unknown }>("/api/bridge-feedback", {
      method: "POST",
      auth: this.hasSession(),
      body: feedback,
    });
  },
};

async function request<T>(
  path: string,
  options: { method?: "GET" | "POST"; body?: unknown; auth?: boolean } = {},
): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (options.auth) {
    const token = apiClient.token();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(path, {
    method: options.method ?? "GET",
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}

