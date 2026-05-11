import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ApiError } from '../lib/runtimeApi';
import { fetchRecentWorkspaces, type RecentWorkspaceSummary } from '../lib/sessionApi';

function formatUpdated(iso?: string): string {
  if (!iso) return '';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

export default function HomePage() {
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
            ? 'Backend not reachable. Start Flask on http://127.0.0.1:6060 and retry.'
            : e.message
          : 'Something went wrong loading workspaces.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <>
      <header className="top-bar">
        <div className="row" style={{ alignItems: 'center', gap: 14 }}>
          <span className="brand brand--soft">Bridge</span>
          <Link className="btn btn-quiet" style={{ fontSize: 13 }} to="/">
            About
          </Link>
        </div>
        <Link className="btn btn-quiet" to="/new">
          Advanced form
        </Link>
      </header>

      <h1 className="h1 home-hero-title">Finish hard things through what you already enjoy.</h1>
      <p className="lede home-hero-lede">
        Bridge is an adaptive completion workspace—not a static checklist. Each session tracks momentum,
        suggests the next move, grows an artifact you can see, and persists on this machine.
      </p>

      <div className="surface home-actions-panel">
        <div className="home-actions-row">
          <div>
            <h2 className="home-section-heading">Start</h2>
            <p className="muted small" style={{ margin: '4px 0 0' }}>
              Guided setup, then a live workspace with continue, rewrite, and export.
            </p>
          </div>
          <div className="row">
            <Link className="btn btn-primary btn-lg" to="/start">
              New Bridge
            </Link>
            <button type="button" className="btn btn-secondary" onClick={() => void load()} disabled={loading}>
              {loading ? 'Refreshing…' : 'Refresh list'}
            </button>
          </div>
        </div>
      </div>

      <div className="surface home-recent-panel">
        <h2 className="home-section-heading">Recent workspaces</h2>
        {error ? (
          <div className="banner-gentle" role="status">
            {error}
          </div>
        ) : null}
        {loading && !workspaces.length ? (
          <p className="muted small">Loading…</p>
        ) : null}
        {!loading && !workspaces.length && !error ? (
          <p className="muted small">
            Nothing yet. <Link to="/start">Start a Bridge</Link>.
          </p>
        ) : null}
        <div className="home-lane-list">
          {workspaces.map((w) => {
            const done = w.progress_done ?? 0;
            const total = w.progress_total ?? 0;
            const pct = total ? Math.round((done / total) * 100) : 0;
            const updated = formatUpdated(w.updated_at);
            return (
              <Link key={w.id} className="home-lane-card" to={`/workspace/${w.id}`}>
                <div className="home-lane-card__top">
                  <strong className="home-lane-card__title">{w.title || w.task || 'Untitled'}</strong>
                  <span className="home-lane-card__badge">{w.frame ?? '—'}</span>
                </div>
                <div className="home-lane-card__meta muted small">
                  {w.status ?? 'active'}
                  {updated ? ` · Updated ${updated}` : ''}
                </div>
                {total > 0 ? (
                  <div className="home-lane-progress">
                    <div className="meter meter--thin">
                      <span style={{ width: `${pct}%` }} />
                    </div>
                    <span className="muted small">
                      {done}/{total} checkpoints
                    </span>
                  </div>
                ) : null}
              </Link>
            );
          })}
        </div>
      </div>

      <details className="fine-print">
        <summary>Local dev</summary>
        <p className="muted small" style={{ marginTop: 10 }}>
          API proxy → port 6060. Workspaces: SQLite <code>data/bridge_engine.db</code> via the runtime API.
        </p>
      </details>
    </>
  );
}
