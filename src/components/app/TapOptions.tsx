import styles from "./TapOptions.module.css";

export type TapOption = {
  id: string;
  label: string;
  helper?: string;
};

export function TapOptions(props: {
  options: TapOption[];
  onPick: (id: string) => void;
  ariaLabel?: string;
}) {
  return (
    <div className={styles.wrap} role="list" aria-label={props.ariaLabel ?? "Options"}>
      {props.options.map((o) => (
        <button key={o.id} type="button" className={styles.option} onClick={() => props.onPick(o.id)}>
          <div className={styles.label}>{o.label}</div>
          {o.helper ? <div className={styles.helper}>{o.helper}</div> : null}
        </button>
      ))}
    </div>
  );
}

