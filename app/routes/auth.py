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

    # 2. Get configured credentials
    expected_username = current_app.config.get("AUTH_USERNAME", "admin")
    expected_password = current_app.config.get("AUTH_PASSWORD", "password123")

    # 3. Verify credentials
    if username != expected_username or password != expected_password:
        return error_response("Unauthorized: Invalid username or password.", 401)

    # 4. Generate signed token (OOP dependency injection)
    token = current_app.authenticator.generate_token(username)

    logger.info("Token generated successfully for user: %s", username)

    return success_response(
        data={
            "token": token,
            "expires_in": 3600,
            "token_type": "Bearer"
        },
        message="Token generated successfully."
    )
