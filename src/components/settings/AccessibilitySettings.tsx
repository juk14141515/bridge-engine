import { Card } from "../ui/Card";
import { useAccessibilityPrefs } from "../../hooks/useAccessibilityPrefs";
import styles from "./SettingsCards.module.css";
import { useEntryMemory } from "../../hooks/useEntryMemory";
import { Button } from "../ui/Button";

export function AccessibilitySettings() {
  const { prefs, setPrefs } = useAccessibilityPrefs();
  const { clearMemory } = useEntryMemory();

  return (
    <Card title="Accessibility + comfort" subtitle="Reduce stimulation. Increase readability.">
      <div className={styles.stack}>
        <label className={styles.toggle}>
          <input
            type="checkbox"
            checked={prefs.reducedMotion}
            onChange={(e) => setPrefs({ ...prefs, reducedMotion: e.target.checked })}
          />
          <span>Reduced motion</span>
        </label>

        <label className={styles.toggle}>
          <input
            type="checkbox"
            checked={prefs.highReadability}
            onChange={(e) => setPrefs({ ...prefs, highReadability: e.target.checked })}
          />
          <span>High readability</span>
        </label>

        <label className={styles.toggle}>
          <input
            type="checkbox"
            checked={prefs.lowStimulation}
            onChange={(e) => setPrefs({ ...prefs, lowStimulation: e.target.checked })}
          />
          <span>Low stimulation (flatter visuals)</span>
        </label>

        <label className={styles.toggle}>
          <input
            type="checkbox"
            checked={prefs.colorblindSafe}
            onChange={(e) => setPrefs({ ...prefs, colorblindSafe: e.target.checked })}
          />
          <span>Colorblind-safe indicators</span>
        </label>

        <div className={styles.rule} />

        <div className={styles.dangerZone}>
          <div className={styles.dangerTitle}>Reset local entry memory</div>
          <div className={styles.dangerText}>Clears saved starts on this device only.</div>
          <Button variant="danger" onClick={clearMemory}>
            Clear entry memory
          </Button>
        </div>
      </div>
    </Card>
  );
}

