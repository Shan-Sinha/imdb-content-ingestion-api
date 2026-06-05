"""User model class representing a system user."""


class User:
    """User class representing registered system credentials."""

    def __init__(self, username: str, password_hash: str, id: str = None):
        """Initialize user instance."""
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @classmethod
    def from_mongo(cls, doc: dict):
        """Build User instance from MongoDB user document."""
        if not doc:
            return None
        return cls(
            id=str(doc.get("_id")),
            username=doc.get("username"),
            password_hash=doc.get("password_hash")
        )

    def to_dict(self) -> dict:
        """Serialize User instance (excluding password hash) for responses."""
        return {
            "id": self.id,
            "username": self.username
        }
