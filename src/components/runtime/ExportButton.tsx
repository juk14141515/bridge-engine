export function ExportButton({
  onExport,
  busy,
  hasContent,
  exportCopied,
}: {
  onExport: () => void;
  busy: boolean;
  hasContent: boolean;
  exportCopied?: boolean;
}) {
  if (!hasContent) return null;
  return (
    <button type="button" className="btn btn-quiet" onClick={onExport} disabled={busy}>
      {busy ? 'Exporting…' : exportCopied ? 'Copied' : 'Export'}
    </button>
  );
}
