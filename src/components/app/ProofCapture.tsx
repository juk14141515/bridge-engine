import { Field } from "../ui/Field";
import { TextArea } from "../ui/Input";
import styles from "./ProofCapture.module.css";

export function ProofCapture(props: {
  prompt: string;
  value: string;
  onChange: (v: string) => void;
  coachTone: "calm" | "direct" | "gentle";
}) {
  return (
    <div className={styles.wrap}>
      <Field label="Quick check-in" hint={toneHint(props.coachTone)}>
        <div className={styles.prompt}>{props.prompt}</div>
        <TextArea
          value={props.value}
          onChange={(e) => props.onChange(e.target.value)}
          placeholder="Optional."
          aria-label="Check-in input"
        />
      </Field>
      <div className={styles.note}>Only if it helps.</div>
    </div>
  );
}

function toneHint(t: "calm" | "direct" | "gentle") {
  if (t === "direct") return "Keep it factual.";
  if (t === "gentle") return "Be kind to yourself.";
  return "No pressure.";
}

