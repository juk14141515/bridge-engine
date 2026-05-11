import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/Button";
import { TextArea } from "../components/ui/Input";
import styles from "./LandingPage.module.css";
import { useState } from "react";
import { TapOptions } from "../components/app/TapOptions";

export function LandingPage() {
  const navigate = useNavigate();
  const [stuck, setStuck] = useState("");
  const [showTyping, setShowTyping] = useState(false);

  const quick = [
    { id: "starting", label: "Starting", helper: "I care. I just can’t get in." },
    { id: "overwhelm", label: "Overwhelmed", helper: "Too much at once." },
    { id: "avoid", label: "Avoiding it", helper: "I bounce off it." },
    { id: "focus", label: "Focusing", helper: "I drift when I try." },
    { id: "recovery", label: "Low fuel", helper: "I’m tired / depleted." },
  ] as const;

  return (
    <div className={styles.wrap}>
      <div className={styles.inner}>
        <h1 className={styles.h1}>Bridge Engine</h1>
        <p className={styles.p}>Turn stuck into one step your brain can enter.</p>
        <p className={styles.p}>
          Bridge connects what you need to do with what already pulls your attention, then shrinks the task until starting feels possible.
        </p>
        <div className={styles.ctaRow}>
          <Button size="lg" onClick={() => navigate("/task/new")}>Start</Button>
          <Button variant="ghost" onClick={() => navigate("/lanes")}>Continue</Button>
          <Button variant="ghost" onClick={() => navigate("/settings")}>Login</Button>
          <Button variant="ghost" onClick={() => navigate("/settings")}>Sign up</Button>
        </div>

        <TapOptions
          options={[...quick]}
          onPick={(id) => {
            const seed =
              id === "starting"
                ? "I keep trying to start, but I bounce off it."
                : id === "overwhelm"
                  ? "It feels like too much at once."
                  : id === "avoid"
                    ? "I keep avoiding it even though I care."
                    : id === "focus"
                      ? "I can’t stay mentally in it."
                      : "I’m low on fuel and it feels heavy.";
            navigate("/app", { state: { initialStuckText: seed } });
          }}
          ariaLabel="Quick start options"
        />

        {!showTyping ? (
          <button type="button" className={styles.typeToggle} onClick={() => setShowTyping(true)}>
            Or type what it is
          </button>
        ) : (
          <div className={styles.input}>
            <TextArea
              value={stuck}
              onChange={(e) => setStuck(e.target.value)}
              placeholder="If you can: one sentence is enough."
              aria-label="What feels hard to start"
            />
          </div>
        )}

        {showTyping ? (
          <div className={styles.ctaRow}>
            <Button
              size="lg"
              disabled={!stuck.trim()}
              onClick={() => navigate("/app", { state: { initialStuckText: stuck } })}
            >
              Continue
            </Button>
          </div>
        ) : null}
      </div>
    </div>
  );
}

