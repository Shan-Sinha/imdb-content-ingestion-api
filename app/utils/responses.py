"""Standardised JSON response helpers.

Every API response follows the envelope:
{
    "success": bool,
    "message": str,
    "data": dict | list | None
}
"""

from flask import jsonify


def success_response(data=None, message="Success", status_code=200):
    """Return a successful JSON response."""
    return jsonify({
        "success": True,
        "message": message,
        "data": data,
    }), status_code


def error_response(message="An error occurred", status_code=400, errors=None):
    """Return an error JSON response."""
    payload = {
        "success": False,
        "message": message,
        "data": None,
    }
    if errors:
        payload["errors"] = errors
    return jsonify(payload), status_code
