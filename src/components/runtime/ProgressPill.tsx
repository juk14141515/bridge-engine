import styles from './WorkspaceRuntime.module.css';

export function ProgressPill({
  done,
  total,
  percent,
}: {
  done: number;
  total: number;
  percent: number;
}) {
  if (total <= 0) return null;
  return (
    <div className={styles.progressPill} role="status" aria-label={`Progress ${percent} percent`}>
      <span>
        {done} of {total}
      </span>
      <span className={styles.progressPill__meter} aria-hidden>
        <span style={{ width: `${Math.min(100, percent)}%` }} />
      </span>
    </div>
  );
}
