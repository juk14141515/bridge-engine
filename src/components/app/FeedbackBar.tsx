import type { BridgeFeedback } from "../../types/bridge";
import styles from "./FeedbackBar.module.css";

export function FeedbackBar(props: { onFeedback: (feedback: BridgeFeedback) => void }) {
  return (
    <div className={styles.wrap} aria-label="Bridge feedback">
      <button type="button" onClick={() => props.onFeedback("helped")}>Helped</button>
      <button type="button" onClick={() => props.onFeedback("not_quite")}>Not quite</button>
      <button type="button" onClick={() => props.onFeedback("too_much")}>Too much</button>
      <button type="button" onClick={() => props.onFeedback("different_angle")}>Different angle</button>
    </div>
  );
}

