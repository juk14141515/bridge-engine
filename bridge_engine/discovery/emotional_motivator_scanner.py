class EmotionalMotivatorScanner:
    """Discovers emotional and identity-based motivators that increase execution momentum."""

    MOTIVATOR_TYPES = [
        "movie",
        "character",
        "community",
        "creator",
        "music",
        "visual_aesthetic",
        "identity_projection",
        "role_model",
    ]

    def scan(self, user_context: dict):
        return {
            "detected_motivators": self.detect(user_context),
            "recommended_outputs": self.recommend(user_context),
        }

    def detect(self, user_context: dict):
        return [
            "cinematic_inspiration",
            "identity_empowerment",
            "community_belonging",
        ]

    def recommend(self, user_context: dict):
        return [
            "watch_specific_movie",
            "study_creator_breakdown",
            "join_interest_community",
            "build_identity_playlist",
            "visual_reference_collection",
        ]
