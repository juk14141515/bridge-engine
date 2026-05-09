class AgentSpecializationSystem:
    """Coordinates specialized execution agents for different cognitive/runtime functions."""

    AGENTS = {
        "planner_agent": "creates strategic execution plans",
        "decomposer_agent": "breaks tasks into executable chunks",
        "motivation_agent": "increases emotional engagement",
        "pacing_agent": "adjusts pacing and cognitive load",
        "explanation_agent": "simplifies difficult concepts",
        "recovery_agent": "helps users resume after abandonment",
        "export_agent": "formats final outputs",
        "relationship_translator_agent": "bridges different identity worlds",
        "cinematic_inspiration_agent": "finds emotional inspiration media",
    }

    def orchestrate(self, objective: str, runtime_state: dict):
        active_agents = self.select_agents(runtime_state)

        return {
            "objective": objective,
            "active_agents": active_agents,
            "coordination_mode": "multi_agent_execution_pipeline",
        }

    def select_agents(self, runtime_state: dict):
        agents = ["planner_agent", "decomposer_agent"]

        if runtime_state.get("stuck"):
            agents.append("recovery_agent")

        if runtime_state.get("needs_emotional_support"):
            agents.append("motivation_agent")
            agents.append("cinematic_inspiration_agent")

        return agents
