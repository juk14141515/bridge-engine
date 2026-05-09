class AdaptiveMediaRecommendationLayer:
    """Recommends media as execution catalysts rather than passive entertainment."""

    MEDIA_TYPES = [
        "movies",
        "documentaries",
        "youtube_channels",
        "podcasts",
        "books",
        "creators",
        "games",
        "soundtracks",
        "communities",
        "discords",
        "visual_aesthetics",
    ]

    def recommend(self, world: str, emotional_state: dict):
        return {
            "world": world,
            "recommendation_type": "execution_catalyst",
            "media": self.select_media(world),
            "emotional_alignment": emotional_state.get("desired_identity", "growth"),
        }

    def select_media(self, world: str):
        mappings = {
            "film": ["director_breakdowns", "cinematic_storytelling", "film_commentary"],
            "startup_founder": ["founder_podcasts", "build_in_public", "startup_documentaries"],
            "fitness_culture": ["discipline_content", "transformation_journeys", "training_films"],
            "software_engineering": ["coding_streams", "build_logs", "architecture_breakdowns"],
        }

        return mappings.get(world, ["general_motivation", "identity_expansion"])
