import type { BridgePlan } from "../../types/bridge";
import { Card } from "../ui/Card";
import styles from "./PlanCards.module.css";

export function TinyActionCard({ plan }: { plan: BridgePlan }) {
  return (
    <Card title="One tiny next action" subtitle="Small enough to start. Real enough to count.">
      <pre className={styles.pre}>{plan.tinyAction}</pre>
      <div className={styles.note}>
        If this still feels too big: shrink it until it feels almost silly.
      </div>
    </Card>
  );
}

