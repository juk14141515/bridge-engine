import { useEffect, useState } from "react";
import { apiClient, type IntakePreferences } from "../../lib/apiClient";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import styles from "./IntakeSettings.module.css";

const defaults: IntakePreferences = {
  startingFeelsHeavierThanDoing: false,
  tooManyOptionsShutMeDown: false,
  brainJumpsTracks: false,
  readingIsTiring: false,
  taskFeelsEmotionallyHeavy: false,
  lowFuelSupport: false,
  dyslexiaFriendlyReadability: false,
  adhdStyleFrictionSupport: false,
  depressionLowEnergySupport: false,
  learningStyle: [],
};

const toggles: Array<[keyof IntakePreferences, string]> = [
  ["startingFeelsHeavierThanDoing", "Starting feels heavier than doing"],
  ["tooManyOptionsShutMeDown", "Too many options shut me down"],
  ["brainJumpsTracks", "My brain jumps tracks"],
  ["readingIsTiring", "Reading gets tiring"],
  ["taskFeelsEmotionallyHeavy", "Some tasks feel emotionally heavy"],
  ["lowFuelSupport", "I need low-fuel support"],
  ["dyslexiaFriendlyReadability", "Dyslexia-friendly readability helps"],
  ["adhdStyleFrictionSupport", "ADHD friction support helps"],
  ["depressionLowEnergySupport", "Low-energy support helps"],
];

const stylesOfLearning = ["visual", "verbal", "step-by-step", "examples", "hands-on"];

export function IntakeSettings() {
  const [intake, setIntake] = useState<IntakePreferences>(defaults);
  const [message, setMessage] = useState("");

  useEffect(() => {
    void apiClient.getIntake().then((data) => setIntake(data.intake)).catch(() => undefined);
  }, []);

  async function save() {
    try {
      await apiClient.saveIntake(intake);
      setMessage("Saved.");
    } catch {
      setMessage("Could not connect. Local entry still works.");
    }
  }

  function toggleLearning(value: string) {
    setIntake((prev) => ({
      ...prev,
      learningStyle: prev.learningStyle.includes(value)
        ? prev.learningStyle.filter((item) => item !== value)
        : [...prev.learningStyle, value],
    }));
  }

  return (
    <Card title="Support preferences" subtitle="Experiential, not diagnostic.">
      <div className={styles.stack}>
        {toggles.map(([key, label]) => (
          <label key={key} className={styles.toggle}>
            <input
              type="checkbox"
              checked={Boolean(intake[key])}
              onChange={(e) => setIntake({ ...intake, [key]: e.target.checked })}
            />
            <span>{label}</span>
          </label>
        ))}

        <div className={styles.learning}>
          <div className={styles.label}>Learning support</div>
          <div className={styles.pills}>
            {stylesOfLearning.map((item) => (
              <button
                key={item}
                type="button"
                className={`${styles.pill} ${intake.learningStyle.includes(item) ? styles.active : ""}`}
                onClick={() => toggleLearning(item)}
              >
                {item}
              </button>
            ))}
          </div>
        </div>

        <Button onClick={save}>Save support preferences</Button>
        {message ? <div className={styles.message}>{message}</div> : null}
      </div>
    </Card>
  );
}

