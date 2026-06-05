"""Authentication and User business logic service implementation."""

import logging
from werkzeug.security import generate_password_hash, check_password_hash

from app.services.interfaces import IAuthService
from app.repositories.user_repository import IUserRepository
from app.utils.auth import TokenAuthenticator

logger = logging.getLogger(__name__)


class AuthService(IAuthService):
    """Concrete implementation of user registration, authentication, and token management."""

    def __init__(self, user_repository: IUserRepository, authenticator: TokenAuthenticator):
        """Initialize AuthService with repositories and authenticator utility."""
        self.user_repository = user_repository
        self.authenticator = authenticator

    def register_user(self, username: str, password_plain: str) -> dict:
        """Register a new user with secure password hashing."""
        username = str(username).strip()
        if not username or not password_plain:
            raise ValueError("Username and password cannot be empty.")

        # Check unique constraint
        existing = self.user_repository.get_by_username(username)
        if existing:
            raise ValueError(f"User with username '{username}' already exists.")

        # Hash and store
        password_hash = generate_password_hash(password_plain)
        user_data = {
            "username": username,
            "password_hash": password_hash
        }
        
        user_id = self.user_repository.create(user_data)
        logger.info("Successfully registered user: %s (ID: %s)", username, user_id)
        
        return {
            "id": user_id,
            "username": username
        }

    def authenticate_user(self, username: str, password_plain: str) -> str | None:
        """Verify username and password hashes against repository data."""
        username = str(username).strip()
        user_doc = self.user_repository.get_by_username(username)
        if not user_doc:
            return None

        # Check password hash match
        password_hash = user_doc.get("password_hash")
        if check_password_hash(password_hash, password_plain):
            return username

        return None

    def generate_token(self, username: str) -> str:
        """Delegate timed bearer token generation to authenticator module."""
        return self.authenticator.generate_token(username)
