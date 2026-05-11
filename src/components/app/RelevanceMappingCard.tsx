import type { BridgePlan } from "../../types/bridge";
import { Card } from "../ui/Card";
import styles from "./PlanCards.module.css";

export function RelevanceMappingCard({ plan }: { plan: BridgePlan }) {
  return (
    <Card title="Why this matters (to you)" subtitle={plan.relevanceTitle}>
      <div className={styles.text}>{plan.relevanceMapping}</div>
      <div className={styles.note}>
        We’re not forcing motivation. We’re translating it into a safe entry step.
      </div>
    </Card>
  );
}

