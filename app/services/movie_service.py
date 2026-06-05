"""Movie query service — filtering, sorting, and pagination."""

import math
import re

from app.models.movie import Movie
from app.services.interfaces import IMovieService
from app.repositories.movie_repository import IMovieRepository


class MovieService(IMovieService):
    """Service to query and search the movie catalog using repository abstraction."""

    def __init__(self, movie_repository: IMovieRepository):
        """Initialize MovieService with movie repository."""
        self.movie_repository = movie_repository

    def get_movies(self, page: int, per_page: int,
                   sort_field: str, sort_direction: int,
                   year: int | None = None,
                   language: str | None = None,
                   original_title: str | None = None) -> dict:
        """Query movies with filtering, sorting, and pagination using MovieRepository."""
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

        # Count total matching documents (via repository)
        total_records = self.movie_repository.count(query)
        total_pages = math.ceil(total_records / per_page) if total_records > 0 else 0

        # Fetch the page (via repository)
        skip = (page - 1) * per_page
        docs = self.movie_repository.get_movies_paginated(
            query=query,
            sort_field=sort_field,
            sort_direction=sort_direction,
            skip=skip,
            limit=per_page
        )

        movies = [Movie.from_mongo(doc).to_dict() for doc in docs]

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
