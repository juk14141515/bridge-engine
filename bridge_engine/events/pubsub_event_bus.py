class PubSubEventBus:
    """Event-driven communication layer for runtime coordination."""

    def publish(self, topic: str, payload: dict):
        return {
            "topic": topic,
            "payload": payload,
            "status": "published",
        }

    def subscribe(self, topic: str):
        return {
            "topic": topic,
            "status": "subscribed",
        }
