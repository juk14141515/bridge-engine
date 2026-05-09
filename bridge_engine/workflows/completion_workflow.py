from datetime import datetime


class CompletionWorkflow:
    """Tracks full assignment/project execution inside Bridge."""

    def build(self, title: str, workflow_type: str, module_path: dict):
        return {
            "id": datetime.utcnow().strftime("%Y%m%d%H%M%S"),
            "title": title,
            "workflow_type": workflow_type,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "steps": module_path.get("steps", []),
            "outputs": [],
            "export_ready": False,
        }

    def add_output(self, workflow: dict, step_id: int, output_data: dict):
        workflow["outputs"].append({
            "step_id": step_id,
            "output": output_data,
            "saved_at": datetime.utcnow().isoformat(),
        })

        completed_steps = {
            item["step_id"] for item in workflow["outputs"]
        }

        if len(completed_steps) >= len(workflow["steps"]):
            workflow["export_ready"] = True
            workflow["status"] = "completed"

        return workflow
