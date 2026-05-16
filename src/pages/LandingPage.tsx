import { useNavigate } from 'react-router-dom';
import styles from './LandingPage.module.css';

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className={styles.wrap}>
      <div className={styles.inner}>
        <h1 className={styles.h1}>Finish hard things through what you already like.</h1>
        <p className={styles.p}>
          Bridge turns work, learning, and projects into step-by-step paths shaped around your interests.
        </p>

        <div className="bridge-transform-row" aria-label="How Bridge works">
          <span>Hard thing</span>
          <span aria-hidden>→</span>
          <span>Interest</span>
          <span aria-hidden>→</span>
          <span>Finished path</span>
        </div>

        <ul className={styles.exampleStrip} aria-label="Examples">
          <li className={styles.exampleItem}>Essay → Gaming → Quest path to finished draft</li>
          <li className={styles.exampleItem}>Spanish → Music → Phrases, rhythm, speaking practice</li>
          <li className={styles.exampleItem}>Project → Coding → Build path to completion</li>
          <li className={styles.exampleItem}>Hard conversation → Fitness → Warmup, reps, talking plan</li>
        </ul>

        <div className={styles.ctaRow}>
          <button type="button" className="btn btn-primary btn-lg" onClick={() => navigate('/start')}>
            Start Bridge
          </button>
          <button type="button" className="btn btn-quiet" onClick={() => navigate('/home')}>
            Sessions
          </button>
          <button type="button" className="btn btn-quiet" onClick={() => navigate('/login')}>
            Sign in
          </button>
        </div>
      </div>
    </div>
  );
}
