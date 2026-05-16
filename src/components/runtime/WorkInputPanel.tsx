import type { NormalizedRuntimeContract } from '../../lib/runtimeContract';
import {
  getCheckpointMessage,
  getInteractionTone,
  getRuntimeDensity,
  requiresUserOutput,
} from '../../lib/runtimeContract';
import styles from './WorkspaceRuntime.module.css';

function workLabel(tone: ReturnType<typeof getInteractionTone>): string {
  if (tone === 'professional') return 'Your output for this step';
  if (tone === 'gentle') return 'A few words are enough';
  return 'Your work for this step';
}

function placeholderFor(
  tone: ReturnType<typeof getInteractionTone>,
  density: ReturnType<typeof getRuntimeDensity>,
): string {
  if (density === 'low') return 'One sentence is enough.';
  if (tone === 'professional') return 'Draft the smallest useful fragment.';
  if (tone === 'gentle') return 'Rough notes are fine — no polish needed.';
  return 'Type something rough. One sentence is enough.';
}

export function WorkInputPanel({
  contract,
  draft,
  onDraftChange,
  onContinue,
  busy,
  disabled,
}: {
  contract: NormalizedRuntimeContract;
  draft: string;
  onDraftChange: (value: string) => void;
  onContinue: () => void;
  busy: boolean;
  disabled?: boolean;
}) {
  const checkpoint = getCheckpointMessage(contract);
  const needsOutput = requiresUserOutput(contract);
  const canContinue = !needsOutput || draft.trim().length > 0;
  const tone = getInteractionTone(contract);
  const density = getRuntimeDensity(contract);
  const rows = density === 'low' ? 4 : density === 'immersive' ? 6 : 5;

  return (
    <section
      className={[
        'session-write',
        styles.workInputShell,
        styles[`workInputShell--density-${density}`],
      ].join(' ')}
      aria-label="Your work"
    >
      {checkpoint ? <p className={styles.checkpoint}>{checkpoint}</p> : null}
      <label className="session-write__label" htmlFor="session-draft">
        {workLabel(tone)}
      </label>
      <textarea
        id="session-draft"
        className="session-write__textarea"
        rows={rows}
        placeholder={placeholderFor(tone, density)}
        value={draft}
        onChange={(e) => onDraftChange(e.target.value)}
        disabled={busy || disabled}
      />
      <div className="session-write__actions">
        <button
          type="button"
          className="btn btn-primary btn-lg btn-block session-write__cta"
          onClick={onContinue}
          disabled={busy || disabled || !canContinue}
        >
          {busy ? 'Saving…' : 'Save and continue'}
        </button>
      </div>
    </section>
  );
}
