import { useMemo, useState } from "react";
import { Button } from "../ui/Button";
import styles from "./AttentionDiscovery.module.css";

type Pathway = { id: string; question: string; tags: string[] };

const pathways: Pathway[] = [
  { id: "systems", question: "Does your brain enter through systems or structure?", tags: ["systems", "coding"] },
  { id: "curiosity", question: "Does your brain enter through curiosity and puzzles?", tags: ["curiosity", "learning"] },
  { id: "people", question: "Does your brain enter through people or connection?", tags: ["people", "communication"] },
  { id: "movement", question: "Does your brain enter through movement or energy?", tags: ["movement", "fitness"] },
  { id: "creative", question: "Does your brain enter through creativity or making?", tags: ["creativity", "art"] },
];

export function AttentionDiscovery(props: {
  value: string[];
  onChange: (next: string[]) => void;
  onDone: () => void;
}) {
  const [idx, setIdx] = useState(0);
  const current = pathways[Math.min(idx, pathways.length - 1)];
  const chosen = props.value;

  const progress = useMemo(() => `${Math.min(idx + 1, pathways.length)} / ${pathways.length}`, [idx]);

  function choose(yes: boolean) {
    const next = yes ? mergeUnique(chosen, current.tags).slice(0, 3) : chosen;
    props.onChange(next);

    const nextIdx = idx + 1;
    if (nextIdx >= pathways.length || next.length >= 3) props.onDone();
    else setIdx(nextIdx);
  }

  return (
    <div className={styles.wrap}>
      <div className={styles.question}>{current.question}</div>
      <div className={styles.actions}>
        <Button size="lg" onClick={() => choose(true)}>
          Yes
        </Button>
        <Button size="lg" variant="ghost" onClick={() => choose(false)}>
          Not really
        </Button>
      </div>
      <div className={styles.meta}>
        <span>{progress}</span>
        <span className={styles.dot} aria-hidden />
        <button type="button" className={styles.skip} onClick={props.onDone}>
          Skip
        </button>
      </div>
    </div>
  );
}

function mergeUnique(a: string[], b: string[]) {
  const set = new Set([...a, ...b]);
  return Array.from(set);
}

