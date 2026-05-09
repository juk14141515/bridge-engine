from datetime import datetime


class WorldModelEngine:
    """Understands the larger identity world a user is trying to enter, not just the task."""

    WORLD_TYPES = [
        "cybersecurity",
        "startup_founder",
        "film",
        "academia",
        "fitness_culture",
        "gaming_communities",
        "fashion_watch_culture",
        "creator_economy",
        "software_engineering",
        "finance_investing",
        "healthcare",
        "law_policy",
        "music",
        "design",
        "research",
    ]

    WORLD_DIMENSIONS = [
        "career_path",
        "industry_language",
        "community_norms",
        "aesthetic_codes",
        "role_models",
        "entry_projects",
        "status_markers",
        "beginner_friction",
        "expert_friction",
        "identity_hooks",
    ]

    def infer_world(self, user_goal: str, interests: list[str] | None = None):
        interests = interests or []
        goal_lower = user_goal.lower()

        if "film" in goal_lower or "movie" in goal_lower:
            world = "film"
        elif "business" in goal_lower or "startup" in goal_lower:
            world = "startup_founder"
        elif "security" in goal_lower or "cyber" in goal_lower:
            world = "cybersecurity"
        elif "fitness" in goal_lower or "gym" in goal_lower:
            world = "fitness_culture"
        elif "invest" in goal_lower or "stock" in goal_lower:
            world = "finance_investing"
        elif "code" in goal_lower or "program" in goal_lower:
            world = "software_engineering"
        else:
            world = interests[0] if interests else "general_execution"

        return {
            "world": world,
            "goal": user_goal,
            "interests": interests,
            "dimensions": self.WORLD_DIMENSIONS,
            "entry_question": "What kind of world does this user want to enter?",
            "updated_at": datetime.utcnow().isoformat(),
        }

    def build_emotional_pathway(self, world: str, user_identity: dict):
        return {
            "world": world,
            "identity_hooks": user_identity.get("interests", []),
            "pathway_style": user_identity.get("preferred_style", "adaptive"),
            "output": "emotionally_authentic_pathway",
        }
