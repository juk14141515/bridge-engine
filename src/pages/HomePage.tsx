import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ApiError } from '../lib/runtimeApi';
import { fetchRecentWorkspaces, type RecentWorkspaceSummary } from '../lib/sessionApi';
import {
  FRAME_CHIPS,
  SURPRISE_FRAME_ID,
  frameTitle,
  frameEmoji,
} from '../lib/onboardingOptions';

function formatUpdated(iso?: string): string {
  if (!iso) return '';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '';
  const now = Date.now();
  const diff = now - d.getTime();
  const minute = 60_000;
  const hour = 60 * minute;
  const day = 24 * hour;
  if (diff < minute) return 'just now';
  if (diff < hour) return `${Math.floor(diff / minute)}m ago`;
  if (diff < day) return `${Math.floor(diff / hour)}h ago`;
  if (diff < 7 * day) return `${Math.floor(diff / day)}d ago`;
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

export default function HomePage() {
  const navigate = useNavigate();
  const [task, setTask] = useState('');
  const [frame, setFrame] = useState<string | null>(null);
  const [workspaces, setWorkspaces] = useState<RecentWorkspaceSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchRecentWorkspaces();
      setWorkspaces(data.workspaces ?? []);
    } catch (e) {
      const msg =
        e instanceof ApiError
          ? e.status === 0
            ? 'Backend not reachable. Start it on port 6060.'
            : e.message
          : 'Could not load sessions.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  function start() {
    const t = task.trim();
    if (t.length < 3) {
      navigate('/start', frame ? { state: { initialFrame: frame } } : undefined);
      return;
    }
    navigate('/start', { state: { initialTask: t, initialFrame: frame ?? undefined } });
  }

  return (
    <div className="home-page">
      <h1 className="home-title">Turn hard things into something your brain can enter.</h1>
      <p className="home-lede">
        One input, one frame, one session. Bridge translates the hard thing through something you
        already enjoy and walks you through it.
      </p>

      <textarea
        className="home-input"
        rows={2}
        placeholder="What do you want to learn, finish, or get through?"
        value={task}
        onChange={(e) => setTask(e.target.value)}
        aria-label="What do you want to learn, finish, or get through?"
      />

      <div className="frame-chip-row">
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

      <div className="home-cta-row">
        <button
          type="button"
          className="btn btn-primary btn-lg btn-block home-cta-primary"
          onClick={start}
        >
          Start Bridge
        </button>
        <Link className="btn btn-quiet home-cta-customize" to="/start">
          Customize more
        </Link>
      </div>

      <section className="recent-section">
        <header className="recent-section__head">
          <h2 className="recent-section__title">Recent sessions</h2>
          {workspaces.length ? (
            <button type="button" className="btn btn-quiet" onClick={() => void load()} disabled={loading}>
              {loading ? 'Refreshing…' : 'Refresh'}
            </button>
          ) : null}
        </header>

        {error ? (
          <div className="banner-gentle" role="status">
            {error}{' '}
            <button type="button" className="btn btn-quiet" onClick={() => void load()}>
              Retry
            </button>
          </div>
        ) : null}

        {loading && !workspaces.length ? <p className="muted small">Loading…</p> : null}

        {!loading && !workspaces.length && !error ? (
          <p className="muted small recent-empty">
            No sessions yet. Type something above and start one.
          </p>
        ) : null}

        <ul className="recent-list">
          {workspaces.map((w) => {
            const done = w.progress_done ?? 0;
            const total = w.progress_total ?? 0;
            const pct = total ? Math.round((done / total) * 100) : 0;
            const updated = formatUpdated(w.updated_at);
            const taskLabel = (w.task && w.task.trim()) || (w.title && w.title.trim()) || 'Untitled';
            const fEmoji = frameEmoji(w.frame);
            const fTitle = frameTitle(w.frame);
            const isComplete = (w.status ?? '').toLowerCase() === 'complete';
            return (
              <li key={w.id}>
                <Link className="recent-card" to={`/workspace/${w.id}`}>
                  <div className="recent-card__main">
                    <span className="recent-card__title">{taskLabel}</span>
                    <span className="recent-card__meta">
                      {fEmoji ? (
                        <>
                          <span aria-hidden>{fEmoji}</span> {fTitle}
                        </>
                      ) : (
                        fTitle || '—'
                      )}
                      {updated ? <span className="recent-card__dot"> · </span> : null}
                      {updated}
                      {isComplete ? (
                        <span className="recent-card__pill recent-card__pill--done">Finished</span>
                      ) : null}
                    </span>
                  </div>
                  {total > 0 && !isComplete ? (
                    <div className="recent-card__progress">
                      <div className="meter meter--thin">
                        <span style={{ width: `${pct}%` }} />
                      </div>
                      <span className="muted small recent-card__progress-label">
                        {done}/{total}
                      </span>
                    </div>
                  ) : null}
                </Link>
              </li>
            );
          })}
        </ul>
      </section>
    </div>
  );
}
