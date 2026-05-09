class FeedbackLearningEngine:
    """Learns from user execution feedback."""

    SIGNALS = [
        "helpful",
        "not_quite",
        "too_much",
        "faster",
        "more_visual",
        "more_like_this",
    ]

    def process(self, signal: str):
        return {
            "signal": signal,
            "adaptation_required": signal in [
                "too_much",
                "more_visual",
                "faster",
            ],
        }
