import type { AdaptiveState, BridgePlan, FrictionType, Profile } from "../types/bridge";

type Classified = { type: FrictionType; label: string; why: string; state: AdaptiveState };

function normalize(s: string) {
  return s.trim().toLowerCase();
}

function includesAny(text: string, needles: string[]) {
  return needles.some((n) => text.includes(n));
}

function classifyFriction(stuckText: string): Classified {
  const t = normalize(stuckText);

  if (includesAny(t, ["too tired", "exhausted", "burnt out", "burned out", "sick", "drained"])) {
    return {
      type: "recovery_depletion",
      label: "Recovery depletion",
      why: "Your system is low on fuel. Starting is hard when energy is scarce.",
      state: "recovery",
    };
  }

  if (includesAny(t, ["too much", "overwhelmed", "overwhelm", "everything", "massive", "so many"])) {
    return {
      type: "overwhelm",
      label: "Overwhelm friction",
      why: "The scope feels too large to mentally enter.",
      state: "overwhelmed",
    };
  }

  if (includesAny(t, ["perfect", "perfectly", "mess up", "mess it up", "not good enough", "imposter"])) {
    return {
      type: "perfectionism",
      label: "Perfectionism friction",
      why: "The brain treats 'starting' like a high-stakes performance.",
      state: "focus",
    };
  }

  if (
    includesAny(t, [
      "avoid",
      "avoiding",
      "dread",
      "anxious",
      "anxiety",
      "scared",
      "feel bad",
      "shame",
      "guilt",
    ])
  ) {
    return {
      type: "emotional_resistance",
      label: "Emotional resistance",
      why: "There’s an emotional cost attached to the task right now.",
      state: "recovery",
    };
  }

  if (includesAny(t, ["switch", "context", "context switch", "can’t transition", "transition"])) {
    return {
      type: "task_switch",
      label: "Task-switch friction",
      why: "Transitions are harder than the work itself.",
      state: "focus",
    };
  }

  if (includesAny(t, ["can't remember", "can’t remember", "forget", "holding", "keep in mind"])) {
    return {
      type: "memory_load",
      label: "Memory-load friction",
      why: "Too much has to be held in working memory to start cleanly.",
      state: "learning",
    };
  }

  if (includesAny(t, ["which", "what should i", "what do i", "decide", "choice", "options"])) {
    return {
      type: "decision_fatigue",
      label: "Decision fatigue",
      why: "Too many micro-decisions block the first step.",
      state: "focus",
    };
  }

  if (t.length < 18 || includesAny(t, ["not sure", "unclear", "vague", "where to start", "start"])) {
    return {
      type: "ambiguity",
      label: "Ambiguity friction",
      why: "The next step isn’t mentally visible yet.",
      state: "learning",
    };
  }

  return {
    type: "ambiguity",
    label: "Ambiguity friction",
    why: "We’ll make the next step visible and smaller.",
    state: "learning",
  };
}

function pickPrimaryInterest(profile: Profile, chosen: string[]) {
  const list = chosen.length ? chosen : profile.interests;
  return list[0] ?? "something you care about";
}

function mapRelevance(interest: string, friction: FrictionType) {
  const base = `Use ${interest} as the entry ramp.`;
  const safe = "No whole plan.";

  const templates: Record<FrictionType, { title: string; body: string }> = {
    ambiguity: {
      title: "Make it legible",
      body: `Find the first visible edge. ${base} ${safe}`,
    },
    overwhelm: {
      title: "Shrink the scope",
      body: `Too much at once. Shrink the surface. ${base} ${safe}`,
    },
    perfectionism: {
      title: "Lower the stakes",
      body: `No quality yet. Just entry. ${base} ${safe}`,
    },
    emotional_resistance: {
      title: "Make it emotionally safe",
      body: `Approach from the side. ${base} ${safe}`,
    },
    task_switch: {
      title: "Create a bridge into the work",
      body: `Transitions need a ramp. ${base} ${safe}`,
    },
    memory_load: {
      title: "Offload the working memory",
      body: `Hold less in your head. ${base} ${safe}`,
    },
    decision_fatigue: {
      title: "Reduce decisions",
      body: `One choice is enough. ${base} ${safe}`,
    },
    recovery_depletion: {
      title: "Protect recovery",
      body: `Protect fuel. Keep the thread. ${base} ${safe}`,
    },
  };

  const chosen = templates[friction];
  return { title: chosen.title, body: chosen.body };
}

function tinyAction(friction: FrictionType, pacing: Profile["pacingPreference"]) {
  const tiny = pacing === "tiny";

  const actions: Record<FrictionType, string> = {
    ambiguity: tiny
      ? `Open the closest place this lives. Stop there.`
      : `Open it and point to the first unclear part.`,
    overwhelm: tiny ? `Pick one corner. Ignore the rest.` : `Choose the smallest visible piece and touch only that.`,
    perfectionism: tiny
      ? `Make one intentionally unfinished mark.`
      : `Create a rough placeholder. No polishing.`,
    emotional_resistance: tiny
      ? `Open it for ten seconds. You can close it after.`
      : `Open it and touch one safe part.`,
    task_switch: tiny
      ? `Put the next thing on screen.`
      : `Open, locate, pause. That is the ramp.`,
    memory_load: tiny
      ? `Move one thing out of your head.`
      : `Put the first thing somewhere visible.`,
    decision_fatigue: tiny
      ? `Choose the easiest option. Not the best one.`
      : `Pick one path for now. You can change later.`,
    recovery_depletion: tiny
      ? `Do one “keep the thread” touch.`
      : `Do the lowest-energy version that keeps contact.`,
  };

  return actions[friction];
}

function proofPrompt(profile: Profile) {
  switch (profile.proofPreference) {
    case "one_sentence":
      return "Better?";
    case "screenshot_note":
      return "Did it feel lighter?";
    case "checkbox_done":
      return "Still moving?";
    case "short_log":
      return "Want it smaller?";
    default:
      return "Better?";
  }
}

export function createBridgePlan(input: {
  stuckText: string;
  chosenInterests: string[];
  profile: Profile;
}): BridgePlan {
  const classified = classifyFriction(input.stuckText);
  const primary = pickPrimaryInterest(input.profile, input.chosenInterests);
  const rel = mapRelevance(primary, classified.type);
  const action = tinyAction(classified.type, input.profile.pacingPreference);

  return {
    stuckText: input.stuckText.trim(),
    interests: input.chosenInterests.length ? input.chosenInterests : input.profile.interests,
    frictionType: classified.type,
    frictionLabel: classified.label,
    frictionWhy: classified.why,
    relevanceTitle: rel.title,
    relevanceMapping: rel.body,
    tinyAction: action,
    proofPrompt: proofPrompt(input.profile),
    adaptiveState: classified.state,
  };
}

