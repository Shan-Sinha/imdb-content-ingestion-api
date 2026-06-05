"""Authentication middleware for protecting API endpoints."""

from functools import wraps
from flask import current_app, request
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from app.utils.responses import error_response


class TokenAuthenticator:
    """Authenticator class utilizing timed signature serializer and static fallback keys."""

    def __init__(self, secret_key: str, static_key: str):
        """Initialize TokenAuthenticator with secret signature and static key."""
        self.secret_key = secret_key
        self.static_key = static_key
        self.serializer = URLSafeTimedSerializer(secret_key, salt="auth-token")

    def generate_token(self, username: str) -> str:
        """Generate a signed timed token containing the username payload."""
        return self.serializer.dumps({"username": username})

    def verify_token(self, token: str) -> str | None:
        """Verify the authentication token.

        Checks if the token is:
        1. A valid, signed, timed Bearer token (max 1 hour age).
        2. A valid static API key.

        Returns:
            The authenticated username or identity, or None on failure.
        """
        if not token:
            return None

        # 1. Try timed signed token
        try:
            payload = self.serializer.loads(token, max_age=3600)  # valid for 1 hour
            return payload.get("username")
        except (SignatureExpired, BadSignature):
            pass

        # 2. Check static key fallback
        if token == self.static_key:
            return "api_client"

        return None


def require_auth(f):
    """Decorator to protect routes requiring authentication.

    Extracts a Bearer/X-API-Key token and checks it using the
    TokenAuthenticator registered in the Flask application context.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # 1. Get token from headers
        token = None
        auth_header = request.headers.get("Authorization")
        api_key_header = request.headers.get("X-API-Key")

        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
        elif api_key_header:
            token = api_key_header

        if not token:
            return error_response("Unauthorized: Missing authentication token.", 401)

        # 2. Retrieve authenticator from application context
        # Fallback to an ad-hoc local authenticator if not attached to app
        authenticator = getattr(current_app, "authenticator", None)
        if not authenticator:
            secret_key = current_app.config.get("SECRET_KEY", "imdb_super_secret_key_98765")
            static_key = current_app.config.get("API_KEY", "default_secret_key_123")
            authenticator = TokenAuthenticator(secret_key, static_key)

        # 3. Verify
        username = authenticator.verify_token(token)
        if not username:
            return error_response("Unauthorized: Invalid or expired authentication token.", 401)

        # Attach identity to request context
        request.authenticated_user = username

        return f(*args, **kwargs)

    return decorated
