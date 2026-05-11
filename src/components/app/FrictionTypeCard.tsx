import type { BridgePlan } from "../../types/bridge";
import { Card } from "../ui/Card";
import styles from "./PlanCards.module.css";

export function FrictionTypeCard({ plan }: { plan: BridgePlan }) {
  return (
    <Card title="Friction type" subtitle={plan.frictionLabel}>
      <div className={styles.text}>{plan.frictionWhy}</div>
      <div className={styles.badgeRow}>
        <span className={styles.badge}>State: {labelState(plan.adaptiveState)}</span>
      </div>
    </Card>
  );
}

function labelState(s: BridgePlan["adaptiveState"]) {
  switch (s) {
    case "overwhelmed":
      return "overwhelm";
    case "recovery":
      return "recovery";
    case "learning":
      return "learning";
    case "focus":
      return "focus";
    case "momentum":
      return "momentum";
    default:
      return "start";
  }
}

