import { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import styles from "./AppShell.module.css";
import { useAccessibilityPrefs } from "../../hooks/useAccessibilityPrefs";
import { ContinueDrawer } from "./ContinueDrawer";

export function AppShell({ children }: { children: ReactNode }) {
  const location = useLocation();
  useAccessibilityPrefs();
  const inApp = location.pathname.startsWith("/app");
  const inLanes = location.pathname.startsWith("/lanes");
  const inNewTask = location.pathname.startsWith("/task/new");
  const inWorkspace = location.pathname.startsWith("/workspace");
  const inSettings = location.pathname.startsWith("/settings");
  const onLanding = location.pathname === "/";
  const minimalHeader = inApp || onLanding;
  const activeWorkflowId = localStorage.getItem("bridge.activeWorkflowId");

  return (
    <div className={styles.root}>
      <header className={`${styles.header} ${minimalHeader ? styles.minimalHeader : ""}`}>
        <div className={styles.brand}>
          <div className={styles.logo} aria-hidden />
          {onLanding ? null : (
            <div className={styles.brandText}>
              <div className={styles.brandName}>Bridge Engine</div>
              <div className={styles.brandTag}>
                {minimalHeader ? "a calm next step" : "turn stuck into one visible next step"}
              </div>
            </div>
          )}
        </div>

        <nav className={styles.nav} aria-label="Primary">
          {onLanding ? null : (
            <>
              <Link
                to="/lanes"
                className={`${styles.navLink} ${inLanes ? styles.active : ""}`}
              >
                Lanes
              </Link>
              <Link to="/task/new" className={`${styles.navLink} ${inNewTask ? styles.active : ""}`}>
                New Task
              </Link>
              {activeWorkflowId ? (
                <Link to={`/workspace/${encodeURIComponent(activeWorkflowId)}`} className={`${styles.navLink} ${inWorkspace ? styles.active : ""}`}>
                  Active Task
                </Link>
              ) : null}
              <Link to="/app" className={`${styles.navLink} ${inApp ? styles.active : ""}`}>
                Bridge
              </Link>
              {inApp ? <ContinueDrawer /> : null}
              <Link
                to="/settings"
                className={`${styles.navLink} ${inSettings ? styles.active : ""}`}
              >
                Settings
              </Link>
              <span className={styles.navLink}>Profile</span>
              <span className={styles.navLink}>Login</span>
            </>
          )}
        </nav>
      </header>

      <main className={styles.main}>{children}</main>
      {minimalHeader ? null : (
        <footer className={styles.footer}>
          <span className={styles.footerText}>Calm. Local-first. No dashboards. No streaks.</span>
        </footer>
      )}
    </div>
  );
}

