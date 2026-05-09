from bridge_engine.modules.coding_module import CodingExecutionModule
from bridge_engine.modules.language_module import LanguageExecutionModule


MODULES = [
    CodingExecutionModule(),
    LanguageExecutionModule(),
]


class ModuleRegistry:
    def resolve(self, interest: str, learning_goal: str):
        for module in MODULES:
            if module.supports(interest, learning_goal):
                return module

        return CodingExecutionModule()
