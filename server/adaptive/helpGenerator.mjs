import { pathwayMap, rotatePathwayApproach } from "./interestMap.mjs";

export function generateHelp(input) {
  const {
    helpMode = "smaller",
    pathway = "systems",
    continuationLevel = 0,
    smallerLevel = 0,
    anotherIndex = 0,
    supportPreferences = {},
    memoryProfile = {},
  } = input;
  const map = pathwayMap(pathway);
  const shouldShrink = memoryProfile.defaultSmaller || supportPreferences.tooManyOptionsShutMeDown;

  if (helpMode === "recovery" || helpMode === "overwhelmed" || supportPreferences.lowFuel || supportPreferences.lowFuelSupport) {
    return {
      headline: "No task yet.",
      reassurance: "Reduce the surface first.",
      instruction: memoryProfile.recentSmaller ? "Close one thing. Then pause." : "Take one breath. Pick one corner.",
      nextChoices: [{ id: "recover", label: "One breath" }, { id: "smaller", label: "Smaller" }, { id: "done", label: "Enough" }],
    };
  }

  if (helpMode === "continue") {
    if (shouldShrink) {
      return generateHelp({ ...input, helpMode: "smaller", smallerLevel: Math.max(smallerLevel, 1), memoryProfile });
    }
    const instructions = [
      map.continue,
      "Do the next 30 seconds only. Then pause.",
      "Move one inch forward. No finishing.",
      "Keep contact with the task. That is enough.",
    ];
    return {
      headline: "Continue gently.",
      reassurance: "Same entry. One more inch.",
      instruction: styleInstruction(instructions[Math.min(Math.max(continuationLevel - 1, 0), instructions.length - 1)], supportPreferences),
      nextChoices: [{ id: "done", label: "One piece done" }, { id: "smaller", label: "Too much" }, { id: "another", label: "Another way" }],
    };
  }

  if (helpMode === "smaller") {
    const smallerInstructions = [
      "Only open the place it lives. Stop there.",
      "Only find the first visible edge. Stop there.",
      "Only touch one corner. No task yet.",
      "This is small enough. Just be near it.",
    ];
    return {
      headline: "Smaller works.",
      reassurance: "You do not need momentum yet.",
      instruction: styleInstruction(smallerInstructions[Math.min(Math.max(smallerLevel - 1, 0), smallerInstructions.length - 1)], supportPreferences),
      nextChoices: [{ id: "done", label: "I did that" }, { id: "smaller", label: "Even smaller" }, { id: "another", label: "Another way" }],
    };
  }

  if (helpMode === "another" || helpMode === "another_way") {
    const adjustedIndex = memoryProfile.rotateSooner ? anotherIndex + 1 : anotherIndex;
    return {
      headline: `Use ${pathway}.`,
      reassurance: "Enter through what already feels easier.",
      instruction: styleInstruction(rotatePathwayApproach(pathway, adjustedIndex), supportPreferences),
      nextChoices: [{ id: "continue", label: "Continue gently" }, { id: "smaller", label: "Smaller" }],
    };
  }

  if (helpMode === "start") {
    return {
      headline: "Find the first edge.",
      reassurance: "Do not solve it yet.",
      instruction: styleInstruction(map.tiny, supportPreferences),
      nextChoices: [{ id: "done", label: "I found it" }, { id: "smaller", label: "Smaller" }],
    };
  }

  return {
    headline: "The entry point is hidden.",
    reassurance: "That is different from not caring.",
    instruction: styleInstruction("We are only finding where the first edge begins.", supportPreferences),
    nextChoices: [{ id: "continue", label: "Show start" }, { id: "smaller", label: "Smaller" }],
  };
}

function styleInstruction(instruction, preferences) {
  const styles = preferences.learningStyle ?? [];
  if (preferences.readingTiring || preferences.readingIsTiring) return instruction.split(".")[0] + ".";
  if (styles.includes("visual")) return `Look for it. ${instruction}`;
  if (styles.includes("verbal")) return `Say it simply. ${instruction}`;
  if (styles.includes("examples")) return `Example: ${instruction}`;
  if (styles.includes("hands-on")) return `Use one physical action. ${instruction}`;
  if (styles.includes("step-by-step")) return `1. ${instruction}\n2. Stop there.`;
  return instruction;
}

