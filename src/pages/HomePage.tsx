import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { formatUserApiError, sessionTaskLabel } from '../lib/displayLabels';
import { fetchRecentWorkspaces, type RecentWorkspaceSummary } from '../lib/sessionApi';
import { frameTitle, frameEmoji } from '../lib/onboardingOptions';

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
      setError(formatUserApiError(e, 'Could not load sessions.'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="home-page">
      <h1 className="home-title">Sessions</h1>
      <p className="home-lede">
        Resume a hard thing being translated through an interest, or start a new Bridge.
      </p>
      <div className="home-cta-row">
        <button
          type="button"
          className="btn btn-primary btn-lg btn-block home-cta-primary"
          onClick={() => navigate('/start')}
        >
          Start Bridge
        </button>
        <Link className="btn btn-quiet home-cta-customize" to="/">
          How Bridge works
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
            No sessions yet. Pick a hard thing, pick an interest, and Bridge will build the path.
          </p>
        ) : null}

        <ul className="recent-list">
          {workspaces.map((w) => {
            const done = w.progress_done ?? 0;
            const total = w.progress_total ?? 0;
            const pct = total ? Math.round((done / total) * 100) : 0;
            const updated = formatUpdated(w.updated_at);
            const taskLabel = sessionTaskLabel(w.task, w.title);
            const fEmoji = frameEmoji(w.frame);
            const fTitle = frameTitle(w.frame);
            const isComplete = (w.status ?? '').toLowerCase() === 'complete';
            return (
              <li key={w.id}>
                <Link className="recent-card" to={`/workspace/${w.id}`}>
                  <div className="recent-card__main">
                    <span className="recent-card__title">{taskLabel} → {fTitle}</span>
                    <span className="recent-card__meta">
                      {fEmoji ? (
                        <>
                          <span aria-hidden>{fEmoji}</span> Continue
                        </>
                      ) : (
                        'Continue'
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
                        {done} of {total} steps complete
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
