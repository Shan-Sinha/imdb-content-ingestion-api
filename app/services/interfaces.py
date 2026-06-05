"""Abstract service interfaces defining business contracts (DIP & ISP)."""

from abc import ABC, abstractmethod


class IMovieService(ABC):
    """Abstract interface for Movie Querying services."""

    @abstractmethod
    def get_movies(self, page: int, per_page: int,
                   sort_field: str, sort_direction: int,
                   year: int | None = None,
                   language: str | None = None,
                   original_title: str | None = None) -> dict:
        """Query and filter movies from data store."""
        pass


class ICSVService(ABC):
    """Abstract interface for CSV Uploading services."""

    @abstractmethod
    def process(self, filepath: str) -> int:
        """Process local CSV file and save data."""
        pass


class IAuthService(ABC):
    """Abstract interface for Authentication and User services."""

    @abstractmethod
    def register_user(self, username: str, password_plain: str) -> dict:
        """Register a new user in the system with hashed password."""
        pass

    @abstractmethod
    def generate_token(self, username: str) -> str:
        """Generate a signed timed bearer token for a user."""
        pass

    @abstractmethod
    def authenticate_user(self, username: str, password_plain: str) -> str | None:
        """Authenticate user credentials and return username if valid."""
        pass
