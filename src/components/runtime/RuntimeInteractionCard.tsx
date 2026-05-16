import type { InteractionAtmosphere, VisibleInteractionCard } from '../../lib/runtimeContract';
import styles from './WorkspaceRuntime.module.css';

const ATMOSPHERE_LABEL: Record<InteractionAtmosphere, string> = {
  simulation: 'Practice scene',
  voice: 'Speaking',
  challenge: 'Focused round',
  checkpoint: 'Checkpoint',
  reflection: 'Reflection',
  quest: 'Mission beat',
  boss_battle: 'Final stretch',
  teach_back: 'Explain it simply',
  conversational: 'Conversation',
  default: 'Extra support',
};

export function RuntimeInteractionCard({
  card,
  onAction,
}: {
  card: VisibleInteractionCard;
  onAction?: () => void;
}) {
  const a = card.atmosphere ?? 'default';
  const ribbon = ATMOSPHERE_LABEL[a] ?? ATMOSPHERE_LABEL.default;

  return (
    <div
      className={`${styles.interactionCard} ${styles[`interactionCard--${a}`]}`}
      data-atmosphere={a}
    >
      <p className={styles.interactionCard__ribbon}>{ribbon}</p>
      <p className={styles.interactionCard__title}>{card.title}</p>
      <p className={styles.interactionCard__sub}>{card.subtitle}</p>
      <button type="button" className={`btn btn-quiet ${styles.interactionCard__cta}`} onClick={onAction}>
        {card.cta}
      </button>
    </div>
  );
}
