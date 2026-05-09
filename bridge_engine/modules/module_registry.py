from bridge_engine.modules.coding_module import CodingExecutionModule
from bridge_engine.modules.language_module import LanguageExecutionModule


MODULES = [
    CodingExecutionModule(),
    LanguageExecutionModule(),
]


class ModuleRegistry:
    def resolve(self, interest: str, learning_goal: str):
        weighted_modules = []

        for module in MODULES:
            score = 0

            if module.supports(interest, learning_goal):
                score += 1

            if module.supports(interest, interest):
                score += 1

            if module.supports(learning_goal, learning_goal):
                score += 2

            if score > 0:
                weighted_modules.append({
                    "module": module,
                    "weight": score,
                })

        if not weighted_modules:
            weighted_modules.append({
                "module": CodingExecutionModule(),
                "weight": 1,
            })

        weighted_modules.sort(
            key=lambda item: item["weight"],
            reverse=True,
        )

        return weighted_modules
