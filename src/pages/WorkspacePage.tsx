import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import {
  continueSession,
  exportSession,
  fetchWorkspace,
  rewriteSession,
  type RuntimeStepPayload,
  type WorkspaceEnvelope,
} from '../lib/sessionApi';
import { isProfessionalMode } from '../lib/onboardingOptions';
import type { EntryRibbonState } from '../lib/startBridgeSession';
import { PRODUCT_WORKSPACE_LOOP } from '../lib/productPitch';
import {
  artifactSectionLabel,
  formatUserApiError,
  frameBlurbSafe,
  frameEmojiSafe,
  frameTitleSafe,
  sessionTaskLabel,
  supportTitleSafe,
} from '../lib/displayLabels';
import { logSessionIssue } from '../lib/sessionDiagnostics';
import { normalizeFrameForSession } from '../lib/sessionApi';

type RewriteMode = 'make_easier' | 'break_smaller' | 'explain_differently' | 'give_example';

interface RewriteButton {
  mode: RewriteMode;
  label: string;
  proLabel: string;
  hint: string;
}

const REWRITE_BUTTONS: ReadonlyArray<RewriteButton> = [
  { mode: 'make_easier', label: 'Make easier', proLabel: 'Reduce scope', hint: 'Shrink the next move.' },
  { mode: 'break_smaller', label: 'Break smaller', proLabel: 'Decompose', hint: 'Split into micro-actions.' },
  { mode: 'give_example', label: 'Give example', proLabel: 'Show example', hint: 'Show one before I try.' },
  { mode: 'explain_differently', label: 'Explain differently', proLabel: 'Reframe', hint: 'Reframe through the interest.' },
];

interface BridgeLocationState {
  entryRibbon?: EntryRibbonState;
}

type ArtifactPreview = WorkspaceEnvelope['artifact_preview'] & {
  type?: string;
  outline?: { introduction?: string; body_points?: string; draft_seed?: string; conclusion?: string };
  cards?: Array<{ front?: string; back?: string }>;
  files?: string[];
  topic?: string;
  project?: string;
  sections?: Record<string, string | undefined | null>;
};

export default function WorkspacePage() {
  const { workflowId } = useParams<{ workflowId: string }>();
  const workspaceId = workflowId ?? '';
  const location = useLocation();
  const navigate = useNavigate();

  const [envelope, setEnvelope] = useState<WorkspaceEnvelope | null>(null);
  const [draft, setDraft] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [helpNotice, setHelpNotice] = useState<string | null>(null);
  const [exportText, setExportText] = useState<string | null>(null);
  const [exportCopied, setExportCopied] = useState(false);
  const [artifactOpen, setArtifactOpen] = useState(true);
  const [planOpen, setPlanOpen] = useState(false);
  const [entryRibbon, setEntryRibbon] = useState<EntryRibbonState | null>(
    () => (location.state as BridgeLocationState | null)?.entryRibbon ?? null,
  );

  useEffect(() => {
    if (!entryRibbon) return;
    const id = window.setTimeout(() => {
      navigate(location.pathname, { replace: true, state: {} });
      setEntryRibbon(null);
    }, 5600);
    return () => window.clearTimeout(id);
  }, [entryRibbon, navigate, location.pathname]);

  const load = useCallback(async () => {
    if (!workspaceId) {
      setError("Couldn't load this session.");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await fetchWorkspace(workspaceId);
      const ws = data?.workspace ?? data?.session;
      if (!ws?.id) {
        logSessionIssue('missing_session_payload', { workspaceId, phase: 'fetch' });
        setEnvelope(null);
        setError("Couldn't load this session.");
        return;
      }
      const rawFrame = String(ws.frame ?? '');
      const normalizedFrame = normalizeFrameForSession(rawFrame);
      if (rawFrame && normalizedFrame !== rawFrame.trim().toLowerCase()) {
        logSessionIssue('invalid_frame', { workspaceId, frame: rawFrame, resolved: normalizedFrame });
      }
      const ribbonState = (location.state as BridgeLocationState | null)?.entryRibbon;
      if (ribbonState && frameTitleSafe(normalizedFrame) !== ribbonState.frameTitle) {
        logSessionIssue('hydration_mismatch', {
          workspaceId,
          ribbonFrame: ribbonState.frameTitle,
          sessionFrame: normalizedFrame,
        });
      }
      setEnvelope(data);
      setDraft('');
    } catch (e) {
      setEnvelope(null);
      setError(formatUserApiError(e, "Couldn't load this session."));
    } finally {
      setLoading(false);
    }
  }, [workspaceId, location.state]);

  useEffect(() => {
    void load();
  }, [load]);

  const session = envelope?.workspace ?? envelope?.session ?? null;
  const steps = (session?.steps ?? []) as RuntimeStepPayload[];
  const currentIndex = Number(session?.current_step_index ?? 0);
  const status = String(session?.status ?? 'active');
  const isComplete = status === 'complete';
  const currentStep = envelope?.current_step ?? steps[currentIndex] ?? null;
  const nextPrompt = envelope?.next_prompt ?? null;
  const intelligence = envelope?.intelligence ?? null;
  const runtimeState = envelope?.runtime_state ?? null;
  const artifactPreview = (envelope?.artifact_preview ?? {}) as ArtifactPreview;
  const progress = envelope?.progress ?? { done: 0, total: steps.length, percent: 0 };
  const task = sessionTaskLabel(
    typeof session?.task === 'string' ? session.task : undefined,
    typeof session?.title === 'string' ? session.title : undefined,
  );
  const frame = normalizeFrameForSession(
    typeof session?.frame === 'string' ? session.frame : undefined,
  );
  const supports = (session?.supports as string[] | undefined) ?? [];
  const professional = isProfessionalMode(supports);

  const liveCompletionRate = useMemo(() => {
    if (typeof runtimeState?.completion_rate === 'number') return runtimeState.completion_rate;
    if (typeof intelligence?.completion_rate === 'number') return intelligence.completion_rate;
    if (progress.total) return Math.round((progress.done / progress.total) * 100);
    return 0;
  }, [runtimeState?.completion_rate, intelligence?.completion_rate, progress.done, progress.total]);

  async function handleContinue() {
    if (!workspaceId || busy || isComplete) return;
    setBusy(true);
    setError(null);
    setHelpNotice(null);
    try {
      const data = await continueSession({ workspace_id: workspaceId, user_output: draft });
      setEnvelope(data);
      setDraft('');
      setExportText(null);
      setExportCopied(false);
    } catch (e) {
      setError(formatUserApiError(e, "Couldn't save this step. Try again."));
    } finally {
      setBusy(false);
    }
  }

  async function handleRewrite(mode: RewriteMode) {
    if (!workspaceId || busy) return;
    setBusy(true);
    setError(null);
    setHelpNotice(null);
    try {
      const data = await rewriteSession({ workspace_id: workspaceId, mode, frame });
      setEnvelope(data);
      const btn = REWRITE_BUTTONS.find((b) => b.mode === mode);
      const label = professional ? btn?.proLabel : btn?.label;
      setHelpNotice(`Rewrote with: ${label ?? mode}`);
    } catch (e) {
      setError(formatUserApiError(e, "Couldn't adjust this step. Try again."));
    } finally {
      setBusy(false);
    }
  }

  async function handleExport() {
    if (!workspaceId || busy) return;
    setBusy(true);
    setError(null);
    try {
      const data = await exportSession({ workspace_id: workspaceId });
      setExportText(data.markdown || data.plain_text || '');
      setExportCopied(false);
    } catch (e) {
      setError(formatUserApiError(e, "Couldn't export this session. Try again."));
    } finally {
      setBusy(false);
    }
  }

  async function handleCopyExport() {
    if (!exportText) return;
    try {
      await navigator.clipboard.writeText(exportText);
      setExportCopied(true);
      window.setTimeout(() => setExportCopied(false), 1800);
    } catch {
      setError('Clipboard not available. Select the text and copy manually.');
    }
  }

  const tone = useTone(professional);
  const fEmoji = frameEmojiSafe(frame);
  const fTitle = frameTitleSafe(frame);
  const fBlurb = frameBlurbSafe(frame);

  return (
    <div className="session">
      <header className="session__top">
        <Link className="btn btn-quiet" to="/home">
          ← Sessions
        </Link>
        <Link className="btn btn-quiet" to="/start">
          New
        </Link>
      </header>

      {loading && !envelope ? <p className="muted small session__loading">Loading session…</p> : null}

      {error ? (
        <div className="banner-gentle session__banner" role="status">
          {error}{' '}
          <button type="button" className="btn btn-quiet" onClick={() => void load()}>
            Retry
          </button>
        </div>
      ) : null}

      {!envelope && !loading ? (
        <div className="session__missing">
          <h2 className="session-step__title">Couldn&apos;t load this session.</h2>
          <p className="muted small">
            It may have been removed, or the server may be offline. You can try again or start fresh.
          </p>
          <div className="row session__missing-actions">
            <button type="button" className="btn" onClick={() => void load()}>
              Retry
            </button>
            <Link className="btn btn-primary" to="/start">
              Start a new Bridge
            </Link>
            <Link className="btn btn-quiet" to="/home">
              Back to sessions
            </Link>
          </div>
        </div>
      ) : null}

      {envelope ? (
        <>
          {entryRibbon ? (
            <div className="bridge-entry-ribbon" role="status" aria-live="polite">
              <div className="bridge-entry-ribbon__row">
                <span className="bridge-entry-ribbon__task">{entryRibbon.task}</span>
                <span className="bridge-entry-ribbon__arrow" aria-hidden>
                  →
                </span>
                <span className="bridge-entry-ribbon__frame">
                  <span aria-hidden>{entryRibbon.frameEmoji}</span> {entryRibbon.frameTitle}
                </span>
              </div>
              <p className="bridge-entry-ribbon__sub">{entryRibbon.frameBlurb}</p>
              <p className="bridge-entry-ribbon__foot">
                You are in your session. Work one step at a time. Save when you are ready. The next step
                will use the {entryRibbon.frameTitle} style you picked, until this task is done.
              </p>
            </div>
          ) : null}

          <section className="session-identity" aria-label="Your session">
            <div className="session-identity__frame">
              <span className="session-identity__frame-emoji" aria-hidden>
                {fEmoji || '✨'}
              </span>
              <span className="session-identity__frame-text">
                <span className="session-identity__frame-label">Using</span>
                <span className="session-identity__frame-name">{fTitle}</span>
              </span>
            </div>
            <h1 className="session-identity__task">{task}</h1>
            {fBlurb ? <p className="session-identity__sub">{fBlurb}</p> : null}
            {progress.total > 0 ? (
              <div className="session-identity__progress">
                <div className="meter meter--ios">
                  <span style={{ width: `${liveCompletionRate}%` }} />
                </div>
                <span className="muted small">
                  {progress.done}/{progress.total} · {liveCompletionRate}%
                </span>
              </div>
            ) : null}
            {supports.length ? (
              <p className="session-identity__supports muted small">
                {supports
                  .map((s) => supportTitleSafe(s))
                  .filter(Boolean)
                  .join(' · ')}
              </p>
            ) : null}
          </section>

          {isComplete ? (
            <CompletionPanel
              task={task}
              onExport={() => void handleExport()}
              exportText={exportText}
              exportCopied={exportCopied}
              onCopy={() => void handleCopyExport()}
              busy={busy}
              tone={tone}
            />
          ) : (
            <>
              <p className="bridge-session-loop" role="note">
                {tone.loopBanner}
              </p>
              <section className="session-step">
                <span className="session-step__eyebrow">{tone.rightNow}</span>
                <h2 className="session-step__title">
                  {currentStep?.title || nextPrompt?.title || tone.fallbackTitle}
                </h2>
                {currentStep?.why ? <p className="session-step__why">{currentStep.why}</p> : null}
                <p className="session-step__prompt session-step__prompt--live">
                  {currentStep?.prompt || nextPrompt?.prompt || tone.fallbackPrompt}
                </p>
                {currentStep?.action ? (
                  <p className="session-step__action">
                    <span className="session-step__action-label">{tone.doneLabel}</span>
                    {currentStep.action}
                  </p>
                ) : null}
              </section>

              <section className="session-write">
                <label className="session-write__label" htmlFor="session-draft">
                  {tone.yourMove}
                </label>
                <textarea
                  id="session-draft"
                  className="session-write__textarea"
                  rows={5}
                  placeholder={tone.placeholder}
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  disabled={busy}
                />
                <div className="session-write__actions">
                  <button
                    type="button"
                    className="btn btn-primary btn-lg btn-block session-write__cta"
                    onClick={() => void handleContinue()}
                    disabled={busy}
                  >
                    {busy ? tone.saving : draft.trim() ? tone.saveContinue : tone.markContinue}
                  </button>
                  <span className="muted small session-write__hint">
                    {draft.trim() ? `${draft.trim().length} characters saved.` : tone.emptyHint}
                  </span>
                </div>
              </section>

              <section className="session-help">
                <span className="session-help__label">{tone.stuckLabel}</span>
                <div className="session-help__grid">
                  {REWRITE_BUTTONS.map((b) => (
                    <button
                      key={b.mode}
                      type="button"
                      className="btn session-help__btn"
                      onClick={() => void handleRewrite(b.mode)}
                      disabled={busy}
                      title={b.hint}
                    >
                      {professional ? b.proLabel : b.label}
                    </button>
                  ))}
                </div>
                {helpNotice ? (
                  <p className="muted small session-help__notice">{helpNotice}</p>
                ) : null}
              </section>
            </>
          )}

          <section className="session-artifact">
            <button
              type="button"
              className="session-disclosure"
              aria-expanded={artifactOpen}
              onClick={() => setArtifactOpen((v) => !v)}
            >
              <span>{tone.buildingLabel}</span>
              <span className="session-disclosure__chev">{artifactOpen ? '−' : '+'}</span>
            </button>
            {artifactOpen ? (
              <ArtifactBody
                preview={artifactPreview}
                sections={session?.artifact as { sections?: Record<string, string> } | undefined}
                emptyHint={tone.artifactEmpty}
              />
            ) : null}
          </section>

          <section className="session-plan">
            <button
              type="button"
              className="session-disclosure"
              aria-expanded={planOpen}
              onClick={() => setPlanOpen((v) => !v)}
            >
              <span>{tone.planLabel}</span>
              <span className="session-disclosure__chev">{planOpen ? '−' : '+'}</span>
            </button>
            {planOpen ? (
              <ol className="session-plan__list">
                {steps.map((s, idx) => {
                  const done = s.status === 'done' || idx < currentIndex;
                  const active = !done && idx === currentIndex;
                  return (
                    <li
                      key={s.id ?? idx}
                      className={`session-plan__li ${active ? 'session-plan__li--active' : ''} ${
                        done ? 'session-plan__li--done' : ''
                      }`}
                    >
                      <span className="session-plan__mark">{done ? '✓' : active ? '→' : '·'}</span>
                      <span>{s.title || `Step ${idx + 1}`}</span>
                    </li>
                  );
                })}
              </ol>
            ) : null}
          </section>
        </>
      ) : null}
    </div>
  );
}

interface Tone {
  rightNow: string;
  yourMove: string;
  doneLabel: string;
  fallbackTitle: string;
  fallbackPrompt: string;
  placeholder: string;
  saveContinue: string;
  markContinue: string;
  saving: string;
  emptyHint: string;
  stuckLabel: string;
  buildingLabel: string;
  planLabel: string;
  artifactEmpty: string;
  loopBanner: string;
  completeLede: string;
}

function useTone(professional: boolean): Tone {
  if (professional) {
    return {
      rightNow: 'Current move',
      yourMove: 'Your output',
      doneLabel: 'Done = ',
      fallbackTitle: 'Next move',
      fallbackPrompt: 'Pick up where you left off.',
      placeholder: 'Draft directly. Rough is fine — you can refine on the next step.',
      saveContinue: 'Save & continue',
      markContinue: 'Mark complete & continue',
      saving: 'Saving…',
      emptyHint: 'Empty is fine. Continue advances the session.',
      stuckLabel: 'Reframe this step',
      buildingLabel: 'Deliverable so far',
      planLabel: 'Session plan',
      artifactEmpty: 'Deliverable populates as you save each step.',
      loopBanner:
        'Process: address the current step, record your output, save to advance. Repeat until the deliverable is complete, using the framing you selected.',
      completeLede:
        'This workstream is complete. Export or copy your materials below, or begin a new session when ready.',
    };
  }
  return {
    rightNow: 'This step',
    yourMove: 'Your move',
    doneLabel: 'Done = ',
    fallbackTitle: 'Next move',
    fallbackPrompt: 'Pick up where you left off.',
    placeholder: 'Type something messy. One ugly sentence beats zero.',
    saveContinue: 'Save & continue',
    markContinue: 'Mark done & continue',
    saving: 'Saving…',
    emptyHint: 'Empty is fine — momentum still counts.',
    stuckLabel: 'Adjust this step',
    buildingLabel: 'What you\u2019re building',
    planLabel: 'Path',
    artifactEmpty: 'Your artifact builds as you save each step.',
    loopBanner: PRODUCT_WORKSPACE_LOOP,
    completeLede:
      'You reached the end of this task. Save a copy below, or start something new whenever you want.',
  };
}

function ArtifactBody({
  preview,
  sections,
  emptyHint,
}: {
  preview: ArtifactPreview;
  sections?: { sections?: Record<string, string> };
  emptyHint: string;
}) {
  const type = preview.type ?? 'general';
  const liveSections = sections?.sections ?? {};
  const hasLiveSections = Object.values(liveSections).some((v) => Boolean(v && String(v).trim()));

  if (type === 'essay_outline') {
    return <EssayOutline preview={preview} live={liveSections} emptyHint={emptyHint} />;
  }
  if (type === 'flashcards' || preview.cards) {
    return <Flashcards preview={preview} emptyHint={emptyHint} />;
  }
  if (type === 'code_scaffold' || preview.files) {
    return <CodeScaffold preview={preview} emptyHint={emptyHint} />;
  }
  if (hasLiveSections) {
    return <LiveSections sections={liveSections} />;
  }
  return <p className="muted small session-artifact__empty">{emptyHint}</p>;
}

function EssayOutline({
  preview,
  live,
  emptyHint,
}: {
  preview: ArtifactPreview;
  live: Record<string, string | undefined | null>;
  emptyHint: string;
}) {
  const outline = preview.outline ?? {};
  const thesis = (live.thesis_seed as string | undefined) || outline.introduction || '';
  const supports = (live.support_points as string | undefined) || outline.body_points || '';
  const body = (live.body_paragraph_seed as string | undefined) || outline.draft_seed || '';
  const closing = (live.draft_outline as string | undefined) || outline.conclusion || '';

  if (!thesis && !supports && !body && !closing) {
    return <p className="muted small session-artifact__empty">{emptyHint}</p>;
  }

  return (
    <ul className="artifact-list">
      <li>
        <strong>Thesis seed</strong>
        <span>{thesis || <em className="muted">drafting…</em>}</span>
      </li>
      <li>
        <strong>Support points</strong>
        <span>{supports || <em className="muted">drafting…</em>}</span>
      </li>
      <li>
        <strong>Body seed</strong>
        <span>{body || <em className="muted">drafting…</em>}</span>
      </li>
      <li>
        <strong>Outline / closing</strong>
        <span>{closing || <em className="muted">drafting…</em>}</span>
      </li>
    </ul>
  );
}

function Flashcards({ preview, emptyHint }: { preview: ArtifactPreview; emptyHint: string }) {
  const cards = (preview.cards ?? []).filter((card) => {
    const front = (card.front ?? '').trim().toLowerCase();
    return front && !['not found', 'not_found', 'undefined', 'null', 'error'].includes(front);
  });
  if (!cards.length) {
    return <p className="muted small session-artifact__empty">{emptyHint}</p>;
  }
  return (
    <ul className="artifact-list">
      {cards.map((card, idx) => (
        <li key={idx}>
          <strong>{card.front?.trim() || `Prompt ${idx + 1}`}</strong>
          <span>{card.back?.trim() || '—'}</span>
        </li>
      ))}
    </ul>
  );
}

function CodeScaffold({ preview, emptyHint }: { preview: ArtifactPreview; emptyHint: string }) {
  const files = preview.files ?? [];
  if (!files.length) {
    return <p className="muted small session-artifact__empty">{emptyHint}</p>;
  }
  return (
    <ul className="artifact-list artifact-list--code">
      {files.map((f) => (
        <li key={f}>
          <code>{f}</code>
        </li>
      ))}
    </ul>
  );
}

function LiveSections({ sections }: { sections: Record<string, string | undefined | null> }) {
  const entries = Object.entries(sections)
    .filter(([, v]) => v && String(v).trim())
    .map(([name, value]) => {
      const label = artifactSectionLabel(name);
      return label ? { name, label, value: String(value) } : null;
    })
    .filter((e): e is { name: string; label: string; value: string } => e !== null);

  if (!entries.length) {
    return null;
  }

  return (
    <ul className="artifact-list">
      {entries.map(({ name, label, value }) => (
        <li key={name}>
          <strong>{label}</strong>
          <span>{value}</span>
        </li>
      ))}
    </ul>
  );
}

function CompletionPanel({
  task,
  onExport,
  exportText,
  exportCopied,
  onCopy,
  busy,
  tone,
}: {
  task: string;
  onExport: () => void;
  exportText: string | null;
  exportCopied: boolean;
  onCopy: () => void;
  busy: boolean;
  tone: Tone;
}) {
  return (
    <section className="session-complete">
      <span className="session-step__eyebrow">{tone.rightNow}</span>
      <h2 className="session-step__title">You finished &ldquo;{task}&rdquo;.</h2>
      <p className="muted">{tone.completeLede}</p>
      <div className="session-complete__actions">
        <button type="button" className="btn btn-primary btn-lg" onClick={onExport} disabled={busy}>
          {exportText ? 'Refresh export' : 'Generate export'}
        </button>
        {exportText ? (
          <button type="button" className="btn" onClick={onCopy} disabled={busy}>
            {exportCopied ? 'Copied' : 'Copy markdown'}
          </button>
        ) : null}
        <Link className="btn btn-quiet" to="/start">
          Start another Bridge
        </Link>
      </div>
      {exportText ? <pre className="export-preview">{exportText}</pre> : null}
    </section>
  );
}

