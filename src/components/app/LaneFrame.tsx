import { ReactNode } from "react";
import styles from "./LaneFrame.module.css";

export function LaneFrame(props: { title: string; subtitle?: string; children: ReactNode }) {
  return (
    <div className={styles.wrap}>
      <header className={styles.header}>
        <div className={styles.title}>{props.title}</div>
        {props.subtitle ? <div className={styles.subtitle}>{props.subtitle}</div> : null}
      </header>
      <div className={styles.content}>{props.children}</div>
    </div>
  );
}

