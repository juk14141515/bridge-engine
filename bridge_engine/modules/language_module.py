from bridge_engine.modules.base_module import BaseExecutionModule


class LanguageExecutionModule(BaseExecutionModule):
    module_name = "language"

    LANGUAGE_KEYWORDS = [
        "spanish",
        "french",
        "japanese",
        "language",
        "communication",
        "conversation",
    ]

    def supports(self, interest: str, learning_goal: str) -> bool:
        combined = f"{interest} {learning_goal}".lower()
        return any(keyword in combined for keyword in self.LANGUAGE_KEYWORDS)

    def generate_steps(self, interest: str, learning_goal: str):
        return [
            self.build_step(
                title="Create a real-world usage scenario",
                why="Language learning works better when emotionally connected.",
                checkpoint=f"Describe a realistic situation where {learning_goal} helps your interest in {interest}."
            ),
            self.build_step(
                title="Learn high-frequency phrases",
                why="Useful phrases create immediate progress and confidence.",
                checkpoint="Memorize and use 5 useful phrases out loud."
            ),
            self.build_step(
                title="Apply the language in context",
                why="Contextual use improves retention dramatically.",
                checkpoint=f"Write or speak about {interest} using the target language."
            ),
            self.build_step(
                title="Reflect and reinforce",
                why="Review strengthens memory formation.",
                checkpoint="Record what phrases or concepts felt easiest to remember."
            ),
        ]
