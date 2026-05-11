export function scoreMemory(entries = [], feedback = []) {
  const pathwayCounts = new Map();
  const avoidedPathwayCounts = new Map();
  const helpModeCounts = new Map();
  let tooMuchCount = 0;
  let differentAngleCount = 0;
  const outcomeCounts = new Map();

  for (const entry of entries) {
    pathwayCounts.set(entry.attentionPathway, (pathwayCounts.get(entry.attentionPathway) ?? 0) + 1);
    outcomeCounts.set(entry.outcome, (outcomeCounts.get(entry.outcome) ?? 0) + 1);
  }

  for (const item of feedback) {
    if (item.feedback === "helped") {
      pathwayCounts.set(item.pathway, (pathwayCounts.get(item.pathway) ?? 0) + 2);
      helpModeCounts.set(item.helpMode, (helpModeCounts.get(item.helpMode) ?? 0) + 1);
    }
    if (item.feedback === "too_much") tooMuchCount += 1;
    if (item.feedback === "different_angle") {
      differentAngleCount += 1;
      avoidedPathwayCounts.set(item.pathway, (avoidedPathwayCounts.get(item.pathway) ?? 0) + 1);
    }
  }

  return {
    preferredPathways: [...pathwayCounts.entries()].sort((a, b) => b[1] - a[1]).map(([pathway]) => pathway),
    avoidedPathways: [...avoidedPathwayCounts.entries()].sort((a, b) => b[1] - a[1]).map(([pathway]) => pathway),
    effectiveHelpModes: [...helpModeCounts.entries()].sort((a, b) => b[1] - a[1]).map(([mode]) => mode),
    outcomes: Object.fromEntries(outcomeCounts),
    recentSmaller: entries.some((entry) => entry.outcome === "smaller"),
    defaultSmaller: tooMuchCount >= 2,
    rotateSooner: differentAngleCount >= 2,
    wordingDensity: tooMuchCount >= 2 ? "short" : "normal",
    lastOutcome: entries[0]?.outcome ?? null,
  };
}

