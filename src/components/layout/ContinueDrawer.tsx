import { useState } from "react";
import { useEntryMemory } from "../../hooks/useEntryMemory";
import { Button } from "../ui/Button";
import styles from "./ContinueDrawer.module.css";

export function ContinueDrawer() {
  const [open, setOpen] = useState(false);
  const { entries } = useEntryMemory();

  if (!entries.length) return null;

  return (
    <>
      <button type="button" className={styles.trigger} onClick={() => setOpen(true)}>
        Continue
      </button>
      {open ? (
        <div className={styles.overlay} role="dialog" aria-label="Continue">
          <div className={styles.drawer}>
            <div className={styles.top}>
              <div>
                <div className={styles.title}>Continue</div>
                <div className={styles.subtitle}>Return gently.</div>
              </div>
              <button type="button" className={styles.close} onClick={() => setOpen(false)}>
                Close
              </button>
            </div>

            <details className={styles.recent}>
              <summary>Recent entries</summary>
              <div className={styles.list}>
                {entries.slice(0, 5).map((entry) => (
                  <button key={entry.id} type="button" className={styles.entry}>
                    <span>{entry.frictionChoice}</span>
                    <span>{entry.attentionPathway}</span>
                    <span>{entry.tinyAction}</span>
                    <span>{entry.outcome}</span>
                  </button>
                ))}
              </div>
            </details>

            <Button variant="ghost" onClick={() => setOpen(false)}>
              Back
            </Button>
          </div>
        </div>
      ) : null}
    </>
  );
}

