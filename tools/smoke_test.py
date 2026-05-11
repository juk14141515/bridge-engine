"""Quick e2e smoke for the new fast-entry + persistence flow.

Hits the live runtime at 127.0.0.1:6060. Confirms:
  - task + frame + supports persist through create/load
  - task title is never the user's literal input (no 'coding project' default leak)
  - professional mode injects its rule into prompts
  - rewrite preserves task/frame
"""

from __future__ import annotations

import json
import sys
import urllib.request

BASE = "http://127.0.0.1:6060"


def post(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def get(path: str) -> dict:
    with urllib.request.urlopen(BASE + path) as r:
        return json.loads(r.read())


def expect(label: str, ok: bool, detail: str = "") -> None:
    mark = "OK " if ok else "FAIL"
    print(f"  [{mark}] {label}{(' - ' + detail) if detail else ''}")
    if not ok:
        sys.exit(1)


def main() -> None:
    print("== Scenario A: Spanish + Music ==")
    a = post("/api/session/create", {
        "task": "Learn Spanish with my favorite songs",
        "frame": "music",
        "supports": ["adhd", "step_by_step"],
    })
    ws_id = a["workspace"]["id"]
    expect("session created", bool(ws_id))
    expect("task echoes user words", a["workspace"]["task"] == "Learn Spanish with my favorite songs")
    expect("frame is music", a["workspace"]["frame"] == "music")
    expect("first step exists", bool(a["current_step"]))
    expect("first step uses music unit", "measure" in a["current_step"]["title"].lower())

    print("== Scenario B: reload and check persistence ==")
    b = get(f"/api/workspace/{ws_id}")
    expect("task persists", b["workspace"]["task"] == "Learn Spanish with my favorite songs")
    expect("frame persists", b["workspace"]["frame"] == "music")
    expect("supports persist", set(b["workspace"]["supports"]) == {"adhd", "step_by_step"})

    print("== Scenario C: continue then rewrite + identity invariant ==")
    c = post("/api/session/continue", {
        "workspace_id": ws_id,
        "user_output": "Hola, me llamo Juan.",
    })
    expect("task still echoes user words", c["workspace"]["task"] == "Learn Spanish with my favorite songs")
    expect("frame still music", c["workspace"]["frame"] == "music")
    expect("step advanced", int(c["workspace"]["current_step_index"]) == 1)

    d = post("/api/session/rewrite", {
        "workspace_id": ws_id,
        "mode": "make_easier",
        "frame": "music",
    })
    expect("rewrite preserves task", d["workspace"]["task"] == "Learn Spanish with my favorite songs")
    expect("rewrite preserves frame", d["workspace"]["frame"] == "music")

    print("== Scenario D: Professional mode injects rule ==")
    e = post("/api/session/create", {
        "task": "Prepare Q3 product strategy memo",
        "frame": "investing",
        "supports": ["professional"],
    })
    prompt_lower = (e["current_step"]["prompt"] or "").lower()
    expect("task echoes user words", e["workspace"]["task"] == "Prepare Q3 product strategy memo")
    expect("frame is investing", e["workspace"]["frame"] == "investing")
    expect(
        "pro rule embedded in prompt",
        "concise" in prompt_lower or "direct" in prompt_lower or "decision" in prompt_lower,
        prompt_lower[:120],
    )

    print("== Scenario E: no 'coding project' leak when user types relationship ==")
    f = post("/api/session/create", {
        "task": "Prepare for the hard conversation with my partner",
        "frame": "fitness",
        "supports": ["step_by_step"],
    })
    expect("task is user words", f["workspace"]["task"] == "Prepare for the hard conversation with my partner")
    expect("no coding fallback", "coding" not in (f["workspace"]["task"] or "").lower())

    print()
    print("All scenarios passed.")


if __name__ == "__main__":
    main()
