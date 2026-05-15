# Runtime V2 Frontend Integration Hooks

## Autosave
Frontend should autosave:
- every completed step
- every rewrite action
- every 15-30 seconds while typing

Recommended endpoint:
POST /api/workspace/save

Payload:
```json
{
  "workspace": workspace
}
```

## Live Sync
Poll or websocket sync:
- current_step_index
- artifact_preview
- progress
- runtime_state
- motivation
- friction

## Export
Supported formats:
- markdown
- plain_text
- json
- future: pdf/docx

Recommended flow:
1. User clicks export
2. RuntimeV2Coordinator.export(format)
3. Download compiled artifact

## Session Recovery
On app launch:
- GET /api/workspaces/recent
- restore unfinished workspaces
- prompt continue recovery flow

## Friction UI
If friction state becomes:
- blank
- hesitant
- overwhelmed

Frontend should:
- shrink UI complexity
- offer rewrite buttons
- reduce visible options
