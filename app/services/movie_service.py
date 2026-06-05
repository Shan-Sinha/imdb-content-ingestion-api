"""Movie query service — filtering, sorting, and pagination."""

import math
import re

from app.models.movie import Movie


class MovieService:
    """Service to query and search the movie catalog in MongoDB."""

    def __init__(self, collection):
        """Initialize the Movie service with MongoDB collection reference."""
        self.collection = collection

    def get_movies(self, page: int, per_page: int,
                   sort_field: str, sort_direction: int,
                   year: int | None = None,
                   language: str | None = None,
                   original_title: str | None = None) -> dict:
        """Query movies with filtering, sorting, and pagination.

        Args:
            page: 1-based page number.
            per_page: Items per page.
            sort_field: MongoDB field name to sort on.
            sort_direction: 1 (ascending) or -1 (descending).
            year: Optional year filter.
            language: Optional language filter (case-insensitive substring).
            original_title: Optional original title filter (case-insensitive substring).

        Returns:
            Dict with 'movies' list and 'pagination' metadata.
        """
        # Build filter query
        query = {}
        if year is not None:
            query["year"] = year
        if language is not None:
            # Case-insensitive regex match to handle exact language name case insensitively
            query["languages"] = {"$regex": f"^{re.escape(language)}$", "$options": "i"}
        if original_title is not None:
            # Case-insensitive substring match
            query["original_title"] = {"$regex": re.escape(original_title), "$options": "i"}

        # Count total matching documents (before pagination)
        total_records = self.collection.count_documents(query)
        total_pages = math.ceil(total_records / per_page) if total_records > 0 else 0

        # Fetch the page
        skip = (page - 1) * per_page
        cursor = (
            self.collection
            .find(query)
            .sort(sort_field, sort_direction)
            .skip(skip)
            .limit(per_page)
        )

        movies = [Movie.from_mongo(doc).to_dict() for doc in cursor]

        return {
            "movies": movies,
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total_records": total_records,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        }
