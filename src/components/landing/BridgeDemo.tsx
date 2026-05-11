import { useMemo, useState } from "react";
import { Card } from "../ui/Card";
import { Chips } from "../ui/Chips";
import { TextArea } from "../ui/Input";
import { createBridgePlan } from "../../lib/bridgeMapping";
import { useProfile } from "../../hooks/useProfile";
import styles from "./BridgeDemo.module.css";

const demoInterests = ["gaming", "coding", "systems", "investing", "fitness", "entrepreneurship"];

export function BridgeDemo() {
  const { state: profile } = useProfile();
  const [stuck, setStuck] = useState("I need to study chemistry but I keep avoiding it.");
  const [chosen, setChosen] = useState<string[]>(["gaming", "systems"]);

  const plan = useMemo(
    () => createBridgePlan({ stuckText: stuck, chosenInterests: chosen, profile }),
    [stuck, chosen, profile],
  );

  function toggleInterest(v: string) {
    setChosen((prev) => (prev.includes(v) ? prev.filter((x) => x !== v) : [...prev, v].slice(0, 4)));
  }

  return (
    <Card title="Live demo" subtitle="Task → friction → relevance → tiny action → proof">
      <div className={styles.stack}>
        <div className={styles.block}>
          <div className={styles.kicker}>What you’re stuck on</div>
          <TextArea
            value={stuck}
            onChange={(e) => setStuck(e.target.value)}
            aria-label="Demo stuck input"
          />
        </div>

        <div className={styles.block}>
          <div className={styles.kicker}>Connect it to</div>
          <Chips options={demoInterests} selected={chosen} onToggle={toggleInterest} />
          <div className={styles.hint}>Pick 1–3. Less is calmer.</div>
        </div>

        <div className={styles.out}>
          <div className={styles.row}>
            <span className={styles.label}>Friction</span>
            <span className={styles.value}>{plan.frictionLabel}</span>
          </div>
          <div className={styles.row2}>{plan.relevanceTitle}</div>
          <div className={styles.text}>{plan.relevanceMapping}</div>
          <div className={styles.rule} />
          <div className={styles.row}>
            <span className={styles.label}>Tiny next action</span>
          </div>
          <pre className={styles.pre}>{plan.tinyAction}</pre>
          <div className={styles.row}>
            <span className={styles.label}>Proof checkpoint</span>
          </div>
          <div className={styles.text}>{plan.proofPrompt}</div>
        </div>
      </div>
    </Card>
  );
}

