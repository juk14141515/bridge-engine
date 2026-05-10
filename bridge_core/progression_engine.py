from datetime import datetime


class ProgressionEngine:
    def next_step(self, session, current_output=""):
        current_index = session.get("current_step_index", 0)
        steps = session.get("steps", [])

        if current_index >= len(steps):
            return {
                "type": "complete",
                "message": "Generate export artifact.",
            }

        step = steps[current_index]

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "title": step.get("title"),
            "prompt": step.get("prompt") or step.get("checkpoint"),
            "remaining": max(0, len(steps) - current_index - 1),
            "current_output": current_output,
        }
