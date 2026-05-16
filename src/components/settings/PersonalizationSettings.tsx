import { Card } from "../ui/Card";
import { Field } from "../ui/Field";
import { Chips } from "../ui/Chips";
import { TextInput } from "../ui/Input";
import { useProfile } from "../../hooks/useProfile";
import styles from "./SettingsCards.module.css";

const driverOptions = ["curiosity", "identity", "future self", "competence", "freedom", "care for others"];
const checkInOptions = ["one_sentence", "screenshot_note", "checkbox_done", "short_log"] as const;
const pacingOptions = ["tiny", "steady"] as const;
const toneOptions = ["calm", "gentle", "direct"] as const;

export function PersonalizationSettings() {
  const { state: profile, setState } = useProfile();

  function toggleInterest(v: string) {
    const cleaned = v.trim().toLowerCase();
    if (!cleaned) return;
    const next = profile.interests.includes(cleaned)
      ? profile.interests.filter((x) => x !== cleaned)
      : [...profile.interests, cleaned].slice(0, 12);
    setState({ ...profile, interests: next });
  }

  function setDrivers(selected: string[]) {
    setState({ ...profile, motivationDrivers: selected.slice(0, 6) });
  }

  return (
    <Card title="Advanced preferences" subtitle="Bridge also learns from taps over time.">
      <div className={styles.stack}>
        <Field label="Name" hint="Shown only on this device.">
          <TextInput
            value={profile.displayName ?? ""}
            onChange={(e) => setState({ ...profile, displayName: e.target.value })}
            placeholder="e.g. Jules"
            aria-label="Display name"
          />
        </Field>

        <Field label="Natural entry points" hint="The main flow learns these too.">
          <Chips options={[...new Set(profile.interests)]} selected={profile.interests} onToggle={toggleInterest} />
          <TextInput
            placeholder="Add an interest and press Enter"
            aria-label="Add interest"
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                toggleInterest((e.currentTarget as HTMLInputElement).value);
                (e.currentTarget as HTMLInputElement).value = "";
              }
            }}
          />
        </Field>

        <Field label="What tends to help">
          <Chips
            options={driverOptions}
            selected={profile.motivationDrivers}
            onToggle={(v) =>
              setDrivers(
                profile.motivationDrivers.includes(v)
                  ? profile.motivationDrivers.filter((x) => x !== v)
                  : [...profile.motivationDrivers, v],
              )
            }
          />
        </Field>

        <div className={styles.grid2}>
          <Field label="Check-in rhythm">
            <select
              className={styles.select}
              value={profile.proofPreference}
              onChange={(e) => setState({ ...profile, proofPreference: e.target.value as (typeof checkInOptions)[number] })}
            >
              {checkInOptions.map((o) => (
                <option key={o} value={o}>
                  {labelize(o)}
                </option>
              ))}
            </select>
          </Field>

          <Field label="Pacing">
            <select
              className={styles.select}
              value={profile.pacingPreference}
              onChange={(e) => setState({ ...profile, pacingPreference: e.target.value as (typeof pacingOptions)[number] })}
            >
              {pacingOptions.map((o) => (
                <option key={o} value={o}>
                  {labelize(o)}
                </option>
              ))}
            </select>
          </Field>
        </div>

        <Field label="Coach tone">
          <select
            className={styles.select}
            value={profile.coachTone}
            onChange={(e) => setState({ ...profile, coachTone: e.target.value as (typeof toneOptions)[number] })}
          >
            {toneOptions.map((o) => (
              <option key={o} value={o}>
                {labelize(o)}
              </option>
            ))}
          </select>
        </Field>

        <div className={styles.privacy}>
          Privacy: Bridge stores your profile + entry memory in <code>localStorage</code> on this device. No backend calls.
        </div>
      </div>
    </Card>
  );
}

function labelize(s: string) {
  return s.replace(/_/g, " ");
}

