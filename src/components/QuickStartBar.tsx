import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { formatUserApiError } from '../lib/displayLabels';
import { openBridgeSession } from '../lib/startBridgeSession';
import { QUICK_START_PRESETS } from '../lib/onboardingOptions';
import { PRODUCT_QUICK_START_LABEL } from '../lib/productPitch';

export function QuickStartBar({
  supports,
  onError,
  className,
}: {
  supports?: string[];
  onError?: (message: string | null) => void;
  className?: string;
}) {
  const navigate = useNavigate();
  const [busyId, setBusyId] = useState<string | null>(null);

  async function launch(presetId: string, task: string, frame: string) {
    if (busyId) return;
    onError?.(null);
    setBusyId(presetId);
    try {
      const { workspaceId, ribbon, initialContract } = await openBridgeSession({
        task,
        frame,
        supports: supports?.length ? supports : undefined,
      });
      navigate(`/workspace/${workspaceId}`, {
        replace: true,
        state: { entryRibbon: ribbon, initialContract },
      });
    } catch (e) {
      onError?.(formatUserApiError(e, 'Could not start. Try again.'));
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div
      className={className ?? 'quick-start'}
      role="group"
      aria-label="Quick ways to start a session"
    >
      <p className="quick-start__label">{PRODUCT_QUICK_START_LABEL}</p>
      <div className="quick-start__grid">
        {QUICK_START_PRESETS.map((p) => (
          <button
            key={p.id}
            type="button"
            className="quick-start__tile"
            disabled={Boolean(busyId)}
            aria-busy={busyId === p.id}
            onClick={() => void launch(p.id, p.task, p.frame)}
          >
            <span className="quick-start__tile-label">{busyId === p.id ? 'Starting…' : p.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
