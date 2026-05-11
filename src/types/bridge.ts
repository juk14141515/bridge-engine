export type FrictionType =
  | "ambiguity"
  | "overwhelm"
  | "perfectionism"
  | "emotional_resistance"
  | "task_switch"
  | "memory_load"
  | "decision_fatigue"
  | "recovery_depletion";

export type AdaptiveState =
  | "start"
  | "overwhelmed"
  | "recovery"
  | "learning"
  | "focus"
  | "momentum";

export type ProofPreference = "one_sentence" | "screenshot_note" | "checkbox_done" | "short_log";

export type CoachTone = "calm" | "direct" | "gentle";

export type StimulationPreference = "low" | "medium";

export type PacingPreference = "tiny" | "steady";

export interface Profile {
  displayName?: string;
  interests: string[];
  motivationDrivers: string[];
  proofPreference: ProofPreference;
  pacingPreference: PacingPreference;
  stimulationPreference: StimulationPreference;
  coachTone: CoachTone;
}

export interface AccessibilityPrefs {
  reducedMotion: boolean;
  highReadability: boolean;
  lowStimulation: boolean;
  colorblindSafe: boolean;
}

export interface ProofItem {
  id: string;
  createdAt: number;
  stuckText: string;
  tinyAction: string;
  proofText: string;
}

export type EntryOutcome = "lighter" | "smaller" | "another";
export type BridgeFeedback = "helped" | "not_quite" | "too_much" | "different_angle";

export interface EntryMemoryItem {
  id: string;
  createdAt: number;
  frictionChoice: string;
  frictionType?: string;
  attentionPathway: string;
  pathway?: string;
  tinyAction: string;
  helpMode?: string;
  continuationLevel?: number;
  smallerLevel?: number;
  outcome: EntryOutcome;
}

export interface BridgeFeedbackItem {
  id: string;
  entryId?: string;
  frictionType: string;
  pathway: string;
  helpMode: string;
  bridgeText: string;
  tinyAction: string;
  feedback: BridgeFeedback;
  timestamp: number;
}

export interface BridgePlan {
  stuckText: string;
  interests: string[];
  frictionType: FrictionType;
  frictionLabel: string;
  frictionWhy: string;
  relevanceTitle: string;
  relevanceMapping: string;
  tinyAction: string;
  proofPrompt: string;
  adaptiveState: AdaptiveState;
}

