"""Authentication routes blueprint."""

import logging
from flask import Blueprint, current_app, request

from app.utils.responses import success_response, error_response

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/token", methods=["POST"])
def generate_token():
    """Generate a timed signed Bearer token using username and password."""
    
    # 1. Parse JSON request body
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return error_response("Missing 'username' or 'password' in request body.", 400)

    # 2. Verify credentials using dynamic auth service (database backed)
    authenticated_user = current_app.auth_service.authenticate_user(username, password)
    if not authenticated_user:
        return error_response("Unauthorized: Invalid username or password.", 401)

    # 3. Generate signed token (SOLID DI)
    token = current_app.auth_service.generate_token(authenticated_user)

    logger.info("Token generated successfully for user: %s", authenticated_user)

    return success_response(
        data={
            "token": token,
            "expires_in": 3600,
            "token_type": "Bearer"
        },
        message="Token generated successfully."
    )
