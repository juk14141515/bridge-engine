import type { NormalizedRuntimeContract } from '../../lib/runtimeContract';
import { getCheckpointMessage, requiresUserOutput } from '../../lib/runtimeContract';
import styles from './WorkspaceRuntime.module.css';

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

  return (
    <section className="session-write" aria-label="Your work">
      {checkpoint ? <p className={styles.checkpoint}>{checkpoint}</p> : null}
      <label className="session-write__label" htmlFor="session-draft">
        Your work for this step
      </label>
      <textarea
        id="session-draft"
        className="session-write__textarea"
        rows={5}
        placeholder="Type something rough. One sentence is enough."
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
