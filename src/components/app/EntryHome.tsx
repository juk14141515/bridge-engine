import type { EntryMemoryItem } from "../../types/bridge";
import { Button } from "../ui/Button";
import styles from "./EntryHome.module.css";
import { useState } from "react";

export function EntryHome(props: {
  entries: EntryMemoryItem[];
  onContinue: () => void;
  onSmaller: () => void;
  onAnother: () => void;
  onAnotherWay: () => void;
  onDone: () => void;
  saved?: boolean;
}) {
  const [selectedEntry, setSelectedEntry] = useState<EntryMemoryItem | null>(null);
  const recentEntries = props.entries.slice(0, 5);

  return (
    <div className={styles.wrap}>
      <div className={styles.check} aria-hidden>
        ✓
      </div>
      <div className={styles.copy}>
        <div className={styles.title}>You got in.</div>
        <div className={styles.text}>That counts.</div>
        {props.saved ? <div className={styles.saved}>Saved for Continue.</div> : null}
      </div>

      <div className={styles.actions}>
        <Button size="lg" onClick={props.onContinue}>
          Continue gently
        </Button>
        <Button variant="ghost" onClick={props.onSmaller}>
          Make smaller
        </Button>
        <Button variant="ghost" onClick={props.onAnotherWay}>
          Another way
        </Button>
        <Button variant="ghost" onClick={props.onAnother}>
          Start another
        </Button>
      </div>

      {recentEntries.length ? (
        <details className={styles.memory}>
          <summary>What helped</summary>
          <div className={styles.entryList}>
            {recentEntries.map((entry) => (
              <button
                key={entry.id}
                type="button"
                className={styles.entryButton}
                onClick={() => setSelectedEntry(entry)}
              >
                <span>{label(entry.frictionChoice)}</span>
                <span>{label(entry.attentionPathway)}</span>
                <span>{entry.tinyAction}</span>
                <span>{label(entry.outcome)}</span>
              </button>
            ))}
          </div>

          {selectedEntry ? (
            <div className={styles.returnBox}>
              <div className={styles.returnTitle}>Return gently</div>
              <div className={styles.returnText}>{selectedEntry.tinyAction}</div>
              <div className={styles.returnActions}>
                <Button size="lg" onClick={props.onContinue}>
                  Continue gently
                </Button>
                <Button variant="ghost" onClick={props.onSmaller}>
                  Make smaller
                </Button>
                <Button variant="ghost" onClick={props.onAnotherWay}>
                  Another way
                </Button>
                <Button variant="ghost" onClick={props.onDone}>
                  Done for now
                </Button>
              </div>
            </div>
          ) : null}
        </details>
      ) : null}
    </div>
  );
}

function label(value: string) {
  return value.replace(/_/g, " ");
}

