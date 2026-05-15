import { useEffect, useMemo, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { formatUserApiError } from '../lib/displayLabels';
import { QuickStartBar } from '../components/QuickStartBar';
import { openBridgeSession } from '../lib/startBridgeSession';
import {
  EXTRA_FRAMES,
  FRAME_CHIPS,
  SUPPORT_CHIPS,
  SURPRISE_FRAME_ID,
  frameTitle,
  frameTranslationPreview,
} from '../lib/onboardingOptions';
import {
  PRODUCT_EYEBROW,
  PRODUCT_EXAMPLE_CALLOUT_BODY,
  PRODUCT_EXAMPLE_CALLOUT_TITLE,
  PRODUCT_CHIP_SECTION_LABEL,
  PRODUCT_HERO_LEDE,
  PRODUCT_HERO_TITLE,
} from '../lib/productPitch';

interface LocationState {
  initialTask?: string;
  initialFrame?: string;
}

const PLACEHOLDERS: ReadonlyArray<string> = [
  'I owe a paper and I keep putting it off',
  'I want to learn Spanish but I never start',
  'I need to finish a project and I’m stuck',
  'I have a hard talk coming and I’m avoiding it',
  'I need a clear memo for work',
  'My room is a mess and I don’t know where to begin',
];

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
  const [phIndex, setPhIndex] = useState(0);

  useEffect(() => {
    const ls = location.state as LocationState | null;
    if (ls?.initialTask && !task) setTask(ls.initialTask);
    if (ls?.initialFrame && !frame) setFrame(ls.initialFrame);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state]);

  useEffect(() => {
    if (task.trim().length > 0) return;
    const id = window.setInterval(() => {
      setPhIndex((i) => (i + 1) % PLACEHOLDERS.length);
    }, 4200);
    return () => window.clearInterval(id);
  }, [task]);

  const canStart = useMemo(() => task.trim().length >= 3, [task]);
  const supportList = useMemo(() => Array.from(supports), [supports]);

  const composerClass =
    frame === SURPRISE_FRAME_ID
      ? 'fast-entry__composer fast-entry__composer--surprise'
      : frame
        ? 'fast-entry__composer fast-entry__composer--framed'
        : 'fast-entry__composer';

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

    setBusy(true);
    setError(null);
    try {
      const { workspaceId, ribbon, initialContract } = await openBridgeSession({
        task: trimmed,
        frame,
        supports: supportList.length ? supportList : undefined,
      });
      navigate(`/workspace/${workspaceId}`, {
        replace: true,
        state: { entryRibbon: ribbon, initialContract },
      });
    } catch (e) {
      setError(formatUserApiError(e, 'Could not start. Try again.'));
    } finally {
      setBusy(false);
    }
  }

  const previewFrame = frame && frame !== SURPRISE_FRAME_ID ? frame : null;
  const previewText = previewFrame ? frameTranslationPreview(previewFrame) : '';

  return (
    <div className="fast-entry">
      <header className="fast-entry__top">
        <Link className="btn btn-quiet" to="/home">
          ← Sessions
        </Link>
      </header>

      <p className="pitch-eyebrow">{PRODUCT_EYEBROW}</p>
      <h1 className="fast-entry__title">{PRODUCT_HERO_TITLE}</h1>
      <p className="fast-entry__lede">{PRODUCT_HERO_LEDE}</p>

      <aside className="pitch-callout" aria-label="Example">
        <p className="pitch-callout__title">{PRODUCT_EXAMPLE_CALLOUT_TITLE}</p>
        <p className="pitch-callout__body">{PRODUCT_EXAMPLE_CALLOUT_BODY}</p>
      </aside>

      <QuickStartBar supports={supportList.length ? supportList : undefined} onError={setError} />

      <p className="fast-entry__or">Or write your own</p>

      <div className={composerClass}>
        <label className="fast-entry__vis-label" htmlFor="bridge-task">
          What do you need to work on?
        </label>
        <textarea
          id="bridge-task"
          className="fast-entry__input"
          rows={3}
          value={task}
          onChange={(e) => setTask(e.target.value)}
          placeholder={PLACEHOLDERS[phIndex] ?? PLACEHOLDERS[0]}
          autoFocus
        />
        {task.trim().length >= 2 ? (
          <div className="fast-entry__preview" aria-live="polite">
            {previewFrame ? (
              <>
                <span className="fast-entry__preview-kicker">
                  Steps will use the {frameTitle(previewFrame)} style
                </span>
                <p className="fast-entry__preview-body">{previewText}</p>
              </>
            ) : frame === SURPRISE_FRAME_ID ? (
              <p className="muted small fast-entry__preview-hint">
                We will pick a style for you when you start. You can still begin with one tap.
              </p>
            ) : (
              <p className="muted small fast-entry__preview-hint">
                Pick a style under the box to see how the steps might feel.
              </p>
            )}
          </div>
        ) : null}
      </div>

      <p className="chip-section-label">{PRODUCT_CHIP_SECTION_LABEL}</p>
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
      <p className="fast-entry__hint muted small">
        You can skip this. If you pick something you like—or Surprise—Bridge keeps the steps in that
        style. It still aims at your real task.
      </p>

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
          {busy ? 'Starting…' : 'Start now'}
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
          <h2 className="customize-panel__title">More options</h2>
          <p className="customize-panel__lede muted small">
            You do not have to change anything here. These choices only adjust tone and how small each
            step feels.
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
