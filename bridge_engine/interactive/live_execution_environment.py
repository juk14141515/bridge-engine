class LiveExecutionEnvironment:
    """Interactive runtime for completing tasks inside Bridge."""

    def create_session(self, workflow: dict):
        return {
            "workflow_id": workflow.get("id"),
            "environment": [
                "editor",
                "voice_input",
                "matching_ui",
                "interactive_canvas",
                "proof_upload",
            ],
            "live_feedback": True,
        }
