import type { NormalizedRuntimeContract } from '../../lib/runtimeContract';
import {
  getImmersionNarrative,
  getInteractionTone,
  getPrimaryStep,
  getRewardNotice,
  getRuntimeDensity,
  shouldShowNextStepFirst,
} from '../../lib/runtimeContract';
import styles from './WorkspaceRuntime.module.css';

function eyebrowForTone(tone: ReturnType<typeof getInteractionTone>): string {
  switch (tone) {
    case 'professional':
      return 'Next move';
    case 'gentle':
      return 'Tiny next move';
    case 'focused':
      return 'Stay with it';
    default:
      return 'Your next step';
  }
}

export function PrimaryStepCard({ contract }: { contract: NormalizedRuntimeContract }) {
  const step = getPrimaryStep(contract);
  const dominant = shouldShowNextStepFirst(contract);
  const narrative = getImmersionNarrative(contract);
  const density = getRuntimeDensity(contract);
  const tone = getInteractionTone(contract);
  const rewardLine = getRewardNotice(contract);

  if (!step.title && !step.prompt) {
    return (
      <section className="session-step" aria-label="Current step" aria-busy="true">
        <span className="session-step__eyebrow">{eyebrowForTone(tone)}</span>
        <p className="muted small">Loading your next step…</p>
      </section>
    );
  }

  const showNarrative = Boolean(narrative && density !== 'low');
  const showWhy = Boolean(step.why && density !== 'low');

  return (
    <section
      className={[
        'session-step',
        dominant ? 'session-step--dominant' : '',
        styles.primaryStepShell,
        styles[`primaryStepShell--density-${density}`],
        styles[`primaryStepShell--tone-${tone}`],
      ]
        .filter(Boolean)
        .join(' ')}
      aria-label="Current step"
    >
      <span className="session-step__eyebrow">{eyebrowForTone(tone)}</span>
      {showNarrative ? (
        <p className={`session-step__why session-step__continuity ${styles.primaryStepContinuity}`}>
          {narrative}
        </p>
      ) : null}
      <h2 className={`session-step__title ${styles.primaryStepTitle}`}>{step.title}</h2>
      {showWhy ? <p className="session-step__why">{step.why}</p> : null}
      <p className={`session-step__prompt session-step__prompt--live ${styles.primaryStepPrompt}`}>
        {step.prompt}
      </p>
      {step.action ? (
        <p className={`session-step__action ${styles.primaryStepAction}`}>
          <span className="session-step__action-label">Finish line</span>
          {step.action}
        </p>
      ) : null}
      {rewardLine && density !== 'low' ? (
        <p className={`muted small ${styles.primaryStepReward}`} role="status">
          {rewardLine}
        </p>
      ) : null}
    </section>
  );
}
