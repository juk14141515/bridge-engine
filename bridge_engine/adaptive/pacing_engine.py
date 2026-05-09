class AdaptivePacingEngine:
    """Determines pacing and execution depth for users."""

    MODES = [
        "stuck",
        "normal",
        "fast",
        "expert",
        "burnout",
        "adhd",
        "dyslexia",
        "high_momentum",
    ]

    def choose_mode(self, profile: dict):
        if profile.get("burnout"):
            return "burnout"

        if profile.get("adhd"):
            return "adhd"

        if profile.get("expert"):
            return "expert"

        if profile.get("high_momentum"):
            return "fast"

        return "normal"
