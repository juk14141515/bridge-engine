import type { VisibleInteractionCard } from '../../lib/runtimeContract';
import styles from './WorkspaceRuntime.module.css';

export function RuntimeInteractionCard({
  card,
  onAction,
}: {
  card: VisibleInteractionCard;
  onAction?: () => void;
}) {
  return (
    <div className={styles.interactionCard}>
      <p className={styles.interactionCard__title}>{card.title}</p>
      <p className={styles.interactionCard__sub}>{card.subtitle}</p>
      <button type="button" className={`btn btn-quiet ${styles.interactionCard__cta}`} onClick={onAction}>
        {card.cta}
      </button>
    </div>
  );
}
