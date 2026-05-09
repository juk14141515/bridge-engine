from collections import Counter


class ModuleComposer:
    """Combines multiple module outputs into hybrid bridge paths."""

    def compose(self, weighted_modules, interest: str, learning_goal: str):
        generated = []

        for item in weighted_modules:
            module = item["module"]
            weight = item["weight"]
            steps = module.generate_steps(interest, learning_goal)

            generated.append({
                "module": module.module_name,
                "weight": weight,
                "steps": steps,
            })

        merged_steps = []

        max_steps = max(len(item["steps"]) for item in generated)

        for index in range(max_steps):
            titles = []
            reasons = []
            checkpoints = []
            modules = []
            interaction_types = []

            for item in generated:
                if index < len(item["steps"]):
                    step = item["steps"][index]
                    titles.append(step["title"])
                    reasons.append(step["why"])
                    checkpoints.append(step["checkpoint"])
                    modules.append(item["module"])
                    interaction_types.append(step.get("interaction_type", "micro_quiz"))

            merged_steps.append({
                "title": titles[0],
                "why": " ".join(reasons[:2]),
                "checkpoint": checkpoints[0],
                "modules": modules,
                "interaction_type": interaction_types[0] if interaction_types else "micro_quiz",
                "interaction_types": interaction_types,
            })

        dominant = Counter([
            item["module"] for item in generated
        ]).most_common(1)[0][0]

        return {
            "dominant_module": dominant,
            "steps": merged_steps,
        }
