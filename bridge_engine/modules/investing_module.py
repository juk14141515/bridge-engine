from bridge_engine.modules.base_module import BaseExecutionModule


class InvestingExecutionModule(BaseExecutionModule):
    module_name = "investing"

    INVESTING_KEYWORDS = [
        "investing",
        "stocks",
        "trading",
        "finance",
        "market",
        "portfolio",
        "risk",
        "economics",
        "statistics",
    ]

    def supports(self, interest: str, learning_goal: str) -> bool:
        combined = f"{interest} {learning_goal}".lower()
        return any(keyword in combined for keyword in self.INVESTING_KEYWORDS)

    def generate_steps(self, interest: str, learning_goal: str):
        return [
            self.build_step(
                title="Find the signal",
                why="Good decisions start with identifying the highest-value signal.",
                checkpoint=f"Identify one useful signal related to {learning_goal}."
            ),
            self.build_step(
                title="Reduce uncertainty",
                why="Breaking uncertainty into smaller observations lowers overwhelm.",
                checkpoint="Write one thing you know and one thing still unclear."
            ),
            self.build_step(
                title="Test a tiny hypothesis",
                why="Small experiments create learning without overwhelming risk.",
                checkpoint=f"Run one tiny test connecting {learning_goal} to {interest}."
            ),
            self.build_step(
                title="Review the outcome",
                why="Reflection compounds future decision quality.",
                checkpoint="Record what signal mattered most."
            ),
        ]
