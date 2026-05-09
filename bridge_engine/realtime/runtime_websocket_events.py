class RuntimeWebsocketEvents:
    def event_payload(self, event_type: str, runtime_state: dict):
        return {
            "event": event_type,
            "lane_id": runtime_state.get("workflow_id"),
            "status": runtime_state.get("status"),
            "next_best_action": runtime_state.get("recommended_next_action"),
            "momentum_score": runtime_state.get("momentum_score"),
        }
