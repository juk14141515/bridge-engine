import { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';
import { ArtifactPreviewPanel } from '../components/runtime/ArtifactPreview';
import { ExportButton } from '../components/runtime/ExportButton';
import { PrimaryStepCard } from '../components/runtime/PrimaryStepCard';
import { ProgressPill } from '../components/runtime/ProgressPill';
import { RuntimeInteractionCard } from '../components/runtime/RuntimeInteractionCard';
import { SessionStepTrail } from '../components/runtime/SessionStepTrail';
import { WorkInputPanel } from '../components/runtime/WorkInputPanel';
import styles from '../components/runtime/WorkspaceRuntime.module.css';
import {
  formatUserApiError,
  frameBlurbSafe,
  frameEmojiSafe,
  frameTitleSafe,
  sessionTaskLabel,
  supportTitleSafe,
} from '../lib/displayLabels';
import { isProfessionalMode } from '../lib/onboardingOptions';
import type { EntryRibbonState } from '../lib/startBridgeSession';
import { logSessionIssue } from '../lib/sessionDiagnostics';
import { normalizeFrameForSession } from '../lib/frameNormalize';
import {
  artifactHasMeaningfulContent,
  getPathwayChips,
  getRuntimeDensity,
  getVisibleInteractionCards,
  getRewardNotice,
  shouldUseFocusLayout,
  shouldUseMinimalMode,
  type NormalizedRuntimeContract,
} from '../lib/runtimeContract';
import {
  continueSession,
  exportSession,
  getWorkspace,
  rewriteSession,
  type RewriteMode,
} from '../lib/runtimeApi';
import { createLoadGeneration, mergeRuntimeContracts } from '../lib/workspaceLifecycle';

const REWRITE_MODES: ReadonlyArray<{ mode: RewriteMode; label: string; proLabel: string }> = [
  { mode: 'make_easier', label: 'Make easier', proLabel: 'Reduce scope' },
  { mode: 'break_smaller', label: 'Break smaller', proLabel: 'Decompose' },
  { mode: 'give_example', label: 'Give example', proLabel: 'Show example' },
  { mode: 'explain_differently', label: 'Explain differently', proLabel: 'Reframe' },
  { mode: 'do_first_line', label: 'Do first line with me', proLabel: 'Draft first line' },
];

interface BridgeLocationState {
  entryRibbon?: EntryRibbonState;
  initialContract?: NormalizedRuntimeContract;
}

function seedContractFromLocation(
  workspaceId: string,
  state: BridgeLocationState | null,
): NormalizedRuntimeContract | null {
  const seeded = state?.initialContract;
  if (!seeded?.workspace?.id || seeded.workspace.id !== workspaceId) return null;
  return seeded;
}

export default function WorkspacePage() {
  const { workflowId } = useParams<{ workflowId: string }>();
  const workspaceId = workflowId ?? '';
  const location = useLocation();
  const loadGen = useRef(createLoadGeneration());
  const contractRef = useRef<NormalizedRuntimeContract | null>(null);

  const [contract, setContract] = useState<NormalizedRuntimeContract | null>(() =>
    seedContractFromLocation(workspaceId, location.state as BridgeLocationState | null),
  );
  const [draft, setDraft] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(() => !contract);
  const [busy, setBusy] = useState(false);
  const [advancing, setAdvancing] = useState(false);
  const [helpNotice, setHelpNotice] = useState<string | null>(null);
  const [exportText, setExportText] = useState<string | null>(null);
  const [exportCopied, setExportCopied] = useState(false);
  const [entryRibbon, setEntryRibbon] = useState<EntryRibbonState | null>(
    () => (location.state as BridgeLocationState | null)?.entryRibbon ?? null,
  );

  const applyContract = useCallback((next: NormalizedRuntimeContract) => {
    const merged = mergeRuntimeContracts(contractRef.current, next);
    contractRef.current = merged;
    setContract(merged);
    return merged;
  }, []);

  useEffect(() => {
    contractRef.current = contract;
  }, [contract]);

  useEffect(() => {
    if (!entryRibbon) return;
    const id = window.setTimeout(() => setEntryRibbon(null), 5600);
    return () => window.clearTimeout(id);
  }, [entryRibbon]);

  const load = useCallback(
    async (opts?: { silent?: boolean }) => {
      if (!workspaceId) {
        setError("Couldn't load this session.");
        setLoading(false);
        return;
      }

      const seq = loadGen.current.next();
      if (!opts?.silent) setLoading(true);
      setError(null);

      try {
        const next = await getWorkspace(workspaceId);
        if (!loadGen.current.isCurrent(seq)) return;

        if (!next.workspace?.id) {
          logSessionIssue('missing_session_payload', { workspaceId, phase: 'fetch' });
          setContract(null);
          contractRef.current = null;
          setError("Couldn't load this session.");
          return;
        }

        applyContract(next);
      } catch (e) {
        if (!loadGen.current.isCurrent(seq)) return;
        if (!contractRef.current) {
          setContract(null);
          contractRef.current = null;
        }
        setError(formatUserApiError(e, "Couldn't load this session."));
      } finally {
        if (loadGen.current.isCurrent(seq)) setLoading(false);
      }
    },
    [workspaceId, applyContract],
  );

  useEffect(() => {
    const seeded = seedContractFromLocation(workspaceId, location.state as BridgeLocationState | null);
    if (seeded) {
      contractRef.current = seeded;
      setContract(seeded);
      setLoading(false);
    } else {
      setContract(null);
      contractRef.current = null;
    }
    setDraft('');
    setError(null);
    setHelpNotice(null);
    void load({ silent: Boolean(seeded) });
  }, [workspaceId]); // eslint-disable-line react-hooks/exhaustive-deps

  const workspace = contract?.workspace;
  const supports = workspace?.supports ?? [];
  const professional = isProfessionalMode(supports);
  const isComplete = (workspace?.status ?? 'active') === 'complete';
  const minimal = contract ? shouldUseMinimalMode(contract) : false;
  const focusLayout = contract ? shouldUseFocusLayout(contract) : false;
  const rewardNotice = contract ? getRewardNotice(contract) : null;
  const task = sessionTaskLabel(workspace?.task, workspace?.title);
  const frame = normalizeFrameForSession(workspace?.frame);
  const fTitle = frameTitleSafe(frame);
  const fEmoji = frameEmojiSafe(frame);
  const fBlurb = frameBlurbSafe(frame);
  const progress = contract?.progress ?? { done: 0, total: 0, percent: 0 };
  const artifactPreview = contract?.artifactPreview ?? {};
  const liveSections = (workspace?.artifact as { sections?: Record<string, string> } | undefined)?.sections;
  const hasArtifact = artifactHasMeaningfulContent(artifactPreview);
  const interactionCards = contract ? getVisibleInteractionCards(contract) : [];
  const pathwayChips = contract ? getPathwayChips(contract) : [];
  const runtimeDensity = contract ? getRuntimeDensity(contract) : 'normal';
  const isLowDensity = runtimeDensity === 'low';
  const hideSecondaryNav = focusLayout || isLowDensity || minimal;
  const verificationBlocked = contract?.frontendRuntime.verification?.verified === false || contract?.frontendRuntime.gate?.advance === false;

  async function handleContinue() {
    if (!contract?.workspace?.id || busy || isComplete) return;
    const output = draft.trim();
    if (!output) return;

    setBusy(true);
    setAdvancing(true);
    setError(null);
    setHelpNotice(null);
    const seq = loadGen.current.next();

    try {
      const next = await continueSession(contract.workspace.id, output);
      if (!loadGen.current.isCurrent(seq)) return;
      const merged = applyContract(next);
      const verification = merged.frontendRuntime.verification;
      const gate = merged.frontendRuntime.gate;
      if (verification?.verified === false || gate?.advance === false) {
        setAdvancing(false);
        setHelpNotice(verification?.message || 'Add one concrete detail and try Continue again.');
        return;
      }
      setDraft('');
      setExportText(null);
      setExportCopied(false);
      window.setTimeout(() => setAdvancing(false), 380);
    } catch (e) {
      setAdvancing(false);
      setError(formatUserApiError(e, "Couldn't save this step. Try again."));
    } finally {
      setBusy(false);
    }
  }

  async function handleRewrite(mode: RewriteMode) {
    if (!contract?.workspace?.id || busy) return;
    setBusy(true);
    setAdvancing(true);
    setError(null);
    const seq = loadGen.current.next();

    try {
      const next = await rewriteSession(contract.workspace.id, mode);
      if (!loadGen.current.isCurrent(seq)) return;
      applyContract(next);
      const label = REWRITE_MODES.find((m) => m.mode === mode);
      setHelpNotice(`Adjusted: ${professional ? label?.proLabel : label?.label ?? mode}`);
      window.setTimeout(() => setAdvancing(false), 320);
    } catch (e) {
      setAdvancing(false);
      setError(formatUserApiError(e, "Couldn't adjust this step. Try again."));
    } finally {
      setBusy(false);
    }
  }

  async function handleExport() {
    if (!contract?.workspace?.id || busy) return;
    setBusy(true);
    setError(null);
    try {
      const data = await exportSession(contract.workspace.id, 'markdown');
      setExportText(data.markdown || data.content || data.plain_text || '');
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
      setError('Copy manually from the export box below.');
    }
  }

  return (
    <div
      className={`session ${styles.runtimeShell} ${styles[`runtimeShell--density-${runtimeDensity}`]} ${
        focusLayout ? styles.runtimeShellFocus : ''
      } ${advancing ? styles.runtimeShellAdvancing : ''}`}
    >
      <header className="session__top">
        <Link className="btn btn-quiet" to="/home">
          ← Sessions
        </Link>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <ExportButton
            hasContent={hasArtifact}
            busy={busy}
            exportCopied={exportCopied}
            onExport={() => void handleExport()}
          />
          <Link className="btn btn-quiet" to="/start">
            New
          </Link>
        </div>
      </header>

      {loading && !contract ? <p className="muted small session__loading">Loading session…</p> : null}

      {error ? (
        <div className="banner-gentle session__banner" role="status">
          {error}{' '}
          <button type="button" className="btn btn-quiet" onClick={() => void load()}>
            Retry
          </button>
        </div>
      ) : null}

      {!contract && !loading ? (
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

      {contract && workspace ? (
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
                One step at a time. Save when you are ready—we will move you forward through the{' '}
                {entryRibbon.frameTitle} path you picked.
              </p>
            </div>
          ) : null}

          <section className="session-identity" aria-label="Your session">
            <div className="session-identity__frame">
              <span className="session-identity__frame-emoji" aria-hidden>
                {fEmoji}
              </span>
              <span className="session-identity__frame-text">
                <span className="session-identity__frame-label">Translating through</span>
                <span className="session-identity__frame-name">{fTitle}</span>
              </span>
            </div>
            <h1 className="session-identity__task">{task} → {fTitle}</h1>
            <p className="session-identity__sub">
              Bridge is turning this through {fTitle} into steps you can keep following.
              {fBlurb ? ` ${fBlurb}` : ''}
            </p>
            <ProgressPill done={progress.done} total={progress.total} percent={progress.percent} />
            {rewardNotice ? (
              <p className="session-identity__reward muted small" role="status">
                {rewardNotice}
              </p>
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

          <div
            className={`${styles.sessionLayout}${focusLayout ? ` ${styles.sessionLayoutFocus}` : ''}`}
          >
            <div className={styles.sessionLayout__main}>
              {isComplete ? (
                <CompletionBlock
                  task={task}
                  exportText={exportText}
                  exportCopied={exportCopied}
                  busy={busy}
                  onExport={() => void handleExport()}
                  onCopy={() => void handleCopyExport()}
                />
              ) : (
                <div className={styles.stack}>
                  <div className={styles.primaryStep}>
                    <PrimaryStepCard contract={contract} />
                  </div>
                  {advancing ? (
                    <p className={`muted small ${styles.flowStatus}`} role="status">
                      Carrying your thread forward…
                    </p>
                  ) : null}
                  <div className={styles.workPanel}>
                    <WorkInputPanel
                      contract={contract}
                      draft={draft}
                      onDraftChange={setDraft}
                      onContinue={() => void handleContinue()}
                      busy={busy}
                    />
                  </div>

                  {(interactionCards.length && !minimal && !focusLayout && !isLowDensity) ||
                  (pathwayChips.length && !minimal && !hideSecondaryNav) ? (
                    <div className={styles.optionalRow}>
                      {interactionCards.length && !minimal && !focusLayout && !isLowDensity
                        ? interactionCards.map((card) => (
                            <RuntimeInteractionCard
                              key={card.kind}
                              card={card}
                              onAction={() =>
                                setHelpNotice(`${card.title} can support this step. The main path is above.`)
                              }
                            />
                          ))
                        : null}
                      {pathwayChips.length && !minimal && !hideSecondaryNav ? (
                        <div className={styles.pathwayRow} role="group" aria-label="Other ways to practice">
                          <span className="muted small">Try another way:</span>
                          {pathwayChips.map((p) => (
                            <button
                              key={p.id}
                              type="button"
                              className={styles.pathwayChip}
                              onClick={() =>
                                setHelpNotice(`Use the main work area for ${p.label.toLowerCase()}.`)
                              }
                            >
                              {p.label}
                            </button>
                          ))}
                        </div>
                      ) : null}
                    </div>
                  ) : null}

                  {helpNotice ? <p className="muted small">{helpNotice}</p> : null}

                  {(!minimal || verificationBlocked) ? (
                    <details className={styles.rewriteFold} open={verificationBlocked || undefined}>
                      <summary>Adjust this step</summary>
                      <div className={styles.rewriteGrid}>
                        {REWRITE_MODES.map((b) => (
                          <button
                            key={b.mode}
                            type="button"
                            className="btn session-help__btn"
                            disabled={busy}
                            onClick={() => void handleRewrite(b.mode)}
                          >
                            {professional ? b.proLabel : b.label}
                          </button>
                        ))}
                      </div>
                    </details>
                  ) : null}
                </div>
              )}

              <div className={styles.artifactBlock}>
                <ArtifactPreviewPanel
                  preview={artifactPreview}
                  liveSections={liveSections}
                  hasContent={hasArtifact}
                  defaultOpen={hasArtifact}
                />
              </div>
            </div>

            <aside className={styles.sessionLayout__aside}>
              <SessionStepTrail contract={contract} variant={focusLayout ? 'minimal' : 'default'} />
            </aside>
          </div>

          {exportText ? (
            <pre className="export-preview" aria-label="Exported content">
              {exportText}
            </pre>
          ) : null}
        </>
      ) : null}
    </div>
  );
}

function CompletionBlock({
  task,
  exportText,
  exportCopied,
  busy,
  onExport,
  onCopy,
}: {
  task: string;
  exportText: string | null;
  exportCopied: boolean;
  busy: boolean;
  onExport: () => void;
  onCopy: () => void;
}) {
  return (
    <section className="session-complete">
      <span className="session-step__eyebrow">Finished</span>
      <h2 className="session-step__title">You finished &ldquo;{task}&rdquo;.</h2>
      <p className="muted">Save a copy below, or start something new when you are ready.</p>
      <div className="session-complete__actions">
        <button type="button" className="btn btn-primary btn-lg" onClick={onExport} disabled={busy}>
          {exportText ? 'Refresh export' : 'Export'}
        </button>
        {exportText ? (
          <button type="button" className="btn" onClick={onCopy} disabled={busy}>
            {exportCopied ? 'Copied' : 'Copy'}
          </button>
        ) : null}
        <Link className="btn btn-quiet" to="/start">
          Start a new Bridge
        </Link>
      </div>
      {exportText ? <pre className="export-preview">{exportText}</pre> : null}
    </section>
  );
}
