// Frame and support catalogs surfaced in the Start / Home flows.
// Frame IDs map 1:1 to `bridge_core.completion_engine.SUPPORTED_FRAMES`.
// Support IDs map 1:1 to `bridge_core.completion_engine.SUPPORT_MODIFIERS`
// so the backend can honor each modifier directly.

import { normalizeFrameForSession } from './frameNormalize';
import { logSessionIssue } from './sessionDiagnostics';

export interface FrameChip {
  id: string;
  title: string;
  /** Short translator phrase used inline. */
  blurb: string;
  /** Tiny one-line example shown only in the marketing surfaces. */
  example: string;
  emoji: string;
}

/** Five primary frames + 'surprise me'. Keep this list short for fast entry. */
export const FRAME_CHIPS: ReadonlyArray<FrameChip> = [
  {
    id: 'gaming',
    title: 'Gaming',
    blurb: 'Quests, XP, boss fights.',
    example: 'Essay → quest with a boss-fight outline.',
    emoji: '🎮',
  },
  {
    id: 'music',
    title: 'Music',
    blurb: 'Measure by measure.',
    example: 'Spanish → one phrase, layered into a verse.',
    emoji: '🎧',
  },
  {
    id: 'fitness',
    title: 'Fitness',
    blurb: 'Warmup, reps, cooldown.',
    example: 'Studying → warmup recall, heavier sets.',
    emoji: '💪',
  },
  {
    id: 'investing',
    title: 'Investing',
    blurb: 'Thesis, evidence, decision.',
    example: 'Strategy memo → thesis, evidence, call.',
    emoji: '📈',
  },
  {
    id: 'systems',
    title: 'Systems',
    blurb: 'Inputs, outputs, loops.',
    example: 'Project → map inputs, run the loop.',
    emoji: '🧠',
  },
];

/** Surprise me picks at random from the five. */
export const SURPRISE_FRAME_ID = '__surprise__';

/** Extended frames available behind "More frames" inside customize. */
export const EXTRA_FRAMES: ReadonlyArray<FrameChip> = [
  {
    id: 'creative',
    title: 'Creative / film',
    blurb: 'Drafts, polish, final cut.',
    example: 'Anything → messy first draft, then shape.',
    emoji: '🎬',
  },
  {
    id: 'relationship',
    title: 'Care',
    blurb: 'Clarity, safe lines.',
    example: 'Hard convo → name signal, draft safe line.',
    emoji: '🤝',
  },
  {
    id: 'coding',
    title: 'Building software',
    blurb: 'Ship small, debug, iterate.',
    example: 'Anything → tiny commits, useful increments.',
    emoji: '⚙️',
  },
];

export const ALL_FRAMES: ReadonlyArray<FrameChip> = [...FRAME_CHIPS, ...EXTRA_FRAMES];

export interface SupportChip {
  id: string;
  title: string;
  desc: string;
  emoji: string;
}

/** IDs match keys in bridge_core.completion_engine.SUPPORT_MODIFIERS. */
export const SUPPORT_CHIPS: ReadonlyArray<SupportChip> = [
  {
    id: 'step_by_step',
    title: 'One step at a time',
    desc: 'Linear, numbered moves.',
    emoji: '🪜',
  },
  {
    id: 'adhd',
    title: 'ADHD-friendly',
    desc: 'Tiny moves, fewer choices.',
    emoji: '🎯',
  },
  {
    id: 'low_energy',
    title: 'Low energy',
    desc: 'Small enough to start tired.',
    emoji: '🌙',
  },
  {
    id: 'anxiety',
    title: 'Lower pressure',
    desc: 'No shame. Messy is fine.',
    emoji: '🫧',
  },
  {
    id: 'examples_first',
    title: 'Show me an example',
    desc: 'One example before I try.',
    emoji: '🧪',
  },
  {
    id: 'visual_first',
    title: 'Visual first',
    desc: 'Boxes, labels, spatial.',
    emoji: '🗺️',
  },
  {
    id: 'dyslexia',
    title: 'Dyslexia-friendly',
    desc: 'Short lines, simple words.',
    emoji: '🔤',
  },
  {
    id: 'professional',
    title: 'Professional mode',
    desc: 'Concise, direct, decision-led.',
    emoji: '🧭',
  },
];

export function frameTitle(id: string | undefined | null): string {
  if (!id?.trim()) return '';
  const resolved = normalizeFrameForSession(id);
  const chip = ALL_FRAMES.find((f) => f.id === resolved);
  if (!chip && id.trim()) {
    logSessionIssue('invalid_frame', { frame: id, resolved });
  }
  return chip?.title ?? 'Your style';
}

export function frameBlurb(id: string | undefined | null): string {
  if (!id?.trim()) return '';
  const resolved = normalizeFrameForSession(id);
  return ALL_FRAMES.find((f) => f.id === resolved)?.blurb ?? '';
}

export function frameEmoji(id: string | undefined | null): string {
  if (!id?.trim()) return '';
  const resolved = normalizeFrameForSession(id);
  return ALL_FRAMES.find((f) => f.id === resolved)?.emoji ?? '✨';
}

export function supportTitle(id: string | undefined | null): string {
  if (!id?.trim()) return '';
  const chip = SUPPORT_CHIPS.find((s) => s.id === id);
  if (!chip) {
    logSessionIssue('unknown_support', { support: id });
    return '';
  }
  return chip.title;
}

export function isProfessionalMode(supports: ReadonlyArray<string> | undefined | null): boolean {
  if (!supports) return false;
  return supports.includes('professional');
}

export function pickSurpriseFrame(): string {
  const idx = Math.floor(Math.random() * FRAME_CHIPS.length);
  return FRAME_CHIPS[idx]?.id ?? 'gaming';
}

/** One line shown under the input as “how it will feel” in that frame. */
export function frameTranslationPreview(frameId: string | undefined | null): string {
  if (!frameId || frameId === SURPRISE_FRAME_ID) return '';
  const map: Record<string, string> = {
    gaming: 'Boss-battle pacing, XP checkpoints, one obvious next move.',
    music: 'Measures and layers—repeatable practice, then a performance pass.',
    fitness: 'Warmup, working sets, cooldown—progress without burning out.',
    investing: 'Thesis, evidence, risk, decision—turn fog into a memo you can ship.',
    systems: 'Inputs, outputs, bottlenecks—turn chaos into a loop you can run.',
    creative: 'Rough cut, shape, polish—permission to be messy first.',
    relationship: 'Signal, safe line, boundary—care without spiraling.',
    coding: 'Small slices, tight loops—ship something useful early.',
  };
  return map[frameId] ?? ALL_FRAMES.find((f) => f.id === frameId)?.example ?? '';
}

export interface QuickStartPreset {
  id: string;
  /** Short label on the tile */
  label: string;
  /** Full task sent to the runtime */
  task: string;
  frame: string;
}

/** One tap = start a real session (no typing). */
export const QUICK_START_PRESETS: ReadonlyArray<QuickStartPreset> = [
  { id: 'essay', label: 'Essay / paper', task: 'Finish the English essay I keep avoiding', frame: 'gaming' },
  { id: 'spanish', label: 'Learn Spanish', task: 'Learn Spanish in a way I can stick with', frame: 'music' },
  { id: 'project', label: 'Finish a project', task: 'Finish the project I started and stalled on', frame: 'systems' },
  { id: 'memo', label: 'Strategy memo', task: 'Draft a clear product strategy memo', frame: 'investing' },
  { id: 'talk', label: 'Hard conversation', task: 'Prepare for the hard conversation I keep avoiding', frame: 'relationship' },
  { id: 'reset', label: 'Reset my space', task: 'Get my room back to baseline without spiraling', frame: 'fitness' },
];
