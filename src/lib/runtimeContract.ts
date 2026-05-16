import { logSessionIssue } from './sessionDiagnostics';

export interface RuntimeStep {
  id: string;
  title: string;
  prompt?: string;
  why?: string;
  action?: string;
  output_slot?: string;
  status?: string;
  user_output?: string;
}

export interface RuntimeWorkspace {
  id: string;
  task?: string;
  title?: string;
  frame?: string;
  supports?: string[];
  status?: string;
  current_step_index?: number;
  steps?: RuntimeStep[];
  artifact?: Record<string, unknown>;
  interests?: string[];
  [key: string]: unknown;
}

export interface CalmContract {
  primary_action_only?: boolean;
  hide_backend_complexity?: boolean;
  show_next_step_first?: boolean;
  focus_mode?: boolean;
}

export interface ImmersionState {
  ambient_state?: string;
  narrative_thread?: string;
  mission_continuity?: string;
  challenge_arc?: string;
  progression_arc?: string;
  mastery_arc?: string;
  identity_reinforcement?: string;
  session_phase?: string;
  tone?: string;
}

export interface FrictionState {
  friction_level?: number;
  probable_cause?: string;
  intervention_strategy?: string;
}

export interface MomentumState {
  mode?: string;
  pace_modifier?: number;
  challenge_level?: string;
  interaction_density?: string;
  reflection_frequency?: string;
  reward_frequency?: string;
}

export interface InteractionRotation {
  current?: string;
  previous?: string;
  candidates?: string[];
  avoid_repeat?: boolean;
  rotation_reason?: string;
}

export interface AdaptivePacing {
  pace_modifier?: number;
  step_size?: string;
  session_length?: string;
  reflection_frequency?: string;
}

export interface RewardState {
  frequency?: string;
  ready?: boolean;
  message?: string;
  streak?: number;
}

export interface IdentityState {
  frame?: string;
  tone?: string;
  reinforcement?: string;
  mission?: string;
}

export interface FrontendRuntime {
  ui_mode?: string;
  interaction_modes?: string[];
  selected_modes?: string[];
  challenge?: Record<string, unknown>;
  simulation?: Record<string, unknown>;
  reward?: Record<string, unknown>;
  voice?: Record<string, unknown>;
  pacing?: { step_size?: string; session_length?: string; reward_frequency?: string };
  verification?: { verified?: boolean; next_action?: string; flags?: string[] };
  gate?: { advance?: boolean; mode?: string };
  engagement?: { state?: string; engagement_score?: number };
  pathways?: { pathways?: string[]; learning_target?: string; adaptive_switching?: boolean };
  immersion_state?: ImmersionState;
  friction_state?: FrictionState;
  adaptive_pacing?: AdaptivePacing;
  interaction_rotation?: InteractionRotation;
  momentum_state?: MomentumState;
  reward_state?: RewardState;
  identity_state?: IdentityState;
  calm_contract?: CalmContract;
}

export interface NormalizedRuntimeContract {
  ok: boolean;
  workspace: RuntimeWorkspace;
  currentStep: RuntimeStep | null;
  nextPrompt: { title?: string; prompt?: string; message?: string };
  artifactPreview: Record<string, unknown>;
  progress: { done: number; total: number; percent: number };
  frontendRuntime: FrontendRuntime;
  rewriteOptions: string[];
}

export type InteractionCardKind = 'voice' | 'challenge' | 'simulation';

/** UX atmosphere for optional interaction surfaces — derived from normalized runtime only. */
export type InteractionAtmosphere =
  | 'simulation'
  | 'voice'
  | 'challenge'
  | 'checkpoint'
  | 'reflection'
  | 'quest'
  | 'boss_battle'
  | 'teach_back'
  | 'conversational'
  | 'default';

export interface VisibleInteractionCard {
  kind: InteractionCardKind;
  title: string;
  subtitle: string;
  cta: string;
  /** How this card should feel visually — never raw backend keys. */
  atmosphere: InteractionAtmosphere;
}

export type RuntimeDensity = 'low' | 'normal' | 'immersive';

export type InteractionTone = 'professional' | 'gentle' | 'calm' | 'focused';

const REWRITE_DEFAULT = [
  'make_easier',
  'break_smaller',
  'give_example',
  'explain_differently',
] as const;

const GAME_LABELS: Record<string, string> = {
  translation_combo: 'Phrase streak',
  bug_hunt: 'Logic check',
  argument_chain: 'Argument builder',
  memory_duel: 'Quick recall',
  momentum_loop: 'Momentum round',
};

const SIM_LABELS: Record<string, string> = {
  travel_conversation: 'Travel conversation',
  startup_launch: 'Launch scenario',
  debate_room: 'Debate practice',
  exam_pressure: 'Timed practice',
  adaptive_growth: 'Practice scenario',
};

const PATHWAY_LABELS: Record<string, string> = {
  voice: 'Voice',
  active_recall: 'Active recall',
  simulation: 'Scenario',
  teach_back: 'Teach back',
  whiteboard: 'Sketch it out',
  challenge_ladders: 'Challenge ladder',
  conversation: 'Conversation',
  textual: 'Write it out',
  diagrammatic: 'Diagram',
  quests: 'Quest path',
};

const CHILDISH_MODES = new Set(['xp_system', 'quests', 'challenge_ladders']);

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

function asStep(value: unknown): RuntimeStep | null {
  if (!value || typeof value !== 'object') return null;
  const s = value as RuntimeStep;
  if (!s.title && !s.prompt) return null;
  return {
    id: String(s.id ?? 'step'),
    title: String(s.title ?? 'Next step'),
    prompt: s.prompt,
    why: s.why,
    action: s.action,
    output_slot: s.output_slot,
    status: s.status,
    user_output: s.user_output,
  };
}

function progressFromWorkspace(workspace: RuntimeWorkspace): { done: number; total: number; percent: number } {
  const steps = workspace.steps ?? [];
  const done = steps.filter((s) => s.status === 'done').length;
  const total = steps.length;
  return { done, total, percent: total ? Math.round((done / total) * 100) : 0 };
}

export function normalizeRuntimeResponse(raw: Record<string, unknown>): NormalizedRuntimeContract {
  const wsRaw = (raw.workspace ?? raw.session) as Record<string, unknown> | undefined;
  const workspace = normalizeWorkspace(wsRaw);
  const progressRaw = asRecord(raw.progress);
  const progress =
    typeof progressRaw.done === 'number' && typeof progressRaw.total === 'number'
      ? {
          done: progressRaw.done,
          total: progressRaw.total,
          percent:
            typeof progressRaw.percent === 'number'
              ? progressRaw.percent
              : progressFromWorkspace(workspace).percent,
        }
      : progressFromWorkspace(workspace);

  const frontendRuntime = normalizeFrontendRuntime(
    asRecord(raw.frontend_runtime),
    raw,
  );

  if (!workspace.id) {
    logSessionIssue('missing_session_payload', { phase: 'normalize' });
  }

  return {
    ok: raw.ok !== false,
    workspace,
    currentStep: resolveCurrentStep(raw, workspace),
    nextPrompt: asRecord(raw.next_prompt) as NormalizedRuntimeContract['nextPrompt'],
    artifactPreview: asRecord(raw.artifact_preview),
    progress,
    frontendRuntime,
    rewriteOptions: Array.isArray(raw.rewrite_options)
      ? (raw.rewrite_options as string[])
      : [...REWRITE_DEFAULT],
  };
}

function normalizeWorkspace(raw: Record<string, unknown> | undefined): RuntimeWorkspace {
  const w = raw ?? {};
  const id = String(w.id ?? w.workspace_id ?? w.session_id ?? '');
  const task = String(w.task ?? w.title ?? '').trim();
  return {
    ...w,
    id,
    task: task || undefined,
    title: String(w.title ?? task ?? 'Bridge session'),
    frame: w.frame ? String(w.frame) : undefined,
    supports: Array.isArray(w.supports) ? (w.supports as string[]) : undefined,
    status: w.status ? String(w.status) : 'active',
    steps: Array.isArray(w.steps)
      ? (w.steps as RuntimeStep[]).map((s, i) => ({
          id: String(s.id ?? `s${i + 1}`),
          title: String(s.title ?? `Step ${i + 1}`),
          prompt: s.prompt,
          why: s.why,
          action: s.action,
          output_slot: s.output_slot,
          status: s.status,
          user_output: s.user_output,
        }))
      : [],
    artifact: asRecord(w.artifact),
    interests: Array.isArray(w.interests) ? (w.interests as string[]) : undefined,
  };
}

function activeStepFromWorkspace(workspace: RuntimeWorkspace): RuntimeStep | null {
  const steps = workspace.steps ?? [];
  const idx = Number(workspace.current_step_index ?? 0);
  if (idx >= 0 && idx < steps.length) return steps[idx] ?? null;
  return null;
}

/** Prefer workspace index when API `current_step` is stale after continue. */
export function resolveCurrentStep(
  raw: Record<string, unknown>,
  workspace: RuntimeWorkspace,
): RuntimeStep | null {
  const fromWorkspace = activeStepFromWorkspace(workspace);
  const fromApi = asStep(raw.current_step);
  if (!fromApi) return fromWorkspace;
  if (!fromWorkspace) return fromApi;

  const steps = workspace.steps ?? [];
  const wsIdx = Number(workspace.current_step_index ?? 0);
  const apiIdx = steps.findIndex((s) => s.id === fromApi.id);
  if (apiIdx >= 0 && apiIdx !== wsIdx) return fromWorkspace;
  if (fromApi.status === 'done' && fromWorkspace.status !== 'done') return fromWorkspace;
  return fromApi;
}

export interface StepTrailItem {
  id: string;
  title: string;
  status: 'done' | 'active' | 'pending';
  index: number;
}

export function getStepTrail(contract: NormalizedRuntimeContract): StepTrailItem[] {
  const steps = contract.workspace.steps ?? [];
  const activeIdx = Number(contract.workspace.current_step_index ?? 0);
  return steps.map((step, index) => {
    let status: StepTrailItem['status'] = 'pending';
    if (step.status === 'done' || index < activeIdx) status = 'done';
    else if (index === activeIdx && contract.workspace.status !== 'complete') status = 'active';
    else if (step.status === 'active') status = 'active';
    return {
      id: step.id,
      title: step.title,
      status,
      index,
    };
  });
}

export function requiresUserOutput(contract: NormalizedRuntimeContract): boolean {
  if (contract.workspace.status === 'complete') return false;
  const gate = contract.frontendRuntime.gate;
  if (gate?.advance === true) return false;
  return true;
}

function normalizeFrontendRuntime(
  fr: Record<string, unknown>,
  raw: Record<string, unknown>,
): FrontendRuntime {
  const cognition = asRecord(raw.adaptive_cognition);
  const pacing = { ...asRecord(raw.pacing), ...asRecord(fr.pacing), ...asRecord(fr.adaptive_pacing) };
  const merged: FrontendRuntime = {
    ...fr,
    challenge: { ...asRecord(fr.challenge), ...asRecord(raw.minigame) },
    simulation: { ...asRecord(fr.simulation), ...asRecord(raw.simulation) },
    voice: { ...asRecord(fr.voice), ...asRecord(raw.voice_runtime) },
    verification: { ...asRecord(fr.verification), ...asRecord(raw.verification) },
    gate: { ...asRecord(fr.gate), ...asRecord(raw.gate) },
    engagement: { ...asRecord(fr.engagement), ...asRecord(raw.engagement) },
    pathways: (fr.pathways as FrontendRuntime['pathways']) ?? (raw.pathways as FrontendRuntime['pathways']),
    pacing,
    immersion_state: (fr.immersion_state as ImmersionState) ?? (cognition.immersion_state as ImmersionState),
    friction_state: (fr.friction_state as FrictionState) ?? (cognition.friction_state as FrictionState),
    adaptive_pacing: (fr.adaptive_pacing as AdaptivePacing) ?? (cognition.adaptive_pacing as AdaptivePacing),
    interaction_rotation:
      (fr.interaction_rotation as InteractionRotation) ?? (cognition.interaction_rotation as InteractionRotation),
    momentum_state: (fr.momentum_state as MomentumState) ?? (cognition.momentum_state as MomentumState),
    reward_state: (fr.reward_state as RewardState) ?? (cognition.reward_state as RewardState),
    identity_state: (fr.identity_state as IdentityState) ?? (cognition.identity_state as IdentityState),
    calm_contract: {
      primary_action_only: fr.calm_contract
        ? (fr.calm_contract as CalmContract).primary_action_only
        : pacing.step_size === 'tiny',
      hide_backend_complexity: true,
      show_next_step_first: true,
      focus_mode: (fr.calm_contract as CalmContract)?.focus_mode,
      ...(fr.calm_contract as CalmContract),
    },
  };
  return merged;
}

export function getPrimaryStep(contract: NormalizedRuntimeContract): {
  title: string;
  prompt: string;
  why?: string;
  action?: string;
} {
  const step = contract.currentStep ?? activeStepFromWorkspace(contract.workspace);
  const np = contract.nextPrompt;
  const isComplete = contract.workspace.status === 'complete';
  if (isComplete) {
    return {
      title: 'Session complete',
      prompt: 'Export your work or start a new Bridge when you are ready.',
    };
  }
  if (!step?.title && !step?.prompt && !np.title && !np.prompt && !np.message) {
    return { title: '', prompt: '' };
  }
  return {
    title: step?.title || np.title || '',
    prompt: step?.prompt || np.prompt || np.message || '',
    why: step?.why,
    action: step?.action,
  };
}

export function shouldUseMinimalMode(contract: NormalizedRuntimeContract): boolean {
  const cc = contract.frontendRuntime.calm_contract;
  const pacing = contract.frontendRuntime.pacing?.step_size;
  return Boolean(cc?.primary_action_only || pacing === 'tiny');
}

export function shouldShowNextStepFirst(contract: NormalizedRuntimeContract): boolean {
  return contract.frontendRuntime.calm_contract?.show_next_step_first !== false;
}

export function isChildishMode(contract: NormalizedRuntimeContract): boolean {
  const modes = contract.frontendRuntime.selected_modes ?? [];
  return modes.some((m) => CHILDISH_MODES.has(m));
}

export function getCheckpointMessage(contract: NormalizedRuntimeContract): string | null {
  const friction = contract.frontendRuntime.friction_state;
  if (friction?.friction_level != null && friction.friction_level >= 0.55) {
    const strategy = friction.intervention_strategy;
    if (strategy === 'simplify') return 'Keep it small — one honest sentence is enough to move forward.';
    if (strategy === 'reduce_pressure') return 'No perfect answer needed. Share a rough thought to continue.';
    if (strategy === 'offer_voice_mode') return 'You can type a short note, or say it out loud first then type the gist.';
    if (strategy === 'switch_interaction_type') return 'Try a different angle — answer in plain words, no polish required.';
  }
  const gate = contract.frontendRuntime.gate;
  const verification = contract.frontendRuntime.verification;
  if (gate?.advance === false) {
    return 'Add one more sentence or detail so Bridge can move you forward.';
  }
  if (verification?.verified === false && verification?.next_action === 'request_checkpoint') {
    return 'Add a little more to your answer before continuing.';
  }
  return null;
}

export function getImmersionNarrative(contract: NormalizedRuntimeContract): string | null {
  const thread = contract.frontendRuntime.immersion_state?.narrative_thread;
  return thread?.trim() || null;
}

export function getRewardNotice(contract: NormalizedRuntimeContract): string | null {
  const reward = contract.frontendRuntime.reward_state;
  if (!reward?.ready || !reward.message) return null;
  return reward.message;
}

export function shouldUseFocusLayout(contract: NormalizedRuntimeContract): boolean {
  return Boolean(contract.frontendRuntime.calm_contract?.focus_mode);
}

/** Primary interaction mode from runtime (first selected, else rotation hint). */
export function getPrimaryMode(contract: NormalizedRuntimeContract): string {
  const selected = contract.frontendRuntime.selected_modes ?? [];
  if (selected.length) return String(selected[0]);
  const rotated = contract.frontendRuntime.interaction_rotation?.current;
  if (rotated) return rotated;
  return '';
}

/** Layout / motion density from engagement, friction, and calm contract. */
export function getRuntimeDensity(contract: NormalizedRuntimeContract): RuntimeDensity {
  const eng = contract.frontendRuntime.engagement?.state;
  const score = Number(contract.frontendRuntime.engagement?.engagement_score ?? 50);
  const friction = Number(contract.frontendRuntime.friction_state?.friction_level ?? 0);
  const cc = contract.frontendRuntime.calm_contract;
  const pacing = contract.frontendRuntime.pacing?.step_size;

  if (cc?.primary_action_only || pacing === 'tiny' || friction >= 0.55 || eng === 'disengaging' || score < 36) {
    return 'low';
  }
  if (eng === 'immersed' || score >= 74 || contract.frontendRuntime.momentum_state?.mode === 'deep_engagement') {
    return 'immersive';
  }
  return 'normal';
}

/** Copy and framing tone — all user-safe labels. */
export function getInteractionTone(contract: NormalizedRuntimeContract): InteractionTone {
  const supports = contract.workspace.supports ?? [];
  if (supports.includes('professional')) return 'professional';
  const friction = Number(contract.frontendRuntime.friction_state?.friction_level ?? 0);
  if (friction >= 0.5) return 'gentle';
  if (contract.frontendRuntime.identity_state?.tone === 'professional') return 'professional';
  if (contract.frontendRuntime.momentum_state?.mode === 'deep_engagement') return 'focused';
  return 'calm';
}

function resolveAtmosphere(
  kind: InteractionCardKind,
  contract: NormalizedRuntimeContract,
): InteractionAtmosphere {
  const mode = getPrimaryMode(contract).toLowerCase();
  const arc = String(contract.frontendRuntime.immersion_state?.challenge_arc ?? '').toLowerCase();
  const ver = contract.frontendRuntime.verification;

  if (kind === 'simulation' || mode.includes('simulation') || mode.includes('scenario')) return 'simulation';
  if (kind === 'voice' || mode.includes('voice') || mode.includes('conversation')) {
    return mode.includes('conversation') ? 'conversational' : 'voice';
  }
  if (mode.includes('reflection')) return 'reflection';
  if (mode.includes('teach')) return 'teach_back';
  if (mode.includes('quest') || mode.includes('quests')) return 'quest';
  if (mode.includes('boss') || arc.includes('final') || arc.includes('boss')) return 'boss_battle';
  if (ver?.next_action === 'request_checkpoint') return 'checkpoint';
  if (kind === 'challenge' || mode.includes('challenge')) return 'challenge';
  return 'default';
}

export function getVoiceOption(contract: NormalizedRuntimeContract): VisibleInteractionCard | null {
  const voice = contract.frontendRuntime.voice ?? {};
  const mode = voice.voice_mode as string | undefined;
  if (!mode) return null;
  const reflection = (voice.reflection_prompts as string) || 'Practice out loud for a minute.';
  const card: VisibleInteractionCard = {
    kind: 'voice',
    title: 'Voice practice',
    subtitle: reflection,
    cta: 'Try speaking',
    atmosphere: resolveAtmosphere('voice', contract),
  };
  return card;
}

export function getChallengeOption(contract: NormalizedRuntimeContract): VisibleInteractionCard | null {
  const ch = contract.frontendRuntime.challenge ?? {};
  const gameType = ch.game_type as string | undefined;
  const objective = ch.objective as string | undefined;
  if (!gameType && !objective) return null;
  const title = GAME_LABELS[gameType ?? ''] || 'Optional challenge';
  const card: VisibleInteractionCard = {
    kind: 'challenge',
    title,
    subtitle: objective || 'A short interactive round tied to your goal.',
    cta: 'Try it',
    atmosphere: resolveAtmosphere('challenge', contract),
  };
  return card;
}

export function getSimulationOption(contract: NormalizedRuntimeContract): VisibleInteractionCard | null {
  const sim = contract.frontendRuntime.simulation ?? {};
  const key = sim.simulation as string | undefined;
  const scenario = sim.scenario as string | undefined;
  if (!key && !scenario) return null;
  const title = SIM_LABELS[key ?? ''] || 'Practice mode';
  const card: VisibleInteractionCard = {
    kind: 'simulation',
    title,
    subtitle: scenario || 'Walk through a scenario version of your task.',
    cta: 'Try scenario',
    atmosphere: resolveAtmosphere('simulation', contract),
  };
  return card;
}

/** At most one optional interaction surface, unless pacing allows more. */
export function getVisibleInteractionCards(
  contract: NormalizedRuntimeContract,
): VisibleInteractionCard[] {
  if (shouldUseMinimalMode(contract)) {
    const voice = getVoiceOption(contract);
    if (voice) return [voice];
    return [];
  }

  const selected = new Set(contract.frontendRuntime.selected_modes ?? []);
  const candidates: VisibleInteractionCard[] = [];

  if (selected.has('voice') || selected.has('conversation') || getVoiceOption(contract)) {
    const v = getVoiceOption(contract);
    if (v) candidates.push(v);
  }
  const challenge = getChallengeOption(contract);
  if (challenge && (selected.has('challenge_ladders') || selected.has('quests') || !selected.size)) {
    candidates.push(challenge);
  }
  const simulation = getSimulationOption(contract);
  if (simulation && (selected.has('simulation') || !selected.size)) {
    candidates.push(simulation);
  }

  if (candidates.length > 1) {
    const p = getPrimaryMode(contract).toLowerCase();
    const rank = (c: VisibleInteractionCard) => {
      if (p.includes('sim') && c.kind === 'simulation') return 3;
      if ((p.includes('voice') || p.includes('conversation')) && c.kind === 'voice') return 3;
      if ((p.includes('challenge') || p.includes('quest')) && c.kind === 'challenge') return 3;
      if (p.includes('writing') && c.kind === 'challenge') return 1;
      return 0;
    };
    candidates.sort((a, b) => rank(b) - rank(a));
  }

  const unique: VisibleInteractionCard[] = [];
  for (const c of candidates) {
    if (!unique.some((u) => u.kind === c.kind)) unique.push(c);
    if (unique.length >= 1) break;
  }
  return unique;
}

export function getPathwayChips(contract: NormalizedRuntimeContract): { id: string; label: string }[] {
  const list = contract.frontendRuntime.pathways?.pathways ?? [];
  return list
    .filter((id) => id !== 'textual')
    .slice(0, 4)
    .map((id) => ({ id, label: PATHWAY_LABELS[id] ?? humanize(id) }));
}

export function artifactHasMeaningfulContent(preview: Record<string, unknown>): boolean {
  const sections = asRecord(preview.sections);
  if (Object.values(sections).some((v) => String(v ?? '').trim().length > 2)) return true;
  const outline = asRecord(preview.outline);
  if (Object.values(outline).some((v) => String(v ?? '').trim().length > 2)) return true;
  if (Array.isArray(preview.cards) && preview.cards.length > 0) return true;
  if (Array.isArray(preview.files) && preview.files.length > 0) return true;
  const finalOut = String(preview.final_output ?? '').trim();
  if (finalOut.length > 2) return true;
  return false;
}

function humanize(id: string): string {
  return id.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}
