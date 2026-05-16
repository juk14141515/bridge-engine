import { AccessibilitySettings } from "../components/settings/AccessibilitySettings";
import { AuthSettings } from "../components/settings/AuthSettings";
import { IntakeSettings } from "../components/settings/IntakeSettings";
import { PersonalizationSettings } from "../components/settings/PersonalizationSettings";
import styles from "./SettingsPage.module.css";

export function SettingsPage() {
  return (
    <div className={styles.wrap}>
      <header className={styles.header}>
        <h1 className={styles.h1}>Advanced</h1>
        <p className={styles.p}>Tune Bridge after the main entry flow.</p>
      </header>

      <div className={styles.grid}>
        <AuthSettings />
        <IntakeSettings />
        <PersonalizationSettings />
        <AccessibilitySettings />
      </div>
    </div>
  );
}

