import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/Button";
import { runtimeApi, type RuntimeLane } from "../lib/runtimeApi";
import styles from "../components/runtime/Runtime.module.css";

export function LanesPage() {
  const navigate = useNavigate();
  const [lanes, setLanes] = useState<RuntimeLane[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    const result = await runtimeApi.getLanes();
    setLoading(false);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    const data = Array.isArray(result.data) ? result.data : result.data.lanes ?? [];
    setLanes(data);
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Lanes</h1>
        <p className={styles.subtle}>Saved execution lanes from the backend runtime.</p>
      </header>

      <div className={styles.actions}>
        <Button onClick={() => navigate("/task/new")}>New task</Button>
        <Button variant="ghost" onClick={load}>Retry</Button>
      </div>

      {loading ? <p className={styles.subtle}>Loading lanes…</p> : null}
      {error ? <div className={styles.error}>Backend unavailable. {error}</div> : null}

      {!loading && !error && lanes.length === 0 ? (
        <div className={styles.demo}>No lanes returned yet. Create a new task to start one.</div>
      ) : null}

      <div className={styles.grid}>
        {lanes.map((lane) => (
          <button
            key={lane.workflow_id}
            className={styles.card}
            type="button"
            onClick={() => {
              localStorage.setItem("bridge.activeWorkflowId", lane.workflow_id);
              navigate(`/workspace/${encodeURIComponent(lane.workflow_id)}`);
            }}
          >
            <div className={styles.cardTitle}>{lane.title ?? "Untitled lane"}</div>
            <div className={styles.meta}>
              <span>workflow: {lane.workflow_id}</span>
              <span>status: {lane.status ?? "unknown"}</span>
              <span>mode: {lane.recommended_mode ?? "not set"}</span>
              <span>momentum: {formatNumber(lane.momentum_score)}</span>
              <span>confidence: {formatNumber(lane.progress_confidence)}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function formatNumber(value: unknown) {
  return typeof value === "number" ? value.toFixed(2) : "n/a";
}

