"""Movies listing endpoint.

GET /api/v1/movies
    Query params:
        page       – page number (default 1)
        per_page   – items per page (default 10, max 100)
        year       – filter by release year
        language   – filter by language
        sort_by    – 'release_date' or 'vote_average' (default 'release_date')
        order      – 'asc' or 'desc' (default 'desc')
"""

import logging

from flask import Blueprint, current_app, request

from app.utils.auth import require_auth
from app.utils.responses import success_response, error_response
from app.utils.validators import validate_pagination, validate_sort

logger = logging.getLogger(__name__)

movies_bp = Blueprint("movies", __name__)


@movies_bp.route("/movies", methods=["GET"])
@require_auth
def list_movies():
    """Return a paginated, filterable, sortable list of movies."""

    try:
        # --- Parse & validate pagination ---
        page, per_page = validate_pagination(
            request.args.get("page"),
            request.args.get("per_page"),
        )

        # --- Parse & validate sort ---
        sort_field, sort_direction = validate_sort(
            request.args.get("sort_by"),
            request.args.get("order"),
        )
    except ValueError as exc:
        return error_response(str(exc), 400)

    # --- Optional filters ---
    year = request.args.get("year")
    language = request.args.get("language")
    original_title = request.args.get("original_title")

    if year is not None:
        try:
            year = int(year)
        except (ValueError, TypeError):
            return error_response("'year' must be a valid integer.", 400)

    # --- Query (OOP) ---
    try:
        from app.services.movie_service import MovieService
        collection = current_app.db["movies"]
        movie_service = MovieService(collection)
        result = movie_service.get_movies(
            page=page,
            per_page=per_page,
            sort_field=sort_field,
            sort_direction=sort_direction,
            year=year,
            language=language,
            original_title=original_title,
        )

        return success_response(
            data=result,
            message="Movies fetched successfully.",
        )
    except Exception as exc:
        logger.exception("Error fetching movies")
        return error_response(f"Internal server error: {str(exc)}", 500)
