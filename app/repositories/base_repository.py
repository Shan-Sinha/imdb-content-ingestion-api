"""Abstract base repository interface defining basic data access contract."""

from abc import ABC, abstractmethod


class IRepository(ABC):
    """Generic interface for data repositories (Interface Segregation & DIP)."""

    @abstractmethod
    def create(self, item):
        """Create a new item in the data store."""
        pass

    @abstractmethod
    def get_by_id(self, item_id: str):
        """Retrieve an item by its unique identifier."""
        pass
