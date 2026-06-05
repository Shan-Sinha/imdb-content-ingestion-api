"""Movie repository contract and MongoDB concrete implementation."""

from abc import abstractmethod
from app.repositories.base_repository import IRepository


class IMovieRepository(IRepository):
    """Abstract interface for Movie repository operations (DIP)."""

    @abstractmethod
    def insert_many(self, documents: list[dict]) -> int:
        """Insert a batch of movie documents."""
        pass

    @abstractmethod
    def get_movies_paginated(self, query: dict, sort_field: str, sort_direction: int, skip: int, limit: int) -> list:
        """Fetch a paginated list of movies based on query and sort fields."""
        pass

    @abstractmethod
    def count(self, query: dict) -> int:
        """Get the count of documents matching the query."""
        pass


class MongoMovieRepository(IMovieRepository):
    """Concrete Movie repository implementation for MongoDB."""

    def __init__(self, db):
        """Initialize repository with MongoDB database reference."""
        self.db = db
        self.collection = db["movies"]

    def create(self, item: dict):
        """Create a single movie document."""
        result = self.collection.insert_one(item)
        return str(result.inserted_id)

    def get_by_id(self, item_id: str) -> dict | None:
        """Retrieve a movie document by ObjectId."""
        from bson import ObjectId
        try:
            return self.collection.find_one({"_id": ObjectId(item_id)})
        except Exception:
            return None

    def insert_many(self, documents: list[dict]) -> int:
        """Bulk-insert movie documents into MongoDB."""
        if not documents:
            return 0
        result = self.collection.insert_many(documents, ordered=False)
        return len(result.inserted_ids)

    def get_movies_paginated(self, query: dict, sort_field: str, sort_direction: int, skip: int, limit: int) -> list:
        """Retrieve paginated, sorted cursor results from MongoDB."""
        return list(
            self.collection
            .find(query)
            .sort(sort_field, sort_direction)
            .skip(skip)
            .limit(limit)
        )

    def count(self, query: dict) -> int:
        """Count matching documents in the movies collection."""
        return self.collection.count_documents(query)
