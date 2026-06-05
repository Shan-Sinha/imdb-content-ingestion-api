"""Movie document model representing a MongoDB movie entry."""

from bson import ObjectId
from datetime import datetime


class Movie:
    """Movie class representing a single movie entry.

    Provides deserialization from MongoDB documents and serialization
    to standard JSON-safe dictionaries.
    """

    def __init__(self, **kwargs):
        self.id = str(kwargs.get("_id")) if kwargs.get("_id") else kwargs.get("id")
        self.budget = self._to_float(kwargs.get("budget"))
        self.homepage = kwargs.get("homepage") or None
        self.original_language = kwargs.get("original_language") or None
        self.original_title = kwargs.get("original_title") or None
        self.overview = kwargs.get("overview") or None
        self.release_date = kwargs.get("release_date")
        self.year = kwargs.get("year")
        self.revenue = self._to_float(kwargs.get("revenue"))
        self.runtime = self._to_int(kwargs.get("runtime"))
        self.status = kwargs.get("status") or None
        self.title = kwargs.get("title") or None
        self.vote_average = self._to_float(kwargs.get("vote_average"))
        self.vote_count = self._to_int(kwargs.get("vote_count"))
        self.production_company_id = self._to_int(kwargs.get("production_company_id"))
        self.genre_id = self._to_int(kwargs.get("genre_id"))
        self.languages = kwargs.get("languages") or []
        self.created_at = kwargs.get("created_at")

    @classmethod
    def from_mongo(cls, doc: dict):
        """Build a Movie object from a MongoDB document."""
        if not doc:
            return None
        return cls(**doc)

    def to_dict(self) -> dict:
        """Convert a Movie instance into a JSON-safe dictionary for API responses."""
        return {
            "id": self.id,
            "budget": self.budget,
            "homepage": self.homepage,
            "original_language": self.original_language,
            "original_title": self.original_title,
            "overview": self.overview,
            "release_date": self.release_date.isoformat() if isinstance(self.release_date, datetime) else self.release_date,
            "year": self.year,
            "revenue": self.revenue,
            "runtime": self.runtime,
            "status": self.status,
            "title": self.title,
            "vote_average": self.vote_average,
            "vote_count": self.vote_count,
            "production_company_id": self.production_company_id,
            "genre_id": self.genre_id,
            "languages": self.languages,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
        }

    # Internal type-coercion helpers for constructor resilience
    @staticmethod
    def _to_float(val) -> float | None:
        if val is None or str(val).strip() == "":
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _to_int(val) -> int | None:
        if val is None or str(val).strip() == "":
            return None
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return None
