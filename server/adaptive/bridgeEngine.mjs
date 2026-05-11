import { pathwayMap } from "./interestMap.mjs";
import { scoreMemory } from "./memoryScorer.mjs";
import { generateHelp } from "./helpGenerator.mjs";

export function createBridgePlan(input) {
  const stuckText = String(input.stuckText ?? "It feels hard to enter.");
  const pathway = String(input.pathway ?? input.chosenInterests?.[0] ?? "systems");
  const frictionType = classifyFriction(stuckText);
  const map = pathwayMap(pathway);
  const supportPreferences = input.supportPreferences ?? {};
  const memoryProfile = scoreMemory(input.entryMemory ?? [], input.feedback ?? []);
  const forceSmaller = memoryProfile.defaultSmaller;

  return {
    stuckText,
    interests: [pathway],
    frictionType,
    frictionLabel: labelFriction(frictionType),
    frictionWhy: "Just enough to enter.",
    relevanceTitle: "Entry ramp",
    relevanceMapping: soften(`${map.frame}`, supportPreferences, memoryProfile),
    tinyAction: firstStep({ frictionType, pathway, supportPreferences, forceSmaller }),
    proofPrompt: "Better?",
    adaptiveState: frictionType === "overwhelm" ? "overwhelmed" : "focus",
  };
}

export function createAdaptiveHelp(input) {
  const memoryProfile = scoreMemory(input.entryMemory ?? [], input.feedback ?? []);
  return generateHelp({ ...input, memoryProfile });
}

export function createAdaptiveProfile({ intake = {}, entryMemory = [], feedback = [] }) {
  const memoryProfile = scoreMemory(entryMemory, feedback);
  return {
    supportPreferences: intake,
    memoryProfile,
    suggestedPathway: memoryProfile.preferredPathways[0] ?? "systems",
    suggestedLoad: intake.lowFuelSupport || intake.readingIsTiring ? "low" : "standard",
  };
}

function firstStep({ frictionType, pathway, supportPreferences, forceSmaller }) {
  const map = pathwayMap(pathway);
  if (forceSmaller) return "Only open the place it lives. Stop there.";
  if (supportPreferences.lowFuel || supportPreferences.lowFuelSupport || frictionType === "recovery_depletion") {
    return "Do one keep-the-thread touch.";
  }
  if (supportPreferences.tooManyOptionsShutMeDown) return "Pick one corner. Ignore the rest.";
  if (frictionType === "overwhelm") return `${map.tiny} Ignore the rest.`;
  if (supportPreferences.brainJumpsTracks) return "Put the next thing on screen.";
  return map.tiny;
}

function classifyFriction(text) {
  const t = text.toLowerCase();
  if (t.includes("too much") || t.includes("overwhelm")) return "overwhelm";
  if (t.includes("avoid")) return "emotional_resistance";
  if (t.includes("focus") || t.includes("drift")) return "task_switch";
  if (t.includes("fuel") || t.includes("tired") || t.includes("burnout")) return "recovery_depletion";
  return "ambiguity";
}

function labelFriction(friction) {
  return String(friction).replace(/_/g, " ");
}

function soften(text, preferences, memoryProfile = {}) {
  if (memoryProfile.wordingDensity === "short" || preferences.readingTiring || preferences.readingIsTiring) return text.split(".")[0] + ".";
  if (preferences.emotionallyHeavy || preferences.taskFeelsEmotionallyHeavy) return `${text} Softly.`;
  return text;
}

