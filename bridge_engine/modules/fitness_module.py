from bridge_engine.modules.base_module import BaseExecutionModule


class FitnessExecutionModule(BaseExecutionModule):
    module_name = "fitness"

    FITNESS_KEYWORDS = [
        "fitness",
        "workout",
        "gym",
        "exercise",
        "lifting",
        "running",
        "cardio",
        "health",
        "muscle",
    ]

    def supports(self, interest: str, learning_goal: str) -> bool:
        combined = f"{interest} {learning_goal}".lower()
        return any(keyword in combined for keyword in self.FITNESS_KEYWORDS)

    def generate_steps(self, interest: str, learning_goal: str):
        return [
            self.build_step(
                title="Warm up the system",
                why="Momentum starts with activation, not intensity.",
                checkpoint="Do a 30-second low-pressure warm-up related to the goal."
            ),
            self.build_step(
                title="Train one movement pattern",
                why="One repeated pattern creates consistency faster than overload.",
                checkpoint=f"Practice one repeatable action that improves {learning_goal}."
            ),
            self.build_step(
                title="Track the signal",
                why="Visible signals help your brain connect effort to progress.",
                checkpoint="Record one measurable improvement or observation."
            ),
            self.build_step(
                title="Recover and reinforce",
                why="Recovery protects momentum and prevents burnout.",
                checkpoint="Write one thing that made the session easier to continue."
            ),
        ]
