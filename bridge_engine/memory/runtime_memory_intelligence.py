class RuntimeMemoryIntelligence:
    def rank_next_actions(self, runtime_history: list):
        if not runtime_history:
            return {
                "best_next_action": "start_small",
                "confidence": 0.4,
            }

        successful = [
            item for item in runtime_history
            if item.get("completed")
        ]

        if len(successful) > 5:
            return {
                "best_next_action": "resume_previous_success_pattern",
                "confidence": 0.82,
            }

        return {
            "best_next_action": "reduce_friction",
            "confidence": 0.58,
        }
