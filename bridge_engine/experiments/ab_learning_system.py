class ABLearningSystem:
    """Tests different execution/runtime variants to improve completion."""

    def run_experiment(self, experiment_name: str, variants: list[str]):
        return {
            "experiment": experiment_name,
            "variants": variants,
            "goal": "improve_completion_and_reduce_friction",
            "status": "running",
        }
