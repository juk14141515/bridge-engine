export type AttachmentInputKind = "photo" | "screenshot" | "voice";

export type FutureIntegrationStatus = {
  enabled: false;
  reason: "frontend-only-mvp";
};

export function photoOrScreenshotInput(): FutureIntegrationStatus {
  return { enabled: false, reason: "frontend-only-mvp" };
}

export function voiceInput(): FutureIntegrationStatus {
  return { enabled: false, reason: "frontend-only-mvp" };
}

export function aiGeneratedAdaptiveHelp(): FutureIntegrationStatus {
  return { enabled: false, reason: "frontend-only-mvp" };
}

export function personalizedLearningPaths(): FutureIntegrationStatus {
  return { enabled: false, reason: "frontend-only-mvp" };
}

