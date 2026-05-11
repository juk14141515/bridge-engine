import { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import styles from "./AppShell.module.css";
import { useAccessibilityPrefs } from "../../hooks/useAccessibilityPrefs";

export function AppShell({ children }: { children: ReactNode }) {
  const location = useLocation();
  useAccessibilityPrefs();

  const onLanding = location.pathname === "/";
  const onWorkspace = location.pathname.startsWith("/workspace");
  const onStart = location.pathname.startsWith("/start");
  const inHome = location.pathname.startsWith("/home");

  return (
    <div className={styles.root}>
      {onLanding ? null : (
        <header className={styles.header}>
          <Link to="/home" className={styles.brand} aria-label="Bridge home">
            <span className={styles.logo} aria-hidden />
            <span className={styles.brandName}>Bridge</span>
          </Link>

          <nav className={styles.nav} aria-label="Primary">
            {!onWorkspace && !inHome ? (
              <Link to="/home" className={styles.navLink}>
                Sessions
              </Link>
            ) : null}
            {!onStart ? (
              <Link to="/start" className={`${styles.navLink} ${styles.navLinkAccent}`}>
                Start
              </Link>
            ) : null}
          </nav>
        </header>
      )}

      <main className={styles.main}>{children}</main>
    </div>
  );
}
