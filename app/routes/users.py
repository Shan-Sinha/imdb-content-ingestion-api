"""User management routes blueprint."""

import logging
from flask import Blueprint, current_app, request

from app.utils.responses import success_response, error_response

logger = logging.getLogger(__name__)

users_bp = Blueprint("users", __name__)


@users_bp.route("/users", methods=["POST"])
def register_user():
    """Register a new user in the system with username and password."""
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return error_response("Missing 'username' or 'password' in request body.", 400)

    try:
        user_info = current_app.auth_service.register_user(username, password)
        return success_response(
            data=user_info,
            message="User registered successfully.",
            status_code=201
        )
    except ValueError as exc:
        return error_response(str(exc), 400)
    except Exception as exc:
        logger.exception("Error during user registration")
        return error_response(f"Internal server error: {str(exc)}", 500)
