class RelationshipPathEngine:
    """Builds paths that bridge identities and interests."""

    def build_bridge(self, user_interest: str, external_interest: str):
        return {
            "user_interest": user_interest,
            "external_interest": external_interest,
            "bridge_paths": self.generate_connections(user_interest, external_interest),
        }

    def generate_connections(self, user_interest: str, external_interest: str):
        if user_interest == "cameras" and external_interest == "gaming":
            return [
                "virtual_photography",
                "cinematic_composition",
                "environmental_storytelling",
                "screenshot_artistry",
                "lighting_design",
            ]

        return [
            "community_understanding",
            "shared_language",
            "participation_path",
        ]
