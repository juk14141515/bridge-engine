import { getStepTrail, type NormalizedRuntimeContract } from '../../lib/runtimeContract';
import styles from './WorkspaceRuntime.module.css';

export function SessionStepTrail({ contract }: { contract: NormalizedRuntimeContract }) {
  const trail = getStepTrail(contract);
  if (trail.length < 2) return null;

  return (
    <nav className={styles.stepTrail} aria-label="Session progress">
      <p className={styles.stepTrail__label}>Your path</p>
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
