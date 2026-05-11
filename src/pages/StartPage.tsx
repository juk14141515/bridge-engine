import { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ApiError } from '../lib/runtimeApi';
import { createSession } from '../lib/sessionApi';
import { FRAME_CARDS, SUPPORT_CARDS, TASK_CATEGORIES, type TaskCategoryId } from '../lib/onboardingOptions';

type StepKey = 1 | 2 | 3;

export default function StartPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState<StepKey>(1);
  const [taskText, setTaskText] = useState('');
  const [categoryId, setCategoryId] = useState<TaskCategoryId | null>(null);
  const [supports, setSupports] = useState<Set<string>>(() => new Set());
  const [interest, setInterest] = useState<string>('gaming');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const goalReady = useMemo(() => {
    const t = taskText.trim();
    if (t.length >= 3) return true;
    if (categoryId) {
      const cat = TASK_CATEGORIES.find((c) => c.id === categoryId);
      return Boolean(cat?.goalSeed);
    }
    return false;
  }, [taskText, categoryId]);

  const composedGoal = useMemo(() => {
    const t = taskText.trim();
    if (t.length >= 3) return t;
    const cat = TASK_CATEGORIES.find((c) => c.id === categoryId);
    return cat?.goalSeed ?? '';
  }, [taskText, categoryId]);

  function toggleSupport(id: string) {
    setSupports((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function openBridge() {
    setBusy(true);
    setError(null);
    try {
      const prefs = Array.from(supports);
      const envelope = await createSession({
        task: composedGoal,
        frame: interest,
        supports: prefs.length ? prefs : ['step_by_step'],
        category: categoryId ?? undefined,
        user_words: taskText.trim().length >= 3 ? taskText.trim() : undefined,
      });
      navigate(`/workspace/${envelope.workspace.id}`, { replace: true });
    } catch (e) {
      const msg =
        e instanceof ApiError
          ? e.status === 0
            ? 'Backend not reachable (port 6060). Start it and try again.'
            : e.message
          : 'Could not open workspace.';
      setError(msg);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <header className="top-bar">
        <Link className="btn btn-quiet" to="/home">
          ← Home
        </Link>
        <span className="brand brand--soft">{step === 1 ? '1 · Task' : step === 2 ? '2 · Supports' : '3 · Open'}</span>
      </header>

      <div className="onboarding-panel">
        {step === 1 ? (
          <>
            <h1 className="onboarding-title">What are you trying to get done?</h1>
            <p className="onboarding-lede">
              Type in your own words—or tap a category to seed it.
            </p>
            <textarea
              className="field onboarding-field"
              rows={4}
              value={taskText}
              onChange={(e) => setTaskText(e.target.value)}
              placeholder="e.g. Finish chem lab write-up before Friday…"
            />
            <p className="onboarding-section-label">Quick categories</p>
            <div className="option-card-list">
              {TASK_CATEGORIES.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  className={`option-card ${categoryId === c.id ? 'option-card--selected' : ''}`}
                  onClick={() => {
                    setCategoryId(c.id);
                    if (!taskText.trim()) setTaskText(c.goalSeed);
                  }}
                >
                  <span className="option-card__emoji" aria-hidden>
                    {c.emoji}
                  </span>
                  <span className="option-card__body">
                    <span className="option-card__title">{c.label}</span>
                    <span className="option-card__desc">{c.hint}</span>
                  </span>
                </button>
              ))}
            </div>
            <div className="onboarding-actions">
              <button
                type="button"
                className="btn btn-primary btn-lg"
                disabled={!goalReady}
                onClick={() => setStep(2)}
              >
                Continue
              </button>
              <Link className="btn btn-quiet" to="/new">
                Prefer a single big form
              </Link>
            </div>
          </>
        ) : null}

        {step === 2 ? (
          <>
            <h1 className="onboarding-title">What would make this easier?</h1>
            <p className="onboarding-lede">Tap any that fit—then pick how Bridge should translate.</p>

            <p className="onboarding-section-label">Supports</p>
            <div className="option-card-list">
              {SUPPORT_CARDS.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  className={`option-card ${supports.has(c.id) ? 'option-card--selected' : ''}`}
                  onClick={() => toggleSupport(c.id)}
                >
                  <span className="option-card__emoji" aria-hidden>
                    {c.emoji}
                  </span>
                  <span className="option-card__body">
                    <span className="option-card__title">{c.title}</span>
                    <span className="option-card__desc">{c.desc}</span>
                  </span>
                </button>
              ))}
            </div>

            <p className="onboarding-section-label">Translate through</p>
            <div className="option-card-list">
              {FRAME_CARDS.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  className={`option-card ${interest === c.id ? 'option-card--selected' : ''}`}
                  onClick={() => setInterest(c.id)}
                >
                  <span className="option-card__emoji" aria-hidden>
                    {c.emoji}
                  </span>
                  <span className="option-card__body">
                    <span className="option-card__title">{c.title}</span>
                    <span className="option-card__desc">{c.desc}</span>
                  </span>
                </button>
              ))}
            </div>

            <div className="onboarding-actions">
              <button type="button" className="btn" onClick={() => setStep(1)}>
                Back
              </button>
              <button type="button" className="btn btn-primary btn-lg" onClick={() => setStep(3)}>
                Continue
              </button>
            </div>
          </>
        ) : null}

        {step === 3 ? (
          <>
            <h1 className="onboarding-title">Open your adaptive workspace</h1>
            <p className="onboarding-lede">
              Bridge starts a live session: checkpoints, artifact preview, rewrites, and progress—all
              saved locally so you can pick up anytime.
            </p>
            <div className="summary-card">
              <div className="summary-row">
                <span className="summary-label">Task</span>
                <span className="summary-value">{composedGoal}</span>
              </div>
              <div className="summary-row">
                <span className="summary-label">Frame</span>
                <span className="summary-value">
                  {FRAME_CARDS.find((f) => f.id === interest)?.title ?? interest}
                </span>
              </div>
              <div className="summary-row">
                <span className="summary-label">Supports</span>
                <span className="summary-value">
                  {supports.size
                    ? Array.from(supports)
                        .map((id) => SUPPORT_CARDS.find((s) => s.id === id)?.title ?? id)
                        .join(' · ')
                    : 'None selected'}
                </span>
              </div>
            </div>
            {error ? (
              <div className="banner-gentle" role="status">
                {error}
              </div>
            ) : null}
            <div className="onboarding-actions">
              <button type="button" className="btn" onClick={() => setStep(2)}>
                Back
              </button>
              <button type="button" className="btn btn-primary btn-lg" disabled={busy} onClick={() => void openBridge()}>
                {busy ? 'Opening…' : 'Open workspace'}
              </button>
            </div>
          </>
        ) : null}
      </div>
    </>
  );
}
