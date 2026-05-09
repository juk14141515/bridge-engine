from datetime import datetime

from bridge_engine.modules.composer import ModuleComposer
from bridge_engine.modules.module_registry import ModuleRegistry


registry = ModuleRegistry()
composer = ModuleComposer()


class PathBuilderService:
    def build(self, interest: str, learning_goal: str):
        weighted_modules = registry.resolve(interest, learning_goal)

        composed = composer.compose(
            weighted_modules,
            interest,
            learning_goal,
        )

        generated_steps = composed["steps"]

        formatted_steps = []

        for index, step in enumerate(generated_steps, start=1):
            formatted_steps.append({
                "id": index,
                "title": step["title"],
                "why": step["why"],
                "checkpoint": step["checkpoint"],
                "status": "unlocked" if index == 1 else "locked",
                "answer": "",
                "modules": step["modules"],
                "interaction_type": step["interaction_type"],
                "interaction_types": step["interaction_types"],
            })

        return {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "interest": interest,
            "learning_goal": learning_goal,
            "module": composed["dominant_module"],
            "title": f"Learn {learning_goal} through {interest}",
            "steps": formatted_steps,
        }
