import type { NormalizedRuntimeContract } from '../../lib/runtimeContract';
import {
  getImmersionNarrative,
  getPrimaryStep,
  shouldShowNextStepFirst,
} from '../../lib/runtimeContract';

export function PrimaryStepCard({ contract }: { contract: NormalizedRuntimeContract }) {
  const step = getPrimaryStep(contract);
  const dominant = shouldShowNextStepFirst(contract);
  const narrative = getImmersionNarrative(contract);

  if (!step.title && !step.prompt) {
    return (
      <section className="session-step" aria-label="Current step" aria-busy="true">
        <span className="session-step__eyebrow">Your next step</span>
        <p className="muted small">Loading your next step…</p>
      </section>
    );
  }

  return (
    <section
      className={`session-step ${dominant ? 'session-step--dominant' : ''}`}
      aria-label="Current step"
    >
      <span className="session-step__eyebrow">Your next step</span>
      {narrative ? <p className="session-step__why session-step__continuity">{narrative}</p> : null}
      <h2 className="session-step__title">{step.title}</h2>
      {step.why ? <p className="session-step__why">{step.why}</p> : null}
      <p className="session-step__prompt session-step__prompt--live">{step.prompt}</p>
      {step.action ? (
        <p className="session-step__action">
          <span className="session-step__action-label">Done when</span>
          {step.action}
        </p>
      ) : null}
    </section>
  );
}
