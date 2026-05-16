import { useEffect, useMemo, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { openBridgeSession } from '../lib/startBridgeSession';

interface LocationState {
  initialTask?: string;
  initialFrame?: string;
}

const HARD_THINGS = [
  { id: 'essay', label: 'Essay / paper', task: 'Write an essay or paper' },
  { id: 'language', label: 'Learn a language', task: 'Learn a language' },
  { id: 'test', label: 'Study for a test', task: 'Study for a test' },
  { id: 'project', label: 'Finish a project', task: 'Finish a project' },
  { id: 'conversation', label: 'Hard conversation', task: 'Prepare for a difficult conversation' },
  { id: 'space', label: 'Clean my space', task: 'Clean my space' },
  { id: 'memo', label: 'Professional memo', task: 'Write a professional memo' },
  { id: 'habit', label: 'Build a habit', task: 'Build a habit' },
  { id: 'shared-interest', label: 'Understand someone’s interest', task: 'Understand someone’s interest' },
  { id: 'fun', label: 'Learn for fun', task: 'Learn something for fun' },
];

const INTERESTS = [
  { id: 'gaming', label: 'Gaming', frame: 'gaming' },
  { id: 'music', label: 'Music', frame: 'music' },
  { id: 'fitness', label: 'Fitness', frame: 'fitness' },
  { id: 'sports', label: 'Sports', frame: 'fitness' },
  { id: 'coding', label: 'Coding', frame: 'coding' },
  { id: 'investing', label: 'Investing', frame: 'investing' },
  { id: 'art', label: 'Art', frame: 'creative' },
  { id: 'movies', label: 'Movies / TV', frame: 'creative' },
  { id: 'anime', label: 'Anime', frame: 'gaming' },
  { id: 'cars', label: 'Cars', frame: 'systems' },
  { id: 'animals', label: 'Dogs / animals', frame: 'relationship' },
  { id: 'fashion', label: 'Fashion', frame: 'creative' },
  { id: 'systems', label: 'Systems', frame: 'systems' },
  { id: 'storytelling', label: 'Storytelling', frame: 'creative' },
];

const PREVIEWS: Record<string, string> = {
  'essay:gaming': 'Bridge will turn your essay into quests, save points, and a finished draft.',
  'language:music': 'Bridge will turn language learning into lyrics, rhythm, phrase loops, speaking practice, and review.',
  'project:coding': 'Bridge will turn your project into build steps, checkpoints, and a finished version.',
  'conversation:fitness': 'Bridge will turn the conversation into warmup, reps, and a clear talking plan.',
  'memo:investing': 'Bridge will turn the memo into thesis, evidence, risks, tradeoffs, and a recommendation.',
  'shared-interest:sports': 'Bridge will turn the sport into simple plays, key terms, and conversation starters.',
  'test:music': 'Bridge will turn studying into rhythm, recall, and short practice loops.',
  'test:fitness': 'Bridge will turn studying into training reps, review rounds, and confidence checks.',
  'space:fitness': 'Bridge will turn your space into warmup, reps, and one clear area at a time.',
  'habit:systems': 'Bridge will turn the habit into a small loop you can actually repeat.',
  'fun:storytelling': 'Bridge will turn learning into a story path with clear next scenes.',
};

const CUSTOM_INTEREST_EXAMPLES = [
  'my girlfriend’s music taste',
  'soccer',
  'Formula 1',
  'Pokémon',
  'watches',
  'Marvel movies',
  'cooking',
  'dogs',
  'fashion',
  'anime',
  'finance',
];

function initialTaskId(task: string | undefined): string | null {
  if (!task) return null;
  const normalized = task.toLowerCase();
  return HARD_THINGS.find((item) => item.task.toLowerCase() === normalized)?.id ?? null;
}

function initialInterestId(frame: string | undefined): string | null {
  if (!frame) return null;
  return INTERESTS.find((item) => item.frame === frame || item.id === frame)?.id ?? null;
}

function initialCustomInterest(frame: string | undefined): string {
  if (!frame || initialInterestId(frame)) return '';
  return frame;
}

function displayTask(task: string): string {
  const normalized = task.trim().toLowerCase();
  if (!normalized) return 'Hard thing';
  if (normalized.includes('essay') || normalized.includes('paper')) return 'your essay';
  if (normalized.includes('language') || normalized.includes('spanish')) return 'language learning';
  if (normalized.includes('conversation')) return 'this conversation';
  if (normalized.includes('memo')) return 'the memo';
  if (normalized.includes('project')) return 'your project';
  if (normalized.includes('study') || normalized.includes('test')) return 'studying';
  return task.trim();
}

function previewFor(taskId: string | null, interestId: string | null, taskLabel: string, interestLabel: string): string {
  if (!taskId && !taskLabel.trim()) return 'Pick a hard thing. Then pick an interest.';
  if (!interestLabel.trim()) return 'Pick a personal interest Bridge can use to make this easier to enter.';
  if (taskId && interestId && PREVIEWS[`${taskId}:${interestId}`]) return PREVIEWS[`${taskId}:${interestId}`];

  const normalizedInterest = interestLabel.trim().toLowerCase();
  const normalizedTask = taskLabel.trim().toLowerCase();
  if (normalizedInterest.includes('pokémon') || normalizedInterest.includes('pokemon')) {
    return `Bridge will turn ${displayTask(taskLabel)} into Pokémon-style steps: starter idea, evolution, battle plan, and final draft.`;
  }
  if (normalizedInterest.includes('girlfriend') && normalizedInterest.includes('music')) {
    return 'Bridge will help you learn through songs, phrases, and shared conversation.';
  }
  if (normalizedTask.includes('conversation') && normalizedInterest.includes('fitness')) {
    return 'Bridge will turn this conversation into warmup, reps, and a clear talking plan.';
  }
  return `Bridge will turn ${displayTask(taskLabel)} through ${interestLabel.trim()} into small steps you can keep following.`;
}

export default function StartPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const initial = (location.state as LocationState | null) ?? {};

  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(() => initialTaskId(initial.initialTask));
  const [selectedInterestId, setSelectedInterestId] = useState<string | null>(() =>
    initialInterestId(initial.initialFrame),
  );
  const [customTask, setCustomTask] = useState(initialTaskId(initial.initialTask) ? '' : (initial.initialTask ?? ''));
  const [customInterest, setCustomInterest] = useState(() => initialCustomInterest(initial.initialFrame));
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const ls = location.state as LocationState | null;
    if (ls?.initialTask && !selectedTaskId && !customTask) {
      const id = initialTaskId(ls.initialTask);
      if (id) setSelectedTaskId(id);
      else setCustomTask(ls.initialTask);
    }
    if (ls?.initialFrame && !selectedInterestId && !customInterest) {
      const id = initialInterestId(ls.initialFrame);
      if (id) setSelectedInterestId(id);
      else setCustomInterest(ls.initialFrame);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state]);

  const selectedTask = HARD_THINGS.find((item) => item.id === selectedTaskId) ?? null;
  const selectedInterest = INTERESTS.find((item) => item.id === selectedInterestId) ?? null;
  const taskToStart = customTask.trim() || selectedTask?.task || '';
  const interestToStart = customInterest.trim() || selectedInterest?.label || '';
  const taskRouteLabel = customTask.trim() || selectedTask?.label || 'Hard thing';
  const interestRouteLabel = interestToStart.trim() || 'Personal interest';
  const canStart = useMemo(
    () => taskToStart.trim().length >= 1 && interestToStart.trim().length >= 1,
    [interestToStart, taskToStart],
  );
  const preview = previewFor(selectedTask?.id ?? null, selectedInterest?.id ?? null, taskToStart, interestToStart);

  async function start() {
    const trimmed = taskToStart.trim();
    const interest = interestToStart.trim();
    if (trimmed.length < 1 || interest.length < 1 || busy) return;

    setBusy(true);
    setError(null);
    try {
      const { workspaceId, ribbon, initialContract } = await openBridgeSession({
        task: trimmed,
        frame: interest,
        interests: [interest],
        supports: ['step_by_step'],
      });
      navigate(`/workspace/${workspaceId}`, {
        replace: true,
        state: { entryRibbon: ribbon, initialContract },
      });
    } catch (e) {
      setError('Bridge couldn’t start that session. Check the backend and try again.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="fast-entry">
      <header className="fast-entry__top">
        <Link className="btn btn-quiet" to="/home">
          ← Sessions
        </Link>
      </header>

      <h1 className="fast-entry__title">Finish hard things through what you already like.</h1>
      <p className="fast-entry__lede">
        Pick a hard thing. Pick an interest. Bridge turns both into small steps until it’s done.
      </p>

      <div className="bridge-transform-row" aria-label="How Bridge works">
        <span>Hard thing</span>
        <span aria-hidden>→</span>
        <span>Personal interest</span>
        <span aria-hidden>→</span>
        <span>Finished path</span>
      </div>
      <div className="bridge-transform-examples" aria-label="Examples">
        <span>Essay / paper → Gaming → Quest path to a finished draft</span>
        <span>Language → Music → Song-based practice path</span>
        <span>Project → Coding → Build path to completion</span>
      </div>

      <section className="choice-section" aria-labelledby="hard-thing-label">
        <p id="hard-thing-label" className="choice-section__label">What do you want to finish, learn, or get through?</p>
        <div className="start-chip-grid">
          {HARD_THINGS.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`start-choice-chip ${selectedTaskId === item.id ? 'start-choice-chip--active' : ''}`}
              onClick={() => {
                setSelectedTaskId(item.id);
                setCustomTask('');
              }}
              aria-pressed={selectedTaskId === item.id}
            >
              {item.label}
            </button>
          ))}
        </div>
      </section>

      <section className="choice-section" aria-labelledby="interest-label">
        <p id="interest-label" className="choice-section__label">Pick what Bridge should translate this through</p>
        <p className="choice-section__hint">Pick a personal interest Bridge can use to make this easier to enter.</p>
        <div className="start-chip-grid start-chip-grid--interests">
          {INTERESTS.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`start-choice-chip ${selectedInterestId === item.id ? 'start-choice-chip--active' : ''}`}
              onClick={() => {
                setSelectedInterestId(item.id);
                setCustomInterest('');
              }}
              aria-pressed={selectedInterestId === item.id}
            >
              {item.label}
            </button>
          ))}
        </div>
        <label className="fast-entry__vis-label" htmlFor="bridge-interest">
          What do you already like?
        </label>
        <input
          id="bridge-interest"
          className="fast-entry__input fast-entry__input--small"
          value={customInterest}
          onChange={(e) => {
            setCustomInterest(e.target.value);
            if (e.target.value.trim()) setSelectedInterestId(null);
          }}
          placeholder="Type your own interest, hobby, person, world, or topic"
        />
        <div className="custom-interest-examples" aria-label="Interest examples">
          {CUSTOM_INTEREST_EXAMPLES.map((example) => (
            <span key={example}>{example}</span>
          ))}
        </div>
      </section>

      <div className="bridge-live-preview" aria-live="polite">
        <span className="bridge-live-preview__route">
          {taskRouteLabel} → {interestRouteLabel}
        </span>
        <p>{preview}</p>
      </div>

      <div className="fast-entry__cta">
        <button
          type="button"
          className="btn btn-primary btn-lg btn-block fast-entry__primary"
          disabled={!canStart || busy}
          onClick={() => void start()}
        >
          {busy ? 'Starting Bridge…' : 'Start Bridge'}
        </button>
        <p className="muted small fast-entry__hint">You can change this later.</p>
      </div>

      <details className="custom-task-fold">
        <summary>Or type your own</summary>
        <label className="fast-entry__vis-label" htmlFor="bridge-task">
          What do you want to finish?
        </label>
        <input
          id="bridge-task"
          className="fast-entry__input fast-entry__input--small"
          value={customTask}
          onChange={(e) => {
            setCustomTask(e.target.value);
            if (e.target.value.trim()) setSelectedTaskId(null);
          }}
          placeholder="Example: write my lab report"
        />
      </details>

      {error ? (
        <div className="banner-gentle" role="status">
          {error}
        </div>
      ) : null}
    </div>
  );
}
