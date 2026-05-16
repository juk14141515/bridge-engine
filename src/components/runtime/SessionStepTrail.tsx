import { getStepTrail, type NormalizedRuntimeContract } from '../../lib/runtimeContract';
import styles from './WorkspaceRuntime.module.css';

export function SessionStepTrail({
  contract,
  variant = 'default',
}: {
  contract: NormalizedRuntimeContract;
  variant?: 'default' | 'minimal';
}) {
  const trail = getStepTrail(contract);
  if (trail.length < 2) return null;

  return (
    <nav
      className={`${styles.stepTrail} ${variant === 'minimal' ? styles.stepTrailMinimal : ''}`}
      aria-label="Session progress"
    >
      <p className={styles.stepTrail__label}>{variant === 'minimal' ? 'Progress' : 'Your path'}</p>
      <ol className={styles.stepTrail__list}>
        {trail.map((item) => (
          <li
            key={item.id}
            className={`${styles.stepTrail__item} ${styles[`stepTrail__item--${item.status}`]}`}
          >
            <span className={styles.stepTrail__marker} aria-hidden />
            <span className={styles.stepTrail__title}>{item.title}</span>
          </li>
        ))}
      </ol>
    </nav>
  );
}
