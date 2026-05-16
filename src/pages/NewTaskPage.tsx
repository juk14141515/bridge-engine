import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/Button";
import { TextArea, TextInput } from "../components/ui/Input";
import { runtimeApi } from "../lib/runtimeApi";
import styles from "../components/runtime/Runtime.module.css";

const interests = ["coding", "gaming", "fitness", "investing", "cameras", "music", "film", "entrepreneurship", "custom"];
const modes = ["ADHD support", "burnout recovery", "dyslexia readability", "high momentum", "expert mode", "low energy"];

export function NewTaskPage() {
  const navigate = useNavigate();
  const [content, setContent] = useState("");
  const [interest, setInterest] = useState("coding");
  const [customInterest, setCustomInterest] = useState("");
  const [mode, setMode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit() {
    setLoading(true);
    setError("");
    const result = await runtimeApi.createTask({
      content,
      interest_frame: interest,
      custom_interest: customInterest,
      cognitive_mode: mode,
    });
    setLoading(false);

    if (!result.ok) {
      setError(result.error);
      return;
    }

    const workflowId = "workflow_id" in result.data
      ? result.data.workflow_id
      : "lane" in result.data
        ? result.data.lane?.workflow_id
        : result.data.workflow_id;

    if (workflowId) {
      localStorage.setItem("bridge.activeWorkflowId", workflowId);
      navigate(`/workspace/${encodeURIComponent(workflowId)}`);
    } else {
      navigate("/lanes");
    }
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>New task</h1>
        <p className={styles.subtle}>Paste the thing you need to move through. Bridge will create a lane.</p>
      </header>

      <div className={styles.panel}>
        <div className={styles.stack}>
          <div className={styles.fieldGroup}>
            <label className={styles.label}>Assignment / goal / problem / idea / context</label>
            <TextArea value={content} onChange={(e) => setContent(e.target.value)} placeholder="Paste it here…" />
          </div>

          <div className={styles.fieldGroup}>
            <label className={styles.label}>Personal interest</label>
            <select className={styles.select} value={interest} onChange={(e) => setInterest(e.target.value)}>
              {interests.map((item) => <option key={item}>{item}</option>)}
            </select>
          </div>

          {interest === "custom" ? (
            <TextInput value={customInterest} onChange={(e) => setCustomInterest(e.target.value)} placeholder="Custom interest" />
          ) : null}

          <div className={styles.fieldGroup}>
            <label className={styles.label}>Cognitive support mode</label>
            <select className={styles.select} value={mode} onChange={(e) => setMode(e.target.value)}>
              <option value="">No preference</option>
              {modes.map((item) => <option key={item}>{item}</option>)}
            </select>
          </div>

          {error ? <div className={styles.error}>API error: {error}</div> : null}
          <div className={styles.actions}>
            <Button disabled={!content.trim() || loading} onClick={submit}>{loading ? "Creating…" : "Create lane"}</Button>
            <Button variant="ghost" onClick={() => navigate("/lanes")}>Back to lanes</Button>
          </div>
        </div>
      </div>
    </div>
  );
}

