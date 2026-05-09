class MultiAgentOrchestrator:
    """Coordinates communication between specialized execution agents."""

    def orchestrate(self, objective: str):
        return {
            "objective": objective,
            "agents": [
                "planner_agent",
                "decomposer_agent",
                "motivation_agent",
                "pacing_agent",
                "recovery_agent",
                "export_agent",
            ],
            "coordination": "live",
            "handoff_enabled": True,
        }
