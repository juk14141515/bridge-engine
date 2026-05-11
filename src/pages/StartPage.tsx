import { useEffect, useMemo, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ApiError } from '../lib/runtimeApi';
import { createSession } from '../lib/sessionApi';
import {
  EXTRA_FRAMES,
  FRAME_CHIPS,
  SUPPORT_CHIPS,
  SURPRISE_FRAME_ID,
  pickSurpriseFrame,
} from '../lib/onboardingOptions';

interface LocationState {
  initialTask?: string;
  initialFrame?: string;
}

const PLACEHOLDERS: ReadonlyArray<string> = [
  'I have an English essay due and I hate writing',
  'I want to learn Spanish but keep stalling',
  'Finish my coding project before it bit-rots',
  'Prepare for the hard conversation I keep avoiding',
  'Draft a product strategy memo',
  'Get my room back to baseline',
];

function pickPlaceholder(): string {
  const i = Math.floor(Math.random() * PLACEHOLDERS.length);
  return PLACEHOLDERS[i] ?? PLACEHOLDERS[0];
}

export default function StartPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const initial = (location.state as LocationState | null) ?? {};

  const [task, setTask] = useState(initial.initialTask ?? '');
  const [frame, setFrame] = useState<string | null>(initial.initialFrame ?? null);
  const [supports, setSupports] = useState<Set<string>>(() => new Set());
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [placeholder] = useState<string>(pickPlaceholder);

  useEffect(() => {
    const ls = location.state as LocationState | null;
    if (ls?.initialTask && !task) setTask(ls.initialTask);
    if (ls?.initialFrame && !frame) setFrame(ls.initialFrame);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state]);

  const canStart = useMemo(() => task.trim().length >= 3, [task]);

  function toggleSupport(id: string) {
    setSupports((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function start() {
    const trimmed = task.trim();
    if (trimmed.length < 3 || busy) return;

    const resolvedFrame =
      !frame || frame === SURPRISE_FRAME_ID ? pickSurpriseFrame() : frame;

    setBusy(true);
    setError(null);
    try {
      const prefs = Array.from(supports);
      const envelope = await createSession({
        task: trimmed,
        frame: resolvedFrame,
        supports: prefs.length ? prefs : ['step_by_step'],
        user_words: trimmed,
      });
      navigate(`/workspace/${envelope.workspace.id}`, { replace: true });
    } catch (e) {
      const msg =
        e instanceof ApiError
          ? e.status === 0
            ? 'Backend not reachable on port 6060. Start it and try again.'
            : e.message
          : 'Could not start your Bridge.';
      setError(msg);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="fast-entry">
      <header className="fast-entry__top">
        <Link className="btn btn-quiet" to="/home">
          ← Workspaces
        </Link>
      </header>

      <h1 className="fast-entry__title">Turn hard things into something your brain can enter.</h1>
      <p className="fast-entry__lede">
        Drop in something you want to learn, finish, or get through. Bridge will translate it
        through something you already enjoy.
      </p>

      <label className="fast-entry__label" htmlFor="bridge-task">
        What do you want to learn, finish, or get through?
      </label>
      <textarea
        id="bridge-task"
        className="fast-entry__input"
        rows={3}
        value={task}
        onChange={(e) => setTask(e.target.value)}
        placeholder={placeholder}
        autoFocus
      />

      <p className="fast-entry__sub">Translate through</p>
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
          onClick={() => setFrame((prev) => (prev === SURPRISE_FRAME_ID ? null : SURPRISE_FRAME_ID))}
          aria-pressed={frame === SURPRISE_FRAME_ID}
        >
          <span className="frame-chip__emoji" aria-hidden>
            ✨
          </span>
          <span className="frame-chip__title">Surprise me</span>
        </button>
      </div>
      <p className="fast-entry__hint muted small">Optional — leave blank and we'll choose one for you.</p>

      {error ? (
        <div className="banner-gentle" role="status">
          {error}
        </div>
      ) : null}

      <div className="fast-entry__cta">
        <button
          type="button"
          className="btn btn-primary btn-lg btn-block fast-entry__primary"
          disabled={!canStart || busy}
          onClick={() => void start()}
        >
          {busy ? 'Opening…' : 'Start Bridge'}
        </button>
        <button
          type="button"
          className="btn btn-quiet fast-entry__customize"
          onClick={() => setAdvancedOpen((v) => !v)}
          aria-expanded={advancedOpen}
        >
          {advancedOpen ? 'Hide customization' : 'Customize more'}
        </button>
      </div>

      {advancedOpen ? (
        <section className="customize-panel">
          <h2 className="customize-panel__title">Customize how this feels</h2>
          <p className="customize-panel__lede muted small">
            All optional. Bridge already adapts; these just tilt the tone.
          </p>

          <p className="customize-panel__label">Make it feel right</p>
          <div className="chip-grid">
            {SUPPORT_CHIPS.map((s) => (
              <button
                key={s.id}
                type="button"
                className={`support-chip ${supports.has(s.id) ? 'support-chip--active' : ''}`}
                onClick={() => toggleSupport(s.id)}
                aria-pressed={supports.has(s.id)}
              >
                <span className="support-chip__emoji" aria-hidden>
                  {s.emoji}
                </span>
                <span className="support-chip__body">
                  <span className="support-chip__title">{s.title}</span>
                  <span className="support-chip__desc">{s.desc}</span>
                </span>
              </button>
            ))}
          </div>

          <p className="customize-panel__label">More frames</p>
          <div className="frame-chip-row">
            {EXTRA_FRAMES.map((f) => (
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
          </div>
        </section>
      ) : null}
    </div>
  );
}
