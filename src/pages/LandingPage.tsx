import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { QuickStartBar } from '../components/QuickStartBar';
import { FRAME_CHIPS, SURPRISE_FRAME_ID } from '../lib/onboardingOptions';
import {
  PRODUCT_EYEBROW,
  PRODUCT_EXAMPLE_CALLOUT_BODY,
  PRODUCT_EXAMPLE_CALLOUT_TITLE,
  PRODUCT_CHIP_SECTION_LABEL,
  PRODUCT_HERO_LEDE,
  PRODUCT_HERO_TITLE,
} from '../lib/productPitch';
import styles from './LandingPage.module.css';

export function LandingPage() {
  const navigate = useNavigate();
  const [task, setTask] = useState('');
  const [frame, setFrame] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function startNow() {
    const t = task.trim();
    if (t.length < 3) {
      navigate('/start', { state: frame ? { initialFrame: frame } : undefined });
      return;
    }
    navigate('/start', { state: { initialTask: t, initialFrame: frame ?? undefined } });
  }

  return (
    <div className={styles.wrap}>
      <div className={styles.inner}>
        <p className="pitch-eyebrow">{PRODUCT_EYEBROW}</p>
        <h1 className={styles.h1}>{PRODUCT_HERO_TITLE}</h1>
        <p className={styles.p}>{PRODUCT_HERO_LEDE}</p>

        <aside className="pitch-callout" aria-label="Example">
          <p className="pitch-callout__title">{PRODUCT_EXAMPLE_CALLOUT_TITLE}</p>
          <p className="pitch-callout__body">{PRODUCT_EXAMPLE_CALLOUT_BODY}</p>
        </aside>

        <QuickStartBar onError={setError} />

        {error ? (
          <div className="banner-gentle" role="status">
            {error}
          </div>
        ) : null}

        <p className={styles.or}>Or write your own</p>

        <textarea
          className={styles.textarea}
          rows={3}
          placeholder="Something you need to finish or get through"
          value={task}
          onChange={(e) => setTask(e.target.value)}
          aria-label="Something you need to finish or get through"
        />

        <p className="chip-section-label">{PRODUCT_CHIP_SECTION_LABEL}</p>

        <div className={styles.chipRow}>
          {FRAME_CHIPS.map((f) => (
            <button
              key={f.id}
              type="button"
              className={`frame-chip ${frame === f.id ? 'frame-chip--active' : ''}`}
              onClick={() => setFrame((prev) => (prev === f.id ? null : f.id))}
              aria-pressed={frame === f.id}
            >
              <span className="frame-chip__emoji" aria-hidden>
                {f.emoji}
              </span>
              <span className="frame-chip__title">{f.title}</span>
            </button>
          ))}
          <button
            type="button"
            className={`frame-chip frame-chip--surprise ${frame === SURPRISE_FRAME_ID ? 'frame-chip--active' : ''}`}
            onClick={() =>
              setFrame((prev) => (prev === SURPRISE_FRAME_ID ? null : SURPRISE_FRAME_ID))
            }
            aria-pressed={frame === SURPRISE_FRAME_ID}
          >
            <span className="frame-chip__emoji" aria-hidden>
              ✨
            </span>
            <span className="frame-chip__title">Surprise me</span>
          </button>
        </div>

        <div className={styles.ctaRow}>
          <button type="button" className="btn btn-primary btn-lg" onClick={startNow}>
            Start now
          </button>
          <button type="button" className="btn btn-quiet" onClick={() => navigate('/home')}>
            Continue a session
          </button>
        </div>
      </div>
    </div>
  );
}
