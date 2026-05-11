import { ReactNode } from "react";
import styles from "./Card.module.css";

export function Card(props: { title?: string; subtitle?: string; children: ReactNode }) {
  return (
    <section className={styles.card} aria-label={props.title ?? "Card"}>
      {props.title ? (
        <header className={styles.header}>
          <h2 className={styles.title}>{props.title}</h2>
          {props.subtitle ? <p className={styles.subtitle}>{props.subtitle}</p> : null}
        </header>
      ) : null}
      <div className={styles.body}>{props.children}</div>
    </section>
  );
}

