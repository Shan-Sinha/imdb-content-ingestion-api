"""User repository contract and MongoDB concrete implementation."""

from abc import abstractmethod
from app.repositories.base_repository import IRepository


class IUserRepository(IRepository):
    """Abstract interface for User repository operations (DIP)."""

    @abstractmethod
    def get_by_username(self, username: str) -> dict | None:
        """Retrieve a user document by their unique username."""
        pass

    @abstractmethod
    def ensure_indexes(self) -> None:
        """Ensure indexes (like unique username constraint) are set up."""
        pass


class MongoUserRepository(IUserRepository):
    """Concrete User repository implementation for MongoDB."""

    def __init__(self, db):
        """Initialize repository with MongoDB database reference."""
        self.db = db
        self.collection = db["users"]

    def create(self, item: dict) -> str:
        """Create a user document in MongoDB.

        Expected format: {'username': '...', 'password_hash': '...'}
        """
        result = self.collection.insert_one(item)
        return str(result.inserted_id)

    def get_by_id(self, item_id: str) -> dict | None:
        """Retrieve a user document by ObjectId."""
        from bson import ObjectId
        try:
            return self.collection.find_one({"_id": ObjectId(item_id)})
        except Exception:
            return None

    def get_by_username(self, username: str) -> dict | None:
        """Retrieve user document by unique username."""
        return self.collection.find_one({"username": username})

    def ensure_indexes(self) -> None:
        """Setup unique index constraint on the username field."""
        self.collection.create_index("username", unique=True)
