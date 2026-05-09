from datetime import datetime

from bridge_engine.modules.module_registry import ModuleRegistry


registry = ModuleRegistry()


class PathBuilderService:
    def build(self, interest: str, learning_goal: str):
        module = registry.resolve(interest, learning_goal)
        generated_steps = module.generate_steps(interest, learning_goal)

        formatted_steps = []

        for index, step in enumerate(generated_steps, start=1):
            formatted_steps.append({
                "id": index,
                "title": step["title"],
                "why": step["why"],
                "checkpoint": step["checkpoint"],
                "status": "unlocked" if index == 1 else "locked",
                "answer": "",
                "module": module.module_name,
            })

        return {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "interest": interest,
            "learning_goal": learning_goal,
            "module": module.module_name,
            "title": f"Learn {learning_goal} through {interest}",
            "steps": formatted_steps,
        }
