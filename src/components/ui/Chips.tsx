import styles from "./Chips.module.css";

export function Chips(props: {
  options: string[];
  selected: string[];
  onToggle: (value: string) => void;
  ariaLabel?: string;
}) {
  return (
    <div className={styles.wrap} role="list" aria-label={props.ariaLabel ?? "Options"}>
      {props.options.map((opt) => {
        const active = props.selected.includes(opt);
        return (
          <button
            key={opt}
            type="button"
            className={[styles.chip, active ? styles.active : ""].join(" ")}
            onClick={() => props.onToggle(opt)}
            aria-pressed={active}
          >
            {opt}
          </button>
        );
      })}
    </div>
  );
}

