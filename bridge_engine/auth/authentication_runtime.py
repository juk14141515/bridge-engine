class AuthenticationRuntime:
    """Authentication and user identity scaffold."""

    PROVIDERS = ["email", "google", "github", "anonymous_beta"]

    def login(self, provider: str, identity: dict):
        return {
            "provider": provider,
            "identity": identity,
            "status": "authenticated",
        }
