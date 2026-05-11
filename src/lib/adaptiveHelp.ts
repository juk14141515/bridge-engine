import type { EntryMemoryItem, FrictionType } from "../types/bridge";

export type HelpMode =
  | "continue"
  | "smaller"
  | "start"
  | "explain"
  | "walkthrough"
  | "overwhelmed"
  | "recovery"
  | "done"
  | "another"
  | "another_way";

export type AdaptiveHelpInput = {
  frictionType: FrictionType;
  pathway: string;
  taskText: string;
  helpMode: HelpMode;
  entryMemory: EntryMemoryItem[];
  continuationLevel?: number;
  smallerLevel?: number;
  anotherIndex?: number;
  supportPreferences?: unknown;
  feedback?: unknown;
};

export type AdaptiveHelpResult = {
  headline: string;
  reassurance: string;
  instruction: string;
  nextChoices: Array<{
    id: "continue" | "smaller" | "done" | "another" | "recover";
    label: string;
  }>;
};

export function createAdaptiveHelp(input: AdaptiveHelpInput): AdaptiveHelpResult {
  const pathway = input.pathway || "what already pulls attention";
  const recentSmaller = input.entryMemory.some((entry) => entry.outcome === "smaller");
  const continuationLevel = input.continuationLevel ?? 0;
  const smallerLevel = input.smallerLevel ?? 0;
  const anotherIndex = input.anotherIndex ?? 0;

  if (input.helpMode === "continue") {
    const instructions = [
      "Stay where you are. Touch the next visible piece. Stop before it gets heavy.",
      "Do the next 30 seconds only. Then pause.",
      "Move one inch forward. No finishing.",
      "Keep contact with the task. That is enough.",
    ];
    return {
      headline: "Continue gently.",
      reassurance: "Same entry. One more inch.",
      instruction: instructions[Math.min(continuationLevel - 1, instructions.length - 1)],
      nextChoices: [
        { id: "done", label: "One piece done" },
        { id: "smaller", label: "Too much" },
        { id: "another", label: "Another way" },
      ],
    };
  }

  if (input.helpMode === "done") {
    return {
      headline: "That counts.",
      reassurance: "One piece is real movement.",
      instruction: "Stay soft. You can continue, stop, or start another bridge.",
      nextChoices: [
        { id: "continue", label: "Continue gently" },
        { id: "another", label: "Start another" },
      ],
    };
  }

  if (input.helpMode === "overwhelmed" || input.helpMode === "recovery") {
    return {
      headline: "No task yet.",
      reassurance: "Reduce the surface first.",
      instruction: recentSmaller ? "Close one thing. Then pause." : "Take one breath. Pick one corner.",
      nextChoices: [
        { id: "recover", label: "One breath" },
        { id: "smaller", label: "Smaller" },
        { id: "done", label: "Enough" },
      ],
    };
  }

  if (input.helpMode === "smaller") {
    const smallerInstructions = [
      "Only open the place it lives. Stop there.",
      "Only find the first visible edge. Stop there.",
      "Only touch one corner. No task yet.",
      "This is small enough. Just be near it.",
    ];
    return {
      headline: "Smaller works.",
      reassurance: "You do not need momentum yet.",
      instruction: smallerInstructions[Math.min(Math.max(smallerLevel - 1, 0), smallerInstructions.length - 1)],
      nextChoices: [
        { id: "done", label: "I did that" },
        { id: "smaller", label: "Even smaller" },
        { id: "another", label: "Another way" },
      ],
    };
  }

  if (input.helpMode === "start") {
    return {
      headline: "Find the first edge.",
      reassurance: "Do not solve it yet.",
      instruction: "Go to the first page, tab, file, or message where this lives.",
      nextChoices: [
        { id: "done", label: "I found it" },
        { id: "smaller", label: "Smaller" },
      ],
    };
  }

  if (input.helpMode === "walkthrough") {
    return {
      headline: "Continue gently.",
      reassurance: "Same entry. One more inch.",
      instruction: "1. Stay where you are.\n2. Touch the next visible piece.\n3. Stop before it gets heavy.",
      nextChoices: [
        { id: "done", label: "One piece done" },
        { id: "smaller", label: "Too much" },
        { id: "another", label: "Another way" },
      ],
    };
  }

  if (input.helpMode === "another" || input.helpMode === "another_way") {
    const approaches = [
      "Treat this like a tiny pattern to notice, not a task to finish.",
      "Enter through the easiest sensory cue: open, look, pause.",
      "Pretend you are only scouting the terrain.",
      "Use the part that feels least resistant and begin there.",
    ];
    return {
      headline: `Use ${pathway}.`,
      reassurance: "Enter through what already feels easier.",
      instruction: approaches[Math.min(Math.max(anotherIndex - 1, 0), approaches.length - 1)],
      nextChoices: [
        { id: "continue", label: "Continue gently" },
        { id: "smaller", label: "Smaller" },
      ],
    };
  }

  return {
    headline: "The entry point is hidden.",
    reassurance: "That is different from not caring.",
    instruction: "We are only finding where the first edge begins.",
    nextChoices: [
      { id: "continue", label: "Show start" },
      { id: "smaller", label: "Smaller" },
    ],
  };
}

