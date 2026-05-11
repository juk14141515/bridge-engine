import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Button } from "../ui/Button";
import { useProfile } from "../../hooks/useProfile";
import { useEntryMemory } from "../../hooks/useEntryMemory";
import { type HelpMode } from "../../lib/adaptiveHelp";
import { adaptiveService } from "../../lib/adaptiveService";
import { feedbackService } from "../../lib/feedbackService";
import type { BridgeFeedback, BridgePlan, EntryMemoryItem, EntryOutcome } from "../../types/bridge";
import { BridgeInput } from "./BridgeInput";
import { EntryHome } from "./EntryHome";
import { FeedbackBar } from "./FeedbackBar";
import { LaneFrame } from "./LaneFrame";
import { TapOptions, type TapOption } from "./TapOptions";
import styles from "./AdaptiveLane.module.css";

type Step =
  | "home"
  | "intake"
  | "friction"
  | "pathway"
  | "bridge"
  | "helpChoices"
  | "help"
  | "complete"
  | "continueHome";
type ActiveHelp = {
  mode: HelpMode;
  result: Awaited<ReturnType<typeof adaptiveService.adaptiveHelp>>;
};
type SupportPreferences = {
  startingFeelsHeavier: boolean;
  optionsShutDown: boolean;
  jumpsTracks: boolean;
  readingTiring: boolean;
  emotionallyHeavy: boolean;
  lowFuel: boolean;
  dyslexiaFriendly: boolean;
  learningStyle: string[];
};

const frictionOptions: TapOption[] = [
  { id: "starting", label: "Starting", helper: "I care. I can’t get in." },
  { id: "overwhelm", label: "Overwhelmed", helper: "Too much at once." },
  { id: "avoid", label: "Avoiding", helper: "I bounce off it." },
  { id: "focus", label: "Focusing", helper: "I drift." },
  { id: "recovery", label: "Low energy", helper: "Not much fuel." },
];

const pathwayOptions: TapOption[] = [
  { id: "systems", label: "Systems", helper: "Rules. Structure. Patterns." },
  { id: "gaming", label: "Gaming", helper: "Levels. Mechanics. Progress." },
  { id: "coding", label: "Coding", helper: "Debugging. State. One failing point." },
  { id: "investing", label: "Investing", helper: "Signals. Risk. Decision quality." },
  { id: "fitness", label: "Fitness", helper: "Warm-up. Adaptation. Low strain." },
  { id: "movement", label: "Movement", helper: "Body first. Mind follows." },
  { id: "music", label: "Music", helper: "Rhythm. Mood. Flow." },
  { id: "visual", label: "Visual", helper: "See it, then enter it." },
  { id: "entrepreneurship", label: "Entrepreneurship", helper: "Leverage. Offer. One useful signal." },
  { id: "creativity", label: "Creativity", helper: "Make first. Judge later." },
  { id: "logic", label: "Logic", helper: "Make the next edge clear." },
];

const helpOptions: TapOption[] = [
  { id: "smaller", label: "Make it smaller", helper: "Less surface." },
  { id: "start", label: "Show me where to start", helper: "Find the first edge." },
  { id: "explain", label: "Explain it simply", helper: "No overthinking." },
  { id: "walkthrough", label: "Walk me through it", helper: "A few soft steps." },
  { id: "recovery", label: "Too overwhelmed", helper: "No task yet." },
  { id: "done", label: "I did one piece", helper: "That counts." },
];

const intakeOptions: TapOption[] = [
  { id: "startingFeelsHeavier", label: "Starting feels heavier", helper: "Doing may be easier than entering." },
  { id: "optionsShutDown", label: "Options shut me down", helper: "Fewer choices helps." },
  { id: "jumpsTracks", label: "My brain jumps tracks", helper: "Keep the path visible." },
  { id: "readingTiring", label: "Reading gets tiring", helper: "Shorter text helps." },
  { id: "emotionallyHeavy", label: "Feels emotionally heavy", helper: "Approach from the side." },
  { id: "lowFuel", label: "Low fuel / burnout", helper: "No-task support first." },
  { id: "dyslexiaFriendly", label: "Readability helps", helper: "Clearer spacing and wording." },
];

const learningOptions: TapOption[] = [
  { id: "visual", label: "Visual" },
  { id: "verbal", label: "Verbal" },
  { id: "examples", label: "Examples" },
  { id: "step-by-step", label: "Step by step" },
  { id: "hands-on", label: "Hands-on" },
];

const defaultSupportPreferences: SupportPreferences = {
  startingFeelsHeavier: false,
  optionsShutDown: false,
  jumpsTracks: false,
  readingTiring: false,
  emotionallyHeavy: false,
  lowFuel: false,
  dyslexiaFriendly: false,
  learningStyle: [],
};

export function AdaptiveLane() {
  const location = useLocation();
  const navigate = useNavigate();
  const { state: profile } = useProfile();
  const { entries, remember, preferredPathways } = useEntryMemory();

  const [step, setStep] = useState<Step>("home");
  const [stuckText, setStuckText] = useState("");
  const [frictionChoice, setFrictionChoice] = useState("");
  const [chosenInterests, setChosenInterests] = useState<string[]>([]);
  const [activeHelp, setActiveHelp] = useState<ActiveHelp | null>(null);
  const [microAck, setMicroAck] = useState<string | null>(null);
  const [showMorePathways, setShowMorePathways] = useState(false);
  const [lastSavedAt, setLastSavedAt] = useState<number | null>(null);
  const [activeEntry, setActiveEntry] = useState<EntryMemoryItem | null>(null);
  const [plan, setPlan] = useState<BridgePlan | null>(null);
  const [supportPreferences, setSupportPreferences] = useState<SupportPreferences>(() => readSupportPreferences());
  const [intakeDone, setIntakeDone] = useState(() => localStorage.getItem("bridge.intakeDone.v1") === "1");
  const [continuationLevel, setContinuationLevel] = useState(0);
  const [smallerLevel, setSmallerLevel] = useState(0);
  const [anotherIndex, setAnotherIndex] = useState(0);

  useEffect(() => {
    console.log("[Bridge state]", {
      step,
      activeEntryId: activeEntry?.id ?? null,
      activeHelpMode: activeHelp?.mode ?? null,
      continuationLevel,
      smallerLevel,
    });
  }, [activeEntry?.id, activeHelp?.mode, continuationLevel, smallerLevel, step]);

  useEffect(() => {
    const initial = (location.state as { initialStuckText?: string } | null)?.initialStuckText;
    if (initial && !stuckText) {
      setStuckText(initial);
      setStep(intakeDone ? "pathway" : "intake");
      navigate("/app", { replace: true, state: null });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const adaptivePathways = useMemo(() => {
    const preferred = preferredPathways();
    if (!preferred.length) return pathwayOptions;

    return [...pathwayOptions].sort((a, b) => {
      const aRank = preferred.indexOf(a.id);
      const bRank = preferred.indexOf(b.id);
      return (aRank === -1 ? 999 : aRank) - (bRank === -1 ? 999 : bRank);
    });
  }, [preferredPathways]);

  function goBack() {
    if (step === "intake") setStep("home");
    else if (step === "friction") setStep("home");
    else if (step === "pathway") setStep("friction");
    else if (step === "bridge") setStep("pathway");
    else if (step === "helpChoices") setStep("bridge");
    else if (step === "help") setStep("continueHome");
    else if (step === "complete") setStep("help");
    else if (step === "continueHome") setStep("helpChoices");
  }

  function reset() {
    setStep("friction");
    setStuckText("");
    setFrictionChoice("");
    setChosenInterests([]);
    setActiveHelp(null);
    setMicroAck(null);
    setLastSavedAt(null);
    setActiveEntry(null);
    setPlan(null);
    setContinuationLevel(0);
    setSmallerLevel(0);
    setAnotherIndex(0);
  }

  function begin() {
    console.log("[Bridge click]", "start");
    setMicroAck(null);
    setStep(intakeDone ? "friction" : "intake");
  }

  function toggleIntake(id: string) {
    console.log("[Bridge click]", "intake", id);
    if (learningOptions.some((option) => option.id === id)) {
      setSupportPreferences((prev) => ({
        ...prev,
        learningStyle: prev.learningStyle.includes(id)
          ? prev.learningStyle.filter((item) => item !== id)
          : [...prev.learningStyle, id],
      }));
      return;
    }
    setSupportPreferences((prev) => ({ ...prev, [id]: !prev[id as keyof SupportPreferences] }));
  }

  function finishIntake() {
    console.log("[Bridge click]", "finish intake");
    writeSupportPreferences(supportPreferences);
    localStorage.setItem("bridge.intakeDone.v1", "1");
    setIntakeDone(true);
    setMicroAck("Saved softly.");
    setStep("friction");
  }

  function pickFriction(id: string) {
    console.log("[Bridge click]", "friction", id);
    const seed: Record<string, string> = {
      starting: "I keep trying to start, but I bounce off it.",
      overwhelm: "It feels like too much at once.",
      avoid: "I keep avoiding it even though I care.",
      focus: "I can’t stay mentally in it.",
      recovery: "I’m low on fuel and it feels heavy.",
    };
    setFrictionChoice(id);
    setStuckText(seed[id] ?? "It feels hard to enter.");
    setMicroAck("Good. That’s enough.");
    setStep("pathway");
  }

  async function pickPathway(id: string) {
    console.log("[Bridge click]", "pathway", id);
    setChosenInterests([id]);
    setMicroAck("We can use that.");
    const nextPlan = await adaptiveService.bridgePlan({
      stuckText,
      chosenInterests: [id],
      profile,
      supportPreferences,
      entryMemory: entries,
    });
    setPlan(nextPlan);
    setStep("bridge");
  }

  function showHelp() {
    console.log("[Bridge click]", "tiny action");
    if (!plan) return;
    setMicroAck("Good. One inch.");
    setActiveHelp(null);
    setStep("helpChoices");
  }

  function rememberOutcome(outcome: EntryOutcome) {
    if (plan) {
      const saved = remember({
        frictionChoice: frictionChoice || plan.frictionType,
        frictionType: plan.frictionType,
        attentionPathway: chosenInterests[0] ?? "unknown",
        pathway: chosenInterests[0] ?? "unknown",
        tinyAction: plan.tinyAction,
        helpMode: activeHelp?.mode ?? "bridge",
        continuationLevel,
        smallerLevel,
        outcome,
      });
      setLastSavedAt(saved.createdAt);
      setActiveEntry(saved);
      return saved;
    }
    return null;
  }

  function complete(outcome: EntryOutcome = "lighter") {
    console.log("[Bridge click]", "complete", outcome);
    rememberOutcome(outcome);
    setActiveHelp(null);
    setMicroAck("That counts.");
    setStep("complete");
  }

  async function createHelpFromClick(mode: HelpMode) {
    console.log("[Bridge click]", mode);
    if (!plan) return;
    const nextContinuationLevel = mode === "continue" ? continuationLevel + 1 : continuationLevel;
    const nextSmallerLevel = mode === "smaller" ? smallerLevel + 1 : smallerLevel;
    const nextAnotherIndex = mode === "another" || mode === "another_way" ? anotherIndex + 1 : anotherIndex;
    const result = await adaptiveService.adaptiveHelp({
      frictionType: plan.frictionType,
      pathway: chosenInterests[0] ?? activeEntry?.attentionPathway ?? "",
      taskText: plan.stuckText,
      helpMode: mode,
      entryMemory: entries,
      continuationLevel: nextContinuationLevel,
      smallerLevel: nextSmallerLevel,
      anotherIndex: nextAnotherIndex,
      supportPreferences,
    });
    setContinuationLevel(nextContinuationLevel);
    setSmallerLevel(nextSmallerLevel);
    setAnotherIndex(nextAnotherIndex);
    setActiveHelp({ mode, result });
    setMicroAck(mode === "smaller" ? "Smaller works." : mode === "another" || mode === "another_way" ? "Another way in." : "Continue softly.");
    setStep("help");
  }

  function pickHelp(id: string) {
    console.log("[Bridge click]", "help option", id);
    const mode = id as HelpMode;
    if (mode === "done") {
      complete("lighter");
      return;
    }
    createHelpFromClick(mode);
  }

  function handleHelpChoice(id: string) {
    console.log("[Bridge click]", "active help choice", id);
    if (id === "done") complete("lighter");
    else if (id === "continue") createHelpFromClick("continue");
    else if (id === "smaller") createHelpFromClick("smaller");
    else if (id === "another") createHelpFromClick("another");
    else if (id === "recover") complete("smaller");
  }

  async function handleFeedback(feedback: BridgeFeedback) {
    console.log("[Bridge click]", "feedback", feedback);
    if (!plan) return;

    await feedbackService.save({
      entryId: activeEntry?.id,
      frictionType: plan.frictionType,
      pathway: chosenInterests[0] ?? activeEntry?.attentionPathway ?? "systems",
      helpMode: activeHelp?.mode ?? "bridge",
      bridgeText: activeHelp?.result.headline ?? plan.relevanceMapping,
      tinyAction: activeHelp?.result.instruction ?? plan.tinyAction,
      feedback,
      timestamp: Date.now(),
    });

    if (feedback === "helped") {
      complete("lighter");
      return;
    }
    if (feedback === "too_much") {
      await createHelpFromClick("smaller");
      return;
    }
    if (feedback === "different_angle") {
      await createHelpFromClick("another");
      return;
    }
    await createHelpFromClick("explain");
  }

  const titleByStep: Record<Step, string> = {
    home: "Bridge Engine",
    intake: "What helps?",
    friction: "What kind of stuck is this?",
    pathway: "What feels easiest to enter?",
    bridge: "Try this",
    helpChoices: "What would help one inch?",
    help: "Here.",
    complete: "You started.",
    continueHome: "You got in.",
  };

  return (
    <LaneFrame
      title={titleByStep[step]}
      subtitle={
        step === "home"
          ? "A calm way back into action."
          : step === "intake"
            ? "Tap what fits. Skip anything."
            : step === "friction"
          ? "Tap what fits. Close is enough."
          : step === "pathway"
            ? "No profile setup. Just an entry ramp."
            : step === "bridge"
              ? "No whole plan. Just enough to enter."
              : step === "helpChoices"
                ? "Tap what feels useful."
                : step === "help"
                  ? "One soft continuation."
                  : step === "complete"
                    ? "The weight shifted."
                  : "Stay or stop. No pressure."
      }
    >
      <div className={styles.stack}>
        {microAck ? <div className={styles.ack}>{microAck}</div> : null}

        {step === "home" ? (
          <div className={styles.panel}>
            <div className={styles.bridge}>
              <div className={styles.bigLine}>Start where you are.</div>
              <div className={styles.reframe}>No setup required. The first tap personalizes the path.</div>
              <div className={styles.checkActions}>
                <Button size="lg" onClick={begin}>
                  Start
                </Button>
                {entries.length ? (
                  <Button variant="ghost" onClick={() => setStep("continueHome")}>
                    Continue
                  </Button>
                ) : null}
              </div>
            </div>
          </div>
        ) : null}

        {step === "intake" ? (
          <div className={styles.panel}>
            <div className={styles.message}>
              <TapOptions options={intakeOptions} onPick={toggleIntake} ariaLabel="Support preferences" />
              <TapOptions options={learningOptions} onPick={toggleIntake} ariaLabel="Learning style" />
              <div className={styles.actions}>
                <Button size="lg" onClick={finishIntake}>
                  Continue
                </Button>
                <Button variant="ghost" onClick={() => {
                  localStorage.setItem("bridge.intakeDone.v1", "1");
                  setIntakeDone(true);
                  setStep("friction");
                }}>
                  Skip
                </Button>
              </div>
            </div>
          </div>
        ) : null}

        {step === "friction" ? (
          <div className={styles.panel}>
            <div className={styles.message}>
              <TapOptions options={frictionOptions} onPick={pickFriction} ariaLabel="Friction options" />
              <details className={styles.details}>
                <summary>Type it instead</summary>
                <div className={styles.detailBody}>
                  <BridgeInput value={stuckText} onChange={setStuckText} />
                  <Button size="lg" disabled={!stuckText.trim()} onClick={() => setStep("pathway")}>
                    Continue
                  </Button>
                </div>
              </details>
            </div>
          </div>
        ) : null}

        {step === "pathway" ? (
          <div className={styles.panel}>
            <div className={styles.message}>
              <TapOptions
                options={showMorePathways ? adaptivePathways : adaptivePathways.slice(0, 4)}
                onPick={pickPathway}
                ariaLabel="Attention pathways"
              />
              {!showMorePathways ? (
                <button
                  type="button"
                  className={styles.quietLink}
                  onClick={() => setShowMorePathways(true)}
                >
                  More
                </button>
              ) : null}
            </div>
            <div className={styles.actions}>
              <Button variant="ghost" onClick={goBack}>
                Back
              </Button>
            </div>
          </div>
        ) : null}

        {step === "bridge" && plan ? (
          <div className={styles.panel}>
            <div className={styles.bridge}>
              <div className={styles.bigLine}>{tinyReframe(plan)}</div>
              <div className={styles.reframe}>Smaller counts.</div>
              <button type="button" className={styles.actionBox} onClick={showHelp}>
                {plan.tinyAction}
              </button>
              <FeedbackBar onFeedback={handleFeedback} />
            </div>
            <div className={styles.actions}>
              <Button variant="ghost" onClick={goBack}>
                Back
              </Button>
            </div>
          </div>
        ) : null}

        {step === "helpChoices" ? (
          <div className={styles.panel}>
            <div className={styles.message}>
              <TapOptions options={helpOptions} onPick={pickHelp} ariaLabel="Adaptive help options" />
              <div className={styles.actions}>
                <Button variant="ghost" onClick={goBack}>
                  Back
                </Button>
              </div>
            </div>
          </div>
        ) : null}

        {step === "complete" ? (
          <div className={styles.panel}>
            <div className={styles.checkWrap}>
              <div className={styles.softCheck} aria-hidden>✓</div>
              <div className={styles.bigLine}>You started.</div>
              <div className={styles.reframe}>That counts. The weight shifted.</div>
              <div className={styles.checkActions}>
                <Button size="lg" onClick={() => setStep("continueHome")}>
                  Continue
                </Button>
              </div>
            </div>
          </div>
        ) : null}

        {step === "help" && activeHelp ? (
          <div className={styles.panel}>
            <div className={styles.bridge}>
              <div className={styles.bigLine}>{activeHelp.result.headline}</div>
              <div className={styles.reframe}>{activeHelp.result.reassurance}</div>
              <button type="button" className={styles.actionBox} onClick={() => complete("lighter")}>
                {activeHelp.result.instruction}
              </button>
              <FeedbackBar onFeedback={handleFeedback} />
              <div className={styles.checkActions}>
                {activeHelp.result.nextChoices.map((choice) => (
                  <Button
                    key={choice.id}
                    size={choice.id === "done" || choice.id === "continue" ? "lg" : "md"}
                    variant={choice.id === "done" || choice.id === "continue" ? "primary" : "ghost"}
                    onClick={() => handleHelpChoice(choice.id)}
                  >
                    {choice.label}
                  </Button>
                ))}
                <Button variant="ghost" onClick={goBack}>
                  Back
                </Button>
              </div>
            </div>
          </div>
        ) : null}

        {step === "continueHome" ? (
          <div className={styles.panel}>
            <EntryHome
              entries={mergeActiveEntry(activeEntry, entries)}
              onContinue={() => {
                createHelpFromClick("continue");
              }}
              onSmaller={() => {
                createHelpFromClick("smaller");
              }}
              onAnotherWay={() => {
                createHelpFromClick("another");
              }}
              onAnother={reset}
              onDone={() => setMicroAck("Enough counts.")}
              saved={Boolean(lastSavedAt)}
            />
          </div>
        ) : null}
      </div>
    </LaneFrame>
  );
}

function tinyReframe(plan: BridgePlan) {
  switch (plan.frictionType) {
    case "overwhelm":
      return "Reduce the surface area.";
    case "perfectionism":
      return "No performance yet.";
    case "emotional_resistance":
      return "Enter sideways.";
    case "task_switch":
      return "Make a ramp.";
    case "memory_load":
      return "Put less in your head.";
    case "decision_fatigue":
      return "Remove the choices.";
    case "recovery_depletion":
      return "Keep the thread.";
    case "ambiguity":
    default:
      return "Find the edge.";
  }
}

function mergeActiveEntry(activeEntry: EntryMemoryItem | null, entries: EntryMemoryItem[]) {
  if (!activeEntry) return entries;
  return [activeEntry, ...entries.filter((entry) => entry.id !== activeEntry.id)];
}

function readSupportPreferences(): SupportPreferences {
  try {
    const raw = localStorage.getItem("bridge.supportPreferences.v1");
    return raw ? { ...defaultSupportPreferences, ...JSON.parse(raw) } : defaultSupportPreferences;
  } catch {
    return defaultSupportPreferences;
  }
}

function writeSupportPreferences(preferences: SupportPreferences) {
  localStorage.setItem("bridge.supportPreferences.v1", JSON.stringify(preferences));
}

