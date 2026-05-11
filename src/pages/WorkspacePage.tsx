import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Button } from "../components/ui/Button";
import { TextArea } from "../components/ui/Input";
import { InteractionSurface } from "../components/runtime/InteractionSurface";
import { runtimeApi, type RuntimeStep } from "../lib/runtimeApi";
import styles from "../components/runtime/Runtime.module.css";

const feedbackOptions = ["Helpful", "Not quite", "Too much", "Faster", "More visual", "More like this"];
const exportFormats = ["Markdown", "checklist", "project plan", "outline"];

export function WorkspacePage() {
  const navigate = useNavigate();
  const { workflowId = "" } = useParams();
  const [step, setStep] = useState<RuntimeStep | null>(null);
  const [response, setResponse] = useState("");
  const [proof, setProof] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [exportMessage, setExportMessage] = useState("");

  const isComplete = useMemo(() => {
    const status = String(step?.status ?? "").toLowerCase();
    return status === "completed" || status === "exported";
  }, [step?.status]);

  async function loadNext() {
    if (!workflowId) return;
    setLoading(true);
    setError("");
    const result = await runtimeApi.getNext(workflowId);
    setLoading(false);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    setStep(result.data);
  }

  useEffect(() => {
    void loadNext();
  }, [workflowId]);

  async function sendFeedback(feedback: string) {
    const result = await runtimeApi.sendFeedback(workflowId, feedback, step ?? undefined);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    await loadNext();
  }

  async function submitProof() {
    const result = await runtimeApi.submitProof(workflowId, proof);
    if (!result.ok) {
      setError(result.error);
      return;
    }
    setProof("");
    await loadNext();
  }

  async function exportLane(format: string) {
    const result = await runtimeApi.exportWorkflow(workflowId, format);
    if (!result.ok) {
      setExportMessage("Export coming soon.");
      return;
    }
    setExportMessage(result.data.url ?? result.data.content ?? "Export ready.");
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Active task</h1>
        <p className={styles.subtle}>workflow: {workflowId}</p>
      </header>

      {loading ? <p className={styles.subtle}>Loading next action…</p> : null}
      {error ? (
        <div className={styles.panel}>
          <div className={styles.error}>Backend unavailable. {error}</div>
          <div className={styles.actions}>
            <Button onClick={loadNext}>Retry</Button>
            <Button variant="ghost" onClick={() => navigate("/lanes")}>Back to lanes</Button>
          </div>
        </div>
      ) : null}

      {!loading && !error && step ? (
        isComplete ? (
          <div className={styles.completion}>
            <div className={styles.check}>✓</div>
            <h2 className={styles.title}>You finished this lane.</h2>
            <p className={styles.subtle}>That counts. Export it if useful.</p>
            <div className={styles.actions}>
              {exportFormats.map((format) => (
                <Button key={format} variant="ghost" onClick={() => exportLane(format)}>{format}</Button>
              ))}
            </div>
            {exportMessage ? <p className={styles.subtle}>{exportMessage}</p> : null}
          </div>
        ) : (
          <div className={styles.stack}>
            <section className={styles.panel}>
              <div className={styles.stack}>
                <div>
                  <div className={styles.label}>Objective</div>
                  <h2 className={styles.cardTitle}>{String(step.current_objective ?? step.objective ?? "Current objective")}</h2>
                </div>
                <div>
                  <div className={styles.label}>Current step</div>
                  <p className={styles.subtle}>{String(step.current_step ?? step.step ?? "Ask the backend for the next action.")}</p>
                </div>
                <div>
                  <div className={styles.label}>Why this matters</div>
                  <p className={styles.subtle}>{String(step.why_this_matters ?? step.why ?? "This keeps the lane moving.")}</p>
                </div>
                <div className={styles.metrics}>
                  <span>interaction: {String(step.interaction_type ?? "text_response")}</span>
                  <span>confidence: {formatMetric(step.progress_confidence)}</span>
                  <span>momentum: {formatMetric(step.momentum_score)}</span>
                </div>
              </div>
            </section>

            <InteractionSurface
              interactionType={String(step.interaction_type ?? "text_response")}
              value={response}
              onChange={setResponse}
            />

            <section className={styles.panel}>
              <div className={styles.stack}>
                <div className={styles.label}>Feedback</div>
                <div className={styles.actions}>
                  {feedbackOptions.map((item) => (
                    <Button key={item} variant="ghost" onClick={() => sendFeedback(item)}>{item}</Button>
                  ))}
                </div>
              </div>
            </section>

            <section className={styles.panel}>
              <div className={styles.proof}>
                <div className={styles.label}>Proof / checkpoint</div>
                <TextArea value={proof} onChange={(e) => setProof(e.target.value)} placeholder="Text proof for now…" />
                <div className={styles.demo}>Future upload proof placeholder.</div>
                <Button disabled={!proof.trim()} onClick={submitProof}>Submit proof</Button>
              </div>
            </section>
          </div>
        )
      ) : null}
    </div>
  );
}

function formatMetric(value: unknown) {
  return typeof value === "number" ? value.toFixed(2) : "n/a";
}

