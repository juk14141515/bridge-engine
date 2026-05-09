import json
from pathlib import Path


EXPORT_DIR = Path("data/exports")


class RuntimeExporter:
    def __init__(self):
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    def export_markdown(self, runtime_state, plan):
        output = [
            f"# {runtime_state.user_goal}",
            "",
            f"Status: {runtime_state.current_status}",
            f"Next Action: {runtime_state.next_best_action}",
            "",
            "## Steps",
        ]

        for step in plan["steps"]:
            output.append(f"- {step['title']}")

        path = EXPORT_DIR / f"{runtime_state.lane_id}.md"
        path.write_text("\n".join(output))

        return str(path)

    def export_json(self, runtime_state, plan):
        path = EXPORT_DIR / f"{runtime_state.lane_id}.json"

        path.write_text(json.dumps({
            "runtime": runtime_state.__dict__,
            "plan": plan,
        }, indent=2))

        return str(path)
