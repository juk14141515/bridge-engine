from bridge_engine.modules.base_module import BaseExecutionModule


class CodingExecutionModule(BaseExecutionModule):
    module_name = "coding"

    CODING_KEYWORDS = [
        "coding",
        "programming",
        "python",
        "software",
        "website",
        "trading bot",
        "ai",
        "automation",
    ]

    def supports(self, interest: str, learning_goal: str) -> bool:
        combined = f"{interest} {learning_goal}".lower()
        return any(keyword in combined for keyword in self.CODING_KEYWORDS)

    def generate_steps(self, interest: str, learning_goal: str):
        return [
            self.build_step(
                title="Define the execution target",
                why="Clear outputs reduce ADHD overwhelm and ambiguity.",
                checkpoint=f"Write the smallest possible version of a {interest} project using {learning_goal}."
            ),
            self.build_step(
                title="Build a tiny working component",
                why="Fast visible progress creates motivation momentum.",
                checkpoint="Create one working feature in under 15 minutes."
            ),
            self.build_step(
                title="Connect learning to a real system",
                why="Applied learning sticks better than passive study.",
                checkpoint=f"Integrate one {learning_goal} concept into your real project."
            ),
            self.build_step(
                title="Measure the improvement",
                why="Visible improvement reinforces continued execution.",
                checkpoint="Write what became easier, faster, or smarter."
            ),
        ]
