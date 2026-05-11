import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { FRAME_CHIPS, SURPRISE_FRAME_ID } from '../lib/onboardingOptions';
import styles from './LandingPage.module.css';

const examples = [
  { hard: 'English essay', through: 'Gaming', emoji: '🎮' },
  { hard: 'Learn Spanish', through: 'Music', emoji: '🎧' },
  { hard: 'Finish my project', through: 'Systems', emoji: '🧠' },
  { hard: 'Strategy memo', through: 'Investing', emoji: '📈' },
  { hard: 'Hard conversation', through: 'Care', emoji: '🤝' },
];

export function LandingPage() {
  const navigate = useNavigate();
  const [task, setTask] = useState('');
  const [frame, setFrame] = useState<string | null>(null);

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
        <h1 className={styles.h1}>Turn hard things into something your brain can enter.</h1>
        <p className={styles.p}>
          Drop in something you want to learn, finish, or get through. Bridge translates it
          through something you already enjoy — and walks you through it.
        </p>

        <textarea
          className={styles.textarea}
          rows={3}
          placeholder="What do you want to learn, finish, or get through?"
          value={task}
          onChange={(e) => setTask(e.target.value)}
          aria-label="What do you want to learn, finish, or get through?"
        />

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
            Start Bridge
          </button>
          <button type="button" className="btn btn-quiet" onClick={() => navigate('/home')}>
            Continue a session
          </button>
        </div>

        <ul className={styles.exampleStrip}>
          {examples.map((ex) => (
            <li key={ex.hard} className={styles.exampleItem}>
              <span className={styles.exampleHard}>{ex.hard}</span>
              <span className={styles.exampleArrow}>→</span>
              <span className={styles.exampleThrough}>
                <span aria-hidden>{ex.emoji}</span> {ex.through}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
