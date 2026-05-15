import type { NormalizedRuntimeContract } from './runtimeContract';

/** Ignore stale GET responses when continue/rewrite finished later. */
export function createLoadGeneration(): { next: () => number; isCurrent: (n: number) => boolean } {
  let seq = 0;
  return {
    next: () => ++seq,
    isCurrent: (n: number) => n === seq,
  };
}

function mergeRecordStrings(
  prev: Record<string, unknown>,
  next: Record<string, unknown>,
): Record<string, unknown> {
  const out = { ...prev };
  for (const [key, value] of Object.entries(next)) {
    const nextStr = String(value ?? '').trim();
    const prevStr = String(out[key] ?? '').trim();
    if (nextStr.length > 0) out[key] = value;
    else if (prevStr.length > 0) out[key] = out[key];
    else out[key] = value;
  }
  return out;
}

/** Preserve artifact sections when a race returns a thinner payload. */
export function mergeRuntimeContracts(
  prev: NormalizedRuntimeContract | null,
  next: NormalizedRuntimeContract,
): NormalizedRuntimeContract {
  if (!prev || prev.workspace.id !== next.workspace.id) return next;

  const prevSections = (prev.workspace.artifact as { sections?: Record<string, unknown> } | undefined)
    ?.sections;
  const nextSections = (next.workspace.artifact as { sections?: Record<string, unknown> } | undefined)
    ?.sections;
  const mergedSections =
    prevSections || nextSections
      ? mergeRecordStrings(prevSections ?? {}, nextSections ?? {})
      : undefined;

  const prevPreviewSections = (prev.artifactPreview.sections ?? {}) as Record<string, unknown>;
  const nextPreviewSections = (next.artifactPreview.sections ?? {}) as Record<string, unknown>;

  return {
    ...next,
    workspace: {
      ...next.workspace,
      artifact: mergedSections
        ? { ...(next.workspace.artifact as object), sections: mergedSections }
        : next.workspace.artifact,
    },
    artifactPreview: {
      ...next.artifactPreview,
      sections: mergeRecordStrings(prevPreviewSections, nextPreviewSections),
    },
  };
}
