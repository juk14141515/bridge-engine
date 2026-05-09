class AdaptiveAgentRouter:
    """Routes tasks dynamically to the most appropriate agents."""

    def route(self, runtime_state: dict):
        if runtime_state.get("burnout"):
            return ["recovery_agent", "motivation_agent"]

        if runtime_state.get("expert"):
            return ["planner_agent", "export_agent"]

        return ["decomposer_agent", "pacing_agent"]
