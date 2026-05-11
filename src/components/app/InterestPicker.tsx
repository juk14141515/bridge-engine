import { useMemo, useState } from "react";
import { Field } from "../ui/Field";
import { Chips } from "../ui/Chips";
import { TextInput } from "../ui/Input";
import styles from "./InterestPicker.module.css";
import { useProfile } from "../../hooks/useProfile";

const suggestions = ["gaming", "coding", "systems", "fitness", "investing", "music", "art", "writing"];

export function InterestPicker(props: { selected: string[]; onChange: (v: string[]) => void }) {
  const { state: profile } = useProfile();
  const [showMore, setShowMore] = useState(false);
  const options = useMemo(() => {
    const set = new Set([...profile.interests, ...suggestions]);
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }, [profile.interests]);
  const primary = options.slice(0, 6);
  const extra = options.slice(6);

  function toggle(v: string) {
    props.onChange(
      props.selected.includes(v)
        ? props.selected.filter((x) => x !== v)
        : [...props.selected, v].slice(0, 4),
    );
  }

  function addCustom(v: string) {
    const cleaned = v.trim().toLowerCase();
    if (!cleaned) return;
    if (props.selected.includes(cleaned)) return;
    props.onChange([...props.selected, cleaned].slice(0, 4));
  }

  return (
    <div className={styles.wrap}>
      <Field
        label="What naturally pulls your attention when you’re tired?"
        hint="Pick 1–3. We’ll use this as an entry ramp."
      >
        <Chips
          options={primary}
          selected={props.selected}
          onToggle={toggle}
          ariaLabel="Attention pathways"
        />
        {extra.length ? (
          <button
            type="button"
            className={styles.more}
            onClick={() => setShowMore((v) => !v)}
            aria-expanded={showMore}
          >
            {showMore ? "Show fewer" : "Show more"}
          </button>
        ) : null}
        {showMore && extra.length ? (
          <div className={styles.moreArea}>
            <Chips
              options={extra}
              selected={props.selected}
              onToggle={toggle}
              ariaLabel="More options"
            />
          </div>
        ) : null}
      </Field>

      <Field label="Add one" hint="Optional.">
        <div className={styles.row}>
          <TextInput
            placeholder="e.g. entrepreneurship"
            aria-label="Add interest"
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                addCustom((e.currentTarget as HTMLInputElement).value);
                (e.currentTarget as HTMLInputElement).value = "";
              }
            }}
          />
          <div className={styles.helper}>Press Enter</div>
        </div>
      </Field>
    </div>
  );
}

