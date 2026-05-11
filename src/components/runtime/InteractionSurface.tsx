import { TextArea, TextInput } from "../ui/Input";
import styles from "./Runtime.module.css";

export function InteractionSurface(props: {
  interactionType?: string;
  value: string;
  onChange: (value: string) => void;
}) {
  const type = (props.interactionType ?? "text_response").toLowerCase();

  if (type.includes("checklist")) {
    return (
      <div className={styles.panel}>
        <div className={styles.label}>Checklist</div>
        <label><input type="checkbox" /> First visible part found</label>
        <label><input type="checkbox" /> One small action attempted</label>
      </div>
    );
  }

  if (type.includes("matching")) return <Placeholder title="Matching" text="Matching interaction placeholder." />;
  if (type.includes("quiz")) return <Placeholder title="Quiz" text="Quiz interaction placeholder." />;
  if (type.includes("upload") || type.includes("proof")) return <Placeholder title="Upload" text="File proof placeholder. Text proof works below." />;
  if (type.includes("markdown")) {
    return <TextArea value={props.value} onChange={(e) => props.onChange(e.target.value)} placeholder="Write in markdown..." />;
  }
  if (type.includes("sentence")) return <TextInput value={props.value} onChange={(e) => props.onChange(e.target.value)} placeholder="Build one sentence..." />;
  if (type.includes("code")) return <TextArea value={props.value} onChange={(e) => props.onChange(e.target.value)} placeholder="Code / notes..." />;
  if (type.includes("reflection")) return <TextArea value={props.value} onChange={(e) => props.onChange(e.target.value)} placeholder="Short reflection..." />;

  return <TextArea value={props.value} onChange={(e) => props.onChange(e.target.value)} placeholder="Respond here..." />;
}

function Placeholder(props: { title: string; text: string }) {
  return (
    <div className={styles.panel}>
      <div className={styles.cardTitle}>{props.title}</div>
      <p className={styles.subtle}>{props.text}</p>
    </div>
  );
}

