import { useState } from 'react';
import { artifactSectionLabel } from '../../lib/displayLabels';

type ArtifactPreviewData = Record<string, unknown> & {
  type?: string;
  outline?: { introduction?: string; body_points?: string; draft_seed?: string; conclusion?: string };
  cards?: Array<{ front?: string; back?: string }>;
  files?: string[];
  sections?: Record<string, string | undefined | null>;
};

export function ArtifactPreviewPanel({
  preview,
  liveSections,
  hasContent,
  defaultOpen = true,
}: {
  preview: ArtifactPreviewData;
  liveSections?: Record<string, string | undefined | null>;
  hasContent: boolean;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen && hasContent);

  return (
    <section className="session-artifact">
      <button
        type="button"
        className="session-disclosure"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
      >
        <span>What you&apos;re building</span>
        <span className="session-disclosure__chev">{open ? '−' : '+'}</span>
      </button>
      {open ? (
        <ArtifactBody preview={preview} sections={liveSections} emptyHint="Your work will show up here as you continue." />
      ) : null}
    </section>
  );
}

function ArtifactBody({
  preview,
  sections,
  emptyHint,
}: {
  preview: ArtifactPreviewData;
  sections?: Record<string, string | undefined | null>;
  emptyHint: string;
}) {
  const type = preview.type ?? 'general';
  const merged = { ...(preview.sections ?? {}), ...(sections ?? {}) };
  const hasLive = Object.values(merged).some((v) => Boolean(v && String(v).trim()));

  if (type === 'essay_outline' || preview.outline) {
    return <EssayOutline preview={preview} live={merged} emptyHint={emptyHint} />;
  }
  if (type === 'flashcards' || preview.cards) {
    return <Flashcards preview={preview} emptyHint={emptyHint} />;
  }
  if (type === 'code_scaffold' || preview.files) {
    return <CodeScaffold preview={preview} emptyHint={emptyHint} />;
  }
  if (hasLive) {
    return <LiveSections sections={merged} />;
  }
  return <p className="muted small session-artifact__empty">{emptyHint}</p>;
}

function EssayOutline({
  preview,
  live,
  emptyHint,
}: {
  preview: ArtifactPreviewData;
  live: Record<string, string | undefined | null>;
  emptyHint: string;
}) {
  const outline = preview.outline ?? {};
  const thesis = (live.thesis_seed as string | undefined) || outline.introduction || '';
  const supports = (live.support_points as string | undefined) || outline.body_points || '';
  const body = (live.body_paragraph_seed as string | undefined) || outline.draft_seed || '';
  const closing = (live.draft_outline as string | undefined) || outline.conclusion || '';

  if (!thesis && !supports && !body && !closing) {
    return <p className="muted small session-artifact__empty">{emptyHint}</p>;
  }

  return (
    <ul className="artifact-list">
      <li>
        <strong>Thesis</strong>
        <span>{thesis || <em className="muted">In progress…</em>}</span>
      </li>
      <li>
        <strong>Main points</strong>
        <span>{supports || <em className="muted">In progress…</em>}</span>
      </li>
      <li>
        <strong>Draft section</strong>
        <span>{body || <em className="muted">In progress…</em>}</span>
      </li>
      <li>
        <strong>Outline</strong>
        <span>{closing || <em className="muted">In progress…</em>}</span>
      </li>
    </ul>
  );
}

function Flashcards({ preview, emptyHint }: { preview: ArtifactPreviewData; emptyHint: string }) {
  const cards = (preview.cards ?? []).filter((card) => {
    const front = (card.front ?? '').trim().toLowerCase();
    return front && !['not found', 'not_found', 'undefined', 'null', 'error'].includes(front);
  });
  if (!cards.length) {
    return <p className="muted small session-artifact__empty">{emptyHint}</p>;
  }
  return (
    <ul className="artifact-list">
      {cards.map((card, idx) => (
        <li key={idx}>
          <strong>{card.front?.trim() || `Card ${idx + 1}`}</strong>
          <span>{card.back?.trim() || '—'}</span>
        </li>
      ))}
    </ul>
  );
}

function CodeScaffold({ preview, emptyHint }: { preview: ArtifactPreviewData; emptyHint: string }) {
  const files = preview.files ?? [];
  if (!files.length) {
    return <p className="muted small session-artifact__empty">{emptyHint}</p>;
  }
  return (
    <ul className="artifact-list artifact-list--code">
      {files.map((f) => (
        <li key={f}>
          <code>{f}</code>
        </li>
      ))}
    </ul>
  );
}

function LiveSections({ sections }: { sections: Record<string, string | undefined | null> }) {
  const entries = Object.entries(sections)
    .filter(([, v]) => v && String(v).trim())
    .map(([name, value]) => {
      const label = artifactSectionLabel(name);
      return label ? { name, label, value: String(value) } : null;
    })
    .filter((e): e is { name: string; label: string; value: string } => e !== null);

  if (!entries.length) {
    return <p className="muted small session-artifact__empty">Your work will show up here as you continue.</p>;
  }

  return (
    <ul className="artifact-list">
      {entries.map(({ name, label, value }) => (
        <li key={name}>
          <strong>{label}</strong>
          <span>{value}</span>
        </li>
      ))}
    </ul>
  );
}
