import { ReactNode } from "react";
import styles from "./Field.module.css";

export function Field(props: {
  label: string;
  hint?: string;
  children: ReactNode;
  id?: string;
}) {
  return (
    <div className={styles.field}>
      <div className={styles.labelRow}>
        <label className={styles.label} htmlFor={props.id}>
          {props.label}
        </label>
        {props.hint ? <span className={styles.hint}>{props.hint}</span> : null}
      </div>
      <div className={styles.control}>{props.children}</div>
    </div>
  );
}

