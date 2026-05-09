from bridge_engine.modules.base_module import BaseExecutionModule


class GamingExecutionModule(BaseExecutionModule):
    module_name = "gaming"

    GAMING_KEYWORDS = [
        "gaming",
        "game",
        "games",
        "level",
        "quest",
        "xp",
        "boss",
        "minecraft",
        "pokemon",
        "rpg",
    ]

    def supports(self, interest: str, learning_goal: str) -> bool:
        combined = f"{interest} {learning_goal}".lower()
        return any(keyword in combined for keyword in self.GAMING_KEYWORDS)

    def generate_steps(self, interest: str, learning_goal: str):
        return [
            self.build_step(
                title="Find the first objective",
                why="A game feels enterable when the first objective is visible.",
                checkpoint=f"Turn {learning_goal} into one first objective you can complete through {interest}."
            ),
            self.build_step(
                title="Run the tutorial version",
                why="Tutorial mode lowers pressure and builds confidence before difficulty increases.",
                checkpoint="Do the easiest version once, without trying to master it."
            ),
            self.build_step(
                title="Unlock the next mechanic",
                why="One new mechanic at a time keeps the path from feeling overloaded.",
                checkpoint=f"Identify one mechanic from {learning_goal} that improves your {interest} path."
            ),
            self.build_step(
                title="Replay and improve",
                why="Repetition with tiny upgrades turns learning into progression.",
                checkpoint="Repeat the step once and improve one small thing."
            ),
        ]
