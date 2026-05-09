class SemanticPlanner:
    def plan(self, task_type: str, user_goal: str):
        blocker = "overwhelm"

        steps = [
            {
                "title": "Clarify the objective",
                "interaction_type": "reflection",
            },
            {
                "title": "Break the task into smaller sections",
                "interaction_type": "checklist",
            },
            {
                "title": "Complete the first meaningful action",
                "interaction_type": "active_work",
            },
        ]

        output_map = {
            "essay": "markdown_outline",
            "coding": "task_list",
            "presentation": "slide_outline",
            "study": "study_deck",
        }

        return {
            "objective": user_goal,
            "task_type": task_type,
            "friction_type": blocker,
            "likely_blockers": ["avoidance", "ambiguity"],
            "interaction_type": steps[0]["interaction_type"],
            "steps": steps,
            "output_type": output_map.get(task_type, "project_plan"),
        }
