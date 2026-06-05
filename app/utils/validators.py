"""Input validation helpers for API parameters."""

ALLOWED_EXTENSIONS = {"csv"}

# Accepted sort fields and their MongoDB field mappings
ALLOWED_SORT_FIELDS = {
    "release_date": "release_date",
    "vote_average": "vote_average",
}

ALLOWED_ORDER = {"asc", "desc"}

# Pagination limits
DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 10
MAX_PER_PAGE = 100


def allowed_file(filename: str) -> bool:
    """Check that the uploaded file has a .csv extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_pagination(page: str | None, per_page: str | None) -> tuple:
    """Parse and clamp pagination parameters.

    Returns:
        (page, per_page) as validated integers.

    Raises:
        ValueError with a descriptive message on invalid input.
    """
    try:
        page = int(page) if page else DEFAULT_PAGE
    except (ValueError, TypeError):
        raise ValueError("'page' must be a positive integer.")

    try:
        per_page = int(per_page) if per_page else DEFAULT_PER_PAGE
    except (ValueError, TypeError):
        raise ValueError("'per_page' must be a positive integer.")

    if page < 1:
        raise ValueError("'page' must be >= 1.")
    if per_page < 1 or per_page > MAX_PER_PAGE:
        raise ValueError(f"'per_page' must be between 1 and {MAX_PER_PAGE}.")

    return page, per_page


def validate_sort(sort_by: str | None, order: str | None) -> tuple:
    """Validate and return sort field + direction.

    Returns:
        (mongo_field, pymongo_direction)  — direction is 1 (asc) or -1 (desc).

    Raises:
        ValueError on invalid input.
    """
    from pymongo import ASCENDING, DESCENDING

    sort_by = sort_by or "release_date"
    order = order or "desc"

    if sort_by not in ALLOWED_SORT_FIELDS:
        raise ValueError(
            f"'sort_by' must be one of: {', '.join(ALLOWED_SORT_FIELDS.keys())}."
        )

    if order not in ALLOWED_ORDER:
        raise ValueError("'order' must be 'asc' or 'desc'.")

    direction = ASCENDING if order == "asc" else DESCENDING
    return ALLOWED_SORT_FIELDS[sort_by], direction
